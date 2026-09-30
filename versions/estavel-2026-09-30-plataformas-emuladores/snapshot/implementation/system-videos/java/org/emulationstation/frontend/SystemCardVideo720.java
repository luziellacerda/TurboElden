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

/** One focused 720p30 loop; three warm players plus one transient preview decoder. */
public final class SystemCardVideo720 {
    private static final String TAG="TurboVideo720";
    private static final int SLOTS=4;
    private static final AtomicReferenceArray<Session> active=new AtomicReferenceArray<>(SLOTS);
    private static Handler worker;
    private static boolean registered,searched;
    private static volatile boolean foreground=true;
    private static volatile int capacity=SLOTS;
    private static int players; // Worker only, includes release operations still queued.
    private static boolean watchdogQueued; // Worker only; exactly one scheduled callback.
    private static long watchdogDueAt;
    private static final HashMap<String,Integer> resumePositions=new HashMap<>();
    private static final class Session {
        final int slot;
        final String asset;
        final SurfaceTexture texture;
        final Surface surface;
        final AtomicBoolean frame=new AtomicBoolean();
        volatile boolean valid=true,failed,hasFrame,visible;
        volatile long lastDraw=SystemClock.uptimeMillis(),lastFrame=SystemClock.uptimeMillis();
        boolean surfacesReleased,counted,prepared,parked;
        long startedAt,nextWatchdogAt;
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
                if(c.getVideoCapabilities().areSizeAndRateSupported(720,720,30))best=Math.max(best,Math.min(SLOTS,c.getMaxSupportedInstances()));
            }catch(IllegalArgumentException ignored){}
        }
        capacity=best;Log.i(TAG,"Focus-only 720p30 decoder budget="+capacity+"; warm3+scratch1");
    }
    // This callback, its scheduling flag, player operations and nextWatchdogAt
    // are worker-owned. Invalidated generations are never resumed or rearmed.
    private static final Runnable watchdog=new Runnable(){public void run(){
        watchdogQueued=false;
        long now=SystemClock.uptimeMillis(),nextDelay=3000;
        boolean any=false;
        for(int i=0;i<SLOTS;i++){
            Session s=active.get(i);if(s==null||!current(s))continue;
            boolean parked=s.prepared&&s.parked&&s.hasFrame&&!s.visible;
            if(now>=s.nextWatchdogAt){
                if(now-s.lastDraw>3000){
                    active.compareAndSet(s.slot,s,null);s.valid=false;release(s);continue;
                }
                // Include prepare, seek completion and first-frame delivery.
                if(!s.hasFrame&&now-s.startedAt>15000){
                    fail(s,new IllegalStateException("Video first-frame timeout"));continue;
                }
                if(s.prepared&&s.visible&&!s.parked&&now-s.lastFrame>4000){
                    try{s.lastFrame=now;s.player.seekTo(0);s.player.start();Log.w(TAG,"Recovering the same 720p loop: "+s.asset);}
                    catch(RuntimeException e){fail(s,e);continue;}
                }
                s.nextWatchdogAt=now+(parked?3000:1000);
            }
            any=true;nextDelay=Math.min(nextDelay,Math.max(1,s.nextWatchdogAt-now));
        }
        if(any){watchdogQueued=true;watchdogDueAt=now+nextDelay;worker().postDelayed(this,nextDelay);}
    }};
    private static void armWatchdog(){ // Worker only. New/resumed sessions get a check within 1s.
        long due=SystemClock.uptimeMillis()+1000;
        if(watchdogQueued&&watchdogDueAt<=due)return;
        Handler h=worker();h.removeCallbacks(watchdog);watchdogQueued=true;watchdogDueAt=due;h.postDelayed(watchdog,1000);
    }
    private static void stopWatchdogIfIdle(){ // Worker only.
        for(int i=0;i<SLOTS;i++){Session s=active.get(i);if(s!=null&&current(s))return;}
        if(watchdogQueued){worker().removeCallbacks(watchdog);watchdogQueued=false;}
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
                try{s.player.pause();s.parked=true;s.nextWatchdogAt=s.lastFrame+3000;Log.i(TAG,"Ready offscreen: "+s.asset);}catch(RuntimeException e){fail(s,e);}
            }
        }},h);
        final android.content.res.AssetManager assets=a.getApplicationContext().getAssets();
        h.post(()->{
            if(!current(s)){release(s);return;}
            try{
                chooseCapacity();if(players>=capacity)throw new IllegalStateException("No free video capacity");
                MediaPlayer player=new MediaPlayer();s.player=player;players++;s.counted=true;
                player.setSurface(s.surface);player.setVolume(0f,0f);
                player.setOnErrorListener((mp,what,extra)->{if(current(s))fail(s,new IllegalStateException("MediaPlayer "+what+"/"+extra));return true;});
                player.setOnPreparedListener(mp->{
                    if(!current(s)){release(s);return;}
                    try{
                        Integer position=resumePositions.get(s.asset);
                        if(position!=null&&position>0){
                            mp.setOnSeekCompleteListener(done->{
                                if(!current(s)){release(s);return;}
                                try{done.setOnSeekCompleteListener(null);beginPlayback(s,done);}
                                catch(RuntimeException e){fail(s,e);}
                            });
                            mp.seekTo((long)position,MediaPlayer.SEEK_CLOSEST);
                        }else beginPlayback(s,mp);
                    }catch(RuntimeException e){fail(s,e);}
                });
                player.setOnCompletionListener(mp->{
                    if(!current(s)||!s.visible)return;
                    try{mp.seekTo(0);mp.start();}catch(RuntimeException e){fail(s,e);}
                });
                try(AssetFileDescriptor fd=assets.openFd(s.asset)){player.setDataSource(fd.getFileDescriptor(),fd.getStartOffset(),fd.getLength());}
                s.startedAt=SystemClock.uptimeMillis();s.nextWatchdogAt=s.startedAt+1000;
                player.prepareAsync();armWatchdog();
            }catch(Exception e){fail(s,e);}
        });return true;
    }
    private static void beginPlayback(Session s,MediaPlayer mp){
        if(!current(s)){release(s);return;}
        try{
            mp.setLooping(true);mp.setVolume(0f,0f);mp.start();
            mp.setPlaybackParams(mp.getPlaybackParams().setSpeed(1.0f).setPitch(1.0f));
            s.prepared=true;s.lastFrame=SystemClock.uptimeMillis();s.nextWatchdogAt=s.lastFrame+1000;
            Log.i(TAG,"720p30 focused/preview video ready: "+s.asset);
        }catch(RuntimeException e){fail(s,e);}
    }
    public static void setVisible(int slot,boolean visible){
        if(slot<0||slot>=SLOTS)return;Session s=active.get(slot);
        if(s==null||s.visible==visible)return;s.visible=visible;
        worker().post(()->{
            if(!current(s)||!s.prepared||s.visible!=visible)return;
            try{
                if(visible&&s.parked){s.lastFrame=SystemClock.uptimeMillis();s.player.start();s.parked=false;Log.i(TAG,"Resume ready video: "+s.asset);}
                else if(!visible&&!s.parked&&s.hasFrame){s.player.pause();s.parked=true;}
                s.nextWatchdogAt=SystemClock.uptimeMillis()+(s.parked?3000:1000);
                if(visible)armWatchdog();
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
        try{s.texture.setOnFrameAvailableListener(null);}catch(RuntimeException ignored){}
        try{s.surface.release();}catch(RuntimeException ignored){}
        try{s.texture.release();}catch(RuntimeException ignored){}
    }}
    private static void release(Session s){
        MediaPlayer p=s.player;s.player=null;
        if(p!=null){
            if(s.prepared){try{resumePositions.put(s.asset,p.getCurrentPosition());}catch(RuntimeException ignored){}}
            try{p.setOnSeekCompleteListener(null);p.setOnPreparedListener(null);p.setOnCompletionListener(null);p.setOnErrorListener(null);p.release();}catch(RuntimeException ignored){}}
        if(s.counted){s.counted=false;players--;}
        releaseSurfaces(s);stopWatchdogIfIdle();
    }
}
