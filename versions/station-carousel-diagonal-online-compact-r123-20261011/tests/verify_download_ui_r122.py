"""Host-only checks of the actual notice policy plus Java API compilation.

No Android window, telephone, file transfer, server or storage failure is simulated
as a physical validation. Generated classes/logs remain in the supplied work dir.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'java/client/src/java/org/emulationstation/frontend/station'
BASE = ROOT.parent / 'station-online-room-gpu-reuse-r121-20261011/java/client/src/java/org/emulationstation/frontend/station'


def read(path):
    return Path('\\\\?\\' + str(Path(path).resolve())).read_text(encoding='utf-8')


def block(source, marker):
    start = source.index(marker)
    opening = source.index('{', start)
    depth, quote, escaped = 0, '', False
    for i in range(opening, len(source)):
        c = source[i]
        if quote:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == quote:
                quote = ''
        elif c in ('"', "'"):
            quote = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise AssertionError('Unbalanced production Java block: ' + marker)


def digest(path):
    with Path('\\\\?\\' + str(Path(path).resolve())).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--android-jar', type=Path, required=True)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    ui, panel, frontend = (read(SOURCE / name) for name in ('StationDownloadUi.java', 'StationDownloadPanel.java', 'StationFrontend.java'))
    notice = block(ui, 'static final class Notice {')
    gate = block(ui, 'static final class SignalGate')
    guard = block(ui, 'static boolean mayPresent(')
    wide = block(panel, 'static boolean wideRows(')
    install = block(ui, 'public static synchronized void install(')
    detach = block(ui, 'private static void detachFocus(')
    harness = '''import java.lang.ref.WeakReference;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
class StationDownloadUi {static void showNext(){}}
public final class DownloadUiProbe {
 static boolean installed;
 static WeakReference<Activity> owner=new WeakReference<>(null);
 static WeakReference<View> focusView=new WeakReference<>(null);
 static ViewTreeObserver focusObserver;
 static final Object FOCUS=new Object();
 static boolean menu(Activity a){return false;}
 static void release(Activity a){}
 static class Bundle{}
 static class ViewTreeObserver {boolean alive=true;int listeners;boolean isAlive(){return alive;}void addOnWindowFocusChangeListener(Object listener){listeners++;}void removeOnWindowFocusChangeListener(Object listener){listeners=Math.max(0,listeners-1);}}
 static class View {ViewTreeObserver observer=new ViewTreeObserver();ViewTreeObserver getViewTreeObserver(){return observer;}void post(Runnable task){}}
 static class Window {View decor=new View();View getDecorView(){return decor;}}
 static class Activity {Window window=new Window();Window getWindow(){return window;}}
 static class Application {int registrations;ActivityLifecycleCallbacks callback;void registerActivityLifecycleCallbacks(ActivityLifecycleCallbacks callback){registrations++;this.callback=callback;}
  interface ActivityLifecycleCallbacks {void onActivityCreated(Activity a,Bundle b);void onActivityStarted(Activity a);void onActivityResumed(Activity a);void onActivityPaused(Activity a);void onActivityStopped(Activity a);void onActivityDestroyed(Activity a);void onActivitySaveInstanceState(Activity a,Bundle b);}
 }
 BODY
 static int checks;
 static void check(boolean value){checks++;if(!value)throw new AssertionError("check="+checks);}
 public static void main(String[] args)throws Exception{
  SignalGate gate=new SignalGate();
  for(int i=0;i<10000;i++)check(!gate.offer("busy","Jogo","Baixando",0,true));
  check(gate.offer("busy","Jogo","Falha",3,false));
  for(int i=0;i<1000;i++)check(!gate.offer("busy","Jogo","Falha",3,false));
  check(gate.offer("busy","Jogo","Na fila",0,true));
  for(int i=0;i<10000;i++)check(!gate.offer("busy","Jogo","Baixando",0,true));
  check(!gate.offer("cancel","Jogo","Cancelado",3,false));
  for(int i=0;i<1000;i++){check(gate.offer("bounded"+i,"Jogo","Falha",3,false));check(gate.known.size()<=48&&gate.slots.get()<=48);}
  check(gate.known.size()==gate.slots.get());
  final SignalGate concurrent=new SignalGate();Thread[] producers=new Thread[8];
  for(int p=0;p<8;p++){final int producer=p;producers[p]=new Thread(()->{for(int i=0;i<1000;i++){String id="producer"+producer+"-"+i;concurrent.offer(id,"Jogo","Falha",3,false);if(i%3==0)concurrent.offer(id,"Jogo","Retomando",0,true);}});producers[p].start();}
  for(Thread producer:producers)producer.join();check(concurrent.known.size()<=48);check(concurrent.known.size()==concurrent.slots.get());
  SignalGate l=new SignalGate();
  l.offer("space","Jogo","Espaço insuficiente para baixar e preparar o jogo.",3,false);
  check(l.known.size()==1);Notice first=l.next();
  for(int i=0;i<100;i++){l.offer("space","Jogo",first.message,3,false);check(l.known.size()==1);check(l.next()==first);}
  l.shown(first);check(l.next()==null);l.offer("space","Jogo",first.message,3,false);check(l.next()==null);
  l.offer("space","Jogo","Na fila",0,true);l.offer("space","Jogo",first.message,3,false);check(l.known.size()==1);
  Notice old=l.next();l.offer("space","Jogo","Outra falha",3,false);l.shown(old);check(l.next()!=null&&l.next()!=old);check(!l.current(old));
  l.offer("space","Jogo","Cancelado",3,false);check(l.next()==null&&l.known.isEmpty());
  for(int i=0;i<1000;i++){
   l.offer("job"+i,"Jogo","Falha",3,false);check(l.known.size()<=48);check(l.slots.get()<=48);
  }
  check(l.known.size()==48);check(!l.known.containsKey("job0"));
  check(l.offer("job0","Jogo","Na fila",0,true)==false);check(!l.current(first));
  check(l.offer("job0","Jogo","Falha",3,false));check(l.known.get("job0").shown.get()==false);
  l=new SignalGate();
  l.offer("done","Jogo","Falha",3,false);l.offer("done","Jogo","Instalado",1,false);check(l.next()==null);
  l.offer("gone","Jogo","Falha",3,false);l.offer("gone","Jogo","Apagado",2,false);check(l.next()==null);
  l.offer("pending","Jogo","Aguardando conexão",0,true);check(l.next()==null);
  l.offer("paused","Jogo","Pausado",0,true);check(l.next()==null);
  l.offer("cancelled","Jogo","Cancelado",3,false);check(l.next()==null);
  l.offer("", "Jogo", "Falha",3,false);l.offer(null,"Jogo","Falha",3,false);check(l.next()==null);
  l.offer("empty","Jogo",null,3,false);check(l.next()==null);
  l.offer("name","", "Falha",3,false);check(l.next().name.equals("Jogo"));
  Application app=new Application();install(app);install(app);check(app.registrations==1);
  View view=new View();ViewTreeObserver oldObserver=new ViewTreeObserver();oldObserver.alive=false;view.observer.listeners=1;focusObserver=oldObserver;focusView=new WeakReference<>(view);detachFocus();check(view.observer.listeners==0);check(focusObserver==null&&focusView.get()==null);
  ViewTreeObserver same=view.observer;same.listeners=1;focusObserver=same;focusView=new WeakReference<>(view);detachFocus();check(same.listeners==0);
  for(int mask=0;mask<64;mask++){
   boolean menu=(mask&1)!=0,finishing=(mask&2)!=0,destroyed=(mask&4)!=0,focused=(mask&8)!=0,panel=(mask&16)!=0,warning=(mask&32)!=0;
   check(mayPresent(menu,finishing,destroyed,focused,panel,warning)==(mask==9));
  }
  for(int width=240;width<=1600;width++){
   check(wideRows(width)==(width>=600));
   if(width>=320){float content=width-32-20-52-12-(wideRows(width)?220:0);check(content>=48);float action=wideRows(width)?100:(Math.min(content,248)-8)/2;check(action>=48);check(action<=120);}
  }
  System.out.println("PASS "+checks);
 }
}
'''.replace(' BODY', '\n'.join((notice, gate, guard, wide, install, detach)))
    probe = args.work / 'DownloadUiProbe.java'
    probe.write_text(harness, encoding='utf-8')
    run([args.jdk / 'javac.exe', '-encoding', 'UTF-8', '--release', '8', '-d', args.work, probe])
    output = run([args.jdk / 'java.exe', '-cp', args.work, 'DownloadUiProbe'])
    checks = int(re.search(r'PASS (\d+)', output).group(1))

    guards = []
    def check(value, label):
        assert value, label
        guards.append(label)
    preserved = {}
    for name in ('StationDownloads.java', 'StationDownloadRetry.java', 'StationApi.java', 'StationInstaller.java', 'StationCoverQueue.java'):
        check(digest(SOURCE / name) == digest(BASE / name), name + ' exact R121 bytes')
        preserved[name] = digest(SOURCE / name)
    check('StationDownloadUi.changed(id,item==null?"Jogo":item.name,message,result,active);' in frontend, 'Download callback dispatches original message and state')
    check('StationDownloadUi.install(application);' in read(SOURCE / 'StationComponentFactory.java'), 'Original factory registers observer before activity resume')
    check('WeakReference<Activity>' in ui and 'owner.clear();detachFocus();' in ui, 'Weak owner and release')
    for name in ('onActivityPaused', 'onActivityStopped', 'onActivityDestroyed'):
        check(name+'(Activity a){release(a);}' in ui, name+' closes warning')
    check('a.getClass().getName().equals("org.emulationstation.frontend.ESActivity")' in ui, 'Only carousel owns origin modal')
    check('addOnWindowFocusChangeListener(FOCUS)' in ui and 'removeOnWindowFocusChangeListener(FOCUS)' in ui, 'Focus event added and removed')
    check('decor.getViewTreeObserver()' in ui and 'current!=focusObserver&&current.isAlive()' in ui, 'Merged decor observer listener also removed')
    check('a.hasWindowFocus()' in ui and 'warning=dialog;' in ui and 'signals.shown(notice);' in ui, 'One presented modal only after valid foreground check')
    check('if(count>=48)return false;' in ui and 'slots.compareAndSet(count,count+1)' in ui, 'Concurrent admission capped at 48 failures')
    check('NoticeLedger' not in ui and 'signals.current(notice)' in ui, 'Single identity-based source of pending/deduplicated failures')
    check('postDelayed' not in ui and 'ScheduledExecutor' not in ui, 'No idle timer added to warning')
    check('if(!signals.offer(id,name,message,result,active))return;' in ui, 'Ordinary progress does not enqueue MAIN work')
    login = read(SOURCE.parent / 'auth/LoginActivity.java')
    check(login.index('StationDownloadUi.install(getApplication())') < login.index('if (StationLogin.ready() && storageAllowed())'), 'API26/27 fallback installs before Login shortcut')
    check(panel.count('main.post(tick)') == 1 and panel.count('main.postDelayed(this,1000)') == 1, 'Single existing one-second panel refresh chain')
    check('main.post(StationDownloadPanel.this::refreshRows)' in panel and 'main.post(tick);' not in block(panel, 'private void confirmCancel('), 'Cancel refresh does not create another timer')
    check('if(confirmation!=null){confirmation.dismiss();confirmation=null;}' in panel, 'Nested confirmation released with center')
    check('controls.execute(()->{StationFrontend.cancel(e.id);' in panel, 'Cancel remains on control worker')
    check('if(retry)StationFrontend.resumeDownload(e.id);else StationFrontend.pauseDownload(e.id);' in panel, 'Original pause/resume routing')
    check('r.pause.setEnabled(e.state!=StationDownloads.State.PREPARING)' in panel, 'Preparing pause restriction retained')
    check('dp(48)' in panel and 'button.setMinHeight(dp(a,48))' in ui, 'Touch targets at least 48dp')
    check('LinearLayout.HORIZONTAL' in panel and 'LinearLayout.HORIZONTAL' in ui, 'Actions remain side by side')
    check('dp(248)' in panel and 'dp(208)' in panel, 'Row action area capped instead of stretching across landscape')
    check('name=text("",14' in panel and 'status=text("",13' in panel, 'Compact 14/13sp item typography')
    check('Math.min(dp(a,420)' in ui and 'dp(a,32)' in ui, 'Confirmation width bounded to available viewport')
    check('android.widget.ScrollView' in ui and 'heightPixels-dp(a,48)' in ui and 'new LinearLayout.LayoutParams(-1,0,1)' in ui, 'Long message scrolls inside bounded modal with actions outside scroll')
    check('"Não foi possível concluir"' in ui, 'Terminal uninstall failure is not mislabeled as downloading')
    check(block(panel, 'private void loadCover(') == block(read(BASE / 'StationDownloadPanel.java'), 'private void loadCover('), 'Existing authenticated cover queue and decode preserved')
    check(block(panel, 'private void deliverCover(') == block(read(BASE / 'StationDownloadPanel.java'), 'private void deliverCover('), 'Cover cancellation/publication/cache preserved')

    # Compile actual client sources against Android API34, without D8 or APK work.
    sources = sorted((ROOT / 'java/client/src/java').rglob('*.java'))
    classes = args.work / 'client-classes'
    classes.mkdir(exist_ok=True)
    arguments = ['-encoding', 'UTF-8', '--release', '8', '-proc:none', '-cp', str(args.android_jar), '-d', str(classes)] + [str(p) for p in sources]
    response = args.work / 'client.args'
    response.write_text('\n'.join('"'+value.replace('\\', '/')+'"' for value in arguments), encoding='utf-8')
    log = run([args.jdk / 'javac.exe', '@'+str(response)])
    (args.work / 'client-javac.log').write_text(log, encoding='utf-8')
    receipt = {
        'revision': 'R122', 'status': 'PASS', 'scope': 'Host execution of exact production SignalGate, mayPresent, wideRows, install and detachFocus with minimal lifecycle/API stubs; source guards and actual client Java compilation against Android34. No Android window, transfer, telephone, gameplay or physical validation.',
        'policyChecks': checks, 'sourceGuards': len(guards), 'sourceGuardNames': guards,
        'clientJavaSources': len(sources), 'preservedDownloadSources': preserved,
        'changedSourceSha256': {name: digest(SOURCE / name) for name in ('StationDownloadUi.java','StationDownloadPanel.java','StationFrontend.java','StationComponentFactory.java')},
        'testSha256': digest(__file__),
    }
    evidence = ROOT / 'evidence/download-ui-r122.json'
    evidence.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('status','policyChecks','sourceGuards','clientJavaSources')}))


if __name__ == '__main__':
    main()
