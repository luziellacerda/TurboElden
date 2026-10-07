"""Apply the reviewed recovery hooks to the exact already patched auto-password runtime."""
from pathlib import Path
import hashlib, json, sys

SNAPSHOT=Path(__file__).resolve().parent.parent
def replace(path, old, new):
    content=path.read_text('utf8')
    if content.count(old)!=1:raise ValueError('Unexpected native base: '+str(path))
    path.write_text(content.replace(old,new),encoding='utf8',newline='\n')

def apply(source):
    source=Path(source)
    expected=json.loads((SNAPSHOT/'native/base-files.json').read_text('utf8'))
    for name, sha in expected.items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest()!=sha:raise ValueError('Native base hash mismatch: '+name)
    replace(source/'frontend/drivers/platform_unix.c',
            'static bool station_netplay_client = false;',
            '#include "station_recovery.h"\n'
            'JNIEXPORT void JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRecoveryControl(JNIEnv *env,jclass type,jlong epoch,jboolean wait,jboolean visible)\n'
            '{ (void)env;(void)type;station_recovery_request(epoch,wait,visible); }\n'
            'JNIEXPORT jlong JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRecoveryStatus(JNIEnv *env,jclass type)\n'
            '{ (void)env;(void)type;return station_recovery_status(); }\n'
            'JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRecoveryStalled(JNIEnv *env,jclass type)\n'
            '{ (void)env;(void)type;return station_recovery_is_stalled(); }\n'
            'static bool station_netplay_client = false;')
    replace(source/'frontend/drivers/platform_unix.c',
            '      station_netplay_client = args->station_netplay_role == 2;',
            '      station_netplay_client = args->station_netplay_role == 2;\n'
            '      CALL_OBJ_METHOD_PARAM(env,jstr,obj,android_app->getStringExtra,\n'
            '            (*env)->NewStringUTF(env,"STATION_RECOVERY_PROTOCOL"));\n'
            '      if(jstr) { const char *value=(*env)->GetStringUTFChars(env,jstr,0);\n'
            '         station_recovery_configure(args->station_netplay_role!=0 && value && !strcmp(value,"station-stream.v2"));\n'
            '         if(value)(*env)->ReleaseStringUTFChars(env,jstr,value); }')
    replace(source/'runloop.c',
            '#ifdef HAVE_THREADS\n   if (runloop_st->flags & RUNLOOP_FLAG_AUTOSAVE)\n      autosave_lock();',
            '#if defined(ANDROID) && defined(HAVE_NETWORKING)\n'
            '   if(station_recovery_waiting())\n'
            '   {\n'
            '      bool connected=station_netplay_recovery_poll();\n'
            '      station_recovery_confirm(true,connected);\n'
            '      /* No retro_run, rollback replay, audio generation or cached-frame rendering. */\n'
            '      retro_sleep(50);return 0;\n'
            '   }\n'
            '   if(station_recovery_active())station_recovery_confirm(false,true);\n'
            '#endif\n'
            '#ifdef HAVE_THREADS\n   if (runloop_st->flags & RUNLOOP_FLAG_AUTOSAVE)\n      autosave_lock();')
    replace(source/'network/netplay/netplay_frontend.c',
            '      netplay_sync_input_post_frame(netplay, true);\n      return false;',
            '      netplay_sync_input_post_frame(netplay, true);\n'
            '#ifdef ANDROID\n'
            '      if(station_recovery_active() && netplay->stall!=NETPLAY_STALL_NONE)station_recovery_mark_stalled();\n'
            '#endif\n      return false;')
    replace(source/'network/netplay/netplay_frontend.c',
            '   if (netplay->stall != NETPLAY_STALL_NONE && netplay->stall_time)',
            '   if (netplay->stall != NETPLAY_STALL_NONE && netplay->stall_time\n'
            '#ifdef ANDROID\n       && !station_recovery_active()\n#endif\n   )')
    replace(source/'network/netplay/netplay_frontend.c',
            'static bool netplay_pre_frame(netplay_t *netplay)\n{',
            '#ifdef ANDROID\n'
            'bool station_netplay_recovery_poll(void)\n'
            '{\n'
            '   netplay_t *np=networking_driver_st.data;\n'
            '   if(!np)return false;\n'
            '   if(!netplay_sync_pre_frame(np)){station_recovery_fail();return false;}\n'
            '   return np->modus==NETPLAY_MODUS_INPUT_FRAME_SYNC &&\n'
            '      (np->is_server?np->connected_players>1:np->self_mode==NETPLAY_CONNECTION_PLAYING);\n'
            '}\n#endif\n'
            'static bool netplay_pre_frame(netplay_t *netplay)\n{')
    replace(source/'network/netplay/netplay_frontend.c',
            '      netplay_disconnect(netplay);\n      return true;\n   }\n\n   if (netplay->is_server)',
            '#ifdef ANDROID\n      if(station_recovery_active()){station_recovery_fail();return false;}\n#endif\n'
            '      netplay_disconnect(netplay);\n      return true;\n   }\n\n   if (netplay->is_server)')
    (source/'frontend/drivers/station_recovery.h').write_bytes((SNAPSHOT/'native/station_recovery.h').read_bytes())

if __name__=='__main__':apply(Path(sys.argv[1]))
