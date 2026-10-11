package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.os.SystemClock;
import android.os.Build;
import android.os.Environment;
import org.emulationstation.frontend.station.StationApi;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;

/** Private one-use handoff. The room worker has already checked the signed,
 * per-game profile and the exact installed content; metadata never grants seats. */
final class StationPsxLaunch {
    static final String BACKEND="psx-player-station-v1";
    static final String OWNER_SHA="62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6";
    static final String CORE_SHA="e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9";
    private static final int MAX_DESCRIPTOR=32768;
    private static File root(Context context)throws IOException {
        File value=new File(context.getNoBackupFilesDir(),"station-online");
        if(!value.isDirectory()&&!value.mkdirs())throw new IOException("PSX_LAUNCH_DIRECTORY");
        if(Files.isSymbolicLink(value.toPath()))throw new IOException("PSX_LAUNCH_SYMLINK");
        return value.getCanonicalFile();
    }
    private static File file(Context context,String name)throws IOException {
        if(name==null||!name.matches("launch-psx-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\.json"))throw new IOException("PSX_LAUNCH_FILE");
        File value=new File(root(context),name);
        if(Files.isSymbolicLink(value.toPath()))throw new IOException("PSX_LAUNCH_SYMLINK");
        return value;
    }
    static String prepare(Context context,StationOnlineGame game,JSONObject room,JSONObject snapshot,StationApi.Cancellation cancel)throws Exception {
        if(Build.VERSION.SDK_INT<28)throw new StationOnlineGame.Unavailable("O online de PlayStation nesta edi\u00e7\u00e3o requer Android 9 ou mais recente. O modo normal continua dispon\u00edvel.");
        game.verifyRoom(room);
        if(!"psx".equals(game.platform)||!BACKEND.equals(game.backend)||game.multiplayerProfile==null||
            !"standard-2p-v1".equals(game.multiplayerProfile.controllerProfile)||!StationPsxPolicy.OPTIONS.equals(game.options)||
            !"station-stream.v3".equals(game.recoveryProtocol))throw new IOException("PSX_PROFILE");
        int count=room.getJSONArray("roster").length(),slot=StationMultiplayerProfile.slot(room,snapshot.getString("selfId")),mask=StationMultiplayerProfile.mask(room);
        if(count!=2||mask!=3||(slot!=1&&slot!=2))throw new IOException("PSX_ROSTER");
        String roomId=room.getString("roomId");long generation=room.getLong("generation");
        if(!roomId.matches("[0-9a-f]{32}")||generation<1)throw new IOException("PSX_ROOM");
        JSONArray links=room.getJSONArray("launchLinks");checkLinks(links,slot);
        verifyBinaries(context,StationOnlineGame.engine(context,"psx"),cancel);
        String name="launch-psx-"+UUID.randomUUID()+".json";
        File home=freshHome(context,name);
        preparePresentation(context,home,cancel);
        JSONObject launch=new JSONObject().put("backend",BACKEND).put("expires",SystemClock.elapsedRealtime()+60000)
            .put("roomId",roomId).put("generation",generation).put("platform","psx").put("role",slot==1?"host":"client")
            .put("localSlot",slot).put("expectedDeviceMask",mask).put("participantCount",count).put("multiplayerLinks",links)
            .put("recoveryProtocol","station-stream.v3").put("rom",game.rom.getCanonicalPath()).put("engine",game.engineId)
            .put("coreSha256",game.coreSha256).put("ownerSha256",OWNER_SHA).put("runtimeSha256",game.runtimeSha256)
            .put("contentSha256",game.contentSha256).put("optionsSha256",game.optionsSha256).put("options",StationPsxPolicy.OPTIONS)
            .put("name",game.name).put("itemId",game.itemId).put("profileId",game.multiplayerProfile.profileId)
            .put("profileSha256",game.multiplayerProfile.profileSha256).put("controllerProfile","standard-2p-v1")
            .put("privateHome",home.getPath()).put("contentIdentityScheme",contentScheme(game.rom));
        launch.put("bindingSha256",binding(launch));validate(context,name,launch);
        byte[] bytes=launch.toString().getBytes(StandardCharsets.UTF_8);
        if(bytes.length>MAX_DESCRIPTOR)throw new IOException("PSX_LAUNCH_SIZE");
        File target=file(context,name),temp=new File(target.getParentFile(),name+".tmp");
        try {
            cancel.check();try(FileOutputStream out=new FileOutputStream(temp)){out.write(bytes);out.getFD().sync();}
            cancel.check();Files.move(temp.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE);return name;
        }catch(Exception failure){Files.deleteIfExists(target.toPath());throw failure;}
        finally{Files.deleteIfExists(temp.toPath());}
    }
    static JSONObject consume(Context context,String name)throws Exception {
        if(Build.VERSION.SDK_INT<28)throw new StationOnlineGame.Unavailable("O online de PlayStation nesta edi\u00e7\u00e3o requer Android 9 ou mais recente. O modo normal continua dispon\u00edvel.");
        JSONObject launch;
        try(InputStream input=new FileInputStream(file(context,name))){launch=new JSONObject(new String(StationOnlineGame.read(input,MAX_DESCRIPTOR),StandardCharsets.UTF_8));}
        validate(context,name,launch);long now=SystemClock.elapsedRealtime(),expires=launch.getLong("expires");
        if(expires<now||expires-now>60000)throw new IOException("PSX_LAUNCH_EXPIRED");
        JSONObject engine=StationOnlineGame.engine(context,"psx");verifyBinaries(context,engine,new StationApi.Cancellation());
        if(!launch.getString("engine").equals(engine.getString("engineId"))||!launch.getString("runtimeSha256").equals(engine.getString("runtimeSha256")))throw new IOException("PSX_ENGINE_CHANGED");
        File rom=new File(launch.getString("rom"));
        if(!rom.isFile()||Files.isSymbolicLink(rom.toPath())||!rom.getPath().equals(rom.getCanonicalPath()))throw new IOException("PSX_ROM_MISSING");
        StationApi.Cancellation cancel=new StationApi.Cancellation();
        String scheme=contentScheme(rom);
        if(!scheme.equals(launch.getString("contentIdentityScheme"))||
            !StationContentIdentity.identity(rom,scheme,cancel).equals(launch.getString("contentSha256")))throw new IOException("PSX_CONTENT_CHANGED");
        // Hashing the full disc belongs on the preparation worker. A descriptor
        // that expired during that IO cannot silently start a stale launch.
        now=SystemClock.elapsedRealtime();if(expires<now||expires-now>60000)throw new IOException("PSX_LAUNCH_EXPIRED");
        Files.delete(file(context,name).toPath());return launch;
    }
    static void discard(Context context,String name){try{Files.deleteIfExists(file(context,name).toPath());}catch(Exception ignored){}}
    private static String contentScheme(File rom)throws IOException {
        String lower=rom.getName().toLowerCase(Locale.ROOT);
        if(lower.endsWith(".cue"))return "cue-set-v1";
        if(lower.endsWith(".chd")||lower.endsWith(".pbp"))return "";
        throw new IOException("PSX_CONTENT_FORMAT");
    }
    private static void validate(Context context,String name,JSONObject launch)throws Exception {
        if(!BACKEND.equals(launch.getString("backend"))||!"psx".equals(launch.getString("platform"))||
            !StationPsxPolicy.OPTIONS.equals(launch.getString("options"))||!"station-stream.v3".equals(launch.getString("recoveryProtocol"))||
            !"standard-2p-v1".equals(launch.getString("controllerProfile"))||!launch.getString("roomId").matches("[0-9a-f]{32}")||
            launch.getLong("generation")<1||launch.getInt("participantCount")!=2||launch.getInt("expectedDeviceMask")!=3)throw new IOException("PSX_LAUNCH_BINDING");
        int slot=launch.getInt("localSlot");if((slot!=1&&slot!=2)||!(slot==1?"host":"client").equals(launch.getString("role")))throw new IOException("PSX_ROLE");
        checkLinks(launch.getJSONArray("multiplayerLinks"),slot);
        if(!contentScheme(new File(launch.getString("rom"))).equals(launch.getString("contentIdentityScheme")))throw new IOException("PSX_CONTENT_SCHEME");
        for(String key:new String[]{"coreSha256","ownerSha256","runtimeSha256","contentSha256","profileSha256","optionsSha256","bindingSha256"})
            if(!launch.getString(key).matches("[0-9a-f]{64}"))throw new IOException("PSX_IDENTITY");
        if(!CORE_SHA.equals(launch.getString("coreSha256"))||!OWNER_SHA.equals(launch.getString("ownerSha256"))||
            !StationPsxPolicy.OPTIONS_SHA.equals(launch.getString("optionsSha256"))||!binding(launch).equals(launch.getString("bindingSha256")))throw new IOException("PSX_BINDING_HASH");
        String profile=StationMultiplayerProfile.canonical("standard-2p-v1",new int[]{1,1},StationPsxPolicy.OPTIONS);
        if(!digest(profile).equals(launch.getString("profileSha256")))throw new IOException("PSX_PROFILE_HASH");
        File home=new File(launch.getString("privateHome"));
        if(!expectedHome(context,name).equals(home.getCanonicalFile())||Files.isSymbolicLink(home.toPath())||!home.isDirectory())throw new IOException("PSX_HOME_BINDING");
    }
    private static void checkLinks(JSONArray links,int slot)throws Exception {
        if(links.length()!=1)throw new IOException("PSX_CHANNELS");JSONObject link=links.getJSONObject(0);
        if(link.getInt("guestSlot")!=2)throw new IOException("PSX_CHANNEL_BINDING");
        StationMultiplayerSession.checkTicket(link.getJSONObject("ticket"),link.getString("linkId"),slot==1,slot);
    }
    private static String binding(JSONObject launch)throws Exception {
        // Identical on host and guest. Tickets, nickname, slot and home differ
        // locally and are intentionally absent from this immutable game binding.
        StringBuilder value=new StringBuilder("station-psx-binding-v1\n");
        for(String key:new String[]{"roomId","generation","engine","coreSha256","ownerSha256","runtimeSha256","contentSha256","profileSha256","optionsSha256","contentIdentityScheme","expectedDeviceMask"}) {
            String text=String.valueOf(launch.get(key));if(text.indexOf('\n')>=0||text.indexOf('\r')>=0)throw new IOException("PSX_BINDING_VALUE");
            value.append(key).append('=').append(text).append('\n');
        }return digest(value.toString());
    }
    private static String digest(String value)throws Exception {return StationOnlineGame.hex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));}
    static byte[] unhex(String value)throws IOException {
        if(value==null||!value.matches("[0-9a-f]{64}"))throw new IOException("PSX_DIGEST");
        byte[] out=new byte[32];for(int i=0;i<32;i++)out[i]=(byte)Integer.parseInt(value.substring(i*2,i*2+2),16);return out;
    }
    private static void verifyBinaries(Context context,JSONObject engine,StationApi.Cancellation cancel)throws Exception {
        if(!BACKEND.equals(engine.optString("backend"))||!CORE_SHA.equals(engine.getString("coreSha256"))||
            !"libpcsx_rearmed_libretro_android.so".equals(engine.getString("library"))||
            !"libstation_psx_online.so".equals(engine.getString("runtimeLibrary"))||!StationPsxPolicy.OPTIONS.equals(engine.getString("options")))throw new IOException("PSX_BACKEND");
        for(String field:new String[]{"library","runtimeLibrary"}){
            String name=engine.getString(field);if(!name.matches("lib[A-Za-z0-9_-]+\\.so")||!StationOnlineGame.sha(new File(context.getApplicationInfo().nativeLibraryDir,name),cancel).equals(engine.getString(field.equals("library")?"coreSha256":"runtimeSha256")))throw new IOException("PSX_BINARY_CHANGED");
        }
        JSONObject dependencies=engine.getJSONObject("dependencySha256");
        if(!OWNER_SHA.equals(dependencies.getString("libmain.so"))||!dependencies.has("libSDL2.so"))throw new IOException("PSX_OWNER_DEPENDENCIES");
        for(Iterator<String> names=dependencies.keys();names.hasNext();){String name=names.next();
            if(!name.matches("lib[A-Za-z0-9_-]+\\.so")||!StationOnlineGame.sha(new File(context.getApplicationInfo().nativeLibraryDir,name),cancel).equals(dependencies.getString(name)))throw new IOException("PSX_DEPENDENCY_CHANGED");
        }
    }
    private static File expectedHome(Context context,String name)throws IOException {
        file(context,name);File parent=new File(context.getFilesDir(),"station-psx-online");
        if(Files.isSymbolicLink(parent.toPath())||!parent.getCanonicalPath().startsWith(context.getFilesDir().getCanonicalPath()+File.separator))throw new IOException("PSX_HOME_PATH");
        File launch=new File(parent,name.substring(0,name.length()-5));
        if(Files.isSymbolicLink(launch.toPath()))throw new IOException("PSX_HOME_SYMLINK");
        return new File(launch,"home").getCanonicalFile();
    }
    private static File freshHome(Context context,String name)throws IOException {
        File home=expectedHome(context,name);
        if(home.exists()||!home.mkdirs())throw new IOException("PSX_HOME_NOT_FRESH");
        for(String path:new String[]{".emulationstation",".emulationstation/bios",".emulationstation/saves",".emulationstation/core-options"}) {
            File value=new File(home,path);if(!value.mkdirs()&&!value.isDirectory())throw new IOException("PSX_HOME_DIRECTORY");
        }return home;
    }
    private static void preparePresentation(Context context,File home,StationApi.Cancellation cancel)throws Exception {
        File resources=new File(home,".emulationstation/resources");
        if(!resources.mkdir())throw new IOException("PSX_FONT_DIRECTORY");
        byte[] font;
        try(InputStream input=context.getAssets().open("resources/sst_medium_condensed.ttf")){font=StationOnlineGame.read(input,1048576);}
        if(font.length!=479776||!StationOnlineGame.hex(MessageDigest.getInstance("SHA-256").digest(font)).equals("cdc99f42f1d69bf8b798ec9d09c4979b574242d7f77aee775322dc286f7681f4"))throw new IOException("PSX_NORMAL_FONT_IDENTITY");
        cancel.check();try(FileOutputStream out=new FileOutputStream(new File(resources,"sst_medium_condensed.ttf"))){out.write(font);out.getFD().sync();}
        // Exact normal HOME from ESActivity.getHomeDir. Read only controller
        // selection names and display stretch: no core settings, BIOS or saves.
        File source=new File(Environment.getExternalStorageDirectory(),"EmulationStation/.emulationstation/es_settings.cfg");
        copyPresentationSettings(source,home,cancel);
    }
    private static void copyPresentationSettings(File source,File home,StationApi.Cancellation cancel)throws Exception {
        if(!source.exists())return;
        if(!source.isFile()||Files.isSymbolicLink(source.toPath())||source.length()>1048576)throw new IOException("PSX_INPUT_PREFERENCES");
        DocumentBuilderFactory factory=DocumentBuilderFactory.newInstance();
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
        factory.setFeature("http://xml.org/sax/features/external-general-entities",false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities",false);
        factory.setExpandEntityReferences(false);
        Document document;try(InputStream input=new FileInputStream(source)){document=factory.newDocumentBuilder().parse(input);}
        StringBuilder config=new StringBuilder("<?xml version=\"1.0\"?>\n<config>\n");
        NodeList nodes=document.getElementsByTagName("string");Set<String> found=new HashSet<>();
        for(int i=0;i<nodes.getLength();i++){cancel.check();Element element=(Element)nodes.item(i);String key=element.getAttribute("name");
            if(!"Player1Controller".equals(key)&&!"Player2Controller".equals(key))continue;
            String value=element.getAttribute("value");if(value.length()>512||!found.add(key))throw new IOException("PSX_INPUT_PREFERENCE_VALUE");
            for(int j=0;j<value.length();j++)if(Character.isISOControl(value.charAt(j)))throw new IOException("PSX_INPUT_PREFERENCE_VALUE");
            config.append("  <string name=\"").append(key).append("\" value=\"")
                .append(value.replace("&","&amp;").replace("\"","&quot;").replace("<","&lt;").replace(">","&gt;")).append("\"/>\n");
        }
        NodeList bools=document.getElementsByTagName("bool");
        for(int i=0;i<bools.getLength();i++){cancel.check();Element element=(Element)bools.item(i);
            if(!"LibretroStretch".equals(element.getAttribute("name")))continue;
            String value=element.getAttribute("value");
            if(!("true".equals(value)||"false".equals(value))||!found.add("LibretroStretch"))throw new IOException("PSX_DISPLAY_PREFERENCE_VALUE");
            config.append("  <bool name=\"LibretroStretch\" value=\"").append(value).append("\"/>\n");
        }config.append("</config>\n");
        try(FileOutputStream out=new FileOutputStream(new File(home,".emulationstation/es_settings.cfg"))){out.write(config.toString().getBytes(StandardCharsets.UTF_8));out.getFD().sync();}
    }
}
