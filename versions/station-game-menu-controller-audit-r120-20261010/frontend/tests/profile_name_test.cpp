#include "../station_profile_bridge.h"
#include "../station_profile_state.hpp"
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <vector>
static unsigned checks=0;
static void check(bool condition,const char* message){++checks;if(!condition){std::fprintf(stderr,"FAIL %s\n",message);std::exit(1);}}
int main(){
 station::ProfileName profile;char output[1025]{};uint64_t revision=99;
 check(profile.revision()==0,"initial revision");
 check(profile.copyName(output,sizeof(output),&revision)&&revision==0&&!output[0],"initial empty snapshot");
 profile.publish("");check(profile.revision()==1,"first empty publication");
 profile.publish("");check(profile.revision()==1,"same empty does not invalidate cache");
 profile.publish("Comprador");check(profile.revision()==2,"changed name revision");
 check(profile.copyName(output,sizeof(output),&revision)&&std::string(output)=="Comprador"&&revision==2,"name and revision together");
 profile.publish("Comprador");check(profile.revision()==2,"same name preserves revision");
 profile.publish(u8"João 李 🎮");check(profile.revision()==3,"UTF8 publication");
 const std::string utf8=u8"João 李 🎮";
 check(profile.copyName(output,sizeof(output),&revision)&&std::string(output)==utf8&&revision==3,"UTF8 complete");
 std::vector<char> exact(utf8.size()+1,'x');
 check(profile.copyName(exact.data(),exact.size(),&revision)&&std::string(exact.data())==utf8,"exact capacity includes NUL");
 std::vector<char> small(utf8.size(),'x');revision=99;
 check(!profile.copyName(small.data(),small.size(),&revision)&&!small[0]&&revision==0,"small buffer clears without partial Unicode");
 revision=99;check(!profile.copyName(nullptr,1,&revision)&&revision==0,"null buffer");
 output[0]='x';revision=99;check(!profile.copyName(output,0,&revision)&&output[0]=='x'&&revision==0,"zero capacity untouched buffer");
 output[0]='x';check(!profile.copyName(output,sizeof(output),nullptr)&&!output[0],"missing revision rejected");
 profile.publish("");check(profile.copyName(output,1,&revision)&&!output[0]&&revision==4,"empty publication clears previous name");
 profile.publish(std::string(1024,'A'));
 check(profile.copyName(output,sizeof(output),&revision)&&std::strlen(output)==1024&&revision==5,"JNI maximum input fits 1025 bytes");
 char one='x';revision=99;check(!profile.copyName(&one,1,&revision)&&one==0&&revision==0,"one byte insufficient nonempty");
 profile.publish("Nova pessoa");check(profile.copyName(output,sizeof(output),&revision)&&std::string(output)=="Nova pessoa"&&revision==6,"new owner name replaces prior");
 // Real concurrent publisher/readers; each copied name must agree with its revision.
 station::ProfileName concurrent;std::atomic<bool> start{false},done{false},bad{false};std::atomic<uint64_t> reads{0};
 std::vector<std::thread> readers;
 for(int r=0;r<3;++r)readers.emplace_back([&]{
  while(!start.load(std::memory_order_acquire))std::this_thread::yield();
  do{char text[80];uint64_t rev=0;if(!concurrent.copyName(text,sizeof(text),&rev))bad=true;
   else if(rev==0){if(text[0])bad=true;}else if(std::string(text)!="Pessoa-"+std::to_string(rev))bad=true;
   ++reads;
  }while(!done.load(std::memory_order_acquire));
 });
 start.store(true,std::memory_order_release);
 for(uint64_t i=1;i<=20000;++i){const std::string name="Pessoa-"+std::to_string(i);concurrent.publish(name);concurrent.publish(name);}
 done.store(true,std::memory_order_release);for(auto& reader:readers)reader.join();
 check(!bad.load(),"concurrent name and revision stay consistent");
 check(concurrent.revision()==20000,"identical republication under contention stays cached");
 check(reads.load()>0,"concurrent readers ran");
 std::printf("PASS %u profile checks; %llu concurrent snapshots; 20000 changed and 20000 identical publications\n",checks,static_cast<unsigned long long>(reads.load()));
}
