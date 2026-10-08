"""Latest owner adjustment: opaque to logo B diagonal, smooth to right edge."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
p=WORK/'carousel-inputs/d0/native_space.h';s=p.read_text('utf8')
a=s.index('// Static diagonal backdrop');b=s.index('static void drawNativeSpace',a)
s=s[:a]+'''// Game-only backdrop: solid black up to the diagonal through the B in
// the focused cover's TURBORAMA wordmark, then broad fading to the right edge.
// Only the background is shaded; artwork and text are drawn afterward.
static float gameBackdropEase(float t){
 if(t<=0)return 0;if(t>=1)return 1;return t*t*(3.f-2.f*t);
}
static void drawGameCornerBackdrop(float w,float h){
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
''' + s[b:];p.write_text(s,'utf8')
for name in ['native','package']:
 p=WORK/name;dest=WORK/(name+'-before-letter-b');assert p.resolve().parent==WORK.resolve() and not dest.exists();p.rename(dest)
print('Opaque boundary anchored to logo B; broad smooth fading to screen right.')
