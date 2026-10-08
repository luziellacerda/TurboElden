"""Produce a minimal lifecycle delta; the frozen R73 tree is read-only."""
from pathlib import Path
import difflib
import hashlib
import json

BASE = Path(r'E:\R73fixed\RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576')
OUT = Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def once(text, old, new):
    assert text.count(old) == 1, old[:120]
    return text.replace(old, new)

files = ['frontend/drivers/platform_unix.c', 'frontend/drivers/platform_unix.h',
         'frontend/drivers/station_recovery.h', 'input/drivers/android_input.c', 'runloop.c',
         'network/netplay/netplay_frontend.c']
original = {name: (BASE/name).read_text(encoding='utf8') for name in files}
changed = dict(original)
p = changed[files[0]]
p = once(p, '#ifdef ANDROID\nstatic void frontend_unix_set_sustained_performance_mode',
         '#ifdef ANDROID\n#include "station_recovery.h"\nstatic void frontend_unix_set_sustained_performance_mode')
p = once(p, 'struct android_app *g_android            = NULL;',
         '''struct android_app *g_android            = NULL;
/* Reserve one native core before reset/thread creation; release after join. */
static pthread_mutex_t station_activity_mutex = PTHREAD_MUTEX_INITIALIZER;
static ANativeActivity *station_activity_owner = NULL;
static struct android_app *station_activity_app = NULL;
static bool station_activity_reserve(ANativeActivity *activity)
{
   bool accepted;
   pthread_mutex_lock(&station_activity_mutex);
   accepted = station_activity_owner == NULL;
   if (accepted)
      station_activity_owner = activity;
   pthread_mutex_unlock(&station_activity_mutex);
   return accepted;
}
static void station_activity_release(ANativeActivity *activity)
{
   pthread_mutex_lock(&station_activity_mutex);
   if (station_activity_owner == activity)
   {
      station_activity_owner = NULL;
      station_activity_app = NULL;
   }
   pthread_mutex_unlock(&station_activity_mutex);
}''')
p = once(p, '#include "station_recovery.h"\nJNIEXPORT', 'JNIEXPORT')
p = once(p, 'static void android_app_free(struct android_app* android_app)\n{\n   slock_lock(android_app->mutex);\n\n   sthread_join(android_app->thread);\n\n   slock_unlock(android_app->mutex);',
'''/* Explicit Activity exit only. Transport pause/reconnect never calls this. */
static bool android_app_request_quit(struct android_app *android_app)
{
   bool accepted;
   if (!android_app)
      return false;
   slock_lock(android_app->mutex);
   accepted = !android_app->destroyed;
   if (accepted)
   {
      /* A wake has no pipe-buffer backpressure and also reaches the initial
       * window wait. Only the emulation thread mutates runloop shutdown. */
      __atomic_store_n(&android_app->stationQuitRequested, 1, __ATOMIC_RELEASE);
      if (android_app->looper)
         ALooper_wake(android_app->looper);
   }
   slock_unlock(android_app->mutex);
   return accepted;
}

static void android_app_free(struct android_app* android_app)
{
   if (!android_app)
      return;
   android_app_request_quit(android_app);
   slock_lock(android_app->mutex);
   /* cond_wait releases the lock needed by android_app_destroy. */
   while (!android_app->destroyed)
      scond_wait(android_app->cond, android_app->mutex);
   slock_unlock(android_app->mutex);

   /* Never join while holding the worker's finalization mutex. */
   sthread_join(android_app->thread);
   if (g_android == android_app)
      g_android = NULL;''')
p = once(p, '''static void onDestroy(ANativeActivity* activity)
{
   android_app_free((struct android_app*)activity->instance);
}''', '''static void onDestroy(ANativeActivity* activity)
{
   pthread_mutex_lock(&station_activity_mutex);
   if (station_activity_owner == activity)
      station_activity_app = NULL;
   pthread_mutex_unlock(&station_activity_mutex);
   android_app_free((struct android_app*)activity->instance);
   activity->instance = NULL;
   station_activity_release(activity);
}''')
# Both legacy external shell hooks are absent from the Station online runtime.
p = once(p, r'   int result = system("sh -c \"sh /sdcard/switch\"");'+'\n', '')
p = once(p, r'   int result  = system("sh -c \"sh /sdcard/reset\"");'+'\n', '')
p = once(p, '''   /* These are set only for the native activity,
    * and are reset when it ends. */''', '''   if (!station_activity_reserve(activity))
   {
      jclass error = (*activity->env)->FindClass(activity->env,
            "java/lang/IllegalStateException");
      if (error)
      {
         (*activity->env)->ThrowNew(activity->env, error,
               "A Station native game is already active in this process");
         (*activity->env)->DeleteLocalRef(activity->env, error);
      }
      return;
   }

   /* These are set only for the native activity,
    * and are reset when it ends. */''')
p = once(p, '''      activity->instance;

   slock_lock(android_app->mutex);''', '''      activity->instance;

   if (!android_app)
   {
      *outLen = 0;
      return NULL;
   }
   slock_lock(android_app->mutex);''')
p = once(p, '   instance->content_rect.changed = true;', '''   if (!instance)
      return;
   instance->content_rect.changed = true;''')
for condition in ('android_app->inputQueue != android_app->pendingInputQueue',
                  'android_app->window != android_app->pendingWindow',
                  'android_app->activityState != cmd', '!android_app->stateSaved'):
    p = once(p, 'while ('+condition+')', 'while ('+condition+' && !android_app->destroyed)')
