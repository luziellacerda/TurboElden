package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.os.*;
import java.io.*;
import java.util.*;
public final class XboxBootstrap {
 private static final Set<Activity> screens=Collections.newSetFromMap(new WeakHashMap<Activity,Boolean>());
 private static String process(){if(Build.VERSION.SDK_INT>=28)return Application.getProcessName();try(FileInputStream f=new FileInputStream("/proc/self/cmdline")){byte[]b=new byte[256];int n=f.read(b),i=0;while(i<n&&b[i]!=0)i++;return new String(b,0,i,"UTF-8");}catch(Exception e){return "";}}
 public static boolean initProcess(Application app){
  String p=process();if(!p.endsWith(":xbox")&&!p.endsWith(":xboxemu"))return false;
  app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   public void onActivityCreated(Activity a,Bundle b){screens.add(a);}
   public void onActivityDestroyed(Activity a){screens.remove(a);}
   public void onActivityStarted(Activity a){} public void onActivityStopped(Activity a){}
   public void onActivityResumed(Activity a){} public void onActivityPaused(Activity a){}
   public void onActivitySaveInstanceState(Activity a,Bundle b){}
  });return true;
 }
 public static File files(Context c){File f=new File(c.getFilesDir(),"xbox");f.mkdirs();return f;}
 public static File cache(Context c){File f=new File(c.getCacheDir(),"xbox");f.mkdirs();return f;}
 public static File userFiles(Context c,String type){File root=c.getExternalFilesDir(null);if(root==null)root=c.getFilesDir();File f=new File(root,"xbox"+(type==null?"":"/"+type));f.mkdirs();return f;}
 public static boolean launch(Activity a,String path,boolean settings){
  if(Build.VERSION.SDK_INT<29){a.runOnUiThread(()->new AlertDialog.Builder(a).setTitle("Xbox clássico").setMessage("O X1 BOX 1.2.8 requer Android 10 ou superior.").setPositiveButton("VOLTAR",null).show());return false;}
  try{Intent i=new Intent(a,XboxEntryActivity.class);i.putExtra("game",path==null?"":path);i.putExtra("settings",settings);a.startActivity(i);return true;}catch(Exception e){android.util.Log.e("TurboXbox","launch",e);return false;}
 }
 public static void seed(Context c)throws IOException{
  File dir=files(c);SharedPreferences pref=c.getSharedPreferences("x1box_prefs",0);
  SharedPreferences.Editor edit=pref.edit();String[][] setup={{"mcpx_1.0.bin","mcpxPath"},{"Complex_4627.bin","flashPath"},{"xbox_hdd.qcow2","hddPath"}};
  for(String[]s:setup){String old=pref.getString(s[1],null);if(old!=null&&new File(old).isFile())continue;
   File f=new File(dir,s[0]);PlatformAssets.copyIfAbsent(c,"xbox-classic/setup/"+s[0],f);edit.putString(s[1],f.getAbsolutePath());}
  edit.commit();
 }
 public static void returnToPlatforms(Activity a){
  Intent i=new Intent();i.setClassName(a,"org.emulationstation.frontend.ESActivity");i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);a.startActivity(i);
  for(Activity s:new ArrayList<>(screens))if(s!=null)s.finish();a.finish();
  new Handler(Looper.getMainLooper()).postDelayed(()->android.os.Process.killProcess(android.os.Process.myPid()),350);
 }
}
