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

/** Visible room/chooser art through the same authenticated, persistent cover store. */
final class StationRoomArtwork {
    interface Callback { void complete(Bitmap bitmap); }
    private final Context context;
    private final Handler ui=new Handler(Looper.getMainLooper());
    private final LruCache<String,Bitmap> bitmaps=new LruCache<String,Bitmap>(8*1024*1024){
        @Override protected int sizeOf(String key,Bitmap value){return value.getAllocationByteCount();}
    };
    private static final class Request {
        final ArrayList<Callback> callbacks=new ArrayList<>();
        StationCoverQueue.Handle handle;
        boolean highPriority;
        int attempt;
    }
    private final Map<String,Request> pending=new HashMap<>();
    private boolean active;
    private int epoch;
    StationRoomArtwork(Context context){this.context=context.getApplicationContext();}
    void start(){active=true;}
    void stop(){
        active=false;epoch++;
        for(Request request:pending.values())if(request.handle!=null)request.handle.cancel();
        pending.clear();
    }
    void close(){stop();bitmaps.evictAll();}
    void load(String itemId,int maximum,Callback callback){load(itemId,maximum,false,callback);}
    void loadHero(String itemId,int maximum,Callback callback){load(itemId,maximum,true,callback);}
    private void load(String itemId,int maximum,boolean highPriority,Callback callback){
        if(!active||itemId==null||itemId.isEmpty()){callback.complete(null);return;}
        final StationAndroid app;final StationCatalog.Item item;
        try{app=StationAndroid.get(context);StationCoordinator.Library library=app.coordinator.current();item=library==null?null:library.catalog.find(itemId);}
        catch(Exception unavailable){callback.complete(null);return;}
        if(item==null){callback.complete(null);return;}
        final int size=Math.max(64,Math.min(1024,maximum));
        final String key=item.coverId+"-"+item.revision+"/"+size;
        Bitmap cached=bitmaps.get(key);if(cached!=null){callback.complete(cached);return;}
        Request existing=pending.get(key);
        if(existing!=null){
            existing.callbacks.add(callback);
            if(highPriority&&!existing.highPriority){existing.highPriority=true;if(existing.handle!=null)existing.handle.cancel();begin(itemId,size,key,existing,epoch,true);}
            return;
        }
        final Request request=new Request();request.callbacks.add(callback);request.highPriority=highPriority;pending.put(key,request);
        begin(itemId,size,key,request,epoch,highPriority);
    }
    private void begin(String itemId,int size,String key,Request request,int generation,boolean highPriority){
        final int attempt=++request.attempt;
        request.handle=StationFrontend.coverWork(itemId,new StationCoverQueue.Work(){
            @Override public void process(Path file,StationApi.Cancellation cancellation)throws Exception {
                byte[] bytes=StationFiles.readBounded(file,5*1024*1024);cancellation.check();
                BitmapFactory.Options options=new BitmapFactory.Options();options.inJustDecodeBounds=true;
                BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);
                if(options.outWidth<1||options.outHeight<1||options.outWidth>8192||options.outHeight>8192)throw new java.io.IOException("Invalid cover bounds");
                options.inJustDecodeBounds=false;options.inSampleSize=1;
                while(Math.max(options.outWidth,options.outHeight)/options.inSampleSize>size)options.inSampleSize*=2;
                Bitmap decoded=BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);
                if(decoded==null)throw new java.io.IOException("Cover decode failed");
                boolean handedOff=false;
                try{cancellation.check();deliver(key,request,generation,attempt,decoded);handedOff=true;}
                finally{if(!handedOff&&!decoded.isRecycled())decoded.recycle();}
            }
            @Override public void failed(int result,long retryMillis){deliver(key,request,generation,attempt,null);}
        },highPriority);
    }
    private void deliver(String key,Request request,int generation,int attempt,Bitmap result){
        ui.post(()->{
            if(!active||epoch!=generation||pending.get(key)!=request||request.attempt!=attempt){if(result!=null&&!result.isRecycled())result.recycle();return;}
            pending.remove(key);if(result!=null)bitmaps.put(key,result);
            for(Callback listener:request.callbacks)listener.complete(result);
        });
    }
}
