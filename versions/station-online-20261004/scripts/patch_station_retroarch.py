from pathlib import Path
import difflib
R=Path(r'E:\StationNetplayWork');S=R/'upstream/libretro--RetroArch-69a4f0ea1e8a';changes=[]
def edit(name,old,new):
 p=S/name;a=p.read_text('utf-8');assert a.count(old)==1,(name,a.count(old));b=a.replace(old,new);p.write_text(b,'utf-8',newline='\n');changes.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
edit('retroarch_types.h','   const char *libretro_path;\n   int argc;',
'''   const char *libretro_path;
#ifdef ANDROID
   int station_netplay_role; /* 1 host, 2 client; explicit internal Activity only */
   const char *station_netplay_address;
   const char *station_netplay_port;
#endif
   int argc;''')
edit('tasks/task_content.c','   wrap_args->argc           = 0;',
'''   wrap_args->argc           = 0;
#ifdef ANDROID
   wrap_args->station_netplay_role = 0;
   wrap_args->station_netplay_address = NULL;
   wrap_args->station_netplay_port = NULL;
#endif''')
edit('tasks/task_content.c','   if (args->flags & RARCH_MAIN_WRAP_FLAG_VERBOSE)\n      argv[(*argc)++] = strldup("-v", sizeof("-v"));',
'''#ifdef ANDROID
   /* Pass typed Android fields through the upstream CLI path. Netcode is unchanged. */
   if (args->station_netplay_role == 1)
      argv[(*argc)++] = strdup("--host");
   else if (args->station_netplay_role == 2 && args->station_netplay_address)
   {
      argv[(*argc)++] = strdup("--connect");
      argv[(*argc)++] = strdup(args->station_netplay_address);
   }
   if (args->station_netplay_role && args->station_netplay_port)
   {
      argv[(*argc)++] = strdup("--port");
      argv[(*argc)++] = strdup(args->station_netplay_port);
   }
#endif
   if (args->flags & RARCH_MAIN_WRAP_FLAG_VERBOSE)
      argv[(*argc)++] = strldup("-v", sizeof("-v"));''')
edit('frontend/drivers/platform_unix.c','   /* Current IME. */',
'''   /* Station-only typed transport selection. No URL, command line or password logging. */
   if (args)
   {
      static char station_address[64], station_port[6];
      args->station_netplay_role = 0;
      station_address[0] = station_port[0] = 0;
      CALL_OBJ_METHOD_PARAM(env, jstr, obj, android_app->getStringExtra,
            (*env)->NewStringUTF(env, "STATION_NETPLAY_ROLE"));
      if (jstr)
      {
         const char *value = (*env)->GetStringUTFChars(env, jstr, 0);
         if (value) args->station_netplay_role = !strcmp(value,"host") ? 1 : (!strcmp(value,"client") ? 2 : 0);
         if (value) (*env)->ReleaseStringUTFChars(env,jstr,value);
      }
      CALL_OBJ_METHOD_PARAM(env, jstr, obj, android_app->getStringExtra,
            (*env)->NewStringUTF(env, "STATION_NETPLAY_ADDRESS"));
      if (jstr)
      {
         const char *value = (*env)->GetStringUTFChars(env, jstr, 0);
         if (value && strlen(value) < sizeof(station_address) &&
               strspn(value,"0123456789abcdefABCDEF:.") == strlen(value))
            strlcpy(station_address,value,sizeof(station_address));
         if (value) (*env)->ReleaseStringUTFChars(env,jstr,value);
      }
      CALL_OBJ_METHOD_PARAM(env, jstr, obj, android_app->getStringExtra,
            (*env)->NewStringUTF(env, "STATION_NETPLAY_PORT"));
      if (jstr)
      {
         const char *value = (*env)->GetStringUTFChars(env, jstr, 0);
         if (value && strlen(value) < sizeof(station_port) && strspn(value,"0123456789") == strlen(value) && atoi(value)>=1024 && atoi(value)<=65535)
            strlcpy(station_port,value,sizeof(station_port));
         if (value) (*env)->ReleaseStringUTFChars(env,jstr,value);
      }
      if (!station_port[0] || (args->station_netplay_role==2 && !station_address[0]))
         args->station_netplay_role = 0;
      args->station_netplay_address = station_address;
      args->station_netplay_port = station_port;
   }

   /* Current IME. */''')
p=S/'pkg/android/phoenix-common/jni/Android.mk';a=p.read_text('utf-8');b=a
for feature in ('HAVE_NETWORKGAMEPAD','HAVE_NETWORK_CMD','HAVE_CLOUDSYNC','HAVE_NETPLAYDISCOVERY','HAVE_ONLINE_UPDATER','HAVE_UPDATE_ASSETS','HAVE_UPDATE_CORES','HAVE_UPDATE_CORE_INFO','HAVE_TRANSLATE'):
 b=b.replace('-D'+feature+' \\\n','')
p.write_text(b,'utf-8',newline='\n');changes.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/pkg/android/phoenix-common/jni/Android.mk',tofile='b/pkg/android/phoenix-common/jni/Android.mk'))
(R/'engine-patches/retroarch-station-direct.patch').write_text(''.join(changes),'utf-8')
print('Typed host/client arguments; removed public updater, discovery, command, cloud sync build features')
