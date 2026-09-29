// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
static bool settingsSkinRect(U,float,float,float,float,unsigned);
// Styling for existing GuiStore components and action rectangles. No Java view or overlay.
static void rect(float x,float y,float w,float h,unsigned color){
 if(w>0&&h>0)fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(x,y,w,h,color,color,false,4,5);
}
static void rounded(float x,float y,float w,float h,unsigned color){
 float r=h*.16f;if(r>14)r=14;
 rect(x+r,y,w-2*r,h,color);rect(x,y+r,r,h-2*r,color);rect(x+w-r,y+r,r,h-2*r,color);
 // Six horizontal bands approximate each corner with no extra textures or assets.
 for(int i=0;i<6;i++){
  float dy=r-(i+.5f)*r/6, q=r*r-dy*dy, root=r;
  for(int n=0;n<5;n++)root=(root+q/root)*.5f;
  float inset=r-root, yy=i*r/6, hh=r/6+.15f;
  rect(x+inset,y+yy,r-inset,hh,color);rect(x+w-r,y+yy,r-inset,hh,color);
  rect(x+inset,y+h-yy-hh,r-inset,hh,color);rect(x+w-r,y+h-yy-hh,r-inset,hh,color);
 }
}
static void place(void*t,float x,float y,float w,float h,float scale,int align){
 fn<void(*)(void*,float,float)>(0x2771b0)(t,0,0);
 fn<void(*)(void*,float)>(0x277200)(t,scale);
 fn<void(*)(void*,float,float,float)>(0x277194)(t,x,y,0);
 fn<void(*)(void*,float,float)>(0x2771d8)(t,w/scale,h/scale);
 fn<void(*)(void*,int)>(0x2d38d8)(t,align);
 fn<void(*)(void*,int)>(0x2d38e8)(t,1);
}
static void bounds(void*p,U offset,float x,float y,float w,float h){
 at<float>(p,offset)=x;at<float>(p,offset+4)=y;at<float>(p,offset+8)=w;at<float>(p,offset+12)=h;
}
static void layoutSkin(void*p){
 static void*owner;static float oldW,oldH;static bool oldMode;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 B*buttons=at<B*>(p,0xde8);if(!buttons)return;
 // Native update animates the old title position on every frame; relocate it after that update.
 fn<void(*)(void*,float,float,float)>(0x277194)((B*)p+0xa58,w*.222f,h*(systemsMode?.023f:.008f),0);
 // Check a native rectangle too: layoutButtons may have reset it after a resize.
 if(owner==p&&oldW==w&&oldH==h&&oldMode==systemsMode&&at<float>(buttons,8)==h*(systemsMode?.865f:.908f))return;
 owner=p;oldW=w;oldH=h;oldMode=systemsMode;
 const U labels[]={0xe00,0xf30,0x1060,0x1190,0x12c0};float gap=w*.012f,bw=(w*.95f-4*gap)/5;
 for(int i=0;i<5;i++){
  float x=w*.025f+i*(bw+gap),width=bw;
  if(systemsMode&&i==0){x=w*.035f;width=coverSlot(p,0).w;}
  bounds(buttons+i*20,4,x,h*(systemsMode?.865f:.908f),width,h*(systemsMode?.072f:.065f));
  place((B*)p+labels[i],x,h*(systemsMode?.865f:.908f),width,h*(systemsMode?.072f:.065f),.70f,1);
 }
 bounds(p,0x13f0,w*.848f,h*.023f,w*.127f,h*.059f); // Installed, original action 0
 bounds(p,0x1400,w*.718f,h*.023f,w*.118f,h*.059f); // Systems, original action 1
 bounds(p,0x1410,w*.012f,h*.023f,h*.059f,h*.059f);  // Settings
 bounds(p,0x698,w*.634f,h*.023f,h*.059f,h*.059f);   // Search
 place((B*)p+0x1470,w*.848f,h*.023f,w*.127f,h*.059f,.70f,1);
 place((B*)p+0x15a0,w*.718f,h*.023f,w*.118f,h*.059f,.70f,1);
 bounds(p,0x1420,w*.055f,h*.015f,w*.17f,h*.066f);
 void*profile=at<void*>(p,0x1468);
 float nameX=w*.055f+h*.066f+w*.012f;
 if(profile)place(profile,nameX,h*.025f,w*.115f,h*.05f,.72f,0);
 place((B*)p+0x7f8,nameX,h*.083f,w*.115f,h*.035f,.70f,0);
 // Reposition the existing title, platform, installation/download state and counter.
 place((B*)p+0xa58,w*.222f,h*(systemsMode?.023f:.008f),w*.39f,h*(systemsMode?.057f:.045f),.76f,0);
 place((B*)p+0x928,w*.222f,h*.031f,w*.17f,h*.043f,.85f,0);
 place((B*)p+0xb88,w*.410f,h*.031f,w*.21f,h*.043f,.75f,0);
 place((B*)p+0xcb8,coverSlot(p,0).x,h*(systemsMode?.814f:.865f),coverSlot(p,0).w,h*.026f,.68f,1);
 log("Native compact menu layout applied");
}
static void skinText(void*t){
 if(!gui)return;U offset=(U)t-(U)gui;unsigned color=0;
 if(offset==0xe00||offset==0xf30||offset==0x1190||offset==0x12c0)color=0xF3FFF6ff;
 if(offset==0x1060)color=0xFF837Aff;
 if(offset==0xa58)color=0xffffffff;
 if(offset==0x928||offset==0x7f8||offset==0xcb8)color=0xAFC3B4ff;
 if(offset==0xb88)color=0xC5D9CBff;
 if(offset==0x1470||offset==0x15a0)color=0xF3FFF6ff;
 if(color&&at<unsigned>(t,0xf8)!=color)fn<void(*)(void*,unsigned)>(0x2d2c48)(t,color);
}
static bool skinInfo,skinTop;static int skinTopIndex;
static unsigned turboramaMenuColor(unsigned color){
 unsigned rgb=color>>8,alpha=color&255;
 switch(rgb){
 case 0x4a9bff:rgb=0x37FF64;break;case 0x1f6feb:rgb=0x147D32;break;
 case 0x131a2d:rgb=0x121A14;break;case 0x0a0f1c:rgb=0x080C09;break;
 case 0x223049:rgb=0x151D17;break;case 0x1b2536:rgb=0x1B281F;break;
 case 0x26345a:rgb=0x284D32;break;case 0x2a3a5c:rgb=0x366C43;break;
 }return (rgb<<8)|alpha;
}
static void rectHook(float x,float y,float w,float h,unsigned c,unsigned d,bool horizontal,int src,int dst){
 U caller=(U)__builtin_return_address(0)-base;
 if(caller>=0x210000&&caller<0x237000&&!mappingCover){c=turboramaMenuColor(c);d=turboramaMenuColor(d);}
 if(settingsSkinRect(caller,x,y,w,h,c))return;
 if(mappingCover){
  x=targetX+(x-sourceX)*scaleX;y=targetY+(y-sourceY)*scaleY;w*=scaleX;h*=scaleY;
  if(caller>=0x22861c&&caller<=0x2286c4)return; // Remove the four broad selected-card glow layers.
  if(caller==0x228714){
   float innerH=h/1.02f,padY=(h-innerH)*.5f,padX=padY*scaleX/scaleY;
   float line=gui?at<float>(gui,0x58)*.00085f:.9f;if(line<.75f)line=.75f;
   unsigned alpha=(c&255)*3/4;
   roundedCoverFill(x+padX-line,y+padY-line,w-2*padX+2*line,innerH+2*line,0xC7CBD300|alpha,0xC7CBD300|alpha,false,src,dst);return;
  }
  if(caller==0x228d68){roundedCoverFill(x,y,w,h,c,d,horizontal,src,dst);return;}
  if(caller>0x228d68&&caller<=0x228e78)return; // Keep the loading placeholder inside the same rounded contour.
 }
 if(gui&&skinInfo){
  float width=at<float>(gui,0x54),height=at<float>(gui,0x58);
  if(caller==0x228168){rect(0,0,width,height*.105f,0x080C09f5);rect(0,height*.105f,width,1.5f,0x28E65870);return;}
  if(caller==0x228190)return;
  if(caller==0x228270||caller==0x2282c8){y=height*.103f;h=height*.004f;}
 }
 if(gui&&skinTop){
  if(caller>=0x21a958&&caller<0x21b0c8)return; // Replace native glow with the flat button fill.
  if(caller>=0x22eba0&&caller<0x22ed00){
   if(caller==0x22ecac){
    bool active=skinTopIndex==0?(!systemsMode&&at<B>(gui,0x148)):skinTopIndex==1?systemsMode:false;
    rounded(x,y,w,h,active?0x147D32ff:0x151D17ff);skinTopIndex++;
   }
   return;
  }
 }
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(x,y,w,h,c,d,horizontal,src,dst);
}
static void infoSkinHook(void*p){skinInfo=true;fn<V>(0x2280e8)(p);skinInfo=false;}
static void topSkinHook(void*p,void*matrix){skinTop=true;skinTopIndex=0;fn<void(*)(void*,void*)>(0x22ea88)(p,matrix);skinTop=false;}
static void buttonsSkinHook(void*p){
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 if(systemsMode)rounded(w*.027f,h*.849f,coverSlot(p,0).w+w*.016f,h*.105f,0x080C09e8);
 else rounded(w*.014f,h*.900f,w*.972f,h*.084f,0x080C09e8);
 B*start=at<B*>(p,0xde8),*end=at<B*>(p,0xdf0);
 int selected=fn<int(*)(void*)>(0x21b0c8)(p);bool installed=false;
 if(!systemsMode&&selected>=0){void*cat=fn<void*(*)()>(0x1887dc)();B*it=at<B*>(cat,0x88)+(U)selected*0xe8;if(it<at<B*>(cat,0x90))installed=it[0xa8];}
 for(B*b=start;b<end;b+=20){
  int action=at<int>(b,0);float x=at<float>(b,4),y=at<float>(b,8),bw=at<float>(b,12),bh=at<float>(b,16);
  bool disabled=(action==1||action==2)&&!installed;
  unsigned color=action==0?0x147D32ff:disabled?0x101512ff:0x151D17ff;
  if(action==2&&selected>=0&&at<int>(p,0x16c)==selected)color=0x8F2424ff;
  if(action>=0&&action<5&&at<float>(p,0x1c4+action*4)>.08f){rounded(x-2,y-2,bw+4,bh+4,0x37FF64ff);}
  rounded(x,y,bw,bh,color);
 }
}

// Synopses share the animated background; no opaque information panel.
static void drawSystemInfoPanel(void*){}
#include "native_space.h"
static void auroraSkinHook(float width,float height,float horizon,float lowerEdge,float elapsed,float introOffset){
 drawNativeSpace(width,height);
}
