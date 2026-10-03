package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/** Bounded, event-driven download queue shared by the native UI and lifecycle. */
public final class StationDownloads implements AutoCloseable {
 public interface Listener {
  void changed(String itemId,boolean active,long processed,long total,String message,String launchPath,int result);
 }
 private final StationApi api;private final StationCoordinator owner;private final StationInstaller installer;
 private final Path staging;private final Listener listener;
 private final ConcurrentHashMap<String,StationApi.Cancellation> jobs=new ConcurrentHashMap<>();
 private final ThreadPoolExecutor worker=new ThreadPoolExecutor(0,1,10,TimeUnit.SECONDS,new ArrayBlockingQueue<Runnable>(4),r->{Thread t=new Thread(r,"Station-install");t.setDaemon(true);return t;});
 public StationDownloads(StationApi api,StationCoordinator owner,StationInstaller installer,Path staging,Listener listener)throws IOException {
  this.api=api;this.owner=owner;this.installer=installer;this.staging=StationInstaller.directory(staging);this.listener=listener;
 }
 public boolean start(String id) {
  StationCoordinator.Library library=owner.current();if(library==null||library.catalog.find(id)==null)return false;
  StationApi.Cancellation cancel=new StationApi.Cancellation();if(jobs.putIfAbsent(id,cancel)!=null)return false;
  listener.changed(id,true,0,-1,"Aguardando autorização","",0);
  try{worker.execute(()->run(id,cancel));return true;}catch(RejectedExecutionException full){jobs.remove(id,cancel);listener.changed(id,false,0,-1,"Aguarde a instalação em andamento.","",3);return false;}
 }
 private void run(String id,StationApi.Cancellation cancel) {
  Path transaction=null;
  try {
   cancel.check();StationApi.Grant grant=owner.authorize(id,cancel);
   StationCoordinator.Library library=owner.current();StationCatalog.Item item=library==null?null:library.catalog.find(id);
   if(item==null||item.revision!=grant.itemRevision)throw new IOException("O catálogo mudou. Atualize a lista.");
   if(Files.getFileStore(staging).getUsableSpace()<grant.artifact.sizeBytes+256L*1024*1024)throw new IOException("Espaço insuficiente para baixar o jogo.");
   transaction=Files.createTempDirectory(staging,"transfer-");Path artifact=transaction.resolve("artifact");
   long total=grant.artifact.sizeBytes+grant.artifact.expandedSizeBytes;
   final long[] last={0};
   StationFiles.Progress download=(n,t)->{long now=System.nanoTime();if(n==t||now-last[0]>=100000000){last[0]=now;listener.changed(id,true,n,total,"Baixando","",0);}};
   api.downloadToStaging(grant,artifact,grant.artifact.sizeBytes,cancel,download);
   StationFiles.Progress extract=(n,t)->{long now=System.nanoTime();if(n==t||now-last[0]>=100000000){last[0]=now;listener.changed(id,true,grant.artifact.sizeBytes+n,total,"Preparando","",0);}};
   StationInstaller.Installed installed=installer.install(item,grant,artifact,cancel,extract);
   listener.changed(id,false,total,total,"Instalado",installed.launchPath.toString(),1);
  }catch(Exception failure){listener.changed(id,false,0,-1,message(failure,cancel),"",3);}
  finally {
   if(transaction!=null)try{Files.deleteIfExists(transaction.resolve("artifact"));Files.deleteIfExists(transaction);}catch(IOException retained){/* Unique partial remains uninstalled; never erase another transaction. */}
   jobs.remove(id,cancel);
  }
 }
 public void cancel(String id){StationApi.Cancellation job=jobs.get(id);if(job!=null)job.cancel();}
 public int activeCount(){return jobs.size();}
 public void uninstall(String id) {
  if(jobs.containsKey(id)){listener.changed(id,true,0,-1,"Cancele o download antes de apagar.","",0);return;}
  try{worker.execute(()->{try{installer.uninstall(id);listener.changed(id,false,0,0,"Apagado","",2);}
   catch(Exception e){listener.changed(id,false,0,-1,"Não foi possível apagar os arquivos do jogo.","",3);}});}
  catch(RejectedExecutionException full){listener.changed(id,false,0,-1,"Aguarde a instalação em andamento.","",3);}
 }
 public StationInstaller.Installed find(StationCatalog.Item item)throws Exception{return installer.find(item);}
 public void close(){for(StationApi.Cancellation cancel:jobs.values())cancel.cancel();worker.shutdown();}
 private static String message(Exception error,StationApi.Cancellation cancel) {
  if(cancel.cancelled()||error instanceof InterruptedIOException)return "Cancelado";
  if(error instanceof StationApi.Failure){StationApi.Failure f=(StationApi.Failure)error;
   if(f.status==503)return "Jogo ainda não preparado pelo servidor.";
   if(f.status==429)return "Limite de consultas. Aguarde um minuto.";
   if(f.status==401||f.status==403)return "Acesso não autorizado. Entre novamente.";
   if(f.status==404)return "Autorização indisponível. Tente baixar novamente.";
  }
  return "Falha ao preparar o jogo. Os arquivos anteriores foram preservados.";
 }
}
