// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Geometry adapter around original GuiStore::drawCoverFlow/drawCover.
// Keeps native textures, animations, cursor and actions. Handles real touch events against drawn bounds.
#include "collection_corner_policy.h"
#include "station_carousel_geometry.h"
static bool modal(void*);
static void updateSystemInfo(void*);
static void drawSystemInfoPanel(void*);
static void drawSystemInfoLayer(void*);
static void drawFocusLaser(void*);
struct alignas(16) NativeMatrix {float values[16];};
static NativeMatrix formationMatrix;
struct CoverRect {float x,y,w,h;int index;bool allGames=false;stationCarouselGeometry::Transform projection{};};
static const stationCarouselGeometry::Transform*formationProjection;
static void drawInstalledCover(void*,U,const CoverRect&);
static bool formationPerspectiveAvailable();
static CoverRect painted[20];static int paintedCount;
static bool mappingCover;static float sourceX,sourceY,scaleX,scaleY,targetX,targetY;
static bool mappingAllGames;
static CoverRect mappedCoverArtwork;static bool mappedCoverArtworkSeen;
static bool mappingHero;static const char*mappingPlatform;
static float lastTouchY;
static float absolute(float n){return n<0?-n:n;}
static bool collectionAllGames(U index){
 return systemsMode&&folderMode&&folderMeta&&folderCount>0&&index<(U)folderCount&&
   stationCollectionCorners::allGamesKind(folderMeta[index].kind);
}
static CoverRect coverSlot(void*p,float d,int effectiveStyle=-1){
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 float bigH=h*(systemsMode?.665f:.865f),bigW=systemsMode?bigH:h*.790f*.828f,bigX=w*(systemsMode?.035f:.025f),top=h*(systemsMode?.135f:.040f);
 float stripX=systemsMode?w*.365f:bigX+bigW+w*.022f,gap=w*.012f,smallW=(w*.965f-stripX-5*gap)/6;
 bool side=d!=0&&stationCarouselGeometry::neighborCount(effectiveStyle<0?stationCarouselStyle():effectiveStyle,stationGraphicsEnabled(16))==10;
 float step=smallW+gap;
 if(side){
  gap=w*.008f;float projectedWidth=(w*.965f-stripX-9*gap)/10;
  smallW=projectedWidth/stationCarouselGeometry::sideWidthRatio();step=projectedWidth+gap;
  stripX-=smallW*stationCarouselGeometry::sideLeftInset();
 }
 float smallH=systemsMode?smallW:smallW/.72f;
 CoverRect result{};float move=d<0?0:d>1?1:d*d*(3-2*d);result.y=top+(!systemsMode?h*.065f*move:0);
 if(d<0){result.x=bigX+d*(bigW+w*.06f);result.w=bigW;result.h=bigH;}
 else if(d<1){float t=d*d*(3-2*d);result.x=bigX+(stripX-bigX)*t;result.w=bigW+(smallW-bigW)*t;result.h=bigH+(smallH-bigH)*t;}
 else {result.x=stripX+(d-1)*step;result.w=smallW;result.h=smallH;}
 return result;
}
static float contentLeft(void*p){if(systemsMode)return at<float>(p,0x54)*.365f;auto r=coverSlot(p,0);return r.x+r.w+at<float>(p,0x54)*.022f;}
static void coverFormationHook(void*p,U index,float distance){
 int style=stationCarouselStyle(),neighbors=stationCarouselGeometry::neighborCount(style,stationGraphicsEnabled(16));
 if(distance < -1.01f || distance > neighbors+.6f)return;
 float h=at<float>(p,0x58),w=at<float>(p,0x54),ad=absolute(distance),n=ad<1?ad:1;
 float bw=h*.38f*.72f,shrink=1-.32f*n,oldW=bw*shrink,oldH=h*.38f*shrink;
 float dx=ad<=1?ad*bw*.885f:bw*(.885f+(ad-1)*.725f);if(distance<0)dx=-dx;
 U*first=at<U*>(p,0xf8),*end=at<U*>(p,0x100);int pos=-1;
 for(U*v=first;v<end;v++)if(*v==index){pos=(int)(v-first);break;}
 // If the active native shader lacks MVP support, draw and hit-test the same flat slot.
 if(style==2&&stationGraphicsEnabled(16)&&pos>=0&&pos!=at<int>(p,0xf0)&&!formationPerspectiveAvailable())style=0;
 if(distance>stationCarouselGeometry::neighborCount(style,stationGraphicsEnabled(16))+.6f)return;
 CoverRect r=coverSlot(p,distance,style);
 r.allGames=collectionAllGames(index);
 sourceX=w*.5f+dx-oldW*.5f;sourceY=h*.37f-oldH*.5f;
 scaleX=r.w/oldW;scaleY=r.h/oldH;targetX=r.x;targetY=r.y;
 r.projection=stationCarouselGeometry::make(r.x,r.y,r.w,r.h,pos,at<int>(p,0xf0),style,stationGraphicsEnabled(16),distance<0?-1:1);
 if(pos>=0&&paintedCount<20&&r.x+r.w>0&&r.x<w){r.index=pos;painted[paintedCount++]=r;}
 mappingHero=!systemsMode&&pos==at<int>(p,0xf0);mappingPlatform=nullptr;
 if(mappingHero){
  void*catalog=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(catalog,0x88),*endItems=at<B*>(catalog,0x90);
  if(begin&&index<(U)(endItems-begin)/0xe8)mappingPlatform=strData(begin+index*0xe8+0x60);
 }
 const auto*previousProjection=formationProjection;formationProjection=&r.projection;
 mappedCoverArtworkSeen=false;mappingAllGames=r.allGames;mappingCover=true;fn<void(*)(void*,U,float)>(0x22833c)(p,index,distance);mappingCover=false;mappingAllGames=false;mappingHero=false;mappingPlatform=nullptr;
 // Artwork can be inset within its animation slot. The badge belongs to the
 // actual texture quad, and must never reuse geometry from another cover.
 if(mappedCoverArtworkSeen&&pos>=0&&r.x+r.w>0&&r.x<w)drawInstalledCover(p,index,mappedCoverArtwork);
 formationProjection=previousProjection;
}
static void flowFormationHook(void*p){
 float retainedAnimation=at<float>(p,0xf4);
 // Presentation-only snap; restore the native input/update state after drawing.
 bool snap=!stationGraphicsEnabled(32);if(snap)at<float>(p,0xf4)=(float)at<int>(p,0xf0);
 paintedCount=0;drawSystemInfoLayer(p);fn<V>(0x22a154)(p);
 // Native flow draws five neighbors. Reta/Diagonal retain the exact sixth-card
 // path; De lado fills ten forward slots, wrapping only the presentation window.
 U*first=at<U*>(p,0xf8);U begin=(U)first,end=at<U>(p,0x100);
 float animated=at<float>(p,0xf4);
 bool side=stationCarouselGeometry::neighborCount(stationCarouselStyle(),stationGraphicsEnabled(16))==10;
 if(!side){
  U size=(end-begin)/8;int extra=(int)animated+6;
  if(extra>=0&&(U)extra<size)coverFormationHook(p,first[extra],extra-animated);
 }else if(first&&end>=begin&&(end-begin)%sizeof(U)==0){
  U size=(end-begin)/sizeof(U);
  if(size>0&&size<=0x7fffffffUL&&animated>=0&&animated<(float)size){
   int anchor=(int)animated,limit=size>10?10:(int)size-1;
   for(int offset=1;offset<=limit;offset++){
    int position=(int)(((U)anchor+(U)offset)%size);bool drawn=false;
    for(int i=0;i<paintedCount;i++)if(painted[i].index==position){drawn=true;break;}
    if(!drawn)coverFormationHook(p,first[position],offset-(animated-anchor));
   }
  }
 }
 if(snap)at<float>(p,0xf4)=retainedAnimation;
 drawSystemVideo720(p);
 // External focus outline removed; artwork LEDs remain inside the magazine shader.

}
struct Vertex {float x,y,u,v;unsigned color;};
// The optional side model changes only an existing MVP uniform. No GL resource/cache.
struct FormationPerspectiveGL {
 void(*GetIntegerv)(unsigned,int*);int(*GetUniformLocation)(unsigned,const char*);
 void(*GetUniformfv)(unsigned,int,float*);void(*UniformMatrix4fv)(int,int,B,const float*);
 bool attempted,loaded;
};
static FormationPerspectiveGL formationPerspectiveGL{};
static bool loadFormationPerspectiveGL(){
 auto&g=formationPerspectiveGL;if(g.attempted)return g.loaded;g.attempted=true;
 void*library=dlopen("libGLESv2.so",2);if(!library)return false;
#define FORMATION_GL(N) g.N=(decltype(g.N))dlsym(library,"gl" #N);if(!g.N)return false;
 FORMATION_GL(GetIntegerv) FORMATION_GL(GetUniformLocation) FORMATION_GL(GetUniformfv) FORMATION_GL(UniformMatrix4fv)
#undef FORMATION_GL
 g.loaded=true;return true;
}
static int formationPerspectiveLocation(unsigned program){
 auto&g=formationPerspectiveGL;int location=g.GetUniformLocation(program,"u_mvp");
 if(location<0)location=g.GetUniformLocation(program,"MVPMatrix");return location;
}
static bool formationPerspectiveAvailable(){
 if(!loadFormationPerspectiveGL())return false;
 auto&g=formationPerspectiveGL;int program=0;g.GetIntegerv(0x8b8d,&program);
 return program>0&&formationPerspectiveLocation((unsigned)program)>=0;
}
static bool drawFormationPerspectiveStrip(const Vertex*input,unsigned count,int src,int dst){
 if(!loadFormationPerspectiveGL())return false;
 auto&g=formationPerspectiveGL;int program=0;g.GetIntegerv(0x8b8d,&program);if(program<=0)return false;
 int location=formationPerspectiveLocation((unsigned)program);if(location<0)return false;
 float saved[16],projected[16];g.GetUniformfv((unsigned)program,location,saved);
 formationProjection->compose(saved,projected);
 struct Restore {FormationPerspectiveGL&g;int location;const float*matrix;~Restore(){g.UniformMatrix4fv(location,1,0,matrix);}};
 Restore restore{g,location,saved};g.UniformMatrix4fv(location,1,0,projected);
 // Verified R122 Renderer::drawTriangleStrips (0x2e5470,size0x140) does not reset MVP/program.
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(input,count,src,dst);return true;
}
// Transform the final existing strip only: UVs, color, texture/filter and draw count stay unchanged.
static void drawFormationStrip(const Vertex*input,unsigned count,int src,int dst){
 if(!formationProjection||!formationProjection->active||count>64){fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(input,count,src,dst);return;}
 if(formationProjection->projective&&drawFormationPerspectiveStrip(input,count,src,dst))return;
 Vertex output[64];memcpy(output,input,count*sizeof(Vertex));
 for(unsigned i=0;i<count;i++){auto point=formationProjection->map(output[i].x,output[i].y);output[i].x=point.x;output[i].y=point.y;}
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(output,count,src,dst);
}
static bool drawMagazineCover(const Vertex*,unsigned,int,int,const char*);
// Round the existing native texture geometrically, retaining its UVs and fade alpha.
// One strip per image; no extra image, Java view, shader or scissor approximation.
static float cornerRadius(float w,float h,bool allGames=false){return stationCollectionCorners::radius(systemsMode,folderMode,w,h,allGames);}
static float squareRoot(float value){
 if(value<=0)return 0;float root=value>1?value:1;
 for(int i=0;i<12;i++)root=(root+value/root)*.5f;return root;
}
static unsigned blendColor(unsigned a,unsigned b,float t){
 unsigned result=0;for(int shift=0;shift<32;shift+=8){float av=(a>>shift)&255,bv=(b>>shift)&255;result|=((unsigned)(av+(bv-av)*t+.5f))<<shift;}return result;
}
static Vertex blendVertex(const Vertex&a,const Vertex&b,float t){return {a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t,a.u+(b.u-a.u)*t,a.v+(b.v-a.v)*t,blendColor(a.color,b.color,t)};}
static void roundedQuad(const Vertex*q,int src,int dst,bool allGames=false){
 float width=q[2].x-q[0].x,height=q[1].y-q[0].y;
 if(width<=0||height<=0)return;
 float radius=cornerRadius(width,height,allGames);if(radius<=0){drawFormationStrip(q,4,src,dst);return;}Vertex strip[52];unsigned count=0;
 for(int half=0;half<2;half++)for(int i=0;i<=12;i++){
  float local=radius*i/12,yy=half?height-radius+local:local;
  float dy=half?local:radius-local,inset=radius-squareRoot(radius*radius-dy*dy);
  Vertex left=blendVertex(q[0],q[1],yy/height),right=blendVertex(q[2],q[3],yy/height);
  strip[count++]=blendVertex(left,right,inset/width);strip[count++]=blendVertex(left,right,1-inset/width);
 }
 drawFormationStrip(strip,count,src,dst);
}
static void roundedCoverQuad(const Vertex*q,int src,int dst,const CoverRect&r){
 const auto*previousProjection=formationProjection;formationProjection=&r.projection;
 roundedQuad(q,src,dst,r.allGames);formationProjection=previousProjection;
}
static void roundedCoverFill(float x,float y,float w,float h,unsigned c,unsigned d,bool horizontal,int src,int dst){
 // Match the native Renderer color packing and untextured fill state.
 fn<void(*)(unsigned)>(3035880)(0);
 c=fn<unsigned(*)(unsigned)>(3029376)(c);d=fn<unsigned(*)(unsigned)>(3029376)(d);
 Vertex q[4]={{x,y,0,0,c},{x,y+h,0,0,horizontal?c:d},{x+w,y,0,0,horizontal?d:c},{x+w,y+h,0,0,d}};
 roundedQuad(q,src,dst,mappingCover&&mappingAllGames);
}
static void stripsFormationHook(const Vertex*input,unsigned count,int src,int dst){
 U caller=(U)__builtin_return_address(0)-base;
 if(storeUiHideMessage&&caller>=0x21a3dc&&caller<0x21b0c8)return;
 // Native selected-cover sweep: additive strip over artwork. Laser rim is a separate shader.
 if(count==6&&src==4&&dst==1)return;
 if(mappingCover&&src==4&&dst==1)return;
 if(caller==0x228a18)return;
 if(mappingCover&&caller>=0x22833c&&caller<0x229014&&count<=64){
  if(caller==0x228ac4)return;
  Vertex vertices[64];memcpy(vertices,input,count*sizeof(Vertex));
  for(unsigned i=0;i<count;i++){vertices[i].x=targetX+(vertices[i].x-sourceX)*scaleX;vertices[i].y=targetY+(vertices[i].y-sourceY)*scaleY;}
  if(caller==0x2288e4&&count==4){
   mappedCoverArtwork={vertices[0].x,vertices[0].y,vertices[2].x-vertices[0].x,vertices[1].y-vertices[0].y,0,mappingAllGames};
   mappedCoverArtworkSeen=mappedCoverArtwork.w>0&&mappedCoverArtwork.h>0;
   if(systemsMode&&stationGraphicsEnabled(2)){
    // No colored loading flash. Live/cached video frames are drawn by the
    // native video layer; an unavailable source has a neutral dark surface.
    roundedCoverFill(vertices[0].x,vertices[0].y,vertices[2].x-vertices[0].x,vertices[1].y-vertices[0].y,
      0x050706ffu,0x050706ffu,true,src,dst);return;
   }
   // The system JPGs contain a thin black margin outside their decorative frame.
   // Move only UVs inward by 8/720; keep source files and visible card geometry intact.
   if(systemsMode){float midU=(vertices[0].u+vertices[3].u)*.5f,midV=(vertices[0].v+vertices[3].v)*.5f;
    for(int i=0;i<4;i++){vertices[i].u=midU+(vertices[i].u-midU)*.9777778f;vertices[i].v=midV+(vertices[i].v-midV)*.9777778f;}}
   if(mappingHero&&drawMagazineCover(vertices,count,src,dst,mappingPlatform))return;
   roundedQuad(vertices,src,dst,mappingAllGames);return;
  }
  drawFormationStrip(vertices,count,src,dst);return;
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(input,count,src,dst);
}
struct Int2{int x,y;};
static void clipFormationHook(const Int2*pos,const Int2*size){
 if(mappingCover){Int2 p{(int)(targetX+(pos->x-sourceX)*scaleX),(int)(targetY+(pos->y-sourceY)*scaleY)},s{(int)(size->x*scaleX),(int)(size->y*scaleY)};
 if(formationProjection&&formationProjection->active){
  auto b=formationProjection->bounds((float)p.x,(float)p.y,(float)s.x,(float)s.y);
  int right=stationCarouselGeometry::upper(b.x+b.w),bottom=stationCarouselGeometry::upper(b.y+b.h);
  p={stationCarouselGeometry::lower(b.x),stationCarouselGeometry::lower(b.y)};s={right-p.x,bottom-p.y};
 }
 fn<void(*)(const Int2*,const Int2*)>(0x2e2800)(&p,&s);return;}
 fn<void(*)(const Int2*,const Int2*)>(0x2e2800)(pos,size);
}
static int hitCover(float x,float y){
 // Reverse painting order gives the foremost original card priority during its native animation.
 for(int i=paintedCount-1;i>=0;i--){const auto&r=painted[i];
  auto local=r.projection.inverse(x,y);float tx=local.x,ty=local.y;
  if(tx<r.x||tx>r.x+r.w||ty<r.y||ty>r.y+r.h)continue;
  float radius=cornerRadius(r.w,r.h,r.allGames),dx=tx<r.x+radius?r.x+radius-tx:tx>r.x+r.w-radius?tx-(r.x+r.w-radius):0;
  float dy=ty<r.y+radius?r.y+radius-ty:ty>r.y+r.h-radius?ty-(r.y+r.h-radius):0;
  if(dx*dx+dy*dy<=radius*radius)return r.index;
 }
 return -1;
}
static int coverAtFormationHook(void*p,float x){return hitCover(x,lastTouchY);}
static bool formationTouch(void*p,const void*event){
 static bool tracking,dragged;static U finger;static float startX,startY,stepX;
 float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);lastTouchY=y;
 int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 if(modal(p)||at<int>(p,0x370)<2){tracking=false;return false;}
 if(type==0){if(hitCover(x,y)<0)return false;tracking=true;dragged=false;finger=id;startX=stepX=x;startY=y;return true;}
 if(!tracking||id!=finger)return false;
 if(type==1){
  if(absolute(x-startX)>24||absolute(y-startY)>24)dragged=true;
  float step=at<float>(p,0x54)*.085f;
  if(absolute(x-stepX)>step){fn<void(*)(void*,int)>(0x2318d0)(p,x<stepX?1:-1);stepX=x;}
  return true;
 }
 if(type==2){
  tracking=false;
  if(!dragged){int target=hitCover(x,y),current=at<int>(p,0xf0);
   if(target==current){__android_log_print(4,"TurboCarousel","Native card touch accept index=%d",target);acceptHook(p);}
   else if(target>=0){fn<void(*)(void*,int)>(0x2318d0)(p,target-current);__android_log_print(4,"TurboCarousel","Native card touch selection index=%d",target);}
  }
  return true;
 }
 return true;
}
