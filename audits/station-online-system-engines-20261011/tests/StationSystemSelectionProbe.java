package org.emulationstation.frontend.netplay;

import android.content.Context;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
import org.json.*;

/** Runs actual compiled R126 selection with a bounded JVM asset fixture.
 * No native core, Android lifecycle, signed room, auth, or gameplay is exercised.
 */
public final class StationSystemSelectionProbe {
    private static int checks;
    private static void check(boolean condition,String message){
        checks++;if(!condition)throw new AssertionError(message);
    }
    public static void main(String[] args)throws Exception {
        byte[] asset;
        try(ZipFile apk=new ZipFile(args[0])){
            asset=apk.getInputStream(apk.getEntry("assets/station-online/engines.json")).readAllBytes();
        }
        Context context=new Context(asset);
        JSONObject receipt=new JSONObject(Files.readString(Paths.get(args[1])));
        JSONArray rows=receipt.getJSONArray("rows");
        check(rows.length()==50,"All system rows required");
        int aliases=0,selected=0,blocked=0;
        for(int i=0;i<rows.length();i++){
            JSONObject row=rows.getJSONObject(i);
            JSONArray names=row.getJSONArray("aliases");
            for(int n=0;n<names.length();n++){
                aliases++;
                String name=names.getString(n);
                check(StationOnlineGame.platform(name).equals(row.getString("onlinePlatform")),"Actual alias policy: "+name);
                JSONObject expected=row.optJSONObject("onlineEngine");
                if(expected==null){
                    boolean rejected=false;
                    try{StationOnlineGame.engine(context,name);}
                    catch(StationOnlineGame.Unavailable e){rejected=true;check(e.getMessage()!=null&&!e.getMessage().isEmpty(),"Explained unsupported system");}
                    check(rejected,"Unintegrated system must not fall through to RetroArch: "+name);
                    blocked++;
                }else{
                    JSONObject actual=StationOnlineGame.engine(context,name);
                    for(String field:new String[]{"engineId","coreSha256","runtimeSha256","library"})
                        check(actual.getString(field).equals(expected.getString(field)),"Actual engine selection: "+name+"/"+field);
                    check(actual.optString("backend","retroarch").equals(expected.getString("backend")),"Actual backend: "+name);
                    check(actual.getBoolean("launchReady")&&"station-stream.v3".equals(actual.getString("recoveryProtocol")),"Eligible exact v3 engine");
                    selected++;
                }
            }
        }
        check(aliases==78,"All aliases executed");
        for(String unknown:new String[]{"not-a-system","N64 not approved","", "psx-new", "neo geo guesses"}){
            boolean rejected=false;
            try{StationOnlineGame.engine(context,unknown);}catch(java.io.IOException expected){rejected=true;}
            check(rejected,"Unknown name rejected: "+unknown);
        }
        JSONObject neogeo=StationOnlineGame.engine(context,"neogeo");
        check(neogeo.getString("engineId").startsWith("fbneo-"),"Disabled Geolith must not be selected");
        System.out.println(new JSONObject().put("checks",checks).put("aliases",aliases)
            .put("selectedAliases",selected).put("blockedAliases",blocked)
            .put("androidExecuted",false).put("serverAuthenticated",false)
            .put("physicalGameplayValidated",false).toString());
    }
}
