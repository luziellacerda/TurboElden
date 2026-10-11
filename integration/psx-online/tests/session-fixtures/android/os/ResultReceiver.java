// Test fixture only. Never included in the application.
package android.os; import java.util.*;public class ResultReceiver{ public final List<Integer> codes=new ArrayList<>();public ResultReceiver(Handler h){} protected void onReceiveResult(int c,Bundle b){}public void send(int c,Bundle b){codes.add(c);onReceiveResult(c,b);} }
