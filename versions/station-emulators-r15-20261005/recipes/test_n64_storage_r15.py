import os
from pathlib import Path
import subprocess,json
W=Path(os.environ['STATION_N64_WORK']);T=W/'tests';J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
s=Path('N64Bootstrap.java').read_text('utf8')
def method(name):
 a=s.index(name);i=s.index('{',a)+1;depth=1
 while depth:
  if s[i]=='{':depth+=1
  elif s[i]=='}':depth-=1
  i+=1
 return s[a:i]
src='''import java.io.*;import java.nio.file.*;import java.util.*;
public class N64StorageTest{
 static class SharedPreferences{Map<String,String> map=new HashMap<>();boolean contains(String k){return map.containsKey(k);} Editor edit(){return new Editor();}class Editor{Editor putString(String k,String v){map.put(k,v);return this;}boolean commit(){return true;}}}
 static class Context{File root;boolean external=true;Map<String,SharedPreferences> prefs=new HashMap<>();Context(File r){root=r;}File getFilesDir(){return new File(root,"files");}File getCacheDir(){return new File(root,"cache");}File getExternalFilesDir(String type){return external?new File(root,"external"):null;}String getPackageName(){return "org.turboramastation.frontend";}SharedPreferences getSharedPreferences(String n,int mode){return prefs.computeIfAbsent(n,k->new SharedPreferences());}}
 static int checks;static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
'''
for name in ('public static SharedPreferences sharedPrefs(','public static SharedPreferences preferences(','private static File directory(','public static File files(','public static File cache(','public static File userFiles(','public static void seed('):src+=method(name)+'\n'
src+='''public static void main(String[] a)throws Exception{
 Context c=new Context(new File(a[0]));seed(c);check(files(c).isDirectory());check(cache(c).isDirectory());check(preferences(c).map.get("gameDataStorageType").equals("internal"));
 check(c.prefs.containsKey("n64.org.turboramastation.frontend_preferences"));check(!c.prefs.containsKey("org.turboramastation.frontend_preferences"));
 check(userFiles(c,null).getCanonicalPath().equals(new File(c.root,"external/n64").getCanonicalPath()));check(userFiles(c,"saves").isDirectory());
 c.external=false;check(userFiles(c,null).getCanonicalPath().equals(new File(c.root,"files/n64").getCanonicalPath()));
 preferences(c).map.put("gameDataStorageType","external");preferences(c).map.put("gameDataStoragePath","content://user-chosen-folder");
 for(int i=0;i<20;i++){seed(c);check(preferences(c).map.get("gameDataStorageType").equals("external"));check(preferences(c).map.get("gameDataStoragePath").equals("content://user-chosen-folder"));}
 File conflict=new File(c.root,"not-a-directory");Files.write(conflict.toPath(),new byte[]{1});boolean failed=false;try{directory(conflict);}catch(IllegalStateException e){failed=true;}check(failed);
 System.out.println("PASS "+checks+" N64 first-launch storage and persistent configuration checks");}}
'''
(T/'N64StorageTest.java').write_text(src,'utf8')
for args in ([J/'javac.exe','-encoding','UTF-8','-d',T,T/'N64StorageTest.java'],[J/'java.exe','-cp',T,'N64StorageTest',T/'storage-fixture']):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr
 if p.stdout:print(p.stdout.strip());(T/'storage.log').write_text(p.stdout,'utf8')
(T/'storage.json').write_text(json.dumps({'passed':True,'output':p.stdout.strip(),'usesExactBootstrapMethods':True,'deviceVerified':False},indent=2),'utf8')
