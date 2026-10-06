#pragma once
#include <cstring>
#include <cstddef>
#include "station_game_details.h"
#include "station_future_metadata.h"
// Bounded, platform-scoped lookup. Unknown Unicode never becomes another title.
static bool stationMetadataNormalize(const char*value,char*out,size_t capacity){
 if(!out||!capacity)return false;out[0]=0;if(!value)return false;size_t used=0;
 const unsigned char*s=(const unsigned char*)value;
 for(size_t i=0;s[i];){unsigned c=s[i++];
  if(c>=128){unsigned n=0,v=0;if(c>=0xc2&&c<=0xdf){n=1;v=c&31;}else if(c>=0xe0&&c<=0xef){n=2;v=c&15;}else if(c>=0xf0&&c<=0xf4){n=3;v=c&7;}else return false;
   for(unsigned j=0;j<n;j++){if(!s[i]||(s[i]&0xc0)!=0x80)return false;v=(v<<6)|(s[i++]&63);}c=v;
   if((n==1&&c<128)||(n==2&&c<2048)||(n==3&&c<65536)||c>0x10ffff||(c>=0xd800&&c<=0xdfff))return false;
   if((c>=0xc0&&c<=0xc5)||(c>=0xe0&&c<=0xe5))c='a';
   else if(c==0xc7||c==0xe7)c='c';else if((c>=0xc8&&c<=0xcb)||(c>=0xe8&&c<=0xeb))c='e';
   else if((c>=0xcc&&c<=0xcf)||(c>=0xec&&c<=0xef))c='i';else if(c==0xd1||c==0xf1)c='n';
   else if((c>=0xd2&&c<=0xd6)||(c>=0xf2&&c<=0xf6))c='o';
   else if((c>=0xd9&&c<=0xdc)||(c>=0xf9&&c<=0xfc))c='u';else if(c==0xdd||c==0xfd||c==0xff)c='y';
   else if(c==0x300||c==0x301||c==0x302||c==0x303||c==0x308||c==0x327||c==0x2018||c==0x2019||c==0x201c||c==0x201d||c==0x2013||c==0x2014||c==0x2122||c==0xae||c==0xa9)continue;
   else return false;
  }
  if(c>='A'&&c<='Z')c+=32;if(!((c>='a'&&c<='z')||(c>='0'&&c<='9')))continue;
  if(used+1>=capacity){out[0]=0;return false;}out[used++]=(char)c;
 }
 out[used]=0;return used>0;
}
static char*stationMetadataLast(char*s,char c){size_t n=std::strlen(s);while(n){--n;if(s[n]==c)return s+n;}return nullptr;}
static bool stationMetadataTitle(const char*title,char*out,size_t capacity){
 if(!title)return false;size_t len=std::strlen(title);if(len>=1024)return false;
 char s[1024];std::memcpy(s,title,len+1);while(len&&s[len-1]==' ')s[--len]=0;char*begin=s;while(*begin==' ')++begin;
 if(len&&s[len-1]==')'){
  char*open=stationMetadataLast(begin,'(');if(open){char region[96];size_t count=s+len-1-open-1;
   if(count<sizeof(region)){std::memcpy(region,open+1,count);region[count]=0;for(char*p=region;*p;++p)if(*p>='A'&&*p<='Z')*p+=32;
    static const char*valid[]={"usa","europe","world","japan","brazil","br","usa, europe","europe, usa","japan, usa","usa, japan","japan, europe","japan, usa, europe"};
    for(const auto*r:valid)if(std::strcmp(region,r)==0){*open=0;break;}
   }
  }
 }
 len=std::strlen(begin);while(len&&begin[len-1]==' ')begin[--len]=0;
 char*comma=stationMetadataLast(begin,',');if(comma&&comma[1]==' '){char article[8];size_t n=std::strlen(comma+2);if(n<sizeof(article)){for(size_t i=0;i<=n;i++){char c=comma[i+2];article[i]=c>='A'&&c<='Z'?c+32:c;}if(!std::strcmp(article,"the")||!std::strcmp(article,"a")||!std::strcmp(article,"an")){*comma=0;char moved[1024];size_t rest=std::strlen(begin);if(n+1+rest>=sizeof(moved))return false;std::memcpy(moved,article,n);moved[n]=' ';std::memcpy(moved+n+1,begin,rest+1);return stationMetadataNormalize(moved,out,capacity);}}}
 return stationMetadataNormalize(begin,out,capacity);
}
static const StationGameDetails*stationFutureByKey(const char*key){
 size_t l=0,r=sizeof(stationFutureDetails)/sizeof(stationFutureDetails[0]);
 while(l<r){size_t m=l+(r-l)/2;int c=std::strcmp(key,stationFutureDetails[m].key);if(!c)return &stationFutureDetails[m].details;if(c<0)r=m;else l=m+1;}return nullptr;
}
static const StationGameDetails*findStationGameDetailsForGame(const char*id,const char*platform,const char*title){
 if(id&&*id)if(auto*exact=findStationGameDetails(id))return exact;
 char p[128],name[1024],key[1200];if(!stationMetadataNormalize(platform,p,sizeof(p))||!stationMetadataTitle(title,name,sizeof(name)))return nullptr;
 size_t l=0,r=sizeof(stationMetadataPlatformAliases)/sizeof(stationMetadataPlatformAliases[0]);const char*slug=nullptr;
 while(l<r){size_t m=l+(r-l)/2;int c=std::strcmp(p,stationMetadataPlatformAliases[m].key);if(!c){slug=stationMetadataPlatformAliases[m].platform;break;}if(c<0)r=m;else l=m+1;}if(!slug)return nullptr;
 size_t a=std::strlen(slug),b=std::strlen(name);if(a+b+2>sizeof(key))return nullptr;std::memcpy(key,slug,a);key[a]='|';std::memcpy(key+a+1,name,b+1);return stationFutureByKey(key);
}
