package org.emulationstation.frontend.netplay;
import java.lang.reflect.*;
import java.util.concurrent.*;
import org.emulationstation.frontend.station.StationApi;
import org.json.JSONObject;

/** Executes the real session event/pause methods without Android or network initialization.
 * A null app forces the existing terminal report catch before any HTTP can occur.
 */
public final class StationGameSessionLifecycleTest {
    private static int checks;
    private static void ok(boolean value){checks++;if(!value)throw new AssertionError("session lifecycle check "+checks);}
    private static Field field(String name)throws Exception{Field f=StationGameSession.class.getDeclaredField(name);f.setAccessible(true);return f;}
    private static void event(Object owner,int value)throws Exception{Method m=StationGameSession.class.getDeclaredMethod("event",int.class,android.os.Bundle.class);m.setAccessible(true);m.invoke(owner,value,null);}
    private static Object owner(boolean recovery,ScheduledThreadPoolExecutor worker)throws Exception{
        Class<?> unsafe=Class.forName("sun.misc.Unsafe");Field singleton=unsafe.getDeclaredField("theUnsafe");singleton.setAccessible(true);
        Object result=unsafe.getMethod("allocateInstance",Class.class).invoke(singleton.get(null),StationGameSession.class);
        field("recovery").setBoolean(result,recovery);field("worker").set(result,worker);field("room").set(result,"fixture-room");field("binding").set(result,new JSONObject().put("generation",1));field("visible").setBoolean(result,true);field("pending").set(result,new StationApi.Cancellation());
        field("heartbeat").set(result,worker.scheduleWithFixedDelay(()->{throw new AssertionError("unexpected heartbeat");},60,60,TimeUnit.SECONDS));
        return result;
    }
    public static void main(String[] args)throws Exception{
        for(boolean recovery:new boolean[]{false,true}){
            ScheduledThreadPoolExecutor worker=new ScheduledThreadPoolExecutor(1);
            try{
                Object owner=owner(recovery,worker);ScheduledFuture<?> heartbeat=(ScheduledFuture<?>)field("heartbeat").get(owner);StationApi.Cancellation pending=(StationApi.Cancellation)field("pending").get(owner);
                event(owner,2);ok(!field("visible").getBoolean(owner));ok(!field("closed").getBoolean(owner));ok(heartbeat.isCancelled()!=recovery);ok(pending.cancelled()!=recovery);ok(!worker.isShutdown());
                event(owner,4);ok(worker.awaitTermination(3,TimeUnit.SECONDS));ok(((ExecutorService)field("departure").get(owner)).awaitTermination(3,TimeUnit.SECONDS));ok(field("closed").getBoolean(owner));ok(heartbeat.isCancelled());ok(pending.cancelled());ok(field("reply").get(owner)==null);
                long reports=worker.getCompletedTaskCount();event(owner,4);event(owner,6);ok(worker.getCompletedTaskCount()==reports);
            }finally{worker.shutdownNow();}
        }
        ScheduledThreadPoolExecutor worker=new ScheduledThreadPoolExecutor(1);
        try{
            Object owner=owner(true,worker);ScheduledFuture<?> heartbeat=(ScheduledFuture<?>)field("heartbeat").get(owner);StationApi.Cancellation pending=(StationApi.Cancellation)field("pending").get(owner);
            event(owner,6);ok(worker.awaitTermination(3,TimeUnit.SECONDS));ok(!field("closed").getBoolean(owner));ok(field("failed").getBoolean(owner));ok(!field("visible").getBoolean(owner));ok(heartbeat.isCancelled());ok(pending.cancelled());ok(field("reply").get(owner)==null);
            long reports=worker.getCompletedTaskCount();ok(reports==1);event(owner,6);ok(worker.getCompletedTaskCount()==reports);ok(field("departure").get(owner)==null);
            for(int ignored:new int[]{1,2,3,5,6}){event(owner,ignored);ok(!field("visible").getBoolean(owner));ok(worker.isTerminated());ok(worker.getCompletedTaskCount()==reports);}
            event(owner,4);ExecutorService departure=(ExecutorService)field("departure").get(owner);ok(departure!=null);ok(departure.awaitTermination(3,TimeUnit.SECONDS));ok(field("humanLeft").getBoolean(owner));
            event(owner,4);event(owner,6);ok(field("departure").get(owner)==departure);ok(worker.getCompletedTaskCount()==reports);
        }finally{worker.shutdownNow();}
        // Serialize main-thread submission with the worker's room-ended transition.
        for(int iteration=0;iteration<40;iteration++){
            ScheduledThreadPoolExecutor raceWorker=new ScheduledThreadPoolExecutor(1);
            try{
                Object owner=owner(true,raceWorker);java.util.concurrent.atomic.AtomicReference<Throwable> error=new java.util.concurrent.atomic.AtomicReference<>();CountDownLatch gate=new CountDownLatch(1);
                Method terminal=StationGameSession.class.getDeclaredMethod("roomEnded");terminal.setAccessible(true);
                Thread first=new Thread(()->{try{gate.await();event(owner,3);}catch(Throwable failure){error.set(failure);}});
                Thread second=new Thread(()->{try{gate.await();terminal.invoke(owner);}catch(Throwable failure){error.set(failure);}});
                first.start();second.start();gate.countDown();first.join();second.join();ok(error.get()==null);ok(raceWorker.awaitTermination(3,TimeUnit.SECONDS));ok(field("closed").getBoolean(owner));
            }finally{raceWorker.shutdownNow();}
        }
        System.out.println("StationGameSessionLifecycleTest: "+checks+" checks passed");
    }
}
