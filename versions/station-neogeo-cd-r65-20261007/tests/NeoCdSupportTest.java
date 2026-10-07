
package org.emulationstation.frontend;
import java.io.*;import java.nio.file.*;import java.security.*;import java.lang.reflect.*;import java.util.*;import java.util.zip.*;
public final class NeoCdSupportTest {
 static int count;
 static void check(boolean yes){count++;if(!yes)throw new AssertionError("check "+count);}
 interface Attempt {void run()throws Exception;}
 static void rejects(Attempt work)throws Exception {try{work.run();throw new AssertionError("not rejected");}catch(IOException expected){count++;}}
 static byte[] header()throws Exception {ByteArrayOutputStream b=new ByteArrayOutputStream();DataOutputStream out=new DataOutputStream(b);out.writeBytes("MComprHD");out.writeInt(124);out.writeInt(5);out.write(new byte[108]);return b.toByteArray();}
 static String hex(byte[] digest){StringBuilder out=new StringBuilder();for(byte b:digest)out.append(String.format("%02x",b&255));return out.toString();}
 static void syntheticIdentity(String[] id,byte[] bytes)throws Exception {CRC32 crc=new CRC32();crc.update(bytes);id[2]=Long.toHexString(crc.getValue());id[3]=hex(MessageDigest.getInstance("SHA-1").digest(bytes));}
 public static void main(String[] args)throws Exception {
  Path r=Paths.get(args[0]);Path content=r.resolve("roms/.station-v2/neo-geo-cd/station_fixture/install-1/content");Files.createDirectories(content);
  File disc=content.resolve("Magical Drop 2 (World).chd").toFile();Files.write(disc.toPath(),header());
  File androidDisc = new File("/games/Neo Geo CD/Disc.chd") {
   @Override public String getAbsolutePath() { return "/games/Neo Geo CD/Disc.chd"; }
  };
  File bios=r.resolve("bios").toFile();File roms=r.resolve("roms").toFile();
  check(NeoCdSupport.isCd(disc));check(!NeoCdSupport.isCd(r.resolve("neo-geo/has-neogeocd-in-name.zip").toFile()));
  check(NeoCdSupport.isCd(r.resolve("neogeocd/disc.chd").toFile()));NeoCdSupport.validateDisc(disc);count++;
  File img=content.resolve("Wrong.img").toFile();Files.write(img.toPath(),header());rejects(()->NeoCdSupport.validateDisc(img));
  File shortDisc=content.resolve("Short.chd").toFile();Files.write(shortDisc.toPath(),Arrays.copyOf(header(),16));rejects(()->NeoCdSupport.validateDisc(shortDisc));
  File parentDisc=content.resolve("Parent.chd").toFile();byte[] parent=header();parent[123]=1;Files.write(parentDisc.toPath(),parent);rejects(()->NeoCdSupport.validateDisc(parentDisc));
  byte[] original=Files.readAllBytes(disc.toPath());rejects(()->NeoCdSupport.prepare(disc,bios,roms));check(Arrays.equals(original,Files.readAllBytes(disc.toPath())));
  rejects(()->NeoCdSupport.importBios(bios,new ByteArrayInputStream(new byte[524288])));
  rejects(()->NeoCdSupport.importBios(bios,new ByteArrayInputStream(new byte[8*1024*1024+1])));
  check(NeoCdSupport.cli(androidDisc,"official").equals("-cdrom '/games/Neo Geo CD/Disc.chd' -bios official"));
  rejects(()->NeoCdSupport.cli(androidDisc,"unexpected"));rejects(()->NeoCdSupport.cli(new File(content.toFile(),"quote'name.chd"),"official"));
  check(MameBootstrap.cliParamsFor(disc.toString()).equals("-rompath '"+disc.getParentFile().getAbsolutePath()+"'"));
  System.out.println("CLI="+MameBootstrap.cliParamsFor(disc.toString())+" "+NeoCdSupport.cli(androidDisc,"official"));
  // Private host test identities never enter Android source or compiled DEX.
  Field field=NeoCdSupport.class.getDeclaredField("IDENTITIES");field.setAccessible(true);String[][] ids=(String[][])field.get(null);
  byte[] firmware=new byte[524288];Arrays.fill(firmware,(byte)70);byte[] zoom=new byte[131072];Arrays.fill(zoom,(byte)90);
  syntheticIdentity(ids[0],firmware);syntheticIdentity(ids[3],zoom);
  NeoCdSupport.importBios(bios,new ByteArrayInputStream(firmware));check(new File(bios,"neocd.bin").isFile());rejects(()->NeoCdSupport.prepare(disc,bios,roms));
  Path old=roms.toPath().resolve(".station-v2/neo-geo/old/install-old/content");Files.createDirectories(old);
  File donor=old.resolve("neogeo.zip").toFile();try(ZipOutputStream z=new ZipOutputStream(new FileOutputStream(donor))){z.putNextEntry(new ZipEntry("other-label.lo"));z.write(zoom);z.closeEntry();}
  byte[] donorBefore=Files.readAllBytes(donor.toPath());check(NeoCdSupport.prepare(disc,bios,roms).equals("official"));
  File driver=new File(disc.getParentFile(),"neocdz.zip");try(ZipFile z=new ZipFile(driver)){check(z.size()==2);check(Arrays.equals(firmware,z.getInputStream(z.getEntry("neocd.bin")).readAllBytes()));check(z.getEntry("000-lo.lo")!=null);}
  byte[] before=Files.readAllBytes(driver.toPath());check(NeoCdSupport.prepare(disc,bios,roms).equals("official"));check(Arrays.equals(before,Files.readAllBytes(driver.toPath())));check(Arrays.equals(donorBefore,Files.readAllBytes(donor.toPath())));check(Arrays.equals(original,Files.readAllBytes(disc.toPath())));

  for (String collection : new String[]{"Todos os jogos", "# THE KING OF FIGHTERS #", "Metal Slug", "Samurai Shodown", "Fatal Fury", "Hacks"}) {
   check(!NeoCdSupport.isCd(new File("roms/.station-v2/neo-geo/"+collection+"/game.zip")));
   check(NeoCdSupport.isCd(new File("roms/.station-v2/neo-geo-cd/"+collection+"/game.chd")));
  }
  System.out.println("PASS "+count+" CD dependency, import, exact identity, header, CLI and preservation checks");
 }
}
