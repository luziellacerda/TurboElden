#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <initializer_list>
using U=unsigned long long;using B=unsigned char;
template<class T> T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
struct Vertex{float x,y,u,v;unsigned color;};
struct alignas(16) NativeMatrix{float values[16];};
struct CoverRect{float x,y,w,h;int index;};
struct StationInfoRect{float x,y,w,h;};
bool systemsMode,folderMode,blocked;
bool modal(void*){return blocked;}
NativeMatrix formationMatrix{{1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1}},current;
alignas(16) B catalog[256]{},items[50*0xe8]{},owner[1024]{};
float hero=575;
CoverRect coverSlot(void*,float){return {58,124,hero,hero/.72f,0};}
int draws,texts,layouts,allocations;unsigned checks;
void* getCat(){return catalog;}
unsigned tick(){return 721;}
NativeMatrix multiply(const void*a,const void*b){
 auto&A=*static_cast<const NativeMatrix*>(a);auto&B=*static_cast<const NativeMatrix*>(b);NativeMatrix r{};
 for(int col=0;col<4;col++)for(int row=0;row<4;row++)for(int k=0;k<4;k++)r.values[col*4+row]+=A.values[k*4+row]*B.values[col*4+k];return r;
}
void matrix(const void*p){current=*static_cast<const NativeMatrix*>(p);}
void bind(unsigned n){assert(n==0);}
void mesh(const Vertex*q,unsigned n,int src,int dst){
 assert(n>0&&n<=448&&src==4&&dst==5);draws++;
 for(unsigned i=0;i<n;i++){assert(std::isfinite(q[i].x)&&std::isfinite(q[i].y));checks++;}
}
void text(void*,void* m){texts++;auto&M=*static_cast<NativeMatrix*>(m);assert(M.values[0]>0&&M.values[4]>0);checks++;}
template<class T>T fn(U id){switch(id){
 case 0x1887dc:return reinterpret_cast<T>(&getCat);case 0x39e240:return reinterpret_cast<T>(&tick);
 case 3019156:return reinterpret_cast<T>(&multiply);case 0x2e5640:return reinterpret_cast<T>(&matrix);
 case 0x2e52e8:return reinterpret_cast<T>(&bind);case 0x2e5470:return reinterpret_cast<T>(&mesh);case 0x2d2dc4:return reinterpret_cast<T>(&text);
 default:assert(false);return nullptr;
}}
void*createInfoText(void*,unsigned){allocations++;return owner+12;}
void setLongText(void*,const char*s){assert(std::strcmp(s,"INSTALADO")==0);}
void fitInfoText(void*,StationInfoRect r,float,int){assert(r.w>0&&r.h>0);layouts++;}
#include "native_installed_tag.h"
int main(){
 at<B*>(catalog,0x88)=items;at<B*>(catalog,0x90)=items+sizeof(items);at<int>(owner,0x370)=2;
 for(int i=0;i<50;i++)items[i*0xe8+0xa8]=(i%3==0);
 // Nonsequential indices, matching filtered lists, and moving cards of every width.
 for(int frame=0;frame<80;frame++)for(int visible=0;visible<9;visible++){
  U index=(visible*7+frame)%50;float width=180+(hero-180)*(frame/79.f);
  CoverRect cover{float(visible*190-100),124,width,width/.72f,visible};
  int before=draws;drawInstalledCover(owner,index,cover);
  assert(draws-before==(index%3==0?1:0));checks++;
 }
 assert(texts==draws&&allocations==1&&layouts==1);checks+=3;
 int before=draws;
 for(int flag=0;flag<4;flag++){
  systemsMode=flag==0;folderMode=flag==1;blocked=flag==2;at<int>(owner,0x370)=flag==3?1:2;
  drawInstalledCover(owner,0,{0,0,hero,hero/.72f,0});assert(draws==before);checks++;
 }
 systemsMode=folderMode=blocked=false;at<int>(owner,0x370)=2;
 drawInstalledCover(owner,50,{0,0,hero,hero/.72f,0});drawInstalledCover(owner,~U(0),{0,0,hero,hero/.72f,0});assert(draws==before);checks++;
 items[0xa8]=0;drawInstalledCover(owner,0,{0,0,hero,hero/.72f,0});assert(draws==before);checks++;
 items[0xa8]=1;drawInstalledCover(owner,0,{0,0,hero,hero/.72f,0});assert(draws==before+1);checks++;
 hero=800;drawInstalledCover(owner,0,{0,0,hero,hero/.72f,0});assert(layouts==2&&allocations==1);checks++;
 printf("PASS %u checks: actual ribbon function, filtered indices, all moving cards, install/delete state, gates, one cached text layout\n",checks);
}
