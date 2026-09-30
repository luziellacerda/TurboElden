package org.emulationstation.frontend;
import android.app.*;import android.os.*;import android.content.*;import android.graphics.Color;import android.widget.*;import java.io.*;
/** Same-task entry with an explicit initialization failure screen. */
public class Xbox360EntryActivity extends Activity {
 @Override public void onCreate(Bundle b){super.onCreate(b);Throwable error=Xbox360Bootstrap.initializationError();if(error!=null){showError("Não foi possível iniciar o XenDroid. Volte às plataformas e tente novamente.");return;}
  try{boolean settings=getIntent().getBooleanExtra("settings",false);Intent next=new Intent();next.setClassName(this,settings?"xendroid.compose.MainActivity":"xendroid.compose.EmulatorHostActivity");
   if(!settings){File f=Xbox360Bootstrap.executable(new File(getIntent().getStringExtra("game")),0);if(f==null){showError("Nenhum arquivo Xbox 360 compatível foi encontrado. Aguarde a extração do jogo.");return;}next.putExtra("game_uri",f.getAbsolutePath());}
   startActivity(next);finish();
  }catch(Throwable e){android.util.Log.e("TurboXbox360","Entry failed",e);showError("Não foi possível abrir o Xbox 360. Verifique o arquivo do jogo.");}}
 private void showError(String text){LinearLayout box=new LinearLayout(this);box.setOrientation(1);box.setPadding(40,40,40,40);box.setBackgroundColor(Color.rgb(6,14,8));TextView message=new TextView(this);message.setText(text);message.setTextColor(Color.WHITE);message.setTextSize(19);box.addView(message);Button back=new Button(this);back.setText("VOLTAR ÀS PLATAFORMAS");back.setOnClickListener(v->finish());box.addView(back);setContentView(box);}
}
