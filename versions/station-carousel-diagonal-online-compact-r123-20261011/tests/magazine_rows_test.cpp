#include <cassert>
#include <cstdio>
#include <vector>
#include "../native/d0/native_magazine_rows.h"
int main(){
 unsigned checks=0;
 for(int height=1;height<=1536;height++){
  MagazineRowPlan plan;plan.reset(height);std::vector<bool> seen(height);int count=0,frames=0;
  while(count<height){int frameRows=0;for(int i=0;i<4;i++){
   int row=plan.next();if(row<0)break;assert(row>=0&&row<height&&!seen[row]);checks++;seen[row]=true;count++;frameRows++;}
   assert(frameRows>0&&frameRows<=4);checks++;frames++;}
  assert(frames==(height+3)/4);checks++;assert(plan.next()==-1&&plan.done==height);checks++;
  for(bool value:seen){assert(value);checks++;}
 }
 MagazineRowPlan plan;plan.reset(960);int expected[]={606,910,328,51};
 for(int row:expected){assert(plan.next()==row);checks++;}
 std::printf("PASS %u executed native progressive-field row checks\n",checks);
}
