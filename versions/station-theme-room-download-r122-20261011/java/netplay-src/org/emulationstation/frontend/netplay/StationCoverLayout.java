package org.emulationstation.frontend.netplay;

/** Presentation geometry uses the space this view received, never the whole display. */
final class StationCoverLayout {
    static final class Size {
        final int width,height;
        Size(int width,int height){this.width=width;this.height=height;}
    }
    static float aspect(float value){return Float.isNaN(value)||Float.isInfinite(value)||value<=0?2f/3f:value;}
    static int gap(int preferred,int available,int occupied){return Math.min(Math.max(0,preferred),Math.max(0,available-Math.max(0,occupied)));}
    static Size fit(int maximumWidth,int maximumHeight,float imageAspect){
        int w=Math.max(0,maximumWidth),h=Math.max(0,maximumHeight);
        if(w==0||h==0)return new Size(0,0);
        double ratio=aspect(imageAspect);
        if(w/ratio>h)w=Math.max(1,(int)Math.floor(h*ratio));
        else h=Math.max(1,(int)Math.floor(w/ratio));
        return new Size(w,h);
    }
    static Size hero(int availableWidth,int availableHeight,float imageAspect,int minimumContent,int gap,int maximumWidth){
        int width=Math.max(0,availableWidth),height=Math.max(0,availableHeight);
        int reserve=Math.min(Math.max(0,minimumContent),(int)(width*.64f));
        int artWidth=Math.min(Math.max(0,maximumWidth),(int)(width*.30f));
        artWidth=Math.min(artWidth,Math.max(0,width-reserve-Math.max(0,gap)));
        return fit(artWidth,(int)(height*.86f),imageAspect);
    }
    static Size thumbnail(int availableWidth,float imageAspect,int maximumWidth,int maximumHeight,int gap){
        int width=Math.max(0,availableWidth);
        int artWidth=Math.min(Math.max(0,maximumWidth),(int)(width*.28f));
        artWidth=Math.min(artWidth,Math.max(0,width-Math.max(0,gap)));
        return fit(artWidth,maximumHeight,imageAspect);
    }
    // Kept for package-local callers outside these three surfaces.
    static int preferredWidth(int availableHeight){return Math.max(1,Math.round(Math.max(0,availableHeight)*.30f));}
    static int width(int availableHeight,int available,int minimumContent,int gap){
        return Math.max(1,Math.min(preferredWidth(availableHeight),Math.max(0,available-minimumContent-gap)));
    }
    static int height(int width,float imageAspect){return Math.max(1,Math.round(Math.max(0,width)/aspect(imageAspect)));}
}
