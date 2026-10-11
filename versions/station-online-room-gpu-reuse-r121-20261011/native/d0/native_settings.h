// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Console presentation only. Original tabs, value changes, scroll and saved settings stay native.
static bool settingsPainting;
static void*settingsBackText;static void*settingsBackOwner;
static void*settingsNetplayText;
static void*settingsEffectsLabel;
static StationThemeToggleGesture settingsEffectsGesture;
static void*settingsThemeLabel;static void*settingsThemeBlack;static void*settingsThemeBlue;
static StationThemeRect settingsEffectsRect,settingsBackRect,settingsNetworkRect,settingsSkyRect;
static float settingsContentY,settingsContentHeight,settingsTabClipHeight,settingsTapHeight,settingsTextInset;
static bool settingsActionPressed;static U settingsActionFinger;static int settingsPressedAction;

// Resolve Android dp only when the settings owner/size changes. No JNI per frame.
static float settingsMinimumTarget(float w,float h){
 float target=h*.12f;JNIEnv*env=videoEnv();if(!env)return target;
 jobject activity=videoActivity();if(!activity)return target;
 jclass activityClass=nullptr,resourcesClass=nullptr,metricsClass=nullptr;jobject resources=nullptr,metrics=nullptr;
 do{
  activityClass=env->GetObjectClass(activity);if(!activityClass||env->ExceptionCheck())break;
  jmethodID getResources=env->GetMethodID(activityClass,"getResources","()Landroid/content/res/Resources;");if(!getResources||env->ExceptionCheck())break;
  resources=env->CallObjectMethod(activity,getResources);if(!resources||env->ExceptionCheck())break;
  resourcesClass=env->GetObjectClass(resources);if(!resourcesClass||env->ExceptionCheck())break;
  jmethodID getMetrics=env->GetMethodID(resourcesClass,"getDisplayMetrics","()Landroid/util/DisplayMetrics;");if(!getMetrics||env->ExceptionCheck())break;
  metrics=env->CallObjectMethod(resources,getMetrics);if(!metrics||env->ExceptionCheck())break;
  metricsClass=env->GetObjectClass(metrics);if(!metricsClass||env->ExceptionCheck())break;
  jfieldID densityField=env->GetFieldID(metricsClass,"density","F");if(!densityField||env->ExceptionCheck())break;
  jfieldID widthField=env->GetFieldID(metricsClass,"widthPixels","I");if(!widthField||env->ExceptionCheck())break;
  float density=env->GetFloatField(metrics,densityField);int pixels=env->GetIntField(metrics,widthField);
  if(!env->ExceptionCheck()&&density>0&&pixels>0&&w>0)target=48.f*density*w/pixels;
 }while(false);
 if(env->ExceptionCheck())env->ExceptionClear();
 if(metricsClass)env->DeleteLocalRef(metricsClass);if(metrics)env->DeleteLocalRef(metrics);
 if(resourcesClass)env->DeleteLocalRef(resourcesClass);if(resources)env->DeleteLocalRef(resources);
 if(activityClass)env->DeleteLocalRef(activityClass);env->DeleteLocalRef(activity);return target;
}
static void settingsRefreshThemeLabels(bool failed=false){
 if(!settingsThemeLabel)return;
 setLongText(settingsThemeLabel,failed?"COR: FALHA AO SALVAR":"COR DO CÉU");
 setLongText(settingsThemeBlack,stationThemeId==0?"PRETO":"AZUL");
 setLongText(settingsThemeBlue,"ESTILO DO FUNDO CÉU");
}
static void requestSettingsClose(void*p){
 themeSwitchGesture={};settingsEffectsGesture={};settingsActionPressed=false;
 if(!at<B>(p,0x2050))return;
 handledBack=true;lastBackTick=fn<unsigned(*)()>(0x39e240)();at<B>(p,0x1ac)=1;
 log("SETTINGS close requested");
}
static void settingsClosedHook(void*p){themeSwitchGesture={};settingsEffectsGesture={};settingsActionPressed=false;fn<V>(0x21dd24)(p);log("SETTINGS closed; original values retained");}

