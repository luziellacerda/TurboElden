package org.emulationstation.frontend.netplay;

/** Terminal load gate plus a pause-aware clock used only by the legacy GIF fallback. */
final class StationSinglePassAnimationState {
    private static final int LOAD_NEW=0,LOAD_RUNNING=1,LOAD_READY=2,LOAD_FAILED=3;
    private long elapsedMs,runningSince=-1;
    private int loadState=LOAD_NEW;
    boolean beginLoad(){if(loadState!=LOAD_NEW)return false;loadState=LOAD_RUNNING;return true;}
    void finishLoad(boolean available){if(loadState==LOAD_RUNNING)loadState=available?LOAD_READY:LOAD_FAILED;}
    boolean loadFailed(){return loadState==LOAD_FAILED;}
    boolean loadReady(){return loadState==LOAD_READY;}
    void resetPlayback(){elapsedMs=0;runningSince=-1;}
    void setRunning(boolean value,long now){
        if(value){if(runningSince<0)runningSince=now;}
        else if(runningSince>=0){elapsedMs+=Math.max(0,now-runningSince);runningSince=-1;}
    }
    int frameTime(long now,int duration){
        int safe=Math.max(1,duration);long elapsed=elapsedMs+(runningSince<0?0:Math.max(0,now-runningSince));
        return (int)(elapsed%safe);
    }
    boolean shouldContinue(){return runningSince>=0;}
}
