package org.emulationstation.frontend;

import android.app.Activity;
import android.app.Application;
import android.content.res.AssetFileDescriptor;
import android.graphics.SurfaceTexture;
import android.media.MediaCodecInfo;
import android.media.MediaCodecList;
import android.media.MediaPlayer;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.util.Log;
import android.view.Surface;
import java.util.HashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReferenceArray;

/** One 720p source per clip; neighbouring offscreen clips stay prepared and paused. */
public final class SystemCardVideo720 {
    private static final String TAG="TurboVideo720";
    private static final int SLOTS=12;
    private static final AtomicReferenceArray<Session> active=new AtomicReferenceArray<>(SLOTS);
    private static Handler worker;
    private static boolean registered,searched;
    private static volatile boolean foreground=true;
    private static volatile int capacity=12;
    private static int players;
    private static final HashMap<String,Integer> resumePositions=new HashMap<>(); // Worker only, bounded by packaged clips.
    private static final class Session {
        final int slot;
        final String asset;
        final SurfaceTexture texture;
        final Surface surface;
        final AtomicBoolean frame=new AtomicBoolean();
        volatile boolean valid=true,failed,hasFrame,visible;
        volatile long lastDraw=SystemClock.uptimeMillis(),lastFrame=SystemClock.uptimeMillis();
        boolean surfacesReleased,counted,prepared,parked;
        long startedAt;
        MediaPlayer player; // Worker only.
        Session(int slot,int textureId,String asset,boolean visible){
            this.slot=slot;this.asset=asset;this.visible=visible;
            texture=new SurfaceTexture(textureId);texture.setDefaultBufferSize(720,720);
            surface=new Surface(texture);
        }
    }
    private static synchronized Handler worker(){
        if(worker==null){HandlerThread t=new HandlerThread("SystemVideo720");t.start();worker=new Handler(t.getLooper());}
        return worker;
    }
    public static int capacity(){return capacity;}
    private static boolean current(Session s){return foreground&&s.valid&&active.get(s.slot)==s;}
    private static synchronized void register(Activity a){
        if(registered)return;
        a.getApplication().registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
            private boolean frontend(Activity x){return x.getClass().getName().equals("org.emulationstation.frontend.ESActivity");}
            public void onActivityResumed(Activity x){foreground=frontend(x);if(!foreground)stopAll();}
            public void onActivityPaused(Activity x){if(frontend(x)){foreground=false;stopAll();}}
            public void onActivityStopped(Activity x){if(frontend(x))stopAll();}
            public void onActivityDestroyed(Activity x){if(frontend(x))stopAll();}
            public void onActivityCreated(Activity x,Bundle b){}
            public void onActivityStarted(Activity x){}
            public void onActivitySaveInstanceState(Activity x,Bundle b){}
        });registered=true;
    }
    private static void chooseCapacity(){
        if(searched)return;searched=true;int best=0;
        for(MediaCodecInfo info:new MediaCodecList(MediaCodecList.REGULAR_CODECS).getCodecInfos()){
            if(info.isEncoder())continue;
            String n=info.getName().toLowerCase(java.util.Locale.ROOT);
            boolean hw=Build.VERSION.SDK_INT>=29?info.isHardwareAccelerated():!n.startsWith("omx.google.")&&!n.startsWith("c2.android.")&&!n.startsWith("c2.google.");
            if(!hw||n.endsWith(".secure"))continue;
            try{
                MediaCodecInfo.CodecCapabilities c=info.getCapabilitiesForType("video/avc");
                if(c.getVideoCapabilities().areSizeAndRateSupported(720,720,60))best=Math.max(best,Math.min(SLOTS,c.getMaxSupportedInstances()));
            }catch(IllegalArgumentException ignored){}
        }
        capacity=best;Log.i(TAG,"Single-source 720p60 capacity="+capacity+"; no atlas/alternate video");
    }
    public static boolean start(Activity a,int slot,int texture,String asset,boolean visible){
        if(slot<0||slot>=SLOTS||a==null||!foreground||a.isFinishing()||!a.hasWindowFocus())return false;
        if(asset==null||!asset.startsWith("turbo-system-videos/720-")||asset.contains(".."))return false;
        register(a);stop(slot);
        final Handler h=worker();final Session s;
        try{s=new Session(slot,texture,asset,visible);}catch(RuntimeException e){return false;}
        active.set(slot,s);
        s.texture.setOnFrameAvailableListener(st->{if(current(s)){
            s.lastFrame=SystemClock.uptimeMillis();s.frame.set(true);
            if(!s.visible&&s.prepared&&!s.parked){
                try{s.player.pause();s.parked=true;Log.i(TAG,"Ready offscreen: "+s.asset);}catch(RuntimeException e){fail(s,e);}
            }
        }},h);
        final android.content.res.AssetManager assets=a.getApplicationContext().getAssets();
        h.post(()->{
            if(!current(s)){release(s);return;}
            try{
                chooseCapacity();if(players>=capacity)throw new IllegalStateException("No free video capacity");
                MediaPlayer player=new MediaPlayer();s.player=player;players++;s.counted=true;
                player.setSurface(s.surface);player.setVolume(0f,0f);
                player.setOnErrorListener((mp,what,extra)->{fail(s,new IllegalStateException("MediaPlayer "+what+"/"+extra));return true;});
                player.setOnPreparedListener(mp->{
                    if(!current(s)){release(s);return;}
                    try{
                        Integer position=resumePositions.get(s.asset);
                        if(position!=null&&position>0){
                            mp.setOnSeekCompleteListener(done->{done.setOnSeekCompleteListener(null);beginPlayback(s,done);});
                            mp.seekTo((long)position,MediaPlayer.SEEK_CLOSEST);
                        }else beginPlayback(s,mp);
                    }catch(RuntimeException e){fail(s,e);}
                });
                player.setOnCompletionListener(mp->{
                    if(!current(s)||!s.visible)return;
                    try{mp.seekTo(0);mp.start();}catch(RuntimeException e){fail(s,e);}
                });
                try(AssetFileDescriptor fd=assets.openFd(s.asset)){player.setDataSource(fd.getFileDescriptor(),fd.getStartOffset(),fd.getLength());}
                player.prepareAsync();s.startedAt=SystemClock.uptimeMillis();
                h.postDelayed(new Runnable(){public void run(){
                    if(!current(s))return;
                    long now=SystemClock.uptimeMillis();
                    if(now-s.lastDraw>3000){active.compareAndSet(s.slot,s,null);s.valid=false;release(s);return;}
                    if(!s.prepared&&now-s.startedAt>15000){fail(s,new IllegalStateException("Video preparation timeout"));return;}
                    if(s.prepared&&s.visible&&!s.parked&&now-s.lastFrame>4000){
                        // Recover this same stream; never substitute a second/lower-resolution video.
                        try{s.lastFrame=now;s.player.seekTo(0);s.player.start();Log.w(TAG,"Recovering the same 720p loop: "+s.asset);}
                        catch(RuntimeException e){fail(s,e);return;}
                    }
                    h.postDelayed(this,300);
                }},300);
            }catch(Exception e){fail(s,e);}
        });return true;
    }
    private static void beginPlayback(Session s,MediaPlayer mp){
        if(!current(s)){release(s);return;}
        try{
            mp.setLooping(true);mp.setVolume(0f,0f);mp.start();
            mp.setPlaybackParams(mp.getPlaybackParams().setSpeed(1.0f).setPitch(1.0f));
            s.prepared=true;s.startedAt=SystemClock.uptimeMillis();s.lastFrame=s.startedAt;
            Log.i(TAG,"720p loop ready at retained position: "+s.asset);
        }catch(RuntimeException e){fail(s,e);}
    }
    // Keep the same player, texture and decoded frame when a neighbouring card
    // leaves the viewport. Pause offscreen; resume without reopen/prepare/seek.
    public static void setVisible(int slot,boolean visible){
        if(slot<0||slot>=SLOTS)return;Session s=active.get(slot);
        if(s==null||s.visible==visible)return;s.visible=visible;
        worker().post(()->{
            if(!current(s)||!s.prepared||s.visible!=visible)return;
            try{
                if(visible&&s.parked){s.lastFrame=SystemClock.uptimeMillis();s.player.start();s.parked=false;Log.i(TAG,"Resume ready video: "+s.asset);}
                else if(!visible&&!s.parked&&s.hasFrame){s.player.pause();s.parked=true;}
            }catch(RuntimeException e){fail(s,e);}
        });
    }
    private static void fail(Session s,Exception e){
        if(s.failed)return;s.failed=true;s.valid=false;Log.w(TAG,"720p stream error: "+s.asset,e);
        worker().post(()->release(s));
    }
    public static int update(int slot,float[] transform){
        if(slot<0||slot>=SLOTS)return -1;Session s=active.get(slot);
        if(s==null)return -1;if(s.failed)return -2;if(!current(s))return -1;
        s.lastDraw=SystemClock.uptimeMillis();
        synchronized(s){
            if(!current(s))return -1;
            try{
                if(s.frame.getAndSet(false)){s.texture.updateTexImage();if(s.prepared)s.hasFrame=true;}
                if(s.hasFrame)s.texture.getTransformMatrix(transform);
                return s.hasFrame?1:0;
            }catch(RuntimeException e){s.failed=true;s.valid=false;worker().post(()->release(s));return -2;}
        }
    }
    public static void stop(int slot){
        if(slot<0||slot>=SLOTS)return;Session s=active.getAndSet(slot,null);if(s==null)return;
        s.valid=false;releaseSurfaces(s);worker().post(()->release(s));
    }
    public static void stopAll(){for(int i=0;i<SLOTS;i++)stop(i);}
    private static void releaseSurfaces(Session s){synchronized(s){
        if(s.surfacesReleased)return;s.surfacesReleased=true;s.hasFrame=false;
        try{s.surface.release();s.texture.release();}catch(RuntimeException ignored){}
    }}
    private static void release(Session s){
        MediaPlayer p=s.player;s.player=null;
        if(p!=null){
            if(s.prepared){try{resumePositions.put(s.asset,p.getCurrentPosition());}catch(RuntimeException ignored){}}
            try{p.setOnSeekCompleteListener(null);p.setOnPreparedListener(null);p.setOnCompletionListener(null);p.setOnErrorListener(null);p.release();}catch(RuntimeException ignored){}}
        if(s.counted){s.counted=false;players--;}
        releaseSurfaces(s);
    }
}
