package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.os.*;
import android.util.Log;
import java.io.*;

public final class VitaBootstrap {
    public static volatile String initializationError;
    public interface Progress { void onProgress(int percent,String phase); boolean isCancelled(); }
    private static native boolean bindSdl();
    public static native String convertRar(String source,String destination,Progress callback);
    public static void registerSdl(){System.loadLibrary("turbo_vita_jni");if(!bindSdl())throw new IllegalStateException("Vita SDL registration failed");}
    public static boolean initProcess(Application app){
        String name="";
        try{
            if(Build.VERSION.SDK_INT>=28)name=Application.getProcessName();
            else try(FileInputStream in=new FileInputStream("/proc/self/cmdline")){byte[] b=new byte[256];int n=in.read(b),end=0;while(end<n&&b[end]!=0)end++;name=new String(b,0,end,"UTF-8");}
            if(!name.endsWith(":psvita"))return false;
            Class.forName("org.vita3k.emulator.Vita3KApplication").getMethod("initEmbedded",Application.class).invoke(null,app);
            Log.i("TurboVita","Vita3K dedicated process initialized");
        }catch(Throwable e){initializationError=e.toString();Log.e("TurboVita","Initialization failed",e);}
        return name.endsWith(":psvita");
    }
    public static File files(Context c){File f=new File(c.getFilesDir(),"psvita");f.mkdirs();return f;}
    public static File userFiles(Context c,String ignored){File base=c.getExternalFilesDir(null);File f=base==null?files(c):new File(base,"psvita");f.mkdirs();return f;}
    public static File cache(Context c){File f=new File(c.getCacheDir(),"psvita");f.mkdirs();return f;}
    public static SharedPreferences preferences(Context c,String name,int mode){return c.getSharedPreferences("psvita_"+name,mode);}
    public static boolean launch(Activity a,String path,boolean settings){
        if(Build.VERSION.SDK_INT<28){new AlertDialog.Builder(a).setTitle("PS Vita").setMessage("O Vita3K integrado precisa do Android 9 ou mais recente.").setPositiveButton("VOLTAR",null).show();return true;}
        try{Intent i=new Intent();i.setClassName(a,"org.emulationstation.frontend.VitaEntryActivity");i.putExtra("game",path==null?"":path);i.putExtra("settings",settings);a.startActivity(i);return true;}
        catch(Throwable e){Log.e("TurboVita","Launch failed",e);return false;}
    }
}
