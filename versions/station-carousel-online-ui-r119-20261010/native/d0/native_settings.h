// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Presentation only. Original tabs, value changes, scroll and saved settings stay native.
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
 setLongText(settingsThemeBlue,"APLICADO AO FUNDO CÉU");
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
  void*label=at<void*>(tab,0x30);if(label){place(label,w*.066f,y+settingsTextInset,w*.202f,tap*.68f,.74f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xDCEEFFff);}
 }
 float maxTabs=nt*tabStep-settingsTabClipHeight;if(maxTabs<0)maxTabs=0;at<float>(p,0x20ec)=maxTabs;if(at<float>(p,0x20e8)>maxTabs)at<float>(p,0x20e8)=maxTabs;
 for(U i=0;i<nr;i++){
  B*row=rows+i*0x48;float y=settingsContentY+i*rowStep;
  bounds(row,8,w*.323f,y,w*.405f,tap);bounds(row,0x18,w*.74f,y,w*.213f,tap);
  void*label=at<void*>(row,0x28),*value=at<void*>(row,0x38);
  if(label){place(label,w*.338f,y+settingsTextInset,w*.373f,tap*.68f,.74f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xEDF6FFff);}
  if(value){place(value,w*.752f,y+settingsTextInset,w*.189f,tap*.68f,.74f,1);fn<void(*)(void*,unsigned)>(0x2d2c48)(value,0x8BDEDCff);}
 }
 float content=nr*rowStep;if(content<settingsContentHeight)content=settingsContentHeight;at<float>(p,0x2130)=content;
 float maxRows=content-settingsContentHeight;if(at<float>(p,0x2128)>maxRows)at<float>(p,0x2128)=maxRows;
 place((B*)p+0x2138,w*.052f,h*.045f,w*.52f,tap,.86f,0);
 if(settingsBackOwner!=p){
  settingsEffectsGesture={};themeSwitchGesture={};settingsActionPressed=false;settingsBackOwner=p;
  settingsEffectsLabel=createInfoText(p,0xDCEEFFff);setLongText(settingsEffectsLabel,"EFEITOS GRÁFICOS");
  settingsBackText=createInfoText(p,0xEDF6FFff);setLongText(settingsBackText,"VOLTAR");
  settingsNetplayText=createInfoText(p,0xEDF6FFff);setLongText(settingsNetplayText,"ONLINE");
  settingsThemeLabel=createInfoText(p,0x9BB9D0ff);settingsThemeBlack=createInfoText(p,0xEDF6FFff);settingsThemeBlue=createInfoText(p,0x9BB9D0ff);settingsRefreshThemeLabels();
 }
 place(settingsEffectsLabel,settingsEffectsRect.x+w*.013f,settingsEffectsRect.y+settingsTextInset,settingsEffectsRect.w-w*.026f,tap*.68f,.67f,0);
 place(settingsThemeLabel,w*.063f,themeY+settingsTextInset,w*.236f,tap*.68f,.65f,0);
 place(settingsThemeBlack,w*.545f,themeY+settingsTextInset,w*.115f,tap*.68f,.69f,0);
 place(settingsThemeBlue,w*.69f,themeY+settingsTextInset,w*.25f,tap*.68f,.49f,0);
 place(settingsBackText,settingsBackRect.x,settingsBackRect.y,settingsBackRect.w,settingsBackRect.h,.72f,1);
 place(settingsNetplayText,settingsNetworkRect.x,settingsNetworkRect.y,settingsNetworkRect.w,settingsNetworkRect.h,.69f,1);
 place((B*)p+0x2268,w*.323f,h*.90f,w*.63f,h*.035f,.65f,0);
 fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2138,0xEDF6FFff);fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2268,0x9BB0C5ff);
 __android_log_print(4,"TurboCarousel","SETTINGS grouped layout; tabs=%lu; options=%lu; tap=%.1f; original actions retained",nt,nr,tap);
}
static void settingsSkinText(void*t){
 if(!settingsPainting||!gui)return;float w=at<float>(gui,0x54);
 for(B*r=at<B*>(gui,0x2110);r&&r<at<B*>(gui,0x2118);r+=0x48){
  bool label=t==at<void*>(r,0x28),value=t==at<void*>(r,0x38);if(!label&&!value)continue;
  float y=at<float>(r,12)-at<float>(gui,0x2128)+settingsTextInset;fn<void(*)(void*,float,float,float)>(0x277194)(t,w*(label?.338f:.752f),y,0);return;
 }
}
static bool settingsSkinRect(U caller,float x,float y,float w,float h,unsigned color){
 if(!settingsPainting)return false;
 if(caller==0x226ee8){
  rounded(x,y,w,h,0x071321ff);float sw=at<float>(gui,0x54),sh=at<float>(gui,0x58),gap=sh*.012f;
  rounded(sw*.043f,settingsContentY-gap,sw*.25f,settingsContentHeight+gap*2,0x0D2032ff);
  rounded(sw*.31f,settingsContentY-gap,sw*.647f,settingsContentHeight+gap*2,0x0C1D2Eff);
  rect(sw*.05f,settingsSkyRect.y-gap*.5f,sw*.90f,1.0f,0x36546F80);
  return true;
 }
 if(caller==0x226f14)return true;if(caller>=0x21a958&&caller<0x21b0c8)return true;
 if(caller==0x227134){bool selected=(color>>8)==0x147D32;rounded(x,y+2,w,h-4,selected?0x205169ff:0x132D43ff);if(selected)rect(x+3,y+h*.2f,2,h*.6f,0x78D7EDff);return true;}
 if(caller==0x22757c){rounded(x,y+2,w,h-4,0x142E43ff);return true;}
 if(caller==0x2275a8){rounded(x+2,y+2,w-2,h-4,0x21475Eff);return true;}
 if((caller>=0x2271ac&&caller<=0x22722c)||(caller>=0x22760c&&caller<=0x22768c)){if(w>h)h=1.5f;else w=1.5f;rect(x,y,w,h,0x78D7EDff);return true;}
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
 rounded(w*.053f,settingsSkyRect.y,w*.895f,settingsSkyRect.h,0x10283Cff);drawSettingsSkySwitch(p,matrix);
 auto e=settingsEffectsRect;rounded(e.x,e.y,e.w,e.h,0x205169ff);rect(e.x+3,e.y+e.h*.2f,2,e.h*.6f,0x78D7EDff);
 if(settingsEffectsLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsEffectsLabel,matrix);
 if(settingsThemeLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeLabel,matrix);
 if(settingsThemeBlack)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlack,matrix);
 if(settingsThemeBlue)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlue,matrix);
 auto n=settingsNetworkRect;rounded(n.x,n.y,n.w,n.h,0x17354Cff);if(settingsNetplayText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsNetplayText,matrix);
 auto b=settingsBackRect;rounded(b.x,b.y,b.w,b.h,0x245B73ff);if(settingsBackText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsBackText,matrix);
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
