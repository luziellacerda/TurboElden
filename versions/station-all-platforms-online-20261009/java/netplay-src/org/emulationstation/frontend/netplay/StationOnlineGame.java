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
    final File rom,core,runtime;final String options,recoveryProtocol;final StationMultiplayerProfile multiplayerProfile;
    private StationOnlineGame(String id,String name,String platform,JSONObject e,File rom,File core,File runtime,String hash,String options,StationMultiplayerProfile profile)throws Exception {
        multiplayerProfile=profile;itemId=id;this.name=name;this.platform=platform;this.rom=rom;this.core=core;this.runtime=runtime;
        recoveryProtocol=e.optString("recoveryProtocol","");engineId=e.getString("engineId");coreSha256=e.getString("coreSha256");runtimeSha256=e.getString("runtimeSha256");
        overlay=e.getString("overlay");contentSha256=hash;this.options=options;optionsSha256=hex(MessageDigest.getInstance("SHA-256").digest(options.getBytes(StandardCharsets.UTF_8)));
    }
    static JSONObject engine(Context context,String raw)throws Exception {
        String platform=platform(raw);JSONObject manifest;try(InputStream input=context.getAssets().open("station-online/engines.json")){manifest=new JSONObject(new String(read(input,32768),StandardCharsets.UTF_8));}
        JSONArray entries=manifest.getJSONArray("engines");for(int i=0;i<entries.length();i++){JSONObject e=entries.getJSONObject(i);if(platform.equals(e.getString("platform"))&&e.optBoolean("launchReady")&&"station-stream.v3".equals(e.optString("recoveryProtocol")))return e;}
        JSONArray policies=manifest.optJSONArray("platformPolicies");
        for(int i=0;policies!=null&&i<policies.length();i++){JSONObject policy=policies.getJSONObject(i);if(platform.equals(policy.optString("platform"))&&!policy.optString("reason").isEmpty())throw new Unavailable(policy.getString("reason"));}
        throw new Unavailable("Esta plataforma ainda aguarda um motor aprovado para estas salas.");
    }
    static List<StationMultiplayerProfile> profiles(Context context,StationOnlineClient client,String itemId,StationApi.Cancellation cancel)throws Exception {
        StationCatalog.Item item=client.item(itemId);if(item==null)throw StationMultiplayerProfile.unavailable();
        return StationMultiplayerProfile.choices(client.profileSnapshot(itemId,cancel),itemId,engine(context,item.platform));
    }
    static List<StationMultiplayerProfile> classifications(Context context,StationOnlineClient client,String itemId,StationApi.Cancellation cancel)throws Exception {
        StationCatalog.Item item=client.item(itemId);if(item==null)throw StationMultiplayerProfile.unavailable();
        return StationMultiplayerProfile.classifications(client.profileSnapshot(itemId,cancel),itemId,engine(context,item.platform));
    }
    static String platform(String raw)throws IOException {
        return StationOnlinePlatformPolicy.platform(raw);
    }
    static StationOnlineGame prepare(Context context,StationOnlineClient client,String itemId,JSONObject snapshot,StationApi.Cancellation cancel)throws Exception {
        JSONObject own=snapshot==null?null:snapshot.optJSONObject("room");String profileId=own!=null&&itemId.equals(own.optString("itemId"))?own.optString("profileId"):"";
        return prepare(context,client,itemId,snapshot,cancel,profileId);
    }
    static StationOnlineGame prepare(Context context,StationOnlineClient client,String itemId,JSONObject snapshot,StationApi.Cancellation cancel,String profileId)throws Exception {
        StationCatalog.Item item=client.item(itemId);if(item==null)throw new Unavailable("Selecione um jogo do catálogo antes de criar a sala.");
        String platform=platform(item.platform);JSONObject engine=engine(context,item.platform);
        if("station-stream.v3".equals(engine.optString("recoveryProtocol"))){
            JSONObject fresh=client.profileSnapshot(itemId,cancel);
            StationMultiplayerProfile p=StationMultiplayerProfile.find(fresh,itemId,engine,profileId);
            File rom=installedRom(itemId);String hash=StationContentIdentity.identity(rom,cancel);
            if(!p.contentSha256.equals(hash))throw new Unavailable("A edição instalada não corresponde ao jogo catalogado para esta sala.");
            File core=new File(context.getApplicationInfo().nativeLibraryDir,engine.getString("library"));File runtime=new File(context.getApplicationInfo().nativeLibraryDir,"libstation_retroarch.so");
            if(!sha(core,cancel).equals(p.coreSha256)||!sha(runtime,cancel).equals(p.runtimeSha256))throw new Unavailable("Atualize o aplicativo para usar o motor aprovado desta sala.");
            boolean extension=false;JSONArray ext=engine.getJSONArray("extensions");for(int j=0;j<ext.length();j++)if(rom.getName().toLowerCase(Locale.ROOT).endsWith("."+ext.getString(j)))extension=true;
            if(!extension)throw new Unavailable("O formato do jogo instalado não é compatível com este motor online.");
            return new StationOnlineGame(itemId,item.name,platform,engine,rom,core,runtime,hash,p.options,p);
        }
        // R77 never grants new seats from the old descriptive metadata.
        if(!snapshot.optBoolean("legacyGameProfileVerified",false))throw StationMultiplayerProfile.unavailable();
        boolean allowed=false;JSONArray approved=snapshot.getJSONArray("engines");
        for(int i=0;i<approved.length();i++){JSONObject e=approved.getJSONObject(i);if(e.getString("engineId").equals(engine.getString("engineId"))&&e.getString("coreSha256").equals(engine.getString("coreSha256"))&&e.getString("runtimeSha256").equals(engine.getString("runtimeSha256")))allowed=true;}
        if("station-stream.v2".equals(engine.optString("recoveryProtocol"))){JSONArray capabilities=snapshot.optJSONArray("recoveryCapabilities");boolean recovery=false;for(int i=0;capabilities!=null&&i<capabilities.length();i++)if("station-stream.v2".equals(capabilities.optString(i)))recovery=true;if(!recovery)throw new Unavailable("A retomada online aguarda habilitação desta edição no servidor.");}
        if(!allowed)throw new Unavailable("Este motor ainda não foi liberado pelo servidor para partidas nesta edição.");
        File rom=installedRom(itemId);String lower=rom.getName().toLowerCase(Locale.ROOT);
        boolean ext=false;JSONArray extensions=engine.getJSONArray("extensions");for(int i=0;i<extensions.length();i++)if(lower.endsWith("."+extensions.getString(i)))ext=true;
        if(!ext)throw new Unavailable(platform.equals("neogeo")?"Geolith exige o formato .neo. Este jogo precisa de uma conversão verificada antes de jogar online.":"O arquivo instalado ainda não é um cartucho compatível com este motor online.");
        File core=new File(context.getApplicationInfo().nativeLibraryDir,engine.getString("library"));
        File runtime=new File(context.getApplicationInfo().nativeLibraryDir,"libstation_retroarch.so");
        if(!sha(core,cancel).equals(engine.getString("coreSha256"))||!sha(runtime,cancel).equals(engine.getString("runtimeSha256")))throw new Unavailable("O motor instalado não corresponde à edição verificada. Atualize o aplicativo.");
        return new StationOnlineGame(itemId,item.name,platform,engine,rom,core,runtime,sha(rom,cancel),engine.getString("options"),null);
    }
    static File installedRom(String itemId)throws Exception {
        final String path;
        try {path=StationFrontend.installedPathForItem(itemId);}
        catch(IOException e) {
            String reason=e.getMessage();
            if("Baixe o jogo antes de criar ou entrar em uma sala".equals(reason))throw new Unavailable("Baixe este jogo primeiro. Volte ao catálogo, toque em Baixar e depois em Jogar online.");
            if("Catálogo não preparado".equals(reason)||"Jogo não está no catálogo atual".equals(reason))throw new Unavailable("Volte ao catálogo e selecione novamente o jogo antes de abrir a sala.");
            throw new Unavailable("Não foi possível acessar o jogo instalado. Confira o arquivo no catálogo antes de jogar online.");
        }
        if(path==null||path.isEmpty())throw new Unavailable("Baixe este jogo antes de criar ou entrar em uma sala.");
        File file=new File(path);
        if(!file.isFile()||Files.isSymbolicLink(file.toPath()))throw new Unavailable("O arquivo do jogo não está disponível. Confira a instalação no catálogo.");
        return file;
    }
    JSONObject fields(JSONObject request)throws JSONException {if(multiplayerProfile!=null)return multiplayerProfile.fields(request);if(!recoveryProtocol.isEmpty())request.put("recoveryProtocol",recoveryProtocol);return request.put("itemId",itemId).put("engineId",engineId).put("coreSha256",coreSha256).put("runtimeSha256",runtimeSha256).put("contentSha256",contentSha256).put("optionsSha256",optionsSha256);}
    void verifyRoom(JSONObject room)throws Exception {
        if(multiplayerProfile!=null){multiplayerProfile.verify(room);return;}
        if(!recoveryProtocol.equals(room.optString("recoveryProtocol",""))||!itemId.equals(room.getString("itemId"))||!engineId.equals(room.getString("engineId"))||!coreSha256.equals(room.getString("coreSha256"))||!runtimeSha256.equals(room.getString("runtimeSha256"))||!contentSha256.equals(room.getString("contentSha256"))||!optionsSha256.equals(room.getString("optionsSha256")))throw new Unavailable("Os dados da sala não correspondem ao jogo preparado.");
    }
    static String sha(File file,StationApi.Cancellation cancel)throws Exception {
        if(!file.isFile()||Files.isSymbolicLink(file.toPath()))throw new Unavailable("O arquivo necessário não está instalado.");
        MessageDigest d=MessageDigest.getInstance("SHA-256");byte[] b=new byte[131072];
        try(InputStream in=new FileInputStream(file)){int n;while((n=in.read(b))!=-1){cancel.check();d.update(b,0,n);}}return hex(d.digest());
    }
    static String hex(byte[] b){StringBuilder out=new StringBuilder();for(byte v:b)out.append(String.format(Locale.ROOT,"%02x",v&255));return out.toString();}
    static byte[] read(InputStream in,int maximum)throws IOException {ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){if(out.size()+n>maximum)throw new IOException("Asset too large");out.write(b,0,n);}return out.toByteArray();}
}
