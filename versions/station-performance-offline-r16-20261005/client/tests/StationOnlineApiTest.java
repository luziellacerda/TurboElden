package org.emulationstation.frontend.station;
import org.json.*;import java.util.UUID;
public final class StationOnlineApiTest {
 public static void main(String[] args)throws Exception {
  StationApiTest.Fake fake=new StationApiTest.Fake();StationApi api=fake.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  StationApi.Session session=api.openSession(fake.license,cancel);JSONObject request=new JSONObject().put("action","enter").put("nickname","Teste").put("requestId",UUID.randomUUID().toString());
  StationApiTest.ok(api.online(session,false,request,cancel).getInt("schemaVersion")==1,"signed command");
  StationApiTest.ok(api.online(session,true,request,cancel).getLong("revision")==1,"signed events");
  for(String field:new String[]{"requestId","domain","deviceId","licenseId","sessionId","productId","applicationId","schemaVersion"}){fake.tamper=field;StationApiTest.fails(()->api.online(session,false,request,cancel));}
  fake.tamper="";fake.badSignature=true;StationApiTest.fails(()->api.online(session,false,request,cancel));fake.badSignature=false;
  StationApiTest.fails(()->api.online(session,false,new JSONObject().put("requestId","bad"),cancel));
  StationApiTest.fails(()->api.online(session,false,new JSONObject(request.toString()).put("text","x".repeat(8200)),cancel));
  fake.failedRoute="/v1/station/online/command";fake.status=503;fake.errorCode="STATION_ONLINE_DISABLED";
  try{api.online(session,false,request,cancel);throw new AssertionError("disabled accepted");}catch(StationApi.Failure e){StationApiTest.ok(e.code.equals(fake.errorCode),"disabled reason preserved");}
  StationApiTest.ok(fake.requests==fake.closed,"every response closed");
  System.out.println("PASS "+StationApiTest.checks+" online transport checks: signatures, owner, request ID, limits and disabled service");
 }
}
