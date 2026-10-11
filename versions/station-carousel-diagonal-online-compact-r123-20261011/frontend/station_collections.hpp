#pragma once
#include <map>
#include <string>
#include <vector>
namespace station {
// These are presentation paths, never filesystem destinations.
inline bool validCollectionPath(const std::string& path){
 if(path.empty())return true;if(path.size()>2048)return false;
 size_t start=0;unsigned depth=0;
 while(start<path.size()){
  size_t end=path.find('/',start);if(end==std::string::npos)end=path.size();
  std::string part=path.substr(start,end-start);
  if(part.empty()||part.size()>320||part=="."||part==".."||++depth>8)return false;
  bool meaningful=false;for(unsigned char c:part){if(c<32||c==127||c=='\\')return false;if(c!=' ')meaningful=true;}
  if(!meaningful)return false;if(end==path.size())return true;start=end+1;
 }
 return false;
}
inline bool collectionContains(const std::string& parent,const std::string& path){
 return parent.empty()||path==parent||(path.size()>parent.size()&&path.compare(0,parent.size(),parent)==0&&path[parent.size()]=='/');
}
struct CollectionChild {std::string path,name,cover;size_t count=0;};
struct CollectionListing {size_t direct=0,total=0;std::map<std::string,CollectionChild> children;};
template<class Items> CollectionListing collectionListing(const Items& items,const std::map<std::string,std::string>& paths,const std::string& platform,const std::string& parent){
 CollectionListing out;if(!validCollectionPath(parent))return out;
 for(const auto& item:items){
  if(item.platform!=platform)continue;auto found=paths.find(item.id);std::string path=found==paths.end()?"":found->second;
  if(!collectionContains(parent,path))continue;out.total++;
  if(path==parent){out.direct++;continue;}
  size_t start=parent.empty()?0:parent.size()+1,end=path.find('/',start);
  std::string name=path.substr(start,end==std::string::npos?std::string::npos:end-start);
  auto& child=out.children[name];child.name=name;child.path=parent.empty()?name:parent+"/"+name;child.count++;
  if(child.cover.empty()&&!item.coverPath.empty())child.cover=item.coverPath;
 }
 return out;
}
}
