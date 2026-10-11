// SPDX-License-Identifier: GPL-2.0-or-later
// Isolated Android/ENet transport probe. No game, server, account, or save data.
#include "Common/StationDolphinTransport.h"
#include <arpa/inet.h>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <vector>
using namespace Common::StationDolphin;
static unsigned checks=0;
static void Check(bool value) { ++checks; if(!value) { std::printf("FAIL %u\n",checks); std::exit(1); } }
static std::vector<std::uint8_t> Data(unsigned from,unsigned to,std::size_t n=12)
{
  std::vector<std::uint8_t> frame{'D','P','L','1',static_cast<std::uint8_t>(from),static_cast<std::uint8_t>(to),static_cast<std::uint8_t>(n>>8),static_cast<std::uint8_t>(n)};
  frame.resize(n+8,0x52); return frame;
}
int main()
{
  Check(enet_initialize()==0); Check(!Active()); Check(!Suspended());
  Check(HumanExitAllowed()); Check(!BlockAutomaticStop("OFFLINE")); Check(AuthorizeHumanExit());
  Check(!Configure(true,2,6,2626,1)); Check(!Configure(true,1,2,2626,1));
  Check(!Configure(true,1,7,2626,1)); Check(!Configure(true,1,6,80,1));
  Check(Configure(true,1,30,2626,1)); Check(!Configure(true,1,30,2626,1));
  Check(!HumanExitAllowed());
  ENetAddress address{htonl(INADDR_LOOPBACK),2626};
  ENetHost* server=enet_host_create(&address,4,2,0,0); Check(server); Attach(server,true);
  ENetHost* local=enet_host_create(nullptr,1,2,0,0); Check(local); Attach(local,false);
  ENetAddress local_address{}; Check(enet_socket_get_address(local->socket,&local_address)==0);
  local_address.host=htonl(INADDR_LOOPBACK); Check(SlotForAddress(local_address)==1);
  Check(SlotForAddress(ENetAddress{htonl(0x7f000002u),40002})==2);
  Check(SlotForAddress(ENetAddress{htonl(0x7f000003u),40003})==3);
  Check(SlotForAddress(ENetAddress{htonl(0x7f000004u),40004})==4);
  Check(SlotForAddress(ENetAddress{htonl(0x7f000005u),40005})==0);
  auto frame=Data(2,1);
  Check(Deliver(2,1,frame)==0); AdmitGuests();
  Check(Deliver(2,1,frame)==1); Check(Deliver(2,1,frame)==1);
  Check(!AwaitDelivery(1,0)); Check(!Drained());
  frame.back()^=1; Check(Deliver(2,1,frame)==-1); frame.back()^=1;
  Check(Deliver(3,2,frame)==-1); Check(Deliver(2,0,frame)==-1);
  frame[7]++; Check(Deliver(2,3,frame)==-1); frame[7]--;
  std::array<std::uint8_t,1392> bytes{}; ENetBuffer buffer{bytes.data(),bytes.size()}; ENetAddress from{};
  Check(enet_socket_receive(server->socket,&from,&buffer,1)==12);
  Check(from.host==htonl(0x7f000002u) && from.port==40002);
  Check(!Drained()); Check(AwaitDelivery(1,0)); Check(Drained());
  Check(Pause(2)); const auto frozen=enet_time_get();
  std::this_thread::sleep_for(std::chrono::milliseconds(40)); Check(enet_time_get()==frozen);
  Check(Suspended()); Check(DeferCPURun()); Check(!ConsumeCPURunRequest());
  Check(!Pause(1)); Check(!Resume(1,1)); Check(!Resume(2,0));
  Check(PublishControl(2,1,false)); Check(CurrentControl(2,1,false));
  Check(PublishControl(2,2,true)); Check(!Resume(2,1)); Check(!Resume(2,2));
  Check(!PublishControl(2,1,false)); Check(!PublishControl(2,2,false));
  Check(PublishControl(2,3,false)); Check(Resume(2,3)); Check(!Suspended());
  Check(ConsumeCPURunRequest()); Check(!ConsumeCPURunRequest());
  ENetAddress guest{htonl(0x7f000003u),40003}; ENetBuffer send{bytes.data(),12};
  Check(enet_socket_send(server->socket,&guest,&send,1)==12);
  auto outgoing=TakeOutgoing(3,0); Check(outgoing.size()==20 && outgoing[4]==1 && outgoing[5]==3);
  Check(Drained()); Check(Pause(3));
  Check(PublishControl(3,4,false));
  frame=Data(4,1); Check(Deliver(4,4,frame)==1); Check(!Resume(3,4));
  Check(enet_socket_receive(server->socket,&from,&buffer,1)==12); Check(!Resume(3,4));
  Check(AwaitDelivery(4,0)); Check(Resume(3,4));
  std::uint64_t emergency_serial=0; Check(EmergencySuspend(3,&emergency_serial));
  Check(emergency_serial==4 && CurrentControl(3,4,true)); Check(!Resume(3,4));
  Check(PublishControl(3,5,false)); Check(Resume(3,5));
  for(std::uint64_t revision=6;revision<1006;revision+=2)
  {
    Check(PublishControl(3,revision,false)); Check(PublishControl(3,revision+1,true));
    Check(!Resume(3,revision)); Check(CurrentControl(3,revision+1,true));
  }
  Check(PublishControl(3,1006,false)); Check(Resume(3,1006));
  Check(BlockAutomaticStop("DOLPHIN_TEST_FAILURE")); Check(Suspended()); Check(Failure()=="DOLPHIN_TEST_FAILURE"); Check(!Resume(3,1006));
  Check(AuthorizeHumanExit()); Check(HumanExitAllowed()); Check(!BlockAutomaticStop("HUMAN_EXIT"));
  Close(); Check(!Active()); Check(!Configure(true,1,6,2626,1));
  Detach(local); enet_host_destroy(local); Detach(server); enet_host_destroy(server);
  Check(Configure(false,2,6,2626,1)); Check(Deliver(1,5,Data(1,2))==0);
  Check(!HumanExitAllowed());
  Close(); enet_deinitialize();
  std::printf("{\"checks\":%u,\"passed\":true,\"gameplay\":false}\n",checks); return 0;
}
