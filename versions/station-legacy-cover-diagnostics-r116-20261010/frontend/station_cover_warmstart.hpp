#pragma once
#include <cstdint>
#include <limits>
#include <string>

namespace station {
inline bool parseCoverRevision(const std::string& text,uint64_t* value){
 if(!value||text.empty()||text.size()>20)return false;
 uint64_t parsed=0;
 for(unsigned char c:text){
  if(c<'0'||c>'9')return false;
  const uint64_t digit=static_cast<uint64_t>(c-'0');
  if(parsed>(std::numeric_limits<uint64_t>::max()-digit)/10)return false;
  parsed=parsed*10+digit;
 }
 if(parsed==0)return false;*value=parsed;return true;
}

inline bool validWarmCoverPath(const std::string& path,const std::string& coverId,uint64_t revision){
 if(path.empty()||path.size()>4096||coverId.empty()||revision==0||path[0]!='/')return false;
 for(unsigned char c:path)if(c==0||c<0x20||c==0x7f)return false;
 if(path.find("/../")!=std::string::npos||path.find("/./")!=std::string::npos||
    (path.size()>=3&&path.compare(path.size()-3,3,"/..") == 0)||
    (path.size()>=2&&path.compare(path.size()-2,2,"/.") == 0))return false;
 const std::string dataRoot="/data/data/org.turboramastation.frontend/no_backup/";
 const std::string userRoot="/data/user/0/org.turboramastation.frontend/no_backup/";
 const std::string canonical="station-v2/covers/"+coverId+"-"+std::to_string(revision)+".img";
 if(path==dataRoot+canonical||path==userRoot+canonical)return true;
 const char*extensions[]={".png",".jpg",".jpeg",".webp",".gif"};
 for(const char*extension:extensions){
  const std::string legacy="station-covers/"+coverId+extension;
  if(path==dataRoot+legacy||path==userRoot+legacy)return true;
 }
 return false;
}

inline bool sameWarmCoverIdentity(const std::string& oldItemId,const std::string& oldCoverId,uint64_t oldRevision,
                                  const std::string& newItemId,const std::string& newCoverId,uint64_t newRevision){
 return oldRevision>0&&oldItemId==newItemId&&oldCoverId==newCoverId&&oldRevision==newRevision;
}

template<class CoverItem>
inline bool preserveWarmCover(const CoverItem& previous,uint64_t oldRevision,CoverItem& next,uint64_t nextRevision){
 if(!previous.coverReady||previous.coverPath.empty()||next.coverReady||!next.coverPath.empty()||
    !sameWarmCoverIdentity(previous.id,previous.coverId,oldRevision,next.id,next.coverId,nextRevision))return false;
 next.coverPath=previous.coverPath;next.coverReady=true;next.coverFailed=false;next.coverPending=false;return true;
}
}
