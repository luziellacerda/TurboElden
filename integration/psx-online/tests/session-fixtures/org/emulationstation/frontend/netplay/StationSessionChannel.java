// Test fixture only. Never included in the application.
package org.emulationstation.frontend.netplay;import android.os.*;final class StationSessionChannel{static ResultReceiver callback;static ResultReceiver read(Bundle b,String k){return callback;}static ResultReceiver transport(ResultReceiver r){return r;} }
