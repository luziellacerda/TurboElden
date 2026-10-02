package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Environment;
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
    private static final String[] FIRMWARE_NAMES={"PSVita-3.74-preinstalled.PUP","PSVita-3.74-main.PUP","PSVita-3.74-fonts.PUP"};
    private static final String[] FIRMWARE_HASHES={"339d1439eb329cfbd1a936f0a1563458e0555ef52975486b2844e24b6049e33e","6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf","c3c03fc7363dd573d90e5157629bf11551f434b283cc898d9ffc71dd716b791c"};
    private static final String[] FIRMWARE_LABELS={"componentes","firmware","fontes"};
    private static final int[] FIRMWARE_MASKS={1,2,4};
    private static final long[] FIRMWARE_SIZES={128798720L,133834240L,56778752L};
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
            new Thread(()->{try{ensureReady();if(!cancelled)originalSettings();}
                catch(Throwable e){if(!cancelled)fail("Não foi possível deixar o PS Vita pronto: "+e.getMessage(),e);}},"VitaFirmwarePreparation").start();return;
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
    private List<File> firmwareRoots(){
        List<File> dirs=new ArrayList<>();
        dirs.add(new File(VitaBootstrap.userFiles(this,null),"setup"));
        dirs.add(new File(VitaBootstrap.files(this),"setup"));
        File[] extras=getExternalFilesDirs(null);
        if(extras!=null)for(File d:extras)if(d!=null){dirs.add(new File(d,"psvita/setup"));dirs.add(new File(d,"setup"));}
        File ext=Environment.getExternalStorageDirectory();
        if(ext!=null){
            dirs.add(new File(ext,"EmulationStation/bios/psvita"));
            dirs.add(new File(ext,"EmulationStation/firmware/psvita"));
            dirs.add(new File(ext,"EmulationStation/bios"));
            dirs.add(new File(ext,"Turborama/firmware/psvita"));
            dirs.add(new File(ext,"Download/psvita"));
            dirs.add(new File(ext,"Download"));
            dirs.add(new File(ext,"Android/data/"+getPackageName()+"/files/psvita/setup"));
        }
        File downloads=Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        if(downloads!=null){dirs.add(new File(downloads,"psvita"));dirs.add(downloads);}
        return dirs;
    }
    private String sha256(File input)throws Exception{
        MessageDigest digest=MessageDigest.getInstance("SHA-256");
        try(InputStream in=new FileInputStream(input)){byte[] buffer=new byte[1024*1024];int count;while((count=in.read(buffer))!=-1){if(cancelled)throw new IOException("cancelado");digest.update(buffer,0,count);}}
        StringBuilder hex=new StringBuilder();for(byte value:digest.digest())hex.append(String.format(Locale.ROOT,"%02x",value&255));
        return hex.toString();
    }
    private File locateFirmware(String name,String expected,long size)throws Exception{
        for(File dir:firmwareRoots()){
            File input=new File(dir,name);
            if(!input.isFile()||input.length()!=size)continue;
            phase(0,"Conferindo "+name+"…");
            if(expected.equals(sha256(input)))return input;
            android.util.Log.w("TurboVita","Firmware candidate hash mismatch: "+input.getAbsolutePath());
        }
        return null;
    }
    private void stageFirmwareFromAssets(File setup)throws Exception{
        long total=0;for(long size:FIRMWARE_SIZES)total+=size;long done=0;
        for(int part=0;part<FIRMWARE_NAMES.length;part++){
            File dest=new File(setup,FIRMWARE_NAMES[part]);
            if(dest.isFile()&&dest.length()==FIRMWARE_SIZES[part]){done+=FIRMWARE_SIZES[part];continue;}
            InputStream in;
            try{in=getAssets().open("psvita-firmware/"+FIRMWARE_NAMES[part]);}
            catch(IOException missing){android.util.Log.w("TurboVita","Firmware asset absent: "+FIRMWARE_NAMES[part]);done+=FIRMWARE_SIZES[part];continue;}
            File tmp=new File(setup,FIRMWARE_NAMES[part]+".part");
            try(InputStream input=in;OutputStream out=new FileOutputStream(tmp)){
                byte[] buffer=new byte[1024*1024];int n;long wrote=0;
                while((n=input.read(buffer))!=-1){
                    if(cancelled)throw new IOException("cancelado");
                    out.write(buffer,0,n);wrote+=n;
                    int p=(int)((done+wrote)*100/Math.max(1L,total));
                    phase(Math.min(99,p),"Copiando "+FIRMWARE_LABELS[part]+" do PS Vita");
                }
            }
            if(tmp.length()!=FIRMWARE_SIZES[part]){tmp.delete();throw new IOException("Pacote incompleto: "+FIRMWARE_NAMES[part]);}
            if(dest.exists()&&!dest.delete())tmp.delete();
            if(!tmp.renameTo(dest)){tmp.delete();throw new IOException("Não foi possível gravar "+FIRMWARE_NAMES[part]);}
            android.util.Log.i("TurboVita","Staged firmware asset "+FIRMWARE_NAMES[part]+" bytes="+dest.length());
            done+=FIRMWARE_SIZES[part];
        }
    }
    /** Official 3.74 packages ship inside the TESTE APK and are copied to setup on first open. */
    private void installPreparedFirmware()throws Exception{
        File setup=new File(VitaBootstrap.userFiles(this,null),"setup");setup.mkdirs();
        stageFirmwareFromAssets(setup);
        List<String> missing=new ArrayList<>();
        for(int part=0;part<FIRMWARE_NAMES.length;part++){
            int state=(Integer)call("getFirmwareInstallStateMask");
            if((state&FIRMWARE_MASKS[part])!=0)continue;
            File input=locateFirmware(FIRMWARE_NAMES[part],FIRMWARE_HASHES[part],FIRMWARE_SIZES[part]);
            if(input==null){missing.add(FIRMWARE_LABELS[part]);continue;}
            final String label="Preparando "+FIRMWARE_LABELS[part]+" do PS Vita";
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
            if((after&FIRMWARE_MASKS[part])==0)throw new IOException("O Vita3K não confirmou a instalação deste componente.");
        }
        int firmware=(Integer)call("getFirmwareInstallStateMask");
        if((firmware&6)!=6){
            String detail=missing.isEmpty()?"":(" Faltam: "+android.text.TextUtils.join(", ",missing)+".");
            throw new IOException("O firmware oficial 3.74 do PS Vita ainda não está pronto neste aparelho."+detail);
        }
    }
    private void markSetupComplete(){
        getSharedPreferences("vita3k_app",MODE_PRIVATE).edit().putBoolean("initial_setup_completed",true).commit();
    }
    private void ensureReady()throws Exception{
        phase(2,"Preparando o PS Vita…");
        initializeNative();
        installPreparedFirmware();
        if(cancelled)return;
        call("prepareFrontend");
        Object[] users=(Object[])call("getUsers");
        if(users==null||users.length==0){String user=(String)call("createUser",new Class<?>[]{String.class},"Jogador");if(user!=null&&!user.isEmpty())call("activateUser",new Class<?>[]{String.class},user);}
        markSetupComplete();
        phase(100,"PS Vita pronto");
    }
    private void prepareGame(){
        File converted=null;
        try{
            ensureReady();if(cancelled)return;
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
                    if(method.getName().equals("onProgress")){int p=(Integer)args[0];phase(70+p*30/100,"Preparando jogo de PS Vita: "+p+"%");return null;}
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
