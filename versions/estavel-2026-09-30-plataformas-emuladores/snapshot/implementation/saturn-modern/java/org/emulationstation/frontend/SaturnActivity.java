package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.graphics.*;
import android.graphics.drawable.GradientDrawable;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import org.uoyabause.android.YabauseRunnable;

/** A dedicated Surface and lifecycle for the upstream Android engine. */
public final class SaturnActivity extends Activity implements SurfaceHolder.Callback {
    private static final int GREEN=0xff60ef43, BG=0xff080e0a, WHITE=0xffedf5ed;
    private FrameLayout root; private SurfaceView surface;private Pad pad;
    private TextView message;private SharedPreferences prefs;private File storage;
    private String game;private boolean initialized,resumed,closing,inMenu,settingsOnly;
    private final ExecutorService jobs=Executors.newSingleThreadExecutor();
    private final Handler ui=new Handler(Looper.getMainLooper());
    private int dp(float n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
    private File dir(String name){File f=new File(storage,name);f.mkdirs();return f;}
    private GradientDrawable bg(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(12));d.setStroke(dp(1),0xff2c5833);return d;}
    private TextView text(String value,int size){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(WHITE);t.setPadding(dp(14),dp(10),dp(14),dp(10));return t;}
    private Button button(String label,Runnable action){Button b=new Button(this);b.setText(label);b.setTextColor(WHITE);b.setTextSize(13);b.setAllCaps(false);b.setBackground(bg(0xee12321b));b.setOnClickListener(v->action.run());return b;}
    @Override public void onCreate(Bundle state){
        super.onCreate(state);getWindow().setFlags(1024,1024);getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().getDecorView().setSystemUiVisibility(5894);
        prefs=getSharedPreferences("turbo_saturn_12046",MODE_PRIVATE);
        File external=getExternalFilesDir(null);storage=new File(external==null?getFilesDir():external,"saturn");storage.mkdirs();
        game=getIntent().getStringExtra("game");settingsOnly=getIntent().getBooleanExtra("settings",false)||game==null||game.isEmpty();
        root=new FrameLayout(this);root.setBackgroundColor(BG);setContentView(root);
        if(settingsOnly){settings();return;}
        if(game.startsWith("file://"))game=android.net.Uri.parse(game).getPath();
        if(!new File(game).isFile()){errorMsg("Arquivo do jogo não encontrado.");return;}
        File bios=new File(getBiosPath());if(!bios.isFile()||bios.length()!=524288){errorMsg("A BIOS Saturn não foi encontrada na pasta de BIOS da TurboramaStation.");return;}
        surface=new SurfaceView(this);surface.getHolder().addCallback(this);root.addView(surface,new FrameLayout.LayoutParams(-1,-1));
        pad=new Pad();root.addView(pad,new FrameLayout.LayoutParams(-1,-1));
        Button menu=button("☰  MENU",this::menu);FrameLayout.LayoutParams mp=new FrameLayout.LayoutParams(dp(104),dp(42),Gravity.TOP|Gravity.RIGHT);mp.setMargins(0,dp(8),dp(10),0);root.addView(menu,mp);
        message=text("Preparando Sega Saturn…",18);message.setGravity(Gravity.CENTER);root.addView(message,new FrameLayout.LayoutParams(-1,-1));
    }
    private int option(String k,int def){return prefs.getInt(k,def);}
    private void applyOptions(){
        YabauseRunnable.setCpu(option("cpu",3));YabauseRunnable.setUseSh2Cache(option("cache",1));
        YabauseRunnable.setUseCpuAffinity(0);YabauseRunnable.enableExtendedMemory(0);
        YabauseRunnable.setResolutionMode(option("resolution",3));YabauseRunnable.setRbgResolutionMode(option("rbg",0));
        YabauseRunnable.setAspectRateMode(option("aspect",0));YabauseRunnable.enableComputeShader(option("compute",0));
        YabauseRunnable.setPolygonGenerationMode(option("polygon",0));YabauseRunnable.setFilter(option("filter",0));
        YabauseRunnable.setSoundEngine(option("sound",0));YabauseRunnable.enableFPS(option("fps",0));
        YabauseRunnable.setFrameLimitMode(0);
    }
    @Override public void surfaceCreated(SurfaceHolder h){}
    @Override public void surfaceChanged(SurfaceHolder holder,int format,int w,int h){
        if(closing)return;
        try {
            if(!initialized){applyOptions();if(YabauseRunnable.init(this)!=0)throw new IOException("Falha na inicialização do motor.");initialized=true;}
            YabauseRunnable.initViewport(holder.getSurface(),w,h);
            waitUntilReady(SystemClock.uptimeMillis());
            android.util.Log.i("TurboSaturn","Yaba Sanshiro 1.20.46 Android surface "+w+"x"+h);
        }catch(Throwable e){errorMsg(e.toString());}
    }
    private void waitUntilReady(long started){
        if(closing||!initialized)return;
        int ready=YabauseRunnable.isReady();
        if(ready==1){YabauseRunnable.enableFrameskip(option("frameskip",1));YabauseRunnable.setVolume(option("volume",100));if(!resumed||inMenu)YabauseRunnable.pause();message.setVisibility(View.GONE);android.util.Log.i("TurboSaturn","Engine ready");}
        else if(ready<0||SystemClock.uptimeMillis()-started>60000)errorMsg("O motor não conseguiu preparar o jogo. Confira os registros e a compatibilidade do título.");
        else ui.postDelayed(()->waitUntilReady(started),250);
    }
    @Override public void surfaceDestroyed(SurfaceHolder h){if(initialized&&!closing){pad.releaseAll();YabauseRunnable.pause();}}
    @Override protected void onResume(){super.onResume();resumed=true;if(initialized&&!closing&&!inMenu)YabauseRunnable.resume();}
    @Override protected void onPause(){resumed=false;if(initialized&&!closing){pad.releaseAll();YabauseRunnable.pause();}super.onPause();}
    @Override public void onBackPressed(){if(settingsOnly)exit();else menu();}
    private void menu(){
        if(closing||inMenu)return;inMenu=true;if(pad!=null)pad.releaseAll();if(initialized)YabauseRunnable.pause();
        String[] labels={"Continuar jogo","Salvar estado","Carregar estado","Configurações","Sair do jogo"};
        AlertDialog d=new AlertDialog.Builder(this).setTitle("TURBORAMA  ·  SATURN").setItems(labels,(dialog,which)->{
            if(which==0){inMenu=false;if(initialized&&resumed)YabauseRunnable.resume();}
            else if(which==1||which==2)state(which==1);
            else if(which==3)settingsDialog();else exit();
        }).create();d.setOnCancelListener(dialog->{inMenu=false;if(initialized&&resumed)YabauseRunnable.resume();});d.show();skin(d);
    }
    private void skin(AlertDialog d){if(d.getWindow()!=null)d.getWindow().setBackgroundDrawable(bg(0xff101d13));}
    private String stateKey(){try{byte[] bytes=java.security.MessageDigest.getInstance("SHA-256").digest(new File(game).getName().getBytes("UTF-8"));StringBuilder b=new StringBuilder();for(int i=0;i<12;i++)b.append(String.format(Locale.ROOT,"%02x",bytes[i]&255));return b.toString();}catch(Exception e){throw new IllegalStateException(e);}}
    private File stateDirectory(){File f=new File(dir("states"),stateKey());f.mkdirs();return f;}
    private File stateFile(){return new File(stateDirectory(),prefs.getString("state_"+stateKey(),"missing.yss"));}
    private void state(boolean save){
        if(!initialized){inMenu=false;return;}File file=stateFile();
        if(!save&&!file.isFile()){Toast.makeText(this,"Nenhum estado salvo para este jogo.",Toast.LENGTH_LONG).show();inMenu=false;menu();return;}
        message.setText(save?"Salvando estado…":"Carregando estado…");message.setVisibility(View.VISIBLE);
        jobs.execute(()->{
            boolean ok=false;try{if(save){String r=YabauseRunnable.savestate(stateDirectory().getAbsolutePath());if(r!=null){File saved=new File(r);ok=saved.isFile()&&saved.length()>0&&saved.getParentFile().equals(stateDirectory());if(ok)prefs.edit().putString("state_"+stateKey(),saved.getName()).commit();}}else ok=YabauseRunnable.loadstate(file.getAbsolutePath())==0;}catch(Throwable e){android.util.Log.e("TurboSaturn","State operation",e);}
            final boolean result=ok;runOnUiThread(()->{if(closing)return;message.setVisibility(View.GONE);Toast.makeText(this,result?"Concluído.":"Não foi possível concluir o estado.",Toast.LENGTH_LONG).show();inMenu=false;menu();});
        });
    }
    private void settings(){
        LinearLayout box=settingsBox();ScrollView scroll=new ScrollView(this);scroll.addView(box);root.addView(scroll,new FrameLayout.LayoutParams(-1,-1));
        Button back=button("VOLTAR À TURBORAMA",this::exit);box.addView(back,new LinearLayout.LayoutParams(-1,dp(48)));
    }
    private void settingsDialog(){
        ScrollView scroll=new ScrollView(this);scroll.addView(settingsBox());
        AlertDialog d=new AlertDialog.Builder(this).setTitle("Configurações do Saturn").setView(scroll).setPositiveButton("VOLTAR",(a,b)->{inMenu=false;menu();}).create();
        d.setOnCancelListener(a->{inMenu=false;menu();});d.show();skin(d);
    }
    private LinearLayout settingsBox(){
        LinearLayout box=new LinearLayout(this);box.setOrientation(1);box.setPadding(dp(24),dp(16),dp(24),dp(20));
        TextView title=text("SEGA SATURN",24);title.setTextColor(GREEN);box.addView(title);
        box.addView(text("Yaba Sanshiro 1.20.46 · OpenGL ES\nAs mudanças valem na próxima abertura do jogo.",13));
        choice(box,"Resolução","resolution",3,new String[]{"Original","2×","4×","720p","1080p"},new int[]{3,2,1,4,5});
        choice(box,"Proporção da imagem","aspect",0,new String[]{"Original","4:3","16:9","Preencher tela"},new int[]{0,1,2,3});
        choice(box,"Processador SH-2","cpu",3,new String[]{"Dinâmico ARM64","Interpretador"},new int[]{3,0});
        choice(box,"Cache SH-2","cache",1,new String[]{"Ativado","Desativado"},new int[]{1,0});
        choice(box,"Pular quadros automaticamente","frameskip",1,new String[]{"Ativado","Desativado"},new int[]{1,0});
        choice(box,"Mostrar FPS","fps",0,new String[]{"Desativado","Ativado"},new int[]{0,1});
        choice(box,"Processamento de fundos na GPU","compute",0,new String[]{"Desativado","Ativado"},new int[]{0,1});
        choice(box,"Cartucho de memória","cart",7,new String[]{"Expansão RAM 4 MB","Expansão RAM 1 MB","Sem cartucho"},new int[]{7,6,0});
        choice(box,"Volume","volume",100,new String[]{"100%","75%","50%","25%","Mudo"},new int[]{100,75,50,25,0});
        choice(box,"Controles na tela","touch",1,new String[]{"Mostrar","Ocultar (controle externo)"},new int[]{1,0});
        return box;
    }
    private void choice(LinearLayout box,String label,String key,int def,String[] labels,int[] values){
        int selected=0;for(int i=0;i<values.length;i++)if(values[i]==option(key,def))selected=i;
        final Button b=button(label+"  ·  "+labels[selected],()->{});
        b.setOnClickListener(v->{int current=0;for(int i=0;i<values.length;i++)if(values[i]==option(key,def))current=i;
            AlertDialog d=new AlertDialog.Builder(this).setTitle(label).setSingleChoiceItems(labels,current,(dialog,index)->{prefs.edit().putInt(key,values[index]).apply();b.setText(label+"  ·  "+labels[index]);dialog.dismiss();}).setNegativeButton("VOLTAR",null).create();d.show();skin(d);});
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(48));lp.bottomMargin=dp(8);box.addView(b,lp);
    }
    public String getBiosPath(){return "/sdcard/EmulationStation/.emulationstation/bios/saturn_bios.bin";}
    public String getGamePath(){return game;}
    public String getMemoryPath(){return new File(dir("backup"),"saturn.bin").getAbsolutePath();}
    public String getCartridgePath(){return new File(dir("backup"),"cartridge.bin").getAbsolutePath();}
    public int getCartridgeType(){return option("cart",7);}
    public int getVideoInterface(){return 1;}
    public int getPlayer2InputDevice(){return -1;}
    public String getShaderPath(){return dir("shaders").getAbsolutePath()+"/";}
    public String getTestPath(){return dir("recordings").getAbsolutePath()+"/";}
    public String getFileDescriptorPath(String path){return path;}
    public void onBackupWrite(String name,int device,byte[] before,byte[] after){}
    public void errorMsg(String value){android.util.Log.e("TurboSaturn",value);runOnUiThread(()->{if(closing)return;AlertDialog d=new AlertDialog.Builder(this).setTitle("Sega Saturn").setMessage(value).setPositiveButton("VOLTAR AO MENU",(a,b)->exit()).setCancelable(false).create();d.show();skin(d);});}
    private void exit(){
        if(closing)return;closing=true;ui.removeCallbacksAndMessages(null);if(pad!=null)pad.releaseAll();
        if(!initialized){finish();return;}
        message.setText("Salvando memória e voltando…");message.setVisibility(View.VISIBLE);
        jobs.execute(()->{try{YabauseRunnable.deinit();}catch(Throwable e){android.util.Log.e("TurboSaturn","Shutdown",e);}runOnUiThread(()->{initialized=false;finish();ui.postDelayed(()->android.os.Process.killProcess(android.os.Process.myPid()),300);});});
    }
    @Override public void onDestroy(){ui.removeCallbacksAndMessages(null);if(initialized&&!closing){closing=true;jobs.execute(()->{YabauseRunnable.deinit();android.os.Process.killProcess(android.os.Process.myPid());});}jobs.shutdown();super.onDestroy();}
    private int key(int k){switch(k){case 19:return 0;case 22:return 1;case 20:return 2;case 21:return 3;case 103:return 4;case 102:return 5;case 108:return 6;case 96:return 7;case 97:return 8;case 98:return 9;case 99:return 10;case 100:return 11;case 101:return 12;case 105:return 9;case 104:return 12;default:return -1;}}
    @Override public boolean onKeyDown(int k,KeyEvent e){int b=key(k);if(initialized&&!inMenu&&b>=0){if(e.getRepeatCount()==0)YabauseRunnable.press(b,0);return true;}return super.onKeyDown(k,e);}
    @Override public boolean onKeyUp(int k,KeyEvent e){int b=key(k);if(initialized&&b>=0){YabauseRunnable.release(b,0);return true;}return super.onKeyUp(k,e);}
    @Override public boolean onGenericMotionEvent(MotionEvent e){
        if(initialized&&!inMenu&&(e.getSource()&InputDevice.SOURCE_JOYSTICK)==InputDevice.SOURCE_JOYSTICK){
            float x=e.getAxisValue(MotionEvent.AXIS_X)+e.getAxisValue(MotionEvent.AXIS_HAT_X),y=e.getAxisValue(MotionEvent.AXIS_Y)+e.getAxisValue(MotionEvent.AXIS_HAT_Y);
            pad.external(0,y<-.45f);pad.external(1,x>.45f);pad.external(2,y>.45f);pad.external(3,x<-.45f);return true;
        }return super.onGenericMotionEvent(e);
    }
    private final class Pad extends View {
        private final Paint paint=new Paint(3);private final RectF[] cells=new RectF[13];private final Map<Integer,Integer> pointers=new HashMap<>();private final boolean[] pressed=new boolean[13],external=new boolean[13];
        private final String[] labels={"▲","▶","▼","◀","R","L","START","A","B","C","X","Y","Z"};
        Pad(){super(SaturnActivity.this);for(int i=0;i<13;i++)cells[i]=new RectF();setFocusable(false);}
        @Override protected void onSizeChanged(int w,int h,int ow,int oh){float s=Math.min(dp(54),h*.15f),gap=dp(8),left=dp(24),top=h-3*s-dp(16);cells[0].set(left+s,top,left+2*s,top+s);cells[1].set(left+2*s,top+s,left+3*s,top+2*s);cells[2].set(left+s,top+2*s,left+2*s,top+3*s);cells[3].set(left,top+s,left+s,top+2*s);for(int row=0;row<2;row++)for(int col=0;col<3;col++){int index=(row==0?10:7)+col;float x=w-dp(22)-(3-col)*(s+gap);float y=h-dp(22)-(2-row)*(s+gap);cells[index].set(x,y,x+s,y+s);}cells[5].set(left,dp(56),left+s*1.5f,dp(56)+s*.7f);cells[4].set(w-left-s*1.5f,dp(56),w-left,dp(56)+s*.7f);cells[6].set(w*.5f-s,h-s*.7f-dp(16),w*.5f+s,h-dp(16));}
        @Override protected void onDraw(Canvas c){if(option("touch",1)==0)return;paint.setTextAlign(Paint.Align.CENTER);paint.setTypeface(Typeface.DEFAULT_BOLD);paint.setTextSize(dp(16));for(int i=0;i<13;i++){paint.setColor(pressed[i]?0xa040a431:0x55213226);paint.setStyle(Paint.Style.FILL);c.drawRoundRect(cells[i],dp(14),dp(14),paint);paint.setStyle(Paint.Style.STROKE);paint.setStrokeWidth(dp(1));paint.setColor(0x9982bd80);c.drawRoundRect(cells[i],dp(14),dp(14),paint);paint.setStyle(Paint.Style.FILL);paint.setColor(0xbbedf5ed);c.drawText(labels[i],cells[i].centerX(),cells[i].centerY()-(paint.ascent()+paint.descent())/2,paint);}}
        private int hit(float x,float y){for(int i=0;i<13;i++)if(cells[i].contains(x,y))return i;return -1;}
        private void sync(){for(int i=0;i<13;i++){boolean down=external[i]||pointers.containsValue(i);if(down!=pressed[i]){pressed[i]=down;if(initialized){if(down)YabauseRunnable.press(i,0);else YabauseRunnable.release(i,0);}}}invalidate();}
        void external(int id,boolean value){external[id]=value;sync();}
        void releaseAll(){pointers.clear();Arrays.fill(external,false);sync();}
        @Override public boolean onTouchEvent(MotionEvent e){if(option("touch",1)==0||inMenu||closing)return false;int action=e.getActionMasked(),index=e.getActionIndex();if(action==MotionEvent.ACTION_CANCEL){releaseAll();return true;}for(int i=0;i<e.getPointerCount();i++){int id=e.getPointerId(i);if((action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_POINTER_UP)&&index==i)pointers.remove(id);else pointers.put(id,hit(e.getX(i),e.getY(i)));}sync();return true;}
    }
}
