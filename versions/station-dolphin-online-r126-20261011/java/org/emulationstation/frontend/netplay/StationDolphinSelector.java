package org.emulationstation.frontend.netplay;

import android.app.*;
import android.content.*;
import android.os.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import org.json.*;

/** Selects one real Dolphin library before its JNI globals are initialized.
 * A private launch prepared by the room worker is the only online selector.
 * An already initialized offline process must return a restart result; it must
 * never load a second Dolphin library into the same process. */
public final class StationDolphinSelector {
    private static volatile JSONObject selected;
    private static volatile String selectedName;
    private static boolean initialized;
    static final int RESTART_IDLE_PROCESS=402;
    static final String EXTRA="station.dolphin.launch";

    public static synchronized String libraryName(Context context) {
        if(initialized)return selected==null?"dolp":"station_dolphin_online";
        initialized=true;
        String name=null;
        try {
            File pending=new File(context.getNoBackupFilesDir(),"station-online/dolphin-pending");
            if(!pending.isFile())return "dolp";
            try(InputStream in=new FileInputStream(pending)){
                name=new String(StationOnlineGame.read(in,128),StandardCharsets.UTF_8);
            }
            JSONObject launch=StationDolphinLaunch.peek(context,name);
            StationDolphinLaunch.verifyIdentity(context,launch);
            selectedName=name;selected=launch;
            return "station_dolphin_online";
        }catch(Exception failure){
            // An orphaned preparation may expire after Android killed a
            // process. Remove that exact pointer so normal launch still works.
            // An online entry with this name fails its own descriptor check;
            // no game is launched with a substituted engine or identity.
            if(name!=null&&(failure instanceof FileNotFoundException||"DOLPHIN_LAUNCH_EXPIRED".equals(failure.getMessage()))){
                StationDolphinLaunch.discard(context,name);return "dolp";
            }
            throw new IllegalStateException("DOLPHIN_PRIVATE_LAUNCH_INVALID",failure);
        }
    }
    static boolean selected(String name){return name!=null&&name.equals(selectedName)&&selected!=null;}
    static JSONObject descriptor(){return selected;}

    /** Only the selected session receives private data/config/cache directories. */
    public static File directory(Context context,String kind) {
        JSONObject launch=selected;if(launch==null)return null;
        if(!kind.equals("User")&&!kind.equals("Internal")&&!kind.equals("Cache"))throw new IllegalArgumentException("Dolphin directory");
        try {
            File dir=new File(context.getNoBackupFilesDir(),"station-online/dolphin/"+launch.getString("roomId")+"/"+launch.getLong("generation")+"/"+kind);
            File root=context.getNoBackupFilesDir().getCanonicalFile();
            if(Files.isSymbolicLink(dir.toPath())||!dir.getCanonicalPath().startsWith(root.getPath()+File.separator))throw new IOException("DOLPHIN_SESSION_DIRECTORY");
            if(!dir.isDirectory()&&!dir.mkdirs())throw new IOException("DOLPHIN_SESSION_DIRECTORY");
            return dir;
        }catch(Exception failure){throw new IllegalStateException("DOLPHIN_SESSION_DIRECTORY",failure);}
    }
    public static boolean skipLegacySaves(Context context){return selected!=null;}

    /** One exclusive process owns Dolphin JNI globals. A normal launch cannot
     * boot over an online session; returning this entry does not stop that game. */
    public static boolean rejectOfflineLaunch(Activity activity){
        if(selected==null)return false;
        android.widget.Toast.makeText(activity,"Saia da partida online antes de abrir outro jogo.",android.widget.Toast.LENGTH_LONG).show();
        activity.setResult(Activity.RESULT_CANCELED);activity.finish();return true;
    }

    /** An existing normal process can restart only while its core is stopped.
     * The parent receives the result before this idle process is terminated. */
    static void requestIdleRestart(Activity entry)throws Exception {
        boolean running=(Boolean)Class.forName("org.dolphinemu.dolphinemu.NativeLibrary").getMethod("IsRunning").invoke(null);
        if(running)throw new IOException("DOLPHIN_OFFLINE_GAME_ACTIVE");
        entry.setResult(RESTART_IDLE_PROCESS,new Intent().putExtra("station.dolphin.pid",android.os.Process.myPid()));entry.finish();
        new Handler(Looper.getMainLooper()).postDelayed(()->android.os.Process.killProcess(android.os.Process.myPid()),500);
    }
    /** The online owner calls this only after explicit exit and native cleanup. */
    static void finishOnlineProcess(Activity entry) {
        if(selected==null)throw new IllegalStateException("DOLPHIN_PROCESS_OWNER");
        entry.setResult(Activity.RESULT_OK);entry.finish();
        new Handler(Looper.getMainLooper()).postDelayed(()->android.os.Process.killProcess(android.os.Process.myPid()),500);
    }
}
