package org.emulationstation.frontend;
import android.app.*;import android.content.*;import android.content.pm.*;import android.os.*;import android.util.Log;import android.widget.Toast;import java.io.*;import java.util.*;
/** XenDroid 0b11201 integration. Upstream settings remain user controlled. */
public final class Xbox360Bootstrap {
 private static Application host; private static Throwable error;
 public static boolean initProcess(Application app){
  if(Build.VERSION.SDK_INT<28)return false;String process=Application.getProcessName();if(!(app.getPackageName()+":xbox360").equals(process)&&!(app.getPackageName()+":xbox360emu").equals(process))return false;
  host=app;
  try{Class.forName("xendroid.compose.Application").getMethod("initEmbedded",Application.class).invoke(null,app);Log.i("TurboXbox360","XenDroid 0b11201 initialized");}catch(Throwable e){error=e;Log.e("TurboXbox360","Xbox360 initialization failed",e);}
  return true;
 }
 public static Throwable initializationError(){return error;}
 private static File dir(File root,String name){if(root==null)throw new IllegalStateException("Armazenamento indisponível");File f=new File(root,name);if(!f.isDirectory()&&!f.mkdirs())throw new IllegalStateException("Não foi possível criar a pasta Xbox 360");return f;}
 public static File files(Context ignored){return dir(host.getFilesDir(),"Xbox360");}
 public static File userFiles(Context ignored,String type){File root=host.getExternalFilesDir(null);File f=dir(root!=null?root:host.getFilesDir(),"Xbox360");return type==null||("compose".equals(type)||"Xbox360".equals(type))?f:dir(f,type);}
 public static File cache(Context ignored){return dir(host.getCacheDir(),"Xbox360");}
 public static SharedPreferences preferences(Context ignored,String name,int mode){return host.getSharedPreferences("xbox360_"+name,mode);}
 public static boolean launch(Activity activity,String path,boolean settings){
  if(activity==null||activity.isFinishing())return false;
  if(Build.VERSION.SDK_INT<30){activity.runOnUiThread(()->Toast.makeText(activity,"Xbox 360 requer Android 11 ou superior.",Toast.LENGTH_LONG).show());return false;}
  boolean vulkan=false;for(FeatureInfo f:activity.getPackageManager().getSystemAvailableFeatures())if("android.hardware.vulkan.version".equals(f.name)&&f.version>=0x401000)vulkan=true;
  if(!vulkan){activity.runOnUiThread(()->Toast.makeText(activity,"Xbox 360 requer suporte a Vulkan 1.1.",Toast.LENGTH_LONG).show());return false;}
  if(!settings&&(path==null||path.isEmpty()))return false;
  activity.runOnUiThread(()->{try{Intent i=new Intent(activity,settings?Xbox360EntryActivity.class:Xbox360GameEntryActivity.class);i.putExtra("game",path);i.putExtra("settings",settings);activity.startActivity(i);Log.i("TurboXbox360",settings?"Xbox360 menu requested":"Xbox360 game requested");}catch(Throwable e){Log.e("TurboXbox360","Launch failed",e);Toast.makeText(activity,"Não foi possível abrir o Xbox 360.",Toast.LENGTH_LONG).show();}});return true;
 }
 static File executable(File file,int depth)throws IOException{
  if(depth>8)return null;
  if(file.isFile()){String n=file.getName().toLowerCase(Locale.ROOT);for(String ext:new String[]{".iso",".xex",".zar",".stfs"})if(n.endsWith(ext))return file;return null;}
  if(!file.isDirectory())return null;File code=new File(file,"default.xex");if(code.isFile())return code;
  File[] list=file.listFiles();if(list==null)return null;Arrays.sort(list,Comparator.comparing(File::getName));
  for(File f:list){if(!f.getCanonicalPath().startsWith(file.getCanonicalPath()+File.separator))continue;if(f.equals(code))continue;File found=executable(f,depth+1);if(found!=null)return found;}return null;
 }
}
