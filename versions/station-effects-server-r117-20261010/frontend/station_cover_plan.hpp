#pragma once
#include <vector>
#include <cstddef>
namespace station {
// Preserve visible priority exactly, then prepare a bounded lookahead in display order.
// No per-frame filesystem or full-catalog expansion: rebuilt only when selection/priorities change.
template<class Items> std::vector<size_t> coverPlan(const Items& items,const std::vector<size_t>& priorities){
 std::vector<size_t> result;if(items.empty())return result;
 std::vector<bool> seen(items.size(),false);size_t anchor=items.size();
 for(size_t i:priorities)if(i<items.size()&&!seen[i]&&result.size()<9){if(anchor==items.size())anchor=i;seen[i]=true;result.push_back(i);}
 if(anchor==items.size())return result;
 for(size_t step=1;step<=items.size()&&result.size()<9;++step){size_t i=(anchor+step)%items.size();
  if(!seen[i]&&items[i].folder==items[anchor].folder&&items[i].platform==items[anchor].platform){seen[i]=true;result.push_back(i);}}
 return result;
}
}
