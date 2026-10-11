package org.emulationstation.frontend.netplay;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

/** Loopback-only gateways. The original Station tunnel alone talks to the internet.
 * One framed pipe per authenticated guest, independent of TCP accept order. */
final class StationN64Mux implements AutoCloseable {
    interface Events {void failed(String reason);}
    private final boolean host;private final int slot,mask;private final Events events;
    private final StationN64Server server;
    private final ServerSocket coreListener,hub;private final DatagramSocket udp;
    private final ConcurrentHashMap<Integer,Integer> bindings=new ConcurrentHashMap<>();
    private final Set<Socket> sockets=ConcurrentHashMap.newKeySet();
    private final Set<StationN64Wire.Queue> queues=ConcurrentHashMap.newKeySet();
    private final ExecutorService workers=Executors.newCachedThreadPool(r->{Thread t=new Thread(r,"Station-N64-local");t.setDaemon(true);return t;});
    private volatile boolean closed;private boolean started;private volatile Socket guestPipe;private volatile SocketAddress coreUdpPeer;
    private final Object guestReady=new Object();
    StationN64Mux(boolean host,int slot,int mask,Events events)throws IOException {
        if((mask&~15)!=0||(mask&1)==0||Integer.bitCount(mask)<2||slot<0||slot>3||(mask&(1<<slot))==0||host!=(slot==0))throw new IOException("N64_ROSTER");
        this.host=host;this.slot=slot;this.mask=mask;this.events=events;
        coreListener=new ServerSocket(0,1,InetAddress.getByName("127.0.0.1"));
        DatagramSocket candidate=null;ServerSocket candidateHub=null;
        try {candidate=new DatagramSocket(new InetSocketAddress("127.0.0.1",coreListener.getLocalPort()));
            if(host)candidateHub=new ServerSocket(0,3,InetAddress.getByName("127.0.0.1"));}
        catch(IOException e){coreListener.close();if(candidate!=null)candidate.close();throw e;}
        udp=candidate;hub=candidateHub;server=host?new StationN64Server(mask,events::failed):null;
    }
    int corePort(){return coreListener.getLocalPort();}
    int hubPort(){return host?hub.getLocalPort():0;}
    synchronized boolean bind(int port,int remoteSlot){return !closed&&host&&port>=1024&&port<=65535&&remoteSlot>=1&&remoteSlot<=3&&(mask&(1<<remoteSlot))!=0&&!bindings.containsValue(remoteSlot)&&bindings.putIfAbsent(port,remoteSlot)==null;}
    synchronized void unbind(int port,int remoteSlot){bindings.remove(port,remoteSlot);}
    synchronized void start(int guestTunnelPort){
        if(closed||started)return;started=true;
        if(host){dispatch(this::acceptGuests);dispatch(this::acceptLocalHost);}
        else dispatch(()->acceptGuestCore(guestTunnelPort));
        dispatch(this::localUdp);
    }
    void awaitRegistered()throws IOException{if(host)server.awaitRegistered();}
    private void acceptGuests(){
        try {while(!closed){Socket socket=hub.accept();track(socket);Integer owner=bindings.get(socket.getPort());
            if(owner==null){socket.close();throw new IOException("N64_LINK_SLOT");}
            if(!dispatch(()->hostPipe(socket,owner)))closeSocket(socket);}}
        catch(IOException e){fail("N64_LOCAL_LINK");}
    }
    private void hostPipe(Socket socket,int owner){
        StationN64Wire.Queue queue=new StationN64Wire.Queue();queues.add(queue);
        try {OutputStream out=socket.getOutputStream();StationN64Wire.header(out);
            if(!dispatch(()->{try{server.tcp(owner,queue,new OutputStream(){
                @Override public void write(int b)throws IOException{write(new byte[]{(byte)b});}
                @Override public void write(byte[] b,int o,int n)throws IOException{while(n>0){int count=Math.min(n,StationN64Wire.MAX_TCP);StationN64Wire.frame(out,StationN64Wire.TCP,b,o,count);o+=count;n-=count;}}
            });}catch(IOException e){fail("N64_CORE_PROTOCOL");}finally{queue.close();}}))return;
            StationN64Wire.read(socket.getInputStream(),new StationN64Wire.Receiver(){
                public void tcp(byte[] bytes)throws IOException{queue.put(bytes);}
                public void udp(byte[] bytes)throws IOException{server.udp(owner,bytes,b->StationN64Wire.frame(out,StationN64Wire.UDP,b,0,b.length));}
            });
        }catch(IOException e){fail("N64_LOCAL_PIPE");}finally{queue.close();queues.remove(queue);closeSocket(socket);}
    }
    private void acceptLocalHost(){
        try {Socket core=coreListener.accept();track(core);coreListener.close();
            server.tcp(0,core.getInputStream(),core.getOutputStream());
        }catch(IOException e){fail("N64_HOST_CORE");}
    }
    private void acceptGuestCore(int port){
        try {Socket core=coreListener.accept();track(core);coreListener.close();
            Socket pipe=new Socket();pipe.connect(new InetSocketAddress("127.0.0.1",port),10000);track(pipe);
            OutputStream out=pipe.getOutputStream();StationN64Wire.header(out);
            synchronized(guestReady){guestPipe=pipe;guestReady.notifyAll();}
            if(!dispatch(()->{try{byte[] b=new byte[StationN64Wire.MAX_TCP];int n;InputStream input=core.getInputStream();
                while((n=input.read(b))!=-1)if(n>0)StationN64Wire.frame(out,StationN64Wire.TCP,b,0,n);
                throw new EOFException();}catch(IOException e){fail("N64_GUEST_CORE");}}))return;
            StationN64Wire.read(pipe.getInputStream(),new StationN64Wire.Receiver(){
                public void tcp(byte[] bytes)throws IOException{core.getOutputStream().write(bytes);core.getOutputStream().flush();}
                public void udp(byte[] bytes)throws IOException{SocketAddress peer=coreUdpPeer;if(peer==null)throw new IOException("N64_UDP_PEER");udp.send(new DatagramPacket(bytes,bytes.length,peer));}
            });
        }catch(IOException e){fail("N64_GUEST_PIPE");}
    }
    private void localUdp(){
        try {byte[] b=new byte[StationN64Wire.MAX_UDP+1];DatagramPacket packet=new DatagramPacket(b,b.length);
            while(!closed){packet.setLength(b.length);udp.receive(packet);if(!packet.getAddress().isLoopbackAddress()||packet.getLength()>StationN64Wire.MAX_UDP)throw new IOException("N64_LOCAL_DATAGRAM");
                SocketAddress peer=packet.getSocketAddress();if(coreUdpPeer==null)coreUdpPeer=peer;else if(!coreUdpPeer.equals(peer))throw new IOException("N64_UDP_PEER_CHANGED");
                byte[] bytes=Arrays.copyOf(b,packet.getLength());
                if(host){server.udp(0,bytes,data->udp.send(new DatagramPacket(data,data.length,peer)));}
                else {Socket pipe;synchronized(guestReady){while(!closed&&guestPipe==null)try{guestReady.wait();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}pipe=guestPipe;}
                    if(closed)return;StationN64Wire.frame(pipe.getOutputStream(),StationN64Wire.UDP,bytes,0,bytes.length);}
            }
        }catch(IOException e){fail("N64_LOCAL_DATAGRAM");}
    }
    private void track(Socket s)throws IOException{s.setTcpNoDelay(true);sockets.add(s);if(closed){closeSocket(s);throw new EOFException("N64_LOCAL_CLOSED");}}
    private boolean dispatch(Runnable work){if(closed)return false;try{workers.execute(work);return true;}catch(RejectedExecutionException e){fail("N64_LOCAL_WORKER");return false;}}
    private void closeSocket(Socket s){sockets.remove(s);try{s.close();}catch(IOException ignored){}}
    private void fail(String reason){if(!closed)events.failed(reason);}
    @Override public synchronized void close(){if(closed)return;closed=true;bindings.clear();if(server!=null)server.close();try{coreListener.close();}catch(IOException ignored){}if(hub!=null)try{hub.close();}catch(IOException ignored){}
        udp.close();for(Socket socket:sockets)closeSocket(socket);for(StationN64Wire.Queue q:queues)q.close();synchronized(guestReady){guestReady.notifyAll();}workers.shutdownNow();}
}
