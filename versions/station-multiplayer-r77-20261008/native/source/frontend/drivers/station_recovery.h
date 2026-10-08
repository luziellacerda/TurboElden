#ifndef STATION_RECOVERY_H
#define STATION_RECOVERY_H
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include "station_multiplayer.h"

/* Android Station-only state. JNI requests; only the emulation thread confirms.
 * This header is compiled in RetroArch's Android griffin translation unit. */
static pthread_mutex_t station_recovery_mutex = PTHREAD_MUTEX_INITIALIZER;
static bool station_recovery_enabled, station_recovery_wait=true;
static bool station_recovery_visible=true, station_recovery_confirmed_wait;
static bool station_recovery_connected, station_recovery_failed;
static bool station_recovery_stalled;
static int64_t station_recovery_epoch, station_recovery_confirmed_epoch;
static uint64_t station_recovery_revision;
/* Only at NativeActivity creation, never on a transport epoch/reconnect. */
static void station_recovery_reset(void)
{
   pthread_mutex_lock(&station_recovery_mutex);
   station_recovery_enabled = false;
   station_recovery_wait = true;
   station_recovery_visible = true;
   station_recovery_confirmed_wait = false;
   station_recovery_connected = false;
   station_recovery_failed = false;
   station_recovery_stalled = false;
   station_recovery_epoch = 0;
   station_recovery_confirmed_epoch = -1;
   station_recovery_revision = 0;
   pthread_mutex_unlock(&station_recovery_mutex);
}
static void station_recovery_configure(bool enabled)
{
   pthread_mutex_lock(&station_recovery_mutex);
   station_recovery_enabled=enabled;
   pthread_mutex_unlock(&station_recovery_mutex);
}
static bool station_recovery_active(void)
{
   bool result; pthread_mutex_lock(&station_recovery_mutex);
   result=station_recovery_enabled; pthread_mutex_unlock(&station_recovery_mutex);
   return result;
}
static void station_recovery_request(int64_t epoch, bool wait, bool visible)
{
   pthread_mutex_lock(&station_recovery_mutex);
   if(epoch>=station_recovery_epoch && epoch<(INT64_MAX>>3))
   {
      if(epoch!=station_recovery_epoch || wait!=station_recovery_wait)
         station_recovery_confirmed_epoch=-1;
      if(epoch!=station_recovery_epoch || wait!=station_recovery_wait || visible!=station_recovery_visible)
         station_recovery_revision++;
      station_recovery_epoch=epoch; station_recovery_wait=wait;
      if(wait)station_recovery_stalled=false;
      station_recovery_visible=visible;
   }
   pthread_mutex_unlock(&station_recovery_mutex);
}
static bool station_recovery_waiting(void)
{
   bool result; pthread_mutex_lock(&station_recovery_mutex);
   result=station_recovery_enabled && (station_recovery_wait || station_recovery_failed);
   pthread_mutex_unlock(&station_recovery_mutex); return result;
}
static void station_recovery_confirm(bool wait, bool connected)
{
   pthread_mutex_lock(&station_recovery_mutex);
   station_recovery_confirmed_epoch=station_recovery_epoch;
   station_recovery_confirmed_wait=wait; station_recovery_connected=connected;
   pthread_mutex_unlock(&station_recovery_mutex);
}
/* v3 confirmation is tied to the request observed before polling. An epoch or
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
static void station_recovery_fail(void)
{
   pthread_mutex_lock(&station_recovery_mutex);station_recovery_failed=true;
   pthread_mutex_unlock(&station_recovery_mutex);
}
static void station_recovery_mark_stalled(void)
{
   pthread_mutex_lock(&station_recovery_mutex);station_recovery_stalled=true;
   pthread_mutex_unlock(&station_recovery_mutex);
}
static bool station_recovery_is_stalled(void)
{
   bool result;pthread_mutex_lock(&station_recovery_mutex);result=station_recovery_stalled;
   pthread_mutex_unlock(&station_recovery_mutex);return result;
}
static int64_t station_recovery_status(void)
{
   int64_t result;pthread_mutex_lock(&station_recovery_mutex);
   result=station_recovery_confirmed_epoch<0?-1:
      (station_recovery_confirmed_epoch<<3) |
      (station_recovery_confirmed_wait?1:0) | (station_recovery_connected?2:0) |
      (station_recovery_failed?4:0);
   pthread_mutex_unlock(&station_recovery_mutex);return result;
}
/* Defined by netplay_frontend.c: receives/flushes protocol while retro_run is stopped. */
bool station_netplay_recovery_poll(void);
#endif
