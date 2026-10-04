#include "../src/native/station_cover_publication.hpp"
#include "../src/native/station_cover_retry.hpp"
#include <map>
#include <set>
#include <vector>
#include <string>
#include <cstdio>
#include <stdexcept>
struct Item {bool coverPending,coverReady,installed;std::string coverPath;};
int main(){
 int checks=0;auto check=[&](bool b){if(!b)throw std::runtime_error("publication policy");++checks;};
 std::map<std::string,std::string> inbox{{"item0001","old.img"}};
 station::discardPreviousCoverResults(inbox);check(inbox.empty());
 std::set<std::string> slots{"item0001","item0002"};station::CoverRetry retry;retry.failed("item0001",0,60);
 station::CoverBackoff backoff;backoff.rateLimited(0,60000);int64_t next=80;
 std::vector<Item> items{{true,false,false,""},{true,true,true,"cached.img"}};
 station::resetCoverPublication(slots,retry,items,next);
 check(slots.empty());check(!items[0].coverPending&&!items[1].coverPending);check(next==0);
 check(retry.ready("item0001",1));check(items[1].installed);check(items[1].coverReady);
 check(items[1].coverPath=="cached.img");check(!backoff.prefetchAllowed(1));
 inbox["item0001"]="new.img";check(inbox.at("item0001")=="new.img");
 std::printf("PASS %d native cover publication checks\n",checks);
}
