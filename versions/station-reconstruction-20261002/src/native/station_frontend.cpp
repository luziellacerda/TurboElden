#include "station_catalog_abi.hpp"
#include <jni.h>
#include <dlfcn.h>
#include <algorithm>
#include <atomic>
#include <map>
#include <mutex>
#include <set>
#include <stdexcept>
#include <utility>
#include <ctime>
#include <cmath>
#include <sys/stat.h>
#define API extern "C" __attribute__((visibility("default")))
namespace {
using station::Catalog;using station::Item;using station::Progress;
JavaVM* vm=nullptr;jclass frontend=nullptr;
jmethodID configureMethod=nullptr,refreshMethod=nullptr,startMethod=nullptr,cancelMethod=nullptr;
jmethodID removeMethod=nullptr,coverMethod=nullptr,reconcileMethod=nullptr,authorizedMethod=nullptr,loginMethod=nullptr;
struct Env {
 JNIEnv* env=nullptr;bool attached=false;
 Env(){if(vm){int status=vm->GetEnv(reinterpret_cast<void**>(&env),JNI_VERSION_1_6);if(status==JNI_EDETACHED){attached=vm->AttachCurrentThread(&env,nullptr)==JNI_OK;if(!attached)env=nullptr;}}}
 ~Env(){if(attached)vm->DetachCurrentThread();}
};
struct Job {Progress progress;std::string message,launch;int result=0;};
struct Inbox {
 std::mutex mutex;std::atomic<bool> changed{false};
 bool hasCatalog=false;std::vector<Item> catalog;
 std::map<std::string,std::string> covers;std::map<std::string,Job> jobs;
 std::string error,name;
} inbox;
struct State {
 Catalog* owner=nullptr;bool pending=false;
 std::vector<Item> catalog;
 std::map<std::string,Job> jobs;
 std::set<std::string> covers;
} state; // Only the SDL thread reads/writes this state.
bool idValid(const std::string& id){return id.size()>=8&&id.size()<=64&&std::all_of(id.begin(),id.end(),[](unsigned char c){return(c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-';});}
void error(JNIEnv* env,const char* text){if(!env->ExceptionCheck()){jclass cls=env->FindClass("java/io/IOException");if(cls){env->ThrowNew(cls,text);env->DeleteLocalRef(cls);}}}
std::string bytes(JNIEnv* env,jbyteArray input,size_t limit){
 if(!input)throw std::runtime_error("Missing native input");
 jsize n=env->GetArrayLength(input);if(n<0||static_cast<size_t>(n)>limit)throw std::runtime_error("Native input limit");
 std::string result(static_cast<size_t>(n),'\0');if(n)env->GetByteArrayRegion(input,0,n,reinterpret_cast<jbyte*>(&result[0]));
 if(env->ExceptionCheck())throw std::runtime_error("Native input failed");return result;
}
std::string identifier(JNIEnv* env,jstring value){
 if(!value||env->GetStringLength(value)>64)throw std::runtime_error("Invalid item identity");
 const char* chars=env->GetStringUTFChars(value,nullptr);if(!chars)throw std::runtime_error("Missing item identity");
 std::string id(chars);env->ReleaseStringUTFChars(value,chars);if(!idValid(id))throw std::runtime_error("Invalid item identity");return id;
}
bool command(jmethodID method,const std::string* id=nullptr,bool result=false){
 Env scope;JNIEnv* env=scope.env;if(!env||!frontend||!method)return false;
 jstring arg=id?env->NewStringUTF(id->c_str()):nullptr;if(id&&!arg)return false;
 bool accepted=true;
 if(result)accepted=env->CallStaticBooleanMethod(frontend,method,arg)==JNI_TRUE;
 else if(id)env->CallStaticVoidMethod(frontend,method,arg);
 else env->CallStaticVoidMethod(frontend,method);
 if(arg)env->DeleteLocalRef(arg);
 if(env->ExceptionCheck()){env->ExceptionClear();accepted=false;}
 return accepted;
}
void changed(Catalog* catalog){++catalog->revision;catalog->installedCount=std::count_if(catalog->items.begin(),catalog->items.end(),[](const Item& item){return item.installed;});}
bool owned(Catalog* catalog){return catalog&&catalog==state.owner;}
Item* find(Catalog* catalog,const std::string& id){auto item=std::find_if(catalog->items.begin(),catalog->items.end(),[&](const Item& i){return i.id==id;});return item==catalog->items.end()?nullptr:&*item;}
bool active(){return std::any_of(state.jobs.begin(),state.jobs.end(),[](const auto& pair){return pair.second.progress.active;});}
void queueCovers(Catalog* catalog){
 if(!owned(catalog)||catalog->state!=2)return;
 for(size_t index:catalog->priorities){
  if(state.covers.size()>=4)break;if(index>=catalog->items.size())continue;Item& item=catalog->items[index];
  if(item.coverId.empty()||!item.coverPath.empty()||item.coverFailed||item.coverPending)continue;
  item.coverPending=true;state.covers.insert(item.id);
  if(!command(coverMethod,&item.id)){item.coverPending=false;item.coverFailed=true;state.covers.erase(item.id);}
 }
}
void drain(Catalog* catalog){
 if(!owned(catalog)||!inbox.changed.load(std::memory_order_acquire))return;
 bool hasCatalog=false;std::vector<Item> next;
 std::map<std::string,std::string> covers;std::map<std::string,Job> jobs;std::string failure;
 {std::lock_guard<std::mutex> lock(inbox.mutex);
  hasCatalog=inbox.hasCatalog;inbox.hasCatalog=false;if(hasCatalog)next.swap(inbox.catalog);
  covers.swap(inbox.covers);jobs.swap(inbox.jobs);failure.swap(inbox.error);inbox.changed.store(false,std::memory_order_release);
 }
 if(hasCatalog){state.catalog=std::move(next);state.pending=true;catalog->error.clear();}
 bool modified=false;
 for(auto& pair:covers){state.covers.erase(pair.first);Item* item=find(catalog,pair.first);if(!item)continue;
  item->coverPending=false;item->coverFailed=pair.second.empty();item->coverReady=!pair.second.empty();item->coverPath=std::move(pair.second);modified=true;
 }
 for(auto& pair:jobs){Item* item=find(catalog,pair.first);if(!item)continue;Job& job=pair.second;
  if(job.result==1&&!job.launch.empty()){item->localPath=job.launch;item->fileName=job.launch.substr(job.launch.find_last_of('/')+1);item->installed=true;modified=true;}
  else if(job.result==2){item->localPath.clear();item->fileName.clear();item->installed=false;modified=true;}
  state.jobs[pair.first]=std::move(job);
 }
 if(!failure.empty()){catalog->error=std::move(failure);if(catalog->items.empty())catalog->state=3;}
 if(modified)changed(catalog);
}
bool apply(Catalog* catalog){
 if(!owned(catalog)||!state.pending||active()||(catalog->engineState[0]&1))return false;
 for(auto& item:state.catalog){auto found=state.jobs.find(item.id);if(found==state.jobs.end())continue;
  const Job& job=found->second;
  if(job.result==1&&!job.launch.empty()){item.localPath=job.launch;item.fileName=job.launch.substr(job.launch.find_last_of('/')+1);item.installed=true;}
  else if(job.result==2){item.localPath.clear();item.fileName.clear();item.installed=false;}
 }
 catalog->items.swap(state.catalog);state.catalog.clear();state.pending=false;
 catalog->priorities.clear();state.covers.clear();state.jobs.clear();
 catalog->state=2;catalog->error.clear();changed(catalog);return true;
}
}
API jint JNI_OnLoad(JavaVM* machine,void*){
 vm=machine;JNIEnv* env=nullptr;if(vm->GetEnv(reinterpret_cast<void**>(&env),JNI_VERSION_1_6)!=JNI_OK)return JNI_ERR;
 jclass cls=env->FindClass("org/emulationstation/frontend/station/StationFrontend");if(!cls)return JNI_ERR;
 frontend=static_cast<jclass>(env->NewGlobalRef(cls));env->DeleteLocalRef(cls);if(!frontend)return JNI_ERR;
 configureMethod=env->GetStaticMethodID(frontend,"configure","(Ljava/lang/String;)V");
 refreshMethod=env->GetStaticMethodID(frontend,"refresh","()V");
 startMethod=env->GetStaticMethodID(frontend,"start","(Ljava/lang/String;)Z");
 cancelMethod=env->GetStaticMethodID(frontend,"cancel","(Ljava/lang/String;)V");
 removeMethod=env->GetStaticMethodID(frontend,"remove","(Ljava/lang/String;)Z");
 coverMethod=env->GetStaticMethodID(frontend,"cover","(Ljava/lang/String;)V");
 reconcileMethod=env->GetStaticMethodID(frontend,"reconcile","()V");
 authorizedMethod=env->GetStaticMethodID(frontend,"authorized","()Z");
 loginMethod=env->GetStaticMethodID(frontend,"requestLogin","()V");
 return env->ExceptionCheck()?JNI_ERR:JNI_VERSION_1_6;
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishCatalog(JNIEnv* env,jclass,jobjectArray rows,jbyteArray name){
 try{
  if(!rows||env->GetArrayLength(rows)>4096)throw std::runtime_error("Catalog limit");
  std::vector<Item> items;std::set<std::string> seen;
  for(jsize i=0;i<env->GetArrayLength(rows);++i){
   auto input=static_cast<jbyteArray>(env->GetObjectArrayElement(rows,i));std::string row;
   try{row=bytes(env,input,16384);}catch(...){if(input)env->DeleteLocalRef(input);throw;}env->DeleteLocalRef(input);
   std::string fields[6];size_t offset=0;
   for(auto& field:fields){size_t end=row.find('\0',offset);if(end==std::string::npos)throw std::runtime_error("Incomplete native catalog row");field=row.substr(offset,end-offset);offset=end+1;}
   if(offset!=row.size()||!idValid(fields[0])||!idValid(fields[4])||!seen.insert(fields[0]).second)throw std::runtime_error("Invalid catalog identity");
   Item item;item.id=fields[0];item.name=fields[1];item.platform=fields[2];item.folder=fields[3];item.coverId=fields[4];item.localPath=fields[5];
   item.installed=!item.localPath.empty();if(item.installed)item.fileName=item.localPath.substr(item.localPath.find_last_of('/')+1);items.push_back(std::move(item));
  }
  std::string display=bytes(env,name,1024);std::lock_guard<std::mutex> lock(inbox.mutex);
  inbox.catalog=std::move(items);inbox.name=std::move(display);inbox.hasCatalog=true;inbox.changed.store(true,std::memory_order_release);
 }catch(const std::exception& failure){error(env,failure.what());}
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishCover(JNIEnv* env,jclass,jstring id,jbyteArray path){
 try{std::string key=identifier(env,id),value=bytes(env,path,8192);std::lock_guard<std::mutex> lock(inbox.mutex);
  if(inbox.covers.size()>=4096&&!inbox.covers.count(key))throw std::runtime_error("Cover queue limit");
  inbox.covers[key]=std::move(value);inbox.changed.store(true,std::memory_order_release);
 }catch(const std::exception& failure){error(env,failure.what());}
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishJob(JNIEnv* env,jclass,jstring id,jboolean running,jlong received,jlong total,jbyteArray message,jbyteArray launch,jint result){
 try{std::string key=identifier(env,id);if(received<0||total< -1||result<0||result>3)throw std::runtime_error("Invalid job event");
  Job job;job.progress.active=running;job.progress.received=received;job.progress.total=total;job.message=bytes(env,message,4096);job.launch=bytes(env,launch,8192);job.result=result;
  if(result==3)job.progress.error=job.message;
  std::lock_guard<std::mutex> lock(inbox.mutex);if(inbox.jobs.size()>=4096&&!inbox.jobs.count(key))throw std::runtime_error("Job queue limit");
  inbox.jobs[key]=std::move(job);inbox.changed.store(true,std::memory_order_release);
 }catch(const std::exception& failure){error(env,failure.what());}
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishError(JNIEnv* env,jclass,jbyteArray message){
 try{std::string text=bytes(env,message,4096);std::lock_guard<std::mutex> lock(inbox.mutex);inbox.error=std::move(text);inbox.changed.store(true,std::memory_order_release);}
 catch(const std::exception& failure){error(env,failure.what());}
}
// Service entry points called by the retained native renderer. No HTTP, URLs or filesystem heuristics.
API void StationCatalog_refresh(Catalog* catalog,const std::string&){
 if(!catalog)return;if(state.owner&&state.owner!=catalog)return;bool initial=state.owner==nullptr;state.owner=catalog;
 if(catalog->items.empty())catalog->state=1;
 using Root=std::string(*)();void* mainLibrary=dlopen("libmain.so",RTLD_NOW|RTLD_NOLOAD);auto root=mainLibrary?reinterpret_cast<Root>(dlsym(mainLibrary,"_ZN14CatalogService11getRomsRootEv")):nullptr;
 if(!root){catalog->state=3;catalog->error="Pasta de jogos indisponivel.";return;}
 std::string folder=root();dlclose(mainLibrary);
 if(!command(configureMethod,&folder)||(!initial&&!command(refreshMethod))){catalog->state=3;catalog->error="Nao foi possivel iniciar o catalogo Station.";}
}
API void StationCatalog_update(Catalog* catalog){drain(catalog);if(owned(catalog)&&catalog->items.empty())apply(catalog);queueCovers(catalog);}
API bool StationCatalog_applyPending(Catalog* catalog){drain(catalog);return apply(catalog);}
API void StationCatalog_refreshInstalled(Catalog* catalog){if(owned(catalog))command(reconcileMethod);}
API void StationCatalog_prioritize(Catalog* catalog,const std::vector<size_t>& indices){
 if(!owned(catalog))return;catalog->priorities.assign(indices.begin(),indices.begin()+std::min<size_t>(indices.size(),64));queueCovers(catalog);
}
API bool StationCatalog_start(Catalog* catalog,size_t index){
 if(!owned(catalog)||index>=catalog->items.size())return false;const std::string& id=catalog->items[index].id;
 if(state.jobs[id].progress.active)return false;if(!command(startMethod,&id,true))return false;
 Job job;job.progress.active=true;state.jobs[id]=std::move(job);return true;
}
API void StationCatalog_cancel(Catalog* catalog,size_t index){if(owned(catalog)&&index<catalog->items.size())command(cancelMethod,&catalog->items[index].id);}
API bool StationCatalog_uninstall(Catalog* catalog,size_t index){return owned(catalog)&&index<catalog->items.size()&&command(removeMethod,&catalog->items[index].id,true);}
API std::vector<size_t> StationCatalog_active(Catalog* catalog){std::vector<size_t> result;if(owned(catalog))for(size_t i=0;i<catalog->items.size();++i){auto job=state.jobs.find(catalog->items[i].id);if(job!=state.jobs.end()&&job->second.progress.active)result.push_back(i);}return result;}
API Progress StationCatalog_progress(Catalog* catalog,size_t index){if(owned(catalog)&&index<catalog->items.size()){auto job=state.jobs.find(catalog->items[index].id);if(job!=state.jobs.end())return job->second.progress;}return {};}

namespace {
template<class T> T mainSymbol(const char* name){
 static void* handle=dlopen("libmain.so",RTLD_NOW|RTLD_NOLOAD);
 return handle?reinterpret_cast<T>(dlsym(handle,name)):nullptr;
}
void localCall(void* self,const char* name){auto method=mainSymbol<void(*)(void*)>(name);if(method)method(self);}
bool authorized(){Env scope;if(!scope.env||!authorizedMethod)return false;
 bool ok=scope.env->CallStaticBooleanMethod(frontend,authorizedMethod)==JNI_TRUE;
 if(scope.env->ExceptionCheck()){scope.env->ExceptionClear();return false;}return ok;}
struct LicenseView {int32_t state=0;uint32_t pad=0;std::string error;int32_t request=0;uint32_t pad2=0;std::string session,code;bool saved=false;uint8_t pad3[7]{};std::string savedCode;int64_t expires=0;};
static_assert(sizeof(LicenseView)==0x80 && offsetof(LicenseView,error)==8 && offsetof(LicenseView,code)==0x40);
struct LocalUsage {bool ready=false,background=false;uint8_t pad[6]{};int64_t started=0;std::string game,platform,core;int64_t gameStarted=0;};
static_assert(sizeof(LocalUsage)==0x60);
void flush(void* self){if(self&&reinterpret_cast<uint8_t*>(self)[0x98])localCall(self,"_ZN16TelemetryService9saveStatsEv");}
}
// Native license UI is a view of the Station session, never a second verifier or local password.
API void StationLicense_sync(LicenseView* view){
 if(!view)return;view->request=0;view->session.clear();view->code.clear();view->savedCode.clear();view->expires=0;view->saved=false;
 if(authorized()){view->state=2;view->error.clear();}
 else{view->state=3;view->error="Entre com seu acesso Station para continuar.";}
}
API void StationLicense_enter(LicenseView* view){StationLicense_sync(view);if(view&&view->state!=2)command(loginMethod);}
// Existing local history format is retained. No IP lookup, upload queue, or remote telemetry.
API void StationStats_init(LocalUsage* self){
 if(!self||self->ready)return;self->ready=true;self->started=std::time(nullptr);
 auto dir=mainSymbol<std::string(*)()>("_ZN16TelemetryService3dirEv");
 if(dir){std::string path=dir();if(!path.empty()&&path[0]=='/')for(size_t i=1;i<=path.size();++i)if(i==path.size()||path[i]=='/')mkdir(path.substr(0,i).c_str(),0700);}
 localCall(self,"_ZN16TelemetryService9loadStatsEv");localCall(self,"_ZN16TelemetryService10loadPlayedEv");
}
API void StationStats_update(LocalUsage* self){flush(self);}
API void StationStats_background(LocalUsage* self,bool background){if(self){self->background=background;if(background)flush(self);}}
API void StationStats_start(LocalUsage* self,const std::string& game,const std::string& platform,const std::string& core){
 if(!self)return;StationStats_init(self);self->game=game;self->platform=platform;self->core=core;self->gameStarted=std::time(nullptr);
}
API void StationStats_end(LocalUsage* self,const std::string&,double,double,double seconds){
 if(!self||self->game.empty())return;
 if(!std::isfinite(seconds)||seconds<0)seconds=static_cast<double>(std::time(nullptr)-self->gameStarted);
 seconds=std::max(0.0,std::min(seconds,static_cast<double>(INT64_MAX/2)));
 using Record=void*(*)(void*,const std::string&,const std::string&,int64_t);
 auto record=mainSymbol<Record>("_ZN16TelemetryService10recordPlayERKNSt6__ndk112basic_stringIcNS0_11char_traitsIcEENS0_9allocatorIcEEEES8_x");
 if(record)record(self,self->game,self->platform,static_cast<int64_t>(seconds));
 self->game.clear();self->platform.clear();self->core.clear();self->gameStarted=0;flush(self);
}
API void StationStats_shutdown(LocalUsage* self){if(self){StationStats_end(self,"",0,0,-1);flush(self);self->ready=false;}}
API void StationStats_event(LocalUsage* self,const std::string&,const std::string&){flush(self);}
API bool StationCore_request(Catalog* catalog){
 if(!catalog)return false;catalog->engineState[0]=0;catalog->engineState[1]=1;catalog->engineState[2]=0;
 *reinterpret_cast<int32_t*>(catalog->engineState+8)=0;
 *reinterpret_cast<std::string*>(catalog->engineState+0x38)="Este motor precisa ser incluido na atualizacao do aplicativo.";
 return false;
}
