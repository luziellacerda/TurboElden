package org.emulationstation.frontend.netplay;

import java.io.IOException;
import java.net.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public final class StationHostConnectorTest {
    private static int checks;
    private static void check(boolean value,String name){checks++;if(!value)throw new AssertionError(name);}
    public static void main(String[] args)throws Exception {
        ExecutorService worker=Executors.newSingleThreadExecutor();
        AtomicReference<Socket> pending=new AtomicReference<>();
        AtomicBoolean cancelled=new AtomicBoolean();
        Semaphore hint=new Semaphore(0);
        int port;
        try(ServerSocket reserve=new ServerSocket(0,1,InetAddress.getByName("127.0.0.1"))){port=reserve.getLocalPort();}
        final int delayedPort=port;
        try {
            Future<Socket> result=worker.submit(()->StationHostConnector.connect(delayedPort,
                    System.nanoTime()+TimeUnit.SECONDS.toNanos(3),cancelled::get,pending::set,hint));
            Thread.sleep(150);
            check(!result.isDone(),"No readiness before a real listening socket");
            try(ServerSocket nativeHost=new ServerSocket(delayedPort,1,InetAddress.getByName("127.0.0.1"));
                Socket accepted=nativeHost.accept();Socket stream=result.get(2,TimeUnit.SECONDS)) {
                accepted.setSoTimeout(2000);stream.setSoTimeout(2000);
                check(stream==pending.get(),"Retain the successful socket instead of opening a probe");
                stream.getOutputStream().write(79);
                check(accepted.getInputStream().read()==79,"Retained connection carries game data");
                accepted.getOutputStream().write(83);
                check(stream.getInputStream().read()==83,"Retained connection carries reverse data");
                check(stream.getTcpNoDelay(),"Small game packets are sent immediately");
                check(stream.getInetAddress().isLoopbackAddress(),"Connect only to loopback");
            }
            hint.release(); // A native hint alone must never become readiness.
            long started=System.nanoTime();
            try{StationHostConnector.connect(port,started+TimeUnit.MILLISECONDS.toNanos(180),
                    cancelled::get,pending::set,hint);throw new AssertionError("False readiness without socket");}
            catch(IOException expected){check(pending.get().isClosed(),"Deadline closes all unsuccessful candidates");}
            check(System.nanoTime()-started<TimeUnit.SECONDS.toNanos(1),"Deadline bounds startup wait");
            Future<Socket> stopped=worker.submit(()->StationHostConnector.connect(delayedPort,
                    System.nanoTime()+TimeUnit.SECONDS.toNanos(3),cancelled::get,pending::set,hint));
            Thread.sleep(80);cancelled.set(true);hint.release();
            try{stopped.get(1,TimeUnit.SECONDS);throw new AssertionError("Cancellation ignored");}
            catch(ExecutionException expected){check(expected.getCause() instanceof IOException,"Cancellation stops connection wait");}
            check(pending.get().isClosed(),"Cancellation closes its pending socket");
        } finally {worker.shutdownNow();}
        System.out.println("{\"passed\":true,\"checks\":"+checks+",\"scope\":\"Real loopback TCP: late listener without JNI, retained stream, false native hint, deadline and cancellation\"}");
    }
}
