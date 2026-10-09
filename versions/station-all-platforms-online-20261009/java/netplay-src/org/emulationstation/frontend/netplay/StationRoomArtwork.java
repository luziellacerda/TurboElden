package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;
import android.util.LruCache;
import org.emulationstation.frontend.station.*;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.*;

/** Visible room/chooser art through the same authenticated, persistent cover store. */
final class StationRoomArtwork {
    interface Callback { void complete(Bitmap bitmap); }
    private final Context context;
    private final Handler ui=new Handler(Looper.getMainLooper());
    private final ThreadPoolExecutor workers=new ThreadPoolExecutor(2,2,0,TimeUnit.SECONDS,
            new ArrayBlockingQueue<Runnable>(24),r->{Thread t=new Thread(r,"Station-room-cover");t.setDaemon(true);return t;});
    private final LruCache<String,Bitmap> bitmaps=new LruCache<String,Bitmap>(8*1024*1024){
        @Override protected int sizeOf(String key,Bitmap value){return value.getAllocationByteCount();}
    };
    private static final class Request {
        final StationApi.Cancellation cancel=new StationApi.Cancellation();
        final ArrayList<Callback> callbacks=new ArrayList<>();
    }
    private final Map<String,Request> pending=new HashMap<>();
    private boolean active;
    private int epoch;
    StationRoomArtwork(Context context){this.context=context.getApplicationContext();}
    void start(){active=true;}
    void stop(){
        active=false;epoch++;
        for(Request request:pending.values())request.cancel.cancel();
        pending.clear();workers.getQueue().clear();
    }
    void close(){stop();workers.shutdownNow();bitmaps.evictAll();}
    void load(String itemId,int maximum,Callback callback){
        if(!active||itemId==null||itemId.isEmpty()){callback.complete(null);return;}
        final StationAndroid app;final StationCatalog.Item item;
        try{app=StationAndroid.get(context);StationCoordinator.Library library=app.coordinator.current();item=library==null?null:library.catalog.find(itemId);}
        catch(Exception unavailable){callback.complete(null);return;}
        if(item==null){callback.complete(null);return;}
        final int size=Math.max(64,Math.min(1024,maximum));
        final String key=item.coverId+"-"+item.revision+"/"+size;
        Bitmap cached=bitmaps.get(key);if(cached!=null){callback.complete(cached);return;}
        Request existing=pending.get(key);
        if(existing!=null){existing.callbacks.add(callback);return;}
        final Request request=new Request();request.callbacks.add(callback);pending.put(key,request);
        final int generation=epoch;
        try{workers.execute(()->{
            Bitmap decoded=null;
            try{
                Path file=app.coordinator.cover(itemId,request.cancel);
                byte[] bytes=StationFiles.readBounded(file,5*1024*1024);request.cancel.check();
                BitmapFactory.Options options=new BitmapFactory.Options();options.inJustDecodeBounds=true;
                BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);
                if(options.outWidth<1||options.outHeight<1||options.outWidth>8192||options.outHeight>8192)throw new java.io.IOException("Invalid cover bounds");
                options.inJustDecodeBounds=false;options.inSampleSize=1;
                while(Math.max(options.outWidth,options.outHeight)/options.inSampleSize>size)options.inSampleSize*=2;
                decoded=BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);request.cancel.check();
            }catch(Exception unavailable){
                if(!request.cancel.cancelled())android.util.Log.i("StationRooms","artwork stage=unavailable type="+unavailable.getClass().getSimpleName());
            }
            final Bitmap result=decoded;
            ui.post(()->{
                if(!active||epoch!=generation||pending.get(key)!=request)return;
                pending.remove(key);if(result!=null)bitmaps.put(key,result);
                for(Callback listener:request.callbacks)listener.complete(result);
            });
        });}catch(RejectedExecutionException full){pending.remove(key);callback.complete(null);}
    }
}
