#pragma once
#include <cstdint>
namespace station {
// Call under the existing Inbox mutex, after Java atomically finishes old tasks.
template<class Results> void discardPreviousCoverResults(Results& results){results.clear();}
// SDL thread only. Preserve cached artwork, jobs and global HTTP429 backoff.
template<class Slots,class Retry,class Items>
void resetCoverPublication(Slots& slots,Retry& retry,Items& items,int64_t& nextSweep){
 slots.clear();retry.clear();nextSweep=0;
 for(auto& item:items)item.coverPending=false;
}
}
