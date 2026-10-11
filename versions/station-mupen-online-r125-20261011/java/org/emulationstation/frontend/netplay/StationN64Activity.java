package org.emulationstation.frontend.netplay;

import android.app.*;
import android.content.*;
import android.os.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;

/** Frontend launch/return anchor; actual rendering and input remain in the
 * existing Mupen GameActivity/CoreService in :n64core. */
public final class StationN64Activity extends Activity {
    private String file;private boolean childStarted;private final ExecutorService worker=Executors.newSingleThreadExecutor();
    @Override protected void onCreate(Bundle state){super.onCreate(state);file=getIntent().getStringExtra("station.launch");
        if(state!=null){childStarted=state.getBoolean("childStarted");if(childStarted)return;}
        getWindow().setBackgroundDrawableResource(android.R.color.black);TextView text=new TextView(this);text.setText("Preparando Nintendo 64…");text.setTextColor(0xffeaf2ff);text.setGravity(17);setContentView(text);
        worker.execute(()->{try {
            JSONObject launch=StationN64Launch.peek(this,file);prepareAssets();File rom=new File(launch.getString("rom"));byte[] header;
            try(InputStream in=new FileInputStream(rom)){header=StationN64Wire.exact(in,64);}
            Object info=Class.forName("paulscode.android.mupen64plusae.util.RomHeader").getConstructor(byte[].class).newInstance((Object)header);
            if(!info.getClass().getField("isValid").getBoolean(info))throw new IOException("N64_ROM_HEADER");
            MessageDigest md5=MessageDigest.getInstance("MD5");byte[] buffer=new byte[131072];try(InputStream in=new FileInputStream(rom)){int n;while((n=in.read(buffer))!=-1)md5.update(buffer,0,n);}
            Intent intent=new Intent().setClassName(this,"paulscode.android.mupen64plusae.game.GameActivity");intent.putExtras(getIntent());intent.putExtra(StationN64Bridge.EXTRA,file);
            intent.putExtra(StationN64Launch.key("ROM_PATH"),android.net.Uri.fromFile(rom).toString());
            intent.putExtra(StationN64Launch.key("ZIP_PATH"),"");intent.putExtra(StationN64Launch.key("ROM_MD5"),StationOnlineGame.hex(md5.digest()));
            intent.putExtra(StationN64Launch.key("ROM_CRC"),(String)info.getClass().getField("crc").get(info));
            intent.putExtra(StationN64Launch.key("ROM_HEADER_NAME"),(String)info.getClass().getField("name").get(info));
            intent.putExtra(StationN64Launch.key("ROM_COUNTRY_CODE"),header[0x3e]);intent.putExtra(StationN64Launch.key("ROM_GOOD_NAME"),launch.getString("name"));
            intent.putExtra(StationN64Launch.key("ROM_DISPLAY_NAME"),launch.getString("name"));intent.putExtra(StationN64Launch.key("DO_RESTART"),true);
            intent.putExtra(StationN64Launch.key("NETPLAY_ENABLED"),true).putExtra(StationN64Launch.key("NETPLAY_SERVER"),false);
            runOnUiThread(()->{if(isFinishing()||isDestroyed())return;childStarted=true;startActivityForResult(intent,64);});
        }catch(Exception error){runOnUiThread(()->{if(isFinishing())return;StationN64Launch.discard(this,file);Toast.makeText(this,"Não foi possível preparar o Nintendo 64 para esta sala.",Toast.LENGTH_LONG).show();setResult(RESULT_CANCELED);finish();});}});
    }
    @Override protected void onSaveInstanceState(Bundle state){state.putBoolean("childStarted",childStarted);super.onSaveInstanceState(state);}
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==64){setResult(result,data);finish();}}
    @Override protected void onDestroy(){worker.shutdownNow();if(isFinishing()&&!childStarted)StationN64Launch.discard(this,file);super.onDestroy();}
    private void prepareAssets()throws Exception {
        File destination=(File)Class.forName("org.emulationstation.frontend.N64Bootstrap").getMethod("files",Context.class).invoke(null,this);
        copyMissing("mupen64plus_data",destination);
    }
    private void copyMissing(String asset,File destination)throws Exception {
        if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("N64_ASSET_CANCELLED");
        String[] children=getAssets().list(asset);
        if(children!=null&&children.length>0){if(!destination.isDirectory()&&!destination.mkdirs())throw new IOException("N64_ASSET_DIRECTORY");
            for(String child:children){if(child.contains("/")||child.equals(".."))throw new IOException("N64_ASSET_PATH");copyMissing(asset+"/"+child,new File(destination,child));}return;}
        if(destination.exists())return;
        File temp=new File(destination.getParentFile(),destination.getName()+".station-"+UUID.randomUUID()+".tmp");
        try {try(InputStream in=getAssets().open(asset);FileOutputStream out=new FileOutputStream(temp)){byte[] b=new byte[32768];int n;while((n=in.read(b))!=-1){if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("N64_ASSET_CANCELLED");out.write(b,0,n);}out.getFD().sync();}
            try{java.nio.file.Files.move(temp.toPath(),destination.toPath(),java.nio.file.StandardCopyOption.ATOMIC_MOVE);}catch(java.nio.file.FileAlreadyExistsException raced){/* Another verified launch supplied this bundled file. */}
        }finally{java.nio.file.Files.deleteIfExists(temp.toPath());}
    }
}
