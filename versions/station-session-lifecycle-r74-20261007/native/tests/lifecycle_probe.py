"""Host tests using extracted native functions and real Windows threads.

Android's Looper and core cleanup are modeled. SRW locks/condition variables
execute the actual lock/join ordering. No emulator, ROM, socket or device runs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/('sources' if (ROOT/'sources').exists() else 'source')
BASE = Path(r'E:\R73fixed\RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576')

def function(text, name):
    pos = text.index(name+'(')
    start = text.rfind('\n', 0, pos)+1
    end = text.index('{',pos)+1
    depth = 1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}')
        end += 1
    return text[start:end]

def sha(data):
    return hashlib.sha256(data).hexdigest()

PREAMBLE = r'''
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef SRWLOCK slock_t;
typedef CONDITION_VARIABLE scond_t;
typedef HANDLE sthread_t;
typedef HANDLE ALooper;
typedef struct FakeNativeActivity { int id; } ANativeActivity;
typedef SRWLOCK pthread_mutex_t;
#define PTHREAD_MUTEX_INITIALIZER SRWLOCK_INIT
static void pthread_mutex_lock(pthread_mutex_t *m){AcquireSRWLockExclusive(m);}
static void pthread_mutex_unlock(pthread_mutex_t *m){ReleaseSRWLockExclusive(m);}
static volatile LONG shutdowns, wakes, writes, checks, lock_at_join;
static HANDLE allow_cleanup;
static bool hold_cleanup_until_join;
static void slock_lock(slock_t *m){AcquireSRWLockExclusive(m);}
static void slock_unlock(slock_t *m){ReleaseSRWLockExclusive(m);}
static void scond_wait(scond_t *c,slock_t *m){SleepConditionVariableSRW(c,m,INFINITE,0);}
static void scond_broadcast(scond_t *c){WakeAllConditionVariable(c);}
static void slock_free(slock_t *m){free(m);}
static void scond_free(scond_t *c){free(c);}
static int close(int fd){(void)fd;return 0;}
static slock_t *join_mutex;
static void sthread_join(sthread_t *t){
   if(TryAcquireSRWLockExclusive(join_mutex))ReleaseSRWLockExclusive(join_mutex);
   else InterlockedIncrement(&lock_at_join);
   SetEvent(allow_cleanup);
   WaitForSingleObject(*t,INFINITE);CloseHandle(*t);free(t);
}
struct android_app {
   slock_t *mutex; scond_t *cond; sthread_t *thread;
   int msgread,msgwrite,destroyed,destroyRequested,stationQuitRequested,activityState,reinitRequested;
   ALooper *looper;
   struct FakeActivity { void *clazz; } *activity;
};
static struct android_app *g_android;
static struct android_app *station_activity_app;
static pthread_mutex_t station_activity_mutex=PTHREAD_MUTEX_INITIALIZER;
static ANativeActivity *station_activity_owner;
typedef int jboolean;
typedef void *jobject;
typedef const struct FakeJNI *JNIEnv;
struct FakeJNI { jboolean (*IsSameObject)(JNIEnv *,jobject,jobject); };
static jboolean same_object(JNIEnv *e,jobject a,jobject b){(void)e;return a==b;}
#define JNIEXPORT
#define JNICALL
#define JNI_FALSE 0
#define JNI_TRUE 1
static void ALooper_wake(ALooper *l){InterlockedIncrement(&wakes);SetEvent(*l);}
static int ALooper_pollOnce(int timeout,void *a,void *b,void *c){
   (void)a;(void)b;(void)c;
   WaitForSingleObject(*g_android->looper,timeout<0?INFINITE:(DWORD)timeout);
   return -1;
}
static void android_app_write_cmd(struct android_app *a,int8_t cmd){(void)a;(void)cmd;InterlockedIncrement(&writes);}
static void android_input_poll_main_cmd(void){}
static void retroarch_ctl(int code,void *unused){(void)code;(void)unused;InterlockedIncrement(&shutdowns);}
static unsigned runloop_get_flags(void){return 0;}
static void command_event(int code,void *unused){(void)code;(void)unused;}
#define RARCH_CTL_SET_SHUTDOWN 1
#define LOOPER_ID_MAIN 1
#define RUNLOOP_FLAG_PAUSED 1
#define CMD_EVENT_REINIT 1
#define APP_CMD_REINIT_DONE 1
#define CHECK(x) do{InterlockedIncrement(&checks);if(!(x)){fprintf(stderr,"FAIL line%d %s\n",__LINE__,#x);return 2;}}while(0)
'''

TEST = r'''
static DWORD WINAPI native_worker(void *data){
   struct android_app *a=data;
   if(hold_cleanup_until_join)WaitForSingleObject(allow_cleanup,INFINITE);
   else WaitForSingleObject(*a->looper,INFINITE);
   /* Android cleanup acquires precisely this mutex in the real source. */
   slock_lock(a->mutex);
   a->destroyed=1;scond_broadcast(a->cond);
   slock_unlock(a->mutex);
   return 0;
}
static struct android_app *make_app(bool worker){
   struct android_app *a=calloc(1,sizeof(*a));
   a->mutex=calloc(1,sizeof(slock_t));a->cond=calloc(1,sizeof(scond_t));
   InitializeSRWLock(a->mutex);InitializeConditionVariable(a->cond);
   a->looper=malloc(sizeof(HANDLE));*a->looper=CreateEvent(NULL,FALSE,FALSE,NULL);
   g_android=a;join_mutex=a->mutex;
   if(worker){a->thread=malloc(sizeof(HANDLE));*a->thread=CreateThread(NULL,0,native_worker,a,0,NULL);}
   return a;
}
static DWORD WINAPI state_waiter(void *data){android_app_set_activity_state(data,4);return 0;}
int main(int argc,char **argv){
   struct android_app *a;HANDLE wake,waiter;
   if(argc!=2)return 3;
   allow_cleanup=CreateEvent(NULL,TRUE,FALSE,NULL);
   if(!strcmp(argv[1],"free")){
      a=make_app(true);puts("entered free");fflush(stdout);android_app_free(a);
      CHECK(g_android==NULL);CHECK(lock_at_join==0);
   }else if(!strcmp(argv[1],"join")){
      hold_cleanup_until_join=true;a=make_app(true);puts("entered join");fflush(stdout);
      android_app_free(a);
   }else if(!strcmp(argv[1],"completed-state")){
      a=make_app(false);a->destroyed=1;puts("entered completed-state");fflush(stdout);
      android_app_set_activity_state(a,4);CHECK(writes==0);
   }
#ifdef CANDIDATE
   else if(!strcmp(argv[1],"repeat")){
      for(int i=0;i<100;i++){
         a=make_app(true);wake=*a->looper;ALooper *looper=a->looper;
         CHECK(android_app_request_quit(a));
         CHECK(__atomic_load_n(&a->stationQuitRequested,__ATOMIC_ACQUIRE)==1);
         /* A second human request is accepted while the same exit is pending.
            If cleanup won the race, false already-finished is also correct. */
         android_app_request_quit(a);
         android_app_free(a);CloseHandle(wake);free(looper);
         CHECK(g_android==NULL);CHECK(lock_at_join==0);
      }
      CHECK(writes==0);
   }else if(!strcmp(argv[1],"initial-window")){
      a=make_app(false);CHECK(android_app_request_quit(a));
      CHECK(!android_run_events(NULL));CHECK(shutdowns==1);CHECK(writes==0);
   }else if(!strcmp(argv[1],"late-state")){
      a=make_app(false);waiter=CreateThread(NULL,0,state_waiter,a,0,NULL);
      while(!writes)Sleep(1);
      slock_lock(a->mutex);a->destroyed=1;scond_broadcast(a->cond);slock_unlock(a->mutex);
      CHECK(WaitForSingleObject(waiter,1000)==WAIT_OBJECT_0);CloseHandle(waiter);
   }else if(!strcmp(argv[1],"ended-quit")){
      CHECK(!android_app_request_quit(NULL));a=make_app(false);a->destroyed=1;
      CHECK(!android_app_request_quit(a));CHECK(wakes==0);CHECK(writes==0);
   }else if(!strcmp(argv[1],"worker-complete")){
      a=make_app(true);ALooper_wake(a->looper);
      slock_lock(a->mutex);while(!a->destroyed)scond_wait(a->cond,a->mutex);slock_unlock(a->mutex);
      android_app_free(a);CHECK(lock_at_join==0);CHECK(g_android==NULL);
   }else if(!strcmp(argv[1],"jni-identity")){
      const struct FakeJNI table={same_object};JNIEnv env=&table;
      a=make_app(false);a->activity=malloc(sizeof(*a->activity));a->activity->clazz=(void*)1;
      station_activity_app=a;
      CHECK(!Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit(&env,(void*)2));
      CHECK(a->stationQuitRequested==0);
      CHECK(Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit(&env,(void*)1));
      CHECK(a->stationQuitRequested==1);
      a->destroyed=1;
      CHECK(!Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit(&env,(void*)1));
      station_activity_app=NULL;
      CHECK(!Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit(&env,(void*)1));
   }else if(!strcmp(argv[1],"reserve-overlap")){
      ANativeActivity one={1},two={2};
      CHECK(station_activity_reserve(&one));CHECK(!station_activity_reserve(&two));
      CHECK(station_activity_owner==&one);
      station_activity_release(&two);CHECK(station_activity_owner==&one);
      /* Releasing ownership is ordered after join in real onDestroy. */
      station_activity_release(&one);CHECK(station_activity_reserve(&two));
      station_activity_release(&one);CHECK(station_activity_owner==&two);
      station_activity_release(&two);CHECK(station_activity_owner==NULL);
   }
#endif
   else return 3;
   printf("PASS checks=%ld\n",checks);return 0;
}
'''

MUTEX_SHIM = r'''
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
typedef SRWLOCK pthread_mutex_t;
#define PTHREAD_MUTEX_INITIALIZER SRWLOCK_INIT
static void pthread_mutex_lock(pthread_mutex_t *m){AcquireSRWLockExclusive(m);}
static void pthread_mutex_unlock(pthread_mutex_t *m){ReleaseSRWLockExclusive(m);}
'''

RESET_TEST = r'''
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL reset line%d %s\n",__LINE__,#x);return 2;}}while(0)
int main(void){int checks=0;
   station_recovery_configure(true);station_recovery_request(9,false,false);
   station_recovery_confirm(false,true);station_recovery_mark_stalled();station_recovery_fail();
#ifdef CANDIDATE
   station_recovery_reset();
#endif
   station_recovery_configure(true);
   CHECK(!station_recovery_failed);
   CHECK(station_recovery_waiting());CHECK(station_recovery_visible);
   CHECK(!station_recovery_is_stalled());CHECK(station_recovery_status()==-1);
   station_recovery_request(1,true,true);station_recovery_confirm(true,true);
   CHECK(station_recovery_status()==11);
   /* Same-session configure/reconnect preserves the new epoch and buffers. */
   station_recovery_configure(true);CHECK(station_recovery_status()==11);
   station_recovery_request(2,true,true);station_recovery_confirm(true,true);
   CHECK(station_recovery_status()==19);
   station_recovery_request(1,false,true);CHECK(station_recovery_epoch==2);
   station_recovery_request(2,false,true);station_recovery_confirm(false,true);
   CHECK(station_recovery_status()==18);CHECK(!station_recovery_waiting());
#ifdef CANDIDATE
   station_recovery_reset();station_recovery_request(1,true,true);
   station_recovery_configure(true);station_recovery_confirm(true,true);
   CHECK(station_recovery_status()==11);
#endif
   printf("PASS reset checks=%d\n",checks);return 0;
}
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();out=args.out.resolve()
    assert str(out).startswith('E:\\'), 'Test build outputs must be on E:'
    out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'native-delta-manifest.json').read_text())
    for name,hashes in manifest['files'].items():
        assert sha((BASE/name).read_bytes())==hashes['baseSHA256']
        assert sha((SOURCE/name).read_bytes())==hashes['patchedSHA256']
    compiler=Path(r'C:\Program Files\LLVM\bin\clang.exe')
    results=[];extracted={}
    for label,tree in [('baseline',BASE),('candidate',SOURCE)]:
        source=(tree/'frontend/drivers/platform_unix.c').read_text(encoding='utf8')
        input_source=(tree/'input/drivers/android_input.c').read_text(encoding='utf8')
        funcs={n:function(source,n) for n in ['android_app_free','android_app_set_activity_state']}
        if label=='candidate':funcs={'android_app_request_quit':function(source,'android_app_request_quit'),**funcs,
                                    'android_run_events':function(input_source,'android_run_events'),
                                    'stationRequestQuit':function(source,'Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit'),
                                    'station_activity_reserve':function(source,'station_activity_reserve'),
                                    'station_activity_release':function(source,'station_activity_release')}
        extracted[label]={n:sha(t.encode()) for n,t in funcs.items()}
        c=PREAMBLE+'\n'+'\n'.join(funcs.values())+'\n'+TEST
        if label=='candidate':c='#define CANDIDATE\n'+c
        src=out/(label+'.c');exe=out/(label+'.exe');src.write_text(c,encoding='utf8')
        cp=subprocess.run([str(compiler),'-std=c11','-Wno-unused-function',str(src),'-o',str(exe)],capture_output=True,text=True)
        (out/(label+'-compile.log')).write_text(cp.stdout+cp.stderr,encoding='utf8')
        assert cp.returncode==0,cp.stderr
        modes=['free','join','completed-state'] if label=='baseline' else ['free','completed-state','repeat','initial-window','late-state','ended-quit','worker-complete','jni-identity','reserve-overlap']
        for mode in modes:
            try:
                run=subprocess.run([str(exe),mode],capture_output=True,text=True,timeout=1 if label=='baseline' else 5)
                assert label=='candidate' and run.returncode==0,(label,mode,run.stdout,run.stderr)
                results.append({'label':label,'mode':mode,'passed':True,'stdout':run.stdout.strip()})
            except subprocess.TimeoutExpired as timeout:
                assert label=='baseline',(label,mode,'unexpected hang')
                text=timeout.stdout.decode() if isinstance(timeout.stdout,bytes) else timeout.stdout
                assert text and 'entered '+mode in text,(label,mode,'did not reach target function')
                results.append({'label':label,'mode':mode,'expectedDeadlockReproduced':True})
        header=(tree/'frontend/drivers/station_recovery.h').read_text(encoding='utf8').replace('#include <pthread.h>','')
        c=MUTEX_SHIM+'\n'+header+'\n'+RESET_TEST
        if label=='candidate':c='#define CANDIDATE\n'+c
        src=out/(label+'-reset.c');exe=out/(label+'-reset.exe');src.write_text(c,encoding='utf8')
        cp=subprocess.run([str(compiler),'-std=c11',str(src),'-o',str(exe)],capture_output=True,text=True)
        assert cp.returncode==0,cp.stderr
        run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5)
        assert run.returncode==(2 if label=='baseline' else 0),(label,run.stdout,run.stderr)
        results.append({'label':label,'mode':'reset','exitCode':run.returncode,'stdout':run.stdout.strip(),'stderr':run.stderr.strip()})
    candidate=(SOURCE/'frontend/drivers/platform_unix.c').read_text(encoding='utf8')
    assert '/sdcard/switch' not in candidate and '/sdcard/reset' not in candidate
    assert candidate.index('station_recovery_reset();') < candidate.index('activity->instance = android_app_create')
    create=function(candidate,'ANativeActivity_onCreate')
    destroy=function(candidate,'onDestroy')
    assert create.index('station_activity_reserve(activity)')<create.index('station_recovery_reset();')
    assert destroy.index('android_app_free(')<destroy.index('station_activity_release(activity)')
    assert manifest['baseFrontendSHA256']==sha((BASE/'network/netplay/netplay_frontend.c').read_bytes())
    receipt={'scope':__doc__,'testRecipeSHA256':sha(Path(__file__).read_bytes()),
             'deltaManifestSHA256':sha((ROOT/'native-delta-manifest.json').read_bytes()),
             'extractedFunctionHashes':extracted,'results':results,
             'baseImmutable':True,'realAndroidTested':False,'networkTested':False,
             'extraGuards':['legacy shell hooks removed','reset before thread creation','R73 network pump unchanged']}
    (out/'lifecycle-probe-result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    (ROOT/'tests/lifecycle-probe-result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
