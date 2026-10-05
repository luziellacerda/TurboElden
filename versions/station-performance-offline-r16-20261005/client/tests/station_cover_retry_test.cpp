#include "../src/native/station_cover_retry.hpp"
#include <iostream>
#include <stdexcept>
int main(){
 station::CoverRetry retry;
 auto check=[](bool result,const char* name){if(!result)throw std::runtime_error(name);};
 check(retry.ready("item_12345",100),"First visible request allowed");
 retry.failed("item_12345",100,60);
 check(!retry.ready("item_12345",159),"Missing cover cannot spin per frame");
 check(retry.ready("item_67890",159),"Failure does not block other covers");
 check(retry.ready("item_12345",160),"Failed cover becomes eligible without catalog refresh");
 retry.failed("item_12345",160,60);retry.succeeded("item_12345");
 check(retry.ready("item_12345",161),"Success clears old failure");
 retry.failed("item_12345",200,5);
 check(!retry.ready("item_12345",204)&&retry.ready("item_12345",205),"JNI command retry is bounded");
 retry.failed("item_12345",300,60);retry.clear();
 check(retry.ready("item_12345",301),"Catalog replacement clears obsolete state");
 std::cout<<"PASS 7 native cover retry checks (host policy; Android bridge build pending)\n";
}
