#ifndef STATION_MULTIPLAYER_H
#define STATION_MULTIPLAYER_H
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>

#define STATION_MULTIPLAYER_MAX_PLAYERS 5U
#define STATION_MULTIPLAYER_MAX_GUESTS (STATION_MULTIPLAYER_MAX_PLAYERS-1U)
#define STATION_MULTIPLAYER_DEVICE_MASK UINT32_C(31)

/* Station v3 only. Slots are zero-based controller ports, not RetroArch client
 * numbers or accept order. The signed Java launch selects the immutable roster. */
struct station_multiplayer_binding
{
   unsigned port, slot;
   int fd;
   bool used, claimed;
};
struct station_multiplayer_profile
{
   bool configured, host;
   unsigned local_slot, count;
   uint32_t devices;
};
static pthread_mutex_t station_multiplayer_mutex = PTHREAD_MUTEX_INITIALIZER;
static struct station_multiplayer_profile station_multiplayer_pending;
static struct station_multiplayer_profile station_multiplayer_profile;
static struct station_multiplayer_binding station_multiplayer_bindings[STATION_MULTIPLAYER_MAX_GUESTS];
static bool station_multiplayer_launched, station_multiplayer_enabled;

static unsigned station_multiplayer_popcount(uint32_t value)
{
   unsigned result=0;
   while(value){result+=value&1U;value>>=1;}
   return result;
}
static bool station_multiplayer_configure(unsigned local_slot, uint32_t devices,
      unsigned count, bool host)
{
   bool accepted=false;
   if(local_slot>=STATION_MULTIPLAYER_MAX_PLAYERS || !devices || (devices&~STATION_MULTIPLAYER_DEVICE_MASK) ||
      count<2 || count>STATION_MULTIPLAYER_MAX_PLAYERS || station_multiplayer_popcount(devices)!=count ||
      !(devices&(UINT32_C(1)<<local_slot)))return false;
   pthread_mutex_lock(&station_multiplayer_mutex);
   if(!station_multiplayer_launched)
   {
      station_multiplayer_pending.configured=true;
      station_multiplayer_pending.local_slot=local_slot;
      station_multiplayer_pending.devices=devices;
      station_multiplayer_pending.count=count;
      station_multiplayer_pending.host=host;
      accepted=true;
   }
   pthread_mutex_unlock(&station_multiplayer_mutex);
   return accepted;
}
/* Consume staged configuration once; reconnection never invokes this. */
static void station_multiplayer_begin_launch(void)
{
   pthread_mutex_lock(&station_multiplayer_mutex);
   station_multiplayer_profile=station_multiplayer_pending;
   memset(&station_multiplayer_pending,0,sizeof(station_multiplayer_pending));
   memset(station_multiplayer_bindings,0,sizeof(station_multiplayer_bindings));
   station_multiplayer_launched=true;station_multiplayer_enabled=false;
   pthread_mutex_unlock(&station_multiplayer_mutex);
}
static void station_multiplayer_end_launch(void)
{
   pthread_mutex_lock(&station_multiplayer_mutex);
   memset(&station_multiplayer_pending,0,sizeof(station_multiplayer_pending));
   memset(&station_multiplayer_profile,0,sizeof(station_multiplayer_profile));
   memset(station_multiplayer_bindings,0,sizeof(station_multiplayer_bindings));
   station_multiplayer_launched=false;station_multiplayer_enabled=false;
   pthread_mutex_unlock(&station_multiplayer_mutex);
}
static bool station_multiplayer_enable(bool host)
{
   bool accepted;
   pthread_mutex_lock(&station_multiplayer_mutex);
   accepted=station_multiplayer_launched && station_multiplayer_profile.configured &&
      station_multiplayer_profile.host==host;
   station_multiplayer_enabled=accepted;
   pthread_mutex_unlock(&station_multiplayer_mutex);
   return accepted;
}
static bool station_multiplayer_active(void)
{
   bool value;pthread_mutex_lock(&station_multiplayer_mutex);
   value=station_multiplayer_enabled;pthread_mutex_unlock(&station_multiplayer_mutex);
   return value;
}
/* Register the socket's already-bound ephemeral source port before connect().
 * This does not trust a nickname, PLAY request or connection arrival order. */
