from pathlib import Path
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'psp-integration';J=R/'java/org/emulationstation/frontend';J.mkdir(parents=True,exist_ok=True)
(J/'PspBootstrap.java').write_text(r'''package org.emulationstation.frontend;
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
''',encoding='utf-8')
s=(P/'ps2-integration/integrate.py').read_text();a=s.index('for rel in');b=s.index('classes=R/',a)
s=s[:a]+'''p=D/'org/ppsspp/ppsspp/PpssppActivity.smali';s=p.read_text()
if 'PspBootstrap;->internalDirectory' not in s:
 for name,args,target in [('getFilesDir','','internalDirectory'),('getExternalFilesDir','Ljava/lang/String;','userDirectory'),('getCacheDir','','cacheDirectory')]:
  s+='\\n.method public '+name+'('+args+')Ljava/io/File;\\n    .locals 1\\n    invoke-static {}, Lorg/emulationstation/frontend/PspBootstrap;->'+target+'()Ljava/io/File;\\n    move-result-object v0\\n    return-object v0\\n.end method\\n'
 s+='\\n.method public finish()V\\n    .locals 0\\n    invoke-static {}, Lorg/emulationstation/frontend/PspBootstrap;->finishing()V\\n    invoke-super {p0}, Landroid/app/Activity;->finish()V\\n    return-void\\n.end method\\n'
 p.write_text(s,encoding='utf-8')
for p in D.rglob('*.smali'):
 s=p.read_text();t=s.replace('Landroid/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;', 'Lorg/emulationstation/frontend/PspBootstrap;->preferences(Landroid/content/Context;)Landroid/content/SharedPreferences;')
 if t!=s:p.write_text(t)
'''+s[b:]
s=s.replace('ps2-integration','psp-integration').replace('smali_classes15','smali_classes17').replace('Ps2Bootstrap','PspBootstrap').replace('turbo_not_ps2','turbo_not_psp').replace('PS2 initialization','PSP initialization')
(R/'integrate.py').write_text(s,encoding='utf-8')
s=(P/'ps2-integration/package.py').read_text().replace("R=P/'ps2-integration'","R=P/'psp-integration'")
a=s.index('BASE=');b=s.index('\nJAVA=',a);s=s[:a]+"BASE=P/'TurboramaStation-PS2-ARMSX2-2.7.2.apk';OUT=P/'TurboramaStation-PSP-PPSSPP-1.20.4.apk'"+s[b:]
s=s.replace('55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85','6e76035e9943896bc7ff0044047749f5c4781821210e2953d697221bdd769911').replace("removed={'lib/arm64-v8a/libarmsx2_libretro_android.so'}","removed=set() # Old PSP core was downloaded, not bundled in the APK")
s=s.replace('classes15.dex','classes17.dex').replace('classes16.dex','classes18.dex').replace('ps2-integration','psp-integration').replace('native_ps2.h','native_psp.h').replace('ps2-unsigned','psp-unsigned').replace('ps2-aligned','psp-aligned').replace('range(2,15)','range(2,17)').replace('classes14.dex','classes16.dex').replace('ARMSX2 2.7.2','PPSSPP 1.20.4')
(R/'package.py').write_text(s,encoding='utf-8')
print('PSP bridge, migration and packaging written')
