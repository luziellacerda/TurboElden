package org.emulationstation.frontend.netplay;
import android.content.*;import org.json.*;import org.emulationstation.frontend.station.*;import java.util.*;
public class StationOnlineClient{
 public static volatile JSONObject own;public static volatile boolean present=true,forceFirstRejection,unconfirmed;public static volatile int failureStatus=409;public static volatile String failureCode="STATION_MULTIPLAYER_GENERATION_MISMATCH";public static final List<JSONObject> calls=Collections.synchronizedList(new ArrayList<>());
 public StationOnlineClient(Context c){}public static JSONObject command(String a){return new JSONObject().put("action",a).put("requestId",UUID.randomUUID().toString());}
 public JSONObject multiplayer(JSONObject r,StationApi.Cancellation cancel)throws Exception{calls.add(new JSONObject(r.toString()));if(r.getString("action").equals("snapshot"))return new JSONObject().put("room",own==null?JSONObject.NULL:own);
  if(failureStatus!=0&&((forceFirstRejection&&calls.size()==1)||!present||own==null||r.getLong("generation")!=own.getLong("generation"))){StationApi.Failure f=new StationApi.Failure();f.status=failureStatus;f.code=failureCode;throw f;}
  if(unconfirmed)return new JSONObject().put("room",own);
  present=false;return new JSONObject().put("room",JSONObject.NULL);}
 public JSONObject call(JSONObject r,boolean events,StationApi.Cancellation c)throws Exception{return new JSONObject().put("room",JSONObject.NULL);}
}
