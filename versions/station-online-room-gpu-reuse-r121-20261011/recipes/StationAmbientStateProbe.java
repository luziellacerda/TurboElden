package org.emulationstation.frontend.netplay;

public final class StationAmbientStateProbe {
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    public static void main(String[] args){
        check(StationHyperspaceState.renderWidth(2400,1080)==1280,"2400x1080 width");
        check(StationHyperspaceState.renderHeight(2400,1080)==576,"2400x1080 height");
        check(StationHyperspaceState.renderWidth(1280,720)==1280,"native width");
        check(StationHyperspaceState.renderHeight(1280,720)==720,"native height");
        check(StationHyperspaceState.renderWidth(800,360)==800,"small width is not enlarged");
        check(StationHyperspaceState.renderWidth(0,1080)==1,"invalid width is bounded");

        System.out.println("Station static ambient state probe: PASS");
    }
}
