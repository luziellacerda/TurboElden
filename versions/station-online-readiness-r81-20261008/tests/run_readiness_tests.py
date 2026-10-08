"""Exercise the actual readiness methods with controlled API and UI callbacks."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent.parent
WORK=Path(r'E:\ESTUDO APK\work\station-online-readiness-r81-20261008')
SRC=ROOT/'java/netplay-src/org/emulationstation/frontend/netplay'
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
JSON=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
def extract(s,start):
    begin=s.index(start);level=0
    for i in range(s.index('{',begin),len(s)):
        if s[i]=='{':level+=1
        elif s[i]=='}':
            level-=1
            if level==0:return s[begin:i+1]
    raise ValueError(start)
def execute(name,source):
    work=WORK/'readiness-tests'/name;work.mkdir(parents=True,exist_ok=True)
    path=work/(name+'.java');path.write_text(source,'utf8')
    cp=str(work)+';'+str(JSON)
    for label,cmd in [('compile',[JDK/'javac.exe','--release','8','-encoding','UTF-8','-cp',JSON,'-d',work,path]),('run',[JDK/'java.exe','-cp',cp,name])]:
        r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',timeout=35)
        (work/(label+'.log')).write_text(r.stdout+r.stderr,'utf8')
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    return r.stdout.strip()

client=(SRC/'StationOnlineClient.java').read_text('utf8')
methods='\n'.join(extract(client,s) for s in ['JSONObject profileSnapshot(', 'void discoverMultiplayer(', 'static String message('])
probe='''import org.json.*;import java.io.*;
class StationApi {static class Cancellation{} static class Failure extends IOException{int status;String code;Failure(int s,String c){status=s;code=c;}}}
class StationOnlineGame {static class Unavailable extends IOException{Unavailable(String s){super(s);}}}
class Client {Exception problem;JSONObject last;JSONObject command(String a)throws Exception{return new JSONObject().put("action",a);}
JSONObject multiplayer(JSONObject request,StationApi.Cancellation cancel)throws Exception{last=request;if(problem!=null)throw problem;return new JSONObject().put("ok",true);}
'''+methods+'''}
public class ReadinessProbe {static int checks;static void ok(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
public static void main(String[] ignored)throws Exception{
 Client c=new Client();StationApi.Cancellation cancel=new StationApi.Cancellation();
 for(int status:new int[]{404,503,401,403,429,500})for(String code:new String[]{"HTTP_ERROR","STATION_MULTIPLAYER_DISABLED"}){
  c.problem=new StationApi.Failure(status,code);
  try{c.discoverMultiplayer(cancel);throw new AssertionError();}catch(Exception e){ok(e==c.problem);}
  try{c.profileSnapshot("exact-item",cancel);throw new AssertionError();}catch(Exception e){ok(e==c.problem);}
  String text=Client.message(c.problem);ok(text.contains("ativação")==code.equals("STATION_MULTIPLAYER_DISABLED"));
 }
 c.problem=new IOException("private details must never be shown");ok(!Client.message(c.problem).contains("private"));
 c.problem=null;c.discoverMultiplayer(cancel);ok(c.last.getString("action").equals("capabilities"));
 ok(c.profileSnapshot("exact-item",cancel).getBoolean("ok"));ok(c.last.getString("itemId").equals("exact-item"));
 ok(Client.message(new StationApi.Failure(503,"HTTP_ERROR")).contains("no momento"));
 ok(Client.message(new StationApi.Failure(404,"HTTP_ERROR")).contains("não encontrou"));
 ok(!Client.message(new StationApi.Failure(503,"STATION_MULTIPLAYER_GAME_UNCLASSIFIED")).contains("ativação"));
 System.out.println("PASS "+checks+" exact error/consultation checks");}}
'''
results={'errors':execute('ReadinessProbe',probe)}

activity=(SRC/'StationRoomsActivity.java').read_text('utf8')
method=extract(activity,'    private void beginMultiplayerDiscovery(')
harness='''import java.util.*;import java.util.concurrent.*;import java.io.*;
class StationApi {static final class Cancellation {boolean stopped;void cancel(){stopped=true;}boolean cancelled(){return stopped;}void check()throws IOException{if(stopped)throw new IOException("cancelled");}}}
class StationOnlineClient {boolean multiplayerEnabled;int scenario;CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);StationOnlineClient(int s){scenario=s;}
 static String message(Throwable e){return e.getMessage();}
 void discoverMultiplayer(StationApi.Cancellation c)throws Exception{entered.countDown();if(scenario>=4)release.await();if(scenario==1)throw new IOException("503 temporary");if(scenario==2)throw new IOException("disabled explicit");if(scenario==3)throw new IOException("404 absent");if(scenario==5)c.cancel();c.check();multiplayerEnabled=true;}
 Object compose(Object ignored){return new Object();}Object pollMultiplayer(StationApi.Cancellation c){return new Object();}}
public class DiscoveryProbe {
 boolean active=true,busy,creating;int epoch=1;StationOnlineClient client;String notice="unset";int delivered,failures,hero;
 Set<StationApi.Cancellation> requests=Collections.synchronizedSet(new HashSet<>());ScheduledExecutorService multiplayerEvents=Executors.newSingleThreadScheduledExecutor();ScheduledFuture<?> multiplayerPolling;
 CountDownLatch painted=new CountDownLatch(1);void runOnUiThread(Runnable r){r.run();}void showCreateMessage(String s,boolean error){notice=s;}void loadHero(){hero++;painted.countDown();}void deliver(Object o,int g){if(active&&g==epoch)delivered++;}void recordFailure(Throwable error){failures++;}
'''+method+'''
 static int checks;static void ok(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
 static void awaitDone(DiscoveryProbe p)throws Exception{p.multiplayerEvents.submit(()->{}).get(2,TimeUnit.SECONDS);}
 public static void main(String[] args)throws Exception{
  for(int scenario=0;scenario<=5;scenario++){DiscoveryProbe p=new DiscoveryProbe();p.client=new StationOnlineClient(scenario);
   try{p.beginMultiplayerDiscovery(p.client,1);ok(p.client.entered.await(2,TimeUnit.SECONDS));
    if(scenario==4){p.epoch++;p.client.release.countDown();awaitDone(p);ok(p.hero==0&&p.delivered==0);}
    else if(scenario==5){p.client.release.countDown();awaitDone(p);ok(p.hero==0&&p.failures==0);}
    else{ok(p.painted.await(2,TimeUnit.SECONDS));awaitDone(p);ok(p.hero==1);ok(p.delivered==(scenario==0?1:0));ok(p.failures==(scenario==0?0:1));ok(p.notice.equals(new String[]{"","503 temporary","disabled explicit","404 absent"}[scenario]));}
    ok(p.requests.isEmpty());
   }finally{p.multiplayerEvents.shutdownNow();}}
  DiscoveryProbe stale=new DiscoveryProbe();stale.client=new StationOnlineClient(0);
  try{stale.beginMultiplayerDiscovery(stale.client,0);ok(stale.multiplayerPolling==null);stale.active=false;stale.beginMultiplayerDiscovery(stale.client,1);ok(stale.multiplayerPolling==null);}
  finally{stale.multiplayerEvents.shutdownNow();}
  System.out.println("PASS "+checks+" discovery lifecycle checks; controlled API/UI fixtures");
 }
}
'''
results['discovery']=execute('DiscoveryProbe',harness)
guards=[
 'deliver(current,generation);beginMultiplayerDiscovery' in activity,
 'state.get()==null' not in extract(activity,'    private void loadHero(){'),
 'stopMultiplayerPoll();cancelAll();' in activity,
 'StationOnlineGame.classifications(this,client,target,check)' in activity,
 'if(info.singlePlayerConfirmed)counts.add(1)' in activity,
 'StationOnlineGame.profiles(this,client,item,cancel)' in activity,
 'if(!p.contentSha256.equals(hash))' in (SRC/'StationOnlineGame.java').read_text('utf8'),
 'if(!sha(core,cancel).equals(p.coreSha256)||!sha(runtime,cancel).equals(p.runtimeSha256))' in (SRC/'StationOnlineGame.java').read_text('utf8')]
assert all(guards),guards
results['staticGuards']=len(guards)
receipt={'passed':True,'results':results,'sourceHashes':{n:hashlib.sha256((SRC/n).read_bytes()).hexdigest() for n in ['StationOnlineClient.java','StationOnlineGame.java','StationRoomsActivity.java']},'scope':'Actual extracted Java methods with controlled API/UI and static integration guards; not signed HTTP, Android or gameplay.'}
(ROOT/'evidence').mkdir(exist_ok=True);(ROOT/'evidence/readiness-tests.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
print(json.dumps(results))
