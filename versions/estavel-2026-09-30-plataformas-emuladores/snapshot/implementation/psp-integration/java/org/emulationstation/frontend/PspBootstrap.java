package org.emulationstation.frontend;
import android.app.*;import android.content.*;import android.os.*;import android.util.Log;import android.widget.Toast;import java.io.*;import java.util.*;
/** GPL-2.0-or-later integration with the official PPSSPP Android API. */
public final class PspBootstrap {
 private static Application host;private static final String TAG="TurboPSP";
 public static boolean initProcess(Application app){String name=null;if(Build.VERSION.SDK_INT>=28)name=Application.getProcessName();else{ActivityManager am=(ActivityManager)app.getSystemService(Context.ACTIVITY_SERVICE);List<ActivityManager.RunningAppProcessInfo> list=am.getRunningAppProcesses();if(list!=null)for(ActivityManager.RunningAppProcessInfo p:list)if(p.pid==android.os.Process.myPid())name=p.processName;}
 if(!(app.getPackageName()+":psp").equals(name))return false;host=app;try{migrate();Log.i(TAG,"PPSSPP 1.20.4 process prepared");}catch(Throwable e){Log.e(TAG,"PSP migration failed",e);}return true;}
 private static File dir(File root,String name){if(root==null)throw new IllegalStateException("Armazenamento indisponível");File f=new File(root,name);if(!f.isDirectory()&&!f.mkdirs())throw new IllegalStateException("Pasta PSP indisponível");return f;}
 public static File userDirectory(){File root=host.getExternalFilesDir(null);return dir(root!=null?root:host.getFilesDir(),"PPSSPP");}
 public static File internalDirectory(){return dir(host.getFilesDir(),"PPSSPP");}
 public static File cacheDirectory(){return dir(host.getCacheDir(),"PPSSPP");}
 public static SharedPreferences preferences(Context c){return host.getSharedPreferences("turborama_ppsspp_preferences",Context.MODE_PRIVATE);}
 private static void copyMissing(File src,File dst)throws IOException{if(!src.exists()||!src.getCanonicalPath().equals(src.getAbsolutePath()))return;if(src.isDirectory()){dir(dst.getParentFile(),dst.getName());File[] children=src.listFiles();if(children!=null)for(File c:children)copyMissing(c,new File(dst,c.getName()));return;}if(!src.isFile()||dst.exists())return;dir(dst.getParentFile(),".");File temp=new File(dst.getPath()+".importing");try(InputStream in=new FileInputStream(src);FileOutputStream out=new FileOutputStream(temp)){byte[]b=new byte[65536];int n;while((n=in.read(b))!=-1)out.write(b,0,n);out.getFD().sync();}if(dst.exists()){temp.delete();return;}if(!temp.renameTo(dst))throw new IOException("Falha ao copiar save PSP");}
 private static void migrate()throws IOException{
 File memstick=dir(userDirectory(),"memstick"),psp=dir(memstick,"PSP"),legacy=new File(Environment.getExternalStorageDirectory(),"EmulationStation/.emulationstation/saves/PSP");
 for(String n:new String[]{"SAVEDATA","PPSSPP_STATE","CHEATS","NAND"})copyMissing(new File(legacy,n),new File(psp,n));
 File target=new File(internalDirectory(),"memstick_dir.txt");if(!target.exists())try(FileOutputStream out=new FileOutputStream(target)){out.write(memstick.getAbsolutePath().getBytes("UTF-8"));out.getFD().sync();}
 // Only the obsolete downloaded engines; save data and support directories are preserved.
 File[] roots={new File(host.getFilesDir(),"cores"),new File(Environment.getExternalStorageDirectory(),"EmulationStation/.emulationstation/cores")};
 for(File root:roots)for(String n:new String[]{"ppsspp_libretro_android.so","libppsspp_libretro_android.so"}){File f=new File(root,n);if(f.isFile())Log.i(TAG,"Remove old PSP core "+n+": "+f.delete());}
 }
 public static boolean launch(Activity activity,String path,boolean settings){if(activity==null||activity.isFinishing()||(!settings&&(path==null||!new File(path).isFile())))return false;
 final String args=settings?"--gamesettings":"--pause-menu-exit \""+path.replace("\\","\\\\").replace("\"","\\\"")+"\"";
 activity.runOnUiThread(()->{try{Intent i=new Intent();i.setClassName(activity,"org.ppsspp.ppsspp.PpssppActivity");i.putExtra("org.ppsspp.ppsspp.Args",args);activity.startActivity(i);Log.i(TAG,settings?"Official PSP settings requested":"Official PSP game requested");}catch(Throwable e){Log.e(TAG,"Launch failed",e);Toast.makeText(activity,"Não foi possível abrir o PSP.",Toast.LENGTH_LONG).show();}});return true;}
 public static void activityReady(Activity activity){Log.i(TAG,"Official PPSSPP Activity initializing");}
 public static void finishing(){Log.i(TAG,"Returning to TurboramaStation; task and login retained");}
}
