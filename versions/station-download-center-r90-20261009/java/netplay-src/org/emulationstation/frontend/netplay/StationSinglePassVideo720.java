package org.emulationstation.frontend.netplay;

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
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReferenceArray;

/** Focused 720p30 clip, one pass. Native retains the image two frames before the last frame, then stop(). */
public final class StationSinglePassVideo720 {
    private static final int SLOTS=4;
    private static final String TAG="StationVideoOnce";
    private static final AtomicReferenceArray<Session> active=new AtomicReferenceArray<>(SLOTS);
    private static Handler handler;
    private static boolean registered,searched,watchdogQueued;
    private static volatile boolean foreground=true;
    private static volatile int decoderCapacity=1;
    private static int players;

    private static final class Session {
        final int slot; final String asset;
        final SurfaceTexture texture; final Surface surface;
        final AtomicBoolean frame=new AtomicBoolean();
        volatile boolean valid=true,failed,hasFrame,visible,completed,finishing,keepPreviousFrame;
        volatile long lastDraw=SystemClock.uptimeMillis(),lastFrame=lastDraw,completionAt;
        boolean prepared,parked,counted,surfacesReleased;
        long startedAt,holdPosition;
        Runnable endCheck,seekTimeout;
        MediaPlayer player; // Only the worker touches MediaPlayer.
        Session(int slot,int textureId,String asset,boolean visible){
            this.slot=slot;this.asset=asset;this.visible=visible;
            texture=new SurfaceTexture(textureId);texture.setDefaultBufferSize(720,720);
            surface=new Surface(texture);
        }
    }
    private static synchronized Handler worker(){
        if(handler==null){HandlerThread t=new HandlerThread("StationVideoOnce");t.start();handler=new Handler(t.getLooper());}
        return handler;
    }
    public static int capacity(){return decoderCapacity;}
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
            String name=info.getName().toLowerCase(java.util.Locale.ROOT);
            boolean hardware=Build.VERSION.SDK_INT>=29?info.isHardwareAccelerated():!name.startsWith("omx.google.")&&!name.startsWith("c2.android.")&&!name.startsWith("c2.google.");
            if(!hardware||name.endsWith(".secure"))continue;
            try{if(info.getCapabilitiesForType("video/avc").getVideoCapabilities().areSizeAndRateSupported(720,720,30))best=1;}
            catch(IllegalArgumentException ignored){}
        }
        decoderCapacity=best;
    }
    private static final Runnable watchdog=new Runnable(){public void run(){
        watchdogQueued=false;long now=SystemClock.uptimeMillis();boolean any=false;
        for(int i=0;i<SLOTS;i++){
            Session s=active.get(i);if(s==null||!current(s))continue;
            if(now-s.lastDraw>3000){active.compareAndSet(i,s,null);s.valid=false;release(s);continue;}
            // Completion is terminal: never seek/start a completed clip.
            if(s.completed)continue;
            if(!s.hasFrame&&now-s.startedAt>15000){fail(s,"first frame timeout");continue;}
            if(s.prepared&&s.visible&&!s.parked&&now-s.lastFrame>4000){fail(s,"frame delivery stalled");continue;}
            any=true;
        }
        if(any)armWatchdog();
    }};
    private static void armWatchdog(){if(!watchdogQueued){watchdogQueued=true;worker().postDelayed(watchdog,1000);}}
    private static void stopWatchdogIfIdle(){
        for(int i=0;i<SLOTS;i++){Session s=active.get(i);if(s!=null&&current(s)&&!s.completed)return;}
        worker().removeCallbacks(watchdog);watchdogQueued=false;
    }
    private static void completeHold(Session s){
        if(!current(s)||s.completed)return;
        s.completionAt=SystemClock.uptimeMillis();s.completed=true;
        if(s.seekTimeout!=null)worker().removeCallbacks(s.seekTimeout);
        stopWatchdogIfIdle();Log.i(TAG,"Hold ready two frames early: "+s.asset);
    }
    private static void finishEarly(Session s,boolean playbackEnded){
        if(!current(s)||s.completed||s.finishing)return;
        s.finishing=true;if(s.endCheck!=null)worker().removeCallbacks(s.endCheck);
        try{
            if(!playbackEnded)s.player.pause();s.parked=true;
            // SEEK_CLOSEST selects a decoded frame, not merely the prior keyframe.
            // The renderer holds its current image until the seek callback.
            s.seekTimeout=()->{if(current(s)&&!s.completed){s.keepPreviousFrame=true;s.frame.set(false);completeHold(s);Log.w(TAG,"End-frame seek timed out; previous image retained");}};
            worker().postDelayed(s.seekTimeout,1500);
            s.player.seekTo(s.holdPosition,MediaPlayer.SEEK_CLOSEST);
            Log.i(TAG,"End-frame requested at "+s.holdPosition+"ms: "+s.asset);
        }catch(RuntimeException e){s.keepPreviousFrame=true;completeHold(s);}
    }
    private static void scheduleEnd(Session s){
        if(s.endCheck==null)s.endCheck=()->{
            if(!current(s)||s.completed||s.finishing||s.parked||!s.visible)return;
            try{long remaining=s.holdPosition-s.player.getCurrentPosition();
                if(remaining>0)worker().postDelayed(s.endCheck,remaining);
                else finishEarly(s,false);
            }catch(RuntimeException e){fail(s,"end-frame timing failed");}
        };
        worker().removeCallbacks(s.endCheck);
        try{worker().postDelayed(s.endCheck,Math.max(1L,s.holdPosition-s.player.getCurrentPosition()));}
        catch(RuntimeException e){fail(s,"end-frame scheduling failed");}
    }
    public static boolean start(Activity a,int slot,int textureId,String asset,boolean visible){
        if(slot<0||slot>=SLOTS||a==null||!foreground||a.isFinishing()||!a.hasWindowFocus())return false;
        if(asset==null||!asset.startsWith("turbo-system-videos/720-")||asset.contains(".."))return false;
        register(a);stopAll(); // Queued releases precede the queued new player.
        final Handler h=worker();final Session s;
        try{s=new Session(slot,textureId,asset,visible);}catch(RuntimeException e){return false;}
        active.set(slot,s);
        s.texture.setOnFrameAvailableListener(st->{
            if(!current(s))return;s.lastFrame=SystemClock.uptimeMillis();s.frame.set(true);
            if(!s.visible&&s.prepared&&!s.parked&&!s.completed){
                try{s.player.pause();s.parked=true;}catch(RuntimeException e){fail(s,"pause failed");}
            }
        },h);
        final android.content.res.AssetManager assets=a.getApplicationContext().getAssets();
        h.post(()->{
            if(!current(s)){release(s);return;}
            try{
                chooseCapacity();if(players>=decoderCapacity)throw new IllegalStateException("decoder capacity");
                MediaPlayer player=new MediaPlayer();s.player=player;players++;s.counted=true;
                player.setSurface(s.surface);player.setVolume(0f,0f);player.setLooping(false);
                player.setOnErrorListener((mp,what,extra)->{if(current(s))fail(s,"decoder "+what+"/"+extra);return true;});
                player.setOnPreparedListener(mp->{
                    if(!current(s)){release(s);return;}
                    try{s.holdPosition=StationVideoEndFrame.positionMs(mp.getDuration());mp.setLooping(false);mp.start();s.prepared=true;s.lastFrame=SystemClock.uptimeMillis();scheduleEnd(s);Log.i(TAG,"Playing once: "+s.asset);}
                    catch(RuntimeException e){fail(s,"start failed");}
                });
                player.setOnSeekCompleteListener(mp->{if(current(s)&&s.finishing)completeHold(s);});
                player.setOnCompletionListener(mp->{if(current(s))finishEarly(s,true);});
                try(AssetFileDescriptor fd=assets.openFd(s.asset)){player.setDataSource(fd.getFileDescriptor(),fd.getStartOffset(),fd.getLength());}
                s.startedAt=SystemClock.uptimeMillis();player.prepareAsync();armWatchdog();
            }catch(Exception e){fail(s,"prepare failed");}
        });return true;
    }
    public static void setVisible(int slot,boolean visible){
        if(slot<0||slot>=SLOTS)return;Session s=active.get(slot);if(s==null||s.visible==visible)return;s.visible=visible;
        worker().post(()->{
            if(!current(s)||!s.prepared||s.completed||s.finishing||s.visible!=visible)return;
            try{if(visible&&s.parked){s.player.start();s.parked=false;s.lastFrame=SystemClock.uptimeMillis();armWatchdog();scheduleEnd(s);}
                else if(!visible&&!s.parked&&s.hasFrame){s.player.pause();s.parked=true;}}
            catch(RuntimeException e){fail(s,"visibility failed");}
        });
    }
    private static void fail(Session s,String reason){
        if(s.failed)return;s.failed=true;s.valid=false;Log.w(TAG,reason);release(s);
    }
    // 0=preparing, 1=image, 2=final image, 3=completed without image, negative=error.
    public static int update(int slot,float[] transform){
        if(slot<0||slot>=SLOTS||transform==null||transform.length<16)return -1;
        Session s=active.get(slot);if(s==null)return -1;if(s.failed)return -2;if(!current(s))return -1;
        s.lastDraw=SystemClock.uptimeMillis();
        synchronized(s){
            if(!current(s))return -1;
            try{
                if(!s.keepPreviousFrame&&(!s.finishing||s.completed)&&s.frame.getAndSet(false)){s.texture.updateTexImage();s.hasFrame=true;}
                if(s.hasFrame)s.texture.getTransformMatrix(transform);
                if(s.completed&&SystemClock.uptimeMillis()-s.completionAt>=50)return s.hasFrame?2:3;
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
        if(s.endCheck!=null)worker().removeCallbacks(s.endCheck);
        if(s.seekTimeout!=null)worker().removeCallbacks(s.seekTimeout);
        MediaPlayer p=s.player;s.player=null;
        if(p!=null){try{p.setOnPreparedListener(null);p.setOnCompletionListener(null);p.setOnSeekCompleteListener(null);p.setOnErrorListener(null);p.release();}catch(RuntimeException ignored){}}
        if(s.counted){s.counted=false;players--;Log.i(TAG,"Decoder released; active="+players);}
        releaseSurfaces(s);stopWatchdogIfIdle();
    }
}
