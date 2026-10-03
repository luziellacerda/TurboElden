package org.emulationstation.frontend.station;

/** Numeric events only: no credentials, IDs, URLs, personal names or response bodies. */
public final class StationDiagnostics {
 public enum Event { ACTIVATION, SESSION, PROFILE, CATALOG, COVER, ARTIFACT, AUTHORIZE,
  SERVER_ITEM_NOT_FOUND, SERVER_COVER_NOT_FOUND, SERVER_GRANT_NOT_FOUND, SERVER_ARTIFACT_NOT_READY, SERVER_OTHER_FAILURE, REQUEST_FAILED, CATALOG_NETWORK, CATALOG_CACHE, CATALOG_PUBLISHED, COVER_CACHE,
  COVER_FAILED, INSTALL_FINISHED, INSTALL_FAILED, RECEIPT_INVALID, LOCAL_REUSE, UNSUPPORTED_PLATFORM }
 public interface Observer {void event(Event event,int status,long count);}
 private static volatile Observer observer=(event,status,count)->{};
 private StationDiagnostics(){}
 public static void observe(Observer value){observer=value==null?(event,status,count)->{}:value;}
 public static void record(Event event,int status,long count){
  try{observer.event(event,status,count);}catch(RuntimeException ignored){/* Diagnostics cannot break the operation. */}
 }
 static Event route(String path){
  if(path.equals("/v1/station/catalog"))return Event.CATALOG;
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
