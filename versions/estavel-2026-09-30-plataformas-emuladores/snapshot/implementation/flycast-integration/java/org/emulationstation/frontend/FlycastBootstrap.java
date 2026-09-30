package org.emulationstation.frontend;

import android.app.*;
import android.content.*;
import android.os.*;
import android.net.Uri;
import android.util.Log;
import android.widget.Toast;
import java.io.*;
import java.util.*;

/** GPL-2.0-or-later integration; upstream engine and emulation settings are retained. */
public final class FlycastBootstrap {
    private static final String TAG="TurboFlycast";
    private static Application host;
    private static Context emulator;
    private static boolean settingsOnly;
    private static volatile String lastLaunchError="Não foi possível abrir o Flycast integrado.";
    private static final Handler main=new Handler(Looper.getMainLooper());

    public static boolean initProcess(Application app) {
        String name=null;
        if (Build.VERSION.SDK_INT>=28) name=Application.getProcessName();
        else {
            ActivityManager am=(ActivityManager)app.getSystemService(Context.ACTIVITY_SERVICE);
            List<ActivityManager.RunningAppProcessInfo> list=am.getRunningAppProcesses();
            if (list!=null) for (ActivityManager.RunningAppProcessInfo item:list)
                if (item.pid==android.os.Process.myPid()) name=item.processName;
        }
        if (!(app.getPackageName()+":flycast").equals(name)) {
            if (app.getPackageName().equals(name)) removeLegacyEngine(app);
            return false;
        }
        host=app;
        try {
            migrate();
            installBundledBios();
            emulator=(Context)Class.forName("com.flycast.emulator.Emulator")
                .getMethod("initEmbedded",Application.class).invoke(null,app);
            System.loadLibrary("turbo_flycast");
            Log.i(TAG,"Official Flycast v2.7-44 initialized in internal process");
        } catch (Throwable e) { Log.e(TAG,"Flycast initialization failed",e); }
        return true;
    }
    public static Context applicationContext(){return emulator;}
    public static SharedPreferences preferences(Context ignored){return host.getSharedPreferences("flycast_preferences",Context.MODE_PRIVATE);}
    private static File dir(File root,String name){
        if(root==null) throw new IllegalStateException("Armazenamento indisponível");
        File f=new File(root,name);
        if(!f.isDirectory()&&!f.mkdirs())throw new IllegalStateException("Não foi possível criar a pasta Flycast");
        return f;
    }
    public static File userDirectory(){File base=host.getExternalFilesDir(null);return dir(base!=null?base:host.getFilesDir(),"Flycast");}
    public static File internalDirectory(){return dir(host.getFilesDir(),"Flycast");}
    public static File cacheDirectory(){return dir(host.getCacheDir(),"Flycast");}
    public static boolean launch(final Activity activity,final String path,final boolean settings){
        if(activity==null||activity.isFinishing()||(!settings&&(path==null||path.isEmpty())))return false;
        final String game;
        try {game=settings?path:resolveGame(path);}
        catch(IOException e){lastLaunchError=e.getMessage();Log.w(TAG,"Game image refused: "+lastLaunchError);return false;}
        activity.runOnUiThread(()->{
            try{
                Intent i=new Intent();i.setClassName(activity,"com.flycast.emulator.NativeGLActivity");
                i.putExtra("turborama_settings",settings);
                // The official ACTION_VIEW route accepts a raw absolute path as a Uri.
                // A file:// Intent would trigger FileUriExposedException on Android 7+.
                if(!settings){i.setAction(Intent.ACTION_VIEW);i.setData(Uri.parse(game));}
                activity.startActivity(i);
                Log.i(TAG,settings?"Embedded settings requested":"Embedded game requested");
            }catch(RuntimeException e){Log.e(TAG,"Launch failed",e);Toast.makeText(activity,"Não foi possível abrir o Flycast.",Toast.LENGTH_LONG).show();}
        });
        return true;
    }
    // Called after upstream initialization and before the first renderer surface.
    public static void activityReady(final Activity activity){
        if(!installNavigation())Log.e(TAG,"Native return button unavailable: unsupported engine ABI");
        Intent i=activity.getIntent();
        settingsOnly=i!=null&&i.getBooleanExtra("turborama_settings",false);
        if(settingsOnly){
            if(!openNativeSettings()){
                Log.e(TAG,"Official Settings entry unavailable");
                Toast.makeText(activity,"Abra Configurações no menu do Flycast.",Toast.LENGTH_LONG).show();
                return;
            }
            Log.i(TAG,"Official settings selected before renderer start");
            main.postDelayed(new Runnable(){public void run(){
                if(activity.isFinishing()||activity.isDestroyed())return;
                if(activity.hasWindowFocus()&&isNativeBrowser()){
                    Log.i(TAG,"Settings closed; returning to TurboramaStation");activity.finish();
                }else main.postDelayed(this,250);
            }},500);
        }
    }
    public static void gameState(boolean started){Log.i(TAG,started?"Emulation resumed":"Emulation paused or stopped");}
    public static void finishActivity(final Activity activity){
        main.post(()->{Log.i(TAG,"Official exit returning to TurboramaStation");activity.finish();});
    }
    private static native boolean installNavigation();
    private static native boolean openNativeSettings();
    private static native boolean isNativeBrowser();

