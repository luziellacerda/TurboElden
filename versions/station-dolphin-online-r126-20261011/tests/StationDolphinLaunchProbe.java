package org.emulationstation.frontend.netplay;

import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import org.emulationstation.frontend.station.StationApi;
import org.json.*;

/** Host probe of the actual private launch validation and file-copy methods.
 * It does not authenticate a room, execute Android APIs or run Dolphin. */
public final class StationDolphinLaunchProbe {
    static int checks;static Method validate,copy;
    static void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    static String sha(String text)throws Exception{return StationOnlineGame.hex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}
    static void call(Method method,Object...args)throws Exception{try{method.invoke(null,args);}catch(InvocationTargetException failure){throw (Exception)failure.getCause();}}
    static void rejected(JSONObject launch,String message)throws Exception{boolean rejected=false;try{call(validate,launch);}catch(Exception expected){rejected=true;}check(rejected,message);}
    static JSONObject fixture(String platform,int count,int slot)throws Exception{
        String controller=StationDolphinLaunch.profileFor(platform);JSONArray links=new JSONArray();
        for(int guest=2;guest<=count;guest++)if(slot==1||guest==slot){String id="fixture-link-"+guest;
            JSONObject ticket=new JSONObject().put("linkId",id).put("path","/v1/station/online/multiplayer/relay").put("protocol","station-stream.v3")
                .put("expiresInSeconds",60).put("windowBytes",262144).put("hostSide",slot==1).put("ownerSlot",slot)
                .put("ticket",String.join("",Collections.nCopies(43,"A"))).put("requestProof","isolated-fixture-no-authentication");
            links.put(new JSONObject().put("linkId",id).put("guestSlot",guest).put("ticket",ticket));
        }
        String hash=String.join("",Collections.nCopies(64,"0"));
        return new JSONObject().put("backend",StationDolphinLaunch.BACKEND).put("options",StationDolphinLaunch.OPTIONS).put("recoveryProtocol","station-stream.v3")
            .put("platform",platform).put("controllerProfile",controller).put("roomId",String.join("",Collections.nCopies(32,"0"))).put("generation",1)
            .put("participantCount",count).put("localSlot",slot).put("expectedDeviceMask",(1<<count)-1).put("role",slot==1?"host":"client").put("multiplayerLinks",links)
            .put("coreSha256",hash).put("runtimeSha256",hash).put("contentSha256",hash).put("optionsSha256",sha(StationDolphinLaunch.OPTIONS))
            .put("profileSha256",sha(StationMultiplayerProfile.canonical(controller,new int[]{1,1,1,1},StationDolphinLaunch.OPTIONS)));
    }
    static JSONObject clone(JSONObject value){return new JSONObject(value.toString());}
    static void descriptors()throws Exception{
        validate=StationDolphinLaunch.class.getDeclaredMethod("validate",JSONObject.class);validate.setAccessible(true);
        for(String platform:new String[]{"gamecube","wii"})for(int count=2;count<=4;count++)for(int slot=1;slot<=count;slot++){
            JSONObject valid=fixture(platform,count,slot);call(validate,valid);check(true,"accept exact "+platform+" roster "+count+" slot "+slot);
            rejected(clone(valid).put("localSlot",0),"reject slot zero");rejected(clone(valid).put("localSlot",5),"reject fifth player");
            rejected(clone(valid).put("expectedDeviceMask",valid.getInt("expectedDeviceMask")|16),"reject fifth bit");
            rejected(clone(valid).put("role",slot==1?"client":"host"),"reject mismatched role");
            rejected(clone(valid).put("options",StationDolphinLaunch.OPTIONS+"cheats=true\n"),"reject altered options");
            rejected(clone(valid).put("profileSha256",valid.getString("coreSha256")),"reject controller hash mismatch");
            rejected(clone(valid).put("controllerProfile",platform.equals("gamecube")?"dolphin-wii-remotes-four-v1":"dolphin-gamecube-four-ports-v1"),"reject cross-system controller");
            JSONObject bad=clone(valid);bad.getJSONArray("multiplayerLinks").getJSONObject(0).getJSONObject("ticket").put("ownerSlot",slot==1?2:1);rejected(bad,"reject foreign ticket owner");
            bad=clone(valid);bad.getJSONArray("multiplayerLinks").getJSONObject(0).put("guestSlot",5);rejected(bad,"reject fifth link");
            bad=clone(valid);bad.getJSONArray("multiplayerLinks").getJSONObject(0).getJSONObject("ticket").put("protocol","station-stream.v2");rejected(bad,"reject old ticket protocol");
        }
        JSONObject valid=fixture("gamecube",2,1);
        for(String field:new String[]{"backend","options","recoveryProtocol","platform","controllerProfile","roomId","generation","participantCount","localSlot","expectedDeviceMask","role","multiplayerLinks","coreSha256","runtimeSha256","contentSha256","optionsSha256","profileSha256"}){JSONObject bad=clone(valid);bad.remove(field);rejected(bad,"require "+field);}
        rejected(clone(valid).put("generation",0),"reject no generation");rejected(clone(valid).put("roomId","../fixture"),"reject path room identity");
        rejected(clone(valid).put("participantCount",1),"reject single-player room");rejected(clone(valid).put("expectedDeviceMask",2),"reject missing host");
        JSONObject duplicate=fixture("gamecube",3,1);duplicate.getJSONArray("multiplayerLinks").put(1,duplicate.getJSONArray("multiplayerLinks").getJSONObject(0));rejected(duplicate,"reject duplicate link/slot");
        check(!sha(StationMultiplayerProfile.canonical(StationDolphinLaunch.profileFor("gamecube"),new int[]{1,1,1,1},StationDolphinLaunch.OPTIONS)).equals(sha(StationMultiplayerProfile.canonical(StationDolphinLaunch.profileFor("wii"),new int[]{1,1,1,1},StationDolphinLaunch.OPTIONS))),"GC and Wii distinct canonical identities");
    }
    static void fileCopy(Path root)throws Exception{
        copy=StationDolphinLaunch.class.getDeclaredMethod("copyInputs",File.class,File.class,String.class,String.class,int[].class,StationApi.Cancellation.class);copy.setAccessible(true);
        Path source=root.resolve("normal"),dest=root.resolve("session");Files.createDirectories(source.resolve("Config/Profiles/GCPad"));Files.createDirectories(dest);
        Files.write(source.resolve("Config/GCPadNew.ini"),"[GCPad1]\nDevice=BSP-D3\n".getBytes(StandardCharsets.UTF_8));Files.write(source.resolve("Config/Profiles/GCPad/Padrão.ini"),"[Profile]\nDevice=BSP-D3\n".getBytes(StandardCharsets.UTF_8));
        Files.write(source.resolve("Config/Profiles/GCPad/not-input.bin"),new byte[]{1,2,3});
        String a=source.toFile().getCanonicalPath(),b=dest.toFile().getCanonicalPath();StationApi.Cancellation cancel=new StationApi.Cancellation();int[] budget={0,0};
        call(copy,source.resolve("Config/GCPadNew.ini").toFile(),dest.resolve("Config/GCPadNew.ini").toFile(),a,b,budget,cancel);
        check(Arrays.equals(Files.readAllBytes(source.resolve("Config/GCPadNew.ini")),Files.readAllBytes(dest.resolve("Config/GCPadNew.ini"))),"copy input byte-identical");
        call(copy,source.resolve("Config/Profiles/GCPad").toFile(),dest.resolve("Config/Profiles/GCPad").toFile(),a,b,budget,cancel);
        check(Files.exists(dest.resolve("Config/Profiles/GCPad/Padrão.ini")),"preserve Unicode profile name");check(!Files.exists(dest.resolve("Config/Profiles/GCPad/not-input.bin")),"skip non-INI profile artifact");
        check(budget[0]==2,"budget counts copied inputs");check(!Files.exists(dest.resolve("Config/Dolphin.ini")),"no offline core config copied");
        Files.write(source.resolve("Config/GCPadNew.ini"),"replacement".getBytes(StandardCharsets.UTF_8));call(copy,source.resolve("Config/GCPadNew.ini").toFile(),dest.resolve("Config/GCPadNew.ini").toFile(),a,b,new int[]{0,0},cancel);
        check(new String(Files.readAllBytes(dest.resolve("Config/GCPadNew.ini")),StandardCharsets.UTF_8).equals("replacement"),"atomic replace only private input");
        boolean failed=false;try{call(copy,source.resolve("Config/GCPadNew.ini").toFile(),root.resolve("outside.ini").toFile(),a,b,new int[]{0,0},cancel);}catch(IOException expected){failed=true;}check(failed&&!Files.exists(root.resolve("outside.ini")),"reject destination outside session");
        Path large=source.resolve("large.ini");Files.write(large,new byte[1048577]);failed=false;try{call(copy,large.toFile(),dest.resolve("large.ini").toFile(),a,b,new int[]{0,0},cancel);}catch(IOException expected){failed=true;}check(failed&&!Files.exists(dest.resolve("large.ini")),"reject input over 1 MiB");
        cancel.cancel();failed=false;try{call(copy,source.resolve("Config/GCPadNew.ini").toFile(),dest.resolve("cancelled.ini").toFile(),a,b,new int[]{0,0},cancel);}catch(Exception expected){failed=true;}check(failed&&!Files.exists(dest.resolve("cancelled.ini")),"cancellation leaves no published input");
        try(java.util.stream.Stream<Path> paths=Files.walk(dest)){check(paths.noneMatch(path->path.getFileName().toString().endsWith(".tmp")),"no temporary input remains");}
    }
    public static void main(String[]args)throws Exception{descriptors();fileCopy(Paths.get(args[0]));System.out.println("launchChecks="+checks+" physicalGameplayValidated=false");}
}
