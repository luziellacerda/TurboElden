// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Clouds-only background. Aircraft and stars have no rendering or update work.
static void drawNativeClouds(float,float,float);
// Two static triangle strips: opaque at the upper corners, clear inward.
// Drawn before artwork; no timer, texture, allocation or offscreen pass.
static void drawGameCornerBackdrop(float w,float h){
 fn<void(*)(unsigned)>(3035880)(0);
 unsigned solid=fn<unsigned(*)(unsigned)>(3029376)(0x000000ffu);
 unsigned clear=fn<unsigned(*)(unsigned)>(3029376)(0x00000000u);
 const float reachX=w*.56f,reachY=h*.68f,hold=.10f;
 for(int side=0;side<2;side++){
  float origin=side?w:0,direction=side?-1.f:1.f;
  Vertex strip[5]={{origin,0,0,0,solid},
   {origin+direction*reachX*hold,0,0,0,solid},
   {origin,reachY*hold,0,0,solid},
   {origin+direction*reachX,0,0,0,clear},
   {origin,reachY,0,0,clear}};
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,5,4,5);
 }
}
static void drawNativeSpace(float w,float h){
 if(w<=0||h<=0)return;
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,stationSkyTop(),stationSkyBottom(),false,4,5);
 static unsigned started;unsigned now=fn<unsigned(*)()>(0x39e240)();if(!started)started=now;float t=(unsigned)(now-started)*.001f;
 drawNativeClouds(w,h,t);
 // GuiStore phases: 0 loading, 1 welcome, 2 entering, 3 open carousel.
 // Keep the original sky during loading/welcome/entry; darken only the open UI.
 if(!gui||at<int>(gui,0x370)!=3)return;
 if(!systemsMode){drawGameCornerBackdrop(w,h);return;}
 // Renderer::drawRect bool is vertical, despite the old hook parameter name.
 // ABI 0x2e2ca4/0x2e2cb0: false gives TL=BL=color1, TR=BR=color2.
 // Both strips must be horizontal so the shared edge has the same alpha.
 // Keep the gradient behind every cover/text/button.
 // 80% black at the left, 70% at the actual focused-cover edge, clear at right.
 float edge=gui?coverSlot(gui,0).x+coverSlot(gui,0).w:w*.34f;
 if(edge<=0)edge=w*.34f;if(edge>=w)edge=w*.95f;
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,edge,h,0x000000ccu,0x000000b3u,false,4,5);
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(edge,0,w-edge,h,0x000000b3u,0x00000000u,false,4,5);
}
