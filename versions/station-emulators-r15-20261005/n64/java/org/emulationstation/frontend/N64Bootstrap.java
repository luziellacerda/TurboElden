package org.emulationstation.frontend;

import android.app.*;
import android.content.*;
import android.os.*;
import android.view.View;
import java.io.*;
import java.util.*;

/** Bridges the complete upstream AE application; it never renders game controls. */
public final class N64Bootstrap {
 private static final Set<Activity> screens=Collections.newSetFromMap(new WeakHashMap<Activity,Boolean>());
 static boolean settingsLaunch, openedSettings, returning;
 public static SharedPreferences sharedPrefs(Context c,String name,int mode){return c.getSharedPreferences("n64."+name,mode);}
 public static SharedPreferences preferences(Context c){return sharedPrefs(c,c.getPackageName()+"_preferences",0);}
 private static File directory(File f){if(!f.isDirectory()&&!f.mkdirs())throw new IllegalStateException("Não foi possível preparar a pasta do Nintendo 64.");return f;}
 public static File files(Context c){return directory(new File(c.getFilesDir(),"n64"));}
 public static File cache(Context c){return directory(new File(c.getCacheDir(),"n64"));}
 public static File userFiles(Context c,String type){File root=c.getExternalFilesDir(null);if(root==null)root=c.getFilesDir();return directory(new File(root,"n64"+(type==null?"":"/"+type)));}
 public static boolean initProcess(Application app){
  String process=Build.VERSION.SDK_INT>=28?Application.getProcessName():"";
  if(!process.endsWith(":n64")&&!process.endsWith(":n64core"))return false;
  seed(app);
  app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   public void onActivityCreated(Activity a,Bundle state){screens.add(a);}
   public void onActivityStarted(Activity a){}
   public void onActivityResumed(Activity a){
    if(settingsLaunch&&!openedSettings&&a.getClass().getName().equals("paulscode.android.mupen64plusae.GalleryActivity")){
     openedSettings=true;a.getWindow().getDecorView().post(()->{
      try{a.getClass().getMethod("onOpenDrawerButtonClicked",View.class).invoke(a,new Object[]{null});}
      catch(Exception e){android.util.Log.e("TurboN64","Could not open upstream settings drawer",e);}
     });
    }
   }
   public void onActivityPaused(Activity a){} public void onActivityStopped(Activity a){}
   public void onActivitySaveInstanceState(Activity a,Bundle state){}
   public void onActivityDestroyed(Activity a){
    screens.remove(a);
    if(!returning&&a.isFinishing()&&a.getClass().getName().equals("paulscode.android.mupen64plusae.GalleryActivity"))returnToPlatforms(a);
   }
  });return true;
 }
 public static void seed(Context c){
  files(c);cache(c);SharedPreferences p=preferences(c);
  if(!p.contains("gameDataStorageType"))p.edit().putString("gameDataStorageType","internal").commit();
 }
 public static boolean launch(Activity a,String game,boolean settings){
  if(Build.VERSION.SDK_INT<28){a.runOnUiThread(()->new AlertDialog.Builder(a).setTitle("Nintendo 64").setMessage("Este emulador requer Android 9 ou superior.").setPositiveButton("VOLTAR",null).show());return false;}
  if(!settings&&(game==null||!new File(game).isFile()||!new File(game).canRead()))return false;
  try{Intent i=new Intent(a,N64EntryActivity.class).putExtra("game",game==null?"":game).putExtra("settings",settings);a.startActivity(i);return true;}
  catch(Exception e){android.util.Log.e("TurboN64","Launch failed",e);return false;}
 }
 public static void returnToPlatforms(Activity a){
  if(returning)return;returning=true;
  Intent i=new Intent().setClassName(a,"org.emulationstation.frontend.ESActivity").addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);
  a.startActivity(i);for(Activity s:new ArrayList<>(screens))if(s!=null&&!s.isFinishing())s.finish();
  // CoreService shuts its own emulation process down through the upstream exit.
  new Handler(Looper.getMainLooper()).postDelayed(()->android.os.Process.killProcess(android.os.Process.myPid()),350);
 }
}
