// Native Libretro pause presentation. Actions, enabled state and touch bounds stay native.
static float pausePanelX,pausePanelY,pausePanelW,pausePanelH;
static void pauseSurface(float x,float y,float w,float h,float radius,unsigned color){
 if(w<=0||h<=0)return;
 float r=radius;if(r>h*.5f)r=h*.5f;if(r>w*.5f)r=w*.5f;
 Vertex v[68];unsigned n=0,c=fn<unsigned(*)(unsigned)>(3029376)(color);
 fn<void(*)(unsigned)>(3035880)(0);
 for(int half=0;half<2;half++)for(int i=0;i<=16;i++){
  float d=r*i/16,yy=half?h-r+d:d,dy=half?d:r-d;
  float inset=r-squareRoot(r*r-dy*dy);
  v[n++]={x+inset,y+yy,0,0,c};v[n++]={x+w-inset,y+yy,0,0,c};
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(v,n,4,5);
}
static B* pauseRow(float x,float y){
 B*begin=at<B*>((void*)base,0x3cf2d0),*end=at<B*>((void*)base,0x3cf2d8);
 if(!begin||end<begin||(U)(end-begin)>56*16)return nullptr;
 for(B*r=begin;r<end;r+=56)if(absolute(at<float>(r,0x24)-x)<1&&absolute(at<float>(r,0x28)-y)<1)return r;
 return nullptr;
}
static void pauseIcon(float x,float y,float size,int action,unsigned color){
 float t=size*.10f;
 if(action==0){
  unsigned c=fn<unsigned(*)(unsigned)>(3029376)(color);
  Vertex v[3]={{x-size*.25f,y-size*.40f,0,0,c},{x-size*.25f,y+size*.40f,0,0,c},{x+size*.4f,y,0,0,c}};
  fn<void(*)(unsigned)>(3035880)(0);fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(v,3,4,5);
 }else if(action==3){
  rect(x-size*.4f,y-size*.42f,t,size*.84f,color);
  rect(x-size*.4f,y-size*.42f,size*.38f,t,color);rect(x-size*.4f,y+size*.32f,size*.38f,t,color);
  rect(x-size*.05f,y-t*.5f,size*.50f,t,color);openButtonChevron(x+size*.16f,y,size*.25f,color);
 }else{
  pauseSurface(x-size*.38f,y-size*.38f,size*.76f,size*.76f,size*.08f,color);
  pauseSurface(x-size*.27f,y-size*.27f,size*.54f,size*.54f,size*.03f,0x111B15ff);
  if(action==1){rect(x-size*.15f,y-size*.29f,size*.3f,size*.2f,color);rect(x-size*.16f,y+size*.10f,size*.32f,t,color);}
  else{rect(x-t*.5f,y-size*.22f,t,size*.42f,color);rect(x-size*.20f,y+size*.12f,size*.40f,t,color);}
 }
}
static void drawRefinedPausePanel(float x,float y,float w,float h){
 pausePanelX=x;pausePanelY=y;pausePanelW=w;pausePanelH=h;
 float r=h*.028f,edge=h*.0018f;
 pauseSurface(x,y+h*.012f,w,h,r,0x00000070);
 pauseSurface(x-edge,y-edge,w+2*edge,h+2*edge,r+edge,0x2A3E31ff);
 pauseSurface(x,y,w,h,r,0x090E0Bff);
 rect(x+w*.06f,y+h*.16f,w*.88f,edge,0x263C2Eff);
 rect(x+w*.06f,y+h*.16f,w*.10f,edge*2,0x42E87Dff);
 rect(x+w*.06f,y+h*.858f,w*.88f,edge,0x263C2Eff);
}
static void drawRefinedPauseAction(float x,float y,float w,float h,unsigned color){
 B*row=pauseRow(x,y);int action=row?at<int>(row,0):-1;
 bool enabled=!row||at<B>(row,0x20)!=0,selected=(color>>8)!=0x223049;
 bool exit=action==3||(color>>8)==0xC62828;
 float gap=h*.045f,hh=h-gap*2,r=h*.11f,edge=h*.014f,yy=y+gap;
 unsigned accent=exit?0xEE5964ff:0x47E886ff;
 unsigned border=selected?accent:enabled?(exit?0x573136ff:0x2B4133ff):0x1B2921ff;
 unsigned face=selected?(exit?0x321B1Fff:0x143A24ff):0x101812ff;
 pauseSurface(x,yy,w,hh,r,border);
 pauseSurface(x+edge,yy+edge,w-2*edge,hh-2*edge,r-edge,face);
 if(selected)pauseSurface(x+h*.10f,y+h*.28f,h*.032f,h*.44f,h*.016f,accent);
 pauseIcon(x+h*.46f,y+h*.5f,h*.31f,action,enabled?(exit?0xF3838Bff:0x82E9AAff):0x617569ff);
 if(selected)openButtonChevron(x+w-h*.40f,y+h*.5f,h*.085f,accent);
}
static void* pauseTextCacheHook(void*font,const void*s,float x,float y,unsigned color){
 U caller=(U)__builtin_return_address(0)-base;
 if(storeUiHideMessage&&caller==0x22d578)color=0;
 const void*text=s;alignas(8) B temporary[24]={};
 if(caller==0x2bc1cc&&pausePanelW>0){
  const char*t=strData(s),*replacement=nullptr;
  if(strcmp(t,"JOGO PAUSADO")==0){replacement="TURBORAMA  /  PAUSA";x=pausePanelX+pausePanelW*.06f;color=0xEDFFF3ff;}
  else if(starts(t,"ESTE EMULADOR NAO TEM SALVAR AQUI")){
   replacement="SEM SAVE RAPIDO. USE O SAVE DO JOGO.";
   x=pausePanelX+pausePanelW*.06f;color=0xA1B8AAff;
  }else{
   B*begin=at<B*>((void*)base,0x3cf2d0),*end=at<B*>((void*)base,0x3cf2d8);
   if(begin&&end>=begin&&(U)(end-begin)<=56*16)for(B*r=begin;r<end;r+=56){
    if(strcmp(t,strData(r+8))==0){
     x=at<float>(r,0x24)+at<float>(r,0x30)*.88f;
     color=!at<B>(r,0x20)?0x768B7Dff:at<int>(r,0)==3?0xFFBBC1ff:0xF0FFF5ff;break;
    }
   }
  }
  if(replacement){
   U n=strlen(replacement);
   if(n<=22){temporary[0]=(B)(n*2);memcpy(temporary+1,replacement,n+1);}
   else{at<U>(temporary,0)=(n+1)|1;at<U>(temporary,8)=n;at<const char*>(temporary,16)=replacement;}
   text=temporary;
  }
 }
 return fn<void*(*)(void*,const void*,float,float,unsigned)>(0x2e9304)(font,text,x,y,color);
}
