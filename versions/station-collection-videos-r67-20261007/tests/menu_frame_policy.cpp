#include "station_menu_frame_policy.h"
using stationMenuFramePolicy::target;
static_assert(target(false,false,false)==30,"Idle carousel");
static_assert(target(false,false,true)==30,"Loading carousel");
static_assert(target(false,true,false)==30,"Moving carousel");
static_assert(target(false,true,true)==30,"Moving/loading carousel");
static_assert(target(true,false,false)==15,"Do not increase idle dialog work");
static_assert(target(true,false,true)==30,"Loading dialog");
static_assert(target(true,true,false)==30,"Interacting dialog");
static_assert(target(true,true,true)==30,"Interacting/loading dialog");
int main(){return 0;}
