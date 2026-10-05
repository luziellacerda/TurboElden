#pragma once
// Artwork mapping only; folder IDs, names and game membership remain authoritative in the catalog.
struct CollectionVideoDef {const char*name;const char*asset;float aspect;};
static const CollectionVideoDef collectionVideoDefinitions[]={
 {"BOMBER MAN","turbo-system-videos/720-collection-snes-bomberman.mp4",16.f/9.f},
 {"DONKEY KONG","turbo-system-videos/720-collection-snes-donkeykong.mp4",16.f/9.f},
 {"SUPER MARIO","turbo-system-videos/720-collection-snes-mario.mp4",1.f},
 {"TOP GEAR","turbo-system-videos/720-collection-snes-topgear.mp4",16.f/9.f},
 {"1 -PT-BR","turbo-system-videos/720-collection-snes-ptbr.mp4",16.f/9.f}
};
static bool collectionVideoEqual(const char*a,const char*b){while(*a&&*a==*b){++a;++b;}return *a==*b;}
static bool collectionVideoTrim(char c){return c==' '||c=='#';}
static const CollectionVideoDef*collectionVideoFor(const char*platform,const char*path,bool all){
 if(all||!platform||!path)return nullptr;
 if(!collectionVideoEqual(platform,"Super Nintendo")&&!collectionVideoEqual(platform,"Super Nintendo - BR")&&!collectionVideoEqual(platform,"snes")&&!collectionVideoEqual(platform,"snesbr"))return nullptr;
 const char*leaf=path;for(const char*p=path;*p;p++)if(*p=='/')leaf=p+1;
 while(collectionVideoTrim(*leaf))++leaf;
 const char*end=leaf;while(*end)++end;while(end>leaf&&collectionVideoTrim(end[-1]))--end;
 for(const auto&v:collectionVideoDefinitions){const char*p=leaf,*q=v.name;while(p<end&&*q&&*p==*q){++p;++q;}if(p==end&&!*q)return &v;}
 return nullptr;
}
