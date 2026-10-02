package org.emulationstation.frontend.station;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Build;
import android.os.SystemClock;
import java.io.IOException;
import java.nio.file.Path;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.spec.X509EncodedKeySpec;

/** Android composition root; all calls performing IO must run outside the UI thread. */
public final class StationAndroid {
    private static StationAndroid instance;
    public static synchronized StationAndroid get(Context context) throws Exception {
        if (instance == null) instance = new StationAndroid(context.getApplicationContext());
        return instance;
    }
    public final StationApi api;
    public final StationSessions sessions;
    public final StationCatalogStore catalogs;
    public final StationCoverStore covers;
    public final StationCoordinator coordinator;
    private StationAndroid(Context context) throws Exception {
        Path privateFiles=context.getApplicationContext().getNoBackupFilesDir().toPath();
        StationApi.Clock clock=SystemClock::elapsedRealtime;
        StationApi.Device identity=new StationApi.Device() {
            public PublicKey publicKey() throws Exception {return StationCrypto.publicKey();}
            public byte[] sign(byte[] payload) throws Exception {return StationCrypto.sign(payload);}
            public String manufacturer(){return deviceText(Build.MANUFACTURER);}
            public String model(){return deviceText(Build.MODEL);}
            public int sdk(){return Build.VERSION.SDK_INT;}
        };
        PublicKey authority=KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(
            StationProtocol.decode(StationConfig.STATION_ASSERTION_SPKI_BASE64URL)));
        api=new StationApi(new StationHttp(),identity,clock,authority,StationConfig.STATION_ASSERTION_KEY_ID);
        // Reuses the existing device Keystore alias and verified license file on upgrade.
        sessions=new StationSessions(api,clock,privateFiles.resolve("station-license-id.txt"));
        catalogs=new StationCatalogStore(privateFiles.resolve("station-v2/catalog"));
        covers=new StationCoverStore(privateFiles.resolve("station-v2/covers"),api,sessions,clock,
            Thread::sleep,StationAndroid::validateImage,new ExistingCoverCache(privateFiles.resolve("station-covers")));
        coordinator=new StationCoordinator(api,sessions,catalogs,covers,privateFiles,clock);
    }
    private static String deviceText(String value) {
        String text=value==null?"":value.trim();
        if(text.isEmpty())return "unknown";
        return text.length()>100?text.substring(0,100):text;
    }
    private static void validateImage(byte[] bytes) throws IOException {
        BitmapFactory.Options options=new BitmapFactory.Options();options.inJustDecodeBounds=true;
        BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);
        if(options.outWidth<1 || options.outHeight<1 || options.outWidth>8192 || options.outHeight>8192)
            throw new IOException("Cover dimensions invalid");
        options.inJustDecodeBounds=false;options.inSampleSize=1;
        while(Math.max(options.outWidth,options.outHeight)/options.inSampleSize>720)options.inSampleSize*=2;
        Bitmap bitmap=BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);
        if(bitmap==null)throw new IOException("Cover cannot be decoded");
        bitmap.recycle();
    }
}
