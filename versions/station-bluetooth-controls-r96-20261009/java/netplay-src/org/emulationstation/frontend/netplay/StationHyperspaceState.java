package org.emulationstation.frontend.netplay;

/** Clock advances exclusively while the online screen is visible and resumed. */
final class StationHyperspaceState {
    private boolean active;
    private long previous=-1;
    private float seconds;
    static boolean mayRun(boolean resumed,boolean attached,boolean shown,boolean windowVisible,boolean focused,boolean animationsEnabled){
        return resumed&&attached&&shown&&windowVisible&&focused&&animationsEnabled;
    }
    void setActive(boolean value){if(active!=value){active=value;previous=-1;}}
    boolean isActive(){return active;}
    boolean advance(long now){
        if(!active)return false;
        if(previous>=0){long delta=Math.max(0,Math.min(67,now-previous));seconds=(seconds+delta*.001f)%120f;}
        previous=now;return true;
    }
    float seconds(){return seconds;}
}
