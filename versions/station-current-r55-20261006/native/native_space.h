// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Clouds-only background. Aircraft and stars have no rendering or update work.
static void drawNativeClouds(float,float,float);
static void drawNativeSpace(float w,float h){
 if(w<=0||h<=0)return;
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,stationSkyTop(),stationSkyBottom(),false,4,5);
 static unsigned started;unsigned now=fn<unsigned(*)()>(0x39e240)();if(!started)started=now;float t=(unsigned)(now-started)*.001f;
 drawNativeClouds(w,h,t);
 // GuiStore phases: 0 loading, 1 welcome, 2 entering, 3 open carousel.
 // Keep the original sky during loading/welcome/entry; darken only the open UI.
 if(!gui||at<int>(gui,0x370)!=3)return;
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
