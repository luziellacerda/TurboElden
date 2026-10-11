package org.emulationstation.frontend.station;

import android.content.Context;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.provider.OpenableColumns;
import android.widget.Toast;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

/** Two local presentation samples. Never modifies the authenticated library. */
public final class StationLocalSonyDemos {
    private static final String[][] DEMOS={
        {"local-demo-ps3-orbital-v1","ps3","Playstation 3","DEMO-AventuraOrbital.iso","DEMO — Aventura orbital","AVENTURA ORBITAL"},
        {"local-demo-ps4-neon-v1","ps4","Playstation 4","DEMO-CorridaNeon.pkg","DEMO — Corrida neon","CORRIDA NEON"}
    };
    private static volatile Set<String> published=Collections.emptySet();
    private static volatile Context application;
    private StationLocalSonyDemos(){}

    /** Runs only on the existing finite catalogue worker after real rows are prepared. */
    public static void append(Context context,ArrayList<byte[]> rows,String suppliedRoot){
        if(Looper.myLooper()==Looper.getMainLooper())throw new IllegalStateException("Demo preparation requires the catalogue worker");
        application=context.getApplicationContext();
        Set<String> next=new LinkedHashSet<>();
        // Existing JNI publishCatalog accepts at most 4096 rows. Real rows win.
        if(suppliedRoot==null||rows.size()>4094){published=Collections.emptySet();return;}
        try{
            Path root=Paths.get(suppliedRoot).toRealPath();
            if(!root.isAbsolute()||!Files.isDirectory(root,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid demo root");
            Path covers=privateCoverDirectory(context);
            for(String[] demo:DEMOS){
                // A real signed item with a colliding ID wins and is never intercepted.
                if(containsId(rows,demo[0]))continue;
                try{
                    Path folder=root.resolve(demo[1]);
                    if(Files.isSymbolicLink(folder))throw new IOException("Demo folder is symbolic");
                    Files.createDirectories(folder);
                    if(!folder.toRealPath().equals(folder))throw new IOException("Demo folder changed");
                    Path sample=folder.resolve(demo[3]);
                    seed(sample,marker(demo[1]));
                    Path cover=covers.resolve(demo[0]+".png");
                    seedCover(cover,demo);
                    String description="DEMONSTRAÇÃO VISUAL — NÃO CONTÉM JOGO.\n\n"+
                        "Este exemplo mostra a plataforma "+demo[2]+" e sua capa na TurboStations. O arquivo é uma amostra identificada, não uma imagem de jogo nem um pacote instalável.\n\n"+
                        "Ao escolher Jogar, aparece um aviso de demonstração. Não faz download, não abre partida online e não comprova compatibilidade do emulador.";
                    String row=demo[0]+"\0"+demo[4]+"\0"+demo[2]+"\0"+demo[1]+"\0"+demo[0]+"\0"+
                        sample.toString()+"\0\0"+description+"\0"+"1\0"+cover.toString()+"\0";
                    rows.add(row.getBytes(StandardCharsets.UTF_8));next.add(demo[0]);
                }catch(IOException|RuntimeException unavailable){
                    // One sample cannot block login, real games or catalogue publication.
                    android.util.Log.w("StationDemos","Local demonstration unavailable");
                }
            }
        }catch(IOException|RuntimeException unavailable){android.util.Log.w("StationDemos","Local demonstration root unavailable");}
        published=Collections.unmodifiableSet(next);
    }

    public static boolean isPublishedDemo(String id){return id!=null&&published.contains(id);}
    public static boolean rejectAction(String id){
        if(!isPublishedDemo(id))return false;
        final Context context=application;
        if(context!=null)new Handler(Looper.getMainLooper()).post(()->Toast.makeText(context,
            "Demonstração visual: não contém um jogo para baixar ou remover.",Toast.LENGTH_LONG).show());
        return true;
    }
    private static boolean containsId(ArrayList<byte[]> rows,String id){
        byte[] prefix=(id+"\0").getBytes(StandardCharsets.UTF_8);
        for(byte[] row:rows){
            if(row==null||row.length<prefix.length)continue;
            boolean equal=true;for(int i=0;i<prefix.length;i++)if(row[i]!=prefix[i]){equal=false;break;}
            if(equal)return true;
        }
        return false;
    }
    private static byte[] marker(String platform){return ("TURBOSTATIONS-LOCAL-DEMO-V1\nplatform="+platform+
        "\nNOT-A-GAME\nSAMPLE-ONLY-NO-EMULATOR-LAUNCH\n").getBytes(StandardCharsets.US_ASCII);}
    /** Exact legacy path accepted by the unchanged native validWarmCoverPath. */
    private static Path privateCoverDirectory(Context context)throws IOException{
        Path backup=context.getNoBackupFilesDir().toPath();
        if(Files.isSymbolicLink(backup))throw new IOException("Private demo root is symbolic");
        backup=backup.toRealPath();String root=backup.toString();
        if(!root.equals("/data/data/org.turboramastation.frontend/no_backup")&&
            !root.equals("/data/user/0/org.turboramastation.frontend/no_backup"))
            throw new IOException("Private demo root is outside the native cover contract");
        Path covers=backup.resolve("station-covers");
        if(Files.isSymbolicLink(covers))throw new IOException("Private demo cover folder is symbolic");
        Files.createDirectories(covers);
        if(!covers.toRealPath().equals(covers))throw new IOException("Private demo cover folder changed");
        return covers;
    }
    private static void seed(Path file,byte[] expected)throws IOException{
        if(Files.isSymbolicLink(file))throw new IOException("Demo file is symbolic");
        if(Files.exists(file,LinkOption.NOFOLLOW_LINKS)){
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)!=expected.length||!Arrays.equals(Files.readAllBytes(file),expected))
                throw new IOException("Existing file is not our demonstration; preserve it");
            return;
        }
        // CREATE_NEW never overwrites a user's file, including a concurrent arrival.
        Files.write(file,expected,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE);
    }
    private static void seedCover(Path file,String[] demo)throws IOException{
        if(Files.isSymbolicLink(file))throw new IOException("Demo cover is symbolic");
        if(Files.exists(file,LinkOption.NOFOLLOW_LINKS)){
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)<8||Files.size(file)>1048576)throw new IOException("Invalid demo cover");
            try(InputStream in=Files.newInputStream(file)){
                byte[] png=new byte[8];int done=0,count;
                while(done<png.length&&(count=in.read(png,done,png.length-done))!=-1){if(count==0)throw new IOException("Demo cover read made no progress");done+=count;}
                if(done!=8||!Arrays.equals(png,new byte[]{(byte)137,80,78,71,13,10,26,10}))throw new IOException("Invalid demo PNG");
            }
            return;
        }
        Bitmap bitmap=Bitmap.createBitmap(520,760,Bitmap.Config.ARGB_8888);
        try{
            Canvas canvas=new Canvas(bitmap);Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
            canvas.drawColor(Color.rgb(10,14,24));int accent="ps3".equals(demo[1])?Color.rgb(57,126,255):Color.rgb(34,214,194);
            paint.setColor(accent);paint.setStrokeWidth(4);paint.setStyle(Paint.Style.STROKE);canvas.drawRect(18,18,502,742,paint);
            paint.setStyle(Paint.Style.FILL);canvas.drawRect(18,18,502,100,paint);
            paint.setTypeface(Typeface.create(Typeface.DEFAULT,Typeface.BOLD));paint.setColor(Color.WHITE);paint.setTextAlign(Paint.Align.CENTER);paint.setTextSize(32);
            canvas.drawText("TURBOSTATIONS",260,69,paint);paint.setTextSize(96);canvas.drawText(demo[1].toUpperCase(java.util.Locale.ROOT),260,278,paint);
            paint.setTextSize(42);paint.setColor(accent);canvas.drawText("DEMO",260,402,paint);
            paint.setTextSize(27);paint.setColor(Color.WHITE);canvas.drawText(demo[5],260,468,paint);
            paint.setTypeface(Typeface.create(Typeface.DEFAULT,Typeface.NORMAL));paint.setTextSize(24);paint.setColor(Color.rgb(180,189,207));canvas.drawText("EXEMPLO VISUAL",260,624,paint);
            paint.setTextSize(21);canvas.drawText("SEM JOGO • SOMENTE OFFLINE",260,668,paint);
            try(OutputStream out=Files.newOutputStream(file,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
                if(!bitmap.compress(Bitmap.CompressFormat.PNG,100,out))throw new IOException("Demo cover encoding failed");
            }
        }finally{bitmap.recycle();}
    }
    /** Exact provider, sample filename AND complete tiny marker; never inferred from extension. */
    public static boolean isMarkedDemo(Context context,Uri source,String platform)throws IOException{
        String[] expected=null;for(String[] demo:DEMOS)if(demo[1].equals(platform)){expected=demo;break;}
        if(expected==null||source==null||!"content".equals(source.getScheme())||
            !(context.getPackageName()+".turboeden.provider").equals(source.getAuthority()))return false;
        String name=null;
        try(Cursor cursor=context.getContentResolver().query(source,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){
            if(cursor!=null&&cursor.moveToFirst())name=cursor.getString(0);
        }
        if(!expected[3].equals(name))return false;
        byte[] bytes=marker(platform),read=new byte[bytes.length];
        try(InputStream in=context.getContentResolver().openInputStream(source)){
            if(in==null)return false;int done=0,count;
            while(done<read.length&&(count=in.read(read,done,read.length-done))!=-1){if(count==0)throw new IOException("Demo marker read made no progress");done+=count;}
            return done==bytes.length&&Arrays.equals(read,bytes)&&in.read()==-1;
        }
    }
}
