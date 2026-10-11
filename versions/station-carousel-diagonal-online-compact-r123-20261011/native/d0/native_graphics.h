#pragma once
// One atomic snapshot, published only on preference changes. No JNI or IO per frame.
static unsigned long long stationGraphicsSnapshot(){
 static unsigned long long(*read)();
 if(!read)read=(decltype(read))dlsym(dlopen("libstation_frontend.so",2),"StationGraphics_snapshot");
 return read?read():127ull; // ALL enabled, WAVES as the first-open backdrop.
}
static int stationCarouselStyle(){
 using Reader=int(*)();
 static Reader read=nullptr;static bool resolved=false;
 if(!resolved){read=(Reader)dlsym(dlopen("libstation_frontend.so",2),"StationCarousel_style");resolved=true;}
 return read?read():0; // No migration: CURRENT remains the exact default.
}
static bool stationGraphicsEnabled(unsigned bit){return (stationGraphicsSnapshot()&bit)!=0;}
static int stationGraphicsBackground(){auto s=stationGraphicsSnapshot();return (s&4u)?(int)((s>>6)&3u):2;}
