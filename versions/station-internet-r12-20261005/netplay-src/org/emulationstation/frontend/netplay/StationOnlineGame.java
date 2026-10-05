package org.emulationstation.frontend.netplay;
import android.content.Context;
import org.emulationstation.frontend.station.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

final class StationOnlineGame {
    static final class Unavailable extends IOException {Unavailable(String message){super(message);}}
    final String itemId,name,platform,engineId,coreSha256,runtimeSha256,contentSha256,optionsSha256,overlay;
    final File rom,core,runtime;final String options;
    private StationOnlineGame(String id,String name,String platform,JSONObject e,File rom,File core,File runtime,String hash,String options)throws Exception {
        itemId=id;this.name=name;this.platform=platform;this.rom=rom;this.core=core;this.runtime=runtime;
        engineId=e.getString("engineId");coreSha256=e.getString("coreSha256");runtimeSha256=e.getString("runtimeSha256");
        overlay=e.getString("overlay");contentSha256=hash;this.options=options;optionsSha256=hex(MessageDigest.getInstance("SHA-256").digest(options.getBytes(StandardCharsets.UTF_8)));
    }
    static String platform(String raw)throws IOException {
        String f=StationPlatforms.resolve(raw).folder;
        if(f.equals("super-nintendo")||f.equals("super-nintendo--br"))return "snes";
        if(f.equals("megadrive")||f.equals("megadrive--br"))return "megadrive";
        if(f.equals("neo-geo"))return "neogeo";
        throw new Unavailable("Esta plataforma ainda não tem um motor aprovado para estas salas. O modo local foi preservado.");
    }
    static StationOnlineGame prepare(Context context,StationOnlineClient client,String itemId,JSONObject snapshot,StationApi.Cancellation cancel)throws Exception {
        StationCatalog.Item item=client.item(itemId);if(item==null)throw new Unavailable("Selecione um jogo do catálogo antes de criar a sala.");
        String platform=platform(item.platform);JSONObject manifest;
        try(InputStream input=context.getAssets().open("station-online/engines.json")){manifest=new JSONObject(new String(read(input,32768),StandardCharsets.UTF_8));}
        JSONArray entries=manifest.getJSONArray("engines");JSONObject engine=null;
        for(int i=0;i<entries.length();i++){JSONObject e=entries.getJSONObject(i);if(platform.equals(e.getString("platform"))){engine=e;break;}}
        if(engine==null)throw new Unavailable("O motor desta plataforma não está incluído nesta edição.");
        if(!engine.optBoolean("launchReady",false))throw new Unavailable("Neo Geo ainda precisa da preparação verificada de BIOS e cartuchos .neo. As salas dessa plataforma ainda não estão liberadas.");
        boolean allowed=false;JSONArray approved=snapshot.getJSONArray("engines");
        for(int i=0;i<approved.length();i++){JSONObject e=approved.getJSONObject(i);if(e.getString("engineId").equals(engine.getString("engineId"))&&e.getString("coreSha256").equals(engine.getString("coreSha256"))&&e.getString("runtimeSha256").equals(engine.getString("runtimeSha256")))allowed=true;}
        if(!allowed)throw new Unavailable("Este motor ainda não foi liberado pelo servidor para partidas nesta edição.");
        File rom=new File(StationFrontend.installedPathForItem(itemId));String lower=rom.getName().toLowerCase(Locale.ROOT);
        boolean ext=false;JSONArray extensions=engine.getJSONArray("extensions");for(int i=0;i<extensions.length();i++)if(lower.endsWith("."+extensions.getString(i)))ext=true;
        if(!ext)throw new Unavailable(platform.equals("neogeo")?"Geolith exige o formato .neo. Este jogo precisa de uma conversão verificada antes de jogar online.":"O arquivo instalado ainda não é um cartucho compatível com este motor online.");
        File core=new File(context.getApplicationInfo().nativeLibraryDir,engine.getString("library"));
        File runtime=new File(context.getApplicationInfo().nativeLibraryDir,"libstation_retroarch.so");
        if(!sha(core,cancel).equals(engine.getString("coreSha256"))||!sha(runtime,cancel).equals(engine.getString("runtimeSha256")))throw new Unavailable("O motor instalado não corresponde à edição verificada. Atualize o aplicativo.");
        return new StationOnlineGame(itemId,item.name,platform,engine,rom,core,runtime,sha(rom,cancel),engine.getString("options"));
    }
    JSONObject fields(JSONObject request)throws JSONException {return request.put("itemId",itemId).put("engineId",engineId).put("coreSha256",coreSha256).put("runtimeSha256",runtimeSha256).put("contentSha256",contentSha256).put("optionsSha256",optionsSha256);}
    void verifyRoom(JSONObject room)throws Exception {
        if(!itemId.equals(room.getString("itemId"))||!engineId.equals(room.getString("engineId"))||!coreSha256.equals(room.getString("coreSha256"))||!runtimeSha256.equals(room.getString("runtimeSha256"))||!contentSha256.equals(room.getString("contentSha256"))||!optionsSha256.equals(room.getString("optionsSha256")))throw new Unavailable("Os dados da sala não correspondem ao jogo preparado.");
    }
    static String sha(File file,StationApi.Cancellation cancel)throws Exception {
        if(!file.isFile()||Files.isSymbolicLink(file.toPath()))throw new Unavailable("O arquivo necessário não está instalado.");
        MessageDigest d=MessageDigest.getInstance("SHA-256");byte[] b=new byte[131072];
        try(InputStream in=new FileInputStream(file)){int n;while((n=in.read(b))!=-1){cancel.check();d.update(b,0,n);}}return hex(d.digest());
    }
    static String hex(byte[] b){StringBuilder out=new StringBuilder();for(byte v:b)out.append(String.format(Locale.ROOT,"%02x",v&255));return out.toString();}
    static byte[] read(InputStream in,int maximum)throws IOException {ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){if(out.size()+n>maximum)throw new IOException("Asset too large");out.write(b,0,n);}return out.toByteArray();}
}
