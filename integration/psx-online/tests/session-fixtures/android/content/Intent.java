// Test fixture only. Never included in the application.
package android.content; import android.os.*; public class Intent { private final Bundle b=new Bundle();public Bundle getExtras(){return b;}public String getStringExtra(String k){return b.getString(k);} public Intent putExtra(String k,String v){b.putString(k,v);return this;} }
