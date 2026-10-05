#include "../src/native/station_catalog_abi.hpp"
#include <dlfcn.h>
#include <cstdio>
#include <cstring>
#include <new>
int main(int argc,char** argv){
 if(argc!=2)return 2;
 void* library=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);
 if(!library){std::fprintf(stderr,"LOAD FAILED: %s\n",dlerror());return 3;}
 using Constructor=void(*)(station::Catalog*);using Progress=station::Progress(*)(station::Catalog*,size_t);
 auto ctor=reinterpret_cast<Constructor>(dlsym(library,"_ZN14CatalogServiceC1Ev"));
 auto progress=reinterpret_cast<Progress>(dlsym(library,"_ZNK14CatalogService11getDownloadEm"));
 if(!ctor||!progress){std::fprintf(stderr,"Required service export missing\n");return 4;}
 Dl_info info{};if(!dladdr(reinterpret_cast<void*>(ctor),&info))return 5;
 if(reinterpret_cast<uintptr_t>(ctor)-reinterpret_cast<uintptr_t>(info.dli_fbase)!=0x18876c)return 6;
 alignas(station::Catalog) unsigned char storage[sizeof(station::Catalog)]{};
 auto catalog=reinterpret_cast<station::Catalog*>(storage);ctor(catalog);
 auto state=progress(catalog,0);
 void* same=dlopen("libmain.so",RTLD_NOW|RTLD_NOLOAD);
 if(!same||!dlsym(same,"_ZN14CatalogService11getRomsRootEv")){std::fprintf(stderr,"Root lookup failed: %s\n",dlerror());return 8;}
 dlclose(same);
 if(state.active||state.received!=0||state.total!=-1||!state.error.empty())return 7;
 catalog->~Catalog();
 std::puts("PASS native ELF load, renderer addresses and rebuilt progress ABI");
 return 0;
}
