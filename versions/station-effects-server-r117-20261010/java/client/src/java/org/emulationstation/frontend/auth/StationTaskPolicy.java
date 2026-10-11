package org.emulationstation.frontend.auth;

/** Pure task selection. Never selects another package or a login/restart task. */
public final class StationTaskPolicy {
    public static final String FRONTEND="org.emulationstation.frontend.ESActivity";
    public static final String ROOMS="org.emulationstation.frontend.netplay.StationRoomsActivity";
    public static final String NETPLAY="org.emulationstation.frontend.netplay.StationNetplayActivity";
    public static final String GAME="org.emulationstation.frontend.netplay.StationRetroActivity";
    // Exact emulation Activities in the frozen R70 Manifest; not entry/setup/auth screens.
    public static final String[] LOCAL_GAMES={"com.imagine.BaseActivity","com.mdimagn.BaseActivity",
        "org.emulationstation.frontend.SaturnActivity","org.ppsspp.ppsspp.PpssppActivity","com.armsx2.Main",
        "org.dolphinemu.dolphinemu.activities.EmulationActivity","com.flycast.emulator.NativeGLActivity",
        "info.cemu.cemu.emulation.EmulationActivity","org.vita3k.emulator.Emulator",
        "com.izzy2lost.x1box.MainActivity","xendroid.compose.EmulatorHostActivity",
        "com.seleuco.mame4droid.MAME4droid","paulscode.android.mupen64plusae.game.GameActivity",
        "org.yuzu.yuzu_emu.activities.EmulationActivity"};
    private StationTaskPolicy(){}
    public static boolean localGame(String name){for(String game:LOCAL_GAMES)if(game.equals(name))return true;return false;}
    public static final class Task {
        public final int id;public final String base,top;public final boolean owned,running;
        public Task(int id,String base,String top,boolean owned,boolean running){this.id=id;this.base=base;this.top=top;this.owned=owned;this.running=running;}
    }
    public static boolean usable(Task task){return task!=null&&task.id>=0&&task.owned&&task.running;}
    public static int gameTask(Task[] tasks,int registered){
        for(Task task:tasks)if(usable(task)&&task.id==registered)return task.id;
        for(Task task:tasks)if(usable(task)&&GAME.equals(task.top))return task.id;
        for(Task task:tasks)if(usable(task)&&(localGame(task.base)||localGame(task.top)))return task.id;
        return -1;
    }
    public static int resumeTask(Task[] tasks,int registered){
        int game=gameTask(tasks,registered);if(game>=0)return game;
        for(Task task:tasks)if(usable(task)&&FRONTEND.equals(task.base))return task.id;
        // Legacy R70 can retain a separate lobby task across an update.
        for(Task task:tasks)if(usable(task)&&(ROOMS.equals(task.base)||NETPLAY.equals(task.base)))return task.id;
        return -1;
    }
    public static boolean canSelectItem(boolean snapshotKnown,boolean hasRoom,boolean launching,boolean returning){return snapshotKnown&&!hasRoom&&!launching&&!returning;}
}
