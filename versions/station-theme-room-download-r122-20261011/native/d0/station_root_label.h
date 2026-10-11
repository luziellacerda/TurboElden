#pragma once
// Three measured native spaces left of the previous centered label, within its slot.
static StationInfoRect stationMainButtonText(StationInfoRect slot,float labelWidth,float threeSpaces){
 float free=slot.w-labelWidth;if(free<0)free=0;float offset=free*.5f-threeSpaces;if(offset<0)offset=0;
 slot.x+=offset;slot.w-=offset;return slot;
}
