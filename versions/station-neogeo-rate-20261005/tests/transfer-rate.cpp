#include <cassert>
#include <cmath>
#include <iostream>
#include "../station/src/native/station_transfer_rate.hpp"
int main() {
 station::TransferRate rate; int checks=0;
 auto check=[&](bool value){assert(value);++checks;};
 check(rate.observe(0,10000000,1000)==0);
 check(rate.observe(100000,10000000,1100)==0); // Wait for an actual sample window.
 check(std::abs(rate.observe(2000000,10000000,1500)-4000000.0)<1);
 check(std::abs(rate.observe(4000000,10000000,2000)-4000000.0)<1);
 check(rate.observe(0,10000000,2100)==0); // Retry resets counter.
 check(std::abs(rate.observe(1000000,10000000,3100)-1000000.0)<1);
 check(rate.observe(2000000,20000000,3200)==0); // Another transfer.
 check(rate.observe(3000000,20000000,3000)==0); // Clock discontinuity.
 check(std::abs(rate.observe(4000000,20000000,4000)-1000000.0)<1);
 std::cout<<"PASS "<<checks<<" measured transfer rate checks\n";
}
