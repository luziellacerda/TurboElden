from pathlib import Path
import shutil
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
B=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
for sub in ('station/src','station/tests','netplay/src','manifest-project'):
    if not (R/sub).exists():shutil.copytree(B/sub,R/sub)
for sub in ('station/run_tests.py','station/build_module.py','netplay/build_netplay.py'):
    if not (R/sub).exists():shutil.copy2(B/sub,R/sub)
S=R/'station/src/java/org/emulationstation/frontend/station'
def patch(name,old,new):
    p=S/name;t=p.read_text('utf-8');assert t.count(old)==1,(name,t.count(old));p.write_text(t.replace(old,new),'utf-8',newline='\n')
patch('StationHttp.java','|| path.equals("/v1/station/sessions") || path.equals("/v1/station/downloads/authorize");',
'''|| path.equals("/v1/station/sessions") || path.equals("/v1/station/downloads/authorize")
            || path.equals("/v1/station/online/command") || path.equals("/v1/station/online/events");''')
patch('StationApi.java','    public String profile(Session session,Cancellation cancel) throws Exception {',
'''    /** Signed, request-bound response; credentials remain private to this transport. */
    public JSONObject online(Session session,boolean events,JSONObject request,Cancellation cancel)throws Exception {
        String requestId=string(request,"requestId");
        if(!requestId.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))throw new IOException("Invalid online request ID");
        byte[] body=request.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
        if(body.length>8192)throw new IOException("Online request too large");
        JSONObject result=signed("POST",events?"online/events":"online/command",body,session,
            "TurboRamaStationAndroid/online/v1",262144,cancel);
        equal(result,"requestId",requestId);
        JSONObject snapshot=result.getJSONObject("snapshot");
        if(snapshot.getInt("schemaVersion")!=1)throw new IOException("Unsupported online snapshot");
        return snapshot;
    }

    public String profile(Session session,Cancellation cancel) throws Exception {''')
patch('StationFrontend.java',' public static int activeCount(){',
''' /** Exact receipt lookup for a selected Station ID, no arbitrary folder scan. */
 public static String installedPathForItem(String itemId)throws Exception {
  if(android.os.Looper.myLooper()==android.os.Looper.getMainLooper())throw new IllegalStateException("Use an IO worker");
  StationAndroid app=StationAndroid.current();StationDownloads current=downloads;
  if(app==null||current==null)throw new IOException("Catálogo não preparado");
  StationCoordinator.Library library=app.coordinator.current();
  StationCatalog.Item item=library==null?null:library.catalog.find(itemId);
  if(item==null)throw new IOException("Jogo não está no catálogo atual");
  StationInstaller.Installed installed=current.find(item);
  if(installed==null)throw new IOException("Baixe o jogo antes de criar ou entrar em uma sala");
  return installed.launchPath.toString();
 }
 public static int activeCount(){''')
print('Created isolated Station online sources; R5 payload remains unchanged')
