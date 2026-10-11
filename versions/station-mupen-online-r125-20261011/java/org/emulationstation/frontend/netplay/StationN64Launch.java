package org.emulationstation.frontend.netplay;

import android.content.*;
import android.os.SystemClock;
import org.emulationstation.frontend.station.StationApi;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

final class StationN64Launch {
    static final String BACKEND="mupen64plus-ae-station-v1";
    static final String OPTIONS="backend=mupen64plus-ae-station-v1\nwire=SN64/1\ncpu=cached-interpreter\nvideo=glide64mk2\nrsp=hle\nrawInput=false\nexpansionPak=true\ncountPerOp=0\ncountPerOpDen=0\nforceAlignmentOfPiDma=0\nrandomizeInterrupt=false\ninputDelay=2\nrollback=false\nsaves=session-only\n";
    private static File root(Context c)throws IOException {File f=new File(c.getNoBackupFilesDir(),"station-online");if(!f.isDirectory()&&!f.mkdirs())throw new IOException("N64_LAUNCH_DIRECTORY");return f.getCanonicalFile();}
    private static File file(Context c,String name)throws IOException {if(name==null||!name.matches("launch-n64-[0-9a-f-]{36}\\.json"))throw new IOException("N64_LAUNCH_FILE");return new File(root(c),name);}
    static String prepare(Context c,StationOnlineGame game,JSONObject room,JSONObject snapshot,StationApi.Cancellation cancel)throws Exception {
        game.verifyRoom(room);if(!"n64".equals(game.platform)||game.multiplayerProfile==null||!OPTIONS.equals(game.options)||!"station-stream.v3".equals(game.recoveryProtocol))throw new IOException("N64_PROFILE");
        int count=room.getJSONArray("roster").length(),slot=StationMultiplayerProfile.slot(room,snapshot.getString("selfId")),mask=StationMultiplayerProfile.mask(room);
        if(count<2||count>4||slot<1||slot>4||(mask&~15)!=0||Integer.bitCount(mask)!=count||(mask&1)==0)throw new IOException("N64_ROSTER");
        String rid=room.getString("roomId");if(!rid.matches("[0-9a-f]{32}")||room.getLong("generation")<1)throw new IOException("N64_ROOM");
        JSONArray links=room.getJSONArray("launchLinks");if(links.length()!=(slot==1?count-1:1))throw new IOException("N64_CHANNELS");
        for(int i=0;i<links.length();i++){JSONObject link=links.getJSONObject(i);StationMultiplayerSession.checkTicket(link.getJSONObject("ticket"),link.getString("linkId"),slot==1,slot);}
        verifyBinaries(c,StationOnlineGame.engine(c,"n64"),cancel);
        JSONObject launch=new JSONObject().put("backend",BACKEND).put("expires",SystemClock.elapsedRealtime()+60000).put("roomId",rid).put("generation",room.getLong("generation"))
            .put("role",slot==1?"host":"client").put("localSlot",slot).put("expectedDeviceMask",mask).put("participantCount",count).put("multiplayerLinks",links)
            .put("recoveryProtocol","station-stream.v3").put("rom",game.rom.getCanonicalPath()).put("engine",game.engineId)
            .put("coreSha256",game.coreSha256).put("runtimeSha256",game.runtimeSha256).put("options",game.options).put("name",game.name);
        String name="launch-n64-"+UUID.randomUUID()+".json";byte[] bytes=launch.toString().getBytes(StandardCharsets.UTF_8);
        if(bytes.length>32768)throw new IOException("N64_LAUNCH_SIZE");
        File target=file(c,name),temp=new File(target+".tmp");
        try {cancel.check();try(FileOutputStream out=new FileOutputStream(temp)){out.write(bytes);out.getFD().sync();}Files.move(temp.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE);cancel.check();return name;}
        catch(Exception e){Files.deleteIfExists(temp.toPath());Files.deleteIfExists(target.toPath());throw e;}
    }
    static JSONObject peek(Context c,String name)throws Exception {
        byte[] bytes;try(InputStream in=new FileInputStream(file(c,name))){bytes=StationOnlineGame.read(in,32768);}JSONObject value=new JSONObject(new String(bytes,StandardCharsets.UTF_8));
        if(!BACKEND.equals(value.getString("backend"))||!OPTIONS.equals(value.getString("options"))||value.getLong("expires")<SystemClock.elapsedRealtime())throw new IOException("N64_LAUNCH_EXPIRED");
        File rom=new File(value.getString("rom"));if(!rom.isFile()||Files.isSymbolicLink(rom.toPath()))throw new IOException("N64_ROM_MISSING");return value;
    }
    static JSONObject consume(Context c,String name)throws Exception {
        JSONObject value=peek(c,name);JSONObject engine=StationOnlineGame.engine(c,"n64");
        if(!BACKEND.equals(engine.optString("backend"))||!value.getString("engine").equals(engine.getString("engineId"))||!value.getString("coreSha256").equals(engine.getString("coreSha256"))||!value.getString("runtimeSha256").equals(engine.getString("runtimeSha256")))throw new IOException("N64_ENGINE_CHANGED");
        // The private descriptor was prepared on the room IO worker. APK native
        // libraries are immutable for the lifetime of this process; do not hash
        // them again on GameActivity's UI thread.
        Files.delete(file(c,name).toPath());return value;
    }
    private static void verifyBinaries(Context c,JSONObject engine,StationApi.Cancellation cancel)throws Exception {
        if(!BACKEND.equals(engine.optString("backend")))throw new IOException("N64_BACKEND");
        for(String field:new String[]{"library","runtimeLibrary"}){String nameInLibrary=engine.getString(field);if(!nameInLibrary.matches("lib[A-Za-z0-9_-]+\\.so"))throw new IOException("N64_LIBRARY");
            if(!StationOnlineGame.sha(new File(c.getApplicationInfo().nativeLibraryDir,nameInLibrary),cancel).equals(engine.getString(field.equals("library")?"coreSha256":"runtimeSha256")))throw new IOException("N64_BINARY_CHANGED");}
        JSONObject plugins=engine.getJSONObject("dependencySha256");for(Iterator<String> names=plugins.keys();names.hasNext();){String lib=names.next();if(!lib.matches("lib[A-Za-z0-9_-]+\\.so")||!StationOnlineGame.sha(new File(c.getApplicationInfo().nativeLibraryDir,lib),cancel).equals(plugins.getString(lib)))throw new IOException("N64_PLUGIN_CHANGED");}
    }
    static void discard(Context c,String name){try{Files.deleteIfExists(file(c,name).toPath());}catch(IOException ignored){}}
    static String key(String key)throws Exception{return (String)Class.forName("paulscode.android.mupen64plusae.ActivityHelper$Keys").getField(key).get(null);}
}
