package org.emulationstation.frontend;
import android.app.*;import android.content.*;import android.content.pm.*;import android.os.*;import android.util.Log;import android.widget.Toast;import java.io.*;import java.util.*;
/** Cemu Android 0.5.2 integration. Upstream settings remain user controlled. */
public final class WiiUBootstrap {
 private static Application host; private static Throwable error;
 public static boolean initProcess(Application app){
  if(Build.VERSION.SDK_INT<28||!(app.getPackageName()+":wiiu").equals(Application.getProcessName()))return false;
  host=app;
  try{Class.forName("info.cemu.cemu.CemuApplication").getMethod("initEmbedded",Application.class).invoke(null,app);configureFirstController(app);Log.i("TurboWiiU","Cemu Android 0.5.2 initialized");}catch(Throwable e){error=e;Log.e("TurboWiiU","Cemu initialization failed",e);}
  return true;
 }
 public static Throwable initializationError(){return error;}
 private static void configureFirstController(Application app){
  SharedPreferences prefs=app.getSharedPreferences("turbo_wiiu_defaults",Context.MODE_PRIVATE);
  if(prefs.getBoolean("gamepad_v1",false))return;
  try{
   Class<?> input=Class.forName("info.cemu.cemu.nativeinterface.NativeInput");
   boolean disabled=(Boolean)input.getMethod("isControllerDisabled",int.class).invoke(null,0);
   if(disabled){
    input.getMethod("setControllerType",int.class,int.class).invoke(null,0,0);
    input.getMethod("saveInputs").invoke(null);
    Log.i("TurboWiiU","Enabled default Wii U GamePad for touch controls");
   }
   prefs.edit().putBoolean("gamepad_v1",true).apply();
  }catch(Throwable e){Log.e("TurboWiiU","Default GamePad setup failed",e);}
 }
 private static File dir(File root,String name){if(root==null)throw new IllegalStateException("Armazenamento indisponível");File f=new File(root,name);if(!f.isDirectory()&&!f.mkdirs())throw new IllegalStateException("Não foi possível criar a pasta Wii U");return f;}
 public static File files(Context ignored){return dir(host.getFilesDir(),"Cemu");}
 public static File userFiles(Context ignored,String type){File root=host.getExternalFilesDir(null);File f=dir(root!=null?root:host.getFilesDir(),"Cemu");return type==null?f:dir(f,type);}
 public static File cache(Context ignored){return dir(host.getCacheDir(),"Cemu");}
 public static SharedPreferences preferences(Context ignored,String name,int mode){return host.getSharedPreferences("cemu_"+name,mode);}
 public static boolean launch(Activity activity,String path,boolean settings){
  if(activity==null||activity.isFinishing())return false;
  if(Build.VERSION.SDK_INT<30){activity.runOnUiThread(()->Toast.makeText(activity,"Wii U requer Android 11 ou superior.",Toast.LENGTH_LONG).show());return false;}
  boolean vulkan=false;for(FeatureInfo f:activity.getPackageManager().getSystemAvailableFeatures())if("android.hardware.vulkan.version".equals(f.name)&&f.version>=0x401000)vulkan=true;
  if(!vulkan){activity.runOnUiThread(()->Toast.makeText(activity,"Wii U requer suporte a Vulkan 1.1.",Toast.LENGTH_LONG).show());return false;}
  if(!settings&&(path==null||path.isEmpty()))return false;
  activity.runOnUiThread(()->{try{Intent i=new Intent(activity,WiiUEntryActivity.class);i.putExtra("game",path);i.putExtra("settings",settings);activity.startActivity(i);Log.i("TurboWiiU",settings?"Cemu menu requested":"Cemu game requested");}catch(Throwable e){Log.e("TurboWiiU","Launch failed",e);Toast.makeText(activity,"Não foi possível abrir o Wii U.",Toast.LENGTH_LONG).show();}});return true;
 }
 static File executable(File file,int depth)throws IOException{
  if(depth>8)return null;
  if(file.isFile()){String n=file.getName().toLowerCase(Locale.ROOT);for(String ext:new String[]{".wux",".wud",".wua",".wuhb",".rpx",".elf",".iso"})if(n.endsWith(ext))return file;return null;}
  if(!file.isDirectory())return null;File code=new File(file,"code");if(code.isDirectory()){File found=executable(code,depth+1);if(found!=null)return found;}
  File[] list=file.listFiles();if(list==null)return null;Arrays.sort(list,Comparator.comparing(File::getName));
  for(File f:list){if(!f.getCanonicalPath().startsWith(file.getCanonicalPath()+File.separator))continue;if(f.equals(code))continue;File found=executable(f,depth+1);if(found!=null)return found;}return null;
 }
}
