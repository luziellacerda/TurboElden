// Installed status belongs to each catalog item; artwork and lettering are
// a single transparent texture, shared by the selected cover and thumbnails.
#include "station_ribbon_placement.h"
static void drawInstalledArtwork(StationInfoRect);
static void drawInstalledCover(void*p,U index,const CoverRect&cover){
 if(systemsMode||folderMode||modal(p)||at<int>(p,0x370)<2||cover.w<=0||cover.h<=0)return;
 void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);
 if(!begin||!end||end<begin||index>=(U)(end-begin)/0xe8||!begin[index*0xe8+0xa8])return;
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);fn<void(*)(unsigned)>(0x2e52e8)(0);
 // Attach each measured fold to the actual cover texture edge. Preserve
 // R52 scale and the unchanged R51 image/lettering; no font or image transform.
 auto placed=stationPlaceRibbon(cover.x,cover.y,cover.w,cover.h);
 drawInstalledArtwork({placed.x,placed.y,placed.w,placed.h});
}
