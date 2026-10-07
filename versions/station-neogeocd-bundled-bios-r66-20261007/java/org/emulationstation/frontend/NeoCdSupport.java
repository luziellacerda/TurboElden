package org.emulationstation.frontend;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.zip.*;

/** CDZ dependencies belong to installed content; no game or save is rewritten. */
public final class NeoCdSupport {
 /** Read-only access to resources already included in the application. */
 public interface BundledAssets { InputStream open(String path)throws IOException; }
 private static final String[][] IDENTITIES={
  {"neocd.bin","524288","df9de490","7bb26d1e5d1e930515219cb18bcde5b7b23e2eda","official"},
  {"uni-bioscd33.rom","524288","ff3abc59","5142f205912869b673a71480c5828b1eaed782a8","unibios33"},
  {"uni-bioscd32.rom","524288","0ffb3127","5158b728e62b391fb69493743dcf7abbc62abc82","unibios32"},
  {"000-lo.lo","131072","5a86cff2","5992277debadeb64d1c1c64b0a92d9293eaf7e4a",""}
 };
 public static boolean isCd(File file){
  if(file==null)return false;
  for(File p=file.getParentFile();p!=null;p=p.getParentFile()){
   String n=p.getName().toLowerCase(Locale.US);
   if(n.equals("neo-geo-cd")||n.equals("neogeocd"))return true;
  }
  return false;
 }
 public static void validateDisc(File disc)throws IOException{
  if(!disc.getName().toLowerCase(Locale.US).endsWith(".chd"))throw new IOException("Este disco precisa da extensão .chd. Atualize a instalação pelo catálogo.");
  try(DataInputStream in=new DataInputStream(new FileInputStream(disc))){
   byte[] magic=new byte[8];in.readFully(magic);
   if(!Arrays.equals(magic,new byte[]{'M','C','o','m','p','r','H','D'})||in.readInt()!=124||in.readInt()!=5)throw new IOException("O disco instalado não é um CHD válido. Baixe novamente pelo catálogo.");
   byte[] remaining=new byte[108];in.readFully(remaining);for(int i=88;i<108;i++)if(remaining[i]!=0)throw new IOException("O disco depende de outro CHD. Atualize pelo catálogo.");
  }
 }
 private static String identify(byte[] data)throws IOException{
  CRC32 crc=new CRC32();crc.update(data);
  String sha;
  try{byte[] digest=MessageDigest.getInstance("SHA-1").digest(data);StringBuilder s=new StringBuilder();for(byte b:digest)s.append(String.format(Locale.US,"%02x",b&255));sha=s.toString();}
  catch(NoSuchAlgorithmException e){throw new IOException(e);}
  for(String[] id:IDENTITIES)if(data.length==Integer.parseInt(id[1])&&crc.getValue()==Long.parseLong(id[2],16)&&sha.equals(id[3]))return id[0];
  return null;
 }
 private static byte[] bounded(InputStream stream,int maximum)throws IOException{
  ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[16384];int n;
  while((n=stream.read(buffer))!=-1){if(n>maximum-out.size())throw new IOException("O arquivo de BIOS é maior que o esperado.");out.write(buffer,0,n);}return out.toByteArray();
 }
 private static Map<String,byte[]> readSource(File source)throws IOException{
  Map<String,byte[]> found=new HashMap<>();
  if(!source.isFile()||!source.canRead())return found;
  if(source.length()>8*1024*1024)throw new IOException("Escolha uma BIOS, não um arquivo de jogo.");
  byte[] prefix=new byte[4];try(FileInputStream in=new FileInputStream(source)){in.read(prefix);}
  if(prefix[0]=='P'&&prefix[1]=='K'){
   try(ZipFile zip=new ZipFile(source)){
    Enumeration<? extends ZipEntry> entries=zip.entries();int count=0;long expanded=0;
    while(entries.hasMoreElements()){
     ZipEntry entry=entries.nextElement();if(++count>256||entry.getSize()<0||(expanded+=entry.getSize())>16*1024*1024)throw new IOException("Pacote de BIOS inválido.");
     if(entry.isDirectory()||(entry.getSize()!=131072&&entry.getSize()!=524288))continue;
     try(InputStream in=zip.getInputStream(entry)){byte[] data=bounded(in,524288);String name=identify(data);if(name!=null)found.put(name,data);}
    }
   }
  }else if(source.length()==131072||source.length()==524288){try(InputStream in=new FileInputStream(source)){byte[] data=bounded(in,524288);String name=identify(data);if(name!=null)found.put(name,data);}}
  return found;
 }
 private static Map<String,byte[]> saved(File home)throws IOException{
  Map<String,byte[]> found=new HashMap<>();
  for(String[] id:IDENTITIES)found.putAll(readSource(new File(home,id[0])));
  return found;
 }
 private static String firmware(Map<String,byte[]> found){for(String[] id:IDENTITIES)if(!id[4].isEmpty()&&found.containsKey(id[0]))return id[0];return null;}
 private static void writeAtomic(File destination,byte[] data)throws IOException{
  File parent=destination.getParentFile();if(!parent.isDirectory()&&!parent.mkdirs())throw new IOException("Não foi possível preparar a pasta da BIOS.");
  File temp=File.createTempFile(".bios-",".tmp",parent);
  try{try(FileOutputStream out=new FileOutputStream(temp)){out.write(data);out.getFD().sync();}Files.move(temp.toPath(),destination.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
  finally{temp.delete();}
 }
 public static void importBios(File home,InputStream input)throws IOException{
  if(!home.isDirectory()&&!home.mkdirs())throw new IOException("Não foi possível preparar a pasta da BIOS.");
  File temp=File.createTempFile(".import-",".tmp",home);
  try{
   writeAtomic(temp,bounded(input,8*1024*1024));Map<String,byte[]> found=readSource(temp);
   if(found.isEmpty())throw new IOException("O arquivo não contém uma BIOS compatível de Neo Geo CD. A BIOS do Neo Geo comum é diferente.");
   for(Map.Entry<String,byte[]> member:found.entrySet())writeAtomic(new File(home,member.getKey()),member.getValue());
  }finally{temp.delete();}
 }
 private static void findZoom(File root,Map<String,byte[]> found,int[] remaining)throws IOException{
  if(found.containsKey("000-lo.lo")||--remaining[0]<0||!root.exists())return;
  if(!root.getCanonicalFile().equals(root.getAbsoluteFile()))return; // never follow links
  if(root.isFile()){
   if(root.getName().equalsIgnoreCase("neogeo.zip")){try{Map<String,byte[]> donor=readSource(root);if(donor.containsKey("000-lo.lo"))found.put("000-lo.lo",donor.get("000-lo.lo"));}catch(IOException ignored){}}
   return;
  }
  File[] files=root.listFiles();if(files!=null)for(File file:files){findZoom(file,found,remaining);if(found.containsKey("000-lo.lo"))break;}
 }
 private static void useBundledBios(File home,Map<String,byte[]> members,BundledAssets assets)throws IOException{
  if(assets==null)return;
  String[] paths={"bios/neocd/neocd.bin","bios/neocd/uni-bioscd.rom","bios/neocd/000-lo.lo"};
  for(String path:paths){
   boolean zoom=path.endsWith("/000-lo.lo");
   if(zoom?members.containsKey("000-lo.lo"):firmware(members)!=null)continue;
   byte[] data;
   try(InputStream input=assets.open(path)){
    if(input==null)throw new IOException("Não foi possível ler a BIOS incluída no aplicativo.");
    data=bounded(input,524288);
   }catch(FileNotFoundException absent){continue;}
   String name=identify(data);
   if(name==null||zoom!=name.equals("000-lo.lo"))throw new IOException("A BIOS incluída no aplicativo está inválida. Reinstale a atualização mantendo seus dados.");
   writeAtomic(new File(home,name),data);members.put(name,data);
  }
 }
 public static String prepare(File disc,File home,File romsRoot)throws IOException{
  return prepare(disc,home,romsRoot,null);
 }
 public static String prepare(File disc,File home,File romsRoot,BundledAssets assets)throws IOException{
  validateDisc(disc);File driver=new File(disc.getParentFile(),"neocdz.zip");Map<String,byte[]> members=saved(home);
  Map<String,byte[]> bundled;
  try{bundled=readSource(driver);}catch(IOException invalid){bundled=new HashMap<>();}
  members.putAll(bundled);useBundledBios(home,members,assets);String selected=firmware(members);
  if(selected==null)throw new IOException("Falta a BIOS do Neo Geo CD. O jogo, capa e sinopse já estão disponíveis. Use IMPORTAR BIOS para escolher seu arquivo neocd.zip, neocdz.zip, .bin ou .rom.");
  if(!members.containsKey("000-lo.lo")){
   int[] budget={6000};findZoom(new File(romsRoot,"neo-geo"),members,budget);findZoom(new File(romsRoot,"neogeo"),members,budget);findZoom(new File(romsRoot,".station-v2/neo-geo"),members,budget);
  }
  if(!members.containsKey("000-lo.lo"))throw new IOException("A BIOS CD foi reconhecida, mas falta o arquivo auxiliar 000-lo.lo. Importe o pacote completo neocdz.zip ou a BIOS Neo Geo que contém esse arquivo.");
  if(!bundled.containsKey(selected)||!bundled.containsKey("000-lo.lo")){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();
   try(ZipOutputStream zip=new ZipOutputStream(bytes)){
    for(String name:new String[]{selected,"000-lo.lo"}){byte[] data=members.get(name);CRC32 crc=new CRC32();crc.update(data);ZipEntry entry=new ZipEntry(name);entry.setTime(315532800000L);entry.setMethod(ZipEntry.STORED);entry.setSize(data.length);entry.setCompressedSize(data.length);entry.setCrc(crc.getValue());zip.putNextEntry(entry);zip.write(data);zip.closeEntry();}
   }
   writeAtomic(driver,bytes.toByteArray());
  }
  for(String[] id:IDENTITIES)if(id[0].equals(selected))return id[4];
  throw new IOException("BIOS CD não reconhecida.");
 }
 public static String cli(File disc,String bios)throws IOException{
  String path=disc.getAbsolutePath();
  if(path.indexOf((char)39)>=0||path.indexOf('\\')>=0||path.indexOf('\n')>=0||path.indexOf('\r')>=0)throw new IOException("O nome do disco contém caracteres incompatíveis. Corrija o nome no catálogo.");
  if(!bios.equals("official")&&!bios.equals("unibios33")&&!bios.equals("unibios32"))throw new IOException("BIOS CD inválida.");
  return "-cdrom '"+path+"' -bios "+bios;
 }
 private NeoCdSupport(){}
}
