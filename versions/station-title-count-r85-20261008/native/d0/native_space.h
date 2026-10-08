// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Clouds-only background. Aircraft and stars have no rendering or update work.
static void drawNativeClouds(float,float,float);
// Shared carousel backdrop: solid black up to the diagonal through the B in
// the focused cover's TURBORAMA wordmark, then broad fading to the right edge.
// Only the background is shaded; artwork and text are drawn afterward.
static float gameBackdropEase(float t){
 if(t<=0)return 0;if(t>=1)return 1;return t*t*(3.f-2.f*t);
}
static void drawCarouselDiagonalBackdrop(float w,float h){
 auto cover=coverSlot(gui,0);
 float anchorX=cover.x+cover.w*.44f,anchorY=cover.y+cover.h*.075f;
 static Vertex strip[754];static unsigned count=0;
 static float lastW=-1,lastH=-1,lastLeft=-1,lastX=-1,lastY=-1;
 if(w!=lastW||h!=lastH||cover.x!=lastLeft||anchorX!=lastX||anchorY!=lastY){
  lastW=w;lastH=h;lastLeft=cover.x;lastX=anchorX;lastY=anchorY;count=0;
  for(int row=0;row<14;row++){
   if(row){strip[count]=strip[count-1];count++;}
   for(int col=0;col<=25;col++){
    float t=col==0?0:(col-1)/24.f;
    unsigned color=fn<unsigned(*)(unsigned)>(3029376)((unsigned)(255.f*(1.f-gameBackdropEase(t))+.5f));
    for(int edge=0;edge<2;edge++){
     float y=h*(row+edge)/14.f,line=anchorX*(h-y)/(h-anchorY);
     if(line<cover.x)line=cover.x; // Entire left lateral space remains black.
     float x=col==0?0:line+(w-line)*t;
     Vertex v={x,y,0,0,color};
     if(row&&col==0&&edge==0)strip[count++]=v;
     strip[count++]=v;
    }
   }
  }
 }
 fn<void(*)(unsigned)>(3035880)(0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);
}
static void drawNativeSpace(float w,float h){
 if(w<=0||h<=0)return;
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,stationSkyTop(),stationSkyBottom(),false,4,5);
 static unsigned started;unsigned now=fn<unsigned(*)()>(0x39e240)();if(!started)started=now;float t=(unsigned)(now-started)*.001f;
 drawNativeClouds(w,h,t);
 // GuiStore phases: 0 loading, 1 welcome, 2 entering, 3 open carousel.
 // Keep the original sky during loading/welcome/entry; darken only the open UI.
 if(!gui||at<int>(gui,0x370)!=3)return;
 drawCarouselDiagonalBackdrop(w,h);
}