    public static String getLastLaunchError(){return lastLaunchError;}
    private static String resolveGame(String path)throws IOException{
        if(path.startsWith("content://"))return path;
        File game=new File(path);
        if(!game.isFile())throw new IOException("Arquivo do jogo não encontrado. Confira o download.");
        String lower=path.replace('\\','/').toLowerCase(Locale.ROOT);
        if(lower.contains("/dreamcast/")&&(lower.endsWith(".bin")||lower.endsWith(".raw"))){
            String name=game.getName();String stem=name.substring(0,name.lastIndexOf('.'));
            stem=stem.replaceFirst("(?i)\\s*\\((?:track|faixa)\\s*\\d+\\)\\s*$","");
            File[] siblings=game.getParentFile().listFiles();File descriptor=null;
            if(siblings!=null)for(File f:siblings){
                String n=f.getName();int dot=n.lastIndexOf('.');if(dot<0||!f.isFile())continue;
                String ext=n.substring(dot).toLowerCase(Locale.ROOT);
                if((ext.equals(".gdi")||ext.equals(".cue")||ext.equals(".chd")||ext.equals(".cdi"))&&n.substring(0,dot).equalsIgnoreCase(stem)){
                    if(descriptor!=null)throw new IOException("Há mais de uma imagem deste disco. Selecione o arquivo GDI, CUE ou CHD na lista.");
                    descriptor=f;
                }
            }
            if(descriptor==null)throw new IOException("Jogo de Dreamcast incompleto: esta é apenas uma faixa do disco. É necessário o GDI/CUE com todas as faixas ou uma imagem CHD/CDI completa.");
            game=descriptor;lower=game.getAbsolutePath().toLowerCase(Locale.ROOT);
            Log.i(TAG,"Resolved disc descriptor instead of isolated track");
        }
        if(lower.endsWith(".gdi")||lower.endsWith(".cue")){
            if(game.length()>1024*1024)throw new IOException("Descritor de disco inválido.");
            java.util.regex.Pattern cue=java.util.regex.Pattern.compile("(?i)^\\s*FILE\\s+(?:\"([^\"]+)\"|(\\S+))\\s+");
            java.util.regex.Pattern gdi=java.util.regex.Pattern.compile("^\\s*\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+(?:\"([^\"]+)\"|(\\S+))\\s+\\d+");
            int tracks=0;
            try(BufferedReader reader=new BufferedReader(new InputStreamReader(new FileInputStream(game),"UTF-8"))){
                String line;while((line=reader.readLine())!=null){
                    java.util.regex.Matcher m=(lower.endsWith(".gdi")?gdi:cue).matcher(line);
                    if(m.find()){
                        String n=m.group(1)!=null?m.group(1):m.group(2);
                        if(!new File(game.getParentFile(),n).isFile())throw new IOException("Jogo incompleto: falta a faixa "+n+". Conclua o download do disco.");
                        tracks++;
                    }
                }
            }
            if(tracks==0)throw new IOException("O descritor do disco não contém faixas válidas.");
        }
        return game.getAbsolutePath();
    }
    /** Provision bundled owner-supplied BIOS files without overwriting existing data. */
    private static void installBundledBios()throws IOException{
        File target=dir(userDirectory(),"data");
        String[] names={"dc_boot.bin","dc_flash.bin","naomi.zip","naomi2.zip","awbios.zip","hod2bios.zip","f355bios.zip","f355dlx.zip","airlbios.zip"};
        for(String n:names){
            File to=new File(target,n);if(to.exists())continue;
            File tmp=new File(target,n+".turborama-bios-copy");
            try(InputStream in=host.getAssets().open("flycast-bios/"+n);OutputStream out=new FileOutputStream(tmp)){
                byte[] buffer=new byte[32768];int count;while((count=in.read(buffer))!=-1)out.write(buffer,0,count);
            }
            if(to.exists()){tmp.delete();continue;}
            if(!tmp.renameTo(to))throw new IOException("Falha ao preparar BIOS "+n);
            Log.i(TAG,"Bundled BIOS ready: "+n);
        }
    }