static bool station_multiplayer_bind(unsigned port,unsigned remote_slot)
{
   unsigned i,free_index=STATION_MULTIPLAYER_MAX_GUESTS;bool accepted=false;
   if(port<1024 || port>65535 || remote_slot>=STATION_MULTIPLAYER_MAX_PLAYERS)return false;
   pthread_mutex_lock(&station_multiplayer_mutex);
   if(!station_multiplayer_launched || !station_multiplayer_profile.configured ||
      !station_multiplayer_profile.host || remote_slot==station_multiplayer_profile.local_slot ||
      !(station_multiplayer_profile.devices&(UINT32_C(1)<<remote_slot)))goto done;
   for(i=0;i<STATION_MULTIPLAYER_MAX_GUESTS;i++)
   {
      struct station_multiplayer_binding *b=&station_multiplayer_bindings[i];
      if(!b->used){if(free_index==STATION_MULTIPLAYER_MAX_GUESTS)free_index=i;continue;}
      if(b->port==port || b->slot==remote_slot)goto done;
   }
   if(free_index<STATION_MULTIPLAYER_MAX_GUESTS)
   {
      struct station_multiplayer_binding *b=&station_multiplayer_bindings[free_index];
      b->used=true;b->claimed=false;b->port=port;b->slot=remote_slot;b->fd=-1;
      accepted=true;
   }
done:
   pthread_mutex_unlock(&station_multiplayer_mutex);return accepted;
}
/* Only an unaccepted connect attempt can release its registration. The native
 * TCP socket and its assignment survive every WSS replacement/room epoch. */
static bool station_multiplayer_unbind(unsigned port,unsigned remote_slot)
{
   unsigned i;bool accepted=false;
   pthread_mutex_lock(&station_multiplayer_mutex);
   for(i=0;i<STATION_MULTIPLAYER_MAX_GUESTS;i++)
   {
      struct station_multiplayer_binding *b=&station_multiplayer_bindings[i];
      if(b->used && !b->claimed && b->port==port && b->slot==remote_slot)
      {memset(b,0,sizeof(*b));accepted=true;break;}
   }
   pthread_mutex_unlock(&station_multiplayer_mutex);return accepted;
}
static bool station_multiplayer_claim(unsigned port,int fd)
{
   unsigned i;bool accepted=false;
   if(fd<0)return false;
   pthread_mutex_lock(&station_multiplayer_mutex);
   if(!station_multiplayer_enabled || !station_multiplayer_profile.host)goto done;
   for(i=0;i<STATION_MULTIPLAYER_MAX_GUESTS;i++)if(station_multiplayer_bindings[i].claimed && station_multiplayer_bindings[i].fd==fd)goto done;
   for(i=0;i<STATION_MULTIPLAYER_MAX_GUESTS;i++)
   {
      struct station_multiplayer_binding *b=&station_multiplayer_bindings[i];
      if(b->used && !b->claimed && b->port==port)
      {b->claimed=true;b->fd=fd;accepted=true;break;}
   }
done:
   pthread_mutex_unlock(&station_multiplayer_mutex);return accepted;
}
static uint32_t station_multiplayer_fd_devices(int fd)
{
   unsigned i;uint32_t result=0;
   pthread_mutex_lock(&station_multiplayer_mutex);
   if(station_multiplayer_enabled)
   {
      if(fd<0)result=UINT32_C(1)<<station_multiplayer_profile.local_slot;
      else for(i=0;i<STATION_MULTIPLAYER_MAX_GUESTS;i++)
      {
         struct station_multiplayer_binding *b=&station_multiplayer_bindings[i];
         if(b->used && b->claimed && b->fd==fd){result=UINT32_C(1)<<b->slot;break;}
      }
   }
   pthread_mutex_unlock(&station_multiplayer_mutex);return result;
}
static bool station_multiplayer_authorize_play(int fd,uint32_t devices,
      unsigned share_mode,bool slave)
{
   uint32_t expected=station_multiplayer_fd_devices(fd);
   return expected && devices==expected && !share_mode && !slave;
}
/* The caller gathers this snapshot on the emulation thread. connected_players
 * is a client BITMAP; controller ownership is client_devices[client]. */
static bool station_multiplayer_roster_ready(bool host,uint32_t self_devices,
      uint32_t connected_players,const uint32_t *client_devices,unsigned length)
{
   struct station_multiplayer_profile p;uint32_t union_devices=0;unsigned i,seen=0;
   pthread_mutex_lock(&station_multiplayer_mutex);
   p=station_multiplayer_profile;
   if(!station_multiplayer_enabled)p.configured=false;
   pthread_mutex_unlock(&station_multiplayer_mutex);
   if(!p.configured || p.host!=host || length>32 || !client_devices ||
      self_devices!=(UINT32_C(1)<<p.local_slot) ||
      station_multiplayer_popcount(connected_players)!=p.count)return false;
   for(i=0;i<length;i++)
   {
      uint32_t devices=client_devices[i];
      if(!(connected_players&(UINT32_C(1)<<i)))
      {if(devices)return false;continue;}
      if(!devices || (devices&(devices-1)) || (devices&~p.devices) || (devices&union_devices))return false;
      union_devices|=devices;seen++;
   }
   return seen==p.count && union_devices==p.devices;
}
#endif