static void layoutSettingsSkin(void*p){
 if(!at<B>(p,0x2050))return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 B*tabs=at<B*>(p,0x2078),*tabsEnd=at<B*>(p,0x2080),*rows=at<B*>(p,0x2110),*rowsEnd=at<B*>(p,0x2118);
 static void*owner;static B*oldTabs;static B*oldRows;static U oldTabsSize,oldRowsSize;static const void*firstLabel;static float oldW,oldH;
 U nt=tabs?(tabsEnd-tabs)/0x40:0,nr=rows?(rowsEnd-rows)/0x48:0;const void*first=nr?at<void*>(rows,0x28):nullptr;
 bool changed=owner!=p||w!=oldW||h!=oldH||tabs!=oldTabs||rows!=oldRows||nt!=oldTabsSize||nr!=oldRowsSize||first!=firstLabel||at<float>(p,0x2054)!=w*.025f||at<float>(p,0x205c)!=w*.95f;
 if(!changed&&nr&&at<float>(rows,8)!=w*.323f)changed=true;if(!changed)return;
 bool ownerChanged=owner!=p||w!=oldW||h!=oldH;
 owner=p;oldW=w;oldH=h;oldTabs=tabs;oldRows=rows;oldTabsSize=nt;oldRowsSize=nr;firstLabel=first;
 if(ownerChanged||settingsTapHeight<=0)settingsTapHeight=settingsMinimumTarget(w,h);
 float gap=h*.012f,tap=settingsTapHeight;
 settingsBackRect={w*.825f,h*.045f,w*.128f,tap};settingsNetworkRect={w*.635f,h*.045f,w*.173f,tap};
 float themeY=h*.045f+tap+gap,themeHeight=tap+gap;
 settingsSkyRect={w*.323f,themeY,w*.205f,tap};
 settingsContentY=themeY+themeHeight+h*.022f;settingsContentHeight=h*.87f-settingsContentY;
 if(settingsContentHeight<tap*2+gap)settingsContentHeight=tap*2+gap;
 settingsTabClipHeight=settingsContentHeight-tap-gap;
 settingsEffectsRect={w*.053f,settingsContentY+settingsTabClipHeight+gap,w*.229f,tap};
 settingsTextInset=tap*.16f;
 bounds(p,0x2054,w*.025f,h*.025f,w*.95f,h*.95f);
 bounds(p,0x20d8,w*.045f,settingsContentY,w*.246f,settingsTabClipHeight);
 bounds(p,0x2064,w*.323f,settingsContentY,w*.63f,settingsContentHeight);
 float tabStep=tap+gap,rowStep=tap+gap;
 for(U i=0;i<nt;i++){
  B*tab=tabs+i*0x40;float y=settingsContentY+i*tabStep;
  bounds(tab,0x18,w*.053f,y,w*.229f,tap);at<float>(tab,0x28)=y+settingsTextInset;
  void*label=at<void*>(tab,0x30);if(label){place(label,w*.066f,y+settingsTextInset,w*.202f,tap*.68f,.74f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xEFF5FFff);}
 }
 float maxTabs=nt*tabStep-settingsTabClipHeight;if(maxTabs<0)maxTabs=0;at<float>(p,0x20ec)=maxTabs;if(at<float>(p,0x20e8)>maxTabs)at<float>(p,0x20e8)=maxTabs;
 for(U i=0;i<nr;i++){
  B*row=rows+i*0x48;float y=settingsContentY+i*rowStep;
  bounds(row,8,w*.323f,y,w*.405f,tap);bounds(row,0x18,w*.74f,y,w*.213f,tap);
  void*label=at<void*>(row,0x28),*value=at<void*>(row,0x38);
  if(label){place(label,w*.338f,y+settingsTextInset,w*.373f,tap*.68f,.74f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xEFF5FFff);}
  if(value){place(value,w*.752f,y+settingsTextInset,w*.189f,tap*.68f,.74f,1);fn<void(*)(void*,unsigned)>(0x2d2c48)(value,0x46DBFFff);}
 }
 float content=nr*rowStep;if(content<settingsContentHeight)content=settingsContentHeight;at<float>(p,0x2130)=content;
 float maxRows=content-settingsContentHeight;if(at<float>(p,0x2128)>maxRows)at<float>(p,0x2128)=maxRows;
 place((B*)p+0x2138,w*.052f,h*.045f,w*.52f,tap,.86f,0);
 if(settingsBackOwner!=p){
  settingsEffectsGesture={};themeSwitchGesture={};settingsActionPressed=false;settingsBackOwner=p;
  settingsEffectsLabel=createInfoText(p,0xEFF5FFff);setLongText(settingsEffectsLabel,"EFEITOS GRÁFICOS");
  settingsBackText=createInfoText(p,0xEFF5FFff);setLongText(settingsBackText,"VOLTAR");
  settingsNetplayText=createInfoText(p,0xEFF5FFff);setLongText(settingsNetplayText,"ONLINE");
  settingsThemeLabel=createInfoText(p,0x9EAABCff);settingsThemeBlack=createInfoText(p,0x46DBFFff);settingsThemeBlue=createInfoText(p,0x9EAABCff);settingsRefreshThemeLabels();
 }
 place(settingsEffectsLabel,settingsEffectsRect.x+w*.013f,settingsEffectsRect.y+settingsTextInset,settingsEffectsRect.w-w*.026f,tap*.68f,.67f,0);
 place(settingsThemeLabel,w*.063f,themeY+settingsTextInset,w*.236f,tap*.68f,.65f,0);
 place(settingsThemeBlack,w*.545f,themeY+settingsTextInset,w*.115f,tap*.68f,.69f,0);
 place(settingsThemeBlue,w*.69f,themeY+settingsTextInset,w*.25f,tap*.68f,.49f,0);
 place(settingsBackText,settingsBackRect.x,settingsBackRect.y,settingsBackRect.w,settingsBackRect.h,.72f,1);
 place(settingsNetplayText,settingsNetworkRect.x,settingsNetworkRect.y,settingsNetworkRect.w,settingsNetworkRect.h,.69f,1);
 place((B*)p+0x2268,w*.323f,h*.90f,w*.63f,h*.035f,.65f,0);
 fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2138,0xEFF5FFff);fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2268,0x9EAABCff);
 __android_log_print(4,"TurboCarousel","SETTINGS grouped layout; tabs=%lu; options=%lu; tap=%.1f; original actions retained",nt,nr,tap);
}
static void settingsSkinText(void*t){
 if(!settingsPainting||!gui)return;float w=at<float>(gui,0x54);
 for(B*r=at<B*>(gui,0x2110);r&&r<at<B*>(gui,0x2118);r+=0x48){
  bool label=t==at<void*>(r,0x28),value=t==at<void*>(r,0x38);if(!label&&!value)continue;
  float y=at<float>(r,12)-at<float>(gui,0x2128)+settingsTextInset;fn<void(*)(void*,float,float,float)>(0x277194)(t,w*(label?.338f:.752f),y,0);return;
 }
}
// Flat rails use the same untextured primitive program/matrix/scissor/blend as rounded().
// Six fixed quads are batched in one draw; no shadow/FBO/filter or heap allocation.
static void settingsConsoleCard(float x,float y,float w,float h,unsigned fill,unsigned rim,unsigned rail=0){
 if(w<=0||h<=0)return;
 if(mappingCover){rect(x,y,w,h,fill);rect(x,y,w,1.5f,rim);rect(x,y+h-1.5f,w,1.5f,rim);rect(x,y,1.5f,h,rim);rect(x+w-1.5f,y,1.5f,h,rim);if(rail)rect(x+3,y+h*.19f,3,h*.62f,rail);return;}
 Vertex vertices[34];unsigned count=0;
 auto append=[&](float rx,float ry,float rw,float rh,unsigned color){
  if(rw<=0||rh<=0)return;unsigned packed=fn<unsigned(*)(unsigned)>(0x2e3980)(stationThemeColor(color));
  Vertex q[4]={{rx,ry,0,0,packed},{rx,ry+rh,0,0,packed},{rx+rw,ry,0,0,packed},{rx+rw,ry+rh,0,0,packed}};
  for(int i=0;i<4;i++)fn<V>(0x2e1a08)(&q[i]);
  if(count){vertices[count]=vertices[count-1];count++;vertices[count++]=q[0];}
  for(int i=0;i<4;i++)vertices[count++]=q[i];
 };
 float edge=1.5f;append(x,y,w,h,fill);
 append(x,y,w,edge,rim);append(x,y+h-edge,w,edge,rim);append(x,y,edge,h,rim);append(x+w-edge,y,edge,h,rim);
 if(rail)append(x+3,y+h*.19f,3,h*.62f,rail);
 fn<void(*)(unsigned)>(0x2e52e8)(0);fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(vertices,count,4,5);
}
static bool settingsSkinRect(U caller,float x,float y,float w,float h,unsigned color){
 if(!settingsPainting)return false;
 if(caller==0x226ee8){
  rect(x,y,w,h,0x06080Dff);float sw=at<float>(gui,0x54),sh=at<float>(gui,0x58),gap=sh*.012f;
  rect(sw*.043f,settingsContentY-gap,sw*.25f,settingsContentHeight+gap*2,0x101620ff);
  rect(sw*.304f,settingsContentY-gap,1.0f,settingsContentHeight+gap*2,0x334153ff);
  rect(sw*.05f,settingsSkyRect.y-gap*.5f,sw*.90f,1.0f,0x334153ff);
  rect(sw*.052f,sh*.032f,sw*.044f,2.f,0x46DBFFff);
  rect(sw*.101f,sh*.032f,sw*.014f,2.f,0x244EB3ff);
  return true;
 }
 if(caller==0x226f14)return true;if(caller>=0x21a958&&caller<0x21b0c8)return true;
 if(caller==0x227134){bool selected=(color>>8)==0x147D32;settingsConsoleCard(x,y+2,w,h-4,selected?0x14283Fff:0x101620ff,selected?0x3C728Eff:0x25303Eff,selected?0x46DBFFff:0);return true;}
 if(caller==0x22757c){float full=at<float>(gui,0x54)*.63f;rect(x,y+2,full,h-4,0x151F2Eff);rect(x,y+h-2,full,1,0x25303Eff);return true;}
 if(caller==0x2275a8){rect(x,y+8,1,h-16,0x334153ff);return true;}
 if((caller>=0x2271ac&&caller<=0x22722c)||(caller>=0x22760c&&caller<=0x22768c)){if(w>h)h=2.f;else w=2.f;rect(x,y,w,h,0xEFF5FFff);return true;}
 return false;
}
static void drawSettingsSkySwitch(void*p,void*matrix){
 auto r=settingsSkyRect;unsigned now=fn<unsigned(*)()>(0x39e240)();
 unsigned frame=stationGraphicsEnabled(8)&&stationGraphicsEnabled(32)?stationThemeTransition.frame(stationThemeId,now):(stationThemeId?0u:85u);
 fn<void(*)(const void*)>(0x2e5640)(matrix);float bh=r.h*1.16f,bw=bh*384.f/216.f;
 drawStationLottie(0,frame,{r.x,r.y+(r.h-bh)*.5f,bw,bh});
}
static void drawSettingsSkinHook(void*p,void*matrix){
 if(!at<B>(p,0x2050))return;layoutSettingsSkin(p);
 static unsigned themeRevision=~0u;if(themeRevision!=stationThemeRevision){themeRevision=stationThemeRevision;settingsRefreshThemeLabels();}
 settingsPainting=true;fn<void(*)(void*,void*)>(0x226e5c)(p,matrix);settingsPainting=false;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);fn<void(*)(const void*)>(0x2e5640)(matrix);
 rect(w*.053f,settingsSkyRect.y,w*.895f,settingsSkyRect.h,0x101722ff);rect(w*.053f,settingsSkyRect.y+settingsSkyRect.h-1,w*.895f,1,0x25303Eff);drawSettingsSkySwitch(p,matrix);
 auto e=settingsEffectsRect;settingsConsoleCard(e.x,e.y,e.w,e.h,0x142038ff,0x3C728Eff,0x46DBFFff);
 if(settingsEffectsLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsEffectsLabel,matrix);
 if(settingsThemeLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeLabel,matrix);
 if(settingsThemeBlack)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlack,matrix);
 if(settingsThemeBlue)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlue,matrix);
 auto n=settingsNetworkRect;bool networkPressed=settingsActionPressed&&settingsPressedAction==2;settingsConsoleCard(n.x,n.y,n.w,n.h,networkPressed?0x3262C8ff:0x244EB3ff,networkPressed?0xEFF5FFff:0x3C728Eff);if(settingsNetplayText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsNetplayText,matrix);
 auto b=settingsBackRect;bool backPressed=settingsActionPressed&&settingsPressedAction==1;settingsConsoleCard(b.x,b.y,b.w,b.h,backPressed?0x244EB3ff:0x151F2Eff,backPressed?0xEFF5FFff:0x334153ff);if(settingsBackText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsBackText,matrix);
}
static bool touchSettingsSkinHook(void*p,const void*event){
 layoutSettingsSkin(p);float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 int effectsAction=settingsEffectsGesture.touch(type,id,x,y,settingsEffectsRect);if(effectsAction>=0){if(effectsAction==1)openGraphicsPanel();return true;}
 int skyAction=themeSwitchGesture.touch(type,id,x,y,settingsSkyRect);
 if(skyAction>=0){if(skyAction==1){stationThemeSaveFailed=!stationThemeChoose(1-stationThemeId);settingsRefreshThemeLabels(stationThemeSaveFailed);}return true;}
 bool inside=stationThemeContains(settingsBackRect,x,y),network=stationThemeContains(settingsNetworkRect,x,y);
 if(type==0){settingsActionPressed=inside||network;settingsPressedAction=network?2:1;settingsActionFinger=id;if(settingsActionPressed)return true;}
 if(settingsActionPressed&&id==settingsActionFinger){
  if(type!=1&&type!=2){settingsActionPressed=false;return true;}
  if(type==2){settingsActionPressed=false;if(settingsPressedAction==1&&inside)requestSettingsClose(p);else if(settingsPressedAction==2&&network&&openStationNetplay())requestSettingsClose(p);}return true;
 }
 return fn<bool(*)(void*,const void*)>(0x2269fc)(p,event);
}
