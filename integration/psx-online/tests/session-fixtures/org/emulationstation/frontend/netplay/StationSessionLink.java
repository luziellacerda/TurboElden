// Test fixture only. Never included in the application.
package org.emulationstation.frontend.netplay;import android.app.*;final class StationSessionLink{interface Listener{void ready();void unavailable(String c);}StationSessionLink(Activity a,String k,String r,long g,Listener l){}void bind(){}void close(){} }
