from pathlib import Path
R=Path(r'E:\StationNetplayWork');src=R/'station/src/java/org/emulationstation/frontend/station';tests=R/'station/tests'
p=src/'StationApi.java';s=p.read_text('utf-8');s=s.replace('"TurboRamaStationAndroid/online/v1",262144,cancel)','"TurboRamaStationAndroid/online/v1",524288,cancel)');p.write_text(s,'utf-8')
p=tests/'StationApiTest.java';s=p.read_text('utf-8');old='else if(operation.equals("downloads/authorize")){';assert s.count(old)==1
s=s.replace(old,'''else if(operation.equals("online/command")||operation.equals("online/events")){
                        domain="TurboRamaStationAndroid/online/v1";JSONObject body=new JSONObject(new String(request,StandardCharsets.UTF_8));
                        response.put("requestId",body.getString("requestId")).put("snapshot",new JSONObject().put("schemaVersion",1).put("instance","a".repeat(32)).put("revision",1));
                    }
                    else if(operation.equals("downloads/authorize")){''');p.write_text(s,'utf-8')
(tests/'StationOnlineApiTest.java').write_text('''package org.emulationstation.frontend.station;
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
''','utf-8')
p=R/'station/run_tests.py';s=p.read_text('utf-8');assert "('StationOnlineApiTest'" not in s;s=s.replace("('StationApiTest','api-test'),","('StationApiTest','api-test'),('StationOnlineApiTest','online-api-test'),");p.write_text(s,'utf-8')
print('Added real signed-client regressions')
