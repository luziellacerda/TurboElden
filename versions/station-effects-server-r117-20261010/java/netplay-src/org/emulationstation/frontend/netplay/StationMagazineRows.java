package org.emulationstation.frontend.netplay;

/** Four disjoint row parcels with the same order as the native field builder. */
final class StationMagazineRows {
    private static final int[] ORDER={2,3,1,0},ART_Y={1454,1010,565,80};
    private final int[] seed=new int[4];
    private int height,ordinal,done;
    void reset(int h,float coverBottom,float coverHeight){
        height=h;ordinal=done=0;
        for(int q=0;q<4;q++){
            int lo=q*h/4,hi=(q+1)*h/4;
            int first=(int)(coverBottom+(1536-ART_Y[q])*coverHeight/1536f);
            seed[q]=hi>lo?Math.max(lo,Math.min(hi-1,first)):lo;
        }
    }
    int next(){
        if(done>=height)return -1;
        for(;;){
            int q=ORDER[ordinal%4],step=ordinal/4;ordinal++;
            int lo=q*height/4,span=(q+1)*height/4-lo;
            if(step>=span)continue;
            done++;return lo+(seed[q]-lo+step)%span;
        }
    }
    int done(){return done;}
}
