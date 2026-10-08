"""Extract real R73 pacing/stall functions and Java recovery tick/lost methods.
The native structs, clock, peer input and Java socket/listener are test models.
No emulator, Android device, real socket, relay server or gameplay is exercised.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/('sources' if (ROOT/'sources').exists() else 'source')
BASE=Path(r'E:\R73fixed\RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576')
JAVA=Path(r'C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git\versions\station-recovery-handshake-r73-20261007\java\netplay-src\org\emulationstation\frontend\netplay\StationRecoveryTunnel.java')
FRONT='network/netplay/netplay_frontend.c'
REMOVED='''#ifdef ANDROID
      if(station_recovery_active() && netplay->stall==NETPLAY_STALL_RUNNING_FAST)station_recovery_mark_stalled();
#endif
'''

def sha(data):return hashlib.sha256(data).hexdigest()

def block(source,anchor):
    start=source.index(anchor);opening=source.index('{',start);depth=0
    for end in range(opening,len(source)):
        if source[end]=='{':depth+=1
        elif source[end]=='}':
            depth-=1
            if depth==0:return source[start:end+1]
    raise AssertionError(anchor)

PRE=r'''
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "station_recovery.h"
#define ANDROID 1
#define NETPLAY_STALL_NONE 0
#define NETPLAY_STALL_RUNNING_FAST 1
#define NETPLAY_CONN_FLAG_ACTIVE 1
#define NETPLAY_CONNECTION_PLAYING 2
#define NETPLAY_MODUS_INPUT_FRAME_SYNC 1
struct netplay_connection {unsigned flags;int mode,stall,stall_slow;};
typedef struct {int stall;bool remote_paused,is_server;unsigned self_frame_count,unread_frame_count,connections_size,connected_players;int modus;long long stall_time;unsigned read_frame_count[3];struct netplay_connection connections[2];} netplay_t;
static int post_frames;
static long long cpu_features_get_time_usec(void){return 1000000;}
static void netplay_sync_input_post_frame(netplay_t*n,bool stalled){(void)n;if(!stalled)abort();post_frames++;}
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL pacing line%d %s\n",__LINE__,#x);return 2;}}while(0)
'''
POST=r'''
int main(int argc,char**argv){
 bool candidate=argc>1&&strcmp(argv[1],"candidate")==0;
 unsigned catchups=0,sticky=0,total_posts=0;
 station_recovery_configure(true);station_recovery_request(1,false,true);
 for(int host=0;host<2;host++){
  for(int cycle=0;cycle<100;cycle++){
   netplay_t n={0};n.is_server=host;n.connections_size=2;n.connected_players=2;n.modus=NETPLAY_MODUS_INPUT_FRAME_SYNC;
   n.connections[0].flags=NETPLAY_CONN_FLAG_ACTIVE;n.connections[0].mode=NETPLAY_CONNECTION_PLAYING;n.connections[1].stall=77;
   n.self_frame_count=120;n.unread_frame_count=120;n.read_frame_count[1]=60;post_frames=0;
   pacing(&n);CHECK(n.stall==NETPLAY_STALL_NONE);CHECK(pre_frame(&n));CHECK(!station_recovery_is_stalled());
   n.unread_frame_count=60;pacing(&n);CHECK(n.stall==NETPLAY_STALL_RUNNING_FAST);CHECK(n.stall_time==1000000);
   CHECK(!pre_frame(&n));CHECK(post_frames==1);CHECK(n.self_frame_count==120);
   CHECK(n.connections[0].stall==(host?NETPLAY_STALL_RUNNING_FAST:NETPLAY_STALL_NONE));
   /* Two-frame hysteresis is unchanged. 62 still waits, 63 can resume. */
   n.unread_frame_count=62;pacing(&n);CHECK(n.stall==NETPLAY_STALL_RUNNING_FAST);
   n.unread_frame_count=63;pacing(&n);CHECK(n.stall==NETPLAY_STALL_NONE);CHECK(n.connections[0].stall==NETPLAY_STALL_NONE);
   CHECK(n.connections[1].stall==77);CHECK(pre_frame(&n));CHECK(post_frames==1);CHECK(n.self_frame_count==120);catchups++;
   bool flag=station_recovery_is_stalled();CHECK(flag==!candidate);if(flag)sticky++;total_posts+=post_frames;
   /* The R73 bool survives catch-up until a Java wait request clears it. */
   station_recovery_request(cycle+host*100+2,true,true);CHECK(!station_recovery_is_stalled());CHECK(station_recovery_waiting());
   station_recovery_request(cycle+host*100+2,false,true);CHECK(!station_recovery_waiting());
  }
 }
 /* A genuine native protocol failure is still terminal; pacing fix does not mask it. */
 station_recovery_fail();CHECK(station_recovery_waiting());CHECK(station_recovery_failed);
 printf("{\"catchups\":%u,\"stickyFlagsAfterCatchup\":%u,\"postFrameCalls\":%u,\"nativeFlagForJava\":%s,\"nativeFailurePreserved\":true}\n",catchups,sticky,total_posts,candidate?"false":"true");return 0;
}
'''

JAVA_PRE=r'''
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
public class PacingJavaProbe {
 final Object gate=new Object();AtomicBoolean closed=new AtomicBoolean();
 boolean terminal,foreground=true,ticketPending,welcome=true,readyNotified=true;
 long state=2,epoch=7,syncRequested=-1,ticketRequested,nextTicket,lastReceive=System.nanoTime(),pauseSent,readySent,accepted=50;
 int attempts,sends,pauses,states,tickets,closedSockets,pumps;boolean nativeFlag;
 Remote remote=new Remote();Listener listener=new Listener();Bytes rx=new Bytes();
 class Bytes{long delivered=33;}
 class Remote{boolean open=true;boolean isOpen(){return open;}boolean isClosed(){return !open;}void send(int[] f){if(f[0]!=13||f[1]!=7)throw new AssertionError("unexpected control");sends++;}void closeConnection(int c,String s){open=false;closedSockets++;}}
 static class StationRecoveryWire{final int type;final long epoch;StationRecoveryWire(int t,long e,long v){type=t;epoch=e;}int[] encode(){return new int[]{type,(int)epoch};}}
 class Listener{void ticket(){tickets++;}boolean nativeStalled(){return nativeFlag;}void nativeControl(long e,boolean p,boolean v){if(e!=epoch||!p||!v)throw new AssertionError("control");pauses++;nativeFlag=false;}void state(boolean w,boolean s){if(!w||s)throw new AssertionError("state");states++;}void trace(String s){}}
 void pump(){pumps++;}void traceWaiting(long now){}void fatal(String type){throw new AssertionError(type);}
 static void check(boolean condition,String name){if(!condition)throw new AssertionError(name);}
'''
JAVA_POST=r'''
 public static void main(String[] args){
  PacingJavaProbe p=new PacingJavaProbe();boolean stale=Boolean.parseBoolean(args[0]);p.nativeFlag=stale;p.tick();
  check(p.sends==(stale?1:0),"stale pacing flag => actual tick SYNC13");check(p.pauses==p.sends,"only stale pause");
  p.nativeFlag=stale;p.tick();check(p.sends==(stale?1:0),"at most one SYNC per epoch");
  PacingJavaProbe loss=new PacingJavaProbe();RemoteIdentity.run(loss);
  System.out.println("PASS actual Java tick: stale="+stale+" SYNC13="+p.sends+"; actual lost(): pause preserved, offsets unchanged, no SYNC13");
 }
 static class RemoteIdentity{static void run(PacingJavaProbe loss){
  PacingJavaProbe.Remote r=loss.remote;loss.lost(r);
  check(loss.remote==null&&!loss.welcome&&loss.pauses==1&&loss.states==1&&loss.closedSockets==1,"real lost path");
  check(loss.accepted==50&&loss.rx.delivered==33&&loss.sends==0,"no data loss or SYNC");
  loss.lost(r);check(loss.pauses==1,"old socket loss idempotent");
 }}
}
'''

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);a=parser.parse_args()
 out=a.out.resolve();assert out.drive.upper()=='E:';out.mkdir(parents=True,exist_ok=True)
 original=(BASE/FRONT).read_text('utf8');candidate=(SOURCE/FRONT).read_text('utf8')
 assert sha((BASE/FRONT).read_bytes())=='3dea62f27a197f2f4fa7c689a0ed09bbe8840ff1e00bf74edb299a2f40d40afa'
 assert original.count(REMOVED)==1 and original.replace(REMOVED,'')==candidate,'Only pacing escalation may change'
 private=(BASE/'network/netplay/netplay_private.h').read_text('utf8')
 maximum=re.search(r'^#define NETPLAY_MAX_STALL_FRAMES\s+60$',private,re.M).group(0)
 header=(BASE/'frontend/drivers/station_recovery.h').read_bytes();(out/'station_recovery.h').write_bytes(header)
 # Native header is unmodified; only pthread implementation is a host adapter.
 (out/'pthread.h').write_text('#include <windows.h>\ntypedef SRWLOCK pthread_mutex_t;\n#define PTHREAD_MUTEX_INITIALIZER SRWLOCK_INIT\nstatic void pthread_mutex_lock(pthread_mutex_t*p){AcquireSRWLockExclusive(p);}\nstatic void pthread_mutex_unlock(pthread_mutex_t*p){ReleaseSRWLockExclusive(p);}\n','utf8')
 jsource=JAVA.read_text('utf8');tick=block(jsource,'private void tick()');lost=block(jsource,'private void lost(Remote current)')
 jpath=out/'PacingJavaProbe.java';jpath.write_text(JAVA_PRE+tick+'\n'+lost+'\n'+JAVA_POST,'utf8')
 java_bin=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
 subprocess.run([str(java_bin/'javac.exe'),'-d',str(out),str(jpath)],check=True,capture_output=True,text=True)
 results=[];fragments=[]
 for label,source in [('baseline',original),('candidate',candidate)]:
  at=source.index('      case NETPLAY_STALL_RUNNING_FAST:',source.index("/* If we're stalled, consider unstalling. */"))
  stop=source.index('      case NETPLAY_STALL_SPECTATOR_WAIT:',at);unstall=source[at:stop]
  stall=block(source,'      if (netplay->stall == NETPLAY_STALL_NONE &&\n            netplay->self_frame_count >= NETPLAY_MAX_STALL_FRAMES)')
  preframe=block(source,'   if ((netplay->stall || netplay->remote_paused)')
  flush=block(source,'bool station_netplay_recovery_poll(void)')
  c=PRE+'\n'+maximum+'\nstatic void pacing(netplay_t*netplay){unsigned i;switch(netplay->stall){\n'+unstall+'default:break;}\n'+stall+'\n}\nstatic bool pre_frame(netplay_t*netplay){\n'+preframe+'\nreturn true;}\n'+POST
  cpath=out/(label+'-pacing.c');exe=out/(label+'-pacing.exe');cpath.write_text(c,'utf8')
  build=subprocess.run([r'C:\Program Files\LLVM\bin\clang.exe','-std=c11','-I',str(out),str(cpath),'-o',str(exe)],capture_output=True,text=True)
  assert build.returncode==0,build.stderr
  run=subprocess.run([str(exe),label],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
  data=json.loads(run.stdout);flag=str(data['nativeFlagForJava']).lower()
  java=subprocess.run([str(java_bin/'java.exe'),'-cp',str(out),'PacingJavaProbe',flag],capture_output=True,text=True,timeout=5)
  assert java.returncode==0,java.stderr
  results.append({'label':label,'frontendSHA256':sha(source.encode()),'native':data,'java':java.stdout.strip()})
  fragments.append({'label':label,'stallSHA256':sha(stall.encode()),'unstallSHA256':sha(unstall.encode()),'preframeSHA256':sha(preframe.encode()),'recoveryPollSHA256':sha(flush.encode())})
 for name in ('stallSHA256','unstallSHA256','recoveryPollSHA256'):assert fragments[0][name]==fragments[1][name],name
 receipt={'scope':__doc__,'testRecipeSHA256':sha(Path(__file__).read_bytes()),'results':results,'fragments':fragments,
          'r73HeaderSHA256':sha(header),'javaSourceSHA256':sha(JAVA.read_bytes()),'javaTickSHA256':sha(tick.encode()),'javaLostSHA256':sha(lost.encode()),
          'onlyRemovedBlockSHA256':sha(REMOVED.encode()),'removedLines':3,'realGameplay':False,'androidExecuted':False,'serverExecuted':False,
          'officialReference':'https://docs.libretro.com/development/retroarch/netplay/'}
 for path in (out/'pacing-result.json',ROOT/'tests/pacing-result.json'):path.write_text(json.dumps(receipt,indent=2)+'\n','utf8')
 print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
