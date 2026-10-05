package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.os.*;
import java.io.*;

public final class N64EntryActivity extends Activity {
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  try{
   boolean settings=getIntent().getBooleanExtra("settings",false);String game=getIntent().getStringExtra("game");
   File rom=game==null?null:new File(game);
   if(!settings&&(rom==null||!rom.isFile()||!rom.canRead()))throw new IOException("O arquivo instalado não está disponível.");
   N64Bootstrap.seed(this);N64Bootstrap.settingsLaunch=settings;N64Bootstrap.openedSettings=false;N64Bootstrap.returning=false;
   Intent i=new Intent().setClassName(this,"paulscode.android.mupen64plusae.SplashActivity");
   if(!settings){
    // Use the upstream internal launch contract; no file:// URI crosses an activity boundary.
    Class<?> keys=Class.forName("paulscode.android.mupen64plusae.ActivityHelper$Keys");
    String key=(String)keys.getField("ROM_PATH").get(null);
    i.putExtra(key,rom.getAbsolutePath());
   }
   android.util.Log.i("TurboN64",settings?"Opening upstream N64 settings":"Opening upstream N64 game: "+rom.getName());
   startActivity(i);finish();
  }catch(Exception e){new AlertDialog.Builder(this).setTitle("Nintendo 64").setMessage(e.getMessage()).setPositiveButton("VOLTAR",(d,w)->N64Bootstrap.returnToPlatforms(this)).setCancelable(false).show();}
 }
 @Override public void onBackPressed(){N64Bootstrap.returnToPlatforms(this);}
}
