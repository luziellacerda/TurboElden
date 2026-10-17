"""Create a isolated, unbuilt candidate and compare allocation failure paths."""
from pathlib import Path
import hashlib, json, subprocess, sys

import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--compiler',type=Path,default=Path(r'C:\Program Files\LLVM\bin\clang.exe'))
args=parser.parse_args()
APP=Path(__file__).resolve().parents[3]
WORK=args.out.resolve()
if WORK.exists() or WORK == APP or APP in WORK.parents:
    raise ValueError('Choose a fresh directory outside the repository')
WORK.mkdir(parents=True)
sys.path.insert(0,str(APP/'integration/online-snes-startup-r138/recipe'))
from patch_native_lifecycle import function_span
source=APP/'integration/online-snes-startup-r138/native/source/frontend/drivers/platform_unix.c'
raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2'
base=raw.decode('utf-8')
a,b=function_span(base,'android_app_create')
candidate_function=r'''static struct android_app* android_app_create(ANativeActivity* activity,
        void* savedState, size_t savedStateSize)
{
   int msgpipe[2] = {-1, -1};
   struct android_app *android_app =
      (struct android_app*)calloc(1, sizeof(*android_app));

   if (!android_app)
   {
      RARCH_ERR("Failed to initialize android_app.\n");
      return NULL;
   }
   android_app->activity = activity;
   android_app->mutex = slock_new();
   android_app->cond = scond_new();
   if (!android_app->mutex || !android_app->cond)
      goto startup_failed;

   if (savedState && savedStateSize)
   {
      android_app->savedState = malloc(savedStateSize);
      if (!android_app->savedState)
         goto startup_failed;
      android_app->savedStateSize = savedStateSize;
      memcpy(android_app->savedState, savedState, savedStateSize);
   }
   if (pipe(msgpipe))
      goto startup_failed;
   android_app->msgread = msgpipe[0];
   android_app->msgwrite = msgpipe[1];
   android_app->thread = sthread_create(android_app_entry, android_app);
   if (!android_app->thread)
      goto startup_failed;

   /* Preserve the normal handshake with the worker. */
   slock_lock(android_app->mutex);
   while (!android_app->running)
      scond_wait(android_app->cond, android_app->mutex);
   slock_unlock(android_app->mutex);
   return android_app;

startup_failed:
   /* No worker exists on these failure branches. Do not wait or join. */
   if (msgpipe[0] >= 0)
      close(msgpipe[0]);
   if (msgpipe[1] >= 0)
      close(msgpipe[1]);
   free(android_app->savedState);
   scond_free(android_app->cond);
   slock_free(android_app->mutex);
   free(android_app);
   RARCH_ERR("Failed to prepare Android native worker.\n");
   return NULL;
}'''
newline='\r\n' if b'\r\n' in raw else '\n'
candidate_function=candidate_function.replace('\n',newline)
old_tail='''   if (!activity->instance)
      station_activity_release(activity);'''.replace('\n',newline)
new_tail='''   if (!activity->instance)
   {
      station_activity_release(activity);
      ANativeActivity_finish(activity);
   }'''.replace('\n',newline)
assert base.count(old_tail)==1
candidate=base[:a]+candidate_function+base[b:]
candidate=candidate.replace(old_tail,new_tail)
assert candidate.replace(candidate_function,base[a:b]).replace(new_tail,old_tail)==base
out=WORK/'native-allocation-candidate.c'
out.write_bytes(candidate.encode('utf-8'))
assert hashlib.sha256(out.read_bytes()).hexdigest()=='b3ad1cbe5843d77a2f645707d3bb329fbbc8bb1a41d86e6cfe76d3d1626858dd'