# Do not append more commands after the emulation thread finished.
for anchor in ('   android_app->pendingInputQueue = inputQueue;',
               '   if (android_app->pendingWindow)',
               '   android_app_write_cmd(android_app, cmd);',
               '   android_app->stateSaved = 0;'):
    guard = '''   if (android_app->destroyed)
   {
      slock_unlock(android_app->mutex);
      return%s;
   }
''' % (' NULL' if 'stateSaved' in anchor else '')
    p = once(p, anchor, guard + anchor)
p = once(p, '''   activity->instance = android_app_create(activity,
         savedState, savedStateSize);''', '''   /* Reset before the worker/Java transport can receive the new epoch.
    * configure() below changes only enabled: reconnect must never reset it. */
   station_recovery_reset();
   activity->instance = android_app_create(activity,
         savedState, savedStateSize);
   pthread_mutex_lock(&station_activity_mutex);
   station_activity_app = (struct android_app*)activity->instance;
   pthread_mutex_unlock(&station_activity_mutex);
   if (!activity->instance)
      station_activity_release(activity);''')
p = once(p, '''JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRecoveryStalled(JNIEnv *env,jclass type)
{ (void)env;(void)type;return station_recovery_is_stalled(); }''', '''JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRecoveryStalled(JNIEnv *env,jclass type)
{ (void)env;(void)type;return station_recovery_is_stalled(); }
/* Instance method; Java calls this on its UI thread after a human exit. */
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit(JNIEnv *env,jobject activity)
{
   jboolean accepted = JNI_FALSE;
   struct android_app *app;
   pthread_mutex_lock(&station_activity_mutex);
   app = station_activity_app;
   if (app && app->activity &&
       (*env)->IsSameObject(env, activity, app->activity->clazz))
      accepted = android_app_request_quit(app) ? JNI_TRUE : JNI_FALSE;
   pthread_mutex_unlock(&station_activity_mutex);
   return accepted;
}''')
changed[files[0]] = p
h = changed[files[1]]
h = once(h, '   int destroyed;','''   int destroyed;
   /* Cross-thread explicit exit; use acquire/release atomic access only. */
   int stationQuitRequested;''')
changed[files[1]] = h
h = changed[files[2]]
h = once(h, 'static void station_recovery_configure(bool enabled)', '''/* Only at NativeActivity creation, never on a transport epoch/reconnect. */
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
   pthread_mutex_unlock(&station_recovery_mutex);
}
static void station_recovery_configure(bool enabled)''')
changed[files[2]] = h
p = changed[files[3]]
p = once(p, '''   settings_t            *settings = config_get_ptr();

   while ((ident =''', '''   settings_t            *settings = config_get_ptr();

   if (__atomic_load_n(&android_app->stationQuitRequested, __ATOMIC_ACQUIRE))
   {
      retroarch_ctl(RARCH_CTL_SET_SHUTDOWN, NULL);
      return;
   }

   while ((ident =''')
assert p.count('if (android_app->destroyRequested != 0)') == 2
p = p.replace('if (android_app->destroyRequested != 0)',
'''if (android_app->destroyRequested != 0 ||
          __atomic_load_n(&android_app->stationQuitRequested, __ATOMIC_ACQUIRE))''')
changed[files[3]] = p
p = changed['runloop.c']
p = once(p, '   switch ((enum runloop_state_enum)runloop_check_state(', '''#if defined(ANDROID) && defined(HAVE_NETWORKING)
   /* The recovery wait skips core_run(), which normally polls Android input.
    * Drain/ack its input queue and lifecycle commands even while no emulated
    * frame may run. The following state check also handles an explicit quit. */
   if (station_recovery_waiting())
      input_driver_poll();
#endif

   switch ((enum runloop_state_enum)runloop_check_state(''')
changed['runloop.c'] = p

front = 'network/netplay/netplay_frontend.c'
changed[front] = once(changed[front], '''#ifdef ANDROID
      if(station_recovery_active() && netplay->stall==NETPLAY_STALL_RUNNING_FAST)station_recovery_mark_stalled();
#endif
''', '')

def function(text, name):
    start=text.index(name); opening=text.index('{', start); depth=0
    for end in range(opening,len(text)):
        if text[end]=='{': depth+=1
        elif text[end]=='}':
            depth-=1
            if depth==0: return text[start:end+1]
    raise AssertionError(name)

flush_before=function(original[front], 'bool station_netplay_recovery_poll(void)')
flush_after=function(changed[front], 'bool station_netplay_recovery_poll(void)')
assert flush_before == flush_after

manifest = {'scope':'Station native lifecycle, Android input during recovery, and upstream pacing',
            'baseRoot':str(BASE), 'files':{},
            'baseFrontendSHA256':sha((BASE/front).read_bytes()),
            'preservedRecoveryPollSHA256':sha(flush_before.encode()),
            'extraJNI':'Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit'}
diff = []
for name in files:
    target = OUT/'sources'/name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(changed[name],encoding='utf8',newline='\n')
    manifest['files'][name] = {'baseSHA256':sha((BASE/name).read_bytes()),
                             'patchedSHA256':sha(target.read_bytes())}
    diff.extend(difflib.unified_diff(original[name].splitlines(True),changed[name].splitlines(True),
                                    fromfile='a/'+name,tofile='b/'+name))
(OUT/'station-lifecycle-r74.patch').write_text(''.join(diff),encoding='utf8',newline='\n')
manifest['patchSHA256'] = sha((OUT/'station-lifecycle-r74.patch').read_bytes())
manifest['recipeSHA256'] = sha(Path(__file__).read_bytes())
(OUT/'native-delta-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
