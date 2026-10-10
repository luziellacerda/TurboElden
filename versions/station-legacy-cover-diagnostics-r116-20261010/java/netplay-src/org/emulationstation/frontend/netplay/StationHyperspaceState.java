package org.emulationstation.frontend.netplay;

/** Pure sizing policy for the pre-rendered online background. */
final class StationHyperspaceState {
    private static final int MAX_RENDER_WIDTH=1280,MAX_RENDER_HEIGHT=720;
    private static float renderScale(int width,int height){
        if(width<=0||height<=0)return 1f;
        return Math.min(1f,Math.min(MAX_RENDER_WIDTH/(float)width,MAX_RENDER_HEIGHT/(float)height));
    }
    static int renderWidth(int width,int height){return width<=0||height<=0?1:Math.max(1,Math.round(width*renderScale(width,height)));}
    static int renderHeight(int width,int height){return width<=0||height<=0?1:Math.max(1,Math.round(height*renderScale(width,height)));}
}
