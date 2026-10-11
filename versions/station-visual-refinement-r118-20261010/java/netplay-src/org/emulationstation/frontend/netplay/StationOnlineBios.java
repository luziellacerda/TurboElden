package org.emulationstation.frontend.netplay;

import android.content.Context;
import org.emulationstation.frontend.station.StationApi;
import org.emulationstation.frontend.station.StationBundledFiles;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Online engines use the APK's firmware, in their own directory, without importing offline saves. */
final class StationOnlineBios {
    static void prepare(Context context,String platform,File system,StationApi.Cancellation cancel)throws Exception {
        prepare(new StationBundledFiles.Source(){
            public String[] list(String path)throws IOException{return context.getAssets().list(path);}
            public InputStream open(String path)throws IOException{return context.getAssets().open(path);}
        },platform,system.toPath(),cancel);
    }
    static void prepare(StationBundledFiles.Source assets,String platform,Path system,StationApi.Cancellation cancel)throws Exception {
        Set<String> names=new HashSet<>();boolean required=false;
        if("neogeo".equals(platform)){names.add("neogeo.zip");required=true;}
        else if("fbneo".equals(platform)||"cps1".equals(platform)||"cps2".equals(platform)||"cps3".equals(platform))names.addAll(Arrays.asList("neogeo.zip","pgm.zip","skns.zip","decocass.zip","cchip.zip","isgsm.zip","namcoc69.zip","ym2608.zip"));
        else if("neogeocd".equals(platform)){
            // The pinned NeoCD core includes its own HLE fallback. Retail firmware remains preferred.
            names.addAll(Arrays.asList("neocd.zip","neocdz.zip","neocd.bin","top-sp1.bin","front-sp1.bin","neocd_f.bin","neocd_sf.bin","neocd_st.bin","neocd_t.bin","neocd_z.bin","neocd_sz.bin","uni-bioscd.rom","uni-bioscd33.rom"));
        }else if("psx".equals(platform)){
            names.addAll(Arrays.asList("psxonpsp660.bin","scph101.bin","scph7001.bin","scph5501.bin","scph1001.bin"));
        }else return;
        SortedMap<String,String> selected=new TreeMap<>();collect(assets,"bios",names,selected,0,new int[]{0});
        if(required&&selected.isEmpty())throw new StationOnlineGame.Unavailable("A BIOS desta plataforma precisa estar incluída nesta versão do aplicativo para iniciar a partida online.");
        Files.createDirectories(system);
        if(Files.isSymbolicLink(system))throw new IOException("Invalid online firmware directory");
        Path target="neogeocd".equals(platform)?system.resolve("neocd"):system;
        Files.createDirectories(target);if(Files.isSymbolicLink(target))throw new IOException("Invalid firmware subdirectory");
        for(Map.Entry<String,String> entry:selected.entrySet()){
            cancel.check();Path destination=target.resolve(entry.getKey());
            if(Files.isSymbolicLink(destination))throw new IOException("Invalid online firmware file");
            // Copy small packaged files atomically; no ROM/download verification or extraction is added here.
            Path temporary=target.resolve(entry.getKey()+".tmp");
            if(Files.isSymbolicLink(temporary))throw new IOException("Invalid firmware temporary file");
            try(InputStream input=assets.open(entry.getValue());OutputStream output=Files.newOutputStream(temporary,StandardOpenOption.CREATE,StandardOpenOption.TRUNCATE_EXISTING,LinkOption.NOFOLLOW_LINKS)){
                byte[] buffer=new byte[32768];int n,total=0;
                while((n=input.read(buffer))!=-1){cancel.check();total+=n;if(total>16*1024*1024)throw new IOException("Firmware asset too large");output.write(buffer,0,n);}
                if(total==0)throw new IOException("Empty firmware asset");
            }catch(Exception error){Files.deleteIfExists(temporary);throw error;}
            Files.move(temporary,destination,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        }
    }
    private static void collect(StationBundledFiles.Source assets,String path,Set<String> names,SortedMap<String,String> found,int depth,int[] visited)throws IOException {
        if(depth>12||++visited[0]>8192)throw new IOException("Firmware asset tree exceeds bounds");
        String[] children=assets.list(path);if(children==null)return;
        Arrays.sort(children);
        for(String child:children){
            if(child.isEmpty()||child.equals(".")||child.equals("..")||child.indexOf('/')>=0||child.indexOf('\\')>=0)throw new IOException("Invalid firmware asset name");
            String next=path+"/"+child,base=child.toLowerCase(Locale.ROOT);
            if(names.contains(base))found.putIfAbsent(base,next);
            else collect(assets,next,names,found,depth+1,visited);
        }
    }
    private StationOnlineBios(){}
}
