import os
from pathlib import Path
import subprocess,json,re
W=Path(os.environ['STATION_EMULATORS_WORK']);S=W/'mame/java/org/emulationstation/frontend';T=W/'mame/tests';T.mkdir(exist_ok=True)
def method(s,start):
 a=s.index(start);i=s.index('{',a)+1;depth=1
 while depth:
  if s[i]=='{':depth+=1
  elif s[i]=='}':depth-=1
  i+=1
 return s[a:i]
s=(S/'MameBootstrap.java').read_text('utf8')
src='''import java.io.*;import java.util.*;import java.nio.file.*;
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
'''
for name in ['static File romDirFor(', 'public static File files(', 'public static void seed(Context c,String path)']:
 src+=method(s,name).replace('android.util.Log.i','Log.i')+'\n'
src+='''public static void main(String[] args)throws Exception {
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
'''
(T/'MamePathsTest.java').write_text(src,'utf8')
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
for args in [[J/'javac.exe','-encoding','UTF-8','-d',T,T/'MamePathsTest.java'],[J/'java.exe','-cp',T,'MamePathsTest',T/'fixture']]:
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr
 print(p.stdout);(T/'result.log').write_text(p.stdout+p.stderr,'utf8')
prefs=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\mame-current\donor-decoded\smali\com\seleuco\mame4droid\helpers\PrefsHelper.smali').read_text('utf8')
actual=prefs.split('.method public getROMsDIR()')[1].split('.end method')[0]
key=re.search('const-string v0, "(.*?)"',actual)[1];assert 'edit.putString("'+key+'",roms.getAbsolutePath());' in s
entry=(S/'MameEntryActivity.java').read_text('utf8');assert 'if(!settings&&(rom==null||!rom.isFile()||!rom.canRead()))' in entry
(T/'result.json').write_text(json.dumps({'passed':True,'host':p.stdout.strip(),'keyVerifiedAgainstPackagedEngine':key,'missingGameDoesNotSilentlyOpenLibrary':True,'devicePending':True},indent=2),'utf8')
