#pragma once
// One atomic snapshot, published only on preference changes. No JNI or IO per frame.
static unsigned long long stationGraphicsSnapshot(){
 static unsigned long long(*read)();
 if(!read)read=(decltype(read))dlsym(dlopen("libstation_frontend.so",2),"StationGraphics_snapshot");
 return read?read():63ull;
}
static bool stationGraphicsEnabled(unsigned bit){return (stationGraphicsSnapshot()&bit)!=0;}
static int stationGraphicsBackground(){auto s=stationGraphicsSnapshot();return (s&4u)?(int)((s>>6)&3u):2;}
