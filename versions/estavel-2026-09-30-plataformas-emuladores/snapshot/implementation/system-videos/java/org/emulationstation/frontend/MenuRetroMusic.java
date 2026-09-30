package org.emulationstation.frontend;

import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.AssetFileDescriptor;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.ArrayList;

/** One streaming music player, owned exclusively by the native menu lifecycle. */
public final class MenuRetroMusic {
    private static final String TAG="TurboRetroMusic";
    private static final ArrayList<String> assets=new ArrayList<>(),titles=new ArrayList<>();
    private static final AudioAttributes ATTRIBUTES=new AudioAttributes.Builder()
        .setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build();
    private static Handler worker;
    private static Context context;
    private static SharedPreferences preferences;
    private static AudioManager audio;
    private static AudioFocusRequest request;
    private static MediaPlayer player;
    private static boolean registered,prepared,hasFocus,focusBlocked,temporaryLoss,loaded,watching;
    private static volatile boolean foreground=true,enabled,gameSuspended;
    private static volatile long lastTick,lastDispatch;
    private static int track,position,failures;
    private static long lastSave,preparingAt;

    private static synchronized Handler worker(){
        if(worker==null){HandlerThread thread=new HandlerThread("RetroMenuMusic");thread.start();worker=new Handler(thread.getLooper());}
        return worker;
    }
    private static boolean allowed(){return foreground&&enabled&&!gameSuspended&&!focusBlocked&&!temporaryLoss;}
    private static synchronized void register(Activity activity){
        if(registered)return;
        context=activity.getApplicationContext();preferences=context.getSharedPreferences("turbo_retro_playlist",0);
        audio=(AudioManager)context.getSystemService(Context.AUDIO_SERVICE);
        activity.runOnUiThread(()->activity.setVolumeControlStream(AudioManager.STREAM_MUSIC));
        activity.getApplication().registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
            private boolean menu(Activity a){return a.getClass().getName().equals("org.emulationstation.frontend.ESActivity");}
            public void onActivityResumed(Activity a){
                foreground=menu(a);
                worker().post(()->{if(foreground){gameSuspended=false;focusBlocked=false;temporaryLoss=false;}else stopPlayback();});
            }
            public void onActivityPaused(Activity a){if(menu(a)){foreground=false;worker().post(()->stopPlayback());}}
            public void onActivityStopped(Activity a){if(menu(a))worker().post(()->stopPlayback());}
            public void onActivityDestroyed(Activity a){if(menu(a))worker().post(()->stopPlayback());}
            public void onActivityCreated(Activity a,Bundle b){}
            public void onActivityStarted(Activity a){}
            public void onActivitySaveInstanceState(Activity a,Bundle b){}
        });registered=true;
    }
    // Native calls at 5Hz. Loading/decoding/storage/focus all run off the GL thread.
    public static void tick(Activity activity,boolean on){
        if(activity==null||activity.isFinishing()||(!registered&&!activity.hasWindowFocus()))return;
        register(activity);
        long now=SystemClock.uptimeMillis(),previous=lastTick;lastTick=now;
        boolean changed=enabled!=on;enabled=on;
        if(gameSuspended&&previous>0&&now-previous>1800)gameSuspended=false;
        if(!changed&&now-lastDispatch<450)return;lastDispatch=now;
        boolean regain=changed&&on;
        worker().post(()->{
            if(regain){focusBlocked=false;temporaryLoss=false;gameSuspended=false;}
            if(!allowed()){if(!temporaryLoss)stopPlayback();return;}
            try{loadPlaylist();ensurePlayback();}catch(Exception e){Log.w(TAG,"Playlist unavailable",e);focusBlocked=true;stopPlayback();}
        });
    }
    public static void suspendForGame(){
        gameSuspended=true;
        worker().post(()->stopPlayback());
    }
    private static void loadPlaylist()throws Exception{
        if(loaded)return;
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        try(InputStream stream=context.getAssets().open("turbo-retro-music/playlist.json")){
            byte[] buffer=new byte[4096];int count;while((count=stream.read(buffer))!=-1)bytes.write(buffer,0,count);
        }
        JSONArray list=new JSONObject(bytes.toString("UTF-8")).getJSONArray("tracks");
        for(int i=0;i<list.length();i++){
            JSONObject item=list.getJSONObject(i);String asset=item.getString("asset");
            if(!asset.startsWith("turbo-retro-music/")||asset.contains(".."))throw new IllegalArgumentException("Invalid music asset");
            assets.add(asset);titles.add(item.getString("game")+" — "+item.getString("title"));
        }
        if(assets.isEmpty())throw new IllegalStateException("Empty playlist");
        track=Math.floorMod(preferences.getInt("track",0),assets.size());position=Math.max(0,preferences.getInt("position",0));loaded=true;
        request=new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN).setAudioAttributes(ATTRIBUTES)
            .setOnAudioFocusChangeListener(change->{
                if(change==AudioManager.AUDIOFOCUS_GAIN){hasFocus=true;temporaryLoss=false;if(allowed())ensurePlayback();}
                else if(change==AudioManager.AUDIOFOCUS_LOSS){hasFocus=false;focusBlocked=true;temporaryLoss=false;stopPlayback();}
                else {temporaryLoss=true;if(player!=null&&prepared){try{player.pause();savePosition();}catch(RuntimeException e){releasePlayer();}}}
            },worker()).setWillPauseWhenDucked(true).build();
        Log.i(TAG,"Local retro playlist loaded: "+assets.size()+" tracks; one streamed player");
    }
    private static void ensurePlayback(){
        if(!allowed()||assets.isEmpty()||failures>=assets.size())return;
        if(!hasFocus){
            if(audio==null||audio.requestAudioFocus(request)!=AudioManager.AUDIOFOCUS_REQUEST_GRANTED){focusBlocked=true;return;}
            hasFocus=true;
        }
        if(player!=null){
            if(prepared){try{if(!player.isPlaying())player.start();}catch(RuntimeException e){failCurrent(player,e);}}
            return;
        }
        final MediaPlayer current=new MediaPlayer();player=current;prepared=false;
        try{
            current.setAudioAttributes(ATTRIBUTES);current.setVolume(.32f,.32f);current.setLooping(false);
            current.setOnErrorListener((mp,what,extra)->{failCurrent(mp,new IllegalStateException("Audio "+what+"/"+extra));return true;});
            current.setOnPreparedListener(mp->{
                if(player!=mp||!allowed()){if(player==mp)stopPlayback();return;}
                try{
                    int duration=mp.getDuration(),resume=duration>0?position%duration:position;
                    if(resume>0){mp.setOnSeekCompleteListener(done->{done.setOnSeekCompleteListener(null);startPrepared(done);});mp.seekTo((long)resume,MediaPlayer.SEEK_CLOSEST);}
                    else startPrepared(mp);
                }catch(RuntimeException e){failCurrent(mp,e);}
            });
            current.setOnCompletionListener(mp->{
                if(player!=mp)return;releasePlayer();track=(track+1)%assets.size();position=0;saveSelection();ensurePlayback();
            });
            try(AssetFileDescriptor fd=context.getAssets().openFd(assets.get(track))){current.setDataSource(fd.getFileDescriptor(),fd.getStartOffset(),fd.getLength());}
            preparingAt=SystemClock.uptimeMillis();current.prepareAsync();scheduleWatchdog();
        }catch(Exception e){failCurrent(current,e);}
    }
    private static void startPrepared(MediaPlayer mp){
        if(player!=mp)return;if(!allowed()){stopPlayback();return;}
        try{prepared=true;failures=0;mp.start();lastSave=SystemClock.uptimeMillis();Log.i(TAG,"Playing: "+titles.get(track));}
        catch(RuntimeException e){failCurrent(mp,e);}
    }
    private static void saveSelection(){if(preferences!=null)preferences.edit().putInt("track",track).putInt("position",position).apply();}
    private static void savePosition(){
        if(player!=null&&prepared){try{position=player.getCurrentPosition();}catch(RuntimeException ignored){}}
        saveSelection();lastSave=SystemClock.uptimeMillis();
    }
    private static void releasePlayer(){
        MediaPlayer old=player;player=null;prepared=false;
        if(old!=null){try{old.setOnPreparedListener(null);old.setOnSeekCompleteListener(null);old.setOnCompletionListener(null);old.setOnErrorListener(null);old.release();}catch(RuntimeException ignored){}}
    }
    private static void stopPlayback(){
        if(player!=null)savePosition();releasePlayer();
        if(hasFocus&&audio!=null&&request!=null)audio.abandonAudioFocusRequest(request);hasFocus=false;
        if(worker!=null)worker.removeCallbacks(watchdog);watching=false;
    }
    private static void failCurrent(MediaPlayer failed,Exception e){
        if(failed!=player)return;Log.w(TAG,"Skipping unavailable playlist track",e);releasePlayer();
        failures++;track=(track+1)%Math.max(1,assets.size());position=0;saveSelection();
        if(allowed()&&failures<assets.size())worker().postDelayed(()->ensurePlayback(),250);else stopPlayback();
    }
    private static void scheduleWatchdog(){if(!watching){watching=true;worker().postDelayed(watchdog,750);}}
    private static final Runnable watchdog=new Runnable(){public void run(){
        watching=false;
        // No poll/decoding remains active during emulation or when the menu stops.
        if(!foreground||!enabled||gameSuspended||SystemClock.uptimeMillis()-lastTick>1800){stopPlayback();return;}
        if(player!=null){
            if(!prepared&&SystemClock.uptimeMillis()-preparingAt>15000){failCurrent(player,new IllegalStateException("Music preparation timeout"));return;}
            if(prepared&&SystemClock.uptimeMillis()-lastSave>15000)savePosition();scheduleWatchdog();
        }
    }};
}
