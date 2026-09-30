package org.emulationstation.frontend;
import android.app.*;import android.content.*;import android.os.*;import android.net.Uri;import android.util.Log;import android.widget.Toast;import java.io.*;import java.util.*;import org.json.JSONArray;
/** GPL-3.0-or-later. Integration only; upstream emulation defaults are retained. */
public final class Ps2Bootstrap {
 private static Application host; private static Context emulator; private static final String TAG="TurboPS2";
 private static final Handler main=new Handler(Looper.getMainLooper());
 public static boolean initProcess(Application app){
  String name=null;
  if(Build.VERSION.SDK_INT>=28)name=Application.getProcessName();
  else {ActivityManager am=(ActivityManager)app.getSystemService(Context.ACTIVITY_SERVICE);List<ActivityManager.RunningAppProcessInfo> list=am.getRunningAppProcesses();if(list!=null)for(ActivityManager.RunningAppProcessInfo p:list)if(p.pid==android.os.Process.myPid())name=p.processName;}
  if(!(app.getPackageName()+":ps2").equals(name))return false;
  host=app;
  try {migrate();emulator=(Context)Class.forName("com.armsx2.Pasx2Application").getMethod("initEmbedded",Application.class).invoke(null,app);Log.i(TAG,"Official ARMSX2 2.7.2 initialized in internal process");}
  catch(Throwable e){Log.e(TAG,"PS2 initialization failed",e);}
  return true;
 }
 private static File dir(File base,String name){if(base==null)throw new IllegalStateException("Armazenamento indisponível");File f=new File(base,name);if(!f.isDirectory()&&!f.mkdirs())throw new IllegalStateException("Pasta PS2 indisponível");return f;}
 public static File userDirectory(){File root=host.getExternalFilesDir(null);return dir(root!=null?root:host.getFilesDir(),"PS2");}
 public static File internalDirectory(){return dir(host.getFilesDir(),"PS2");}
 public static File cacheDirectory(){return dir(host.getCacheDir(),"PS2");}
 public static Context applicationContext(){return emulator!=null?emulator:host;}
 private static void copy(InputStream in,File target)throws IOException{
  try(InputStream input=in){if(target.exists())return;dir(target.getParentFile(),".");File temp=new File(target.getPath()+".importing");try(FileOutputStream out=new FileOutputStream(temp)){byte[]b=new byte[65536];int n;while((n=input.read(b))!=-1)out.write(b,0,n);out.getFD().sync();}if(target.exists()){temp.delete();return;}if(!temp.renameTo(target))throw new IOException("Falha ao importar "+target.getName());Log.i(TAG,"Copied missing support file "+target.getName());}
 }
 private static void migrate()throws Exception{
  File user=userDirectory(),bios=dir(internalDirectory(),"bios"),cards=dir(user,"memcards");
  for(String name:host.getAssets().list("bios/pcsx2/bios"))if(!new File(bios,name).exists())copy(host.getAssets().open("bios/pcsx2/bios/"+name),new File(bios,name));
  File legacy=new File(Environment.getExternalStorageDirectory(),"EmulationStation/.emulationstation/bios/pcsx2/memcards");
  File[] list=legacy.listFiles();if(list!=null)for(File f:list)if(f.isFile()&&f.getName().toLowerCase(Locale.ROOT).endsWith(".ps2"))copy(new FileInputStream(f),new File(cards,f.getName().toLowerCase(Locale.ROOT)));
  SharedPreferences prefs=host.getSharedPreferences("TURBORAMA_PS2",Context.MODE_PRIVATE);
  if(!prefs.getBoolean("turborama.initialized",false)){
   File chosen=null;File[] available=bios.listFiles();if(available!=null)for(File f:available)if(f.isFile()&&f.length()==4194304){chosen=f;break;}
   if(chosen==null)throw new IOException("BIOS PS2 ausente ou inválida");
   JSONArray roms=new JSONArray();File root=new File(Environment.getExternalStorageDirectory(),"EmulationStation/roms");
   for(String n:new String[]{"ps2","ps2br"}){File d=new File(root,n);if(d.isDirectory())roms.put(d.getAbsolutePath());}
   if(roms.length()==0)roms.put(root.getAbsolutePath());
   if(!prefs.edit().putString("bios",chosen.getAbsolutePath()).putString("biosDir",bios.getAbsolutePath()).putString("systemDir",user.getAbsolutePath()).putString("romsDirs",roms.toString()).putBoolean("setupComplete",true).putBoolean("ui.exitToLauncherExternal",true).putBoolean("turborama.initialized",true).commit())throw new IOException("Falha ao salvar configuração inicial PS2");
  }
 }
 public static boolean launch(Activity activity,String path,boolean settings){
  if(activity==null||activity.isFinishing()||(!settings&&(path==null||!new File(path).isFile())))return false;
  activity.runOnUiThread(()->{try{Intent i=new Intent();i.setClassName(activity,"com.armsx2.Main");i.putExtra("turborama_settings",settings);if(!settings){i.setAction(Intent.ACTION_VIEW);i.setData(Uri.parse(path));}activity.startActivity(i);Log.i(TAG,settings?"Official PS2 settings requested":"Official PS2 game requested");}catch(Throwable e){Log.e(TAG,"PS2 launch failed",e);Toast.makeText(activity,"Não foi possível abrir o PS2.",Toast.LENGTH_LONG).show();}});return true;
 }
 public static void finishActivity(Activity activity){Log.i(TAG,"Returning to TurboramaStation with task and login retained");activity.finish();}
 public static void activityReady(Activity activity){
  if(activity.getIntent()==null||!activity.getIntent().getBooleanExtra("turborama_settings",false))return;
  try{activity.getClass().getMethod("embeddedSettings").invoke(null);Log.i(TAG,"Official PS2 settings opened");}
  catch(Throwable e){Log.e(TAG,"Settings route failed",e);return;}
  main.postDelayed(new Runnable(){public void run(){if(activity.isFinishing()||activity.isDestroyed())return;try{if(activity.hasWindowFocus()&&(Boolean)activity.getClass().getMethod("embeddedAtHome").invoke(null)){finishActivity(activity);return;}}catch(Throwable e){Log.e(TAG,"Settings return monitor failed",e);return;}main.postDelayed(this,250);}},500);
 }
}