    private static void removeLegacyEngine(Context c){
        File[] dirs={new File(c.getFilesDir(),"cores"),new File(Environment.getExternalStorageDirectory(),"EmulationStation/.emulationstation/cores")};
        for(File d:dirs)for(String n:new String[]{"flycast_libretro_android.so","libflycast_libretro_android.so"}){
            File f=new File(d,n);if(f.isFile())Log.i(TAG,f.delete()?"Removed obsolete Flycast Libretro binary":"Legacy binary retained on disk; route disabled");
        }
    }
    private static void copyMissing(File from,File to)throws IOException{
        if(!from.isFile()||to.exists())return;
        File parent=to.getParentFile();if(!parent.isDirectory()&&!parent.mkdirs())throw new IOException("Cannot create save folder");
        File temp=new File(parent,to.getName()+".turborama-copy");
        try(InputStream in=new FileInputStream(from);OutputStream out=new FileOutputStream(temp)){
            byte[] b=new byte[32768];int n;while((n=in.read(b))!=-1)out.write(b,0,n);
        }
        if(to.exists()){temp.delete();return;}
        if(!temp.renameTo(to))throw new IOException("Cannot commit copied save");
        Log.i(TAG,"Copied missing legacy support/save: "+from.getName());
    }
    private static boolean support(String n){
        n=n.toLowerCase(Locale.ROOT);
        return n.equals("dc_boot.bin")||n.equals("dc_flash.bin")||n.equals("dc_nvmem.bin")||n.equals("naomi.zip")||n.equals("naomi2.zip")||n.equals("awbios.zip")||n.equals("hod2bios.zip")||n.equals("f355bios.zip")||n.equals("f355dlx.zip")||n.equals("airlbios.zip")||n.endsWith(".nvmem")||n.endsWith(".nvmem2")||n.endsWith(".eeprom")||n.startsWith("vmu_save_")&&n.endsWith(".bin")||n.matches(".*[._][a-d][12]\\.bin");
    }
    private static void migrate() throws IOException{
        File target=userDirectory();File data=dir(target,"data");File mark=new File(target,".turborama-legacy-copy-v1");
        preferences(host).edit().putString("home_directory",preferences(host).getString("home_directory",target.getAbsolutePath())).apply();
        if(mark.exists())return;
        File root=new File(Environment.getExternalStorageDirectory(),"EmulationStation/.emulationstation");
        File[] sources={new File(root,"saves/reicast"),new File(root,"bios/dc"),new File(root,"bios/dc/data")};
        boolean shared=false,perGame=false;
        for(File source:sources){
            File[] files=source.listFiles();if(files==null)continue;
            for(File f:files)if(f.isFile()&&support(f.getName())){
                String n=f.getName();
                if(n.matches(".*\\.[A-D][12]\\.bin")){
                    int at=n.length()-7;n=n.substring(0,at)+"_vmu_save_"+n.substring(at+1);
                    perGame=true;
                }
                if(n.equalsIgnoreCase("vmu_save_A1.bin"))shared=true;
                copyMissing(f,new File(data,n));
            }
        }
        // Shared Libretro VMUs must remain shared when no per-game VMU exists.
        File cfg=new File(target,"emu.cfg");
        if(shared&&!perGame&&!cfg.exists())try(Writer out=new OutputStreamWriter(new FileOutputStream(cfg),"UTF-8")){out.write("[config]\nPerGameVmu = no\n");}
        try(Writer out=new OutputStreamWriter(new FileOutputStream(mark),"UTF-8")){out.write("Missing native saves/support copied; source preserved. No shader/state/config import.\n");}
    }
}
