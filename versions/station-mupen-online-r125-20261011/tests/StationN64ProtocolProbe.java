package org.emulationstation.frontend.netplay;

import java.io.*;
import java.lang.reflect.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Pure JVM loopback fixtures. No Android, ROM, native core, server credentials,
 * or gameplay. The peers implement only the documented upstream wire format. */
public final class StationN64ProtocolProbe {
    static int checks;
    static final InetAddress LOOP;
    static { try { LOOP=InetAddress.getByName("127.0.0.1"); } catch(Exception e) { throw new ExceptionInInitializerError(e); } }
    static void check(boolean result,String name) { checks++;if(!result)throw new AssertionError(name); }
    interface Io {void run()throws Exception;}
    static void rejected(Io operation,String name)throws Exception {try {operation.run();throw new AssertionError("accepted "+name);}catch(IOException expected){checks++;}}
    static byte[] ints(int... values)throws IOException {ByteArrayOutputStream b=new ByteArrayOutputStream();DataOutputStream d=new DataOutputStream(b);for(int n:values)d.writeInt(n);return b.toByteArray();}
    static byte[] register(int slot,int id)throws IOException {ByteArrayOutputStream b=new ByteArrayOutputStream();DataOutputStream d=new DataOutputStream(b);d.writeByte(5);d.writeByte(slot);d.writeByte(1);d.writeByte(0);d.writeInt(id);return b.toByteArray();}
    static byte[] input(int slot,int count,int keys)throws IOException {ByteArrayOutputStream b=new ByteArrayOutputStream();DataOutputStream d=new DataOutputStream(b);d.writeByte(0);d.writeByte(slot);d.writeInt(count);d.writeInt(keys);d.writeByte(1);return b.toByteArray();}
    static byte[] request(int target,int owner,int count)throws IOException {ByteArrayOutputStream b=new ByteArrayOutputStream();DataOutputStream d=new DataOutputStream(b);d.writeByte(2);d.writeByte(target);d.writeInt(100+owner);d.writeInt(count);d.writeByte(0);d.writeByte(2);return b.toByteArray();}
    static byte[] settings(int cpu)throws IOException {return ints(2,0,0,0,cpu,0);}
    static void registerDirect(StationN64Server s,int slot)throws Exception {ByteArrayOutputStream response=new ByteArrayOutputStream();try{s.tcp(slot,new ByteArrayInputStream(register(slot,100+slot)),response);}catch(EOFException end){}check(Arrays.equals(response.toByteArray(),new byte[]{1,2}),"registered slot "+slot);}
    static void wire()throws Exception {
        byte[] payload=new byte[16384];new Random(7).nextBytes(payload);ByteArrayOutputStream stream=new ByteArrayOutputStream();StationN64Wire.header(stream);StationN64Wire.frame(stream,1,payload,0,payload.length);StationN64Wire.frame(stream,2,payload,0,512);
        AtomicInteger frames=new AtomicInteger();InputStream fragmented=new FilterInputStream(new ByteArrayInputStream(stream.toByteArray())){@Override public int read(byte[] b,int o,int n)throws IOException{return super.read(b,o,Math.min(1,n));}};
        try{StationN64Wire.read(fragmented,new StationN64Wire.Receiver(){public void tcp(byte[] b){check(Arrays.equals(b,payload),"fragmented max TCP");frames.incrementAndGet();}public void udp(byte[] b){check(Arrays.equals(b,Arrays.copyOf(payload,512)),"fragmented max UDP");frames.incrementAndGet();}});}catch(EOFException end){}
        check(frames.get()==2,"two wire frames");
        for(byte[] bad:new byte[][]{{0,0,0,0,1},{0x53,0x4e,0x36,0x34,2},{0x53,0x4e,0x36,0x34,1,3,0,1,0},{0x53,0x4e,0x36,0x34,1,1,0,0},{0x53,0x4e,0x36,0x34,1,2,2,1},{0x53,0x4e,0x36,0x34,1,1,0,2,0}})rejected(()->StationN64Wire.read(new ByteArrayInputStream(bad),new StationN64Wire.Receiver(){public void tcp(byte[] b){throw new AssertionError();}public void udp(byte[] b){throw new AssertionError();}}),"malformed wire");
        for(String name:new String[]{"../save","a/b","a\\b","",".","..","bad\nname"})rejected(()->StationN64Wire.filename(new ByteArrayInputStream((name+"\0").getBytes(StandardCharsets.UTF_8))),"save path");
        check("Mario Kart 64.sra".equals(StationN64Wire.filename(new ByteArrayInputStream("Mario Kart 64.sra\0".getBytes(StandardCharsets.UTF_8)))),"plain save filename");
        for(String name:new String[]{"a..b.sra","L'été (Europe).sra","ゼルダの伝説.sra","é".repeat(63)+"a"})check(name.equals(StationN64Wire.filename(new ByteArrayInputStream((name+"\0").getBytes(StandardCharsets.UTF_8)))),"UTF8 basename "+name);
        for(byte[] malformed:new byte[][]{{(byte)0xc3,0},{(byte)0xc0,(byte)0xaf,0},{(byte)0xed,(byte)0xa0,(byte)0x80,0}})rejected(()->StationN64Wire.filename(new ByteArrayInputStream(malformed)),"malformed UTF8 filename");
        rejected(()->StationN64Wire.filename(new ByteArrayInputStream(("é".repeat(64)+"\0").getBytes(StandardCharsets.UTF_8))),"filename byte budget");
        StationN64Wire.Queue queue=new StationN64Wire.Queue();ExecutorService e=Executors.newSingleThreadExecutor();byte[] capacity=new byte[262145];Future<?> producer=e.submit(()->{try{queue.put(capacity);}catch(IOException x){throw new UncheckedIOException(x);}});
        try{producer.get(120,TimeUnit.MILLISECONDS);throw new AssertionError("queue unbounded");}catch(TimeoutException bounded){checks++;}
        check(queue.read()==0,"queue consumes one");producer.get(1,TimeUnit.SECONDS);queue.close();e.shutdownNow();
        StationN64Wire.Queue cancelled=new StationN64Wire.Queue();ExecutorService e2=Executors.newSingleThreadExecutor();Future<Boolean> blocked=e2.submit(()->{try{cancelled.put(capacity);return false;}catch(IOException x){return true;}});Thread.sleep(30);cancelled.close();check(blocked.get(1,TimeUnit.SECONDS),"queue cancel wakes blocked producer");e2.shutdownNow();
    }
    static void directServer()throws Exception {
        for(int mask:new int[]{3,7,15,11}){
            AtomicInteger failures=new AtomicInteger();try(StationN64Server s=new StationN64Server(mask,r->failures.incrementAndGet())){
                ExecutorService executor=Executors.newSingleThreadExecutor();Future<?> waiting=executor.submit(()->{try{s.awaitRegistered();}catch(IOException x){throw new UncheckedIOException(x);}});
                int last=31-Integer.numberOfLeadingZeros(mask);for(int slot=0;slot<4;slot++)if((mask&(1<<slot))!=0&&slot!=last)registerDirect(s,slot);
                try{waiting.get(80,TimeUnit.MILLISECONDS);throw new AssertionError("early roster");}catch(TimeoutException expected){checks++;}
                registerDirect(s,last);waiting.get(1,TimeUnit.SECONDS);check(failures.get()==0,"roster without failure");executor.shutdownNow();
                rejected(()->s.udp(0,input(last,0,1),b->{}),"UDP slot spoof");
                rejected(()->s.udp(0,new byte[]{0},b->{}),"short input");
                rejected(()->s.udp(0,input(0,-1,1),b->{}),"negative input");
                rejected(()->s.udp(0,input(0,8191,1),b->{}),"future input bound");
                AtomicReference<byte[]> data=new AtomicReference<>();s.udp(0,request(last,0,3),data::set);check(data.get()==null,"missing input not guessed");
                s.udp(last,input(last,1,0x11223344),b->{});check(failures.get()==0,"later missing input remains live");
            }
        }
        for(int mask:new int[]{0,1,2,16,17})rejected(()->new StationN64Server(mask,r->{}),"invalid mask");
        for(int cpu:new int[]{0,2}){try(StationN64Server s=new StationN64Server(3,r->{})){ByteArrayOutputStream b=new ByteArrayOutputStream();b.write(register(0,100));b.write(3);b.write(settings(cpu));rejected(()->s.tcp(0,new ByteArrayInputStream(b.toByteArray()),new ByteArrayOutputStream()),"CPU setting mismatch");}}
        try(StationN64Server s=new StationN64Server(3,r->{})){
            registerDirect(s,0);registerDirect(s,1);for(int n=0;n<=8190;n++)s.udp(0,input(0,n,n),b->{});
            Field players=StationN64Server.class.getDeclaredField("players");players.setAccessible(true);Object p=((Object[])players.get(s))[0];Field map=p.getClass().getDeclaredField("input");map.setAccessible(true);
            check(((Map<?,?>)map.get(p)).size()==8193,"missing peer input history bounded by window");
            rejected(()->s.udp(0,input(0,8191,0),b->{}),"missing peer cannot grow forever");
        }
        try(StationN64Server s=new StationN64Server(3,r->{})){ExecutorService e=Executors.newSingleThreadExecutor();Future<Boolean> f=e.submit(()->{try{s.awaitRegistered();return false;}catch(IOException x){return true;}});s.close();check(f.get(1,TimeUnit.SECONDS),"cancel missing roster");e.shutdownNow();}
        for(int operation:new int[]{2,4}){
            StationN64Server s=new StationN64Server(3,r->{});ByteArrayOutputStream b=new ByteArrayOutputStream();b.write(register(1,101));b.write(operation);if(operation==2)b.write("waiting.sra\0".getBytes(StandardCharsets.UTF_8));ExecutorService e=Executors.newSingleThreadExecutor();Future<Boolean> f=e.submit(()->{try{s.tcp(1,new ByteArrayInputStream(b.toByteArray()),new ByteArrayOutputStream());return false;}catch(IOException x){return true;}});
            Thread.sleep(30);s.close();check(f.get(1,TimeUnit.SECONDS),"cancel waiting settings/save "+operation);e.shutdownNow();
        }
    }
    static final class Tunnel implements AutoCloseable {
        final ServerSocket entry;final Socket relay;final Thread accept;final AtomicReference<Throwable> failure=new AtomicReference<>();volatile Socket guest;
        Tunnel(StationN64Mux host,int slot)throws IOException {
            entry=new ServerSocket(0,1,LOOP);relay=new Socket();relay.bind(new InetSocketAddress(LOOP,0));check(host.bind(relay.getLocalPort(),slot),"bind exact slot "+slot);relay.connect(new InetSocketAddress(LOOP,host.hubPort()));relay.setTcpNoDelay(true);
            accept=daemon(()->{try{guest=entry.accept();guest.setTcpNoDelay(true);daemon(()->copy(guest,relay),"fixture-forward");copy(relay,guest);}catch(Throwable x){failure.compareAndSet(null,x);}},"fixture-tunnel");
        }
        int port(){return entry.getLocalPort();}
        void copy(Socket from,Socket to){try{byte[] b=new byte[17];InputStream input=from.getInputStream();OutputStream out=to.getOutputStream();int n;while((n=input.read(b))>=0){for(int at=0;at<n;){int count=Math.min(1+(at%7),n-at);out.write(b,at,count);out.flush();at+=count;}}}catch(IOException normalClose){} }
        public void close(){try{entry.close();}catch(IOException ignored){}try{relay.close();}catch(IOException ignored){}try{if(guest!=null)guest.close();}catch(IOException ignored){} }
    }
    interface RunnableIo {void run();}
    static Thread daemon(RunnableIo r,String name){Thread t=new Thread(r::run,name);t.setDaemon(true);t.start();return t;}
    static final class Fixture implements AutoCloseable {
        final int count;final StationN64Mux[] mux=new StationN64Mux[4];final Socket[] core=new Socket[4];final DatagramSocket[] udp=new DatagramSocket[4];final Tunnel[] tunnel=new Tunnel[4];final List<String> failure=Collections.synchronizedList(new ArrayList<>());
        Fixture(int count)throws Exception {this.count=count;int mask=(1<<count)-1;mux[0]=new StationN64Mux(true,0,mask,failure::add);mux[0].start(0);
            for(int s=1;s<count;s++){tunnel[s]=new Tunnel(mux[0],s);mux[s]=new StationN64Mux(false,s,mask,failure::add);mux[s].start(tunnel[s].port());}
            for(int s=0;s<count;s++){core[s]=new Socket(LOOP,mux[s].corePort());core[s].setTcpNoDelay(true);core[s].setSoTimeout(2500);core[s].getOutputStream().write(register(s,100+s));check(Arrays.equals(StationN64Wire.exact(core[s].getInputStream(),2),new byte[]{1,2}),"mux registered "+count+"/"+s);udp[s]=new DatagramSocket(new InetSocketAddress(LOOP,0));udp[s].setSoTimeout(180);}
            mux[0].awaitRegistered();check(failure.isEmpty(),"no failure after exact mux roster "+count);
        }
        void packet(int owner,byte[] b)throws IOException {udp[owner].send(new DatagramPacket(b,b.length,new InetSocketAddress(LOOP,mux[owner].corePort())));}
        byte[] receive(int owner)throws IOException {byte[] b=new byte[512];DatagramPacket p=new DatagramPacket(b,b.length);udp[owner].receive(p);return Arrays.copyOf(b,p.getLength());}
        public void close(){for(int s=0;s<count;s++)if(mux[s]!=null)mux[s].close();for(int s=0;s<count;s++){if(tunnel[s]!=null)tunnel[s].close();if(core[s]!=null)try{core[s].close();}catch(IOException ignored){}if(udp[s]!=null)udp[s].close();}}
    }
    static void loopback(int count)throws Exception {
        try(Fixture f=new Fixture(count)){
            f.core[0].getOutputStream().write(6);byte[] roster=StationN64Wire.exact(f.core[0].getInputStream(),24);for(int s=0;s<4;s++){check(StationN64Wire.int32(roster,s*6)==(s<count?100+s:0),"roster exact "+count+"/"+s);check(roster[s*6+4]==(s<count?1:0),"plugin exact roster");check(roster[s*6+5]==0,"raw input off");}
            OutputStream out=f.core[0].getOutputStream();out.write(3);out.write(settings(1));out.flush();
            for(int s=1;s<count;s++){f.core[s].getOutputStream().write(4);check(Arrays.equals(StationN64Wire.exact(f.core[s].getInputStream(),24),settings(1)),"settings synced "+count+"/"+s);}
            byte[] save=new byte[524291];new Random(33).nextBytes(save);DataOutputStream d=new DataOutputStream(out);d.writeByte(1);d.write("MarioKart64.sra\0".getBytes(StandardCharsets.UTF_8));d.writeInt(save.length);d.write(save);d.flush();
            for(int s=1;s<count;s++){OutputStream guest=f.core[s].getOutputStream();guest.write(2);guest.write("MarioKart64.sra\0".getBytes(StandardCharsets.UTF_8));guest.flush();check(Arrays.equals(StationN64Wire.exact(f.core[s].getInputStream(),save.length),save),"fragmented large save "+count+"/"+s);}
            for(int s=0;s<count;s++)f.packet(s,input(s,0,0x102030+s));
            for(int s=0;s<count;s++){boolean found=false;long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);while(System.nanoTime()<deadline&&!found){try{byte[] b=f.receive(s);check(b[0]==1&&b.length==5+(b[4]&255)*9,"input packet bounds");int owner=b[1]&255;for(int at=5;at<b.length;at+=9)if(StationN64Wire.int32(b,at)==2){check(StationN64Wire.int32(b,at+4)==0x102030+owner,"input correct remote slot");found=true;}}catch(SocketTimeoutException wait){}}
                check(found,"delayed input returned "+count+"/"+s);}
            check(f.failure.isEmpty(),"loopback final no failures "+count);
        }
    }
    static void bindAdmission()throws Exception {
        try(StationN64Mux m=new StationN64Mux(true,0,3,r->{})){
            check(!m.bind(30000,2),"bind excludes missing signed slot");check(m.bind(30001,1),"bind roster slot");check(!m.bind(30002,1),"duplicate slot link rejected");m.unbind(30001,1);check(m.bind(30002,1),"bind after explicit unbind");
        }
    }
    static void backpressure()throws Exception {
        AtomicInteger failures=new AtomicInteger();StationN64Server s=new StationN64Server(3,r->failures.incrementAndGet());
        ExecutorService producers=Executors.newCachedThreadPool();CountDownLatch release=new CountDownLatch(1);
        try {
            registerDirect(s,0);registerDirect(s,1);CountDownLatch initial=new CountDownLatch(82);
            for(int n=0;n<82;n++)s.udp(0,input(0,n,n),b->initial.countDown());
            check(initial.await(2,TimeUnit.SECONDS),"setup datagrams drained");
            CountDownLatch entered=new CountDownLatch(1),received=new CountDownLatch(81);List<Integer> order=Collections.synchronizedList(new ArrayList<>());
            StationN64Server.Datagram slow=b->{entered.countDown();try{release.await();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}order.add(StationN64Wire.int32(b,5));received.countDown();};
            s.udp(0,request(0,0,0),slow);check(entered.await(1,TimeUnit.SECONDS),"slow sender entered");
            Future<?> producer=producers.submit(()->{try{for(int n=1;n<=80;n++)s.udp(0,request(0,0,n),slow);}catch(IOException e){throw new UncheckedIOException(e);}});
            try{producer.get(100,TimeUnit.MILLISECONDS);throw new AssertionError("unbounded sender queue");}catch(TimeoutException bounded){checks++;}
            Future<Boolean> monitor=producers.submit(()->s.registered(1));check(monitor.get(1,TimeUnit.SECONDS),"slow send does not hold roster monitor");
            Field players=StationN64Server.class.getDeclaredField("players");players.setAccessible(true);Object p=((Object[])players.get(s))[0];Field outbound=p.getClass().getDeclaredField("outbound");outbound.setAccessible(true);Object q=outbound.get(p);
            synchronized(q){check(((Collection<?>)q).size()<=64,"sender queue bounded to 64");}
            release.countDown();producer.get(2,TimeUnit.SECONDS);check(received.await(2,TimeUnit.SECONDS),"backpressure releases without dropping");
            for(int n=0;n<=80;n++)check(order.get(n)==n,"per-peer FIFO "+n);
            check(failures.get()==0,"backpressure creates no transport failure");
        }finally{release.countDown();s.close();producers.shutdownNow();}
        AtomicInteger cancelledFailures=new AtomicInteger();StationN64Server cancelled=new StationN64Server(3,r->cancelledFailures.incrementAndGet());ExecutorService blocked=Executors.newSingleThreadExecutor();CountDownLatch senderEntered=new CountDownLatch(1);
        try {
            registerDirect(cancelled,0);registerDirect(cancelled,1);
            StationN64Server.Datagram sink=b->{senderEntered.countDown();try{new CountDownLatch(1).await();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}};
            cancelled.udp(0,request(0,0,0),sink);check(senderEntered.await(1,TimeUnit.SECONDS),"cancellable sender entered");
            Future<Boolean> f=blocked.submit(()->{try{for(int n=0;n<80;n++)cancelled.udp(0,request(0,0,0),sink);return false;}catch(IOException e){return true;}});
            try{f.get(100,TimeUnit.MILLISECONDS);throw new AssertionError("expected queued producer");}catch(TimeoutException bounded){checks++;}
            cancelled.close();check(f.get(1,TimeUnit.SECONDS),"close unblocks backpressure producer");check(cancelledFailures.get()==0,"explicit close does not report network failure");
        }finally{cancelled.close();blocked.shutdownNow();}
    }
    public static void main(String[] args)throws Exception {long begin=System.nanoTime();wire();directServer();loopback(2);loopback(3);loopback(4);bindAdmission();backpressure();System.out.println("{\"checks\":"+checks+",\"jvmLoopbackOnly\":true,\"androidOrNativeGameplay\":false,\"elapsedMs\":"+TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-begin)+"}");}
}
