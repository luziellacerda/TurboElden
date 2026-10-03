#pragma once
#include <cstdint>
#include <map>
#include <string>

namespace station {
// Kept outside Item: the retained renderer requires its original binary layout.
class CoverRetry {
 std::map<std::string,int64_t> retryAt;
public:
 bool ready(const std::string& id,int64_t now) {
  auto found=retryAt.find(id);
  if(found==retryAt.end())return true;
  if(now<found->second)return false;
  retryAt.erase(found);return true;
 }
 void failed(const std::string& id,int64_t now,int64_t delaySeconds) {
  if(retryAt.size()<4096||retryAt.count(id))retryAt[id]=now+delaySeconds;
 }
 void succeeded(const std::string& id){retryAt.erase(id);}
 void clear(){retryAt.clear();}
};
}
