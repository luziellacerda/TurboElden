package org.emulationstation.frontend;
import android.app.*;import android.content.*;import android.os.*;
public final class XboxEntryActivity extends Activity {
 private boolean launched;
 @Override public void onCreate(Bundle state){super.onCreate(state);try{
  XboxBootstrap.seed(this);String game=getIntent().getStringExtra("game");
  Intent i=new Intent();i.setClassName(this,game!=null&&!game.isEmpty()?"com.izzy2lost.x1box.LauncherActivity":"com.izzy2lost.x1box.SettingsActivity");
  if(game!=null&&!game.isEmpty())i.putExtra("rom",game);
  if(game!=null&&!game.isEmpty()){startActivity(i);finish();}else{startActivityForResult(i,41);launched=true;}
 }catch(Exception e){new AlertDialog.Builder(this).setTitle("Xbox clássico").setMessage("Não foi possível preparar o emulador: "+e.getMessage()).setPositiveButton("VOLTAR",(d,w)->XboxBootstrap.returnToPlatforms(this)).setCancelable(false).show();}}
 @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==41&&launched)XboxBootstrap.returnToPlatforms(this);}
 @Override public void onBackPressed(){XboxBootstrap.returnToPlatforms(this);}
}
