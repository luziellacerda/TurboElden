package org.emulationstation.frontend;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;

/** Reads the user's existing APK. No firmware bytes are embedded in this test. */
public final class NeoCdBundledTest {
 static int checks;
 static void check(boolean value){checks++;if(!value)throw new AssertionError("check "+checks);}
 interface Attempt{void run()throws Exception;}
 static void rejects(Attempt call)throws Exception{try{call.run();throw new AssertionError("not rejected");}catch(IOException expected){checks++;}}
 static File disc(Path root,String name)throws Exception{
  Path path=root.resolve(name+"/neo-geo-cd/game.chd");Files.createDirectories(path.getParent());
  try(DataOutputStream out=new DataOutputStream(Files.newOutputStream(path))){out.writeBytes("MComprHD");out.writeInt(124);out.writeInt(5);out.write(new byte[108]);}return path.toFile();
 }
 static InputStream asset(ZipFile apk,String path)throws IOException{
  ZipEntry item=apk.getEntry("assets/"+path);if(item==null)throw new FileNotFoundException(path);return apk.getInputStream(item);
 }
 public static void main(String[] args)throws Exception{
  Path root=Paths.get(args[1]);Files.createDirectories(root);
  try(ZipFile apk=new ZipFile(args[0])){
   File roms=root.resolve("roms").toFile();File game=disc(root,"fresh");File home=root.resolve("fresh-home").toFile();
   byte[] gameBefore=Files.readAllBytes(game.toPath());List<String> reads=new ArrayList<>();
   NeoCdSupport.BundledAssets bundled=p->{reads.add(p);return asset(apk,p);};
   check(NeoCdSupport.prepare(game,home,roms,bundled).equals("official"));
   check(reads.equals(Arrays.asList("bios/neocd/neocd.bin","bios/neocd/000-lo.lo")));
   check(new File(home,"neocd.bin").isFile());check(new File(home,"000-lo.lo").isFile());
   File driver=new File(game.getParentFile(),"neocdz.zip");byte[] driverBefore=Files.readAllBytes(driver.toPath());
   try(ZipFile z=new ZipFile(driver)){
    check(z.size()==2);check(z.getEntry("neocd.bin")!=null);check(z.getEntry("000-lo.lo")!=null);
    try(InputStream original=asset(apk,"bios/neocd/neocd.bin")){check(Arrays.equals(original.readAllBytes(),z.getInputStream(z.getEntry("neocd.bin")).readAllBytes()));}
   }
   long timestamp=driver.lastModified();reads.clear();
   check(NeoCdSupport.prepare(game,home,roms,bundled).equals("official"));
   check(reads.isEmpty());check(driver.lastModified()==timestamp);check(Arrays.equals(driverBefore,Files.readAllBytes(driver.toPath())));
   check(Arrays.equals(gameBefore,Files.readAllBytes(game.toPath())));
   File custom=disc(root,"custom");File customHome=root.resolve("custom-home").toFile();
   try(InputStream input=asset(apk,"bios/neocd/uni-bioscd.rom")){NeoCdSupport.importBios(customHome,input);}
   byte[] customBefore=Files.readAllBytes(new File(customHome,"uni-bioscd33.rom").toPath());reads.clear();
   check(NeoCdSupport.prepare(custom,customHome,roms,bundled).equals("unibios33"));
   check(reads.equals(Arrays.asList("bios/neocd/000-lo.lo")));check(!new File(customHome,"neocd.bin").exists());
   check(Arrays.equals(customBefore,Files.readAllBytes(new File(customHome,"uni-bioscd33.rom").toPath())));
   File fallback=disc(root,"fallback");File fallbackHome=root.resolve("fallback-home").toFile();
   check(NeoCdSupport.prepare(fallback,fallbackHome,roms,p->{if(p.endsWith("neocd.bin"))throw new FileNotFoundException(p);return asset(apk,p);}).equals("unibios33"));
   check(new File(fallbackHome,"uni-bioscd33.rom").isFile());
   File broken=disc(root,"broken");File brokenHome=root.resolve("broken-home").toFile();
   rejects(()->NeoCdSupport.prepare(broken,brokenHome,roms,p->new ByteArrayInputStream(new byte[524288])));
   check(!new File(broken.getParentFile(),"neocdz.zip").exists());
   rejects(()->NeoCdSupport.prepare(broken,brokenHome,roms,p->new ByteArrayInputStream(new byte[524289])));
   rejects(()->NeoCdSupport.prepare(broken,brokenHome,roms,p->null));
   rejects(()->NeoCdSupport.prepare(broken,brokenHome,roms,p->{throw new FileNotFoundException(p);}));
   // A complete existing setup must not need to access bundled assets again.
   check(NeoCdSupport.prepare(game,home,roms,p->{throw new IOException("unexpected asset read");}).equals("official"));
   check(Arrays.equals(driverBefore,Files.readAllBytes(driver.toPath())));
   File badDisc=disc(root,"bad-disc");Files.write(badDisc.toPath(),new byte[124]);reads.clear();
   rejects(()->NeoCdSupport.prepare(badDisc,root.resolve("bad-home").toFile(),roms,bundled));check(reads.isEmpty());
   check(!Files.exists(root.resolve("bad-home")));
  }
  System.out.println("PASS "+checks+" bundled BIOS cold-start, preservation, fallback and failure checks");
 }
}
