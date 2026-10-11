"""Host-only: execute the real room reconciler and EGL lifecycle gate with API stubs.

No shader, Android renderer, telephone, server request or game is exercised.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'java/netplay-src/org/emulationstation/frontend/netplay'
BASE = ROOT.parent / 'station-game-menu-controller-audit-r120-20261010/java/netplay-src/org/emulationstation/frontend/netplay'


def block(source, start):
    """Balanced Java block, preserving the production body byte for byte."""
    opening = source.index('{', start)
    depth, quote, comment, escaped = 0, '', '', False
    i = opening
    while i < len(source):
        c, nxt = source[i], source[i:i + 2]
        if comment == '//':
            if c == '\n': comment = ''
        elif comment == '/*':
            if nxt == '*/': comment = ''; i += 1
        elif quote:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == quote: quote = ''
        elif nxt in ('//', '/*'): comment = nxt; i += 1
        elif c in ('"', "'"): quote = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return source[start:i + 1]
        i += 1
    raise AssertionError('Unbalanced source block')


def methods(source, name):
    matches = list(re.finditer(r'(?m)^\s{4,8}(?:(?:private|public|protected|static|final|synchronized|@Override)\s+)*[\w<>.\[\]]+\s+' + re.escape(name) + r'\([^\n]*', source))
    return [block(source, match.start()).strip() for match in matches]


def method(source, name):
    matches = methods(source, name)
    if len(matches) != 1: raise AssertionError((name, len(matches)))
    return matches[0]


ROOM_STUBS = r'''
static int checks;
static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
static class View {
 ViewGroup parent;Object params;int attaches,detaches;
 Object getLayoutParams(){return params;}void setLayoutParams(Object p){params=p;}
 void setPadding(int a,int b,int c,int d){}
 void attached(){attaches++;}void detached(){detaches++;}
}
static class ViewGroup extends View {
 final List<View> children=new ArrayList<>();
 void addView(View v,Object p){if(v.parent!=null)throw new AssertionError("already parented");v.params=p;v.parent=this;children.add(v);v.attached();}
 void removeViewAt(int i){View v=children.remove(i);v.parent=null;v.detached();}
 void removeAllViews(){for(int i=children.size()-1;i>=0;i--)removeViewAt(i);}
 int getChildCount(){return children.size();}View getChildAt(int i){return children.get(i);}
 void bringChildToFront(View v){if(v.parent!=this)throw new AssertionError("missing child");children.remove(v);children.add(v);}
 @Override void attached(){super.attached();for(View v:children)v.attached();}
 @Override void detached(){super.detached();for(View v:children)v.detached();}
}
static class LinearLayout extends ViewGroup {
 static class LayoutParams {int width,height;LayoutParams(int w,int h){width=w;height=h;}}
}
static class ScrollView extends ViewGroup {
 ScrollView(Object owner){}void setFillViewport(boolean b){}void setVerticalScrollBarEnabled(boolean b){}
 static class LayoutParams extends LinearLayout.LayoutParams {LayoutParams(int w,int h){super(w,h);}}
}
static class Bitmap {}
static class StationCreateGameCard extends LinearLayout {
 static int created;final LinearLayout actions=new LinearLayout();final View surface=new View();Bitmap bitmap;boolean bounded;String name,platform;
 StationCreateGameCard(Object o,boolean room){created++;addView(actions,new LayoutParams(1,1));addView(surface,new LayoutParams(1,1));}
 void setViewportBounded(boolean v){bounded=v;}void setGameName(String n){name=n;}void setPlatform(String p){platform=p;}void setCover(Bitmap b){bitmap=b;}
}
static class Client {String name(String id){return "game "+id;}}
static class Artwork {
 interface Callback {void complete(Bitmap b);}final List<Callback> pending=new ArrayList<>();int requests;boolean delayed;Bitmap image=new Bitmap();
 void load(String item,int max,Callback cb){check(max==1536);requests++;if(delayed)pending.add(cb);else cb.complete(image);}
}
final LinearLayout rooms=new LinearLayout();final Client client=new Client();final Artwork artwork=new Artwork();
StationCreateGameCard ownRoomCard;String ownRoomCoverItem="";Object start,roomReadiness;
int viewport=320;int dp(int v){return v;}int roomViewportHeight(){return viewport;}
String coverPlatform(String id){return "snes";}
LinearLayout vertical(){return new LinearLayout();}
LinearLayout card(LinearLayout p){LinearLayout c=vertical();p.addView(c,new LinearLayout.LayoutParams(-1,-2));return c;}
void bindHeroCover(){ownRoomCard.setCover(artwork.image);}
'''

ROOM_TEST = r'''
static void current(RoomTest t,String own,String item,boolean reverse){
 t.beginRoomRows();
 if(!own.isEmpty()){LinearLayout body=t.roomCoverCard("own",own,item,true);body.addView(new View(),new LinearLayout.LayoutParams(1,1));}
 if(reverse){t.roomCoverCard("room","b","same",false);t.roomCoverCard("room","a","same",false);}
 else{t.roomCoverCard("room","a","same",false);t.roomCoverCard("room","b","same",false);}
 t.reconcileRoomRows();
}
public static void main(String[] args){
 RoomTest t=new RoomTest();current(t,"mine","snes",false);
 check(t.roomRows.size()==3);check(t.rooms.getChildCount()==3);check(t.ownRoomCard.bounded);check(t.ownRoomCard.bitmap==t.artwork.image);
 RoomRow own=t.roomRows.get(roomRowKey("own","mine","snes"));View surface=own.display.surface;
 List<RoomRow> initial=new ArrayList<>(t.roomRows.values());int created=StationCreateGameCard.created,requests=t.artwork.requests;
 for(int i=0;i<600;i++){
  current(t,"mine","snes",i%2==1);check(t.roomRows.get(roomRowKey("own","mine","snes"))==own);check(t.ownRoomCard==own.display);
  check(surface.detaches==0);check(own.content.getChildCount()==1);check(t.roomRows.size()==3);check(StationCreateGameCard.created==created);check(t.artwork.requests==requests);
  for(RoomRow row:initial)check(row.display.surface.detaches==0);
 }
 check(t.rooms.getChildAt(0)==own.root);check(t.rooms.getChildAt(1)==t.roomRows.get(roomRowKey("room","b","same")).root);
 t.viewport=260;current(t,"mine","snes",false);check(((LinearLayout.LayoutParams)own.root.getLayoutParams()).height==260);check(surface.detaches==0);
 current(t,"mine","other",false);check(!t.roomRows.containsValue(own));check(own.display.bitmap==null);check(surface.detaches==1);check(t.ownRoomCard!=own.display);check(t.roomRows.size()==3);
 RoomRow oldB=t.roomRows.get(roomRowKey("room","b","same"));t.beginRoomRows();t.roomCoverCard("room","a","same",false);t.reconcileRoomRows();
 check(oldB.display.bitmap==null);check(oldB.display.surface.detaches==1);check(t.ownRoomCard==null);check(t.roomRows.size()==1);check(t.rooms.getChildCount()==1);
 t.beginRoomRows();t.roomCoverCard("room","a","same",false);LinearLayout ephemeral=t.card(t.rooms);t.desiredRoomRows.add(ephemeral);t.reconcileRoomRows();
 t.beginRoomRows();t.roomCoverCard("room","a","same",false);t.reconcileRoomRows();check(ephemeral.detaches==1);check(t.rooms.getChildCount()==1);
 t.beginRoomRows();t.roomCoverCard("room","a","same",false);t.roomCoverCard("room","a","same",false);t.reconcileRoomRows();check(t.rooms.getChildCount()==2);check(t.roomRows.size()==2);
 for(int i=0;i<300;i++){t.beginRoomRows();t.roomCoverCard("room","page-"+i,"snes",false);t.reconcileRoomRows();check(t.roomRows.size()==1);check(t.rooms.getChildCount()==1);}
 RoomTest async=new RoomTest();async.artwork.delayed=true;async.beginRoomRows();async.roomCoverCard("room","old","one",false);async.reconcileRoomRows();RoomRow removed=async.roomRows.values().iterator().next();
 for(int i=0;i<40;i++){async.beginRoomRows();async.roomCoverCard("room","old","one",false);async.reconcileRoomRows();}check(async.artwork.requests==1);
 async.beginRoomRows();async.roomCoverCard("room","new","two",false);async.reconcileRoomRows();RoomRow newer=async.roomRows.values().iterator().next();
 async.artwork.pending.get(0).complete(async.artwork.image);check(removed.display.bitmap==null);check(newer.display.bitmap==null);
 async.artwork.pending.get(1).complete(null);async.beginRoomRows();async.roomCoverCard("room","new","two",false);async.reconcileRoomRows();check(async.artwork.requests==3);
 async.artwork.pending.get(2).complete(async.artwork.image);async.beginRoomRows();async.roomCoverCard("room","new","two",false);async.reconcileRoomRows();check(async.artwork.requests==3);check(newer.display.bitmap==async.artwork.image);
 async.clearRoomRows();check(async.roomRows.isEmpty());check(async.rooms.getChildCount()==0);check(newer.display.bitmap==null);check(newer.display.surface.detaches==1);
 check(!roomRowKey("room","a:b","c").equals(roomRowKey("room","a","b:c")));
 System.out.println("PASS roomReuse="+checks);
}
'''

GPU_STUBS = r'''
static int checks;static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
static final GpuLifecycle GPU_LIFECYCLE=new GpuLifecycle();
static class Handler {final Deque<Runnable> tasks=new ArrayDeque<>();boolean accepting=true;boolean post(Runnable r){if(!accepting)return false;tasks.add(r);return true;}void drain(){while(!tasks.isEmpty())tasks.remove().run();}}
static class Source {int releases;void release(){releases++;}}
static class ThreadHandle {int quits;void quitSafely(){quits++;}}
static class Worker {
 volatile Handler handler=new Handler();final ConcurrentLinkedQueue<Runnable> startup=new ConcurrentLinkedQueue<>();final Source source=new Source();final ThreadHandle thread=new ThreadHandle();
 volatile boolean closed,failed,preparing=true,enabled=true;int inits,releases;Runnable compiler=()->{};
 void init(){inits++;compiler.run();}
 void releaseGraphics(){releases++;preparing=false;}
'''

GPU_TEST = r'''
public static void main(String[] args)throws Exception {
 GpuLifecycle life=new GpuLifecycle();AtomicInteger compiled=new AtomicInteger();
 check(!life.initialize(()->false,compiled::incrementAndGet));check(compiled.get()==0);
 life.reserveRelease();check(!life.initialize(()->true,compiled::incrementAndGet));check(compiled.get()==0);life.release(()->{});
 check(life.initialize(()->true,compiled::incrementAndGet));check(compiled.get()==1);
 life.reserveRelease();life.reserveRelease();life.release(()->{});check(!life.initialize(()->true,compiled::incrementAndGet));life.release(()->{});check(life.initialize(()->true,compiled::incrementAndGet));
 life.reserveRelease();try{life.release(()->{throw new IllegalStateException("stub release failure");});throw new AssertionError();}catch(IllegalStateException expected){}check(life.initialize(()->true,compiled::incrementAndGet));
 life.reserveRelease();life.cancelRelease();check(life.initialize(()->true,compiled::incrementAndGet));
 AtomicInteger simultaneous=new AtomicInteger(),maximum=new AtomicInteger(),runs=new AtomicInteger();ExecutorService pool=Executors.newFixedThreadPool(8);List<Future<?>> work=new ArrayList<>();
 for(int i=0;i<8;i++)work.add(pool.submit(()->{for(int j=0;j<50;j++)life.initialize(()->true,()->{int active=simultaneous.incrementAndGet();maximum.accumulateAndGet(active,Math::max);runs.incrementAndGet();try{Thread.sleep(1);}catch(InterruptedException e){throw new RuntimeException(e);}finally{simultaneous.decrementAndGet();}});}));
 for(Future<?> f:work)f.get(10,TimeUnit.SECONDS);pool.shutdown();check(maximum.get()==1);check(runs.get()==400);
 Worker one=new Worker();one.setEnabled(false);one.setEnabled(true);check(one.preparing);check(!one.initialize());check(one.inits==0);one.handler.drain();check(one.initialize());check(one.inits==1);check(!one.preparing);
 one.close();one.close();check(one.closed);check(!one.initialize());check(one.source.releases==0);one.handler.drain();check(one.source.releases==1);check(one.thread.quits==1);check(one.releases==2);one.setEnabled(false);check(one.handler.tasks.isEmpty());
 Worker old=new Worker(),fresh=new Worker();old.close();check(!fresh.initialize());old.handler.drain();check(fresh.initialize());check(fresh.inits==1);
 Worker failing=new Worker();failing.compiler=()->{throw new IllegalStateException("stub compile failure");};try{failing.initialize();throw new AssertionError();}catch(IllegalStateException expected){}check(failing.releases==1);check(new Worker().initialize());
 Worker rejected=new Worker();rejected.handler.accepting=false;rejected.close();check(new Worker().initialize());
 Worker bootstrap=new Worker();bootstrap.handler=null;AtomicInteger delivered=new AtomicInteger();bootstrap.postWorker(delivered::incrementAndGet);bootstrap.postWorker(delivered::incrementAndGet);check(delivered.get()==0);bootstrap.handler=new Handler();bootstrap.drainStartup();check(delivered.get()==2);check(bootstrap.startup.isEmpty());bootstrap.postWorker(delivered::incrementAndGet);check(delivered.get()==2);bootstrap.handler.drain();check(delivered.get()==3);
 Worker closedBeforeReady=new Worker();closedBeforeReady.handler=null;closedBeforeReady.close();check(closedBeforeReady.closed);check(closedBeforeReady.source.releases==0);check(!new Worker().initialize());closedBeforeReady.handler=new Handler();closedBeforeReady.drainStartup();check(closedBeforeReady.source.releases==1);check(closedBeforeReady.thread.quits==1);check(new Worker().initialize());
 CountDownLatch inside=new CountDownLatch(1),finish=new CountDownLatch(1);AtomicBoolean alive=new AtomicBoolean(true);GpuLifecycle inFlight=new GpuLifecycle();ExecutorService single=Executors.newSingleThreadExecutor();
 Future<Boolean> ready=single.submit(()->inFlight.initialize(alive::get,()->{inside.countDown();try{finish.await(5,TimeUnit.SECONDS);}catch(InterruptedException e){throw new RuntimeException(e);}}));
 check(inside.await(5,TimeUnit.SECONDS));inFlight.reserveRelease();alive.set(false);finish.countDown();check(!ready.get(5,TimeUnit.SECONDS));check(!inFlight.initialize(()->true,compiled::incrementAndGet));inFlight.release(()->{});check(inFlight.initialize(()->true,compiled::incrementAndGet));single.shutdown();
 System.out.println("PASS gpuLifecycle="+checks+" serializedInitRuns="+runs.get());
}
'''

EGL_STUBS = r'''
static int checks;static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
static class EGL14 {
 static final Object EGL_NO_DISPLAY=new Object(),EGL_NO_CONTEXT=new Object(),EGL_NO_SURFACE=new Object(),EGL_DEFAULT_DISPLAY=new Object(),READY=new Object();
 static boolean success;static int initialized,terminated,destroyedSurfaces,destroyedContexts,releasedThreads;
 static Object eglGetDisplay(Object d){return READY;}static boolean eglInitialize(Object d,int[] a,int b,int[] c,int e){if(success)initialized++;return success;}
 static void eglMakeCurrent(Object a,Object b,Object c,Object d){}static void eglDestroySurface(Object a,Object b){destroyedSurfaces++;}static void eglDestroyContext(Object a,Object b){destroyedContexts++;}static void eglReleaseThread(){releasedThreads++;}static void eglTerminate(Object d){terminated++;}
}
static class GLES20 {static int deletes;static void glDeleteProgram(int p){deletes++;}static void glDeleteTextures(int n,int[] p,int o){deletes++;}}
static class Surface {int releases;void release(){releases++;}}
Object display=EGL14.EGL_NO_DISPLAY,context=EGL14.EGL_NO_CONTEXT,window=EGL14.EGL_NO_SURFACE,uploaded;boolean displayInitialized,preparing;Surface surface;int program,tex,fieldReleases;
void checkOpen(){}void releaseFieldCache(){fieldReleases++;}
'''

EGL_TEST = r'''
public static void main(String[] args){
 EglTest w=new EglTest();w.releaseGraphics();check(EGL14.terminated==0);check(w.fieldReleases==0);
 EGL14.success=false;try{w.acquireDisplay();throw new AssertionError();}catch(IllegalStateException expected){}w.releaseGraphics();check(EGL14.initialized==0);check(EGL14.terminated==0);check(w.fieldReleases==0);check(!w.displayInitialized);
 for(int i=0;i<200;i++){EGL14.success=true;w.acquireDisplay();w.context=new Object();w.window=new Object();Surface surface=new Surface();w.surface=surface;w.program=4;w.tex=5;w.releaseGraphics();check(EGL14.initialized==i+1);check(EGL14.terminated==i+1);check(surface.releases==1);check(!w.displayInitialized);check(w.display==EGL14.EGL_NO_DISPLAY);w.releaseGraphics();check(EGL14.terminated==i+1);}
 check(EGL14.destroyedContexts==200);check(EGL14.destroyedSurfaces==200);check(EGL14.releasedThreads==200);check(w.fieldReleases==200);check(GLES20.deletes==400);
 System.out.println("PASS eglBalance="+checks);
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, default=ROOT / 'evidence/room-gpu-reuse-r121.json')
    args = parser.parse_args()
    jdk = args.jdk / 'bin' if (args.jdk / 'bin/javac.exe').is_file() else args.jdk
    rooms = (JAVA / 'StationRoomsActivity.java').read_text(encoding='utf-8')
    gpu = (JAVA / 'StationOnlineCoverView.java').read_text(encoding='utf-8')
    baseline = (BASE / 'StationRoomsActivity.java').read_text(encoding='utf-8')
    room_class = block(rooms, rooms.index('    private static final class RoomRow')).strip()
    room_fields = '\n'.join(x for x in rooms.splitlines() if any((' ' + name + '=') in x for name in ('roomRows', 'desiredRoomRows', 'usedRoomRows')))
    room_methods = '\n'.join(method(rooms, x) for x in ('roomRowKey', 'beginRoomRows', 'roomCoverCard', 'reconcileRoomRows', 'clearRoomRows'))
    gate = block(gpu, gpu.index('    private static final class GpuLifecycle')).strip()
    worker = block(gpu, gpu.index('    private final class Worker'))
    worker_methods = '\n'.join(method(worker, x) for x in ('drainStartup','postWorker','setEnabled', 'queueRelease', 'initialize', 'close'))
    init = method(worker,'init')
    display_init = init[init.index('{')+1:init.index('            int[] config=')]
    headers = 'import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;import java.util.function.*;\n'
    programs = {'RoomTest': headers + 'public class RoomTest {\n' + ROOM_STUBS + room_class + '\n' + room_fields + '\n' + room_methods + ROOM_TEST + '\n}',
                'GpuTest': headers + 'public class GpuTest {\n' + gate + '\n' + GPU_STUBS + worker_methods + '\n}\n' + GPU_TEST + '\n}',
                'EglTest': headers+'public class EglTest {\n'+EGL_STUBS+'\nvoid acquireDisplay(){'+display_init+'}\n'+method(worker,'releaseGraphics')+EGL_TEST+'\n}'}
    outputs = []
    with tempfile.TemporaryDirectory(prefix='station-room-reuse-r121-') as out:
        out = Path(out)
        for name, source in programs.items():
            path = out / (name + '.java'); path.write_text(source, encoding='utf-8')
            run = subprocess.run([str(jdk / 'javac.exe'), '--release', '8', '-d', str(out), str(path)], capture_output=True, text=True)
            if run.returncode: raise AssertionError(run.stderr)
            outputs.append(subprocess.check_output([str(jdk / 'java.exe'), '-cp', str(out), name], text=True).strip())
    guards = []
    def guard(name, value):
        if not value: raise AssertionError(name)
        guards.append(name)
    contracts = ('createRoom','prepareRoom','join','joinConfirmed','startDialog','launch','action','command','deliver','beginMultiplayerDiscovery','pageRooms','pagePeers','prepareLocal','verifyPreparedRoom')
    unchanged = {}
    for name in contracts:
        old, new = methods(baseline, name), methods(rooms, name)
        if not old and name in ('prepareLocal','verifyPreparedRoom'): continue
        guard('contract method present: ' + name, bool(old) and bool(new))
        guard('contract method unchanged: ' + name, old == new)
        unchanged[name] = hashlib.sha256('\n'.join(new).encode()).hexdigest()
    guard('command callbacks unchanged', Counter(re.findall(r'->(?:command|socialAction)\([^;\n]+', baseline)) == Counter(re.findall(r'->(?:command|socialAction)\([^;\n]+', rooms)))
    guard('paint does not detach retained cover roots', 'rooms.removeAllViews()' not in method(rooms, 'paint') and 'ownRoomCard=new ' not in method(rooms, 'paint'))
    guard('reconcile reorders without remove/add retained roots', 'rooms.bringChildToFront(row)' in method(rooms,'reconcileRoomRows') and 'rooms.addView' not in method(rooms,'reconcileRoomRows'))
    guard('closed surfaces stay worker owned', 'onSurfaceTextureDestroyed' in gpu and 'return false;' in method(gpu, 'onSurfaceTextureDestroyed') and 'source.release();thread.quitSafely();' in method(gpu,'queueRelease'))
    guard('no EGL lifecycle gate in normal draw', 'synchronized' not in method(gpu,'draw') and 'if(program==0&&!initialize())return;' in method(gpu,'draw'))
    guard('UI release reservation is atomic only', 'synchronized' not in method(gpu,'queueRelease') and 'GPU_LIFECYCLE.reserveRelease();' in method(gpu,'queueRelease'))
    guard('late initialization cancellation checked before upload', 'if(closed||!enabled||image.isRecycled())return;' in method(gpu,'draw'))
    guard('shader cancellation does not trigger fallback compiler', gpu.count('instanceof CancellationException') == 2)
    guard('worker bootstrap does not wait for Looper on UI', 'thread.getLooper()' not in worker and 'new Handler(Looper.myLooper());drainStartup();' in worker)
    guard('terminate only follows successful initialize', '&&displayInitialized)' in method(worker,'releaseGraphics') and 'displayInitialized=true;' in display_init and 'displayInitialized=false;' in method(worker,'releaseGraphics'))
    guard('existing cadence retained', 'postDelayed(frame,34)' in gpu)
    guard('existing shader source retained', 'prefix+StationCoverLightingShader.SOURCE' in gpu)
    for name in ('profile','visible','schedule','motion','stepLightField','drawQuad','configure','takeField','rememberField'):
        guard('render policy unchanged: ' + name, method(gpu,name) == method((BASE/'StationOnlineCoverView.java').read_text(encoding='utf-8'),name))
    evidence = {'revision':'R121','scope':'real Java bodies extracted unchanged into host harnesses; stub views/handlers/GL cleanup; no Android or gameplay', 'status':'PASS', 'results':outputs, 'sourceGuardChecks':len(guards), 'guards':guards, 'contractMethodSha256':unchanged, 'sourceSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (JAVA/'StationRoomsActivity.java',JAVA/'StationOnlineCoverView.java')}, 'recipeSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'limitations':['No GPU shader or Android driver executed','No physical ANR or gameplay validation','Initial compile can still be expensive on an OEM driver; init concurrency and redundant surface creation are controlled','Vendor native mutex ownership and unique ANR cause remain unproven']}
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for output in outputs: print(output)
    print('PASS sourceGuards='+str(len(guards)))


if __name__ == '__main__': main()
