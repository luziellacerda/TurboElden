package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.os.Build;
import java.io.*;
public final class SaturnBootstrap {
    public static boolean isProcess() {
        if(Build.VERSION.SDK_INT>=28)return Application.getProcessName().endsWith(":saturn");
        try(FileInputStream in=new FileInputStream("/proc/self/cmdline")){
            byte[] b=new byte[256];int n=in.read(b),end=0;while(end<n&&b[end]!=0)end++;
            return new String(b,0,end,"UTF-8").endsWith(":saturn");
        }catch(IOException e){return false;}
    }
    public static boolean launch(Activity activity,String path,boolean settings) {
        try {
            Intent i=new Intent(activity,SaturnActivity.class);
            i.putExtra("game",path==null?"":path);i.putExtra("settings",settings);
            activity.startActivity(i);return true;
        }catch(Throwable e){android.util.Log.e("TurboSaturn","Launch failed",e);return false;}
    }
}
