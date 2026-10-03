#include "../src/native/station_frontend.cpp"
API jint Java_org_emulationstation_frontend_station_StationFrontendDeviceTest_run(JNIEnv* env,jclass){
 int count=0;
 auto check=[&](bool ok,const char* message){if(!ok)throw std::runtime_error(message);++count;};
 auto byteArray=[&](const std::string& value){jbyteArray result=env->NewByteArray(value.size());env->SetByteArrayRegion(result,0,value.size(),reinterpret_cast<const jbyte*>(value.data()));return result;};
 auto publish=[&](const std::vector<std::string>& ids){
  jclass cls=env->FindClass("[B");jobjectArray rows=env->NewObjectArray(ids.size(),cls,nullptr);env->DeleteLocalRef(cls);
  for(size_t i=0;i<ids.size();++i){std::string value;for(const std::string& text:{ids[i],std::string("Game"),std::string("Nintendo"),std::string("nes"),std::string("cover001"),std::string("")}){value+=text;value+='\0';}
   jbyteArray row=byteArray(value);env->SetObjectArrayElement(rows,i,row);env->DeleteLocalRef(row);}
  jbyteArray name=byteArray("Test");Java_org_emulationstation_frontend_station_StationFrontend_publishCatalog(env,nullptr,rows,name);env->DeleteLocalRef(rows);env->DeleteLocalRef(name);
 };
 auto job=[&](bool active,int result,const std::string& launch){
  jstring id=env->NewStringUTF("item0001");jbyteArray text=byteArray(result==3?"Error":""),path=byteArray(launch);
  Java_org_emulationstation_frontend_station_StationFrontend_publishJob(env,nullptr,id,active,50,100,text,path,result);
  env->DeleteLocalRef(id);env->DeleteLocalRef(text);env->DeleteLocalRef(path);
 };
 Catalog catalog{};state=State{};state.owner=&catalog;
 try{
  check(sizeof(catalog)==0x138,"catalog ABI");check(sizeof(Item)==0xe8,"item ABI");check(sizeof(Progress)==48,"progress ABI");
  publish({"item0001","item0002"});check(!env->ExceptionCheck(),"catalog JNI");
  StationCatalog_update(&catalog);check(catalog.state==2&&catalog.items.size()==2,"initial catalog");check(catalog.revision==1,"initial revision");check(preparationCommitted.load(),"100 percent only after native commit");
  check(catalog.items[0].unusedGameUrl.empty(),"no invented game URL");check(catalog.items[0].coverId=="cover001","opaque cover identity");
  jstring id=env->NewStringUTF("item0001");jbyteArray cover=byteArray("/private/covers/cover001-r1.png");
  Java_org_emulationstation_frontend_station_StationFrontend_publishCover(env,nullptr,id,cover);env->DeleteLocalRef(id);env->DeleteLocalRef(cover);
  StationCatalog_update(&catalog);check(catalog.items[0].coverReady&&!catalog.items[0].coverFailed,"cover ready");check(catalog.items[0].coverPath=="/private/covers/cover001-r1.png","cover path");
  job(true,0,"");StationCatalog_update(&catalog);check(StationCatalog_active(&catalog)==std::vector<size_t>{0},"active download");check(StationCatalog_progress(&catalog,0).received==50,"download progress");
  publish({"item0002","item0001"});StationCatalog_update(&catalog);check(catalog.unusedPending.size()==2,"renderer sees pending publication");check(!StationCatalog_applyPending(&catalog),"do not reorder active downloads");
  job(false,1,"/roms/install/content/game.bin");StationCatalog_update(&catalog);check(catalog.items[0].installed,"commit installation");check(catalog.installedCount==1,"installed count");
  check(StationCatalog_applyPending(&catalog),"apply idle catalog");check(catalog.items[1].id=="item0001"&&catalog.items[1].installed,"preserve committed installation on refresh");
  job(false,3,"");StationCatalog_update(&catalog);check(catalog.items[1].installed,"failed update preserves installed item");check(StationCatalog_progress(&catalog,1).error=="Error","failure reported");
  job(false,2,"");StationCatalog_update(&catalog);check(!catalog.items[1].installed&&catalog.installedCount==0,"explicit deletion");
  publish({"item0001","item0001"});check(env->ExceptionCheck(),"duplicate catalog rejected");env->ExceptionClear();
  publish({"bad"});check(env->ExceptionCheck(),"invalid id rejected");env->ExceptionClear();
  publish({});StationCatalog_update(&catalog);check(StationCatalog_applyPending(&catalog),"empty catalog published");check(catalog.items.empty()&&catalog.state==2,"empty catalog ready");
  check(!StationCatalog_start(&catalog,0),"invalid index rejected");
  check(StationCatalog_active(&catalog).empty(),"no active job after catalog replacement");
  std::vector<std::string> many;many.reserve(station::MaximumCatalogItems);
  for(size_t i=0;i<station::MaximumCatalogItems;++i)many.push_back("capacity_"+std::to_string(100000+i));
  publish(many);check(!env->ExceptionCheck(),"40000 rows JNI accepted");StationCatalog_update(&catalog);
  check(catalog.items.size()==40000&&state.indices.size()==40000,"40000 rows applied and indexed");
  check(find(&catalog,"capacity_139999")==&catalog.items.back(),"Last row lookup exact");
  check(StationCatalog_active(&catalog).empty(),"Idle large catalog has no active work");
  Java_org_emulationstation_frontend_station_StationFrontend_publishPreparation(env,nullptr,40000,40000,5000000);
  check(!env->ExceptionCheck()&&preparedItems.load()==40000,"Large preparation count accepted");
  many.push_back("capacity_140000");publish(many);check(env->ExceptionCheck(),"40001 rows JNI rejected");env->ExceptionClear();
  check(catalog.items.size()==40000,"Oversized publication preserves current catalog");
 }catch(const std::exception& failure){error(env,failure.what());count=0;}
 state=State{};return count;
}
