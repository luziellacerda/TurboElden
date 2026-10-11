package org.emulationstation.frontend.netplay;

/** Same physical width as the R85 focused game cover; constrained only by available space. */
final class StationCoverLayout {
    static int preferredWidth(int screenHeight){return Math.max(1,Math.round(screenHeight*.790f*.828f));}
    static int width(int screenHeight,int available,int minimumActions,int gap){return Math.max(1,Math.min(preferredWidth(screenHeight),available-minimumActions-gap));}
    static int height(int width,float aspect){return Math.max(1,Math.round(width/Math.max(.1f,aspect)));}
}
