package org.emulationstation.frontend.netplay;
import android.app.Activity;import android.os.ResultReceiver;import java.lang.reflect.*;import java.lang.management.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;import org.json.*;import sun.misc.Unsafe;
/** Executes unmodified production Session.closeByHuman and production transport
 * unrecoverable callback. Only Android/native/IO edges are fixtures. */
public final class StationDolphinExitDeadlockProbe{
 static void set(Object o,String n,Object v)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);f.set(o,v);}
 static Object get(Object o,String n)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(o);}
 public static void main(String[] args)throws Exception{
  boolean fixed="fixed".equals(args[0]);Field uf=Unsafe.class.getDeclaredField("theUnsafe");uf.setAccessible(true);Unsafe unsafe=(Unsafe)uf.get(null);
  Class<?> sessionType=Class.forName("org.emulationstation.frontend.netplay.StationDolphinSession$Session");Object session=unsafe.allocateInstance(sessionType);
  set(session,"entry",new Activity());set(session,"events",new ResultReceiver());set(session,"owner",new StationSessionLink());
  ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"cleanup-fixture");t.setDaemon(true);return t;});set(session,"worker",worker);
  JSONObject ticket=new JSONObject().put("linkId","fixture").put("path","/v1/station/online/multiplayer/relay").put("protocol","station-stream.v3").put("expiresInSeconds",60).put("windowBytes",262144).put("hostSide",true).put("ownerSlot",1).put("ticket",String.join("",Collections.nCopies(43,"a"))).put("requestProof","fixture");
  JSONObject launch=new JSONObject().put("role","host").put("participantCount",2).put("localSlot",1).put("expectedDeviceMask",3).put("port",0).put("multiplayerLinks",new JSONArray().put(new JSONObject().put("linkId","fixture").put("guestSlot",2).put("ticket",ticket)));
  StationMultiplayerSession transport=new StationMultiplayerSession(launch,(StationMultiplayerSession.Listener)session);set(session,"transport",transport);
  Object channel=((ArrayList<?>)get(transport,"channels")).get(0);StationMultiplayerTunnel tunnel=(StationMultiplayerTunnel)get(channel,"tunnel");
  Method close=sessionType.getDeclaredMethod("closeByHuman",Runnable.class);close.setAccessible(true);CountDownLatch done=new CountDownLatch(1),ownsTransport=new CountDownLatch(1);
  Thread ui=new Thread(()->{try{close.invoke(session,(Runnable)done::countDown);}catch(Exception e){throw new AssertionError(e);}},"fixture-ui");ui.setDaemon(true);ui.start();
  if(!ResultReceiver.entered.await(2,TimeUnit.SECONDS))throw new AssertionError("human authority not reached");
  Thread callback=new Thread(()->{synchronized(transport){ownsTransport.countDown();tunnel.listener.unrecoverable("TEST");}},"fixture-native-fatal");callback.setDaemon(true);callback.start();
  if(!ownsTransport.await(2,TimeUnit.SECONDS))throw new AssertionError("callback transport monitor not held");
  long until=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);while(callback.getState()!=Thread.State.BLOCKED&&System.nanoTime()<until)Thread.yield();
  if(callback.getState()!=Thread.State.BLOCKED)throw new AssertionError("callback did not contend Session");ResultReceiver.release.countDown();
  if(fixed){if(!done.await(2,TimeUnit.SECONDS))throw new AssertionError("fixed human cleanup stalled");ui.join(1000);callback.join(1000);if(ui.isAlive()||callback.isAlive())throw new AssertionError("fixed thread leaked");System.out.println("fixed: actual Session and actual transport callback complete without monitor cycle");}
  else{until=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);long[] ids=null;while(System.nanoTime()<until&&(ids=ManagementFactory.getThreadMXBean().findDeadlockedThreads())==null)Thread.yield();if(ids==null)throw new AssertionError("baseline deadlock not reproduced");Set<Long> found=new HashSet<>();for(long id:ids)found.add(id);if(!found.contains(ui.getId())||!found.contains(callback.getId()))throw new AssertionError("unexpected deadlock");System.out.println("baseline: deterministic ABBA proven by ThreadMXBean for UI and production fatal callback");}
  worker.shutdownNow();
 }
}