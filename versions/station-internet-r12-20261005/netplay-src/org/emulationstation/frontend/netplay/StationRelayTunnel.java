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
 interface Listener {void failed();}
 private final boolean host;private final int hostPort;private final Listener listener;
 private final ExecutorService io=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-relay-local");t.setDaemon(true);return t;});
 private final CountDownLatch nativeListening=new CountDownLatch(1),localConnected=new CountDownLatch(1);
 private final AtomicBoolean closed=new AtomicBoolean();
 private final ServerSocket accept;private volatile Socket local;private final WebSocketClient remote;
 StationRelayTunnel(URI uri,String ticket,boolean host,int hostPort,SSLSocketFactory tls,Listener listener)throws Exception {
  if(!uri.getScheme().equals("wss")||uri.getUserInfo()!=null||uri.getQuery()!=null||uri.getFragment()!=null||!uri.getPath().equals("/v1/station/online/relay")||!ticket.matches("[A-Za-z0-9_-]{43}"))throw new IOException("Invalid relay descriptor");
  this.host=host;this.hostPort=hostPort;this.listener=listener;
  accept=host?null:new ServerSocket(0,1,InetAddress.getByName("127.0.0.1"));if(accept!=null)accept.setSoTimeout(60000);
  Draft_6455 draft=new Draft_6455(Collections.emptyList(),Collections.singletonList(new Protocol("station-relay.v1")),65536);
  remote=new WebSocketClient(uri,draft,Collections.singletonMap("Authorization","StationRelay "+ticket),10000){
   @Override protected void onSetSSLParameters(SSLParameters p){p.setEndpointIdentificationAlgorithm("HTTPS");}
   @Override public void onOpen(ServerHandshake h){if(!"station-relay.v1".equals(h.getFieldValue("Sec-WebSocket-Protocol")))fail();}
   @Override public void onMessage(String ignored){fail();}
   @Override public void onMessage(ByteBuffer data){
    try{
     if(data.remaining()>32768||!localConnected.await(60,TimeUnit.SECONDS)||closed.get())throw new IOException("Local endpoint unavailable");
     byte[] bytes=new byte[data.remaining()];data.get(bytes);local.getOutputStream().write(bytes);
    }catch(Exception e){fail();}
   }
   @Override public void onClose(int code,String reason,boolean peer){fail();}
   @Override public void onError(Exception error){fail();}
  };
  remote.setSocketFactory(tls);remote.setTcpNoDelay(true);remote.setConnectionLostTimeout(20);remote.setDaemon(true);
 }
 int localPort(){return host?hostPort:accept.getLocalPort();}
 void listening(){nativeListening.countDown();}
 void start(){io.execute(()->{
  try{
   remote.connect();
   if(host){if(!nativeListening.await(60,TimeUnit.SECONDS))throw new IOException("Native listener unavailable");Socket s=new Socket();local=s;s.connect(new InetSocketAddress("127.0.0.1",hostPort),10000);}
   else local=accept.accept();
   if(closed.get()){local.close();return;}
   local.setTcpNoDelay(true);localConnected.countDown();
   long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(15);
   while(!remote.isOpen()&&!closed.get()){if(remote.isClosed()||System.nanoTime()>deadline)throw new IOException("Relay unavailable");Thread.sleep(5);}
   byte[] bytes=new byte[16384];InputStream input=local.getInputStream();int count;
   while(!closed.get()&&(count=input.read(bytes))>=0){
    if(count==0)continue;
    // Only backpressure waits; regular input packets are forwarded immediately.
    while(!closed.get()&&queuedBytes()>262144)Thread.sleep(2);
    if(closed.get())break;remote.send(Arrays.copyOf(bytes,count));
   }
   fail();
  }catch(Exception e){if(e instanceof InterruptedException)Thread.currentThread().interrupt();fail();}
 });}
 private long queuedBytes(){long n=0;for(ByteBuffer b:((org.emulationstation.frontend.relay.ws.WebSocketImpl)remote.getConnection()).outQueue)n+=b.remaining();return n;}
 private void fail(){if(closeOnce())listener.failed();}
 private boolean closeOnce(){
  if(!closed.compareAndSet(false,true))return false;
  nativeListening.countDown();localConnected.countDown();
  try{if(accept!=null)accept.close();}catch(IOException ignored){}
  try{if(local!=null)local.close();}catch(IOException ignored){}
  remote.closeConnection(1000,"");io.shutdownNow();return true;
 }
 @Override public void close(){closeOnce();}
}
