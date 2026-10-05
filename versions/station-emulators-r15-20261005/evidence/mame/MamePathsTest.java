import java.io.*;import java.util.*;import java.nio.file.*;
public class MamePathsTest {
static File ROMS_ROOT;
static class Context {File dir;Context(File p){dir=p;}File getFilesDir(){return dir;}}
static class SharedPreferences {
 Map<String,String> data=new HashMap<>();String getString(String k,String d){return data.getOrDefault(k,d);}
 Editor edit(){return new Editor();}
 class Editor {Editor putString(String k,String v){if(v==null)data.remove(k);else data.put(k,v);return this;}Editor remove(String k){data.remove(k);return this;}boolean commit(){return true;}}
}
static class PreferenceManager {static SharedPreferences prefs=new SharedPreferences();static SharedPreferences getDefaultSharedPreferences(Context c){return prefs;}}
static class Log {static void i(String t,String v){}}
static int checks;static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
static File romDirFor(String path){
  // Station installs each artifact in its own generation/content directory.
  // MAME reads only the filename from ACTION_VIEW; its ROM search path must
  // therefore be the actual parent, where the signed package also puts BIOS.
  if(path!=null){File selected=new File(path);if(selected.isFile())return selected.getAbsoluteFile().getParentFile();}
  String p=path==null?"":path.toLowerCase(Locale.US);
  if(p.contains("neogeocd")||p.contains("neo-geo-cd")||p.contains("neocd")||p.contains("neocdz")){
   File hyphen=new File(ROMS_ROOT,"neo-geo-cd");
   File compact=new File(ROMS_ROOT,"neogeocd");
   File dir=hyphen.isDirectory()?hyphen:compact;
   dir.mkdirs();return dir;
  }
  if(p.contains("neogeo")||p.contains("neo-geo")||p.contains("neo geo")){
   File hyphen=new File(ROMS_ROOT,"neo-geo");
   File compact=new File(ROMS_ROOT,"neogeo");
   File dir=hyphen.isDirectory()?hyphen:compact;
   dir.mkdirs();return dir;
  }
  if(p.contains("cps3")){File dir=new File(ROMS_ROOT,"cps3");dir.mkdirs();return dir;}
  if(p.contains("cps2")){File dir=new File(ROMS_ROOT,"cps2");dir.mkdirs();return dir;}
  if(p.contains("cps1")){File dir=new File(ROMS_ROOT,"cps1");dir.mkdirs();return dir;}
  if(p.contains("model2")||p.contains("model 2")){File dir=new File(ROMS_ROOT,"model2");dir.mkdirs();return dir;}
  File dir=new File(ROMS_ROOT,"mame");dir.mkdirs();return dir;
 }
public static File files(Context c){File f=new File(c.getFilesDir(),"mame");f.mkdirs();return f;}
public static void seed(Context c,String path){
  File dir=files(c);
  File roms=romDirFor(path);
  SharedPreferences pref=PreferenceManager.getDefaultSharedPreferences(c);
  SharedPreferences.Editor edit=pref.edit();
  String install=dir.getAbsolutePath();
  if(!install.endsWith("/"))install=install+"/";
  String current=pref.getString("PREF_INSTALLATION_DIR",null);
  File existing=current==null||current.isEmpty()?null:new File(current);
  if(existing==null||!existing.isDirectory()||!existing.canWrite())edit.putString("PREF_INSTALLATION_DIR",install);
  if(pref.getString("PREF_OLD_INSTALLATION_DIR",null)==null)edit.putString("PREF_OLD_INSTALLATION_DIR",install);
  // Exact key read by MAME4droid 1.41.2 PrefsHelper.getROMsDIR().
  edit.putString("PREF_ROMsDIR_2",roms.getAbsolutePath());
  edit.remove("PREF_ROMsDIR");
  edit.putString("PREF_SAF_URI",null);
  if(!dir.isDirectory()||!dir.canWrite()||!roms.isDirectory()||!roms.canRead())throw new IllegalStateException("Não foi possível preparar as pastas do emulador.");
  if(!edit.commit())throw new IllegalStateException("Não foi possível salvar a configuração do emulador.");
  Log.i("TurboMame","Configured ROM directory="+roms.getAbsolutePath()+"; launch="+(path==null?"settings":new File(path).getName()));
 }
public static void main(String[] args)throws Exception {
 Path root=Paths.get(args[0]);Files.createDirectories(root);ROMS_ROOT=root.resolve("roms").toFile();ROMS_ROOT.mkdirs();Context c=new Context(root.resolve("private").toFile());c.dir.mkdirs();
 for(String platform:new String[]{"neo-geo","mame","cps1","cps2","cps3","neo-geo-cd"}){
  Path content=root.resolve("roms/.station-v2/"+platform+"/station_fixture/install-123/content");Files.createDirectories(content);
  File game=content.resolve("game.zip").toFile();Files.write(game.toPath(),new byte[]{1,2,3});Files.write(content.resolve("neogeo.zip"),new byte[]{4,5,6});
  check(romDirFor(game.toString()).equals(content.toFile().getAbsoluteFile()));seed(c,game.toString());
  check(PreferenceManager.prefs.data.get("PREF_ROMsDIR_2").equals(content.toFile().getAbsolutePath()));
  check(!PreferenceManager.prefs.data.containsKey("PREF_ROMsDIR"));check(!PreferenceManager.prefs.data.containsKey("PREF_SAF_URI"));
  check(new File(PreferenceManager.prefs.data.get("PREF_INSTALLATION_DIR")).isDirectory());
 }
 String saved=PreferenceManager.prefs.getString("PREF_INSTALLATION_DIR",null);seed(c,ROMS_ROOT+"/neo-geo");check(saved.equals(PreferenceManager.prefs.getString("PREF_INSTALLATION_DIR",null)));
 File custom=root.resolve("custom-saves").toFile();custom.mkdirs();PreferenceManager.prefs.data.put("PREF_INSTALLATION_DIR",custom.toString());seed(c,ROMS_ROOT+"/neo-geo");check(PreferenceManager.prefs.getString("PREF_INSTALLATION_DIR",null).equals(custom.toString()));
 PreferenceManager.prefs.data.put("PREF_INSTALLATION_DIR",root.resolve("missing").toString());seed(c,null);check(PreferenceManager.prefs.getString("PREF_INSTALLATION_DIR",null).equals(saved));
 for(int i=0;i<20;i++){seed(c,ROMS_ROOT+"/neo-geo");check(PreferenceManager.prefs.getString("PREF_INSTALLATION_DIR",null).equals(saved));}
 System.out.println("PASS "+checks+" exact bootstrap checks: Station parent paths, actual engine preference, first run, repeated run, retained saves and invalid prior path");
}}
