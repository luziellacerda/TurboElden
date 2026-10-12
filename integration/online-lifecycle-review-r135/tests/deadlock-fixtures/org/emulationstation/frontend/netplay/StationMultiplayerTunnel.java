package org.emulationstation.frontend.netplay;import java.net.*;import javax.net.ssl.*;
final class StationMultiplayerTunnel implements AutoCloseable {
interface Listener {void trace(String s);void ticket();void ready();void state(boolean w,boolean s);void nativeControl(long e,boolean p,boolean v);long nativeStatus();boolean nativeStalled();void unrecoverable(String c);}
interface SocketBinding{boolean bind(int p);void release(int p);}
final Listener listener;StationMultiplayerTunnel(URI u,String t,String p,int w,boolean h,int port,SSLSocketFactory f,Listener l,StationMultiplayerEndpoint ep,int local,int remote){listener=l;}
void socketBinding(SocketBinding b){}int localPort(){return 0;}boolean available(){return false;}void start(){}void listening(){}void visible(boolean v){}void provide(String t,String p,int w){}void reject(){}void unavailable(){}public void close(){}boolean awaitClosed(long t){return true;}
}