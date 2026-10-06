#include <cassert>
#include <cstdio>
#include <cstring>
#include <cmath>
#include <initializer_list>
#include "station_theme_palette.h"
#include "station_lottie_once.h"
#include "station_theme_switch_state.h"
#include "station_bottom_action_layout.h"
#include "collection_presentation.h"
static bool utf8(const char*s){for(unsigned i=0;s[i];){unsigned c=(unsigned char)s[i],n=c<128?1:c<224?2:c<240?3:4;for(unsigned j=1;j<n;j++)if(!s[i+j]||((unsigned char)s[i+j]&192)!=128)return false;i+=n;}return true;}
int main(){unsigned checks=0;
 for(unsigned alpha=0;alpha<256;alpha++)for(unsigned color:{0x080c0900u,0x02060400u,0x151d1700u,0x131E1700u,0x37FF6400u,0xff556600u,0xffffff00u}){
  stationThemeId=0;assert(stationThemeColor(color|alpha)==(color|alpha));checks++;
  stationThemeId=1;auto c=stationThemeColor(color|alpha);assert((c&255)==alpha);assert(stationThemeColor(c)==c);checks+=2;
  if(color==0x37ff6400||color==0xff556600||color==0xffffff00){assert(c==(color|alpha));checks++;}
 }
 for(float h:{360.f,480.f,720.f,1080.f,1440.f,2160.f})for(float ratio:{1.25f,1.5f,1.777778f,2.f,2.166667f,2.4f}){
  float w=h*ratio;auto a=stationThemeToggleRect(w,h,true),b=stationThemeToggleRect(w,h,false);
  assert(b.x+b.w<w*.965f&&b.y>h*.945f&&b.y+b.h<h&&a.y+a.h<h*.235f&&a.y>h*.139f);checks++;
  auto primary=stationBottomGameAction(w,h,0);auto l=stationPrimaryRatingLayout(primary,primary.h*.98f);
  assert(l.label.w>primary.h*2&&l.label.x+l.label.w+l.gap<=l.stars.x+.01f&&l.stars.x+l.stars.w<primary.x+primary.w&&l.stars.y>=primary.y&&l.stars.y+l.stars.h<=primary.y+primary.h);checks++;
  for(int i=0;i<2;i++){auto r=stationThemeToggleRect(w,h,i==1);float x=r.x+r.w*.5f,y=r.y+r.h*.5f;StationThemeToggleGesture g;
   assert(g.touch(0,1,x,y,r)==0);assert(g.touch(2,1,x,y,r)==1);assert(g.touch(2,1,x,y,r)==-1);checks+=3;
   g.touch(0,1,x,y,r);assert(g.touch(1,1,0,0,r)==0);assert(g.touch(2,1,x,y,r)==0);checks+=2;
   g.touch(0,1,x,y,r);assert(g.touch(2,2,x,y,r)==0);assert(g.touch(2,1,x,y,r)==1);checks+=2;
   g.touch(0,1,x,y,r);assert(g.touch(3,1,x,y,r)==0);assert(!g.pressed);checks+=2;
  }
 }
 StationLottieOnce animation;
 for(unsigned i=0;i<1000;i++){assert(animation.frame(i*113)==0);checks++;}
 for(unsigned start:{0u,1000u,0xfffffff0u}){
  animation.press(start);for(unsigned t=0;t<3003;t++){assert(animation.frame(start+t)==t*90u/3003u);checks++;}
  assert(animation.frame(start+3003)==0&&!animation.playing);checks++;assert(animation.frame(start+6006)==0);checks++;
 }
 char body[6144];const char*examples[]={"Título real A","Título real B","Título real C"};
 for(auto&e:collectionEditorials){
  assert(strlen(e.text)>650);assert(strstr(e.text,"\n\n"));checks+=2;
  for(unsigned count:{0u,1u,3u,191u,40000u}){
   collectionSynopsis(body,sizeof(body),collectionLeafName(e.path),e.platform,count,0,examples,3,e.path);
   assert(strstr(body,e.text)&&strstr(body,examples[0])&&strlen(body)>850&&strlen(body)<4000&&utf8(body));checks++;
  }
  for(unsigned capacity=0;capacity<3600;capacity+=7){
   memset(body,0x5a,sizeof(body));collectionSynopsis(body,capacity,e.path,e.platform,9,0,examples,3,e.path);
   assert(body[capacity]==0x5a);if(capacity){assert(strlen(body)<capacity&&utf8(body));}checks+=2;
  }
 }
 assert(sizeof(collectionEditorials)/sizeof(collectionEditorials[0])==14);checks++;
 for(auto&info:systemInfos){collectionSynopsis(body,sizeof(body),"Todos os jogos",info.key,40000,2,examples,3);assert(strstr(body,info.description)&&strstr(body,"40000")&&utf8(body)&&strlen(body)<6000);checks++;}
 collectionSynopsis(body,sizeof(body),"Coleção futura","Plataforma futura",2,0,examples,3,"Nova/Pasta");assert(strstr(body,"Coleção futura")&&strstr(body,examples[2])&&utf8(body));checks++;
 assert(!collectionEditorial("Neo Geo","# 1 - METAL SLUG COLEÇÃO #/Nova"));checks++;
 printf("PASS %u theme, gesture, one-shot Lottie, rating geometry and complete collection editorial checks\n",checks);
}
