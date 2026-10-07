package org.emulationstation.frontend.netplay;

import org.emulationstation.frontend.relay.ws.client.WebSocketClient;
import org.emulationstation.frontend.relay.ws.drafts.Draft_6455;
import org.emulationstation.frontend.relay.ws.protocols.Protocol;
import org.emulationstation.frontend.relay.ws.handshake.ServerHandshake;
import javax.net.ssl.*;
import java.net.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** TCP stream bridge: both phones initiate WSS to the same Station authority. */
final class StationRelayTunnel implements Closeable {
 enum Failure {NATIVE_LISTENER, RELAY, LOCAL_STREAM, PROTOCOL}
 interface Listener {void failed();default void failed(Failure reason){failed();}default void ready(){}default void trace(String event){}}
 private final long started=System.nanoTime();
 private volatile long sentBytes,receivedBytes,localWriteStarted,lastPong;
 private final boolean host;private final int hostPort;private final Listener listener;
 private final ExecutorService io=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-relay-local");t.setDaemon(true);return t;});
 private final Semaphore nativeHint=new Semaphore(0);
 private final CountDownLatch localConnected=new CountDownLatch(1);
 private final AtomicBoolean closed=new AtomicBoolean();
 private final ServerSocket accept;private volatile Socket local;private final WebSocketClient remote;
 StationRelayTunnel(URI uri,String ticket,boolean host,int hostPort,SSLSocketFactory tls,Listener listener)throws Exception {
  if(!uri.getScheme().equals("wss")||uri.getUserInfo()!=null||uri.getQuery()!=null||uri.getFragment()!=null||!uri.getPath().equals("/v1/station/online/relay")||!ticket.matches("[A-Za-z0-9_-]{43}"))throw new IOException("Invalid relay descriptor");
  this.host=host;this.hostPort=hostPort;this.listener=listener;
  accept=host?null:new ServerSocket(0,1,InetAddress.getByName("127.0.0.1"));if(accept!=null)accept.setSoTimeout(60000);
  Draft_6455 draft=new Draft_6455(Collections.emptyList(),Collections.singletonList(new Protocol("station-relay.v1")),65536);
  remote=new WebSocketClient(uri,draft,Collections.singletonMap("Authorization","StationRelay "+ticket),10000){
   @Override protected void onSetSSLParameters(SSLParameters p){p.setEndpointIdentificationAlgorithm("HTTPS");}
   @Override public void onOpen(ServerHandshake h){lastPong=System.nanoTime();trace("open");if(!"station-relay.v1".equals(h.getFieldValue("Sec-WebSocket-Protocol")))fail(Failure.PROTOCOL);}
   @Override public void onWebsocketPong(org.emulationstation.frontend.relay.ws.WebSocket connection,org.emulationstation.frontend.relay.ws.framing.Framedata frame){lastPong=System.nanoTime();super.onWebsocketPong(connection,frame);}
   @Override public void onMessage(String ignored){fail(Failure.PROTOCOL);}
   @Override public void onMessage(ByteBuffer data){
    try{
     if(data.remaining()>32768||!localConnected.await(60,TimeUnit.SECONDS)||closed.get())throw new IOException("Local endpoint unavailable");
     byte[] bytes=new byte[data.remaining()];data.get(bytes);localWriteStarted=System.nanoTime();local.getOutputStream().write(bytes);receivedBytes+=bytes.length;localWriteStarted=0;
    }catch(Exception e){trace("local-write-error type="+e.getClass().getSimpleName());fail(Failure.LOCAL_STREAM);}
   }
   @Override public void onClose(int code,String reason,boolean peer){if(!closed.get())trace("remote-close code="+code+" peer="+peer);fail(Failure.RELAY);}
   @Override public void onError(Exception error){if(!closed.get())trace("remote-error type="+error.getClass().getSimpleName());fail(Failure.RELAY);}
  };
  remote.setSocketFactory(tls);remote.setTcpNoDelay(true);remote.setConnectionLostTimeout(20);remote.setDaemon(true);
 }
 int localPort(){return host?hostPort:accept.getLocalPort();}
 boolean available(){Socket current=local;return !closed.get()&&current!=null&&current.isConnected()&&!current.isClosed()&&remote.isOpen();}
 void listening(){nativeHint.release();}
 void start(){io.execute(()->{
  Failure phase=host?Failure.NATIVE_LISTENER:Failure.LOCAL_STREAM;
  try{
   remote.connect();
   if(host)local=StationHostConnector.connect(hostPort,System.nanoTime()+TimeUnit.SECONDS.toNanos(45),closed::get,s->local=s,nativeHint);
   else local=accept.accept();
   if(closed.get()){local.close();return;}
   local.setTcpNoDelay(true);localConnected.countDown();
   phase=Failure.RELAY;long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(15);
   while(!remote.isOpen()&&!closed.get()){if(remote.isClosed()||System.nanoTime()>deadline)throw new IOException("Relay unavailable");Thread.sleep(5);}
   if(closed.get())return;
   listener.ready();phase=Failure.LOCAL_STREAM;
   byte[] bytes=new byte[16384];InputStream input=local.getInputStream();int count;
   while(!closed.get()&&(count=input.read(bytes))>=0){
    if(count==0)continue;
    // Only backpressure waits; regular input packets are forwarded immediately.
    while(!closed.get()&&queuedBytes()>262144)Thread.sleep(2);
    if(closed.get())break;remote.send(Arrays.copyOf(bytes,count));sentBytes+=count;
   }
   trace("local-eof");fail(Failure.LOCAL_STREAM);
  }catch(Exception e){trace("io-error phase="+phase+" type="+e.getClass().getSimpleName());if(e instanceof InterruptedException)Thread.currentThread().interrupt();fail(phase);}
 });}
 private long queuedBytes(){long n=0;for(ByteBuffer b:((org.emulationstation.frontend.relay.ws.WebSocketImpl)remote.getConnection()).outQueue)n+=b.remaining();return n;}
 private void trace(String event){
  long now=System.nanoTime(),pongAge=lastPong==0?-1:TimeUnit.NANOSECONDS.toMillis(now-lastPong);
  String value="stage="+event+" role="+(host?"host":"client")+" elapsedMs="+TimeUnit.NANOSECONDS.toMillis(now-started)+" sentBytes="+sentBytes+" receivedBytes="+receivedBytes+" pongAgeMs="+pongAge+" localWriteMs="+(localWriteStarted==0?0:TimeUnit.NANOSECONDS.toMillis(now-localWriteStarted));
  try{listener.trace(value);}catch(RuntimeException ignored){}
 }
 private void fail(Failure reason){if(!closed.get())trace("failure reason="+reason);if(closeOnce())listener.failed(reason);}
 private boolean closeOnce(){
  if(!closed.compareAndSet(false,true))return false;
  nativeHint.release();localConnected.countDown();
  try{if(accept!=null)accept.close();}catch(IOException ignored){}
  try{if(local!=null)local.close();}catch(IOException ignored){}
  remote.closeConnection(1000,"");io.shutdownNow();return true;
 }
 @Override public void close(){closeOnce();}
}
