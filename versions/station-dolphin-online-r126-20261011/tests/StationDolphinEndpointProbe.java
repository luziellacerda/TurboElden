package org.emulationstation.frontend.netplay;

import java.io.*;
import java.lang.reflect.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import javax.net.ssl.SSLSocketFactory;
import org.json.*;

/** Pure JVM fixtures. No native Dolphin, ROM, Android lifecycle or remote network. */
public final class StationDolphinEndpointProbe {
    private static final AtomicInteger CHECKS = new AtomicInteger();
    private static void check(boolean value, String name) { if (!value) throw new AssertionError(name); CHECKS.incrementAndGet(); }
    private interface Op { void run() throws Exception; }
    private static void rejects(Op op, String name) throws Exception { try { op.run(); } catch (IOException | IllegalArgumentException expected) { CHECKS.incrementAndGet(); return; } throw new AssertionError(name); }
    private static void until(Callable<Boolean> condition, String name) throws Exception {
        long end = System.nanoTime() + TimeUnit.SECONDS.toNanos(4);
        while (!condition.call() && System.nanoTime() < end) Thread.sleep(2);
        check(condition.call(), name);
    }
    private static byte[] frame(int from, int to, int count) {
        byte[] value = new byte[count + 8]; value[0]='D';value[1]='P';value[2]='L';value[3]='1';value[4]=(byte)from;value[5]=(byte)to;value[6]=(byte)(count>>8);value[7]=(byte)count;
        for (int i=8;i<value.length;i++)value[i]=(byte)(i*17); return value;
    }
    private static byte[] join(byte[]... values) throws IOException { ByteArrayOutputStream bytes = new ByteArrayOutputStream(); for(byte[] value:values)bytes.write(value);return bytes.toByteArray(); }
    private static final class FakeEndpoint implements StationMultiplayerEndpoint {
        final Object lock = new Object(); final BlockingQueue<byte[]> outgoing = new LinkedBlockingQueue<>();
        final LinkedHashMap<Long, byte[]> delivered = new LinkedHashMap<>(), attemptedFrames = new LinkedHashMap<>(); final ArrayList<Long> attempts = new ArrayList<>(); final HashSet<Long> consumed = new HashSet<>();
        volatile int retries, awaits; volatile boolean rejected, autoConsume, closed;
        public byte[] takeOutgoing(int timeout) throws InterruptedException { return outgoing.poll(timeout, TimeUnit.MILLISECONDS); }
        public int deliver(long id,byte[] bytes) { synchronized(lock){attempts.add(id);byte[] attempted=attemptedFrames.putIfAbsent(id,bytes.clone());if(attempted!=null&&!Arrays.equals(attempted,bytes))throw new AssertionError("retry changed bytes");if(rejected)return -1;if(retries-->0)return 0;
            byte[] previous=delivered.putIfAbsent(id,bytes.clone());if(previous!=null&&!Arrays.equals(previous,bytes))throw new AssertionError("retry changed bytes");lock.notifyAll();return 1;} }
        public boolean awaitDelivery(long id,int timeout)throws InterruptedException {synchronized(lock){awaits++;if(!autoConsume&&!consumed.contains(id))lock.wait(Math.min(timeout,10));return autoConsume||consumed.contains(id);} }
        void consumeAll(){synchronized(lock){consumed.addAll(delivered.keySet());lock.notifyAll();}}
        int count(){synchronized(lock){return delivered.size();}}
        long firstId(){synchronized(lock){return delivered.keySet().iterator().next();}}
        public void close(){closed=true;}
    }
    private static final class Source implements StationMultiplayerEndpoint.Receiver.Source {
        final StationMultiplayerWire.Bytes rx=new StationMultiplayerWire.Bytes(32768);final int fragment;final long target;volatile boolean cancelled;
        Source(byte[] input,int fragment){this.fragment=fragment;target=input.length;for(int at=0;at<input.length;at+=16384)try{rx.append(at,Arrays.copyOfRange(input,at,Math.min(input.length,at+16384)));}catch(IOException e){throw new AssertionError(e);}}
        public synchronized byte[] read(long at,int max)throws Exception {while(!cancelled&&rx.next<=at)wait(10);if(cancelled)return null;byte[] bytes=rx.read(at);return Arrays.copyOf(bytes,Math.min(bytes.length,Math.min(fragment,max)));}
        public synchronized void confirm(long at)throws Exception {rx.confirm(at);if(at==target)cancelled=true;notifyAll();}
        public boolean cancelled(){return cancelled;}
        public void retryWait(int ms)throws InterruptedException {Thread.sleep(Math.min(ms,2));}
        synchronized void cancel(){cancelled=true;notifyAll();}
        synchronized long confirmed(){return rx.delivered;}
    }
    private static final class Runner implements AutoCloseable {
        final Thread thread;final AtomicReference<Throwable> failure=new AtomicReference<>();final Source source;
        Runner(FakeEndpoint endpoint,Source source,int local,int remote){this.source=source;thread=new Thread(()->{try{new StationMultiplayerEndpoint.Receiver(endpoint,local,remote,0).run(source);}catch(Throwable t){failure.set(t);}},"fixture-DPL1");thread.setDaemon(true);thread.start();}
        void done()throws Exception{thread.join(4000);check(!thread.isAlive(),"receiver finished");if(failure.get()!=null)throw new AssertionError(failure.get());}
        public void close()throws InterruptedException{source.cancel();thread.join(4000);}
    }
    private static void fragmentsAndAcknowledgments() throws Exception {
        for(int fragmentation:new int[]{1,3,7,8,29,1400,16384}){
            FakeEndpoint endpoint=new FakeEndpoint();endpoint.retries=3;byte[] a=frame(1,2,17),b=frame(1,2,1392);Source source=new Source(join(a,b),fragmentation);
            try(Runner run=new Runner(endpoint,source,2,1)){
                until(()->endpoint.count()==1,"complete first frame");check(source.confirmed()==0,"accepted is not delivered");Thread.sleep(35);check(source.confirmed()==0,"timeout does not ACK");check(!endpoint.closed,"timeout never closes endpoint");
                synchronized(endpoint.lock){check(endpoint.attempts.size()==4,"three temporary retries");for(long id:endpoint.attempts)check(id==endpoint.firstId(),"retry retains exact delivery ID");check(Arrays.equals(a,endpoint.delivered.get(endpoint.firstId())),"first payload exact");check(endpoint.attemptedFrames.size()==1,"retry bytes retained before acceptance");}
                endpoint.consumeAll();until(()->endpoint.count()==2,"second complete frame");check(source.confirmed()==a.length,"ACK includes only consumed frame");endpoint.consumeAll();run.done();check(source.confirmed()==a.length+b.length,"all consumed bytes confirmed");
            }
        }
    }
    private static void malformedAndCancellation()throws Exception {
        ArrayList<byte[]> invalid=new ArrayList<>();byte[] bad=frame(1,2,1);bad[0]='X';invalid.add(bad);invalid.add(frame(3,2,1));invalid.add(frame(1,3,1));invalid.add(frame(1,2,0));invalid.add(frame(1,2,1393));
        for(byte[] bytes:invalid){FakeEndpoint endpoint=new FakeEndpoint();Source source=new Source(bytes,1);rejects(()->new StationMultiplayerEndpoint.Receiver(endpoint,2,1,0).run(source),"malformed rejected");check(source.confirmed()==0&&endpoint.count()==0,"malformed cannot confirm or deliver");}
        FakeEndpoint endpoint=new FakeEndpoint();endpoint.retries=100000;Source source=new Source(frame(1,2,10),1);
        FakeEndpoint retryEndpoint=endpoint;
        try(Runner run=new Runner(endpoint,source,2,1)){until(()->{synchronized(retryEndpoint.lock){return retryEndpoint.attempts.size()>=5;}},"bounded backpressure waits");check(source.confirmed()==0&&!endpoint.closed,"backpressure neither ACKs nor closes");source.cancel();run.done();check(endpoint.count()==0,"cancel before native accept retains bytes");}
        endpoint=new FakeEndpoint();source=new Source(Arrays.copyOf(frame(1,2,20),13),1);
        try(Runner run=new Runner(endpoint,source,2,1)){Thread.sleep(40);check(source.confirmed()==0&&endpoint.count()==0,"partial frame waits without ACK");source.cancel();run.done();}
        endpoint=new FakeEndpoint();endpoint.rejected=true;source=new Source(frame(1,2,10),10);FakeEndpoint rejectEndpoint=endpoint;Source rejectSource=source;
        rejects(()->new StationMultiplayerEndpoint.Receiver(rejectEndpoint,2,1,0).run(rejectSource),"native invalid is terminal");check(source.confirmed()==0,"native reject not confirmed");
        rejects(()->StationMultiplayerEndpoint.Dpl1.outgoing(frame(2,1,0),2,1),"empty datagram invalid");rejects(()->StationMultiplayerEndpoint.Dpl1.outgoing(frame(1,2,1),2,1),"outgoing slot spoof invalid");rejects(()->StationMultiplayerEndpoint.Dpl1.outgoing(Arrays.copyOf(frame(2,1,12),15),2,1),"outgoing truncated invalid");
    }
    private static void globalIds()throws Exception {
        HashSet<Long> ids=new HashSet<>();ArrayList<FakeEndpoint> endpoints=new ArrayList<>();ArrayList<Runner> runs=new ArrayList<>();
        for(int remote=2;remote<=4;remote++){FakeEndpoint e=new FakeEndpoint();e.autoConsume=true;endpoints.add(e);byte[][] frames=new byte[100][];for(int i=0;i<frames.length;i++)frames[i]=frame(remote,1,17);runs.add(new Runner(e,new Source(join(frames),5),1,remote));}
        for(Runner r:runs)r.done();for(FakeEndpoint e:endpoints)synchronized(e.lock){for(long id:e.delivered.keySet())check(id>0&&ids.add(id),"process-wide IDs unique across channels");}check(ids.size()==300,"all concurrent frames consumed");
    }
    private static Object field(Object value,String name)throws Exception{Field f=value.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(value);}
    private static Thread methodThread(Object value,String name,AtomicReference<Throwable> error)throws Exception{Method m=value.getClass().getDeclaredMethod(name);m.setAccessible(true);Thread t=new Thread(()->{try{m.invoke(value);}catch(Throwable e){error.set(e);}},"fixture-"+name);t.setDaemon(true);t.start();return t;}
    private static StationMultiplayerTunnel.Listener listener(){return new StationMultiplayerTunnel.Listener(){public void ticket(){}public void ready(){}public void state(boolean w,boolean s){}public void nativeControl(long e,boolean p,boolean v){}public long nativeStatus(){return -1;}public boolean nativeStalled(){return false;}public void unrecoverable(String category){throw new AssertionError(category);}};}
    private static final String TICKET="abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG", PROOF="v1.1791696000.abcdefghijklmnopqrstuv.fixture";
    private static StationMultiplayerTunnel tunnel(StationMultiplayerEndpoint endpoint)throws Exception{return new StationMultiplayerTunnel(new URI("wss://127.0.0.1/v1/station/online/multiplayer/relay"),TICKET,PROOF,262144,false,23456,(SSLSocketFactory)SSLSocketFactory.getDefault(),listener(),endpoint,2,1);}
    private static void append(StationMultiplayerTunnel tunnel,long offset,byte[] bytes)throws Exception{Object gate=field(tunnel,"gate");synchronized(gate){((StationMultiplayerWire.Bytes)field(tunnel,"rx")).append(offset,bytes);gate.notifyAll();}}
    private static long received(StationMultiplayerTunnel t)throws Exception{Object gate=field(t,"gate");synchronized(gate){return ((StationMultiplayerWire.Bytes)field(t,"rx")).delivered;}}
    private static void actualTunnel()throws Exception {
        FakeEndpoint e=new FakeEndpoint();StationMultiplayerTunnel t=tunnel(e);AtomicReference<Throwable> error=new AtomicReference<>();Thread in=methodThread(t,"nativeInput",error),out=methodThread(t,"nativeOutput",error);
        try{until(()->(boolean)field(t,"localReady"),"endpoint prepared");check(field(t,"accept")==null&&t.localPort()==23456,"native endpoint opens no listener socket");
            byte[] incoming=frame(1,2,1392);for(int at=0;at<incoming.length;at+=7)append(t,at,Arrays.copyOfRange(incoming,at,Math.min(incoming.length,at+7)));
            until(()->e.count()==1,"tunnel reassembles segmented TSR3 bytes");check(received(t)==0,"tunnel does not ACK native queue admission");e.consumeAll();until(()->received(t)==incoming.length,"tunnel ACK after native consumption");
            byte[] outgoing=frame(2,1,1392);e.outgoing.add(outgoing);StationMultiplayerWire.Bytes tx=(StationMultiplayerWire.Bytes)field(t,"tx");until(()->{synchronized(field(t,"gate")){return tx.next==outgoing.length;}},"outgoing DPL1 bytes recorded");synchronized(field(t,"gate")){check(Arrays.equals(outgoing,tx.read(0)),"outgoing bytes exact");}
            byte[] fill=new byte[16384];synchronized(field(t,"gate")){while(tx.credit()>0){int n=Math.min(fill.length,tx.credit());tx.append(tx.next,Arrays.copyOf(fill,n));}}
            long fullOffset=tx.next;e.outgoing.add(frame(2,1,5));Thread.sleep(40);synchronized(field(t,"gate")){check(tx.next==fullOffset,"credit exhaustion prevents stream append");check(e.outgoing.size()==1||(boolean)field(t,"endpointReading"),"queued or single bounded frame prevents premature READY");tx.confirm(tx.next);field(t,"gate").notifyAll();}until(()->{synchronized(field(t,"gate")){return tx.next==fullOffset+13;}},"credit release resumes reader");check(error.get()==null,"endpoint threads healthy");
        }finally{t.close();in.join(1500);out.join(1500);}check(!in.isAlive()&&!out.isAlive()&&e.closed,"explicit close releases endpoint workers");
    }
    private static void legacySocket()throws Exception {
        StationMultiplayerTunnel t=tunnel(null);check(field(t,"accept")!=null,"default guest still has TCP listener");AtomicReference<Throwable> error=new AtomicReference<>();Thread in=methodThread(t,"nativeInput",error),out=methodThread(t,"nativeOutput",error);
        try(Socket nativeSocket=new Socket("127.0.0.1",t.localPort())){nativeSocket.setSoTimeout(4000);byte[] sent=new byte[4096];new Random(71).nextBytes(sent);nativeSocket.getOutputStream().write(sent);
            StationMultiplayerWire.Bytes tx=(StationMultiplayerWire.Bytes)field(t,"tx");until(()->{synchronized(field(t,"gate")){return tx.next==sent.length;}},"legacy TCP input");synchronized(field(t,"gate")){check(Arrays.equals(sent,tx.read(0)),"legacy TCP input unchanged");}
            byte[] incoming=new byte[8192];new Random(29).nextBytes(incoming);append(t,0,incoming);byte[] result=nativeSocket.getInputStream().readNBytes(incoming.length);check(Arrays.equals(incoming,result),"legacy TCP output unchanged");until(()->received(t)==incoming.length,"legacy confirms after socket write");t.close();
        }finally{t.close();in.join(1500);out.join(1500);}check(!in.isAlive()&&!out.isAlive()&&error.get()==null,"legacy closes cleanly");
    }
    private static JSONObject ticket(String id,boolean host,int slot){return new JSONObject().put("linkId",id).put("path","/v1/station/online/multiplayer/relay").put("protocol","station-stream.v3").put("expiresInSeconds",45).put("windowBytes",262144).put("hostSide",host).put("ownerSlot",slot).put("ticket",TICKET).put("requestProof",PROOF);}
    private static JSONObject launch(boolean host,int count,int slot,int mask){JSONArray links=new JSONArray();for(int guest=2;guest<=4;guest++)if((mask&(1<<(guest-1)))!=0&&(host||guest==slot)){String id="fixture-"+guest;links.put(new JSONObject().put("linkId",id).put("guestSlot",guest).put("ticket",ticket(id,host,slot)));}return new JSONObject().put("role",host?"host":"client").put("participantCount",count).put("localSlot",slot).put("expectedDeviceMask",mask).put("port",23456).put("multiplayerLinks",links);}
    private static void sessionBinding()throws Exception{
        StationMultiplayerSession.Listener listener=new StationMultiplayerSession.Listener(){public void nativeControl(long e,boolean p,boolean v){}public long nativeStatus(){return -1;}public boolean nativeStalled(){return false;}public boolean bind(int p,int s){throw new AssertionError("datagram binding called");}public void unbind(int p,int s){throw new AssertionError("datagram binding called");}public void ticket(String l,long s){}public void ready(){}public void state(boolean w,boolean s){}public void fatal(String c){}public void trace(String e){}};
        for(int count=2;count<=4;count++){ArrayList<String> created=new ArrayList<>();StationMultiplayerEndpoint.Factory factory=(local,remote)->{created.add(local+":"+remote);return new FakeEndpoint();};
            try(StationMultiplayerSession s=new StationMultiplayerSession(launch(true,count,1,(1<<count)-1),listener,factory)){check(created.size()==count-1,"exact host link count");for(int remote=2;remote<=count;remote++)check(created.contains("1:"+remote),"authenticated host endpoint slots");}
            for(int slot=2;slot<=count;slot++){created.clear();try(StationMultiplayerSession s=new StationMultiplayerSession(launch(false,count,slot,(1<<count)-1),listener,factory)){check(created.equals(Collections.singletonList(slot+":1")),"authenticated guest endpoint slots");}}
        }
        try(StationMultiplayerSession s=new StationMultiplayerSession(launch(true,3,1,13),listener,(a,b)->new FakeEndpoint())){check(s.localPort()==23456,"sparse signed roster supported");}
        JSONObject bad=launch(false,2,2,3);bad.getJSONArray("multiplayerLinks").getJSONObject(0).getJSONObject("ticket").put("ownerSlot",1);rejects(()->new StationMultiplayerSession(bad,listener,(a,b)->new FakeEndpoint()),"ticket role rejected before endpoint");
        JSONObject invalid=launch(true,2,1,3);invalid.getJSONArray("multiplayerLinks").getJSONObject(0).put("guestSlot",3);rejects(()->new StationMultiplayerSession(invalid,listener,(a,b)->new FakeEndpoint()),"slot outside signed mask rejected");
        rejects(()->new StationMultiplayerSession(launch(true,2,1,3),listener,(a,b)->null),"missing endpoint rejected");
    }
    private static void idExhaustion()throws Exception {Field field=StationMultiplayerEndpoint.Dpl1.class.getDeclaredField("DELIVERY_IDS");field.setAccessible(true);AtomicLong ids=(AtomicLong)field.get(null);long previous=ids.getAndSet(Long.MAX_VALUE);try{check(StationMultiplayerEndpoint.Dpl1.nextDeliveryId()==Long.MAX_VALUE,"last positive delivery ID valid");rejects(()->StationMultiplayerEndpoint.Dpl1.nextDeliveryId(),"ID exhaustion cannot wrap");rejects(()->StationMultiplayerEndpoint.Dpl1.nextDeliveryId(),"exhaustion remains terminal");}finally{ids.set(previous);}}
    public static void main(String[] args)throws Exception{long start=System.nanoTime();fragmentsAndAcknowledgments();malformedAndCancellation();globalIds();actualTunnel();legacySocket();sessionBinding();idExhaustion();System.out.println("PASS checks="+CHECKS.get()+" elapsedMs="+TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-start));}
}
