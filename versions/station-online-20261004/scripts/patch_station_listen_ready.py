from pathlib import Path
import difflib
R=Path(r'E:\StationNetplayWork');S=R/'upstream/libretro--RetroArch-69a4f0ea1e8a';diff=[]
def edit(name,old,new):
 p=S/name;a=p.read_text('utf8');assert a.count(old)==1,(name,a.count(old));b=a.replace(old,new);p.write_text(b,'utf8',newline='\n');diff.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
edit('frontend/drivers/platform_unix.c','static void frontend_android_shutdown(bool unused)', '''/* Report a real listening socket to the internal Station Activity. */
void station_android_netplay_listening(void)
{
   JNIEnv *env = jni_thread_getenv();
   jclass cls;
   jmethodID callback;
   if (!env || !g_android || !g_android->activity) return;
   cls = (*env)->GetObjectClass(env, g_android->activity->clazz);
   if (!cls) return;
   callback = (*env)->GetMethodID(env, cls, "onNetplayListening", "()V");
   if (callback && !(*env)->ExceptionCheck(env))
      (*env)->CallVoidMethod(env,g_android->activity->clazz,callback);
   if ((*env)->ExceptionCheck(env)) (*env)->ExceptionClear(env);
   (*env)->DeleteLocalRef(env,cls);
}

static void frontend_android_shutdown(bool unused)''')
edit('network/netplay/netplay_frontend.c','static int init_tcp_connection(netplay_t *netplay, const struct addrinfo *addr,','''#ifdef ANDROID
extern void station_android_netplay_listening(void);
#endif
static int init_tcp_connection(netplay_t *netplay, const struct addrinfo *addr,''')
edit('network/netplay/netplay_frontend.c','''         if (!listen(fd, 64) && socket_nonblock(fd))
            return fd;''','''         if (!listen(fd, 64) && socket_nonblock(fd))
         {
#ifdef ANDROID
            station_android_netplay_listening();
#endif
            return fd;
         }''')
(R/'engine-patches/retroarch-station-listening.patch').write_text(''.join(diff),'utf8')
print('Native listener event now controls guest start')
