package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.graphics.Color;
import android.os.Bundle;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.regex.*;
import java.security.MessageDigest;

public final class VitaEntryActivity extends Activity {
    private TextView status;private ProgressBar progress;private Button back;
    private volatile boolean cancelled,nativeInstall;private Object nativeApi;private Class<?> nativeClass;
    private boolean resumed;private Intent pendingLaunch;
    private Object call(String name,Class<?>[] types,Object...args)throws Exception{return nativeClass.getMethod(name,types).invoke(nativeApi,args);}
    private Object call(String name)throws Exception{return call(name,new Class<?>[0]);}
    private void phase(int p,String text){runOnUiThread(()->{if(!isFinishing()){progress.setProgress(Math.max(0,Math.min(100,p)));status.setText(text);}});}
    private void fail(String text,Throwable e){android.util.Log.e("TurboVita",text,e);runOnUiThread(()->{if(!isFinishing()){nativeInstall=false;status.setText(text);progress.setVisibility(View.GONE);back.setEnabled(true);}});}
    private void launchVisible(Intent intent){runOnUiThread(()->{if(cancelled||isFinishing())return;if(!resumed){pendingLaunch=intent;return;}startActivity(intent);finish();});}
    private void originalSettings(){Intent i=new Intent();i.setClassName(this,"org.vita3k.emulator.MainActivity");launchVisible(i);}
    @Override protected void onResume(){super.onResume();resumed=true;if(pendingLaunch!=null){Intent next=pendingLaunch;pendingLaunch=null;launchVisible(next);}}
    @Override protected void onPause(){resumed=false;super.onPause();}
    @Override public void onCreate(Bundle b){
        super.onCreate(b);getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setGravity(Gravity.CENTER);box.setPadding(64,40,64,40);box.setBackgroundColor(Color.rgb(3,10,6));
        TextView title=new TextView(this);title.setText("TURBORAMA · PS VITA");title.setTextSize(26);title.setTextColor(Color.rgb(89,241,103));box.addView(title);
        status=new TextView(this);status.setText("Preparando PS Vita…");status.setTextColor(Color.WHITE);status.setTextSize(18);status.setPadding(0,24,0,24);box.addView(status);
        progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);progress.setMax(100);box.addView(progress,new LinearLayout.LayoutParams(-1,24));
        back=new Button(this);back.setText("VOLTAR À TURBORAMA");back.setOnClickListener(v->onBackPressed());box.addView(back);setContentView(box);
        if(VitaBootstrap.initializationError!=null){fail("Não foi possível iniciar o PS Vita. Consulte o registro da integração.",new IllegalStateException(VitaBootstrap.initializationError));return;}
        if(getIntent().getBooleanExtra("settings",false)){
            new Thread(()->{try{initializeNative();installPreparedFirmware();if(!cancelled)originalSettings();}
                catch(Throwable e){if(!cancelled)fail("Não foi possível preparar o firmware do PS Vita: "+e.getMessage(),e);}},"VitaFirmwarePreparation").start();return;
        }
        new Thread(this::prepareGame,"VitaGamePreparation").start();
    }
    private List<Object> apps()throws Exception{
        Object result=call("getAppListDetailed");List<Object> out=new ArrayList<>();if(result instanceof Object[])Collections.addAll(out,(Object[])result);return out;
    }
    private String id(Object app)throws Exception{return (String)app.getClass().getMethod("getTitleId").invoke(app);}
    private Object find(List<Object> list,String id)throws Exception{for(Object a:list)if(id(a).equals(id))return a;return null;}
    private void initializeNative()throws Exception{
        nativeClass=Class.forName("org.vita3k.emulator.NativeLib");nativeApi=nativeClass.getField("INSTANCE").get(null);
        if(!(Boolean)call("isInitialized")&&!(Boolean)call("init",new Class<?>[]{String.class},VitaBootstrap.userFiles(this,null).getAbsolutePath()))throw new IOException("Vita3K initialization failed");
    }
    /** Optional owner-staged official packages. No download or firmware is embedded in this APK. */
    private void installPreparedFirmware()throws Exception{
        String[] names={"PSVita-3.74-preinstalled.PUP","PSVita-3.74-main.PUP","PSVita-3.74-fonts.PUP"};
        String[] hashes={"339d1439eb329cfbd1a936f0a1563458e0555ef52975486b2844e24b6049e33e","6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf","c3c03fc7363dd573d90e5157629bf11551f434b283cc898d9ffc71dd716b791c"};
        String[] labels={"componentes","firmware","fontes"};
        int[] masks={1,2,4};
        File setup=new File(VitaBootstrap.userFiles(this,null),"setup");
        for(int part=0;part<names.length;part++){
            int state=(Integer)call("getFirmwareInstallStateMask");
            if((state&masks[part])!=0)continue;
            File input=new File(setup,names[part]);if(!input.isFile())continue;
            phase(0,"Conferindo "+labels[part]+" do PS Vita…");
            MessageDigest digest=MessageDigest.getInstance("SHA-256");
            try(InputStream in=new FileInputStream(input)){byte[] buffer=new byte[1024*1024];int count;while((count=in.read(buffer))!=-1){if(cancelled)return;digest.update(buffer,0,count);}}
            StringBuilder hex=new StringBuilder();for(byte value:digest.digest())hex.append(String.format(Locale.ROOT,"%02x",value&255));
            if(!hashes[part].equals(hex.toString()))throw new IOException("Arquivo de firmware incompleto ou diferente do preparado.");
            if(cancelled)return;
            final String label="Instalando "+labels[part]+" do PS Vita";
            Class<?> callbackClass=Class.forName("org.vita3k.emulator.data.InstallCallback");
            Object callback=Proxy.newProxyInstance(getClassLoader(),new Class<?>[]{callbackClass},(proxy,method,args)->{
                if(method.getName().equals("onProgress")){int percent=(Integer)args[0];phase(percent,label+": "+percent+"%");return null;}
                if(method.getName().equals("toString"))return "TurboramaFirmwareCallback";
                if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
                if(method.getName().equals("equals"))return proxy==args[0];return null;
            });
            nativeInstall=true;runOnUiThread(()->back.setEnabled(false));
            try{call("installFirmware",new Class<?>[]{String.class,callbackClass},input.getAbsolutePath(),callback);}
            finally{nativeInstall=false;runOnUiThread(()->back.setEnabled(true));}
            int after=(Integer)call("getFirmwareInstallStateMask");
            android.util.Log.i("TurboVita","Prepared firmware component="+part+" mask="+after);
            if((after&masks[part])==0)throw new IOException("O Vita3K não confirmou a instalação deste componente.");
        }
    }
    private void prepareGame(){
        File converted=null;
        try{
            initializeNative();installPreparedFirmware();if(cancelled)return;
            int firmware=(Integer)call("getFirmwareInstallStateMask");
            if((firmware&6)!=6){
                runOnUiThread(()->Toast.makeText(this,"Conclua a instalação do firmware nas configurações do PS Vita e volte a tocar em Jogar.",Toast.LENGTH_LONG).show());originalSettings();return;
            }
            call("prepareFrontend");
            Object[] users=(Object[])call("getUsers");
            if(users==null||users.length==0){String user=(String)call("createUser",new Class<?>[]{String.class},"Jogador");if(user!=null&&!user.isEmpty())call("activateUser",new Class<?>[]{String.class},user);}
            String source=getIntent().getStringExtra("game");if(source==null||source.isEmpty()){originalSettings();return;}
            File input=new File(source);if(!input.isFile())throw new IOException("O arquivo do jogo não foi encontrado.");
            Matcher matcher=Pattern.compile("(?i)(PCS[A-Z][0-9]{5})").matcher(input.getName());String titleId=matcher.find()?matcher.group(1).toUpperCase(Locale.ROOT):"";
            List<Object> before=apps();Object selected=find(before,titleId);
            if(selected==null){
                String lower=source.toLowerCase(Locale.ROOT),installPath=source;
                if(lower.endsWith(".rar")){
                    converted=new File(VitaBootstrap.cache(this),"install-"+UUID.randomUUID()+".zip");
                    String error=VitaBootstrap.convertRar(source,converted.getAbsolutePath(),new VitaBootstrap.Progress(){
                        public void onProgress(int p,String text){phase(p*70/100,"Preparando pacote: "+p+"%");}
                        public boolean isCancelled(){return cancelled;}
                    });
                    if(error!=null)throw new IOException(error);installPath=converted.getAbsolutePath();
                }else if(!lower.endsWith(".zip")&&!lower.endsWith(".vpk")&&!lower.endsWith(".vci"))throw new IOException("Formato de PS Vita não reconhecido: use RAR, ZIP, VPK ou VCI.");
                if(cancelled)return;
                Class<?> callbackClass=Class.forName("org.vita3k.emulator.data.InstallCallback");
                Object callback=Proxy.newProxyInstance(getClassLoader(),new Class<?>[]{callbackClass},(proxy,method,args)->{
                    if(method.getName().equals("onProgress")){int p=(Integer)args[0];phase(70+p*30/100,"Instalando jogo de PS Vita: "+p+"%");return null;}
                    if(method.getName().equals("toString"))return "TurboramaVitaInstallCallback";
                    if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
                    if(method.getName().equals("equals"))return proxy==args[0];return null;
                });
                nativeInstall=true;runOnUiThread(()->back.setEnabled(false));
                boolean installed=(Boolean)call("installArchive",new Class<?>[]{String.class,callbackClass,boolean.class},installPath,callback,false);
                nativeInstall=false;runOnUiThread(()->back.setEnabled(true));
                if(!installed)throw new IOException("O Vita3K não conseguiu instalar este pacote. Confira o formato e a licença do seu jogo.");
                call("refreshAppsList");List<Object> after=apps();selected=find(after,titleId);
                if(selected==null){Set<String> known=new HashSet<>();for(Object a:before)known.add(id(a));List<Object> added=new ArrayList<>();for(Object a:after)if(!known.contains(id(a)))added.add(a);if(added.size()==1)selected=added.get(0);}
                if(selected==null){originalSettings();return;}
            }
            if(cancelled)return;
            final String launchId=id(selected),title=(String)selected.getClass().getMethod("getTitle").invoke(selected);
            Intent i=new Intent();i.setClassName(this,"org.vita3k.emulator.Emulator");i.putExtra("title_id",launchId);i.putExtra("game_title",title);launchVisible(i);
        }catch(Throwable e){if(!cancelled)fail(e.getCause()!=null?e.getCause().toString():e.getMessage(),e);}
        finally{nativeInstall=false;if(converted!=null&&converted.getParentFile().equals(VitaBootstrap.cache(this)))converted.delete();}
    }
    @Override public void onBackPressed(){if(nativeInstall){Toast.makeText(this,"Concluindo a instalação. Aguarde para voltar.",Toast.LENGTH_SHORT).show();return;}cancelled=true;finish();}
    @Override public void onDestroy(){cancelled=true;super.onDestroy();}
}
