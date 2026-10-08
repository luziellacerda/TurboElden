"""Create the reviewed R77 C overlay from the exact R74 sources (no build)."""
from pathlib import Path
import hashlib,json,difflib
ROOT=Path(__file__).resolve().parent
BASE=Path(r'E:\R74fixed\RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576')
RUNTIME='804b2acfea4c6d615bf40dba30e1777015098bf7375d0745db8d117555eb2516'
def sha(b):return hashlib.sha256(b).hexdigest()
def change(s,old,new):
    assert s.count(old)==1,(old[:90],s.count(old))
    return s.replace(old,new)
files={};diff=[]
def emit(name,old,new):
    path=ROOT/'source'/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(new,encoding='utf8',newline='\n')
    files[name]={'beforeSHA256':sha(old.encode()) if old is not None else None,'afterSHA256':sha(new.encode())}
    diff.extend(difflib.unified_diff((old or '').splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
name='frontend/drivers/station_multiplayer.h'
emit(name,None,(ROOT/'source'/name).read_text('utf8'))

name='frontend/drivers/station_recovery.h';old=(BASE/name).read_text('utf8');s=old
s=change(s,'#include <pthread.h>','#include <pthread.h>\n#include "station_multiplayer.h"')
s=change(s,'static int64_t station_recovery_epoch, station_recovery_confirmed_epoch;',
'''static int64_t station_recovery_epoch, station_recovery_confirmed_epoch;
static uint64_t station_recovery_revision;''')
s=change(s,'   station_recovery_confirmed_epoch = -1;','   station_recovery_confirmed_epoch = -1;\n   station_recovery_revision = 0;')
s=change(s,'''      if(epoch!=station_recovery_epoch || wait!=station_recovery_wait)
         station_recovery_confirmed_epoch=-1;''','''      if(epoch!=station_recovery_epoch || wait!=station_recovery_wait)
         station_recovery_confirmed_epoch=-1;
      if(epoch!=station_recovery_epoch || wait!=station_recovery_wait || visible!=station_recovery_visible)
         station_recovery_revision++;''')
s=change(s,'static void station_recovery_fail(void)', '''/* v3 confirmation is tied to the request observed before polling. An epoch or
 * visibility change during the poll cannot be acknowledged by stale work. */
static uint64_t station_recovery_token(void)
{
   uint64_t token;pthread_mutex_lock(&station_recovery_mutex);
   token=station_recovery_revision;pthread_mutex_unlock(&station_recovery_mutex);
   return token;
}
static void station_recovery_confirm_token(uint64_t token,bool wait,bool connected)
{
   pthread_mutex_lock(&station_recovery_mutex);
   if(token==station_recovery_revision && wait==station_recovery_wait)
   {
      station_recovery_confirmed_epoch=station_recovery_epoch;
      station_recovery_confirmed_wait=wait;station_recovery_connected=connected;
   }
   pthread_mutex_unlock(&station_recovery_mutex);
}
static void station_recovery_fail(void)''')
emit(name,old,s)

name='frontend/drivers/platform_unix.c';old=(BASE/name).read_text('utf8');s=old
s=change(s,'''      station_activity_owner = NULL;
      station_activity_app = NULL;''','''      station_activity_owner = NULL;
      station_activity_app = NULL;
      station_multiplayer_end_launch();''')
s=change(s,'''   station_recovery_reset();
   activity->instance = android_app_create''','''   station_recovery_reset();
   station_multiplayer_begin_launch();
   activity->instance = android_app_create''')
s=change(s,'/* Instance method; Java calls this on its UI thread after a human exit. */', '''/* Configure is staged before NativeActivity.onCreate and consumed once there.
 * All methods return false without mutating the running profile on rejection. */
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationMultiplayerConfigure(JNIEnv *env,jclass type,jint slot,jint devices,jint count,jboolean host)
{
   bool accepted=false;(void)env;(void)type;
   pthread_mutex_lock(&station_activity_mutex);
   if(!station_activity_owner)
      accepted=station_multiplayer_configure((unsigned)slot,(uint32_t)devices,(unsigned)count,host==JNI_TRUE);
   pthread_mutex_unlock(&station_activity_mutex);
   return accepted?JNI_TRUE:JNI_FALSE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationMultiplayerBind(JNIEnv *env,jclass type,jint port,jint slot)
{ (void)env;(void)type;return station_multiplayer_bind((unsigned)port,(unsigned)slot)?JNI_TRUE:JNI_FALSE; }
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationMultiplayerUnbind(JNIEnv *env,jclass type,jint port,jint slot)
{ (void)env;(void)type;return station_multiplayer_unbind((unsigned)port,(unsigned)slot)?JNI_TRUE:JNI_FALSE; }
/* Instance method; Java calls this on its UI thread after a human exit. */''')
s=change(s,'''         station_recovery_configure(args->station_netplay_role!=0 && value && !strcmp(value,"station-stream.v2"));''','''         bool multiplayer=value && !strcmp(value,"station-stream.v3");
         station_recovery_configure(multiplayer || (args->station_netplay_role!=0 && value && !strcmp(value,"station-stream.v2")));
         if(multiplayer && (args->station_netplay_role==0 ||
               !station_multiplayer_enable(args->station_netplay_role==1)))
            station_recovery_fail();''')
emit(name,old,s)

name='network/netplay/netplay_frontend.c';old=(BASE/name).read_text('utf8');s=old
# The accepted TCP source port is local bookkeeping, never a new wire field.
s=change(s,'static struct netplay_connection *allocate_connection(netplay_t *netplay)', '''#ifdef ANDROID
static bool station_multiplayer_accept_fd(int fd)
{
   struct sockaddr_storage peer;socklen_t length=sizeof(peer);unsigned port=0;
   if(getpeername(fd,(struct sockaddr*)&peer,&length)!=0)return false;
   if(peer.ss_family==AF_INET)
   {
      struct sockaddr_in *v4=(struct sockaddr_in*)&peer;
      if(ntohl(v4->sin_addr.s_addr)!=UINT32_C(0x7f000001))return false;
      port=ntohs(v4->sin_port);
   }
#ifdef HAVE_INET6
   else if(peer.ss_family==AF_INET6)
   {
      static const unsigned char loopback[16]={0,0,0,0,0,0,0,0,0,0,0xff,0xff,127,0,0,1};
      struct sockaddr_in6 *v6=(struct sockaddr_in6*)&peer;
      if(memcmp(&v6->sin6_addr,loopback,sizeof(loopback))!=0)return false;
      port=ntohs(v6->sin6_port);
   }
#endif
   return port && station_multiplayer_claim(port,fd);
}
#endif
static struct netplay_connection *allocate_connection(netplay_t *netplay)''')
s=change(s,'''         if (!connection)
         {
            socket_close(new_fd);
            goto process;
         }

         if (    !netplay_init_socket_buffer(''','''         if (!connection)
         {
#ifdef ANDROID
            if(station_multiplayer_active())station_recovery_fail();
#endif
            socket_close(new_fd);
            goto process;
         }

         if (    !netplay_init_socket_buffer(''')
s=change(s,'''            netplay_deinit_socket_buffer(&connection->recv_packet_buffer);
            socket_close(new_fd);
            goto process;
         }

         /* Set it up */''','''            netplay_deinit_socket_buffer(&connection->recv_packet_buffer);
#ifdef ANDROID
            if(station_multiplayer_active())station_recovery_fail();
#endif
            socket_close(new_fd);
            goto process;
         }

#ifdef ANDROID
         /* Claim only after all fallible allocation succeeds. A rejected fd
          * never becomes active, and a failed allocation consumes no slot. */
         if(station_multiplayer_active() && !station_multiplayer_accept_fd(new_fd))
         {
            netplay_deinit_socket_buffer(&connection->send_packet_buffer);
            netplay_deinit_socket_buffer(&connection->recv_packet_buffer);
            socket_close(new_fd);
            goto process;
         }
#endif
         /* Set it up */''')
s=change(s,'''            share_mode = (mode >> 16) & 0xFF;

            /* Fix our share mode */''','''            share_mode = (mode >> 16) & 0xFF;
#ifdef ANDROID
            if(station_multiplayer_active() &&
                  !station_multiplayer_authorize_play(connection?connection->fd:-1,
                     devices,share_mode,(mode&NETPLAY_CMD_PLAY_BIT_SLAVE)!=0))
            {
               if(connection)
               {
                  uint32_t reason=htonl(NETPLAY_CMD_MODE_REFUSED_REASON_NOT_AVAILABLE);
                  netplay_send_raw_cmd(netplay,connection,NETPLAY_CMD_MODE_REFUSED,&reason,sizeof(reason));
                  netplay_hangup(netplay,connection);
               }
               else station_recovery_fail();
               return;
            }
#endif

            /* Fix our share mode */''')
s=change(s,'''#ifdef ANDROID
bool station_netplay_recovery_poll(void)''','''#ifdef ANDROID
static bool station_netplay_multiplayer_ready(netplay_t *np)
{
   size_t i;uint32_t active_players=UINT32_C(1);
   if(np->self_mode!=NETPLAY_CONNECTION_PLAYING ||
         !station_multiplayer_roster_ready(np->is_server,np->self_devices,
            np->connected_players,np->client_devices,MAX_CLIENTS))return false;
   if(!np->is_server)
      return np->connections_size==1 &&
         (np->connections[0].flags&NETPLAY_CONN_FLAG_ACTIVE)!=0;
   for(i=0;i<np->connections_size;i++)
   {
      struct netplay_connection *connection=&np->connections[i];
      if(!(connection->flags&NETPLAY_CONN_FLAG_ACTIVE))continue;
      if(i+1>=MAX_CLIENTS || connection->mode!=NETPLAY_CONNECTION_PLAYING ||
            np->client_devices[i+1]!=station_multiplayer_fd_devices(connection->fd))return false;
      active_players|=UINT32_C(1)<<(i+1);
   }
   return active_players==np->connected_players;
}
bool station_netplay_recovery_poll(void)''')
s=change(s,'''   return np->modus==NETPLAY_MODUS_INPUT_FRAME_SYNC &&
      (np->is_server?np->connected_players>1:np->self_mode==NETPLAY_CONNECTION_PLAYING);''','''   if(station_multiplayer_active())
      return np->modus==NETPLAY_MODUS_INPUT_FRAME_SYNC && station_netplay_multiplayer_ready(np);
   return np->modus==NETPLAY_MODUS_INPUT_FRAME_SYNC &&
      (np->is_server?np->connected_players>1:np->self_mode==NETPLAY_CONNECTION_PLAYING);''')
emit(name,old,s)

name='runloop.c';old=(BASE/name).read_text('utf8');s=old
s=change(s,'''      bool connected=station_netplay_recovery_poll();
      station_recovery_confirm(true,connected);''','''      uint64_t token=station_recovery_token();
      bool connected=station_netplay_recovery_poll();
      if(station_multiplayer_active())station_recovery_confirm_token(token,true,connected);
      else station_recovery_confirm(true,connected);''')
s=change(s,'''   if(station_recovery_active())station_recovery_confirm(false,true);''','''   if(station_recovery_active())
   {
      if(station_multiplayer_active())
      {
         uint64_t token=station_recovery_token();
         station_recovery_confirm_token(token,false,true);
      }
      else station_recovery_confirm(false,true);
   }''')
emit(name,old,s)
(ROOT/'station-multiplayer-r77.patch').write_text(''.join(diff),encoding='utf8',newline='\n')
(ROOT/'OVERLAY-MANIFEST.json').write_text(json.dumps({'baseRuntimeSHA256':RUNTIME,'upstreamCommit':'69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576','files':files,'protocols':['station-stream.v2','station-stream.v3'],'jniMethods':['stationRecoveryControl','stationRecoveryStatus','stationRecoveryStalled','stationRequestQuit','stationMultiplayerConfigure','stationMultiplayerBind','stationMultiplayerUnbind']},indent=2)+'\n','utf8')
print(json.dumps(files,indent=2))
