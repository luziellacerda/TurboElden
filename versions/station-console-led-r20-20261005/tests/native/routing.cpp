#include <initializer_list>

#include <cstring>
#include <cstdio>
#include <cstdlib>
static bool presentationKeyEqual(const char*a,const char*b){if(!a||!b)return false;while(*a&&*b){char x=*a++,y=*b++;if(x>='A'&&x<='Z')x+=32;if(y>='A'&&y<='Z')y+=32;if(x!=y)return false;}while(*a==' ')a++;while(*b==' ')b++;return *a==*b;}
#include "station_console_keys.h"
#include "neogeo_led_profile.h"
static int n;static void check(bool x){++n;if(!x){printf("FAIL %d\n",n);exit(2);}}
int main(){
 for(const auto&r:stationConsoleAliases)check(stationConsoleKey(r.alias)&&strcmp(stationConsoleKey(r.alias),r.key)==0);
 for(const char*s:{"Neo Geo","Neo Geo CD","neo-geo","neo-geo-cd","neogeo","neogeocd","NEO GEO CD"})check(neoMagazineKey(s));
 for(const char*s:{"Neo Geo Extra","neo-geo-cd-wrong","Nintendo 64","Super Nintendo","MegaDrive",""})check(!neoMagazineKey(s));
 check(!neoMagazineKey(nullptr));check(!stationConsoleKey(nullptr));check(!stationConsoleKey("unknown"));
 check(neoSquareVideoAsset("turbo-system-videos/720-neogeocd.mp4"));
 for(const char*s:{"turbo-system-videos/720-neogeo.mp4","720-neogeocd.mp4","turbo-system-videos/720-neogeocd.mp4.old",""})check(!neoSquareVideoAsset(s));
 check(!neoSquareVideoAsset(nullptr));printf("PASS %d console and LED routing checks\n",n);
}
