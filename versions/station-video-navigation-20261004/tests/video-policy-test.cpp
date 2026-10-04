#include <cassert>
#include <cstdio>
#include "video720_policy.h"
int main(){
 static_assert(video720MaxRetainedBytes==8294400,"retained cache memory budget");
 assert(video720Older(1,2));assert(!video720Older(2,1));assert(!video720Older(2,2));
 assert(video720Older(0xfffffff0u,0x10u));assert(!video720Older(0x10u,0xfffffff0u));
 puts("5 unsigned age ordering checks, GPU budget assertion passed");
}
