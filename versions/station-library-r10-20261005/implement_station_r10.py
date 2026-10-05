from pathlib import Path
import shutil
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
S=R/'station/src/java/org/emulationstation/frontend/station'
repo=Path('work/TurboElden-git')
def edit(name,old,new):
 p=S/name;s=p.read_text('utf-8');assert old in s,name;p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
edit('StationDiagnostics.java','if(path.equals("/v1/station/catalog"))','if(path.equals("/v1/station/catalog")||path.equals("/v1/station/catalog?metadata=1"))')
edit('StationCoordinator.java','authorized=session;library=result;return result;\n        }catch(StationApi.Failure','cancel.check();authorized=session;library=result;return result;\n        }catch(StationApi.Failure')
edit('StationCatalog.java','row.optJSONObject("metadata")','metadata(row)')
edit('StationCatalog.java','    private static String metadataText(','''    private static JSONObject metadata(JSONObject row)throws IOException,JSONException {
        if(!row.has("metadata"))return null;
        Object value=row.get("metadata");
        if(!(value instanceof JSONObject))throw new IOException("Invalid catalog metadata");
        return (JSONObject)value;
    }
    private static String metadataText(''')
(S/'StationCatalogPoll.java').write_text('''package org.emulationstation.frontend.station;

/** Generation gate for foreground-only refresh. No network operation runs under this lock. */
final class StationCatalogPoll {
 static final class Ticket {
  final long generation;final StationApi.Cancellation cancel=new StationApi.Cancellation();
  Ticket(long generation){this.generation=generation;}
 }
 private long generation;private boolean enabled;private Ticket active;
 synchronized void resume(){if(!enabled){enabled=true;generation++;}}
 void pause(){Ticket old;synchronized(this){enabled=false;generation++;old=active;}if(old!=null)old.cancel.cancel();}
 synchronized Ticket begin(){if(!enabled||active!=null)return null;active=new Ticket(generation);return active;}
 synchronized boolean current(Ticket ticket){return enabled&&active==ticket&&ticket.generation==generation&&!ticket.cancel.cancelled();}
 synchronized void finish(Ticket ticket){if(active==ticket)active=null;}
 static boolean changed(long oldRevision,String oldName,long newRevision,String newName){return oldRevision!=newRevision||!oldName.equals(newName);}
}
''',encoding='utf-8')
p=S/'StationFrontend.java';s=p.read_text('utf-8');a=s.index(' private static final java.util.concurrent.atomic.AtomicBoolean automaticRefresh=');b=s.index(' public static void refresh(){',a)
s=s[:a]+''' private static final StationCatalogPoll automaticRefresh=new StationCatalogPoll();
 private static boolean mayPoll(){return foreground&&configured&&authorized()&&activeCount()==0&&images.activeCount()==0;}
 private static synchronized void startCatalogPoll(){
  if(catalogPollTask!=null||!foreground||!configured)return;
  automaticRefresh.resume();
  catalogPollTask=catalogPoll.scheduleWithFixedDelay(()->{
   if(!mayPoll())return;
   StationCatalogPoll.Ticket ticket=automaticRefresh.begin();if(ticket==null)return;
   try{commands.execute(()->{
    try{if(!mayPoll()||!automaticRefresh.current(ticket))return;
     StationAndroid app=StationAndroid.current();if(app==null)return;
     StationCoordinator.Library old=app.coordinator.current();
     StationCoordinator.Library next=app.coordinator.refresh(ticket.cancel);
     if(foreground&&automaticRefresh.current(ticket)&&(old==null||StationCatalogPoll.changed(old.catalog.revision,old.displayName,next.catalog.revision,next.displayName)))publishCurrent(app);
    }catch(Exception failure){if(foreground&&automaticRefresh.current(ticket)&&failure instanceof StationApi.Failure&&((StationApi.Failure)failure).sessionDenied())publishError(utf8("Entre novamente para atualizar o catálogo."));}
    finally{automaticRefresh.finish(ticket);}
   });}catch(RejectedExecutionException busy){automaticRefresh.finish(ticket);}
  },5,60,TimeUnit.SECONDS);
 }
 private static synchronized void stopCatalogPoll(){
  if(catalogPollTask!=null){catalogPollTask.cancel(false);catalogPollTask=null;}
  automaticRefresh.pause();
 }
'''+s[b:];p.write_text(s,encoding='utf-8',newline='\n')
for name in ['StationAutomaticCatalogTest.java','StationApiTest.java']:
 shutil.copyfile(repo/'versions/station-online-20261004/station/tests'/name,R/'station/tests'/name)
p=R/'station/run_tests.py';s=p.read_text('utf-8');s=s.replace("('StationFilesTest','file-test')","('StationCatalogPollTest','poll-test'),('StationAutomaticCatalogTest','automatic-test'),('StationFoldersTest','folders-test'),('StationFilesTest','file-test')");p.write_text(s,encoding='utf-8')
print('Applied lifecycle cancellation, cover priority, diagnostic classification and strict metadata validation')
