"""Execute extracted production C with real host mutexes/threads.

RetroArch connection arrays, getpeername, sync and flush are bounded fixtures.
No Android, emulated frames, ROM, TLS or multiplayer gameplay is claimed.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,os,shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source'
def sha(b):return hashlib.sha256(b).hexdigest()
def function(text,name):
    pos=text.index(name+'(');start=text.rfind('\n',0,pos)+1;end=text.index('{',pos)+1;depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]
PREAMBLE=r'''
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef SRWLOCK pthread_mutex_t;
#define PTHREAD_MUTEX_INITIALIZER SRWLOCK_INIT
static void pthread_mutex_lock(pthread_mutex_t *m){AcquireSRWLockExclusive(m);}
static void pthread_mutex_unlock(pthread_mutex_t *m){ReleaseSRWLockExclusive(m);}
static unsigned checks;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(2);}}while(0)
'''
NET_FIXTURE=r'''
#define MAX_CLIENTS 32
#define NETPLAY_CONN_FLAG_ACTIVE 1
#define NETPLAY_CONNECTION_PLAYING 5
#define NETPLAY_MODUS_INPUT_FRAME_SYNC 1
struct socket_buffer {unsigned used;};
struct netplay_connection {unsigned flags,mode;int fd;struct socket_buffer send_packet_buffer;};
typedef struct netplay {
 bool is_server;unsigned modus,self_mode;uint32_t self_devices,connected_players;
 uint32_t client_devices[MAX_CLIENTS];size_t connections_size;
 struct netplay_connection connections[6];
} netplay_t;
static struct {netplay_t *data;} networking_driver_st;
static bool sync_success=true,flush_success=true;
static unsigned flush_calls;
static bool netplay_sync_pre_frame(netplay_t *np){(void)np;return sync_success;}
static bool netplay_send_flush(struct socket_buffer *s,int fd,bool block){(void)s;(void)fd;(void)block;flush_calls++;return flush_success;}
static unsigned buf_used(struct socket_buffer *s){return s->used;}
#define HAVE_INET6 1
typedef int socklen_t;
static struct sockaddr_storage fake_peer;
static int fake_peer_result;
static int test_getpeername(int fd,struct sockaddr *peer,int *len){(void)fd;memcpy(peer,&fake_peer,sizeof(fake_peer));*len=sizeof(fake_peer);return fake_peer_result;}
#define getpeername test_getpeername
'''
TEST=r'''
static void new_profile(unsigned self,uint32_t mask,unsigned count,bool host)
{
 station_multiplayer_end_launch();station_recovery_reset();
 CHECK(station_multiplayer_configure(self,mask,count,host));
 CHECK(!station_multiplayer_active());
 station_multiplayer_begin_launch();CHECK(station_multiplayer_enable(host));
 station_recovery_configure(true);station_recovery_request(1,true,true);
}
static void basic_profile(void)
{
 station_multiplayer_end_launch();
 CHECK(!station_multiplayer_configure(4,15,4,true));
 CHECK(!station_multiplayer_configure(0,0,2,true));
 CHECK(!station_multiplayer_configure(0,31,4,true));
 CHECK(!station_multiplayer_configure(0,3,3,true));
 CHECK(!station_multiplayer_configure(0,1,1,true));
 CHECK(!station_multiplayer_configure(0,6,2,true));
 CHECK(!station_multiplayer_configure(0,15,5,true));
 CHECK(station_multiplayer_configure(2,5,2,false));
 station_multiplayer_begin_launch();CHECK(!station_multiplayer_enable(true));
 CHECK(station_multiplayer_enable(false));CHECK(!station_multiplayer_configure(0,3,2,true));
 CHECK(!station_multiplayer_bind(13000,0));
 station_multiplayer_end_launch();station_multiplayer_begin_launch();
 CHECK(!station_multiplayer_enable(false));CHECK(!station_multiplayer_active());
}
static void binding(void)
{
 new_profile(0,15,4,true);
 CHECK(!station_multiplayer_bind(1023,1));CHECK(!station_multiplayer_bind(65536,1));
 CHECK(!station_multiplayer_bind(12000,0));CHECK(!station_multiplayer_bind(12000,4));
 CHECK(station_multiplayer_bind(12000,3));CHECK(!station_multiplayer_bind(12000,2));
 CHECK(!station_multiplayer_bind(12001,3));CHECK(!station_multiplayer_unbind(12000,2));
 CHECK(station_multiplayer_unbind(12000,3));CHECK(!station_multiplayer_unbind(12000,3));
 CHECK(station_multiplayer_bind(12002,3));CHECK(!station_multiplayer_claim(9999,21));
 CHECK(!station_multiplayer_claim(12002,-1));CHECK(station_multiplayer_claim(12002,21));
 CHECK(!station_multiplayer_claim(12002,22));CHECK(!station_multiplayer_unbind(12002,3));
 CHECK(station_multiplayer_bind(12003,1));CHECK(!station_multiplayer_claim(12003,21));
 CHECK(station_multiplayer_claim(12003,22));CHECK(station_multiplayer_bind(12004,2));
 CHECK(station_multiplayer_claim(12004,23));CHECK(station_multiplayer_fd_devices(21)==8);
 CHECK(station_multiplayer_fd_devices(22)==2);CHECK(station_multiplayer_fd_devices(23)==4);
 CHECK(station_multiplayer_fd_devices(24)==0);CHECK(station_multiplayer_fd_devices(-1)==1);
 CHECK(station_multiplayer_authorize_play(21,8,0,false));
 CHECK(!station_multiplayer_authorize_play(21,1,0,false));
 CHECK(!station_multiplayer_authorize_play(21,10,0,false));
 CHECK(!station_multiplayer_authorize_play(21,8,1,false));
 CHECK(!station_multiplayer_authorize_play(21,8,0,true));
 CHECK(!station_multiplayer_authorize_play(24,8,0,false));
 CHECK(station_multiplayer_authorize_play(-1,1,0,false));
 CHECK(!station_multiplayer_authorize_play(-1,2,0,false));
 new_profile(0,5,2,true);CHECK(!station_multiplayer_bind(14000,1));
 CHECK(station_multiplayer_bind(14000,2));
}
static void loopback(void)
{
 struct sockaddr_in *v4=(struct sockaddr_in*)&fake_peer;
 struct sockaddr_in6 *v6=(struct sockaddr_in6*)&fake_peer;
 new_profile(0,15,4,true);CHECK(station_multiplayer_bind(15000,2));
 memset(&fake_peer,0,sizeof(fake_peer));v4->sin_family=AF_INET;
 v4->sin_port=htons(15000);v4->sin_addr.s_addr=htonl(0x7f000002);
 CHECK(!station_multiplayer_accept_fd(30));
 v4->sin_addr.s_addr=htonl(0x7f000001);fake_peer_result=-1;
 CHECK(!station_multiplayer_accept_fd(30));fake_peer_result=0;
 v4->sin_port=htons(15001);CHECK(!station_multiplayer_accept_fd(30));
 v4->sin_port=htons(15000);CHECK(station_multiplayer_accept_fd(30));
 CHECK(station_multiplayer_fd_devices(30)==4);
 CHECK(station_multiplayer_bind(15002,3));memset(&fake_peer,0,sizeof(fake_peer));
 v6->sin6_family=AF_INET6;v6->sin6_port=htons(15002);
 ((unsigned char*)&v6->sin6_addr)[15]=1;CHECK(!station_multiplayer_accept_fd(31));
 {const unsigned char mapped[16]={0,0,0,0,0,0,0,0,0,0,0xff,0xff,127,0,0,1};memcpy(&v6->sin6_addr,mapped,16);}
 CHECK(station_multiplayer_accept_fd(31));CHECK(station_multiplayer_fd_devices(31)==8);
}
static void roster_and_pump(void)
{
 unsigned n,local,mask;
 for(mask=1;mask<32;mask++)for(local=0;local<5;local++)
 {
  uint32_t maps[32]={0};unsigned index=0;uint32_t connected=0;
  n=station_multiplayer_popcount(mask);if(n<2 || !(mask&(1U<<local)))continue;
  new_profile(local,mask,n,false);
  for(int slot=4;slot>=0;slot--)if(mask&(1U<<slot))
  {maps[index*2]=1U<<slot;connected|=1U<<(index*2);index++;}
  CHECK(station_multiplayer_roster_ready(false,1U<<local,connected,maps,32));
  CHECK(!station_multiplayer_roster_ready(true,1U<<local,connected,maps,32));
  CHECK(!station_multiplayer_roster_ready(false,0,connected,maps,32));
  CHECK(!station_multiplayer_roster_ready(false,1U<<local,connected&~1U,maps,32));
  CHECK(!station_multiplayer_roster_ready(false,1U<<local,connected,maps,1));
 }
 for(n=2;n<=5;n++)
 {
  netplay_t np={0};uint32_t maps[32]={0};unsigned i;
  new_profile(0,(1U<<n)-1,n,true);
  np.is_server=true;np.modus=1;np.self_mode=5;np.self_devices=1;np.client_devices[0]=1;
  np.connected_players=1;np.connections_size=5;networking_driver_st.data=&np;
  for(i=1;i<n;i++)
  {
   unsigned slot=n-i;unsigned index=i+1;int fd=40+i;
   CHECK(station_multiplayer_bind(16000+i,slot));CHECK(station_multiplayer_claim(16000+i,fd));
   CHECK(!station_netplay_recovery_poll());
   np.connections[index-1].flags=1;np.connections[index-1].mode=5;np.connections[index-1].fd=fd;
   np.client_devices[index]=1U<<slot;np.connected_players|=1U<<index;
  }
  flush_calls=0;CHECK(station_netplay_recovery_poll());CHECK(flush_calls==n-1);
  np.connections[1].send_packet_buffer.used=8;CHECK(!station_netplay_recovery_poll());
  np.connections[1].send_packet_buffer.used=0;np.connections[1].mode=3;
  CHECK(!station_netplay_recovery_poll());np.connections[1].mode=5;
  np.client_devices[2]=1;CHECK(!station_netplay_recovery_poll());np.client_devices[2]=1U<<(n-1);
  CHECK(station_netplay_recovery_poll());
  np.connections[1].fd=99;CHECK(!station_netplay_recovery_poll());np.connections[1].fd=41;
  np.self_mode=3;CHECK(!station_netplay_recovery_poll());np.self_mode=5;
  np.client_devices[31]=2;CHECK(!station_netplay_recovery_poll());np.client_devices[31]=0;
  sync_success=false;CHECK(!station_netplay_recovery_poll());CHECK((station_recovery_status()&4)!=0 || station_recovery_failed);
  sync_success=true;station_recovery_reset();station_recovery_configure(true);
  flush_success=false;CHECK(!station_netplay_recovery_poll());CHECK(station_recovery_failed);flush_success=true;
  (void)maps;
 }
 /* Legacy v2 has no profile/bindings and preserves its existing two-peer rule. */
 {netplay_t np={0};station_multiplayer_end_launch();station_recovery_reset();
  np.modus=1;np.is_server=true;np.connected_players=3;networking_driver_st.data=&np;
  CHECK(station_netplay_recovery_poll());np.connected_players=1;CHECK(!station_netplay_recovery_poll());
  np.is_server=false;np.self_mode=5;CHECK(station_netplay_recovery_poll());}
 /* Client must observe every other participant, not just its own MODE. */
 {netplay_t np={0};new_profile(3,15,4,false);np.modus=1;np.self_mode=5;np.self_devices=8;
  np.connections_size=1;np.connections[0].flags=1;np.connected_players=15;
  np.client_devices[0]=1;np.client_devices[1]=8;np.client_devices[2]=2;np.client_devices[3]=4;
  networking_driver_st.data=&np;CHECK(station_netplay_recovery_poll());np.connected_players=3;
  np.client_devices[2]=0;np.client_devices[3]=0;CHECK(!station_netplay_recovery_poll());}
}
static HANDLE poll_started,allow_confirmation;
static DWORD WINAPI stale_poll(LPVOID ignored)
{
 uint64_t token=station_recovery_token();(void)ignored;
 SetEvent(poll_started);WaitForSingleObject(allow_confirmation,INFINITE);
 station_recovery_confirm_token(token,true,true);return 0;
}
static void epoch(void)
{
 unsigned i;uint64_t token;
 for(i=0;i<64;i++)
 {
  HANDLE t;station_recovery_reset();station_recovery_configure(true);station_recovery_request(1,true,true);
  poll_started=CreateEvent(NULL,TRUE,FALSE,NULL);allow_confirmation=CreateEvent(NULL,TRUE,FALSE,NULL);
  CHECK(poll_started && allow_confirmation);t=CreateThread(NULL,0,stale_poll,NULL,0,NULL);CHECK(t!=NULL);
  CHECK(WaitForSingleObject(poll_started,2000)==WAIT_OBJECT_0);
  station_recovery_request(2,true,true);SetEvent(allow_confirmation);CHECK(WaitForSingleObject(t,2000)==WAIT_OBJECT_0);
  CHECK(station_recovery_status()==-1);token=station_recovery_token();station_recovery_confirm_token(token,true,true);
  CHECK(station_recovery_status()==19);CloseHandle(t);CloseHandle(poll_started);CloseHandle(allow_confirmation);
 }
 token=station_recovery_token();station_recovery_confirm_token(token,true,false);
 CHECK(station_recovery_status()==17);
 station_recovery_request(2,true,false);
 station_recovery_confirm_token(token,true,true);CHECK(station_recovery_status()==17);
 token=station_recovery_token();station_recovery_confirm_token(token,true,true);
 CHECK(station_recovery_status()==19);
 token=station_recovery_token();station_recovery_request(2,false,true);
 station_recovery_confirm_token(token,true,true);CHECK(station_recovery_status()==-1);
 token=station_recovery_token();station_recovery_confirm_token(token,true,true);CHECK(station_recovery_status()==-1);
 station_recovery_confirm_token(token,false,true);CHECK(station_recovery_status()==18);
 station_recovery_request(1,true,true);CHECK(station_recovery_status()==18);
}
int main(void)
{
 basic_profile();binding();loopback();roster_and_pump();epoch();
 printf("PASS native-multiplayer checks=%u\n",checks);return 0;
}
'''
if os.name!='nt':
    PREAMBLE=r'''
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(2);}}while(0)
'''
    NET_FIXTURE=NET_FIXTURE.replace('typedef int socklen_t;','').replace('struct sockaddr *peer,int *len','struct sockaddr *peer,socklen_t *len')
    start=TEST.index('static HANDLE poll_started');end=TEST.index('int main(void)',start)
    TEST=TEST[:start]+r'''
static pthread_barrier_t poll_started,allow_confirmation;
static void *stale_poll(void *ignored){
 uint64_t token=station_recovery_token();(void)ignored;
 pthread_barrier_wait(&poll_started);pthread_barrier_wait(&allow_confirmation);
 station_recovery_confirm_token(token,true,true);return NULL;
}
static void epoch(void){
 unsigned i;uint64_t token;
 for(i=0;i<64;i++){
  pthread_t worker;station_recovery_reset();station_recovery_configure(true);station_recovery_request(1,true,true);
  CHECK(!pthread_barrier_init(&poll_started,NULL,2));CHECK(!pthread_barrier_init(&allow_confirmation,NULL,2));
  CHECK(!pthread_create(&worker,NULL,stale_poll,NULL));pthread_barrier_wait(&poll_started);
  station_recovery_request(2,true,true);pthread_barrier_wait(&allow_confirmation);CHECK(!pthread_join(worker,NULL));
  CHECK(station_recovery_status()==-1);token=station_recovery_token();station_recovery_confirm_token(token,true,true);CHECK(station_recovery_status()==19);
  pthread_barrier_destroy(&poll_started);pthread_barrier_destroy(&allow_confirmation);
 }
 token=station_recovery_token();station_recovery_request(2,false,true);
 station_recovery_confirm_token(token,true,true);CHECK(station_recovery_status()==-1);
 token=station_recovery_token();station_recovery_confirm_token(token,false,true);CHECK(station_recovery_status()==18);
}
'''+TEST[end:]

TEST=TEST.replace('int main(void)',r'''
static void fifth_binding(void){
 new_profile(0,31,5,true);unsigned slot;
 for(slot=4;slot>=1;slot--){CHECK(station_multiplayer_bind(18000+slot,slot));CHECK(station_multiplayer_claim(18000+slot,100+slot));CHECK(station_multiplayer_fd_devices(100+slot)==(1U<<slot));}
 CHECK(!station_multiplayer_bind(19000,5));CHECK(!station_multiplayer_bind(19000,4));
 CHECK(station_multiplayer_authorize_play(104,16,0,false));CHECK(!station_multiplayer_authorize_play(104,8,0,false));
}
int main(void)
''').replace('basic_profile();binding();','basic_profile();binding();fifth_binding();')

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();assert out.is_absolute();out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'OVERLAY-MANIFEST.json').read_text('utf8'))
    for n,v in manifest['files'].items():assert sha((SOURCE/n).read_bytes())==v['afterSHA256']
    mp=(SOURCE/'frontend/drivers/station_multiplayer.h').read_text('utf8').replace('#include <pthread.h>','')
    recovery=(SOURCE/'frontend/drivers/station_recovery.h').read_text('utf8').replace('#include <pthread.h>','').replace('#include "station_multiplayer.h"','')
    frontend=(SOURCE/'network/netplay/netplay_frontend.c').read_text('utf8')
    names=['station_multiplayer_accept_fd','station_netplay_multiplayer_ready','station_netplay_recovery_poll']
    functions={n:function(frontend,n) for n in names}
    src=out/'native-multiplayer.c';exe=out/('native-multiplayer.exe' if os.name=='nt' else 'native-multiplayer')
    src.write_text(PREAMBLE+'\n'+mp+'\n'+recovery+'\n'+NET_FIXTURE+'\n'+'\n'.join(functions.values())+'\n'+TEST,'utf8')
    compiler=r'C:\Program Files\LLVM\bin\clang.exe' if os.name=='nt' else shutil.which('cc')
    cp=subprocess.run([compiler,'-std=c11','-D_GNU_SOURCE','-Werror','-Wno-unused-function',str(src),*(['-lws2_32'] if os.name=='nt' else ['-pthread']),'-o',str(exe)],capture_output=True,text=True)
    (out/'compile.log').write_text(cp.stdout+cp.stderr,'utf8');assert cp.returncode==0,cp.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=30)
    (out/'run.log').write_text(run.stdout+run.stderr,'utf8');assert run.returncode==0,(run.stdout,run.stderr)
    native=(SOURCE/'frontend/drivers/platform_unix.c').read_text('utf8')
    guards=[]
    def guard(label,ok):assert ok,label;guards.append(label)
    guard('typed v3 protocol', '"station-stream.v3"' in native and '"station-stream.v2"' in native)
    guard('configuration consumed before native thread',native.index('station_multiplayer_begin_launch();')<native.index('activity->instance = android_app_create'))
    release=function(native,'station_activity_release');guard('mapping cleared at final release','station_multiplayer_end_launch();' in release)
    guard('onStop preserves TCP mappings','station_multiplayer_end_launch' not in function(native,'onStop'))
    guard('PLAY validates actual fd','station_multiplayer_authorize_play(connection?connection->fd:-1,' in frontend)
    guard('v3 accepts only registered local peer','station_multiplayer_active() && !station_multiplayer_accept_fd(new_fd)' in frontend)
    accept=function(frontend,'netplay_sync_pre_frame')
    claim=accept.index('station_multiplayer_accept_fd(new_fd)')
    guard('slot claim follows all socket allocations',claim>accept.index('!netplay_init_socket_buffer(\n                  &connection->recv_packet_buffer'))
    guard('slot claim precedes native activation',claim<accept.index('connection->flags |= NETPLAY_CONN_FLAG_ACTIVE;'))
    guard('v3 allocation failures report native failure',accept.count('if(station_multiplayer_active())station_recovery_fail();')==2)
    rejection=accept[claim:accept.index('/* Set it up */',claim)]
    guard('rejected slot releases both buffers','netplay_deinit_socket_buffer(&connection->send_packet_buffer)' in rejection and 'netplay_deinit_socket_buffer(&connection->recv_packet_buffer)' in rejection)
    guard('native poll never executes core','retro_run(' not in functions['station_netplay_recovery_poll'])
    guard('legacy predicate unchanged','(np->is_server?np->connected_players>1:np->self_mode==NETPLAY_CONNECTION_PLAYING)' in frontend)
    report={'scope':__doc__,'passed':True,'stdout':run.stdout.strip(),'sourceManifestSHA256':sha((ROOT/'OVERLAY-MANIFEST.json').read_bytes()),'sourceSHA256':sha(src.read_bytes()),'extractedFunctions':{n:sha(v.encode()) for n,v in functions.items()},'guards':guards,'androidExecuted':False,'gameplayTested':False,'TLSNetworkTested':False,'realHostMutexThreads':True}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    (ROOT/'tests/native-result.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
