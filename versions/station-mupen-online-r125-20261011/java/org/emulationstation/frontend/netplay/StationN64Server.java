package org.emulationstation.frontend.netplay;

import java.io.*;
import java.util.*;

/** Host-local Mupen protocol v1. Admission comes exclusively from the signed
 * Station roster/link. Implements the upstream TCP/UDP formats, not RetroArch.
 * The host is the source of truth for inputs; missing input never means exit. */
final class StationN64Server implements AutoCloseable {
    interface Events {void failed(String reason);}
    interface Datagram {void send(byte[] bytes)throws IOException;}
    private static final int DELAY=2, BUFFER=2, HISTORY=8192, MAX_SAVE=1048576, SEND_QUEUE=64;
    private final int mask;private final Events events;
    private final Player[] players=new Player[4];
    private final HashMap<String,byte[]> saves=new HashMap<>();private int totalSaves;
    private final LinkedHashMap<Integer,Sync> syncs=new LinkedHashMap<>();
    private byte[] settings;private volatile boolean closed,failed;
    private static final class Input {final int keys,plugin;Input(int k,int p){keys=k;plugin=p;}}
    private static final class Sync {final byte[] bytes;int mask;Sync(byte[] b,int slot){bytes=b;mask=1<<slot;}}
    private static final class Player {
        int registration,plugin,lead;boolean raw;Datagram sink;
        final HashMap<Integer,Input> input=new HashMap<>();
        final ArrayDeque<Delivery> outbound=new ArrayDeque<>();
        long sequence,nextEnqueue;Thread sender;
    }
    private static final class Delivery {
        final Player player;final Datagram sink;final byte[] bytes;final long sequence;
        Delivery(Player p,Datagram s,byte[] b){player=p;sink=s;bytes=b;sequence=p.sequence++;}
    }
    StationN64Server(int mask,Events events)throws IOException {
        if(mask<3||(mask&~15)!=0||(mask&1)==0)throw new IOException("N64_ROSTER");this.mask=mask;this.events=events;
        for(int i=0;i<4;i++)if((mask&(1<<i))!=0){Player p=new Player();players[i]=p;final int slot=i;
            p.sender=new Thread(()->sendLoop(p),"Station-N64-send-"+slot);p.sender.setDaemon(true);p.sender.start();}
    }
    synchronized void awaitRegistered()throws IOException {while(!closed&&!failed&&!registered())await();check();}
    private boolean registered(){for(Player p:players)if(p!=null&&p.registration==0)return false;return true;}
    private void await()throws IOException{try{wait();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}}
    private void check()throws IOException{if(closed||failed)throw new IOException("N64_SESSION_ENDED");}
    private synchronized Player player(int slot)throws IOException {check();if(slot<0||slot>3||players[slot]==null)throw new IOException("N64_SLOT");return players[slot];}
    synchronized boolean registered(int slot){return slot>=0&&slot<4&&players[slot]!=null&&players[slot].registration!=0;}
    void tcp(int slot,InputStream input,OutputStream output)throws IOException {
        Player p=player(slot);DataInputStream in=new DataInputStream(input);DataOutputStream out=new DataOutputStream(output);
        boolean admitted=false;
        for(;;){int op=in.read();if(op<0)throw new EOFException();
            if(op==5){byte[] b=StationN64Wire.exact(in,7);int requested=b[0]&255,plugin=b[1]&255,raw=b[2]&255,reg=StationN64Wire.int32(b,3);
                synchronized(this){check();if(admitted||requested!=slot||reg==0||plugin<1||plugin>5||raw!=0||p.registration!=0)throw new IOException("N64_REGISTRATION");
                    for(Player other:players)if(other!=null&&other.registration==reg)throw new IOException("N64_REGISTRATION");
                    p.registration=reg;p.plugin=slot>0&&plugin==2?1:plugin;p.raw=false;
                    for(int count=0;count<DELAY;count++)p.input.put(count,new Input(0,p.plugin));admitted=true;notifyAll();}
                out.writeByte(1);out.writeByte(BUFFER);out.flush();continue;
            }
            if(!admitted)throw new IOException("N64_UNREGISTERED");
            if(op==1){if(slot!=0)throw new IOException("N64_HOST_ONLY");String name=StationN64Wire.filename(in);int length=in.readInt();
                if(length<1||length>MAX_SAVE)throw new IOException("N64_SAVE_SIZE");byte[] bytes=StationN64Wire.exact(in,length);
                synchronized(this){check();byte[] old=saves.get(name);int total=totalSaves-(old==null?0:old.length)+length;
                    if(total>4*MAX_SAVE||(!saves.containsKey(name)&&saves.size()>=32))throw new IOException("N64_SAVE_BUDGET");saves.put(name,bytes);totalSaves=total;notifyAll();}
            }else if(op==2){if(slot==0)throw new IOException("N64_GUEST_ONLY");String name=StationN64Wire.filename(in);byte[] bytes;
                synchronized(this){while(!closed&&!failed&&!saves.containsKey(name))await();check();bytes=saves.get(name);}out.write(bytes);out.flush();
            }else if(op==3){if(slot!=0)throw new IOException("N64_HOST_ONLY");byte[] value=StationN64Wire.exact(in,24);
                // Config is synchronized by the core; JIT mode/cheats are pinned by the launch profile.
                if(StationN64Wire.int32(value,16)!=1)throw new IOException("N64_CPU_PROFILE");
                synchronized(this){check();if(settings!=null&&!Arrays.equals(settings,value))throw new IOException("N64_SETTINGS_CHANGED");settings=value;notifyAll();}
            }else if(op==4){if(slot==0)throw new IOException("N64_GUEST_ONLY");byte[] value;
                synchronized(this){while(!closed&&!failed&&settings==null)await();check();value=settings;}out.write(value);out.flush();
            }else if(op==6){awaitRegistered();ByteArrayOutputStream roster=new ByteArrayOutputStream(24);DataOutputStream snapshot=new DataOutputStream(roster);
                synchronized(this){check();for(Player q:players){snapshot.writeInt(q==null?0:q.registration);snapshot.writeByte(q==null?0:q.plugin);snapshot.writeByte(0);}}out.write(roster.toByteArray());out.flush();
            }else if(op==7){int reg=in.readInt();if(reg!=p.registration)throw new IOException("N64_DISCONNECT_SLOT");throw new EOFException("N64_HUMAN_EXIT");
            }else throw new IOException("N64_TCP_OPCODE");
        }
    }
    void udp(int owner,byte[] bytes,Datagram sink)throws IOException {
        List<Delivery> deliveries=new ArrayList<>();String failure=null;
        synchronized(this){
        Player p=player(owner);if(p.registration==0)throw new IOException("N64_UNREGISTERED");
        if(bytes.length==0)throw new IOException("N64_UDP_SIZE");int op=bytes[0]&255;
        if(op==0){if(bytes.length!=11||(bytes[1]&255)!=owner)throw new IOException("N64_INPUT_SLOT");
            int count=StationN64Wire.int32(bytes,2),plugin=bytes[10]&255;
            if(count<0||count>Integer.MAX_VALUE-DELAY||plugin!=p.plugin)throw new IOException("N64_INPUT_PROFILE");
            int target=count+DELAY;if(target>p.lead+HISTORY)throw new IOException("N64_INPUT_WINDOW");
            Input old=p.input.get(target),next=new Input(StationN64Wire.int32(bytes,6),plugin);
            if(old!=null&&(old.keys!=next.keys||old.plugin!=next.plugin))throw new IOException("N64_INPUT_CHANGED");
            p.input.put(target,next);p.sink=sink;
            for(Player targetPlayer:players)if(targetPlayer!=null&&targetPlayer.sink!=null)reply(owner,Math.max(0,count),targetPlayer,deliveries);
        }else if(op==2){if(bytes.length!=12||StationN64Wire.int32(bytes,2)!=p.registration||bytes[10]!=0)throw new IOException("N64_INPUT_REGISTRATION");
            int requested=bytes[1]&255,count=StationN64Wire.int32(bytes,6);Player source=player(requested);
            if(count<0||count>source.lead+HISTORY)throw new IOException("N64_INPUT_WINDOW");source.lead=Math.max(source.lead,count);p.sink=sink;
            reply(requested,count,p,deliveries);if(prune(source))failure="N64_INPUT_BUDGET";
        }else if(op==4){if(bytes.length!=133)throw new IOException("N64_SYNC_SIZE");int vi=StationN64Wire.int32(bytes,1);if(vi<0)throw new IOException("N64_SYNC_COUNT");
            byte[] value=Arrays.copyOfRange(bytes,5,133);Sync sync=syncs.get(vi);
            if(sync==null){if(syncs.size()>=512)throw new IOException("N64_SYNC_WINDOW");syncs.put(vi,new Sync(value,owner));}
            else {if(!Arrays.equals(sync.bytes,value)){failed=true;notifyAll();failure="N64_STATE_DIVERGED";}else{sync.mask|=1<<owner;if(sync.mask==mask)syncs.remove(vi);}}
        }else throw new IOException("N64_UDP_OPCODE");
        }
        // Never hold the global input/registration monitor across socket sends
        // or backpressure. Per-peer sequence reservations retain response order.
        if(failure!=null){wakeSenders();events.failed(failure);return;}
        for(Delivery d:deliveries)enqueue(d);
    }
    private void reply(int slot,int count,Player target,List<Delivery> deliveries)throws IOException {
        Player p=players[slot];ByteArrayOutputStream bytes=new ByteArrayOutputStream(512);DataOutputStream out=new DataOutputStream(bytes);
        out.writeByte(1);out.writeByte(slot);out.writeByte(failed?1:0);out.writeByte(Math.min(127,Math.max(0,p.lead-count)));out.writeByte(0);
        int n=0;for(int c=count;n<54;c++){Input value=p.input.get(c);if(value==null)break;out.writeInt(c);out.writeInt(value.keys);out.writeByte(value.plugin);n++;}
        if(n>0){byte[] result=bytes.toByteArray();result[4]=(byte)n;deliveries.add(new Delivery(target,target.sink,result));}
    }
    private boolean prune(Player source){
        // Keep enough history for all retained native clients during reconnect; never guess a missing input.
        int min=Integer.MAX_VALUE;for(Player p:players)if(p!=null)min=Math.min(min,p.lead);
        final int before=Math.max(0,min-HISTORY);source.input.keySet().removeIf(n->n<before);
        if(source.input.size()>2*HISTORY+DELAY){failed=true;notifyAll();return true;}return false;
    }
    private void enqueue(Delivery d)throws IOException {
        Player p=d.player;
        try{synchronized(p.outbound){while(!closed&&!failed&&(d.sequence!=p.nextEnqueue||p.outbound.size()==SEND_QUEUE))p.outbound.wait();
            check();p.outbound.addLast(d);p.nextEnqueue++;p.outbound.notifyAll();}}
        catch(InterruptedException e){Thread.currentThread().interrupt();markFailed("N64_SEND_INTERRUPTED");throw new InterruptedIOException();}
    }
    private void sendLoop(Player p){
        try{for(;;){Delivery d;synchronized(p.outbound){while(p.outbound.isEmpty()&&!closed&&!failed)p.outbound.wait();if(closed||failed)return;d=p.outbound.removeFirst();p.outbound.notifyAll();}d.sink.send(d.bytes);}}
        catch(InterruptedException e){Thread.currentThread().interrupt();if(!closed)markFailed("N64_SEND_INTERRUPTED");}
        catch(IOException e){if(!closed)markFailed("N64_LOCAL_SEND");}
    }
    private void markFailed(String reason){boolean announce;synchronized(this){announce=!closed&&!failed;if(announce){failed=true;notifyAll();}}wakeSenders();if(announce)events.failed(reason);}
    private void wakeSenders(){for(Player p:players)if(p!=null)synchronized(p.outbound){p.outbound.notifyAll();}}
    @Override public void close(){synchronized(this){if(closed)return;closed=true;notifyAll();}wakeSenders();for(Player p:players)if(p!=null)p.sender.interrupt();}
}
