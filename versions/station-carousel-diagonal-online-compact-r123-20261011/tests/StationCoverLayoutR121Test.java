package org.emulationstation.frontend.netplay;

/** Pure presentation arithmetic; this does not run Android layout or emulation. */
public final class StationCoverLayoutR121Test {
    private static int checks,cases;
    private static void check(boolean value,String label){checks++;if(!value)throw new AssertionError(label);}
    private static void bounded(StationCoverLayout.Size size,int width,int height,float aspect){
        check(size.width>=0&&size.height>=0,"nonnegative size");
        check(size.width<=Math.max(0,width)&&size.height<=Math.max(0,height),"received bounds");
        if(size.width>0&&size.height>0){double ratio=StationCoverLayout.aspect(aspect);
            check(Math.abs(size.width/ratio-size.height)<=Math.max(1,1/ratio)+.001,"aspect rounding within one pixel");}
    }
    public static void main(String[] args){
        int[] widths={0,1,8,48,180,240,320,412,576,640,720,960,1080,1280};
        int[] heights={0,1,48,90,128,200,280,400,640};
        float[] densities={.75f,1,1.33f,2,2.75f,3.5f};
        float[] aspects={2f/3f,.5625f,.75f,1,1.3333f,1.5f,2,1f/8192,8192,0,-1,Float.NaN,Float.POSITIVE_INFINITY};
        for(int logicalWidth:widths)for(int logicalHeight:heights)for(float density:densities)for(float aspect:aspects){
            cases++;
            int width=Math.round(logicalWidth*density),height=Math.round(logicalHeight*density),gap=Math.min(Math.round(12*density),width);
            int minimum=Math.round(280*density),maximum=Math.round(224*density);
            StationCoverLayout.Size hero=StationCoverLayout.hero(width,height,aspect,minimum,gap,maximum);
            bounded(hero,(int)(width*.30f),(int)(height*.86f),aspect);
            check(hero.width<=maximum,"hero maximum");
            int textWidth=Math.max(0,width-hero.width-gap),reserve=Math.min(minimum,(int)(width*.64f));
            check(textWidth>=Math.min(reserve,width-gap),"content remains available");
            StationCoverLayout.Size thumb=StationCoverLayout.thumbnail(width,aspect,Math.round(76*density),Math.round(112*density),gap);
            bounded(thumb,Math.min((int)(width*.28f),Math.round(76*density)),Math.round(112*density),aspect);
            check(thumb.width+gap<=width,"list columns fit");
            StationCoverLayout.Size flow=StationCoverLayout.hero(width,height,aspect,minimum,gap,Math.round(184*density));
            bounded(flow,(int)(width*.30f),(int)(height*.86f),aspect);
            StationCoverLayout.Size stacked=StationCoverLayout.fit(Math.min((int)(width*.38f),Math.round(120*density)),Math.min(Math.round(130*density),height/3),aspect);
            int stackGap=StationCoverLayout.gap(Math.round(12*density),height,stacked.height);
            bounded(stacked,width,height/3,aspect);
            check(stacked.height+stackGap<=height,"stack preserves content height");
        }
        StationCoverLayout.Size a=StationCoverLayout.thumbnail(640,2f/3f,76,112,12);
        check(a.width==74&&a.height==112,"portrait room thumbnail 74x112");
        StationCoverLayout.Size b=StationCoverLayout.hero(640,280,2f/3f,280,12,224);
        check(b.width==160&&b.height==240,"portrait hero uses received height");
        StationCoverLayout.Size c=StationCoverLayout.hero(640,200,2f/3f,280,12,224);
        check(c.width<b.width&&c.height<b.height,"smaller viewport shrinks art");
        check(StationCoverLayout.aspect(Float.NaN)==2f/3f,"invalid ratio fallback");
        System.out.println("PASS checks="+checks+" cases="+cases);
    }
}
