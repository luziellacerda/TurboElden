package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.*;
import java.io.File;
public final class MameEntryActivity extends Activity {
 private boolean launched;
 private static final int IMPORT_BIOS=42;
 private boolean importing;
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  try{
   boolean settings=getIntent().getBooleanExtra("settings",false);
   String game=getIntent().getStringExtra("game");
   File rom=game==null?null:new File(game);
   if(!settings&&(rom==null||!rom.isFile()||!rom.canRead()))throw new IllegalStateException("O arquivo instalado não está disponível. Volte ao catálogo e confira a instalação deste jogo.");
   String cdBios=null;
   if(!settings&&NeoCdSupport.isCd(rom))cdBios=NeoCdSupport.prepare(rom,biosHome(),new File("/storage/emulated/0/EmulationStation/roms"));
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
    i.putExtra("cli_params",MameBootstrap.cliParamsFor(game));
    if(cdBios!=null){
     i.setDataAndType(Uri.fromFile(new File(rom.getParentFile(),"neocdz.zip")),"application/zip");
     i.putExtra("cli_params",MameBootstrap.cliParamsFor(game)+" "+NeoCdSupport.cli(rom,cdBios));
    }else i.setDataAndType(Uri.fromFile(rom),mimeFor(game));
   }else{
    i.setAction(Intent.ACTION_MAIN);
   }
   i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
   startActivity(i);
   finish();
  }catch(Exception e){showError(e);}
 }
 private File biosHome(){return new File(getFilesDir(),"mame/station-bios/neogeocd");}
 private void showError(Exception error){
  String game=getIntent().getStringExtra("game");boolean cd=game!=null&&NeoCdSupport.isCd(new File(game));
  AlertDialog.Builder dialog=new AlertDialog.Builder(this).setTitle(cd?"Neo Geo CD":"Neo Geo / MAME").setMessage(error.getMessage()).setPositiveButton("VOLTAR",(d,w)->MameBootstrap.returnToPlatforms(this)).setCancelable(false);
  if(cd)dialog.setNegativeButton("IMPORTAR BIOS",(d,w)->{
   try{Intent pick=new Intent(Intent.ACTION_OPEN_DOCUMENT);pick.addCategory(Intent.CATEGORY_OPENABLE);pick.setType("*/*");startActivityForResult(pick,IMPORT_BIOS);}
   catch(Exception failure){showError(failure);}
  });
  dialog.show();
 }
 @Override protected void onActivityResult(int request,int result,Intent data){
  super.onActivityResult(request,result,data);
  if(request==41&&launched){MameBootstrap.returnToPlatforms(this);return;}
  if(request==IMPORT_BIOS){
   if(result!=RESULT_OK||data==null||data.getData()==null){showError(new IllegalStateException("A BIOS não foi selecionada. O jogo continua disponível no catálogo."));return;}
   if(importing)return;importing=true;
   ProgressDialog progress=ProgressDialog.show(this,"Neo Geo CD","Conferindo a BIOS…",true,false);
   new Thread(()->{
    Exception failure=null;
    try(java.io.InputStream input=getContentResolver().openInputStream(data.getData())){
     if(input==null)throw new java.io.IOException("Não foi possível ler a BIOS selecionada.");
     NeoCdSupport.importBios(biosHome(),input);
     NeoCdSupport.prepare(new File(getIntent().getStringExtra("game")),biosHome(),new File("/storage/emulated/0/EmulationStation/roms"));
    }catch(Exception error){failure=error;}
    final Exception error=failure;
    runOnUiThread(()->{importing=false;progress.dismiss();if(isFinishing()||isDestroyed())return;if(error!=null)showError(error);else{Intent retry=new Intent(this,MameEntryActivity.class);retry.putExtra("game",getIntent().getStringExtra("game"));startActivity(retry);finish();}});
   },"Station-CD-BIOS").start();
  }
 }
 @Override public void onBackPressed(){MameBootstrap.returnToPlatforms(this);}
 private static String mimeFor(String path){
  String p=path==null?"":path.toLowerCase();
  if(p.endsWith(".chd")||p.endsWith(".iso")||p.endsWith(".bin"))return "application/octet-stream";
  if(p.endsWith(".cue")||p.endsWith(".m3u"))return "text/plain";
  return "application/zip";
 }
}
