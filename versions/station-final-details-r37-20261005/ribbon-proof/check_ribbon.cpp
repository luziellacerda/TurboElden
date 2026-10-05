#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include "station_installed_ribbon.h"
struct Vertex{float x,y,u,v;unsigned color;};
int main(int argc,char**argv){
 const float widths[]={160,280,420,575,800};unsigned checks=0,maxVertices=0;
 for(float width:widths){
  StationRibbonMesh<Vertex> start,loop;
  stationBuildInstalledRibbon(start,width,0);stationBuildInstalledRibbon(loop,width,3600);
  assert(start.count==loop.count&&std::memcmp(start.vertices,loop.vertices,start.count*sizeof(Vertex))==0);checks++;
  for(unsigned ms=0;ms<3600;ms++){
   StationRibbonMesh<Vertex> mesh;stationBuildInstalledRibbon(mesh,width,ms);
   assert(mesh.count>0&&mesh.count<=448);checks++;
   if(mesh.count>maxVertices)maxVertices=mesh.count;
   for(unsigned i=0;i<mesh.count;i++){
    auto v=mesh.vertices[i];assert(std::isfinite(v.x)&&std::isfinite(v.y));
    assert(v.x>=-width*.02101f&&v.y>=-width*.02101f);
    assert(v.x<width*.505f&&v.y<width*.505f);checks+=3;
   }
   assert(std::memcmp(start.vertices,mesh.vertices,118*sizeof(Vertex))==0);checks++;
  }
 }
 assert(stationRibbonColor(0x12345678u)==0x78563412u);checks++;
 StationRibbonMesh<Vertex> empty;stationBuildInstalledRibbon(empty,0,5);assert(empty.count==0);checks++;
 if(argc==2){
  FILE*f=std::fopen(argv[1],"wb");assert(f);std::fputs("[",f);
  const unsigned times[]={0,1000,1500,2000,2600};
  for(unsigned frame=0;frame<5;frame++){
   StationRibbonMesh<Vertex> mesh;stationBuildInstalledRibbon(mesh,800,times[frame]);
   std::fprintf(f,"%s{\"time\":%u,\"vertices\":[",frame?",":"",times[frame]);
   for(unsigned i=0;i<mesh.count;i++){auto v=mesh.vertices[i];std::fprintf(f,"%s[%.6f,%.6f,%u]",i?",":"",v.x,v.y,stationRibbonColor(v.color));}
   std::fputs("]}",f);
  }
  std::fputs("]",f);std::fclose(f);
 }
 std::printf("PASS %u checks: 18000 animation meshes; max %u/448 vertices; one ribbon draw; finite bounded geometry; static surface stable; seamless 3600 ms loop.\n",checks,maxVertices);
}
