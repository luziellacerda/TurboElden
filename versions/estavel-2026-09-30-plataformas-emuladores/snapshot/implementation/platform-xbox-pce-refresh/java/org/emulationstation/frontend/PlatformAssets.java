package org.emulationstation.frontend;
import android.content.*;import android.app.*;import android.os.*;import java.io.*;
public final class PlatformAssets {
 public static void copyIfAbsent(Context c,String asset,File f)throws IOException{
  if(f.isFile()&&f.length()>0)return;
  File parent=f.getParentFile();if(!parent.isDirectory()&&!parent.mkdirs())throw new IOException("Pasta indisponível: "+parent);
  File tmp=new File(parent,f.getName()+".tmp");
  try(InputStream in=c.getAssets().open(asset);FileOutputStream out=new FileOutputStream(tmp)){byte[]b=new byte[65536];int n;while((n=in.read(b))!=-1)out.write(b,0,n);out.getFD().sync();}
  if(!tmp.renameTo(f))throw new IOException("Não foi possível concluir "+f.getName());
 }
 public static void install(Context c){
  try{for(String name:c.getAssets().list("platform-refresh/covers"))copyIfAbsent(c,"platform-refresh/covers/"+name,new File(c.getFilesDir(),"turbo-game-covers/"+name));}
  catch(Exception e){android.util.Log.e("TurboPlatforms","cover assets",e);}
 }
 public static String preparePce(Context c,String home){
  try{File bios=new File(home,".emulationstation/bios/syscard3.pce");copyIfAbsent(c,"platform-refresh/setup/syscard3.pce",bios);return "";}
  catch(Exception e){android.util.Log.e("TurboPlatforms","PC Engine CD BIOS",e);return "Não foi possível preparar a BIOS do PC Engine CD. Confira o acesso à pasta de BIOS.";}
 }
}
