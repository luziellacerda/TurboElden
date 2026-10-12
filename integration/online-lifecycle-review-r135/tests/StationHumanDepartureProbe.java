package org.emulationstation.frontend.netplay;
import android.content.Context;import android.os.*;import java.lang.reflect.*;import java.util.*;import java.util.concurrent.*;import org.json.*;import org.emulationstation.frontend.station.StationApi;
/** Actual main-process event 4 on the base and overlay, plus adversarial helper cases. */
public class StationHumanDepartureProbe{
 static JSONObject binding(){JSONObject b=new JSONObject().put("roomId","0123456789abcdef0123456789abcdef").put("generation",3).put("recoveryProtocol","station-stream.v3");for(String k:new String[]{"itemId","engineId","coreSha256","runtimeSha256","contentSha256","profileId","profileSha256"})b.put(k,k+"-fixture");return b;}
 static void reset(JSONObject current){StationOnlineClient.own=current;StationOnlineClient.present=true;StationOnlineClient.forceFirstRejection=false;StationOnlineClient.unconfirmed=false;StationOnlineClient.failureStatus=409;StationOnlineClient.failureCode="STATION_MULTIPLAYER_GENERATION_MISMATCH";StationOnlineClient.calls.clear();}
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 public static void main(String[] args)throws Exception{
  boolean fixed="fixed".equals(args[0]);JSONObject b=binding();reset(new JSONObject(b.toString()).put("generation",4));
  Object owner;Constructor<?> ctor=StationGameSession.class.getDeclaredConstructor(Context.class,String.class,JSONObject.class);ctor.setAccessible(true);owner=ctor.newInstance(new Context(),b.getString("roomId"),b);
  Method event=StationGameSession.class.getDeclaredMethod("event",Integer.TYPE,Bundle.class);event.setAccessible(true);event.invoke(owner,4,null);
  Field departure=StationGameSession.class.getDeclaredField("departure");departure.setAccessible(true);ExecutorService service=(ExecutorService)departure.get(owner);service.awaitTermination(3,TimeUnit.SECONDS);
  check(StationOnlineClient.present!=fixed,"actual event 4 departure outcome");
  check(StationOnlineClient.calls.size()==(fixed?3:1),"bounded call count");
  if(!fixed){System.out.println("baseline: actual event 4 silently strands membership on stale generation");return;}
  check(!StationOnlineClient.calls.get(0).getString("requestId").equals(StationOnlineClient.calls.get(2).getString("requestId")),"new idempotency key after proved rejection");
  for(String mismatch:new String[]{"roomId","recoveryProtocol","itemId","engineId","coreSha256","runtimeSha256","contentSha256","profileId","profileSha256"}){
   reset(new JSONObject(b.toString()).put("generation",4).put(mismatch,"different"));boolean failed=false;try{StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,new StationApi.Cancellation());}catch(Exception expected){failed=true;}
   check(StationOnlineClient.present,"mismatched target not mutated "+mismatch);check(StationOnlineClient.calls.size()==2,"no second mutation "+mismatch);if(!mismatch.equals("roomId"))check(failed,"identity rejection "+mismatch);
  }
  for(String code:new String[]{"NETWORK","STATION_MULTIPLAYER_PROFILE_UNAPPROVED","STATION_MULTIPLAYER_MEMBERSHIP_REQUIRED"}){reset(new JSONObject(b.toString()).put("generation",4));StationOnlineClient.failureCode=code;try{StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,new StationApi.Cancellation());throw new AssertionError("wrong error accepted");}catch(StationApi.Failure expected){}check(StationOnlineClient.calls.size()==1,"no blind retry "+code);}
  reset(null);StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,new StationApi.Cancellation());check(StationOnlineClient.calls.size()==2,"fresh absence needs no mutation");
  reset(new JSONObject(b.toString()));StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,new StationApi.Cancellation());check(StationOnlineClient.calls.size()==1,"ordinary generation departure single request");
  reset(new JSONObject(b.toString()).put("generation",4));StationOnlineClient.failureStatus=500;try{StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,new StationApi.Cancellation());throw new AssertionError("500 retried");}catch(StationApi.Failure expected){}check(StationOnlineClient.calls.size()==1,"500 never mutation retry even with mismatch text");
  reset(new JSONObject(b.toString()).put("generation",4));StationApi.Cancellation canceled=new StationApi.Cancellation();canceled.cancel();try{StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,canceled);throw new AssertionError("canceled retried");}catch(StationApi.Failure expected){}check(StationOnlineClient.calls.size()==1,"canceled no fresh mutation");
  reset(new JSONObject(b.toString()));StationOnlineClient.forceFirstRejection=true;try{StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,new StationApi.Cancellation());throw new AssertionError("stale snapshot accepted");}catch(java.io.IOException expected){}check(StationOnlineClient.calls.size()==2,"old snapshot does not authorize second leave");
  reset(new JSONObject(b.toString()));StationOnlineClient.unconfirmed=true;try{StationHumanDeparture.leave(new StationOnlineClient(new Context()),b,new StationApi.Cancellation());throw new AssertionError("unconfirmed own room accepted");}catch(java.io.IOException expected){}check(StationOnlineClient.calls.size()==1,"success without target absence not declared left");
  System.out.println("fixed: actual event 4; exact identity, new request id, signed absence, stale snapshot, cancellation and no blind error retries passed");
 }
}
