package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.os.SystemClock;
import org.emulationstation.frontend.station.StationApi;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Immutable, private handoff prepared by the room IO worker, never by the UI. */
final class StationDolphinLaunch {
    static final String BACKEND="dolphin-station-v1";
    static final String OPTIONS="backend=dolphin-station-v1\nwire=DPL1\nsettingsPolicy=official-pinned-gameini+host-synchronized-strict-v1\ntraversal=direct\nupnp=false\nindex=false\nqos=false\nchunkedUploadLimit=false\nnetworkMode=fixeddelay\npadBuffer=5\nclientBuffer=1\nsaveLoad=true\nsaveWrite=true\nsyncAllWii=false\nsyncCodes=false\ncheats=false\nrecordInputs=false\nstrictSettingsSync=true\ngolfMode=false\nremoteGbas=false\nsaves=session-only\n";
    private static final int MAX_DESCRIPTOR=32768,MAX_INPUT_FILE=1048576,MAX_INPUT_TOTAL=8388608,MAX_INPUT_FILES=128;
    private static File root(Context context)throws IOException {
        File value=new File(context.getNoBackupFilesDir(),"station-online");
        if(!value.isDirectory()&&!value.mkdirs())throw new IOException("DOLPHIN_LAUNCH_DIRECTORY");
        if(Files.isSymbolicLink(value.toPath()))throw new IOException("DOLPHIN_LAUNCH_SYMLINK");
        return value.getCanonicalFile();
    }
    private static File file(Context context,String name)throws IOException {
        if(name==null||!name.matches("launch-dolphin-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\.json"))throw new IOException("DOLPHIN_LAUNCH_FILE");
        File value=new File(root(context),name);if(Files.isSymbolicLink(value.toPath()))throw new IOException("DOLPHIN_LAUNCH_SYMLINK");return value;
    }
    static String prepare(Context context,StationOnlineGame game,JSONObject room,JSONObject snapshot,StationApi.Cancellation cancel)throws Exception {
        game.verifyRoom(room);
        if(game.multiplayerProfile==null||!profileFor(game.platform).equals(game.multiplayerProfile.controllerProfile)||!OPTIONS.equals(game.options)||!"station-stream.v3".equals(game.recoveryProtocol))throw new IOException("DOLPHIN_PROFILE");
        int count=room.getJSONArray("roster").length(),slot=StationMultiplayerProfile.slot(room,snapshot.getString("selfId")),mask=StationMultiplayerProfile.mask(room);
        if(count<2||count>4||slot<1||slot>4||(mask&~15)!=0||Integer.bitCount(mask)!=count||(mask&1)==0||(mask&(1<<(slot-1)))==0)throw new IOException("DOLPHIN_ROSTER");
        String roomId=room.getString("roomId");long generation=room.getLong("generation");
        if(!roomId.matches("[0-9a-f]{32}")||generation<1)throw new IOException("DOLPHIN_ROOM");
        JSONArray links=room.getJSONArray("launchLinks");checkLinks(links,slot,count,mask);
        JSONObject engine=StationOnlineGame.engine(context,game.platform);verifyBinaries(context,engine,cancel);
        JSONObject launch=new JSONObject().put("backend",BACKEND).put("expires",SystemClock.elapsedRealtime()+60000)
            .put("roomId",roomId).put("generation",generation).put("platform",game.platform).put("role",slot==1?"host":"client")
            .put("localSlot",slot).put("expectedDeviceMask",mask).put("participantCount",count).put("multiplayerLinks",links)
            .put("recoveryProtocol","station-stream.v3").put("rom",game.rom.getCanonicalPath()).put("engine",game.engineId)
            .put("coreSha256",game.coreSha256).put("runtimeSha256",game.runtimeSha256).put("contentSha256",game.contentSha256)
            .put("optionsSha256",game.optionsSha256).put("options",OPTIONS).put("name",game.name).put("itemId",game.itemId)
            .put("profileId",game.multiplayerProfile.profileId).put("profileSha256",game.multiplayerProfile.profileSha256)
            .put("controllerProfile",game.multiplayerProfile.controllerProfile);
        // Copy only controller/UI input preferences. Core settings, saves, cheats,
        // game INIs and quick states are never copied from the offline User tree.
        prepareInputs(context,launch,cancel);
        String name="launch-dolphin-"+UUID.randomUUID()+".json";byte[] bytes=launch.toString().getBytes(StandardCharsets.UTF_8);
        if(bytes.length>MAX_DESCRIPTOR)throw new IOException("DOLPHIN_LAUNCH_SIZE");
        File target=file(context,name);
        try{writeAtomic(target,bytes,false,cancel);cancel.check();return name;}
        catch(Exception failure){Files.deleteIfExists(target.toPath());throw failure;}
    }
    static JSONObject peek(Context context,String name)throws Exception {
        byte[] bytes;try(InputStream input=new FileInputStream(file(context,name))){bytes=StationOnlineGame.read(input,MAX_DESCRIPTOR);}
        JSONObject launch=new JSONObject(new String(bytes,StandardCharsets.UTF_8));validate(launch);
        long now=SystemClock.elapsedRealtime(),expires=launch.getLong("expires");
        if(expires<now||expires-now>60000)throw new IOException("DOLPHIN_LAUNCH_EXPIRED");
        File rom=new File(launch.getString("rom"));if(!rom.isFile()||Files.isSymbolicLink(rom.toPath())||!rom.getCanonicalPath().equals(rom.getPath()))throw new IOException("DOLPHIN_ROM_MISSING");
        return launch;
    }
    /** Fast identity comparison during Application bootstrap; native files were
     * hashed by prepare's IO worker and the installed APK is immutable here. */
    static void verifyIdentity(Context context,JSONObject launch)throws Exception {
        validate(launch);JSONObject engine=StationOnlineGame.engine(context,launch.getString("platform"));
        if(!BACKEND.equals(engine.optString("backend"))||!OPTIONS.equals(engine.getString("options"))||!"libstation_dolphin_online.so".equals(engine.getString("library"))
            ||!launch.getString("engine").equals(engine.getString("engineId"))||!launch.getString("coreSha256").equals(engine.getString("coreSha256"))
            ||!launch.getString("runtimeSha256").equals(engine.getString("runtimeSha256")))throw new IOException("DOLPHIN_ENGINE_CHANGED");
    }
    static JSONObject consume(Context context,String name)throws Exception {
        JSONObject launch=peek(context,name);verifyIdentity(context,launch);Files.delete(file(context,name).toPath());clearPending(context,name);return launch;
    }
    /** Must happen before starting :dolphin: its Application loads one JNI library. */
    static synchronized void publishPending(Context context,String name)throws Exception {
        JSONObject launch=peek(context,name);verifyIdentity(context,launch);File pointer=new File(root(context),"dolphin-pending");
        if(pointer.exists()){
            String existing=readPending(pointer);
            if(name.equals(existing))return;
            try{peek(context,existing);throw new IOException("DOLPHIN_OTHER_LAUNCH_PENDING");}
            catch(IOException failure){if("DOLPHIN_OTHER_LAUNCH_PENDING".equals(failure.getMessage()))throw failure;}
            Files.deleteIfExists(pointer.toPath());
        }
        writeAtomic(pointer,name.getBytes(StandardCharsets.UTF_8),false,new StationApi.Cancellation());
    }
    static void discard(Context context,String name){try{clearPending(context,name);Files.deleteIfExists(file(context,name).toPath());}catch(Exception ignored){}}
    private static synchronized void clearPending(Context context,String name)throws Exception {
        File pointer=new File(root(context),"dolphin-pending");if(pointer.isFile()&&name!=null&&name.equals(readPending(pointer)))Files.delete(pointer.toPath());
    }
    private static String readPending(File pointer)throws Exception {
        if(Files.isSymbolicLink(pointer.toPath()))throw new IOException("DOLPHIN_POINTER_SYMLINK");
        try(InputStream input=new FileInputStream(pointer)){return new String(StationOnlineGame.read(input,128),StandardCharsets.UTF_8);}
    }
    static String profileFor(String platform)throws IOException {
        if("gamecube".equals(platform))return "dolphin-gamecube-four-ports-v1";
        if("wii".equals(platform))return "dolphin-wii-remotes-four-v1";
        throw new IOException("DOLPHIN_PLATFORM");
    }
    private static void validate(JSONObject launch)throws Exception {
        if(!BACKEND.equals(launch.getString("backend"))||!OPTIONS.equals(launch.getString("options"))||!"station-stream.v3".equals(launch.getString("recoveryProtocol"))
            ||!profileFor(launch.getString("platform")).equals(launch.getString("controllerProfile"))||!launch.getString("roomId").matches("[0-9a-f]{32}")||launch.getLong("generation")<1)throw new IOException("DOLPHIN_LAUNCH_BINDING");
        int count=launch.getInt("participantCount"),slot=launch.getInt("localSlot"),mask=launch.getInt("expectedDeviceMask");
        if(count<2||count>4||slot<1||slot>4||(mask&~15)!=0||Integer.bitCount(mask)!=count||(mask&1)==0||(mask&(1<<(slot-1)))==0
            ||!(slot==1?"host":"client").equals(launch.getString("role")))throw new IOException("DOLPHIN_ROSTER");
        checkLinks(launch.getJSONArray("multiplayerLinks"),slot,count,mask);
        for(String key:new String[]{"coreSha256","runtimeSha256","contentSha256","profileSha256","optionsSha256"})if(!launch.getString(key).matches("[0-9a-f]{64}"))throw new IOException("DOLPHIN_IDENTITY");
        String expected=StationOnlineGame.hex(java.security.MessageDigest.getInstance("SHA-256").digest(OPTIONS.getBytes(StandardCharsets.UTF_8)));
        if(!expected.equals(launch.getString("optionsSha256")))throw new IOException("DOLPHIN_OPTIONS");
        expected=StationOnlineGame.hex(java.security.MessageDigest.getInstance("SHA-256").digest(StationMultiplayerProfile.canonical(launch.getString("controllerProfile"),new int[]{1,1,1,1},OPTIONS).getBytes(StandardCharsets.UTF_8)));
        if(!expected.equals(launch.getString("profileSha256")))throw new IOException("DOLPHIN_PROFILE_HASH");
    }
    private static void checkLinks(JSONArray links,int slot,int count,int mask)throws Exception {
        if(links.length()!=(slot==1?count-1:1))throw new IOException("DOLPHIN_CHANNELS");Set<String> ids=new HashSet<>();Set<Integer> peers=new HashSet<>();
        for(int i=0;i<links.length();i++){
            JSONObject link=links.getJSONObject(i);String id=link.getString("linkId");int guest=link.getInt("guestSlot");
            if(!ids.add(id)||!peers.add(guest)||guest<2||guest>4||(mask&(1<<(guest-1)))==0||(slot!=1&&guest!=slot))throw new IOException("DOLPHIN_CHANNEL_BINDING");
            StationMultiplayerSession.checkTicket(link.getJSONObject("ticket"),id,slot==1,slot);
        }
    }
    private static void verifyBinaries(Context context,JSONObject engine,StationApi.Cancellation cancel)throws Exception {
        if(!BACKEND.equals(engine.optString("backend"))||!"libstation_dolphin_online.so".equals(engine.getString("library"))||!OPTIONS.equals(engine.getString("options")))throw new IOException("DOLPHIN_BACKEND");
        for(String field:new String[]{"library","runtimeLibrary"}){
            String name=engine.getString(field);if(!name.matches("lib[A-Za-z0-9_-]+\\.so")||!StationOnlineGame.sha(new File(context.getApplicationInfo().nativeLibraryDir,name),cancel).equals(engine.getString(field.equals("library")?"coreSha256":"runtimeSha256")))throw new IOException("DOLPHIN_BINARY_CHANGED");
        }
        JSONObject dependencies=engine.getJSONObject("dependencySha256");for(Iterator<String> names=dependencies.keys();names.hasNext();){String name=names.next();if(!name.matches("lib[A-Za-z0-9_-]+\\.so")||!StationOnlineGame.sha(new File(context.getApplicationInfo().nativeLibraryDir,name),cancel).equals(dependencies.getString(name)))throw new IOException("DOLPHIN_DEPENDENCY_CHANGED");}
    }
    private static File privateUser(Context context,JSONObject launch)throws Exception {
        File value=new File(root(context),"dolphin/"+launch.getString("roomId")+"/"+launch.getLong("generation")+"/User");
        if(!value.isDirectory()&&!value.mkdirs())throw new IOException("DOLPHIN_INPUT_DIRECTORY");
        if(!value.getCanonicalPath().startsWith(root(context).getPath()+File.separator)||Files.isSymbolicLink(value.toPath()))throw new IOException("DOLPHIN_INPUT_PATH");return value;
    }
    private static void prepareInputs(Context context,JSONObject launch,StationApi.Cancellation cancel)throws Exception {
        File external=context.getExternalFilesDir(null);if(external==null)throw new IOException("DOLPHIN_INPUT_STORAGE");
        File normal=new File(external,"Dolphin"),destination=privateUser(context,launch);int[] budget={0,0};
        for(String path:new String[]{"Config/GCPadNew.ini","Config/WiimoteNew.ini","Config/Android.ini","Config/Profiles/GCPad","Config/Profiles/Wiimote"})
            copyInputs(new File(normal,path),new File(destination,path),normal.getCanonicalPath(),destination.getCanonicalPath(),budget,cancel);
    }
    private static void copyInputs(File source,File target,String fromRoot,String toRoot,int[] budget,StationApi.Cancellation cancel)throws Exception {
        cancel.check();if(!source.exists())return;
        if(Files.isSymbolicLink(source.toPath())||!source.getCanonicalPath().startsWith(fromRoot+File.separator)||!target.getCanonicalPath().startsWith(toRoot+File.separator))throw new IOException("DOLPHIN_INPUT_PATH");
        if(source.isDirectory()){
            File[] children=source.listFiles();if(children==null)throw new IOException("DOLPHIN_INPUT_READ");
            for(File child:children){String name=child.getName();if(name.length()>160||name.equals(".")||name.equals("..")||name.indexOf('/')>=0||name.indexOf('\\')>=0)throw new IOException("DOLPHIN_INPUT_NAME");
                for(int i=0;i<name.length();i++)if(Character.isISOControl(name.charAt(i)))throw new IOException("DOLPHIN_INPUT_NAME");
                if(child.isDirectory())throw new IOException("DOLPHIN_INPUT_NESTED_DIRECTORY");
                if(child.getName().toLowerCase(Locale.ROOT).endsWith(".ini"))copyInputs(child,new File(target,child.getName()),fromRoot,toRoot,budget,cancel);
            }return;
        }
        if(!source.isFile()||source.length()>MAX_INPUT_FILE||++budget[0]>MAX_INPUT_FILES)throw new IOException("DOLPHIN_INPUT_SIZE");
        byte[] bytes;try(InputStream input=new FileInputStream(source)){bytes=StationOnlineGame.read(input,MAX_INPUT_FILE);}
        budget[1]+=bytes.length;if(budget[1]>MAX_INPUT_TOTAL)throw new IOException("DOLPHIN_INPUT_TOTAL");
        File parent=target.getParentFile();if(!parent.isDirectory()&&!parent.mkdirs())throw new IOException("DOLPHIN_INPUT_DIRECTORY");
        writeAtomic(target,bytes,true,cancel);
    }
    private static void writeAtomic(File target,byte[] bytes,boolean replace,StationApi.Cancellation cancel)throws Exception {
        File temp=new File(target.getParentFile(),target.getName()+"."+UUID.randomUUID()+".tmp");
        try{cancel.check();try(FileOutputStream output=new FileOutputStream(temp)){output.write(bytes);output.getFD().sync();}cancel.check();
            if(Files.isSymbolicLink(target.toPath()))throw new IOException("DOLPHIN_ATOMIC_SYMLINK");
            if(replace)Files.move(temp.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
            else Files.move(temp.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE);
        }finally{Files.deleteIfExists(temp.toPath());}
    }
}
