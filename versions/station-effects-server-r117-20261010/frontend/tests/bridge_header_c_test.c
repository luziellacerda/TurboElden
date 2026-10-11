#include "../station_profile_bridge.h"
uint64_t (*station_revision_signature)(void)=StationProfile_nameRevision;
bool (*station_copy_signature)(char*,size_t,uint64_t*)=StationProfile_copyName;
