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
 private static final ThreadPoolExecutor commands=pool("Station-catalog",8),images=pool("Station-covers",32);
 private static final ConcurrentHashMap<String,StationApi.Cancellation> requests=new ConcurrentHashMap<>();
 private static volatile StationDownloads downloads;private static volatile boolean foreground=true,configured;
 private static ThreadPoolExecutor pool(String name,int capacity){return new ThreadPoolExecutor(0,1,10,TimeUnit.SECONDS,new ArrayBlockingQueue<Runnable>(capacity),r->{Thread t=new Thread(r,name);t.setDaemon(true);return t;});}
 private StationFrontend(){}
 public static boolean authorized(){StationAndroid app=StationAndroid.current();return app!=null&&app.coordinator.ready();}
 public static void requestLogin(){StationAndroid app=StationAndroid.current();if(app!=null){
  android.content.Intent intent=new android.content.Intent(app.context,org.emulationstation.frontend.auth.LoginActivity.class);
  intent.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK|android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP);app.context.startActivity(intent);
 }}
 public static void configure(String romsRoot) {
  synchronized(StationFrontend.class){if(configured)return;configured=true;}
  if(!execute(()->{
   try {
    StationAndroid app=StationAndroid.current();if(app==null)throw new IOException("Entre no aplicativo para carregar o catálogo.");
    Path roms=Paths.get(romsRoot);
    StationInstaller installer=new StationInstaller(roms,app.privateFiles.resolve("station-v2/installs"),new StationArchive());
    downloads=new StationDownloads(app.api,app.coordinator,installer,roms.resolve(".station-v2/staging"),
      (id,active,received,total,message,path,result)->{
       publishJob(id,active,received,total,utf8(message),utf8(path),result);
       StationCoordinator.Library library=app.coordinator.current();StationCatalog.Item item=library==null?null:library.catalog.find(id);
       org.emulationstation.frontend.DownloadService.changed(app.context,id,item==null?"Jogo":item.name,active,received,total,message,result);
       if(result==3&&library==null)requestLogin();
      });
    publishCurrent(app);
   }catch(Exception e){configured=false;publishError(utf8("Não foi possível preparar o catálogo Station."));}
  }))configured=false;
 }
 public static void refresh(){execute(()->{
  try{StationAndroid app=StationAndroid.current();if(app==null)throw new IOException();app.coordinator.refresh(new StationApi.Cancellation());publishCurrent(app);}
  catch(Exception e){publishError(utf8("Não foi possível atualizar. Confira a conexão e tente novamente."));}
 });}
 private static void publishCurrent(StationAndroid app)throws Exception {
  StationCoordinator.Library library=app.coordinator.current();if(library==null)throw new IOException("Catálogo não carregado");
  ArrayList<byte[]> rows=new ArrayList<>();
  for(StationCatalog.Item item:library.catalog.items){
   StationPlatforms.Platform platform=StationPlatforms.resolve(item.platform);
   StationInstaller.Installed installed=downloads.find(item);
   rows.add(utf8(item.itemId+"\0"+item.name+"\0"+platform.label+"\0"+platform.folder+"\0"+item.coverId+"\0"+(installed==null?"":installed.launchPath.toString())+"\0"));
  }
  publishCatalog(rows.toArray(new byte[0][]),utf8(library.displayName));
 }
 public static boolean start(String itemId){StationDownloads current=downloads;return current!=null&&current.start(itemId);}
 public static void cancel(String itemId){StationDownloads current=downloads;if(current!=null)current.cancel(itemId);}
 public static boolean remove(String itemId){StationDownloads current=downloads;if(current==null)return false;current.uninstall(itemId);return true;}
 public static int activeCount(){StationDownloads current=downloads;return current==null?0:current.activeCount();}
 public static void cover(String itemId){
  if(!foreground)return;StationApi.Cancellation cancel=new StationApi.Cancellation();if(requests.putIfAbsent(itemId,cancel)!=null)return;
  try{images.execute(()->{
   try{StationAndroid app=StationAndroid.current();if(app!=null){Path path=app.coordinator.cover(itemId,cancel);cancel.check();publishCover(itemId,utf8(path.toString()));}}
   catch(Exception failed){publishCover(itemId,new byte[0]);}
   finally{requests.remove(itemId,cancel);}
  });}catch(RejectedExecutionException busy){requests.remove(itemId,cancel);publishCover(itemId,new byte[0]);}
 }
 public static void setForeground(boolean visible){boolean resumed=visible&&!foreground;foreground=visible;if(!visible){for(StationApi.Cancellation cancel:requests.values())cancel.cancel();}else if(resumed&&configured)reconcile();}
 public static void reconcile(){execute(()->{try{StationAndroid app=StationAndroid.current();if(app!=null&&downloads!=null)publishCurrent(app);}catch(Exception e){publishError(utf8("Não foi possível conferir os jogos instalados."));}});}
 private static boolean execute(Runnable operation){try{commands.execute(operation);return true;}catch(RejectedExecutionException busy){publishError(utf8("Aguarde a consulta em andamento."));return false;}}
 private static byte[] utf8(String text){return text.getBytes(StandardCharsets.UTF_8);}
 private static native void publishCatalog(byte[][] rows,byte[] displayName);
 private static native void publishCover(String itemId,byte[] path);
 private static native void publishJob(String itemId,boolean active,long received,long total,byte[] message,byte[] launch,int result);
 private static native void publishError(byte[] message);
}
