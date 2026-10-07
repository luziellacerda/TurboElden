#include "collection_corner_policy.h"
#include <cassert>
#include <cstdio>
#include <initializer_list>
int main(){
 int checks=0;
 for(bool systems:{false,true})for(bool folders:{false,true})for(bool allGames:{false,true}){
  for(float width:{25.f,100.f,720.f}){
   assert(stationCollectionCorners::squareCollection(systems,folders,allGames)==(systems&&folders&&!allGames));++checks;
   float height=200.f,min=width<height?width:height;
   float expected=systems&&(!folders||allGames)?min*.115f:0.f;
   assert(stationCollectionCorners::radius(systems,folders,width,height,allGames)==expected);++checks;
  }
 }
 // The all-games sentinel is a metadata kind. Reordering or filtering the visible
 // list must never round an ordinary collection merely because it becomes first.
 const int kinds[]={0,1,2,0};
 const unsigned reordered[]={3,2,1,0},filtered[]={3,1},onlyAll[]={2};
 for(const auto index:reordered){
  bool allGames=stationCollectionCorners::allGamesKind(kinds[index]);
  assert(allGames==(index==2));++checks;
  assert(stationCollectionCorners::radius(true,true,100,200,allGames)==(index==2?11.5f:0.f));++checks;
 }
 for(const auto index:filtered){
  assert(!stationCollectionCorners::allGamesKind(kinds[index]));++checks;
 }
 assert(stationCollectionCorners::allGamesKind(kinds[onlyAll[0]]));++checks;
 for(int kind:{-1,0,1,3,99}){assert(!stationCollectionCorners::allGamesKind(kind));++checks;}
 // Original four-argument callers retain R68 behavior until they pass card identity.
 assert(stationCollectionCorners::radius(true,true,100,200)==0.f);++checks;
 assert(stationCollectionCorners::radius(true,false,100,200)==11.5f);++checks;
 std::printf("PASS %d corner-policy checks; all-games rounded, actual collections square\n",checks);
}
