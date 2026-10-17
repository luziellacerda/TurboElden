// SPDX-License-Identifier: GPL-2.0-or-later
// Discrete schedule model with real protocol; not phone or network measurement.
// One-way5ms, owner60Hz, work0/3/6/9ms, independent owner phases.

#define main existing_protocol_probe_main
#include "protocol_probe.cpp"
#undef main
struct PacingResult { unsigned host{},guest{}; };
PacingResult pace(unsigned pollMs,unsigned oneWayMs,unsigned workMs,unsigned guestPhaseUs) {
 Pair p(4096,4);p.init();
 struct Flight {std::uint64_t due;bool toHost;Bytes packet;};
 struct Owner {std::uint64_t next{},done{};bool executing{};Lease lease{};};
 Owner h{},g{};g.next=guestPhaseUs;std::deque<Flight> flight;
 std::uint64_t pollAt[2]={0,guestPhaseUs};constexpr std::uint64_t period=16667;
 auto finish=[&](Session& s,Core& c,Owner& o,std::uint64_t now){
  if(o.executing&&o.done<=now){eq(s.ownerComplete(o.lease),Result::Ok,"real protocol owner completion");++c.runs;o.executing=false;}
 };
 auto begin=[&](Session& s,Owner& o,unsigned slot,std::uint64_t now){
  if(now<o.next||o.executing)return;o.next=now+period;
  eq(s.ownerCheckpoint(),Result::Ok,"owner live while waiting");
  if(s.needsLocalSample())eq(s.ownerSampleLocal(slot==1?0x20:0x40),Result::Ok,"sample future input");
  auto r=s.ownerBegin(o.lease);if(r==Result::Wait)return;eq(r,Result::Ok,"owner lease");o.executing=true;o.done=now+workMs*1000;
 };
 for(std::uint64_t now=0;now<10000000;now+=100){
  while(!flight.empty()&&flight.front().due<=now){auto f=std::move(flight.front());flight.pop_front();p.accept(f.toHost?p.h:p.g,f.toHost?2:1,std::move(f.packet));}
  finish(p.h,p.hc,h,now);finish(p.g,p.gc,g,now);
  for(unsigned i=0;i<2;i++)if(now>=pollAt[i]){
   for(;;){auto b=(i?p.g:p.h).takeOutgoing();if(b.empty())break;flight.push_back({now+oneWayMs*1000,i==1,std::move(b)});}
   pollAt[i]=now+std::max(100u,pollMs*1000);
  }
  begin(p.h,h,1,now);begin(p.g,g,2,now);p.clearEvents();
 }
 check(!p.h.status().failed&&!p.g.status().failed,"no simulation failure");return{p.hc.runs,p.gc.runs};
}
int main(){try{for(unsigned work:{0u,3u,6u,9u})for(unsigned phase:{0u,4000u,8000u,12000u})for(unsigned poll:{25u,2u,0u}){
 auto r=pace(poll,5,work,phase);if(poll==0)check(r.host>=599&&r.guest>=597,"event-driven model sustains target over tested phase/work matrix");std::cout<<"pollMs="<<poll<<" oneWayMs=5 workMs="<<work<<" guestPhaseUs="<<phase<<" hostFps="<<r.host/10.0<<" guestFps="<<r.guest/10.0<<"\n";
 }return 0;}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
