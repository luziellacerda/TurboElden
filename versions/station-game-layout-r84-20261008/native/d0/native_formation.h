// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Geometry adapter around original GuiStore::drawCoverFlow/drawCover.
// Keeps native textures, animations, cursor and actions. Handles real touch events against drawn bounds.
#include "collection_corner_policy.h"
static bool modal(void*);
static void updateSystemInfo(void*);
static void drawSystemInfoPanel(void*);
static void drawSystemInfoLayer(void*);
static void drawFocusLaser(void*);
struct alignas(16) NativeMatrix {float values[16];};
static NativeMatrix formationMatrix;
struct CoverRect {float x,y,w,h;int index;bool allGames=false;};
static void drawInstalledCover(void*,U,const CoverRect&);
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
static CoverRect coverSlot(void*p,float d){
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 float bigH=h*(systemsMode?.665f:.790f),bigW=systemsMode?bigH:bigH*.828f,bigX=w*(systemsMode?.035f:.025f),top=h*(systemsMode?.135f:.115f);
 float stripX=systemsMode?w*.365f:bigX+bigW+w*.022f,gap=w*.012f,smallW=(w*.965f-stripX-5*gap)/6,smallH=systemsMode?smallW:smallW/.72f;
 CoverRect result{};result.y=top;
 if(d<0){result.x=bigX+d*(bigW+w*.06f);result.w=bigW;result.h=bigH;}
 else if(d<1){float t=d*d*(3-2*d);result.x=bigX+(stripX-bigX)*t;result.w=bigW+(smallW-bigW)*t;result.h=bigH+(smallH-bigH)*t;}
 else {result.x=stripX+(d-1)*(smallW+gap);result.w=smallW;result.h=smallH;}
 return result;
}
static float contentLeft(void*p){if(systemsMode)return at<float>(p,0x54)*.365f;auto r=coverSlot(p,0);return r.x+r.w+at<float>(p,0x54)*.022f;}
static void coverFormationHook(void*p,U index,float distance){
 if(distance < -1.01f || distance > 6.6f)return;
 float h=at<float>(p,0x58),w=at<float>(p,0x54),ad=absolute(distance),n=ad<1?ad:1;
 float bw=h*.38f*.72f,shrink=1-.32f*n,oldW=bw*shrink,oldH=h*.38f*shrink;
 float dx=ad<=1?ad*bw*.885f:bw*(.885f+(ad-1)*.725f);if(distance<0)dx=-dx;
 CoverRect r=coverSlot(p,distance);
 r.allGames=collectionAllGames(index);
 sourceX=w*.5f+dx-oldW*.5f;sourceY=h*.37f-oldH*.5f;
 scaleX=r.w/oldW;scaleY=r.h/oldH;targetX=r.x;targetY=r.y;
 U*first=at<U*>(p,0xf8),*end=at<U*>(p,0x100);int pos=-1;
 for(U*v=first;v<end;v++)if(*v==index){pos=(int)(v-first);break;}
 if(pos>=0&&paintedCount<20&&r.x+r.w>0&&r.x<w){r.index=pos;painted[paintedCount++]=r;}
 mappingHero=!systemsMode&&pos==at<int>(p,0xf0);mappingPlatform=nullptr;
 if(mappingHero){
  void*catalog=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(catalog,0x88),*endItems=at<B*>(catalog,0x90);
  if(begin&&index<(U)(endItems-begin)/0xe8)mappingPlatform=strData(begin+index*0xe8+0x60);
 }
 mappedCoverArtworkSeen=false;mappingAllGames=r.allGames;mappingCover=true;fn<void(*)(void*,U,float)>(0x22833c)(p,index,distance);mappingCover=false;mappingAllGames=false;mappingHero=false;mappingPlatform=nullptr;
 // Artwork can be inset within its animation slot. The badge belongs to the
 // actual texture quad, and must never reuse geometry from another cover.
 if(mappedCoverArtworkSeen&&pos>=0&&r.x+r.w>0&&r.x<w)drawInstalledCover(p,index,mappedCoverArtwork);
}
static void flowFormationHook(void*p){
 paintedCount=0;drawSystemInfoLayer(p);fn<V>(0x22a154)(p);
 // Native flow draws five neighbours. Add its sixth neighbour using the same original card renderer.
 U*first=at<U*>(p,0xf8);U size=(at<U>(p,0x100)-at<U>(p,0xf8))/8;
 float animated=at<float>(p,0xf4);int extra=(int)animated+6;
 if(extra>=0&&(U)extra<size)coverFormationHook(p,first[extra],extra-animated);
 drawSystemVideo720(p);
 // External focus outline removed; artwork LEDs remain inside the magazine shader.

}
struct Vertex {float x,y,u,v;unsigned color;};
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
 float radius=cornerRadius(width,height,allGames);if(radius<=0){fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,src,dst);return;}Vertex strip[52];unsigned count=0;
 for(int half=0;half<2;half++)for(int i=0;i<=12;i++){
  float local=radius*i/12,yy=half?height-radius+local:local;
  float dy=half?local:radius-local,inset=radius-squareRoot(radius*radius-dy*dy);
  Vertex left=blendVertex(q[0],q[1],yy/height),right=blendVertex(q[2],q[3],yy/height);
  strip[count++]=blendVertex(left,right,inset/width);strip[count++]=blendVertex(left,right,1-inset/width);
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,src,dst);
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
   if(systemsMode){
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
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(vertices,count,src,dst);return;
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(input,count,src,dst);
}
struct Int2{int x,y;};
static void clipFormationHook(const Int2*pos,const Int2*size){
 if(mappingCover){Int2 p{(int)(targetX+(pos->x-sourceX)*scaleX),(int)(targetY+(pos->y-sourceY)*scaleY)},s{(int)(size->x*scaleX),(int)(size->y*scaleY)};
 fn<void(*)(const Int2*,const Int2*)>(0x2e2800)(&p,&s);return;}
 fn<void(*)(const Int2*,const Int2*)>(0x2e2800)(pos,size);
}
static int hitCover(float x,float y){
 // Reverse painting order gives the foremost original card priority during its native animation.
 for(int i=paintedCount-1;i>=0;i--){const auto&r=painted[i];
  if(x<r.x||x>r.x+r.w||y<r.y||y>r.y+r.h)continue;
  float radius=cornerRadius(r.w,r.h,r.allGames),dx=x<r.x+radius?r.x+radius-x:x>r.x+r.w-radius?x-(r.x+r.w-radius):0;
  float dy=y<r.y+radius?r.y+radius-y:y>r.y+r.h-radius?y-(r.y+r.h-radius):0;
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
