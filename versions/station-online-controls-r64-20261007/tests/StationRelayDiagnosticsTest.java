package org.emulationstation.frontend.netplay;
import java.net.URI;
import java.lang.reflect.*;
import java.util.*;
import javax.net.ssl.SSLSocketFactory;

/** No production requests or credentials. Does not simulate or claim a real match. */
public final class StationRelayDiagnosticsTest {
    public static void main(String[] args)throws Exception {
        List<String> events=new ArrayList<>();int[] failures={0};
        String secret="abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG";
        StationRelayTunnel.Listener listener=new StationRelayTunnel.Listener(){
            public void failed(){failures[0]++;}
            public void trace(String text){events.add(text);}
        };
        StationRelayTunnel tunnel=new StationRelayTunnel(new URI("wss://fixture.invalid/v1/station/online/relay"),secret,true,23500,(SSLSocketFactory)SSLSocketFactory.getDefault(),listener);
        Method trace=StationRelayTunnel.class.getDeclaredMethod("trace",String.class);trace.setAccessible(true);
        trace.invoke(tunnel,"fixture");
        if(events.size()!=1||!events.get(0).contains("role=host")||!events.get(0).contains("sentBytes=0 receivedBytes=0 pongAgeMs=-1 localWriteMs=0"))throw new AssertionError(events);
        for(String s:events)if(s.contains(secret)||s.contains("fixture.invalid"))throw new AssertionError("credential/address leak");
        Field remote=StationRelayTunnel.class.getDeclaredField("remote");remote.setAccessible(true);
        org.emulationstation.frontend.relay.ws.client.WebSocketClient socket=(org.emulationstation.frontend.relay.ws.client.WebSocketClient)remote.get(tunnel);
        socket.onWebsocketPong(null,null);trace.invoke(tunnel,"after-pong");
        if(events.get(1).contains("pongAgeMs=-1"))throw new AssertionError("pong not observed");
        if(socket.getConnectionLostTimeout()!=20)throw new AssertionError("policy was changed");
        // Closure records metadata only, never server-supplied reason/secret.
        socket.onClose(1006,secret,true);
        if(failures[0]!=1||events.stream().noneMatch(s->s.contains("remote-close code=1006 peer=true")))throw new AssertionError(events);
        socket.onClose(1000,"",false);tunnel.close();
        if(failures[0]!=1||events.stream().anyMatch(s->s.contains(secret)))throw new AssertionError("duplicate failure or secret leak");
        System.out.println("PASS: relay close diagnostics, pong observation, unchanged timeout, idempotence, credential privacy; no production traffic");
    }
}
