// Authorized presentation update. Native query, key actions, download workers,
// message lifecycle and confirmation handling remain in the original GuiStore.
struct UiBox {float x,y,w,h;};
struct UiString {alignas(8) B data[24];};
static void* storeUiOwner;static void* storeUiLabels[51];
static float uiUnit(float v){return v<0?0:v>1?1:v;}
static unsigned uiAlpha(unsigned rgb,float alpha){return (rgb&0xffffff00)|unsigned(uiUnit(alpha)*255);}
static bool uiContains(const char*s,const char*word){for(;*s;s++)if(starts(s,word))return true;return false;}
static bool uiError(const char*s){
 return uiContains(s,"Erro")||uiContains(s,"ERRO")||uiContains(s,"erro")||
  uiContains(s,"Falha")||uiContains(s,"FALHA")||uiContains(s,"falha")||
  uiContains(s,"insuficiente")||uiContains(s,"INSUFICIENTE")||uiContains(s,"Error")||uiContains(s,"Não foi")||uiContains(s,"SEM ESPAÇO");
}
static bool isStoreUiLabel(void*t){for(void*label:storeUiLabels)if(label&&label==t)return true;return false;}
static void uiMatrix(const void*m){fn<void(*)(const void*)>(0x2e5640)(m);}
static void uiSurface(UiBox b,unsigned face,unsigned edge,float alpha=1){
 float r=b.h*.13f;if(gui&&r>at<float>(gui,0x58)*.016f)r=at<float>(gui,0x58)*.016f;
 float line=gui?at<float>(gui,0x58)*.0015f:1;if(line<1)line=1;
 pauseSurface(b.x,b.y,b.w,b.h,r,uiAlpha(edge,alpha));
 pauseSurface(b.x+line,b.y+line,b.w-2*line,b.h-2*line,r-line,uiAlpha(face,alpha));
}
static void uiText(void*t,const void*m,UiBox b,float scale,unsigned color,int align=0,float alpha=1){
 if(!t)return;
 // Re-layout only on actual changes; TextComponent retains its native text cache.
 if(at<float>(t,0x38)!=b.x||at<float>(t,0x3c)!=b.y||at<float>(t,0x54)!=b.w/scale||at<float>(t,0x58)!=b.h/scale||at<float>(t,0x60)!=scale)
  place(t,b.x,b.y,b.w,b.h,scale,align);
 if(at<int>(t,0x120)!=align)fn<void(*)(void*,int)>(0x2d38d8)(t,align);
 if((at<unsigned>(t,0xf8)&0xffffff00)!=(color&0xffffff00))fn<void(*)(void*,unsigned)>(0x2d2c48)(t,color);
 fn<void(*)(void*,unsigned char)>(0x2d2d2c)(t,(unsigned char)(uiUnit(alpha)*255));
 fn<void(*)(void*,const void*)>(0x2d2dc4)(t,m);uiMatrix(m);
}
static void uiLabel(void*p,int slot,const char*value,const void*m,UiBox b,float scale,unsigned color,int align=0,float alpha=1){
 if(slot<0||slot>=51)return;
 if(storeUiOwner!=p){storeUiOwner=p;memset(storeUiLabels,0,sizeof(storeUiLabels));}
 void*&t=storeUiLabels[slot];if(!t)t=createInfoText(p,color);
 if(strcmp(strData((B*)t+0xd0),value)!=0)setLongText(t,value);
 uiText(t,m,b,scale,color,align,alpha);
}
static void uiStatusIcon(float x,float y,float size,unsigned color,bool error){
 float line=size*.105f;
 if(error){
  pauseSurface(x-size*.035f,y-size*.28f,line,size*.35f,line*.45f,color);
  pauseSurface(x-size*.035f,y+size*.18f,line,line,line*.45f,color);
 }else{
  rect(x-line*.5f,y-size*.32f,line,size*.45f,color);
  unsigned c=fn<unsigned(*)(unsigned)>(3029376)(color);
  Vertex v[3]={{x-size*.23f,y,0,0,c},{x,y+size*.24f,0,0,c},{x+size*.23f,y,0,0,c}};
  fn<void(*)(unsigned)>(3035880)(0);fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(v,3,4,5);
  rect(x-size*.27f,y+size*.34f,size*.54f,line,color);
 }
}
static void layoutSearchPresentation(void*p){
 float w=at<float>(p,0x54),h=at<float>(p,0x58);bool active=at<B>(p,0x648)!=0;
 // Both native touch and controller code read these same rectangles.
 float x=active?w*.18f:w*.24f,y=active?h*.237f:h*.026f;
 float bw=active?w*.64f:w*.375f,bh=active?h*.083f:h*.053f;
 bounds(p,0x6a8,x,y,bw,bh);bounds(p,0x6b8,x+bw-bh,y,bh,bh);
 if(active)bounds(p,0x5a4,w*.167f,h*.358f,w*.666f,h*.442f);
 static void*imeOwner;static float imeX,imeY,imeW,imeH;
 if(active&&!at<B>(p,0x598)&&(imeOwner!=p||imeX!=x||imeY!=y||imeW!=bw||imeH!=bh)){
  struct ImeRect{int x,y,w,h;} target{int(x),int(y),int(bw),int(bh)};
  auto setRect=(void(*)(const ImeRect*))dlsym(dlopen("libSDL2.so",2),"SDL_SetTextInputRect");
  if(setRect)setRect(&target);imeOwner=p;imeX=x;imeY=y;imeW=bw;imeH=bh;
 }
 if(!active)imeOwner=nullptr;
}
static void layoutSearchPresentationHook(void*p){fn<V>(0x219034)(p);layoutSearchPresentation(p);}
static void drawSearchField(void*p,const void*m){
 float h=at<float>(p,0x58);bool active=at<B>(p,0x648)!=0;
 UiBox b{at<float>(p,0x6a8),at<float>(p,0x6ac),at<float>(p,0x6b0),at<float>(p,0x6b4)};
 uiMatrix(m);uiSurface(b,0x101D15ff,active?0x37DD72ff:0x315B40ff);
 fn<void(*)(void*,float,float,float,unsigned)>(0x22f090)(p,b.x+b.h*.44f,b.y+b.h*.5f,b.h*.21f,0x76EDA0ff);
 const char*q=strData((B*)p+0x650);bool has=*q!=0;char display[160]={};
 // Show the end of long queries without modifying the native search string.
 U length=strlen(q);U limit=active?54:32;
 if(length>limit){U start=length-limit;while((B(q[start])&0xc0)==0x80)start++;memcpy(display,"...",3);memcpy(display+3,q+start,length-start);q=display;}
 uiLabel(p,0,has?q:(systemsMode?"Digite o nome da plataforma":"Digite o nome do jogo"),m,{b.x+b.h*.92f,b.y,b.w-b.h*2.10f,b.h},active?.88f:.66f,has?0xF1FFF6ff:0x8AAB96ff);
 if(has){
  float cx=at<float>(p,0x6b8),cw=at<float>(p,0x6c0);
  uiSurface({cx+b.h*.10f,b.y+b.h*.14f,cw-b.h*.24f,b.h*.72f},0x1D2B23ff,0x304A3Aff);
  uiLabel(p,1,"X",m,{cx,b.y,cw,b.h},active?.78f:.62f,0xBAD5C4ff,1);
 }
 uiMatrix(m);
}
static void drawSearchPresentationHook(void*p,void*m){
 layoutSearchPresentation(p);
 // Open search is painted at the modal layer, above the carousel and synopsis.
 if(at<B>(p,0x648)||!*strData((B*)p+0x650))return;
 drawSearchField(p,m);
}
static void drawKeyboardPresentationHook(void*p,void*m){
 if(at<B>(p,0x648))return;
 fn<void(*)(void*,void*)>(0x219c4c)(p,m);
}
static void paintSearchModal(void*p,const void*m){
 if(!at<B>(p,0x648))return;
 layoutSearchPresentation(p);float w=at<float>(p,0x54),h=at<float>(p,0x58);
 bool pad=at<B>(p,0x598)!=0;uiMatrix(m);
 rect(0,0,w,h,0x020704b5);
 UiBox panel{w*.145f,h*.125f,w*.71f,h*(pad?.744f:.245f)};
 uiSurface(panel,0x080F0Bff,0x294B35ff);
 rect(w*.180f,h*.188f,w*.026f,h*.003f,0x39E579ff);
 uiLabel(p,2,systemsMode?"PESQUISAR PLATAFORMAS":"PESQUISAR JOGOS",m,{w*.217f,h*.155f,w*.40f,h*.060f},1.03f,0xEDFFF3ff);
 const char*scope="SOMENTE PLATAFORMAS";
 if(!systemsMode){scope=strData((B*)p+0x150);
  for(int i=0;i<systemCount;i++)if(strcmp(strData(items+i*0xe8+0x60),scope)==0){scope=strData(items+i*0xe8+0x18);break;}}
 uiLabel(p,3,scope,m,{w*.620f,h*.157f,w*.200f,h*.055f},.60f,0x6CD791ff,2);
 drawSearchField(p,m);
 if(pad){
  for(int row=0;row<5;row++){
   int count=fn<int(*)(int)>(0x2192b0)(row);
   for(int col=0;col<count;col++){
    UiBox b=fn<UiBox(*)(void*,int,int)>(0x21938c)(p,row,col);
    bool focus=at<int>(p,0x59c)==row&&at<int>(p,0x5a0)==col;
    bool ok=row==4&&col==2,erase=row==4&&col==1;
    unsigned face=ok?0x1FAD51ff:focus?0x1C472Dff:0x132019ff;
    unsigned edge=focus?0x6DF799ff:ok?0x36DA70ff:0x2A4032ff;
    uiSurface(b,face,edge);
    UiString label=fn<UiString(*)(int,int)>(0x2192c4)(row,col);
    const char*text=ok?"VER RESULTADOS":strData(label.data);
    uiLabel(p,4+row*10+col,text,m,b,row==4?.72f:.87f,ok?0x04190Bff:erase?0xEDABB0ff:0xEEFFF4ff,1);
    if(label.data[0]&1)fn<V>(0x39d820)(at<void*>(label.data,16));
   }
  }
  uiLabel(p,47,"Use as setas e confirme. Voltar fecha a pesquisa.",m,{w*.183f,h*.807f,w*.63f,h*.035f},.65f,0x88A793ff);
 }else uiLabel(p,47,"Os resultados mudam enquanto você digita.",m,{w*.182f,h*.329f,w*.63f,h*.029f},.63f,0x88A793ff);
 uiMatrix(m);
}
static void layoutMessagePresentation(void*p){
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 bounds(p,0x2030,w*.21f,h*.245f,w*.58f,h*.51f);
 bounds(p,0x2040,w*.608f,h*.650f,w*.148f,h*.070f);
}
static void layoutMessagePresentationHook(void*p){fn<V>(0x22cef4)(p);layoutMessagePresentation(p);}
static void drawMessagePresentationHook(void*p,void*m){
 paintSearchModal(p,m);
 bool active=at<B>(p,0x1d98)||at<B>(p,0x1d99);
 if(!active){fn<void(*)(void*,void*)>(0x22d090)(p,m);return;}
 layoutMessagePresentation(p);
 // Execute the original renderer's fade/lifecycle work with only its old paint hidden.
 storeUiHideMessage=true;fn<void(*)(void*,void*)>(0x22d090)(p,m);storeUiHideMessage=false;
 if(!at<B>(p,0x1d98)&&!at<B>(p,0x1d99))return;
 float progress=uiUnit(at<float>(p,0x1d9c)/180.f),inv=1-progress;
 float alpha=1-inv*inv*inv;if(!at<B>(p,0x1d98))alpha=1-alpha;
 if(alpha<=0)return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 void*title=(B*)p+0x1dd0,*body=(B*)p+0x1f00;
 bool error=uiError(strData((B*)title+0xd0));unsigned accent=error?0xF26975ff:0x46E888ff;
 uiMatrix(m);rect(0,0,w,h,uiAlpha(0x020604ff,alpha*.72f));
 uiSurface({w*.21f,h*.245f,w*.58f,h*.51f},0x090F0Bff,error?0x61323Aff:0x30513Aff,alpha);
 uiLabel(p,48,"TURBORAMA",m,{w*.247f,h*.273f,w*.44f,h*.035f},.64f,accent,0,alpha);
 uiText(title,m,{w*.247f,h*.323f,w*.509f,h*.081f},1.02f,0xF1FFF6ff,0,alpha);
 rect(w*.247f,h*.416f,w*.509f,h*.0015f,uiAlpha(0x294033ff,alpha));
 uiText(body,m,{w*.247f,h*.445f,w*.509f,h*.165f},.82f,0xBCD1C3ff,0,alpha);
 UiBox button{at<float>(p,0x2040),at<float>(p,0x2044),at<float>(p,0x2048),at<float>(p,0x204c)};
 uiSurface(button,0x239C4Dff,0x45E67Fff,alpha);
 uiLabel(p,49,at<B>(p,0x4b0)?"A  /  OK":"OK",m,button,.92f,0xEFFFF4ff,1,alpha);uiMatrix(m);
}
static void drawToastPresentationHook(void*p,void*m){
 float t=at<float>(p,0x2a8);void*title=at<void*>(p,0x288),*body=at<void*>(p,0x298);
 if(t<0||!title||!body)return;
 // The native queue and its 3600ms lifetime remain untouched.
 float f=uiUnit(t/450.f),out=uiUnit((t-3180.f)/420.f),inv=1-out;
 float alpha=uiUnit(f*3)*inv*inv*inv;if(alpha<=0)return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58),shift=(1-f)*(1-f)*h*.016f;
 bool error=uiError(strData((B*)title+0xd0));unsigned accent=error?0xF16B77ff:0x49E58Aff;
 UiBox b{w*.49f,h*.125f-shift,w*.48f,h*.20f};uiMatrix(m);
 uiSurface(b,0x0A130Dff,error?0x61333Bff:0x335A40ff,alpha);
 float icon=b.h*.29f,cx=b.x+h*.047f,cy=b.y+b.h*.50f;
 pauseSurface(cx-icon*.65f,cy-icon*.65f,icon*1.3f,icon*1.3f,icon*.25f,uiAlpha(error?0x342026ff:0x183823ff,alpha));
 // Neutral notice marker; the original title states success, start or error.
 uiStatusIcon(cx,cy,icon,uiAlpha(accent,alpha),error);
 float tx=b.x+h*.10f,tw=b.w-h*.126f;
 uiText(title,m,{tx,b.y+h*.021f,tw,h*.060f},.81f,accent,0,alpha);
 uiText(body,m,{tx,b.y+h*.084f,tw,h*.090f},.74f,0xE1EEE5ff,0,alpha);
 uiMatrix(m);
}
static char* downloadNumber(char*out,unsigned long long value){
 char digits[24];int count=0;do{digits[count++]=char('0'+value%10);value/=10;}while(value);
 while(count)*out++=digits[--count];return out;
}
static void drawDownloadPresentationHook(void*p,float x,float y,float w,float h,long long current,long long total){
 if(mappingCover){x=targetX+(x-sourceX)*scaleX;y=targetY+(y-sourceY)*scaleY;w*=scaleX;h*=scaleY;}
 if(w<=0||h<=0)return;
 float boxH=h*.137f,by=y+h-boxH;rect(x,by,w,boxH,0x06110Cf0);
 float bx=x+w*.07f,bw=w*.86f,bh=h*.012f;if(bh<2)bh=2;
 float barY=y+h-h*.035f;
 pauseSurface(bx,barY,bw,bh,bh*.5f,0x264433ff);
 float fraction=total>0?uiUnit(float(double(current)/double(total))):0;
 if(total>0){if(fraction>0)pauseSurface(bx,barY,bw*fraction,bh,bh*.5f,0x3CED80ff);}
 else{float phase=float(fn<unsigned(*)()>(0x39e240)()%1600)/1600.f;pauseSurface(bx+(bw-bw*.22f)*phase,barY,bw*.22f,bh,bh*.5f,0x3CED80ff);}
 if(w>at<float>(p,0x54)*.12f){
  // The item selected by StationCatalog_progress disambiguates equal counters.
  static bool linked=false;static int(*phase)(long long,long long);static double(*networkRate)(long long,long long);
  if(!linked){linked=true;void*lib=dlopen("libstation_frontend.so",2);if(lib){phase=(decltype(phase))dlsym(lib,"StationDownload_phase");networkRate=(decltype(networkRate))dlsym(lib,"StationDownload_networkRate");}}
  const int step=phase?phase(current,total):2;
  const char*title=step==3?"PREPARANDO":step==2?"BAIXANDO":step==1?"AGUARDANDO":"PROCESSANDO";
  const double rate=step==2&&networkRate?networkRate(current,total):-1;
  char label[80];U titleSize=strlen(title);memcpy(label,title,titleSize);char*out=label+titleSize;
  if(total>0){*out++=' ';out=downloadNumber(out,(unsigned)int(fraction*100));*out++='%';}
  else{memcpy(out,"...",3);out+=3;}
  if(total>0&&rate>0&&rate<1e15){
   const auto hundredths=(unsigned long long)(rate/10000.0+0.5);
   const char separator[]=" · ";memcpy(out,separator,sizeof(separator)-1);out+=sizeof(separator)-1;
   out=downloadNumber(out,hundredths/100);*out++='.';*out++=char('0'+hundredths/10%10);*out++=char('0'+hundredths%10);
   memcpy(out," MB/s",5);out+=5;
  }*out=0;
  float scale=h/at<float>(p,0x58)*.80f;
  uiLabel(p,50,label,&formationMatrix,{bx,by+h*.011f,bw,boxH*.60f},scale,0xDFFFF0ff,0);
 }
 uiMatrix(&formationMatrix);
}