TEMPLATE=r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
typedef struct {int live;} slock_t;
typedef struct {int live;} scond_t;
typedef struct {int live;} sthread_t;
typedef struct {void *instance;} ANativeActivity;
struct android_app {
 ANativeActivity *activity;slock_t *mutex;scond_t *cond;sthread_t *thread;
 void *savedState;size_t savedStateSize;int msgread,msgwrite,running;
};
static int fault,live_allocs,live_fds,finish_calls,release_calls,create_calls;
static void *station_activity_app;
static int station_activity_mutex;
static void *alloc(size_t n){void *p=malloc(n?n:1);if(p)live_allocs++;return p;}
static void dealloc(void *p){if(p){live_allocs--;free(p);}}
static void *fake_calloc(size_t n,size_t size){if(fault==1)return NULL;void *p=alloc(n*size);if(p)memset(p,0,n*size);return p;}
static void *fake_malloc(size_t n){if(fault==4)return NULL;return alloc(n);}
static void *fake_memcpy(void *to,const void *from,size_t n){if(!to&&n){puts("NULL_SAVED_STATE_DESTINATION");exit(0);}if(!n)return to;return memcpy(to,from,n);}
static slock_t *slock_new(void){return fault==2?NULL:alloc(sizeof(slock_t));}
static scond_t *scond_new(void){return fault==3?NULL:alloc(sizeof(scond_t));}
static void slock_free(slock_t *p){dealloc(p);}
static void scond_free(scond_t *p){dealloc(p);}
static void slock_lock(slock_t *p){if(!p)return;/* Matches rthreads null guard. */}
static void slock_unlock(slock_t *p){(void)p;}
static void scond_wait(scond_t *p,slock_t *m){if(!m){puts("NULL_MUTEX_PASSED_TO_CONDITION_WAIT");exit(0);}if(!p){puts("NULL_CONDITION_PASSED_TO_WAIT");exit(0);}puts("WAIT_WITHOUT_WORKER");exit(0);}
static int pipe(int fds[2]){if(fault==5)return -1;fds[0]=101;fds[1]=102;live_fds+=2;return 0;}
static int close(int fd){if(fd==101||fd==102)live_fds--;return 0;}
static void android_app_entry(void *p){(void)p;}
static sthread_t *sthread_create(void (*fn)(void*),void *p){(void)fn;create_calls++;if(fault==6)return NULL;((struct android_app*)p)->running=1;return alloc(sizeof(sthread_t));}
static void pthread_mutex_lock(int *p){(void)p;}
static void pthread_mutex_unlock(int *p){(void)p;}
static void station_activity_release(ANativeActivity *a){(void)a;release_calls++;}
static void ANativeActivity_finish(ANativeActivity *a){(void)a;finish_calls++;}
#define malloc fake_malloc
#define calloc fake_calloc
#define free dealloc
#define memcpy fake_memcpy
#define RARCH_ERR(...) fprintf(stderr,__VA_ARGS__)
/* @PRODUCTION@ */
static void creation_tail(ANativeActivity *activity,void *savedState,size_t savedStateSize){
/* @TAIL@ */
}
int main(int argc,char **argv){
 if(argc<2||argc>3)return 2;fault=atoi(argv[1]);ANativeActivity activity={0};char saved[8]={0};
 void *saved_pointer=saved;size_t saved_size=sizeof(saved);bool empty_state=argc==3;
 if(empty_state){saved_size=0;if(!strcmp(argv[2],"none"))saved_pointer=NULL;else if(strcmp(argv[2],"zero"))return 2;}
 creation_tail(&activity,saved_pointer,saved_size);
 if(fault==2&&activity.instance&&((struct android_app*)activity.instance)->mutex==NULL)
  puts("NULL_MUTEX_ACCEPTED_IN_RUNNING_INSTANCE");
 if(fault==3&&activity.instance&&((struct android_app*)activity.instance)->cond==NULL)
  puts("NULL_CONDITION_ACCEPTED_IN_RUNNING_INSTANCE");
 if(fault==0||empty_state){
  struct android_app *a=activity.instance;if(!a||!a->running||create_calls!=1||finish_calls||release_calls)return 3;
  close(a->msgread);close(a->msgwrite);free(a->savedState);scond_free(a->cond);slock_free(a->mutex);free(a->thread);free(a);
 }
 printf("RESULT fault=%d instanceNull=%d liveAllocations=%d liveFds=%d releaseCalls=%d finishCalls=%d createCalls=%d\n",fault,activity.instance==NULL,live_allocs,live_fds,release_calls,finish_calls,create_calls);
 return 0;
}
'''
def build_fixture(label,text):
    a,b=function_span(text,'android_app_create')
    tail=text[text.index('   activity->instance = android_app_create(activity,'):]
    tail=tail[:tail.index(newline+'}'+newline)]
    generated=WORK/('native-allocation-'+label+'-fixture.c')
    generated.write_text(TEMPLATE.replace('/* @PRODUCTION@ */',text[a:b]).replace('/* @TAIL@ */',tail),encoding='utf-8')
    exe=generated.with_suffix('.exe')
    compiled=subprocess.run([str(args.compiler),'-std=c11','-O2','-Wall','-Wextra',str(generated),'-o',str(exe)],capture_output=True,text=True)
    if compiled.returncode:raise RuntimeError(compiled.stderr)
    cases={}
    for mode,name in enumerate(['success','app_calloc','mutex','condition','saved_state','pipe','thread']):
        run=subprocess.run([str(exe),str(mode)],capture_output=True,text=True,timeout=5)
        if run.returncode:raise RuntimeError(run.stdout+run.stderr)
        cases[name]=dict(exitCode=run.returncode,output=run.stdout.strip())
        if label=='candidate':
            assert 'liveAllocations=0 liveFds=0' in run.stdout
            assert ('releaseCalls=0 finishCalls=0' if mode==0 else 'instanceNull=1') in run.stdout
            if mode:assert 'releaseCalls=1 finishCalls=1' in run.stdout
    for variant in ('none','zero'):
        for fault in (0,4):
            run=subprocess.run([str(exe),str(fault),variant],capture_output=True,text=True,timeout=5)
            if run.returncode:raise RuntimeError(run.stdout+run.stderr)
            assert 'instanceNull=0 liveAllocations=0 liveFds=0 releaseCalls=0 finishCalls=0' in run.stdout
            cases['empty-state-'+variant+'-malloc-fault-'+str(fault)]=dict(exitCode=run.returncode,output=run.stdout.strip())
    return dict(fixtureSha256=hashlib.sha256(generated.read_bytes()).hexdigest(),cases=cases)
results={'baseline':build_fixture('baseline',base),'candidate':build_fixture('candidate',candidate)}
report=dict(schemaVersion=1,baselineSha256=hashlib.sha256(raw).hexdigest(),candidateSha256=hashlib.sha256(out.read_bytes()).hexdigest(),
 changedFunctions=['android_app_create','ANativeActivity_onCreate failure tail'],
 allOtherSourceBytesPreserved=True,
 normalHandshakePreserved=True,normalWorkerSchedulingPreserved=True,hotLoopsChanged=False,
 emptySavedStateCases=4,emptySavedStateCasesPassed=True,
 nativeActivityFinishOnlyOnCreationFailure=True,allCandidateResourceFailureBranchesReturnWithoutWait=True,
 compilerSha256=hashlib.sha256(args.compiler.read_bytes()).hexdigest(),
 results=results,productCodeChanged=False,apkBuilt=False,androidExecuted=False,
 scope='Exact android_app_create and exact onCreate creation tail. Allocation, FD, lock and worker primitives are controlled fixtures. Baseline unsafe wait/null branches are recorded without actually blocking or crashing the host.',
 futurePackagingRisk='Requires a new native runtime and engine IDs after real Android/NDK build, byte preservation checks, signed package and all-device validation. Candidate remains isolated and unapplied.')
(WORK/'native-allocation-candidate-receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
