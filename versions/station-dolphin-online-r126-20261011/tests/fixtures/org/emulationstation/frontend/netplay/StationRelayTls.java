package org.emulationstation.frontend.netplay;
import java.net.URI;
import javax.net.ssl.SSLSocketFactory;
/** Loopback-only fixture, no real server or production TLS changes. */
final class StationRelayTls {
    static URI multiplayerEndpoint(){return URI.create("wss://127.0.0.1/v1/station/online/multiplayer/relay");}
    static SSLSocketFactory create(){return (SSLSocketFactory)SSLSocketFactory.getDefault();}
}
