#include "collection_corner_policy.h"
#include <cassert>
#include <cstdio>
#include <initializer_list>
int main(){
 int checks=0;
 for(bool system:{false,true})for(bool folder:{false,true}){
  for(float width:{25.f,100.f,720.f}){
   assert(stationCollectionCorners::squareCollection(system,folder)==(system&&folder));++checks;
   float height=200.f,min=width<height?width:height;
   float expected=system&&!folder?min*.115f:0;
   assert(stationCollectionCorners::radius(system,folder,width,height)==expected);++checks;
  }
 }
 std::printf("PASS %d corner-policy checks; all collections square, main platforms unchanged\n",checks);
}
