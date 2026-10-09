package org.emulationstation.frontend.netplay;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import org.emulationstation.frontend.station.StationApi;
import org.emulationstation.frontend.station.StationBundledFiles;

final class StationOnlineBiosTest {
    static int checks;
    static void check(boolean value,String label){checks++;if(!value)throw new AssertionError(label);}
    interface Action{void run()throws Exception;}
    static void rejects(Action action)throws Exception{checks++;try{action.run();}catch(IOException expected){return;}throw new AssertionError("Unsafe firmware accepted");}
    static final class Assets implements StationBundledFiles.Source {
        final SortedMap<String,byte[]> files=new TreeMap<>();
        Assets put(String name,int value){files.put(name,new byte[]{(byte)value});return this;}
        public String[] list(String path){TreeSet<String> names=new TreeSet<>();for(String name:files.keySet())if(name.startsWith(path+"/")){String rest=name.substring(path.length()+1);names.add(rest.split("/")[0]);}return names.toArray(new String[0]);}
        public InputStream open(String path)throws IOException{byte[] value=files.get(path);if(value==null)throw new FileNotFoundException();return new ByteArrayInputStream(value);}
    }
    static void prepare(Assets a,String platform,Path dir)throws Exception{StationOnlineBios.prepare(a,platform,dir,new StationApi.Cancellation());}
    public static void main(String[] args)throws Exception {
        Path root=Paths.get(args[0]);Files.createDirectory(root);
        Assets assets=new Assets().put("bios/a/neogeo.zip",3).put("bios/b/neogeo.zip",7).put("bios/psx/SCPH5501.BIN",9).put("bios/neocd/neocd.bin",11).put("bios/arcade/pgm.zip",13).put("bios/arcade/skns.zip",14).put("bios/unrelated/savedata.bin",15);
        Path neo=root.resolve("neo");prepare(assets,"neogeo",neo);
        check(Files.readAllBytes(neo.resolve("neogeo.zip"))[0]==3,"deterministic packaged BIOS selection");
        check(!Files.exists(neo.resolve("savedata.bin")),"offline saves never imported");
        check(!Files.exists(neo.resolve("pgm.zip")),"unrelated platform firmware omitted");
        Files.write(neo.resolve("neogeo.zip"),new byte[]{22});prepare(assets,"neogeo",neo);
        check(Files.readAllBytes(neo.resolve("neogeo.zip"))[0]==3,"local firmware cannot replace packaged online firmware");
        rejects(()->prepare(new Assets(),"neogeo",root.resolve("missing")));
        Path cd=root.resolve("cd");prepare(assets,"neogeocd",cd);
        check(Files.readAllBytes(cd.resolve("neocd/neocd.bin"))[0]==11,"NeoCD uses actual core subdirectory");
        check(!Files.exists(cd.resolve("neocd.bin")),"NeoCD root is not mistaken for its BIOS directory");
        prepare(new Assets(),"neogeocd",root.resolve("hle"));check(Files.isDirectory(root.resolve("hle/neocd")),"pinned NeoCD HLE fallback allowed");
        Path psx=root.resolve("psx");prepare(assets,"psx",psx);check(Files.readAllBytes(psx.resolve("scph5501.bin"))[0]==9,"case-insensitive known firmware basename");
        prepare(new Assets(),"psx",root.resolve("psx-hle"));check(Files.isDirectory(root.resolve("psx-hle")),"PCSX HLE fallback allowed");
        Path arcade=root.resolve("arcade");prepare(assets,"fbneo",arcade);
        for(String name:new String[]{"neogeo.zip","pgm.zip","skns.zip"})check(Files.isRegularFile(arcade.resolve(name)),"arcade firmware "+name);
        prepare(assets,"n64",root.resolve("n64"));check(!Files.exists(root.resolve("n64")),"N64 does not import firmware");
        Assets empty=new Assets();empty.files.put("bios/neogeo.zip",new byte[0]);Path emptyDir=root.resolve("empty");rejects(()->prepare(empty,"neogeo",emptyDir));check(!Files.exists(emptyDir.resolve("neogeo.zip.tmp")),"failed copy removes temporary file");
        Path cancelled=root.resolve("cancelled");StationApi.Cancellation cancellation=new StationApi.Cancellation();cancellation.cancel();
        rejects(()->StationOnlineBios.prepare(assets,"neogeo",cancelled,cancellation));check(!Files.exists(cancelled.resolve("neogeo.zip")),"cancellation precedes firmware write");
        System.out.println("{\"passed\":true,\"checks\":"+checks+",\"physicalGameplayVerified\":false}");
    }
}
