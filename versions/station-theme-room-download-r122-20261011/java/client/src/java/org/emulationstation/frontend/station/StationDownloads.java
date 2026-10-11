package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;

/** One transfer at a time; paused/offline jobs release the worker for other games. */
public final class StationDownloads implements AutoCloseable {
 public interface Listener {void changed(String id,boolean active,long processed,long total,String message,String launchPath,int result);}
 public enum State {QUEUED,AUTHORIZING,DOWNLOADING,PREPARING,WAITING,PAUSED,ERROR,COMPLETE,CANCELLED}
 public static final class Entry {
  public final String id,name,platform,coverId,message;public final long revision,done,total,networkDone,networkTotal,elapsedMillis;
  public final double bytesPerSecond;public final State state;
  Entry(Job j){id=j.item.itemId;name=j.item.name;platform=j.item.platform;coverId=j.item.coverId;revision=j.item.revision;
   message=j.message;done=j.done;total=j.total;networkDone=j.networkDone;networkTotal=j.networkTotal;state=j.state;
   elapsedMillis=Math.max(0,(System.nanoTime()-j.started)/1000000);bytesPerSecond=state==State.DOWNLOADING?j.rate:0;}
  public boolean active(){return state!=State.COMPLETE&&state!=State.CANCELLED&&state!=State.ERROR;}
 }
 private static final class Job {
  final StationCatalog.Item item;final long started=System.nanoTime();
  State state=State.QUEUED;String message="Na fila";long done,total=-1,networkDone,networkTotal=-1,sampleAt,sampleBytes,lastNotice;
  double rate;int failures;boolean running,paused,cancelled;StationApi.Cancellation attempt;ScheduledFuture<?> future;
  Job(StationCatalog.Item item){this.item=item;}
  boolean terminal(){return state==State.COMPLETE||state==State.CANCELLED||state==State.ERROR;}
 }
 private final StationApi api;private final StationCoordinator owner;private final StationInstaller installer;
 private final Path staging,pending;private final Listener listener;
 private final LinkedHashMap<String,Job> jobs=new LinkedHashMap<>();
 private final ScheduledThreadPoolExecutor worker=new ScheduledThreadPoolExecutor(1,r->{Thread t=new Thread(r,"Station-install");t.setDaemon(true);return t;});
 private final ExecutorService journal=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-download-journal");t.setDaemon(true);return t;});
 private boolean closed;
 public StationDownloads(StationApi api,StationCoordinator owner,StationInstaller installer,Path staging,Listener listener)throws IOException {
  this.api=api;this.owner=owner;this.installer=installer;this.staging=StationInstaller.directory(staging);this.pending=this.staging.resolve("pending-downloads-v1");this.listener=listener;
  worker.setRemoveOnCancelPolicy(true);worker.setKeepAliveTime(10,TimeUnit.SECONDS);worker.allowCoreThreadTimeOut(true);
 }
 public synchronized List<Entry> entries(){List<Entry> rows=new ArrayList<>();for(Job j:jobs.values())if(j.state!=State.CANCELLED)rows.add(new Entry(j));return Collections.unmodifiableList(rows);}
 public synchronized int activeCount(){int count=0;for(Job j:jobs.values())if(!j.terminal())count++;return count;}
 public synchronized int entryCount(){int count=0;for(Job j:jobs.values())if(j.state!=State.CANCELLED)count++;return count;}
 public synchronized boolean start(String id){
  StationCoordinator.Library library=owner.current();if(closed||library==null||library.catalog.find(id)==null)return false;
  Job old=jobs.get(id);if(old!=null&&(!old.terminal()||old.running))return false;
  if(activeCount()>=32){listener.changed(id,false,0,-1,"A fila já tem 32 jogos. Aguarde ou cancele um download.","",3);return false;}
  jobs.remove(id);trim();Job job=new Job(library.catalog.find(id));jobs.put(id,job);notifyJob(job,"",0);persist();schedule(job,0);return true;
 }
 private void trim(){Iterator<Job> it=jobs.values().iterator();while(jobs.size()>=48&&it.hasNext()){Job j=it.next();if(j.terminal()&&!j.running)it.remove();}}
 private void schedule(Job j,long delay){
  if(closed||j.running||j.paused||j.cancelled||j.terminal())return;
  if(j.future!=null)j.future.cancel(false);
  j.future=worker.schedule(()->run(j),delay,TimeUnit.MILLISECONDS);
 }
 private synchronized void notifyJob(Job j,String launch,int result){listener.changed(j.item.itemId,!j.terminal(),j.done,j.total,j.message,launch,result);}
 private synchronized void stage(Job j,State state,String message){if(j.paused||j.cancelled)return;j.state=state;j.message=message;j.rate=0;notifyJob(j,"",0);}
 private synchronized void progress(Job j,long n,long total,boolean network){
  if(j.paused||j.cancelled)return;long now=System.nanoTime();j.done=n;j.total=total;
  if(network){j.networkDone=n;if(j.sampleAt==0){j.sampleAt=now;j.sampleBytes=n;}else if(now-j.sampleAt>=500000000L){j.rate=Math.max(0,(n-j.sampleBytes)*1e9/(now-j.sampleAt));j.sampleAt=now;j.sampleBytes=n;}}
  if(n==total||now-j.lastNotice>=100000000L){j.lastNotice=now;notifyJob(j,"",0);}
 }
 private void run(Job job){
  StationApi.Cancellation cancel;
  synchronized(this){job.future=null;if(closed||job.paused||job.cancelled||job.terminal()||job.running)return;
   job.running=true;job.attempt=cancel=new StationApi.Cancellation();job.done=0;job.networkDone=0;job.rate=0;job.sampleAt=0;}
  Path transaction=null;StationApi.ArtifactTransfer transfer=null;StationCoordinator.Access used=null;long retry=0;
  try {
   stage(job,State.AUTHORIZING,"Aguardando autorização");
   final StationApi.Grant grant;final StationCatalog.Item item;final Path artifact;final long total;
   // Every retry requests a NEW signed grant. Never reuse a consumed GET or guess Range support.
   long authorizeStarted=System.nanoTime();
   try(StationCoordinator.Access access=owner.acquireItem(job.item.itemId,cancel)){
    used=access;cancel.check();grant=owner.authorize(access,cancel);item=access.item;
    StationDiagnostics.record(StationDiagnostics.Event.AUTHORIZE_ELAPSED_MS,0,elapsedMillis(authorizeStarted));
    if(item==null||item.revision!=grant.itemRevision)throw new IOException("O catálogo mudou. Atualize a lista.");
    total=grant.artifact.sizeBytes+grant.artifact.expandedSizeBytes;
    if(StationStorage.usableBytes(staging)<total+256L*1024*1024)throw new InsufficientSpace();
    transaction=Files.createTempDirectory(staging,"transfer-");artifact=transaction.resolve("artifact");
    synchronized(this){job.networkTotal=grant.artifact.sizeBytes;job.total=total;}
    try(StationDiagnostics.Scope trace=StationDiagnostics.selection(item.itemId,item.coverId,item.revision)){long headers=System.nanoTime();transfer=api.openArtifact(grant,grant.artifact.sizeBytes,cancel);StationDiagnostics.record(StationDiagnostics.Event.ARTIFACT_HEADERS_ELAPSED_MS,0,elapsedMillis(headers));}
   }
   stage(job,State.DOWNLOADING,"Baixando");long began=System.nanoTime();
   try(StationApi.ArtifactTransfer stream=transfer){stream.copyToStaging(artifact,cancel,(n,t)->progress(job,n,total,true));}
   StationDiagnostics.record(StationDiagnostics.Event.DOWNLOAD_ELAPSED_MS,0,elapsedMillis(began));
   StationDiagnostics.record(StationDiagnostics.Event.DOWNLOAD_BYTES,0,grant.artifact.sizeBytes);
   cancel.check();stage(job,State.PREPARING,"Preparando");
   long installStarted=System.nanoTime();
   StationInstaller.Installed installed=installer.install(item,grant,artifact,cancel,(n,t)->progress(job,grant.artifact.sizeBytes+n,total,false));
   StationDiagnostics.record(StationDiagnostics.Event.INSTALL_ELAPSED_MS,0,elapsedMillis(installStarted));
   synchronized(this){job.state=State.COMPLETE;job.message="Instalado";job.done=job.total=total;job.rate=0;notifyJob(job,installed.launchPath.toString(),1);}
   StationDiagnostics.record(StationDiagnostics.Event.INSTALL_FINISHED,0,total);
  }catch(Exception error){
   if(error instanceof StationApi.Failure)owner.rejected(used,(StationApi.Failure)error);
   synchronized(this){
    job.rate=0;
    if(job.cancelled){job.state=State.CANCELLED;job.message="Cancelado";notifyJob(job,"",3);}
    else if(job.paused){job.state=State.PAUSED;job.message="Pausado";notifyJob(job,"",0);}
    else if(cancel.cancelled()){job.state=State.QUEUED;job.message="Retomando";notifyJob(job,"",0);}
    else if(StationDownloadRetry.transientFailure(error)){
     job.state=State.WAITING;job.message=error instanceof StationApi.Failure?"Aguardando servidor":"Aguardando conexão";
     retry=StationDownloadRetry.delayMillis(++job.failures,error instanceof StationApi.Failure?((StationApi.Failure)error).retryAfterMillis:0);notifyJob(job,"",0);
    }else{job.state=State.ERROR;job.message=message(error,cancel);notifyJob(job,"",3);StationDiagnostics.record(StationDiagnostics.Event.INSTALL_FAILED,StationDiagnostics.status(error),0);}
   }
  }finally{
   if(transfer!=null)try{transfer.close();}catch(IOException ignored){}
   if(transaction!=null)try{Files.deleteIfExists(transaction.resolve("artifact"));Files.deleteIfExists(transaction);}catch(IOException retained){}
   synchronized(this){job.running=false;job.attempt=null;if(job.cancelled)jobs.remove(job.item.itemId,job);persist();schedule(job,retry);}
  }
 }
 public void pause(String id){StationApi.Cancellation abort;
  synchronized(this){Job j=jobs.get(id);if(j==null||j.terminal()||j.state==State.PREPARING)return;j.paused=true;j.state=State.PAUSED;j.message="Pausado";j.rate=0;if(j.future!=null)j.future.cancel(false);abort=j.attempt;notifyJob(j,"",0);persist();}
  if(abort!=null)abort.cancel();
 }
 public synchronized void resume(String id){Job j=jobs.get(id);if(j==null||j.cancelled||j.state==State.COMPLETE)return;j.paused=false;j.state=State.QUEUED;j.message="Na fila";j.failures=0;notifyJob(j,"",0);persist();schedule(j,0);}
 public void cancel(String id){StationApi.Cancellation abort;
  synchronized(this){Job j=jobs.get(id);if(j==null||j.state==State.COMPLETE)return;j.cancelled=true;j.paused=false;j.state=State.CANCELLED;j.message="Cancelado";j.rate=0;if(j.future!=null)j.future.cancel(false);abort=j.attempt;notifyJob(j,"",3);if(!j.running)jobs.remove(id,j);persist();}
  if(abort!=null)abort.cancel();
 }
 public synchronized void connectionChanged(){if(!api.available())return;for(Job j:jobs.values())if(j.state==State.WAITING&&j.message.equals("Aguardando conexão"))schedule(j,0);}
 private synchronized void persist(){
  StringBuilder data=new StringBuilder();for(Job j:jobs.values())if(!j.terminal()||j.state==State.ERROR)data.append(j.item.itemId).append('\t').append(j.paused||j.state==State.ERROR?'P':'Q').append('\n');
  byte[] bytes=data.toString().getBytes(StandardCharsets.UTF_8);
  try{journal.execute(()->{try{if(bytes.length==0)Files.deleteIfExists(pending);else StationFiles.replace(new ByteArrayInputStream(bytes),pending,bytes.length,16384,StationFiles.NEVER_CANCELLED,StationFiles.NO_PROGRESS);}catch(IOException e){StationDiagnostics.record(StationDiagnostics.Event.RECEIPT_INVALID,0,1);}});}catch(RejectedExecutionException ignored){}
 }
 public synchronized void restorePending(){
  if(!jobs.isEmpty()||!Files.isRegularFile(pending,LinkOption.NOFOLLOW_LINKS))return;
  try{String text=new String(StationFiles.readBounded(pending,16384),StandardCharsets.UTF_8);StationCoordinator.Library l=owner.current();if(l==null)return;
   for(String row:text.split("\n")){String[] parts=row.split("\t");if(parts.length!=2||!StationProtocol.libraryId(parts[0])||jobs.size()>=32||jobs.containsKey(parts[0]))continue;
    StationCatalog.Item item=l.catalog.find(parts[0]);if(item==null)continue;Job j=new Job(item);j.paused=parts[1].equals("P");if(j.paused){j.state=State.PAUSED;j.message="Pausado";}jobs.put(parts[0],j);notifyJob(j,"",0);schedule(j,0);
   }
  }catch(IOException invalid){StationDiagnostics.record(StationDiagnostics.Event.RECEIPT_INVALID,0,1);}
 }
 public void uninstall(String id){synchronized(this){Job j=jobs.get(id);if(j!=null&&(!j.terminal()||j.running)){listener.changed(id,true,j.done,j.total,"Cancele o download antes de apagar.","",0);return;}}
  worker.execute(()->{try{installer.uninstall(id);listener.changed(id,false,0,0,"Apagado","",2);}catch(Exception e){listener.changed(id,false,0,-1,"Não foi possível apagar os arquivos do jogo.","",3);}});
 }
 public StationInstaller.Installed find(StationCatalog.Item item)throws Exception{return installer.find(item);}
 public void close(){List<StationApi.Cancellation> attempts=new ArrayList<>();
  synchronized(this){if(closed)return;closed=true;for(Job j:jobs.values()){if(j.future!=null)j.future.cancel(false);if(j.attempt!=null)attempts.add(j.attempt);}}
  for(StationApi.Cancellation c:attempts)c.cancel();worker.shutdown();
  try{if(!worker.awaitTermination(5,TimeUnit.SECONDS))worker.shutdownNow();}catch(InterruptedException e){worker.shutdownNow();Thread.currentThread().interrupt();}
  synchronized(this){persist();}journal.shutdown();
  try{journal.awaitTermination(5,TimeUnit.SECONDS);}catch(InterruptedException e){Thread.currentThread().interrupt();}
 }
 private static long elapsedMillis(long started){return Math.max(0,(System.nanoTime()-started)/1000000L);}
 private static final class InsufficientSpace extends IOException {}
 static String message(Exception error,StationApi.Cancellation cancel){
  if(cancel.cancelled())return "Cancelado";
  if(error instanceof StationPlatforms.UnsupportedPlatform)return "Esta plataforma ainda precisa de suporte. Atualize o aplicativo.";
  if(error instanceof StationApi.ArtifactUnavailable)return "O servidor ainda não publicou os dados de instalação deste jogo.";
  if(error instanceof InsufficientSpace)return "Espaço insuficiente para baixar e preparar o jogo.";
  if(error instanceof StationApi.Failure){StationApi.Failure f=(StationApi.Failure)error;
   if(f.status==401||f.status==403)return "Acesso não autorizado. Entre novamente.";
   if(f.status==404)return "Jogo indisponível no catálogo atual. Atualize a lista e tente novamente.";
  }
  return "Falha ao preparar o jogo. Os arquivos anteriores foram preservados.";
 }
}
