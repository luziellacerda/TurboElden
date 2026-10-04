package org.emulationstation.frontend.station;
import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/** JNI entry points are commands, not URL interceptors. Network work stays off the SDL thread. */
public final class StationFrontend {
 static {System.loadLibrary("station_frontend");}
 private static final ThreadPoolExecutor commands=pool("Station-catalog",8);
 private static final StationCoverQueue images=new StationCoverQueue((itemId,cancel)->{
  StationAndroid app=StationAndroid.current();if(app==null)throw new IOException("Station not initialized");return app.coordinator.cover(itemId,cancel);
 },(itemId,path,result,retryMillis)->publishCoverResult(itemId,path==null?new byte[0]:utf8(path.toString()),result,retryMillis));
 private static volatile StationDownloads downloads;private static volatile boolean foreground=true,configured;
 private static volatile String requestedStorageRoot;
 private static String platformWarning="";
 private static ThreadPoolExecutor pool(String name,int capacity){return new ThreadPoolExecutor(0,1,10,TimeUnit.SECONDS,new ArrayBlockingQueue<Runnable>(capacity),r->{Thread t=new Thread(r,name);t.setDaemon(true);return t;});}
 private StationFrontend(){}
 public static boolean authorized(){StationAndroid app=StationAndroid.current();return app!=null&&app.coordinator.ready();}
 public static void requestLogin(){StationAndroid app=StationAndroid.current();if(app!=null){
  android.content.Intent intent=new android.content.Intent(app.context,org.emulationstation.frontend.auth.LoginActivity.class);
  intent.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK|android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP);app.context.startActivity(intent);
 }}
 public static void configure(String romsRoot) {
  requestedStorageRoot=romsRoot;
  synchronized(StationFrontend.class){if(configured)return;configured=true;}
  if(!execute(()->{
   try {
    android.util.Log.i("StationFrontend","Configuring catalog");
    StationAndroid app=StationAndroid.current();if(app==null)throw new IOException("Entre no aplicativo para carregar o catálogo.");
    prepareStorage(app,romsRoot);
    publishCurrent(app);
   }catch(Exception e){android.util.Log.e("StationFrontend","configure: "+e.getClass().getSimpleName()+": "+safeReason(e));configured=false;publishError(utf8(catalogError(e,"Não foi possível preparar o catálogo Station.")));}
  }))configured=false;
 }
 private static void prepareStorage(StationAndroid app,String romsRoot)throws Exception {
    if(downloads!=null)return;
    // This root comes from the native application, never a catalog/archive entry.
    Path roms=StationStorage.prepareRoot(Paths.get(romsRoot));
    android.util.Log.i("StationFrontend","Storage root prepared");
    StationInstaller installer=new StationInstaller(roms,app.privateFiles.resolve("station-v2/installs"),new StationArchive());
    downloads=new StationDownloads(app.api,app.coordinator,installer,roms.resolve(".station-v2/staging"),
      (id,active,received,total,message,path,result)->{
       publishJob(id,active,received,total,utf8(message),utf8(path),result);
       StationCoordinator.Library library=app.coordinator.current();StationCatalog.Item item=library==null?null:library.catalog.find(id);
       org.emulationstation.frontend.DownloadService.changed(app.context,id,item==null?"Jogo":item.name,active,received,total,message,result);
       if(result==3&&library==null)requestLogin();
      });
 }
 public static void refresh(){execute(()->{
  try{StationAndroid app=StationAndroid.current();if(app==null)throw new IOException();
   if(downloads==null){if(requestedStorageRoot==null)throw new IOException("Storage root not supplied");prepareStorage(app,requestedStorageRoot);configured=true;}
   app.coordinator.refresh(new StationApi.Cancellation());publishCurrent(app);}
  catch(Exception e){publishError(utf8(catalogError(e,"Não foi possível atualizar. Confira a conexão e tente novamente.")));}
 });}
 private static void publishCurrent(StationAndroid app)throws Exception {
  StationCoordinator.Library library=app.coordinator.current();if(library==null)throw new IOException("Catálogo não carregado");
  StationPublication publication=new StationPublication(library.catalog);
  ArrayList<byte[]> rows=new ArrayList<>();
  long preparedBytes=0;int preparedItems=0;publishPreparation(0,publication.rows.size(),0);
  for(StationPublication.Row entry:publication.rows){
   StationCatalog.Item item=entry.item;StationPlatforms.Platform platform=entry.platform;
   StationInstaller.Installed installed=null;
   try{installed=downloads.find(item);}catch(Exception invalidReceipt){
    // One invalid receipt cannot hide the rest of an authenticated catalog.
    StationDiagnostics.record(StationDiagnostics.Event.RECEIPT_INVALID,0,1);
   }
   byte[] row=utf8(item.itemId+"\0"+item.name+"\0"+platform.label+"\0"+platform.folder+"\0"+item.coverId+"\0"+(installed==null?"":installed.launchPath.toString())+"\0"+StationCatalog.folderKey(item)+"\0");
   rows.add(row);preparedBytes+=row.length;publishPreparation(++preparedItems,publication.rows.size(),preparedBytes);
  }
  StationDiagnostics.record(StationDiagnostics.Event.UNSUPPORTED_PLATFORM,0,publication.unsupportedCount);
  StationDiagnostics.record(StationDiagnostics.Event.CATALOG_PUBLISHED,library.cached?503:200,rows.size());
  android.util.Log.i("StationFrontend","Publishing catalog items="+rows.size());
  images.replaceCatalog(()->publishCatalog(rows.toArray(new byte[0][]),utf8(library.displayName)));
  String warning=publication.warning();
  if(!warning.equals(platformWarning)){
   platformWarning=warning;
   if(!warning.isEmpty())new android.os.Handler(android.os.Looper.getMainLooper()).post(()->android.widget.Toast.makeText(app.context,warning,android.widget.Toast.LENGTH_LONG).show());
  }
 }
 public static boolean start(String itemId){StationDownloads current=downloads;return current!=null&&current.start(itemId);}
 public static void cancel(String itemId){StationDownloads current=downloads;if(current!=null)current.cancel(itemId);}
 public static boolean remove(String itemId){StationDownloads current=downloads;if(current==null)return false;current.uninstall(itemId);return true;}
 /** Background-only lookup of verified installed launch files; never scans arbitrary ROM folders. */
 public static String[] installedPathsFor(String platform)throws Exception {
  if(android.os.Looper.myLooper()==android.os.Looper.getMainLooper())throw new IllegalStateException("Use an IO worker");
  StationAndroid app=StationAndroid.current();StationDownloads current=downloads;
  if(app==null||current==null||!app.coordinator.ready())throw new IllegalStateException("Station catalog is not ready");
  StationPlatforms.Platform selected=StationPlatforms.resolve(platform);
  StationCoordinator.Library library=app.coordinator.current();if(library==null)throw new IllegalStateException("Station catalog is not ready");
  LinkedHashSet<String> paths=new LinkedHashSet<>();
  for(StationCatalog.Item item:library.catalog.items){
   StationPlatforms.Platform value;
   try{value=StationPlatforms.resolve(item.platform);}catch(StationPlatforms.UnsupportedPlatform unsupported){continue;}
   if(!selected.folder.equals(value.folder))continue;
   try{StationInstaller.Installed installed=current.find(item);if(installed!=null)paths.add(installed.launchPath.toString());}
   catch(IOException invalid){StationDiagnostics.record(StationDiagnostics.Event.RECEIPT_INVALID,0,1);}
  }
  return paths.toArray(new String[0]);
 }
 /** Exact receipt lookup for a selected Station ID, no arbitrary folder scan. */
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
 public static int activeCount(){StationDownloads current=downloads;return current==null?0:current.activeCount();}
 public static void cover(String itemId){images.request(itemId);}
 public static void setForeground(boolean visible){boolean resumed=visible&&!foreground;foreground=visible;images.setForeground(visible);publishForeground(visible);
  StationAndroid onlineApp=StationAndroid.current();if(onlineApp!=null)try{Class.forName("org.emulationstation.frontend.netplay.StationPresence").getMethod("foreground",Context.class,boolean.class).invoke(null,onlineApp.context,visible);}catch(ReflectiveOperationException optional){android.util.Log.w("StationOnline","Presence lifecycle unavailable");}
  if(resumed){if(!configured&&requestedStorageRoot!=null)configure(requestedStorageRoot);else if(configured)reconcile();}}
 public static void reconcile(){execute(()->{try{StationAndroid app=StationAndroid.current();if(app!=null&&downloads!=null)publishCurrent(app);}catch(Exception e){publishError(utf8("Não foi possível conferir os jogos instalados."));}});}
 private static boolean execute(Runnable operation){try{commands.execute(operation);return true;}catch(RejectedExecutionException busy){publishError(utf8("Aguarde a consulta em andamento."));return false;}}
 private static String catalogError(Exception e,String fallback){
  if(e instanceof StationStorage.Failure)return ((StationStorage.Failure)e).userMessage;
  if(e instanceof StationPlatforms.UnsupportedPlatform){
   StationDiagnostics.record(StationDiagnostics.Event.UNSUPPORTED_PLATFORM,0,1);
   return "Plataforma ainda sem integração: "+((StationPlatforms.UnsupportedPlatform)e).platform+". Atualize o aplicativo.";
  }return fallback;
 }
 private static String safeReason(Exception e){if(e instanceof StationStorage.Failure)return ((StationStorage.Failure)e).reason;String m=e.getMessage();if(m!=null&&(m.equals("Symbolic path refused")||m.equals("Invalid catalog identity")))return m;return "operation failed";}
 private static byte[] utf8(String text){return text.getBytes(StandardCharsets.UTF_8);}
 private static native void publishPreparation(int done,int total,long bytes);
 private static native void publishCatalog(byte[][] rows,byte[] displayName);
 private static native void publishCoverResult(String itemId,byte[] path,int result,long retryMillis);
 private static native void publishForeground(boolean visible);
 private static native void publishJob(String itemId,boolean active,long received,long total,byte[] message,byte[] launch,int result);
 private static native void publishError(byte[] message);
}
