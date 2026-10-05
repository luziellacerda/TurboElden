package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.*;
import java.io.File;
public final class MameEntryActivity extends Activity {
 private boolean launched;
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  try{
   boolean settings=getIntent().getBooleanExtra("settings",false);
   String game=getIntent().getStringExtra("game");
   File rom=game==null?null:new File(game);
   if(!settings&&(rom==null||!rom.isFile()||!rom.canRead()))throw new IllegalStateException("O arquivo instalado não está disponível. Volte ao catálogo e confira a instalação deste jogo.");
   MameBootstrap.seed(this,game);
   Intent i=new Intent();
   if(settings){
    i.setClassName(this,"com.seleuco.mame4droid.prefs.UserPreferences");
    i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
    startActivityForResult(i,41);
    launched=true;
    return;
   }
   i.setClassName(this,"com.seleuco.mame4droid.MAME4droid");
   if(rom!=null&&rom.isFile()){
    i.setAction(Intent.ACTION_VIEW);
    i.setDataAndType(Uri.fromFile(rom),mimeFor(game));
   }else{
    i.setAction(Intent.ACTION_MAIN);
   }
   i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
   startActivity(i);
   finish();
  }catch(Exception e){
   new AlertDialog.Builder(this).setTitle("Neo Geo / MAME").setMessage("Não foi possível abrir o emulador: "+e.getMessage()).setPositiveButton("VOLTAR",(d,w)->MameBootstrap.returnToPlatforms(this)).setCancelable(false).show();
  }
 }
 @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==41&&launched)MameBootstrap.returnToPlatforms(this);}
 @Override public void onBackPressed(){MameBootstrap.returnToPlatforms(this);}
 private static String mimeFor(String path){
  String p=path==null?"":path.toLowerCase();
  if(p.endsWith(".chd")||p.endsWith(".iso")||p.endsWith(".bin"))return "application/octet-stream";
  if(p.endsWith(".cue")||p.endsWith(".m3u"))return "text/plain";
  return "application/zip";
 }
}
