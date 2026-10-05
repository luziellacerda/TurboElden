package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.*;
import android.preference.PreferenceManager;
import java.io.*;
import java.util.*;
public final class MameBootstrap {
 private static final Set<Activity> screens=Collections.newSetFromMap(new WeakHashMap<Activity,Boolean>());
 private static final File ROMS_ROOT=new File("/storage/emulated/0/EmulationStation/roms");
 static File romDirFor(String path){
  // Station installs each artifact in its own generation/content directory.
  // MAME reads only the filename from ACTION_VIEW. The explicit -rompath
  // argument must be the actual parent, where the package also puts BIOS.
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
 static String quoteCliPath(String path){
  if(path==null||path.isEmpty())throw new IllegalArgumentException("O caminho do jogo está vazio.");
  // MAME4droid 1.41.2's native CLI tokenizer recognizes single quotes and
  // spaces, with no escape syntax. Semicolon separates MAME search paths.
  for(int n=0;n<path.length();n++){
   char ch=path.charAt(n);
   if(ch=='\''||ch==';'||Character.isISOControl(ch))throw new IllegalArgumentException("O caminho do jogo contém um caractere não suportado pelo emulador.");
  }
  return "'"+path+"'";
 }
 static String cliParamsFor(String path){
  File rom=path==null?null:new File(path);
  if(rom==null||!rom.isFile()||!rom.canRead())throw new IllegalArgumentException("O arquivo instalado não está disponível.");
  File parent=rom.getAbsoluteFile().getParentFile();
  if(parent==null||!parent.isDirectory()||!parent.canRead())throw new IllegalArgumentException("A pasta do jogo não está disponível.");
  return "-rompath "+quoteCliPath(parent.getAbsolutePath());
 }
 private static String process(){
  if(Build.VERSION.SDK_INT>=28)return Application.getProcessName();
  try(FileInputStream f=new FileInputStream("/proc/self/cmdline")){
   byte[]b=new byte[256];int n=f.read(b),i=0;while(i<n&&b[i]!=0)i++;
   return new String(b,0,i,"UTF-8");
  }catch(Exception e){return "";}
 }
 public static boolean initProcess(Application app){
  String p=process();if(!p.endsWith(":mame"))return false;
  app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   public void onActivityCreated(Activity a,Bundle b){screens.add(a);}
   public void onActivityDestroyed(Activity a){screens.remove(a);}
   public void onActivityStarted(Activity a){} public void onActivityStopped(Activity a){}
   public void onActivityResumed(Activity a){} public void onActivityPaused(Activity a){}
   public void onActivitySaveInstanceState(Activity a,Bundle b){}
  });return true;
 }
 public static File files(Context c){File f=new File(c.getFilesDir(),"mame");f.mkdirs();return f;}
 public static File cache(Context c){File f=new File(c.getCacheDir(),"mame");f.mkdirs();return f;}
 public static File userFiles(Context c,String type){
  File root=c.getExternalFilesDir(null);if(root==null)root=c.getFilesDir();
  File f=new File(root,"mame"+(type==null?"":"/"+type));f.mkdirs();return f;
 }
 public static boolean launch(Activity a,String path,boolean settings){
  if(Build.VERSION.SDK_INT<29){
   a.runOnUiThread(()->new AlertDialog.Builder(a).setTitle("Arcade M.A.M.E.").setMessage("O MAME4droid Current 1.41.2 requer Android 10 ou superior.").setPositiveButton("VOLTAR",null).show());
   return false;
  }
  try{
   Intent i=new Intent(a,MameEntryActivity.class);
   i.putExtra("game",path==null?"":path);
   i.putExtra("settings",settings);
   if(settings)i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
   a.startActivity(i);return true;
  }catch(Exception e){android.util.Log.e("TurboMame","launch",e);return false;}
 }
 public static void seed(Context c){seed(c,null);}
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
  // Upstream uses a nonempty ROMsDIR to enable SAF, even without a URI.
  // Empty (not null) is its filesystem mode and skips the first-run picker.
  // ACTION_VIEW supplies the real ROM/BIOS directory through cli_params.
  edit.putString("PREF_ROMsDIR_2","");
  edit.remove("PREF_ROMsDIR");
  edit.putString("PREF_SAF_URI",null);
  if(!dir.isDirectory()||!dir.canWrite()||!roms.isDirectory()||!roms.canRead())throw new IllegalStateException("Não foi possível preparar as pastas do emulador.");
  if(!edit.commit())throw new IllegalStateException("Não foi possível salvar a configuração do emulador.");
  android.util.Log.i("TurboMame","Configured ROM directory="+roms.getAbsolutePath()+"; mode=filesystem; launch="+(path==null?"settings":new File(path).getName()));
 }
 public static void returnToPlatforms(Activity a){
  Intent i=new Intent();i.setClassName(a,"org.emulationstation.frontend.ESActivity");
  i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);a.startActivity(i);
  for(Activity s:new ArrayList<>(screens))if(s!=null)s.finish();a.finish();
  new Handler(Looper.getMainLooper()).postDelayed(()->android.os.Process.killProcess(android.os.Process.myPid()),350);
 }
}
