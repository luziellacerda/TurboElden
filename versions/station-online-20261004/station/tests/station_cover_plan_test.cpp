#include "../src/native/station_cover_plan.hpp"
#include "../src/native/station_cover_retry.hpp"
#include <string>
#include <iostream>
#include <stdexcept>
struct Item {std::string folder,platform;};
int main(){
 int checks=0;auto check=[&](bool result,const char* name){++checks;if(!result)throw std::runtime_error(name);};
 std::vector<Item> items{{"snes"},{"mega"},{"snes"},{"snes"},{"mega"},{"snes"}};
 auto plan=station::coverPlan(items,std::vector<size_t>{2,0,2,99});
 check(plan==std::vector<size_t>({2,0,3,5}),"Visible first; remaining selected-platform covers follow once");
 check(station::coverPlan(items,std::vector<size_t>{4})==std::vector<size_t>({4,1}),"Changed platform gets its own continuous queue");
 check(station::coverPlan(items,std::vector<size_t>{99}).empty(),"Invalid priority never broadens to every platform");
 check(station::coverPlan(std::vector<Item>{},std::vector<size_t>{0}).empty(),"Empty catalog safe");
 station::CoverRetry retry;retry.failed("id",100,60);check(!retry.ready("id",159),"Missing image backoff honored");
 retry.succeeded("id");check(retry.ready("id",101),"Cancellation/success clear retry state immediately");
 retry.failed("id",200,3);check(!retry.ready("id",202)&&retry.ready("id",203),"Server Retry-After deadline is exact in native seconds");
 std::vector<Item> shared{{"psp","PSP"},{"psp","PSP BR"},{"psp","PSP"}};
 check(station::coverPlan(shared,std::vector<size_t>{0})==std::vector<size_t>({0,2}),"Shared emulator folder does not prefetch another platform variant");
 station::CoverBackoff pressure;check(pressure.prefetchAllowed(100),"No artificial delay before server throttles");
 pressure.rateLimited(100,3000);check(!pressure.prefetchAllowed(102),"429 stops offscreen plan until server deadline");
 pressure.rateLimited(101,1000);check(!pressure.prefetchAllowed(102)&&pressure.prefetchAllowed(103),"Shorter concurrent 429 cannot shorten global deadline");
 std::cout<<"PASS "<<checks<<" native prefetch/retry policy checks\n";
}
