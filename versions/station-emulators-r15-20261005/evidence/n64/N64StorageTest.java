import java.io.*;import java.nio.file.*;import java.util.*;
public class N64StorageTest{
 static class SharedPreferences{Map<String,String> map=new HashMap<>();boolean contains(String k){return map.containsKey(k);} Editor edit(){return new Editor();}class Editor{Editor putString(String k,String v){map.put(k,v);return this;}boolean commit(){return true;}}}
 static class Context{File root;boolean external=true;Map<String,SharedPreferences> prefs=new HashMap<>();Context(File r){root=r;}File getFilesDir(){return new File(root,"files");}File getCacheDir(){return new File(root,"cache");}File getExternalFilesDir(String type){return external?new File(root,"external"):null;}String getPackageName(){return "org.turboramastation.frontend";}SharedPreferences getSharedPreferences(String n,int mode){return prefs.computeIfAbsent(n,k->new SharedPreferences());}}
 static int checks;static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
public static SharedPreferences sharedPrefs(Context c,String name,int mode){return c.getSharedPreferences("n64."+name,mode);}
public static SharedPreferences preferences(Context c){return sharedPrefs(c,c.getPackageName()+"_preferences",0);}
private static File directory(File f){if(!f.isDirectory()&&!f.mkdirs())throw new IllegalStateException("Não foi possível preparar a pasta do Nintendo 64.");return f;}
public static File files(Context c){return directory(new File(c.getFilesDir(),"n64"));}
public static File cache(Context c){return directory(new File(c.getCacheDir(),"n64"));}
public static File userFiles(Context c,String type){File root=c.getExternalFilesDir(null);if(root==null)root=c.getFilesDir();return directory(new File(root,"n64"+(type==null?"":"/"+type)));}
public static void seed(Context c){
  files(c);cache(c);SharedPreferences p=preferences(c);
  if(!p.contains("gameDataStorageType"))p.edit().putString("gameDataStorageType","internal").commit();
 }
public static void main(String[] a)throws Exception{
 Context c=new Context(new File(a[0]));seed(c);check(files(c).isDirectory());check(cache(c).isDirectory());check(preferences(c).map.get("gameDataStorageType").equals("internal"));
 check(c.prefs.containsKey("n64.org.turboramastation.frontend_preferences"));check(!c.prefs.containsKey("org.turboramastation.frontend_preferences"));
 check(userFiles(c,null).getCanonicalPath().equals(new File(c.root,"external/n64").getCanonicalPath()));check(userFiles(c,"saves").isDirectory());
 c.external=false;check(userFiles(c,null).getCanonicalPath().equals(new File(c.root,"files/n64").getCanonicalPath()));
 preferences(c).map.put("gameDataStorageType","external");preferences(c).map.put("gameDataStoragePath","content://user-chosen-folder");
 for(int i=0;i<20;i++){seed(c);check(preferences(c).map.get("gameDataStorageType").equals("external"));check(preferences(c).map.get("gameDataStoragePath").equals("content://user-chosen-folder"));}
 File conflict=new File(c.root,"not-a-directory");Files.write(conflict.toPath(),new byte[]{1});boolean failed=false;try{directory(conflict);}catch(IllegalStateException e){failed=true;}check(failed);
 System.out.println("PASS "+checks+" N64 first-launch storage and persistent configuration checks");}}
