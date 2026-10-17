package org.emulationstation.frontend.netplay;

import java.io.*;
import java.net.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import javax.net.ssl.SSLSocketFactory;

/** Isolated JVM fixtures: no Android, JNI, core, ROM, server or phone. */
public final class StationPsxEndpointProbe {
    static int checks;
    static void check(boolean value,String label){++checks;if(!value)throw new AssertionError(label);}
    interface Op{void run()throws Exception;}
    static void reject(Op op,String label)throws Exception{try{op.run();}catch(IOException|IllegalArgumentException expected){++checks;return;}throw new AssertionError(label);}
    static byte[] packet(String magic,int from,int to,int count){byte[] b=new byte[8+count];for(int i=0;i<4;i++)b[i]=(byte)magic.charAt(i);b[4]=(byte)from;b[5]=(byte)to;b[6]=(byte)(count>>8);b[7]=(byte)count;for(int i=8;i<b.length;i++)b[i]=(byte)i;return b;}
    static final class Source implements StationMultiplayerEndpoint.Receiver.Source {
        final byte[] data;final int fragment;volatile long confirmed;volatile boolean cancelled;
        Source(byte[] data,int fragment){this.data=data;this.fragment=fragment;}
        public byte[] read(long offset,int max){if(cancelled||offset>=data.length)return null;return Arrays.copyOfRange(data,(int)offset,Math.min(data.length,(int)offset+Math.min(fragment,max)));}
        public void confirm(long offset){confirmed=offset;if(offset==data.length)cancelled=true;}
        public boolean cancelled(){return cancelled;}
        public void retryWait(int ms)throws Exception{Thread.sleep(1);}
    }
    static void framing()throws Exception{
        for(StationMultiplayerEndpoint.Wire wire:StationMultiplayerEndpoint.Wire.values()){
            int slots=wire==StationMultiplayerEndpoint.Wire.PXL1?2:4;
            for(int local=1;local<=slots;local++)for(int remote=1;remote<=slots;remote++)if(local!=remote){
                byte[] b=packet(wire.magic,remote,local,1392);check(wire.size(b,local,remote,true)==1400,"exact wire cap");wire.outgoing(packet(wire.magic,local,remote,28),local,remote);checks++;
            }
        }
        byte[] pxl=packet("PXL1",1,2,28),dpl=packet("DPL1",1,2,28);
        reject(()->StationMultiplayerEndpoint.Wire.PXL1.size(dpl,2,1,true),"Dolphin datagram cannot enter PSX");
        reject(()->StationMultiplayerEndpoint.Wire.DPL1.size(pxl,2,1,true),"PSX packet cannot enter Dolphin");
        for(int length:new int[]{0,1,27,1393})reject(()->StationMultiplayerEndpoint.Wire.PXL1.size(packet("PXL1",1,2,length),2,1,true),"PXL1 payload bounds");
        reject(()->StationMultiplayerEndpoint.Wire.PXL1.size(packet("PXL1",3,2,28),2,3,true),"PSX has no third slot");
        reject(()->StationMultiplayerEndpoint.Wire.PXL1.outgoing(packet("PXL1",1,2,28),2,1),"outgoing cannot spoof authenticated slot");
        reject(()->StationPsxEndpoint.factory().create(1,3),"PSX factory bounds before JNI");
        StationMultiplayerEndpoint ordinary=new StationMultiplayerEndpoint(){public byte[] takeOutgoing(int t){return null;}public int deliver(long n,byte[] b){return 1;}public boolean awaitDelivery(long n,int t){return true;}};
        check(ordinary.wire()==StationMultiplayerEndpoint.Wire.DPL1,"default DPL1 preserved");ordinary.deliveryConfirmed(1);checks++;
        check(!ordinary.awaitOutgoingWake(100),"ordinary endpoint retains legacy nativeHint wait");
    }
    static void adapter()throws Exception{
        for(int result:new int[]{0,1,8,2,4,3,5,6,7,9,10,11,99}){
            StationPsxBridge.reset();StationPsxBridge.result=result;
            StationMultiplayerEndpoint endpoint=StationPsxEndpoint.factory().create(2,1);
            int got=endpoint.deliver(73,packet("PXL1",1,2,28));int want=result==0||result==1||result==8?1:result==2||result==4?0:-1;
            check(got==want,"native Result mapping exact");check(StationPsxBridge.remote==1&&StationPsxBridge.deliveryId==73,"authenticated remote and id exact");
            check(endpoint.awaitDelivery(73,100)==(want==1),"copied receipt distinct from run");
            if(want==1){endpoint.deliveryConfirmed(73);check(StationPsxBridge.released==1&&!endpoint.awaitDelivery(73,100),"receipt released only by explicit confirmed callback");}
            endpoint.close();check(endpoint.deliver(74,packet("PXL1",1,2,28))==-1,"closed link never accepts");
        }
        StationPsxBridge.reset();StationPsxBridge.admit=false;StationMultiplayerEndpoint endpoint=StationPsxEndpoint.factory().create(2,1);
        check(endpoint.deliver(17,packet("PXL1",1,2,28))==-1,"Ok without real copied receipt cannot ACK");
        StationPsxBridge.admit=true;endpoint.deliver(18,packet("PXL1",1,2,28));StationPsxBridge.releaseResult=5;
        reject(()->endpoint.deliveryConfirmed(18),"failed release does not claim drained");
        StationPsxBridge.releaseResult=1;endpoint.deliveryConfirmed(18);checks++;
        StationPsxBridge.receipts.remove(18L);reject(()->endpoint.deliveryConfirmed(18),"Duplicate release without actual retired receipt rejected");
        StationPsxBridge.outgoing.add(packet("DPL1",2,1,28));reject(()->endpoint.takeOutgoing(10),"native outgoing wire mismatch rejected");
        check(endpoint.awaitOutgoingWake(100)&&StationPsxBridge.awaited==100,"PSX event wait forwarded without dequeue");
        reject(()->endpoint.awaitOutgoingWake(0),"zero event timeout rejected");
        reject(()->endpoint.awaitOutgoingWake(101),"unbounded event timeout rejected");
        StationPsxBridge.awaited=-1;endpoint.close();
        check(endpoint.awaitOutgoingWake(100)&&StationPsxBridge.awaited==-1,"closed endpoint never enters native wait");
        StationPsxBridge.reset();StationPsxBridge.result=5;
        StationMultiplayerEndpoint malformed=StationPsxEndpoint.factory().create(2,1);
        byte[] shortPacket=Arrays.copyOf(packet("PXL1",1,2,28),8);
        check(malformed.deliver(21,shortPacket)==-1,"native rejection of truncated payload keeps diagnostics bounded");
    }
    static void fragmentation()throws Exception{
        for(int result:new int[]{0,8})for(int fragment:new int[]{1,3,7,8,29,1400,16384}){
            StationPsxBridge.reset();StationPsxBridge.result=result;
            byte[] a=packet("PXL1",1,2,28),b=packet("PXL1",1,2,1392),both=new byte[a.length+b.length];System.arraycopy(a,0,both,0,a.length);System.arraycopy(b,0,both,a.length,b.length);
            Source source=new Source(both,fragment);
            StationPsxBridge.beforeRelease=()->check(source.confirmed==a.length||source.confirmed==both.length,"source.confirm occurs BEFORE receipt release");
            new StationMultiplayerEndpoint.Receiver(StationPsxEndpoint.factory().create(2,1),2,1,0).run(source);
            check(source.confirmed==both.length&&StationPsxBridge.calls==2&&StationPsxBridge.released==2,"all complete PXL1 frames copied/confirmed/released");
            check(StationPsxBridge.receipts.isEmpty(),"native receipt window drains while core paused");
        }
        for(String magic:new String[]{"DPL1","PSL1","PXL2"}){StationPsxBridge.reset();Source source=new Source(packet(magic,1,2,28),1);
            reject(()->new StationMultiplayerEndpoint.Receiver(StationPsxEndpoint.factory().create(2,1),2,1,0).run(source),"incompatible wire rejects before native delivery");
            check(source.confirmed==0&&StationPsxBridge.calls==0,"wrong wire never copied or ACKed");}
        StationPsxBridge.reset();Source partial=new Source(Arrays.copyOf(packet("PXL1",1,2,1392),31),1);
        new StationMultiplayerEndpoint.Receiver(StationPsxEndpoint.factory().create(2,1),2,1,0).run(partial);
        check(partial.confirmed==0&&StationPsxBridge.calls==0,"truncated packet never admitted");
    }
    static Object field(Object value,String name)throws Exception{Field f=value.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(value);}
    static void set(Object value,String name,Object set)throws Exception{Field f=value.getClass().getDeclaredField(name);f.setAccessible(true);f.set(value,set);}
    static void until(Callable<Boolean> condition,String name)throws Exception{long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(4);while(!condition.call()&&System.nanoTime()<end)Thread.sleep(2);check(condition.call(),name);}
    static Thread thread(Object value,String method,AtomicReference<Throwable> error)throws Exception{Method m=value.getClass().getDeclaredMethod(method);m.setAccessible(true);Thread t=new Thread(()->{try{m.invoke(value);}catch(Throwable e){error.set(e);}},"PSX-fixture");t.setDaemon(true);t.start();return t;}
    static void actualTunnel()throws Exception{
        StationPsxBridge.reset();AtomicReference<Throwable> error=new AtomicReference<>();
        StationMultiplayerTunnel.Listener listener=new StationMultiplayerTunnel.Listener(){public void ticket(){}public void ready(){}public void state(boolean w,boolean s){}public void nativeControl(long e,boolean p,boolean v){}public long nativeStatus(){return -1;}public boolean nativeStalled(){return false;}public void unrecoverable(String category){error.set(new AssertionError(category));}};
        StationMultiplayerTunnel tunnel=new StationMultiplayerTunnel(new URI("wss://127.0.0.1/v1/station/online/multiplayer/relay"),"abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG","v1.1791696000.abcdefghijklmnopqrstuv.fixture",262144,false,0,(SSLSocketFactory)SSLSocketFactory.getDefault(),listener,StationPsxEndpoint.factory().create(2,1),2,1);
        Thread in=thread(tunnel,"nativeInput",error),out=thread(tunnel,"nativeOutput",error);
        try{until(()->(boolean)field(tunnel,"localReady"),"PSX endpoint ready without native socket");check(field(tunnel,"accept")==null,"PSX opens no listener");
            byte[] incoming=packet("PXL1",1,2,1392);Object gate=field(tunnel,"gate");StationMultiplayerWire.Bytes rx=(StationMultiplayerWire.Bytes)field(tunnel,"rx");
            StationPsxBridge.beforeRelease=()->{synchronized(gate){check(rx.delivered==incoming.length,"tunnel confirms DATA before release");}};
            for(int at=0;at<incoming.length;at+=7)synchronized(gate){rx.append(at,Arrays.copyOfRange(incoming,at,Math.min(incoming.length,at+7)));gate.notifyAll();}
            until(()->StationPsxBridge.released==1,"tunnel copied and released PSX receipt");
            byte[] outgoing=packet("PXL1",2,1,1392);StationPsxBridge.outgoing.add(outgoing);StationMultiplayerWire.Bytes tx=(StationMultiplayerWire.Bytes)field(tunnel,"tx");
            until(()->{synchronized(gate){return tx.next==outgoing.length;}},"tunnel accepts opt-in outgoing PXL1");synchronized(gate){check(Arrays.equals(outgoing,tx.read(0)),"PXL1 outer bytes unchanged");}check(error.get()==null,"PSX tunnel healthy");
        }finally{tunnel.close();in.join(1500);out.join(1500);}
        check(!in.isAlive()&&!out.isAlive(),"link close releases workers without native STOP");
    }
    static void cleanup()throws Exception{
        StationMultiplayerTunnel.Listener listener=new StationMultiplayerTunnel.Listener(){public void ticket(){}public void ready(){}public void state(boolean w,boolean s){}public void nativeControl(long e,boolean p,boolean v){}public long nativeStatus(){return -1;}public boolean nativeStalled(){return false;}public void unrecoverable(String c){throw new AssertionError(c);}};
        StationMultiplayerTunnel tunnel=new StationMultiplayerTunnel(new URI("wss://127.0.0.1/v1/station/online/multiplayer/relay"),"abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG","v1.1791696000.abcdefghijklmnopqrstuv.fixture",262144,false,0,(SSLSocketFactory)SSLSocketFactory.getDefault(),listener,StationPsxEndpoint.factory().create(2,1),2,1);
        check(!tunnel.awaitClosed(20),"unclosed tunnel cannot prove cleanup");reject(()->tunnel.awaitClosed(0),"zero cleanup timeout rejected");
        Object neverStarted=field(tunnel,"remote");Field previousThread=org.emulationstation.frontend.relay.ws.client.WebSocketClient.class.getDeclaredField("connectReadThread");previousThread.setAccessible(true);previousThread.set(neverStarted,new Thread());Method begin=neverStarted.getClass().getDeclaredMethod("begin");begin.setAccessible(true);
        try{begin.invoke(neverStarted);throw new AssertionError("connect should reject reused client");}catch(InvocationTargetException expected){check(expected.getCause() instanceof IllegalStateException,"failed connect rejects before reader starts");}
        check(((Set<?>)field(tunnel,"activeReaders")).isEmpty(),"failed registration removed when connect throws before start");
        CountDownLatch entered=new CountDownLatch(2),release=new CountDownLatch(1);Runnable blocked=()->{entered.countDown();while(release.getCount()>0)try{release.await();}catch(InterruptedException ignored){}};
        ((ExecutorService)field(tunnel,"worker")).execute(blocked);((ExecutorService)field(tunnel,"writes")).execute(blocked);check(entered.await(2,TimeUnit.SECONDS),"real executors started");
        Object remote=field(tunnel,"remote");java.net.Socket rawSocket=new java.net.Socket();((org.emulationstation.frontend.relay.ws.client.WebSocketClient)remote).setSocket(rawSocket);
        CountDownLatch writerRelease=new CountDownLatch(1);Thread webWriter=new Thread(()->{while(writerRelease.getCount()>0)try{writerRelease.await();}catch(InterruptedException ignored){}},"fixture-ws-writer");webWriter.setDaemon(true);Field writerField=org.emulationstation.frontend.relay.ws.client.WebSocketClient.class.getDeclaredField("writeThread");writerField.setAccessible(true);writerField.set(remote,webWriter);webWriter.start();
        Thread reader=new Thread(blocked,"fixture-real-reader");reader.setDaemon(true);set(remote,"readerThread",reader);((Set<Object>)field(tunnel,"activeReaders")).add(remote);reader.start();
        tunnel.close();begin.invoke(neverStarted);check(((Set<?>)field(tunnel,"activeReaders")).size()==1,"closed tunnel prevents a future reader registration");check(!tunnel.awaitClosed(25),"interruption/shutdown request is not executor termination");check(reader.isAlive(),"timeout never kills a reader");release.countDown();reader.join(2000);check(!tunnel.awaitClosed(25)&&webWriter.isAlive(),"terminated reader alone cannot prove WebSocket writer cleanup");check(rawSocket.isClosed(),"confirmed human cleanup closes real WebSocket socket");writerRelease.countDown();webWriter.join(2000);check(tunnel.awaitClosed(1000),"cleanup completes only after actual executors/readers/writer terminate");
        set(tunnel,"inputThread",Thread.currentThread());check(!tunnel.awaitClosed(10),"cannot claim cleanup from its own worker");set(tunnel,"inputThread",null);check(tunnel.awaitClosed(100),"completed cleanup remains idempotent");
        org.json.JSONObject ticket=new org.json.JSONObject().put("linkId","fixture").put("path","/v1/station/online/multiplayer/relay").put("protocol","station-stream.v3").put("expiresInSeconds",45).put("windowBytes",262144).put("hostSide",true).put("ownerSlot",1).put("ticket","abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG").put("requestProof","v1.1791696000.abcdefghijklmnopqrstuv.fixture");
        org.json.JSONObject launch=new org.json.JSONObject().put("role","host").put("participantCount",2).put("localSlot",1).put("expectedDeviceMask",3).put("port",0).put("multiplayerLinks",new org.json.JSONArray().put(new org.json.JSONObject().put("linkId","fixture").put("guestSlot",2).put("ticket",ticket)));
        StationMultiplayerSession session=new StationMultiplayerSession(launch,new StationMultiplayerSession.Listener(){public void nativeControl(long e,boolean p,boolean v){}public long nativeStatus(){return -1;}public boolean nativeStalled(){return false;}public boolean bind(int p,int s){throw new AssertionError();}public void unbind(int p,int s){throw new AssertionError();}public void ticket(String l,long s){}public void ready(){}public void state(boolean w,boolean s){}public void fatal(String c){throw new AssertionError(c);}public void trace(String e){}},StationPsxEndpoint.factory());
        check(!session.awaitClosed(20),"aggregate session cannot retire before explicit close");session.close();check(session.awaitClosed(1000),"aggregate requires each real tunnel cleanup");check(session.awaitClosed(100),"aggregate cleanup idempotent");
    }
    public static void main(String[] args)throws Exception{framing();adapter();fragmentation();actualTunnel();cleanup();System.out.println("PASS PSX endpoint checks="+checks+" isolated_fixture_only=true");}
}
