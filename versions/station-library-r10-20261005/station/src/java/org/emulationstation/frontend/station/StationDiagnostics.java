package org.emulationstation.frontend.station;

/** Counts and optional request traces; identities are SHA256 tags, never credentials or paths. */
public final class StationDiagnostics {
 public enum Event { ACTIVATION, SESSION, PROFILE, CATALOG, COVER, ARTIFACT, AUTHORIZE,
  SERVER_ITEM_NOT_FOUND, SERVER_COVER_NOT_FOUND, SERVER_GRANT_NOT_FOUND, SERVER_ARTIFACT_NOT_READY, SERVER_OTHER_FAILURE, REQUEST_FAILED, CATALOG_NETWORK, CATALOG_CACHE, CATALOG_PUBLISHED, COVER_CACHE,
  COVER_FAILED, INSTALL_FINISHED, INSTALL_FAILED, RECEIPT_INVALID, LOCAL_REUSE, UNSUPPORTED_PLATFORM }
 public interface Observer {void event(Event event,int status,long count);}
 public interface TraceObserver {void event(Event event,int status,String correlation,String itemTag,String coverTag,long revision);}
 private static volatile TraceObserver traceObserver=(e,s,c,i,v,r)->{};
 private static final ThreadLocal<Selection> selected=new ThreadLocal<>();
 private static final class Selection {
  final String item,cover;final long revision;
  Selection(String item,String cover,long revision){this.item=tag(item);this.cover=tag(cover);this.revision=revision;}
 }
 public static final class Scope implements AutoCloseable {
  private final Selection previous;
  private Scope(Selection value){previous=selected.get();selected.set(value);}
  public void close(){if(previous==null)selected.remove();else selected.set(previous);}
 }
 private static volatile Observer observer=(event,status,count)->{};
 private StationDiagnostics(){}
 public static void observe(Observer value){observer=value==null?(event,status,count)->{}:value;}
 public static void observeTrace(TraceObserver value){traceObserver=value==null?(e,s,c,i,v,r)->{}:value;}
 public static Scope selection(String item,String cover,long revision){return new Scope(new Selection(item,cover,revision));}
 static String tag(String id){
  if(!StationProtocol.libraryId(id))return "";
  StringBuilder hex=new StringBuilder();for(byte b:StationProtocol.sha256(id.getBytes(java.nio.charset.StandardCharsets.UTF_8)))hex.append(String.format(java.util.Locale.ROOT,"%02x",b&255));
  return hex.toString();
 }
 static void trace(Event event,int status,String correlation){
  if(correlation==null||!correlation.matches("[A-Za-z0-9_-]{8,64}"))return;
  Selection value=selected.get();
  try{traceObserver.event(event,status,correlation,value==null?"":value.item,value==null?"":value.cover,value==null?0:value.revision);}
  catch(RuntimeException ignored){/* Diagnostics cannot break the operation. */}
 }
 public static void record(Event event,int status,long count){
  try{observer.event(event,status,count);}catch(RuntimeException ignored){/* Diagnostics cannot break the operation. */}
 }
 static Event route(String path){
  if(path.equals("/v1/station/catalog")||path.equals("/v1/station/catalog?metadata=1"))return Event.CATALOG;
  if(path.equals("/v1/station/me"))return Event.PROFILE;
  if(path.equals("/v1/station/downloads/authorize"))return Event.AUTHORIZE;
  if(path.startsWith("/v1/station/covers/"))return Event.COVER;
  if(path.startsWith("/v1/station/artifacts/"))return Event.ARTIFACT;
  if(path.startsWith("/v1/station/activations/"))return Event.ACTIVATION;
  if(path.equals("/v1/station/challenges")||path.equals("/v1/station/sessions"))return Event.SESSION;
  return Event.REQUEST_FAILED;
 }
 static void serverFailure(int status,String code){
  Event event;
  switch(code){
   case "STATION_ITEM_NOT_FOUND":event=Event.SERVER_ITEM_NOT_FOUND;break;
   case "STATION_COVER_NOT_FOUND":event=Event.SERVER_COVER_NOT_FOUND;break;
   case "STATION_GRANT_NOT_FOUND":event=Event.SERVER_GRANT_NOT_FOUND;break;
   case "STATION_ARTIFACT_NOT_READY":event=Event.SERVER_ARTIFACT_NOT_READY;break;
   default:event=Event.SERVER_OTHER_FAILURE;
  }
  record(event,status,0);
 }
 static int status(Exception e){return e instanceof StationApi.Failure?((StationApi.Failure)e).status:0;}
}
