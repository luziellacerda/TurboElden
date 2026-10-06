#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>
#include <fstream>
#include <iterator>
#include <chrono>
#include "station_theme_palette.h"
#include "station_theme_switch_state.h"
#include "station_lottie_decode.h"
#include "station_lottie_assets.h"
#include "station_metadata_lookup.h"
#include "station_bottom_action_layout.h"
#include "station_chatbot_state.h"
#include "station_online_robot_state.h"
static unsigned long checks;
#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"Failed %s:%d: %s\n",__FILE__,__LINE__,#v);return 1;}}while(0)
int main(int argc,char**argv){
 CHECK(argc==5);unsigned output[384*216+2];
 for(unsigned a=0;a<4;a++){
  std::ifstream f(argv[a+1],std::ios::binary);std::vector<char>b((std::istreambuf_iterator<char>(f)),{});CHECK(!b.empty()&&b.size()%4==0);std::vector<unsigned>rle(b.size()/4);std::memcpy(rle.data(),b.data(),b.size());
  const unsigned*offsets=a==0?stationLottie_switch_offsets:a==1?stationLottie_stars_offsets:a==2?stationLottie_chatbot_offsets:stationLottie_online_offsets;unsigned frames=a==0?stationLottie_switch_frames:a==1?stationLottie_stars_frames:a==2?stationLottie_chatbot_frames:stationLottie_online_frames,pixels=a==0?384*216:a==1?128*128:a==2?stationLottie_chatbot_width*stationLottie_chatbot_height:stationLottie_online_width*stationLottie_online_height;
  CHECK(offsets[frames]==rle.size());
  for(unsigned frame=0;frame<frames;frame++){output[0]=output[pixels+1]=0xface0001;CHECK(stationLottieDecode(output+1,pixels,rle.data(),offsets[frame],offsets[frame+1],rle.size()));CHECK(output[0]==0xface0001&&output[pixels+1]==0xface0001);CHECK(!stationLottieDecode(output,pixels,rle.data(),offsets[frame],offsets[frame+1]+1,rle.size()));}
 }
 for(unsigned start:{0u,100000u,0xfffffff0u}){
  StationChatbotPlayback chatbot;StationOnlineRobotPlayback online;
  CHECK(chatbot.frame(start)==0&&online.frame(start)==0);chatbot.press(start);online.press(start);
  for(unsigned i=0;i<4034;i++){
   CHECK(online.frame(start+i)==(i*60/1000>241?241:i*60/1000));
   if(i<2867)CHECK(chatbot.frame(start+i)==(i*30/1000>85?85:i*30/1000));else CHECK(chatbot.frame(start+i)==0&&!chatbot.playing);
  }
  CHECK(online.frame(start+4034)==0&&!online.playing);
 }
 for(float h:{360.f,480.f,720.f,1080.f,1440.f,2160.f})for(float ratio:{1.25f,1.5f,1.777778f,2.f,2.166667f,2.4f}){
  float w=h*ratio,aspect=(float)stationLottie_online_width/stationLottie_online_height;auto r=stationOnlineRobotRect(w,h,aspect),b=stationBottomGameAction(w,h,1);
  CHECK(r.w>0&&r.h>0&&r.y>=h*.830f&&r.y+r.h<b.y);CHECK(r.x>=b.x&&r.x+r.w<=b.x+b.w);CHECK((r.w/r.h-aspect)<.0001f);
 }
 unsigned data[]={0,1,1,2,10,3};CHECK(!stationLottieDecode(output,1,data,0,2,6));CHECK(!stationLottieDecode(output,1,data,4,6,6));CHECK(!stationLottieDecode(output,1,data,5,4,6));CHECK(!stationLottieDecode(output,1,data,0,8,6));CHECK(stationLottieDecode(output,1,data,2,4,6)&&output[0]==2);CHECK(!stationLottieDecode(nullptr,1,data,0,2,6));
 for(unsigned start:{0u,10000u,0xfffffff0u}){
  StationThemeTransition t;CHECK(t.frame(0,start)==85);CHECK(t.frame(1,start)==85);
  unsigned prior=85;for(unsigned i=1;i<1500;i++){unsigned v=t.frame(1,start+i);CHECK(v<=prior&&v<=85);prior=v;}CHECK(prior==0);
  CHECK(t.frame(0,start+1500)==0);CHECK(t.frame(0,start+2000)==30);CHECK(t.frame(1,start+2000)==30);CHECK(t.frame(1,start+2200)==18);CHECK(t.frame(1,start+3000)==0);
  for(unsigned i=0;i<1000;i++)CHECK(t.frame(1,start+5000+i*31)==0);
 }
 char norm[1024];CHECK(stationMetadataTitle("Legend of Zelda, The (USA, Europe)",norm,sizeof(norm))&&std::strcmp(norm,"thelegendofzelda")==0);CHECK(stationMetadataTitle("Super Mario World (Hack)",norm,sizeof(norm))&&std::strcmp(norm,"supermarioworldhack")==0);
 CHECK(stationMetadataNormalize("Pok\xc3\xa9mon\xe2\x84\xa2",norm,sizeof(norm))&&std::strcmp(norm,"pokemon")==0);CHECK(!stationMetadataNormalize("Mario \xe6\x97\xa5",norm,sizeof(norm)));CHECK(!stationMetadataNormalize("\xc0\x81",norm,sizeof(norm)));CHECK(!stationMetadataNormalize("\xf0\x80\x80\x80",norm,sizeof(norm)));CHECK(!stationMetadataNormalize("long",norm,3));
 size_t count=sizeof(stationFutureDetails)/sizeof(stationFutureDetails[0]);auto begin=std::chrono::steady_clock::now();
 for(size_t i=0;i<count;i++){auto&e=stationFutureDetails[i];CHECK(!i||std::strcmp(stationFutureDetails[i-1].key,e.key)<0);CHECK(stationFutureByKey(e.key)==&e.details);CHECK(e.details.ratingThousandths>=-1&&e.details.ratingThousandths<=1000);CHECK(e.details.players&&(*e.details.players||e.details.ratingThousandths>=0));}
 for(auto&e:stationGameDetails){CHECK(findStationGameDetailsForGame(e.id,"incorrect","incorrect")==&e);CHECK(e.ratingThousandths>=-1&&e.ratingThousandths<=1000);}
 auto*game=findStationGameDetailsForGame("new-future-id","Xbox 360","Halo 3");CHECK(game&&*game->players&&game->ratingThousandths>=0);CHECK(!findStationGameDetailsForGame("not-there","Unknown platform","Halo 3"));CHECK(!findStationGameDetailsForGame("not-there","Xbox 360","Absolutely nonexistent title 99177"));
 CHECK(!stationFutureByKey("megadrive|blockout")); // Ambiguous public entries never guessed in future fallback.
 double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-begin).count();
 printf("PASS %lu checks; %zu metadata keys; complete binary-search sweep %.3f ms (host only)\n",checks,count,ms);
}
