from pathlib import Path
import hashlib,json,re,subprocess
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=R/'ui-r8';N=R/'native';S=R/'netplay/src/org/emulationstation/frontend/netplay'
checks=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)});assert value,name
def method(s,name):
 p=s.index(name);a=s.index('{',p);i=a+1;depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 return s[p:i]
old=(W/'before/StationRoomsActivity.java').read_text('utf8');new=(S/'StationRoomsActivity.java').read_text('utf8')
for signature in ('private void action(','private void createRoom(','private void join(','private void command(','private void sendChat(','private void launch(','private void exitRooms(','private void page(','private void deliver(','private void cancelAll(','protected void onStop(','protected void onDestroy('):
 check('unchanged business logic '+signature,method(old,signature)==method(new,signature))
for name in ('StationOnlineClient.java','StationOnlineGame.java','StationRoomState.java','StationPresence.java','StationRetroLaunch.java','StationRetroActivity.java','StationGameSession.java'):
 baseline=Path('work/TurboElden-git/versions/station-online-20261004/netplay/src/org/emulationstation/frontend/netplay')/name
 if not baseline.exists():
  hits=list(Path('work/TurboElden-git/versions/station-online-20261004').rglob(name));assert len(hits)==1;baseline=hits[0]
 check('source unchanged '+name,baseline.read_text('utf8')==(S/name).read_text('utf8'))
for name,signature in [('native_netplay.h','static bool touchOnlineAction('),('native_netplay.h','static bool dispatchStationNetplay(')]:
 check('unchanged native route '+signature,method((W/'before'/name).read_text('utf8'),signature)==method((N/name).read_text('utf8'),signature))
check('chat separate from room controls','scroll(right,messages)' in new and 'card(messages)' in new)
check('compose gated by membership','composer(mine!=null)' in new and 'composer(false)' in new)
check('loading and offline states explicit','loadingLobby();' in new and 'if(state.get()==null)unavailableLobby();' in new)
check('no fake players','snapshot.optJSONArray("peers")' in new)
check('exactly one continuous animated CTA',new.count('.setMotion(true)')==1)
b=(S/'StationActionButton.java').read_text('utf8')
check('animation visibility guard','isAttachedToWindow()&&getWindowVisibility()==View.VISIBLE&&isShown()&&hasWindowFocus()' in b)
check('animation cancelled on detach','onDetachedFromWindow(){if(animator!=null){animator.cancel();animator=null;}' in b)
check('disabled button has distinct state','new int[]{-android.R.attr.state_enabled}' in b)
skin=(N/'native_skin.h').read_text('utf8');online=(N/'native_netplay.h').read_text('utf8')
check('game actions share renderer','drawGameAction(x,y,bw,bh,' in skin and 'drawGameAction(x,h*.908f,bw,h*.065f,' in online)
check('game actions share label scale','systemsMode?.92f:gameActionTextScale' in skin and 'h*.065f,gameActionTextScale' in online)
check('confirmation rim preserved','bool confirming=action==2&&selected>=0&&at<int>(p,0x16c)==selected' in skin)
check('platform open renderer untouched','if(systemsMode&&action==0){drawPrimaryOpen(p,x,y,bw,bh);continue;}' in skin)

# Execute the exact native helper with a captured renderer on Windows.
formation=(N/'native_formation.h').read_text('utf8');motion=(N/'native_action_motion.h').read_text('utf8')
cpp='''#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <vector>
using U=uintptr_t;struct Vertex{float x,y,u,v;unsigned color;};
static unsigned ticks;static std::vector<Vertex> captured;static int draws;
static unsigned clockTick(){return ticks;}static unsigned packed(unsigned c){return c;}
static void bind(unsigned){}static void draw(const Vertex*v,unsigned n,int,int){assert(n==286);captured.assign(v,v+n);draws++;}
template<class T>static T fn(U p){if(p==0x39e240)return (T)clockTick;if(p==0x2e3980)return (T)packed;if(p==0x2e52e8)return (T)bind;assert(p==0x2e5470);return (T)draw;}
static void openButtonFill(float,float,float w,float h,unsigned,unsigned){assert(w>0&&h>0);}
'''
for src,sig in ((formation,'static float absolute('),(formation,'static float squareRoot('),(formation,'static unsigned blendColor('),(motion,'static float actionClamp('),(motion,'static float actionEase('),(motion,'static float actionCycle('),(motion,'static float actionInset(')):
 cpp+=method(src,sig)+'\n'
cpp+='\n#include "native_game_actions.h"\n'+r'''
int main(){
 unsigned frames[]={0,100,170,420,800,1200,2000,3399,3400,0xfffffff0u};int cases=0;
 for(float width:{120.f,200.f,351.f,600.f})for(float height:{32.f,44.f,70.f})for(unsigned t:frames)for(int slot=0;slot<6;slot++)for(bool disabled:{false,true}){
  ticks=t;drawGameAction(10,20,width,height,slot,disabled,false,false);assert(captured.size()==286);
  for(const auto&v:captured){assert(std::isfinite(v.x)&&std::isfinite(v.y));assert(v.x>=9.99&&v.x<=10+width+.01);assert(v.y>=19.99&&v.y<=20+height+.01);assert((v.color&255)==255);}
  cases++;
 }
 int before=draws;drawGameAction(0,0,0,50,0,false,false,false);assert(before==draws);
 assert(gameActionColor(.3,.4,0,0,false)!=gameActionColor(.3,.4,1300,0,false));
 assert(gameActionColor(.3,.4,0,0,true)==gameActionColor(.3,.4,1300,0,true));
 printf("PASS %d native meshes; clipping, animation, disabled state and zero dimensions\n",cases);
}
'''
(W/'action-test.cpp').write_text(cpp,'utf8')
r=subprocess.run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-I'+str(N),str(W/'action-test.cpp'),'-o',str(W/'action-test.exe')],capture_output=True,text=True);assert r.returncode==0,r.stderr
r=subprocess.run([str(W/'action-test.exe')],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
check('executed native geometry',True)
(W/'tests.json').write_text(json.dumps({'checks':checks,'passed':True,'native':r.stdout,'deviceVisualVerified':False,'note':'Native host geometry and source regressions; Android visual and performance checks require device.'},indent=2)+'\n','utf8')
print(len(checks),'source/host checks passed;',r.stdout)
