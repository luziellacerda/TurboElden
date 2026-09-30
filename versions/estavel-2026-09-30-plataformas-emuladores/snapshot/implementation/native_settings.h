// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Native settings presentation. Tabs, options, value changes, persistence and input
// continue through the original GuiStore routines; only geometry and drawing change.
static bool settingsPainting;
static void*settingsBackText;static void*settingsBackOwner;
static void requestSettingsClose(void*p){
 if(!at<B>(p,0x2050))return;
 handledBack=true;lastBackTick=fn<unsigned(*)()>(0x39e240)();
 at<B>(p,0x1ac)=1; // Original close animation; update calls the original close routine.
 log("SETTINGS close requested");
}
static void settingsClosedHook(void*p){fn<V>(0x21dd24)(p);log("SETTINGS closed; original values retained");}

static void layoutSettingsSkin(void*p){
 if(!at<B>(p,0x2050))return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 B*tabs=at<B*>(p,0x2078),*tabsEnd=at<B*>(p,0x2080);
 B*rows=at<B*>(p,0x2110),*rowsEnd=at<B*>(p,0x2118);
 static void*owner;static B*oldTabs;static B*oldRows;static U oldTabsSize,oldRowsSize;static const void*firstLabel;
 U nt=tabs?(tabsEnd-tabs)/0x40:0,nr=rows?(rowsEnd-rows)/0x48:0;
 const void*first=nr?at<void*>(rows,0x28):nullptr;
 bool changed=owner!=p||tabs!=oldTabs||rows!=oldRows||nt!=oldTabsSize||nr!=oldRowsSize||first!=firstLabel||at<float>(p,0x2054)!=w*.025f||at<float>(p,0x205c)!=w*.95f;
 if(!changed&&nr&&at<float>(rows,8)!=w*.323f)changed=true;
 if(!changed)return;
 owner=p;oldTabs=tabs;oldRows=rows;oldTabsSize=nt;oldRowsSize=nr;firstLabel=first;
 bounds(p,0x2054,w*.025f,h*.035f,w*.95f,h*.93f);
 bounds(p,0x20d8,w*.045f,h*.185f,w*.246f,h*.682f);
 bounds(p,0x2064,w*.323f,h*.185f,w*.63f,h*.682f);
 float tabStep=h*.086f,rowStep=h*.107f,tabHeight=h*.070f,rowHeight=h*.086f;
 for(U i=0;i<nt;i++){
  B*tab=tabs+i*0x40;float y=h*.193f+i*tabStep;
  bounds(tab,0x18,w*.053f,y,w*.229f,tabHeight);at<float>(tab,0x28)=y+h*.010f;
  void*label=at<void*>(tab,0x30);
  if(label){place(label,w*.063f,y+h*.009f,w*.209f,h*.052f,.80f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xDCEBE0ff);}
 }
 float maxTabs=nt*tabStep-h*.682f;if(maxTabs<0)maxTabs=0;at<float>(p,0x20ec)=maxTabs;
 if(at<float>(p,0x20e8)>maxTabs)at<float>(p,0x20e8)=maxTabs;
 for(U i=0;i<nr;i++){
  B*row=rows+i*0x48;float y=h*.193f+i*rowStep;
  bounds(row,8,w*.323f,y,w*.405f,rowHeight);
  bounds(row,0x18,w*.74f,y,w*.213f,rowHeight);
  void*label=at<void*>(row,0x28),*value=at<void*>(row,0x38);
  if(label){place(label,w*.338f,y+h*.014f,w*.373f,h*.058f,.80f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xF3FFF6ff);}
  if(value){place(value,w*.752f,y+h*.014f,w*.189f,h*.058f,.80f,1);fn<void(*)(void*,unsigned)>(0x2d2c48)(value,0xAAFFBDff);}
 }
 float content=nr*rowStep;if(content<h*.682f)content=h*.682f;at<float>(p,0x2130)=content;
 float maxRows=content-h*.682f;if(at<float>(p,0x2128)>maxRows)at<float>(p,0x2128)=maxRows;
 place((B*)p+0x2138,w*.052f,h*.064f,w*.70f,h*.075f,.90f,0);
 if(settingsBackOwner!=p){settingsBackOwner=p;settingsBackText=createInfoText(p,0xF3FFF6ff);setLongText(settingsBackText,"VOLTAR");}
 place(settingsBackText,w*.825f,h*.064f,w*.128f,h*.065f,.85f,1);
 place((B*)p+0x2268,w*.323f,h*.902f,w*.63f,h*.035f,.70f,0);
 fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2138,0xF3FFF6ff);
 fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2268,0x9AB9A4ff);
 __android_log_print(4,"TurboCarousel","SETTINGS native layout; tabs=%lu; options=%lu; tab=%s; all actions unchanged",nt,nr,strData((B*)p+0x2090));
 for(U i=0;i<nr;i++){B*row=rows+i*0x48;void*label=at<void*>(row,0x28),*value=at<void*>(row,0x38);if(label&&value)__android_log_print(4,"TurboCarousel","SETTING %lu; %s = %s",i,strData((B*)label+0xd0),strData((B*)value+0xd0));}
}
static void settingsSkinText(void*t){
 if(!settingsPainting||!gui)return;
 float w=at<float>(gui,0x54),h=at<float>(gui,0x58);
 for(B*r=at<B*>(gui,0x2110);r&&r<at<B*>(gui,0x2118);r+=0x48){
  bool label=t==at<void*>(r,0x28),value=t==at<void*>(r,0x38);if(!label&&!value)continue;
  float y=at<float>(r,12)-at<float>(gui,0x2128)+h*.014f;
  fn<void(*)(void*,float,float,float)>(0x277194)(t,w*(label?.338f:.752f),y,0);return;
 }
}
static bool settingsSkinRect(U caller,float x,float y,float w,float h,unsigned color){
 if(!settingsPainting)return false;
 if(caller==0x226ee8){
  rounded(x,y,w,h,0x080C09fc);
  float sw=at<float>(gui,0x54),sh=at<float>(gui,0x58);
  rounded(sw*.043f,sh*.178f,sw*.25f,sh*.696f,0x101B13ff);
  rect(sw*.307f,sh*.19f,1.0f,sh*.67f,0x2E65454a);
  rect(sw*.05f,sh*.155f,sw*.90f,1.0f,0x2EDD6255);
  return true;
 }
 if(caller==0x226f14)return true;
 if(caller>=0x21a958&&caller<0x21b0c8)return true;
 if(caller==0x227134){
  bool selected=(color>>8)==0x147D32;rounded(x,y,w,h,selected?0x147D32ff:0x17251Bff);
  if(selected)rect(x,y+h*.2f,3,h*.6f,0x37FF64ff);return true;
 }
 if(caller==0x22757c){rounded(x,y,w,h,0x131E17ff);return true;}
 if(caller==0x2275a8){rounded(x,y,w,h,0x203F2Aff);return true;}
 if((caller>=0x2271ac&&caller<=0x22722c)||(caller>=0x22760c&&caller<=0x22768c)){
  if(w>h)h=1.5f;else w=1.5f;rect(x,y,w,h,0x37FF64ff);return true;
 }
 return false;
}
static void drawSettingsSkinHook(void*p,void*matrix){
 layoutSettingsSkin(p);settingsPainting=true;fn<void(*)(void*,void*)>(0x226e5c)(p,matrix);settingsPainting=false;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 fn<void(*)(const void*)>(0x2e5640)(matrix);
 rounded(w*.825f,h*.064f,w*.128f,h*.065f,0x147D32ff);
 if(settingsBackText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsBackText,matrix);
}
static bool touchSettingsSkinHook(void*p,const void*event){
 layoutSettingsSkin(p);
 static bool pressed;static U finger;
 float w=at<float>(p,0x54),h=at<float>(p,0x58),x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);
 int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 bool inside=x>=w*.825f&&x<=w*.953f&&y>=h*.064f&&y<=h*.129f;
 if(type==0){pressed=inside;finger=id;if(inside)return true;}
 if(pressed&&id==finger){if(type==2){pressed=false;if(inside)requestSettingsClose(p);}return true;}
 return fn<bool(*)(void*,const void*)>(0x2269fc)(p,event);
}
