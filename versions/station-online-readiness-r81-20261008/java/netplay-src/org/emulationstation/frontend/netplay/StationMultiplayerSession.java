package org.emulationstation.frontend.netplay;
import java.io.*;
import java.util.*;
import org.json.*;

/** A single native barrier owns the independently recoverable host/guest links. */
final class StationMultiplayerSession implements AutoCloseable {
    interface Listener {
        void nativeControl(long epoch,boolean pause,boolean visible);long nativeStatus();boolean nativeStalled();
        boolean bind(int sourcePort,int zeroBasedSlot);void unbind(int sourcePort,int zeroBasedSlot);
        void ticket(String link,long serial);void ready();void state(boolean waiting,boolean synchronizing);void fatal(String category);void trace(String event);
    }
    private final Listener listener;private final ArrayList<Channel> channels=new ArrayList<>();
    private final boolean host;private final int localSlot;private boolean closed,visible=true,started,notified;private long epoch;
    private final class Channel {
        final String id;final int guestSlot;final StationMultiplayerTunnel tunnel;long at=-1,serial;boolean running,ready,sync;
        Channel(JSONObject value,int port)throws Exception {
            id=value.getString("linkId");guestSlot=value.getInt("guestSlot");
            JSONObject ticket=value.getJSONObject("ticket");checkTicket(ticket,id,host,localSlot);
            tunnel=new StationMultiplayerTunnel(StationRelayTls.multiplayerEndpoint(),ticket.getString("ticket"),ticket.getString("requestProof"),ticket.getInt("windowBytes"),host,port,StationRelayTls.create(),new StationMultiplayerTunnel.Listener(){
                public void trace(String event){listener.trace("linkSlot="+guestSlot+" "+event);}
                public void ticket(){synchronized(StationMultiplayerSession.this){if(!closed)listener.ticket(id,++serial);}}
                public void ready(){synchronized(StationMultiplayerSession.this){ready=true;update();}}
                public void state(boolean waiting,boolean synchronizing){synchronized(StationMultiplayerSession.this){sync=synchronizing;update();}}
                public void nativeControl(long e,boolean pause,boolean shown){synchronized(StationMultiplayerSession.this){if(closed||e<at)return;at=e;running=!pause;sync=pause;epoch=Math.max(epoch,e);update();}}
                public long nativeStatus(){return listener.nativeStatus();}
                public boolean nativeStalled(){return listener.nativeStalled();}
                public void unrecoverable(String category){synchronized(StationMultiplayerSession.this){running=false;update();if(!closed)listener.fatal(category);}}
            });
            if(host)tunnel.socketBinding(new StationMultiplayerTunnel.SocketBinding(){public boolean bind(int p){return listener.bind(p,guestSlot-1);}public void release(int p){listener.unbind(p,guestSlot-1);}});
        }
    }
    StationMultiplayerSession(JSONObject launch,Listener listener)throws Exception {
        this.listener=listener;host="host".equals(launch.getString("role"));
        JSONArray links=launch.getJSONArray("multiplayerLinks");int count=launch.getInt("participantCount"),slot=launch.getInt("localSlot");localSlot=slot;int mask=launch.getInt("expectedDeviceMask");
        if(count<2||count>4||links.length()!=(host?count-1:1)||slot<1||slot>4||host!=(slot==1)||mask<1||(mask&~15)!=0||Integer.bitCount(mask)!=count||(mask&(1<<(slot-1)))==0)throw new IOException("ROSTER");
        HashSet<String> ids=new HashSet<>();HashSet<Integer> slots=new HashSet<>();
        try{for(int i=0;i<links.length();i++){JSONObject link=links.getJSONObject(i);int guest=link.getInt("guestSlot");if(guest<2||guest>4||(mask&(1<<(guest-1)))==0||!slots.add(guest)||!ids.add(link.getString("linkId"))||(!host&&slot!=guest))throw new IOException("LINK");channels.add(new Channel(link,launch.getInt("port")));}}
        catch(Exception e){for(Channel c:channels)c.tunnel.close();throw e;}
    }
    static void checkTicket(JSONObject value,String id)throws Exception {
        if(!id.equals(value.getString("linkId"))||!"/v1/station/online/multiplayer/relay".equals(value.getString("path"))||!"station-stream.v3".equals(value.getString("protocol"))||value.getInt("expiresInSeconds")<1||value.getInt("expiresInSeconds")>60||value.getInt("windowBytes")!=262144)throw new IOException("TICKET_BINDING");
    }
    static void checkTicket(JSONObject value,String id,boolean host,int slot)throws Exception {
        checkTicket(value,id);if(value.getBoolean("hostSide")!=host||value.getInt("ownerSlot")!=slot||!value.getString("ticket").matches("[A-Za-z0-9_-]{43}")||value.getString("requestProof").isEmpty())throw new IOException("TICKET_ROLE");
    }
    private void update(){
        if(closed||!started)return;boolean run=visible,allReady=true,allSync=true;
        for(Channel c:channels){run&=c.at==epoch&&c.running&&c.tunnel.available();allReady&=c.ready;allSync&=c.at==epoch&&c.sync;}
        listener.nativeControl(epoch,!run,visible);listener.state(!run,!run&&allSync);
        if(allReady&&!notified){notified=true;listener.ready();}
    }
    int localPort(){return channels.get(0).tunnel.localPort();}
    synchronized void start(){if(started||closed)return;started=true;for(Channel c:channels)c.tunnel.start();update();}
    synchronized void listening(){for(Channel c:channels)c.tunnel.listening();}
    synchronized void visible(boolean shown){visible=shown;for(Channel c:channels){if(!shown)c.running=false;c.tunnel.visible(shown);}update();}
    synchronized void provide(String id,long serial,JSONObject ticket)throws Exception {if(closed)return;for(Channel c:channels)if(c.id.equals(id)){if(serial!=c.serial)return;checkTicket(ticket,id,host,localSlot);c.tunnel.provide(ticket.getString("ticket"),ticket.getString("requestProof"),ticket.getInt("windowBytes"));return;}throw new IOException("LINK");}
    synchronized void unavailable(String id,long serial,boolean terminal){if(closed)return;for(Channel c:channels)if(c.id.equals(id)&&serial==c.serial){if(terminal)c.tunnel.reject();else c.tunnel.unavailable();}}
    public synchronized void close(){if(closed)return;closed=true;for(Channel c:channels)c.tunnel.close();}
}
