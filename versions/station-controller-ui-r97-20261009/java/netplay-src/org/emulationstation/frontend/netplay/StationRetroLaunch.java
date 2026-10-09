package org.emulationstation.frontend.netplay;
import android.content.*;
import android.os.SystemClock;
import org.emulationstation.frontend.station.StationApi;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

final class StationRetroLaunch {
    private static File root(Context c)throws IOException {File f=new File(c.getNoBackupFilesDir(),"station-online");if(!f.isDirectory()&&!f.mkdirs())throw new IOException("Cannot create online directory");return f.getCanonicalFile();}
    static String prepare(Context c,StationOnlineGame game,JSONObject room,JSONObject snapshot,StationApi.Cancellation cancel)throws Exception {
        game.verifyRoom(room);String rid=room.getString("roomId"),password=room.getString("connectionPassword");
        if(!rid.matches("[0-9a-f]{32}")||!password.matches("[0-9a-f]{64}"))throw new IOException("Invalid room secret");
        boolean multi=game.multiplayerProfile!=null;
        boolean recoverable="relay-wss-v2".equals(room.optString("transport"));boolean relay=multi||recoverable||"relay-wss-v1".equals(room.optString("transport"));JSONObject tunnel=relay&&!multi?room.getJSONObject("relay"):null;
        if(relay&&!multi&&(!"/v1/station/online/relay".equals(tunnel.getString("path"))||!(recoverable?"station-stream.v2":"station-relay.v1").equals(tunnel.getString("protocol"))||!tunnel.getString("ticket").matches("[A-Za-z0-9_-]{43}")||tunnel.getInt("expiresInSeconds")<1))throw new IOException("Invalid relay ticket");
        JSONObject endpoint=relay?new JSONObject().put("address","127.0.0.1").put("port",55435):room.getJSONObject("directEndpoint");String address=endpoint.getString("address");int port=endpoint.getInt("port");
        if(address.length()>63||!address.matches("[0-9a-fA-F:.]+")||port<1024||port>65535)throw new IOException("Invalid direct endpoint");
        File parent=root(c),dir=new File(parent,rid);if(!dir.isDirectory()&&!dir.mkdir())throw new IOException("Cannot create room directory");
        File overlays=new File(parent,"overlays");copyAssets(c,"station-online/overlays",overlays,cancel);
        File autoconfig=new File(parent,"autoconfig");copyAssets(c,"station-online/autoconfig",autoconfig,cancel);
        File saves=new File(dir,"saves"),states=new File(dir,"states"),system=new File(parent,"system");
        for(File d:new File[]{saves,states,system})if(!d.isDirectory()&&!d.mkdirs())throw new IOException("Cannot create netplay data directory");
        // No offline saves or controller configuration are imported or overwritten.
        if(game.platform.equals("neogeo"))throw new StationOnlineGame.Unavailable("Neo Geo ainda precisa da preparação verificada de BIOS e cartuchos .neo. O motor está compilado, mas esta partida ainda não pode ser iniciada.");
        File options=new File(dir,"core-options.cfg");write(options,game.options);
        StringBuilder config=new StringBuilder();
        set(config,"video_driver","gl");set(config,"audio_driver","opensl");set(config,"input_driver","android");set(config,"input_joypad_driver","android");set(config,"menu_driver","rgui");
        set(config,"joypad_autoconfig_dir",autoconfig.toString());set(config,"input_autodetect_enable","true");set(config,"input_max_users","16");
        set(config,"android_input_disconnect_workaround","true");set(config,"notification_show_autoconfig","false");set(config,"notification_show_autoconfig_fails","false");
        set(config,"savefile_directory",saves.toString());set(config,"savestate_directory",states.toString());set(config,"system_directory",system.toString());
        set(config,"core_options_path",options.toString());set(config,"input_overlay",new File(overlays,game.overlay).toString());
        set(config,"netplay_password",password);set(config,"netplay_spectate_password",password);set(config,"netplay_ip_address",address);set(config,"netplay_ip_port",String.valueOf(port));
        for(String key:new String[]{"netplay_public_announce","netplay_use_mitm_server","netplay_start_as_spectator","netplay_nat_traversal","netplay_allow_slaves","netplay_require_slaves","config_save_on_exit","auto_overrides_enable","auto_remaps_enable","auto_shaders_enable","rewind_enable","run_ahead_enabled","preemptive_frames_enable","savestate_auto_load","savestate_auto_save","cheevos_enable","network_cmd_enable","network_remote_enable","menu_show_online_updater","menu_show_core_updater","menu_show_load_core","menu_show_load_content","menu_show_configurations","content_show_netplay","menu_enable_widgets","menu_pause_libretro","pause_nonactive","log_to_file"})set(config,key,"false");
        for(String key:new String[]{"input_overlay_enable","input_overlay_hide_in_menu","video_vsync","audio_sync","netplay_allow_pausing","video_font_enable","block_sram_overwrite"})set(config,key,"true");
        set(config,"input_overlay_opacity","0.55");set(config,"input_overlay_scale_landscape","1.0");set(config,"netplay_max_connections",String.valueOf(multi?room.getJSONArray("roster").length()-1:1));set(config,"netplay_input_latency_frames_min","0");set(config,"netplay_input_latency_frames_range","0");set(config,"input_libretro_device_p1","1");set(config,"input_libretro_device_p2",multi?String.valueOf(game.multiplayerProfile.devices[1]):"1");
        if(multi){
            set(config,"netplay_share_digital","0");set(config,"netplay_share_analog","0");
            int local=StationMultiplayerProfile.slot(room,snapshot.getString("selfId"));
            for(int n=1;n<=16;n++){
                set(config,"netplay_request_device_p"+n,String.valueOf(n==local));
                if(n>2)set(config,"input_libretro_device_p"+n,String.valueOf(n<=game.multiplayerProfile.devices.length?game.multiplayerProfile.devices[n-1]:0));
            }
        }
        File cfg=new File(dir,"retroarch.cfg");write(cfg,config.toString());
        JSONObject launch=new JSONObject().put("expires",SystemClock.elapsedRealtime()+60000).put("roomId",rid)
            .put("role",snapshot.getString("selfId").equals(room.getString("hostId"))?"host":"client")
            .put("address",address).put("port",port).put("rom",game.rom.toString()).put("core",game.core.toString())
            .put("config",cfg.toString()).put("engine",game.engineId);
        if(recoverable){launch.put("recoveryProtocol","station-stream.v2").put("windowBytes",tunnel.getInt("windowBytes")).put("generation",room.getLong("generation")).put("relayCorrelation",room.getString("relayCorrelation"));}
        if(multi){
            int count=room.getJSONArray("roster").length(),local=StationMultiplayerProfile.slot(room,snapshot.getString("selfId"));
            JSONArray links=room.getJSONArray("launchLinks");if(links.length()!=(local==1?count-1:1))throw new IOException("Missing channel tickets");
            launch.put("recoveryProtocol","station-stream.v3").put("generation",room.getLong("generation")).put("localSlot",local)
                .put("expectedDeviceMask",StationMultiplayerProfile.mask(room)).put("participantCount",count).put("multiplayerLinks",links);
        }
        if(relay&&!multi){launch.put("relayTicket",tunnel.getString("ticket"));
            if(tunnel.has("requestProof"))launch.put("relayRequestProof",tunnel.getString("requestProof"));}
        String file="launch-"+UUID.randomUUID()+".json";write(new File(parent,file),launch.toString());cancel.check();return file;
    }
    static JSONObject consume(Context c,String name)throws Exception {
        if(name==null||!name.matches("launch-[0-9a-f-]{36}\\.json"))throw new IOException("Invalid launch file");
        File file=new File(root(c),name);byte[] b;try(InputStream in=new FileInputStream(file)){b=StationOnlineGame.read(in,16384);}Files.delete(file.toPath());
        JSONObject value=new JSONObject(new String(b,StandardCharsets.UTF_8));if(value.getLong("expires")<SystemClock.elapsedRealtime())throw new IOException("Launch expired");
        return value;
    }
    static void discard(Context c,String name){try{if(name!=null&&name.matches("launch-[0-9a-f-]{36}\\.json"))Files.deleteIfExists(new File(root(c),name).toPath());}catch(IOException ignored){}}
    static void clearSecret(Context c,String roomId){try{if(roomId!=null&&roomId.matches("[0-9a-f]{32}"))Files.deleteIfExists(new File(new File(root(c),roomId),"retroarch.cfg").toPath());}catch(IOException ignored){}}
    private static void set(StringBuilder out,String k,String v)throws IOException {if(v.indexOf('"')>=0||v.indexOf('\n')>=0||v.indexOf('\r')>=0)throw new IOException("Unsafe config value");out.append(k).append(" = \"").append(v.replace("\\","/" )).append("\"\n");}
    private static void write(File target,String text)throws IOException {File temp=new File(target.getParentFile(),target.getName()+".tmp");try(FileOutputStream out=new FileOutputStream(temp)){out.write(text.getBytes(StandardCharsets.UTF_8));out.getFD().sync();}Files.move(temp.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
    private static void copyAssets(Context c,String asset,File dst,StationApi.Cancellation cancel)throws Exception {
        String[] children=c.getAssets().list(asset);if(children!=null&&children.length>0){if(!dst.isDirectory()&&!dst.mkdirs())throw new IOException("Cannot create overlay folder");for(String child:children)copyAssets(c,asset+"/"+child,new File(dst,child),cancel);return;}
        cancel.check();try(InputStream in=c.getAssets().open(asset)){byte[] bytes=StationOnlineGame.read(in,4*1024*1024);if(dst.isFile()&&Arrays.equals(Files.readAllBytes(dst.toPath()),bytes))return;File temp=new File(dst.toString()+".tmp");try(FileOutputStream out=new FileOutputStream(temp)){out.write(bytes);out.getFD().sync();}Files.move(temp.toPath(),dst.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
    }
}
