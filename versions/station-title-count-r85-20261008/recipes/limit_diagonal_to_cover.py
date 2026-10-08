"""Correct only the requested diagonal backdrop; never darken the synopsis."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
p=WORK/'carousel-inputs/d0/native_space.h';s=p.read_text('utf8')
a=s.index('// One continuous, static full-height fade.');b=s.index('static void drawNativeSpace',a)
s=s[:a]+'''// Static diagonal backdrop confined to the focused-cover region.
// The left lateral space stays black; diagonal runs from the search icon toward the bottom-left corner.
// Its opacity reaches zero before the synopsis begins.
// Geometry is cached and rebuilt only when screen/cover geometry changes.
static float gameBackdropEase(float t){
 if(t<=0)return 0;if(t>=1)return 1;return t*t*(3.f-2.f*t);
}
static void drawGameCornerBackdrop(float w,float h){
 auto cover=coverSlot(gui,0);
 float right=contentLeft(gui)+h*.059f*.5f;
 float startY=stationScreenTopbarActionY(h)+h*.059f*.5f;
 static Vertex strip[754];static unsigned count=0;
 static float lastW=-1,lastH=-1,lastLeft=-1,lastRight=-1;
 if(w!=lastW||h!=lastH||cover.x!=lastLeft||right!=lastRight){
  lastW=w;lastH=h;lastLeft=cover.x;lastRight=right;count=0;
  for(int row=0;row<14;row++){
   if(row){strip[count]=strip[count-1];count++;}
   for(int col=0;col<=25;col++){
    float x=col==0?0:cover.x+(right-cover.x)*(col-1)/24.f;
    for(int edge=0;edge<2;edge++){
     float y=h*(row+edge)/14.f;
     float lateral=1.f-gameBackdropEase((x-cover.x)/(h*.020f));
     float line=y<=startY?right:right*(h-y)/(h-startY);
     float diagonal=1.f-gameBackdropEase((x-line+h*.10f)/(h*.10f));
     float opacity=1.f-(1.f-lateral)*(1.f-diagonal);
     unsigned color=fn<unsigned(*)(unsigned)>(3029376)((unsigned)(255.f*opacity+.5f));
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
old='449933b7cf9c77d330221da64ea764fffb15db9a673bd4602ae73d937f026e45';current='f0987cc3ba846ed2b4f632d64d41ed799d4ffad29190e18915498992b2f69354'
for name in ['package_candidate.py','refresh_candidate.py']:
 p=ROOT/'recipes'/name;t=p.read_text();assert old in t;p.write_text(t.replace(old,current),'utf8')
for name in ['native','package']:
 p=WORK/name;dest=WORK/(name+'-before-cover-diagonal');assert p.resolve().parent==WORK.resolve() and not dest.exists();p.rename(dest)
for name in ['installation-motorola-r85','physical-check']:
 p=ROOT/'evidence'/(name+'.json');dest=p.with_name(name+'-before-cover-diagonal.json');assert not dest.exists();p.rename(dest)
print('Only the game backdrop geometry changed; diagonal stops before text.')
