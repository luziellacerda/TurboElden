package org.emulationstation.frontend.netplay;
import org.json.JSONObject;
public class StationLaunchPolicyTest {
 public static void main(String[] args)throws Exception {
  int checks=0;
  for(String state:new String[]{"waiting","starting","connecting","closed","","error"})for(boolean host:new boolean[]{false,true}){
   boolean expected=state.equals("connecting")||(host&&state.equals("starting"));
   if(StationLaunchPolicy.eligible(state,host)!=expected)throw new AssertionError(state);checks++;
  }
  JSONObject first=new JSONObject().put("roomId","a").put("generation",1),next=new JSONObject().put("roomId","a").put("generation",2),other=new JSONObject().put("roomId","b").put("generation",1);
  if(!StationLaunchPolicy.key(first).equals("a:1")||StationLaunchPolicy.key(first).equals(StationLaunchPolicy.key(next))||StationLaunchPolicy.key(first).equals(StationLaunchPolicy.key(other)))throw new AssertionError("identity");checks+=3;
  System.out.println("PASS "+checks+": host/guest launch eligibility and generation identity");
 }
}
