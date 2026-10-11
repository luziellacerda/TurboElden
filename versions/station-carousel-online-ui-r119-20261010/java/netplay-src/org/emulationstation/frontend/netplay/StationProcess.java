package org.emulationstation.frontend.netplay;
import android.app.Application;
import android.os.Build;
import java.io.*;
import java.nio.charset.StandardCharsets;
public final class StationProcess {
    private StationProcess(){}
    public static boolean isNetplay(){
        String name="";
        if(Build.VERSION.SDK_INT>=28)name=Application.getProcessName();
        else try(InputStream input=new FileInputStream("/proc/self/cmdline")){byte[] b=new byte[256];int n=input.read(b),end=0;while(end<n&&b[end]!=0)end++;name=new String(b,0,end,StandardCharsets.UTF_8);}catch(IOException ignored){}
        return name!=null&&name.endsWith(":station_netplay");
    }
}
