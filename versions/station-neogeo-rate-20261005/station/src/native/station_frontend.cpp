#include "station_catalog_abi.hpp"
#include "station_collections.hpp"
#include "station_synopsis_pages.hpp"
#include "station_cover_retry.hpp"
#include "station_cover_plan.hpp"
#include "station_cover_publication.hpp"
#include "station_transfer_rate.hpp"
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
#include <chrono>
#include <android/log.h>
#include <cstdio>
#include <sys/stat.h>
#define API extern "C" __attribute__((visibility("default")))
namespace {
using station::Catalog;using station::Item;using station::Progress;
std::atomic<int> preparedItems{0},preparationTotal{0};std::atomic<int64_t> preparationBytes{0};std::atomic<bool> preparationCommitted{false};
JavaVM* vm=nullptr;jclass frontend=nullptr;
jmethodID configureMethod=nullptr,refreshMethod=nullptr,startMethod=nullptr,cancelMethod=nullptr;
jmethodID removeMethod=nullptr,coverMethod=nullptr,reconcileMethod=nullptr,authorizedMethod=nullptr,loginMethod=nullptr;
struct Env {
 JNIEnv* env=nullptr;bool attached=false;
 Env(){if(vm){int status=vm->GetEnv(reinterpret_cast<void**>(&env),JNI_VERSION_1_6);if(status==JNI_EDETACHED){attached=vm->AttachCurrentThread(&env,nullptr)==JNI_OK;if(!attached)env=nullptr;}}}
 ~Env(){if(attached)vm->DetachCurrentThread();}
};
struct Job {Progress progress;std::string message,launch;int result=0;double networkBytesPerSecond=0;};
struct CoverResult {std::string path;int result=0;int64_t retryMillis=0;};
std::atomic<bool> coversForeground{true};
struct Inbox {
 std::mutex mutex;std::atomic<bool> changed{false};
 bool hasCatalog=false;std::vector<Item> catalog;std::map<std::string,std::string> folderPaths;
 std::map<std::string,CoverResult> covers;std::map<std::string,Job> jobs;
 std::map<std::string,station::TransferRate> rates;
 std::string error,name;
} inbox;
struct State {
 Catalog* owner=nullptr;bool pending=false;
 std::map<std::string,std::string> folderPaths,pendingFolders;uint64_t folderRevision=0;
 std::vector<Item> catalog;
 std::map<std::string,Job> jobs;
 std::set<std::string> covers;
 station::CoverRetry coverRetry;station::CoverBackoff coverBackoff;std::vector<size_t> coverPlan;int64_t nextCoverSweep=0;
} state; // Only the SDL thread reads/writes this state.
int64_t coverTime(){return std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
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
 if(env->ExceptionCheck()){__android_log_print(6,"StationNative","Java command failed");env->ExceptionClear();accepted=false;}
 return accepted;
}
void changed(Catalog* catalog){++catalog->revision;catalog->installedCount=std::count_if(catalog->items.begin(),catalog->items.end(),[](const Item& item){return item.installed;});}
bool owned(Catalog* catalog){return catalog&&catalog==state.owner;}
Item* find(Catalog* catalog,const std::string& id){auto item=std::find_if(catalog->items.begin(),catalog->items.end(),[&](const Item& i){return i.id==id;});return item==catalog->items.end()?nullptr:&*item;}
bool active(){return std::any_of(state.jobs.begin(),state.jobs.end(),[](const auto& pair){return pair.second.progress.active;});}
void queueCovers(Catalog* catalog){
 if(!owned(catalog)||catalog->state!=2||!coversForeground.load(std::memory_order_acquire)||state.covers.size()>=4)return;
 int64_t now=coverTime();if(now<state.nextCoverSweep)return;
 // Completed responses reset this immediately; only an exhausted/retrying plan waits for the next sweep.
 state.nextCoverSweep=now+1;
 const auto& candidates=state.coverBackoff.prefetchAllowed(now)?state.coverPlan:catalog->priorities;
 for(size_t index:candidates){
  if(state.covers.size()>=4)break;if(index>=catalog->items.size())continue;Item& item=catalog->items[index];
  if(item.coverId.empty()||!item.coverPath.empty()||item.coverPending||!state.coverRetry.ready(item.id,coverTime()))continue;
  item.coverFailed=false;
  item.coverPending=true;state.covers.insert(item.id);
  if(!command(coverMethod,&item.id)){item.coverPending=false;item.coverFailed=true;state.coverRetry.failed(item.id,coverTime(),5);state.covers.erase(item.id);}
 }
}
void drain(Catalog* catalog){
 if(!owned(catalog)||!inbox.changed.load(std::memory_order_acquire))return;
 bool hasCatalog=false;std::vector<Item> next;std::map<std::string,std::string> folders;
 std::map<std::string,CoverResult> covers;std::map<std::string,Job> jobs;std::string failure;
 {std::lock_guard<std::mutex> lock(inbox.mutex);
  hasCatalog=inbox.hasCatalog;inbox.hasCatalog=false;if(hasCatalog){next.swap(inbox.catalog);folders.swap(inbox.folderPaths);}
  covers.swap(inbox.covers);jobs.swap(inbox.jobs);failure.swap(inbox.error);inbox.changed.store(false,std::memory_order_release);
 }
 if(hasCatalog){station::resetCoverPublication(state.covers,state.coverRetry,catalog->items,state.nextCoverSweep);catalog->unusedPending=std::move(next);state.pendingFolders=std::move(folders);state.pending=true;catalog->error.clear();__android_log_print(4,"StationNative","Catalog received items=%zu",catalog->unusedPending.size());}
 bool modified=false;
 for(auto& pair:covers){state.covers.erase(pair.first);Item* item=find(catalog,pair.first);if(!item)continue;
  CoverResult& result=pair.second;item->coverPending=false;modified=true;
  if(result.result==4)state.coverBackoff.rateLimited(coverTime(),result.retryMillis);
  if(result.result==0&&!result.path.empty()){item->coverReady=true;item->coverFailed=false;item->coverPath=std::move(result.path);state.coverRetry.succeeded(item->id);modified=true;}
  else if(result.result==1){item->coverFailed=false;state.coverRetry.succeeded(item->id);}
  else{item->coverFailed=true;state.coverRetry.failed(item->id,coverTime(),std::max<int64_t>(1,(result.retryMillis+999)/1000));}
  state.nextCoverSweep=0;
 }
 for(auto& pair:jobs){Item* item=find(catalog,pair.first);if(!item)continue;Job& job=pair.second;
  if(job.result==1&&!job.launch.empty()){item->localPath=job.launch;item->fileName=job.launch.substr(job.launch.find_last_of('/')+1);item->installed=true;modified=true;}
  else if(job.result==2){item->localPath.clear();item->fileName.clear();item->installed=false;modified=true;}
  state.jobs[pair.first]=std::move(job);
 }
 if(!failure.empty()){__android_log_print(6,"StationNative","Frontend error received");catalog->error=std::move(failure);if(catalog->items.empty())catalog->state=3;}
 if(modified)changed(catalog);
}
bool apply(Catalog* catalog){
 if(!owned(catalog)||!state.pending||active()||(catalog->engineState[0]&1))return false;
 for(auto& item:catalog->unusedPending){auto found=state.jobs.find(item.id);if(found==state.jobs.end())continue;
  const Job& job=found->second;
  if(job.result==1&&!job.launch.empty()){item.localPath=job.launch;item.fileName=job.launch.substr(job.launch.find_last_of('/')+1);item.installed=true;}
  else if(job.result==2){item.localPath.clear();item.fileName.clear();item.installed=false;}
 }
 catalog->items.swap(catalog->unusedPending);catalog->unusedPending.clear();state.folderPaths.swap(state.pendingFolders);state.pendingFolders.clear();++state.folderRevision;state.pending=false;__android_log_print(4,"StationNative","Catalog applied items=%zu",catalog->items.size());
 catalog->priorities.clear();state.coverPlan.clear();state.nextCoverSweep=0;state.covers.clear();state.coverRetry.clear();state.jobs.clear();
 catalog->state=2;catalog->error.clear();preparationCommitted=true;changed(catalog);return true;
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
API void Java_org_emulationstation_frontend_station_StationFrontend_publishPreparation(JNIEnv* env,jclass,jint done,jint total,jlong count){
 if(done<0||total<0||done>total||total>4096||count<0){error(env,"Invalid preparation counters");return;}
 if(done==0)preparationCommitted=false;preparationTotal=total;preparedItems=done;preparationBytes=count;
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishCatalog(JNIEnv* env,jclass,jobjectArray rows,jbyteArray name){
 try{
  if(!rows||env->GetArrayLength(rows)>4096)throw std::runtime_error("Catalog limit");
  std::vector<Item> items;std::set<std::string> seen;std::map<std::string,std::string> folders;
  for(jsize i=0;i<env->GetArrayLength(rows);++i){
   auto input=static_cast<jbyteArray>(env->GetObjectArrayElement(rows,i));std::string row;
   try{row=bytes(env,input,16384);}catch(...){if(input)env->DeleteLocalRef(input);throw;}env->DeleteLocalRef(input);
   std::string fields[6];size_t offset=0;
   for(auto& field:fields){size_t end=row.find('\0',offset);if(end==std::string::npos)throw std::runtime_error("Incomplete native catalog row");field=row.substr(offset,end-offset);offset=end+1;}
   std::string folderPath;
   if(offset<row.size()){size_t end=row.find('\0',offset);if(end==std::string::npos)throw std::runtime_error("Incomplete collection path");folderPath=row.substr(offset,end-offset);offset=end+1;}
   std::string description;
   if(offset<row.size()){size_t end=row.find('\0',offset);if(end==std::string::npos||end-offset>8000)throw std::runtime_error("Invalid description");description=row.substr(offset,end-offset);offset=end+1;}
   if(!station::validCollectionPath(folderPath))throw std::runtime_error("Invalid collection path");
   if(!folderPath.empty())folders.emplace(fields[0],std::move(folderPath));
   if(offset!=row.size()||!idValid(fields[0])||!idValid(fields[4])||!seen.insert(fields[0]).second)throw std::runtime_error("Invalid catalog identity");
   Item item;item.id=fields[0];item.name=fields[1];item.platform=fields[2];item.folder=fields[3];item.coverId=fields[4];item.localPath=fields[5];item.unusedGameUrl=station::synopsisPages(description);
   item.installed=!item.localPath.empty();if(item.installed)item.fileName=item.localPath.substr(item.localPath.find_last_of('/')+1);items.push_back(std::move(item));
  }
  std::string display=bytes(env,name,1024);std::lock_guard<std::mutex> lock(inbox.mutex);
  station::discardPreviousCoverResults(inbox.covers);
  inbox.catalog=std::move(items);inbox.folderPaths=std::move(folders);inbox.name=std::move(display);inbox.hasCatalog=true;inbox.changed.store(true,std::memory_order_release);
 }catch(const std::exception& failure){error(env,failure.what());}
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishCoverResult(JNIEnv* env,jclass,jstring id,jbyteArray path,jint result,jlong retryMillis){
 try{std::string key=identifier(env,id),value=bytes(env,path,8192);
  if(result<0||result>5||retryMillis<0||retryMillis>86400000||(result==0&&value.empty()))throw std::runtime_error("Invalid cover result");
  std::lock_guard<std::mutex> lock(inbox.mutex);
  if(inbox.covers.size()>=4096&&!inbox.covers.count(key))throw std::runtime_error("Cover queue limit");
  inbox.covers[key]={std::move(value),result,retryMillis};inbox.changed.store(true,std::memory_order_release);
 }catch(const std::exception& failure){error(env,failure.what());}
}
// Retained for the existing isolated JNI fixture; the app uses the typed completion above.
API void Java_org_emulationstation_frontend_station_StationFrontend_publishCover(JNIEnv* env,jclass cls,jstring id,jbyteArray path){
 bool present=path&&env->GetArrayLength(path)>0;
 Java_org_emulationstation_frontend_station_StationFrontend_publishCoverResult(env,cls,id,path,present?0:2,present?0:2000);
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishForeground(JNIEnv*,jclass,jboolean visible){
 coversForeground.store(visible==JNI_TRUE,std::memory_order_release);
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishJob(JNIEnv* env,jclass,jstring id,jboolean running,jlong received,jlong total,jbyteArray message,jbyteArray launch,jint result){
 try{std::string key=identifier(env,id);if(received<0||total< -1||result<0||result>3)throw std::runtime_error("Invalid job event");
  Job job;job.progress.active=running;job.progress.received=received;job.progress.total=total;job.message=bytes(env,message,4096);job.launch=bytes(env,launch,8192);job.result=result;
  if(result==3)job.progress.error=job.message;
  std::lock_guard<std::mutex> lock(inbox.mutex);if(inbox.jobs.size()>=4096&&!inbox.jobs.count(key))throw std::runtime_error("Job queue limit");
  if(running&&job.message=="Baixando"){
   auto now=std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
   job.networkBytesPerSecond=inbox.rates[key].observe(received,total,static_cast<uint64_t>(now));
  }else inbox.rates.erase(key);
  inbox.jobs[key]=std::move(job);inbox.changed.store(true,std::memory_order_release);
 }catch(const std::exception& failure){error(env,failure.what());}
}
API void Java_org_emulationstation_frontend_station_StationFrontend_publishError(JNIEnv* env,jclass,jbyteArray message){
 try{std::string text=bytes(env,message,4096);std::lock_guard<std::mutex> lock(inbox.mutex);inbox.error=std::move(text);inbox.changed.store(true,std::memory_order_release);}
 catch(const std::exception& failure){error(env,failure.what());}
}
// Service entry points called by the retained native renderer. No HTTP, URLs or filesystem heuristics.
API void StationCatalog_refresh(Catalog* catalog,const std::string&){
 if(!catalog)return;if(state.owner&&state.owner!=catalog)return;__android_log_print(4,"StationNative","Catalog refresh entered");bool initial=state.owner==nullptr;state.owner=catalog;
 if(catalog->items.empty())catalog->state=1;
 using Root=std::string(*)();void* mainLibrary=dlopen("libmain.so",RTLD_NOW|RTLD_NOLOAD);auto root=mainLibrary?reinterpret_cast<Root>(dlsym(mainLibrary,"_ZN14CatalogService11getRomsRootEv")):nullptr;
 if(!root){__android_log_print(6,"StationNative","Roms root export missing");catalog->state=3;catalog->error="Pasta de jogos indisponivel.";return;}
 std::string folder=root();dlclose(mainLibrary);__android_log_print(4,"StationNative","Configure root bytes=%zu",folder.size());
 if(!command(configureMethod,&folder)||(!initial&&!command(refreshMethod))){catalog->state=3;catalog->error="Nao foi possivel iniciar o catalogo Station.";}
}
API void StationCatalog_update(Catalog* catalog){drain(catalog);if(owned(catalog)&&catalog->items.empty())apply(catalog);queueCovers(catalog);}
API bool StationCatalog_applyPending(Catalog* catalog){drain(catalog);return apply(catalog);}
API void StationCatalog_refreshInstalled(Catalog* catalog){if(owned(catalog))command(reconcileMethod);}
API void StationCatalog_prioritize(Catalog* catalog,const std::vector<size_t>& indices){
 if(!owned(catalog))return;
 std::vector<size_t> next(indices.begin(),indices.begin()+std::min<size_t>(indices.size(),64));
 if(next!=catalog->priorities){catalog->priorities=std::move(next);state.coverPlan=station::coverPlan(catalog->items,catalog->priorities);state.nextCoverSweep=0;}
 queueCovers(catalog);
}
API bool StationCatalog_start(Catalog* catalog,size_t index){
 if(!owned(catalog)||index>=catalog->items.size())return false;const std::string& id=catalog->items[index].id;
 if(state.jobs[id].progress.active)return false;if(!command(startMethod,&id,true))return false;
 Job job;job.progress.active=true;state.jobs[id]=std::move(job);return true;
}
// Collection readers run on the same SDL thread that commits catalog snapshots.
// Returned text is borrowed until the next apply; callers must not retain it.
API uint64_t StationCatalog_folderRevision(){return state.folderRevision;}
API const char* StationCatalog_itemFolderPath(const char* id){
 if(!id)return "";auto it=state.folderPaths.find(id);return it==state.folderPaths.end()?"":it->second.c_str();
}
using FolderVisitor=void(*)(void*,const char*,const char*,size_t,const char*);
API int StationCatalog_visitFolders(const char* platform,const char* parent,size_t* direct,FolderVisitor visitor,void* context){
 if(direct)*direct=0;if(!state.owner||!platform||!parent)return 0;
 auto listing=station::collectionListing(state.owner->items,state.folderPaths,platform,parent);
 if(direct)*direct=listing.direct;
 if(visitor)for(const auto& pair:listing.children){const auto& node=pair.second;visitor(context,node.path.c_str(),node.name.c_str(),node.count,node.cover.c_str());}
 return static_cast<int>(listing.children.size());
}
API void StationCatalog_cancel(Catalog* catalog,size_t index){if(owned(catalog)&&index<catalog->items.size())command(cancelMethod,&catalog->items[index].id);}
API bool StationCatalog_uninstall(Catalog* catalog,size_t index){return owned(catalog)&&index<catalog->items.size()&&command(removeMethod,&catalog->items[index].id,true);}
API std::vector<size_t> StationCatalog_active(Catalog* catalog){std::vector<size_t> result;if(owned(catalog))for(size_t i=0;i<catalog->items.size();++i){auto job=state.jobs.find(catalog->items[i].id);if(job!=state.jobs.end()&&job->second.progress.active)result.push_back(i);}return result;}
API Progress StationCatalog_progress(Catalog* catalog,size_t index){if(owned(catalog)&&index<catalog->items.size()){auto job=state.jobs.find(catalog->items[index].id);if(job!=state.jobs.end())return job->second.progress;}return {};}
API double StationDownload_networkRate(int64_t received,int64_t total){
 for(const auto& entry:state.jobs){const auto& job=entry.second;
  if(job.progress.active&&job.progress.received==received&&job.progress.total==total&&job.message=="Baixando")return job.networkBytesPerSecond;
 }return -1;
}

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

namespace {
template<class T>T renderer(uintptr_t offset){
 static uintptr_t base=[](){auto symbol=mainSymbol<void*>("_ZN14CatalogServiceC1Ev");Dl_info info{};return symbol&&dladdr(symbol,&info)?reinterpret_cast<uintptr_t>(info.dli_fbase):uintptr_t(0);}();
 return reinterpret_cast<T>(base+offset);
}
template<class T>T& field(void* p,size_t offset){return *reinterpret_cast<T*>(static_cast<uint8_t*>(p)+offset);}
struct V2{float x,y;};struct V3{float x,y,z;};
void* loadingOwner=nullptr;void* loadingLabels[4]{};std::string loadingTexts[4];float shownPercent=0,lastDrawTime=0;
void loadingText(void* owner,int slot,const std::string& value,const void* matrix,float x,float y,float w,float h,float scale,unsigned color){
 if(loadingOwner!=owner){loadingOwner=owner;for(int i=0;i<4;++i){loadingLabels[i]=nullptr;loadingTexts[i].clear();}shownPercent=0;lastDrawTime=0;}
 void*& label=loadingLabels[slot];
 if(!label){
  label=renderer<void*(*)(size_t)>(0x39d9c0)(0x130);std::string empty;
  renderer<void(*)(void*,void*,const std::string&,const void*,unsigned,int,V3,V2,unsigned)>(0x2d2a04)(label,field<void*>(owner,0x10),empty,static_cast<uint8_t*>(owner)+0x928+0xe8,color,0,V3{0,0,0},V2{0,0},0);
  renderer<void(*)(void*,void*)>(0x2772c8)(owner,label);
 }
 if(loadingTexts[slot]!=value){renderer<void(*)(void*,const std::string&)>(0x2d2c70)(label,value);loadingTexts[slot]=value;}
 if(field<float>(label,0x38)!=x||field<float>(label,0x3c)!=y||field<float>(label,0x54)!=w/scale||field<float>(label,0x58)!=h/scale){
  renderer<void(*)(void*,float,float)>(0x2771b0)(label,0,0);
  renderer<void(*)(void*,float)>(0x277200)(label,scale);
  renderer<void(*)(void*,float,float,float)>(0x277194)(label,x,y,0);
  renderer<void(*)(void*,float,float)>(0x2771d8)(label,w/scale,h/scale);
  renderer<void(*)(void*,int)>(0x2d38d8)(label,1);renderer<void(*)(void*,int)>(0x2d38e8)(label,1);
 }
 // Owned by GuiStore for destruction, visible only during this explicit loading draw.
 renderer<void(*)(void*,bool)>(0x277228)(label,true);
 renderer<void(*)(void*,const void*)>(0x2d2dc4)(label,matrix);
 renderer<void(*)(void*,bool)>(0x277228)(label,false);
 renderer<void(*)(const void*)>(0x2e5640)(matrix);
}
}
API void StationLoading_draw(void* gui,const void* matrix){
 if(!gui||!matrix)return;
 const float w=field<float>(gui,0x54),h=field<float>(gui,0x58),time=field<float>(gui,0x374);
 const int done=preparedItems.load(),total=preparationTotal.load();const bool committed=preparationCommitted.load();
 const float target=committed?100.0f:(total?100.0f*done/(total+1):0.0f);
 // Visual interpolation is always bounded by completed work, never estimated elapsed progress.
 float elapsed=std::max(0.0f,std::min(100.0f,time-lastDrawTime));lastDrawTime=time;
 shownPercent=std::min(target,shownPercent+elapsed*.16f);
 bool failed=state.owner&&state.owner->state==3;
 auto rect=renderer<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38);
 renderer<void(*)(const void*)>(0x2e5640)(matrix);
 rect(w*.19f,h*.35f,w*.62f,h*.30f,0x07110de8,0x07110de8,false,4,5);
 rect(w*.23f,h*.50f,w*.54f,h*.018f,0x21392bff,0x21392bff,false,4,5);
 if(shownPercent>0)rect(w*.23f,h*.50f,w*.54f*shownPercent/100.0f,h*.018f,0x35ee75ff,0x8aff99ff,true,4,5);
 const std::string title=failed?"CARREGAMENTO INTERROMPIDO":committed?"BIBLIOTECA PREPARADA":"PREPARANDO SUA BIBLIOTECA";
 char percent[32];std::snprintf(percent,sizeof(percent),"%d%%",static_cast<int>(shownPercent));
 char count[160];std::snprintf(count,sizeof(count),"%d / %d jogos preparados   |   %.1f KiB de dados",done,total,preparationBytes.load()/1024.0);
 std::string detail=failed?state.owner->error:(total?count:"Aguardando catalogo autenticado...");
 loadingText(gui,0,title,matrix,w*.23f,h*.385f,w*.54f,h*.06f,.9f,0xf1fff5ff);
 loadingText(gui,1,percent,matrix,w*.23f,h*.442f,w*.54f,h*.05f,.85f,0x6cf696ff);
 loadingText(gui,2,detail,matrix,w*.23f,h*.537f,w*.54f,h*.055f,.68f,failed?0xff8e86ff:0xb4d4bfff);
 loadingText(gui,3,"TURBORAMA STATION",matrix,w*.23f,h*.592f,w*.54f,h*.035f,.5f,0x789c84ff);
}
