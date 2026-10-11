package org.emulationstation.frontend.offline;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import java.io.IOException;
import java.security.MessageDigest;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** A single foreground hand-off to an independently installed Android emulator. */
public final class StationSonyOfflineActivity extends Activity {
    private ExecutorService preparation;
    private volatile boolean closed;
    private boolean dispatched;

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        if(saved!=null&&saved.getBoolean("station.offline.dispatched",false)){
            dispatched=true;finish();return;
        }
        final Intent incoming=getIntent();
        final String platform=incoming.getStringExtra("station.platform");
        if(!StationSonyOfflinePolicy.supportedPlatform(platform)){
            fail("Sistema não reconhecido.");return;
        }
        if(Build.VERSION.SDK_INT<("ps4".equals(platform)?31:28)){
            fail("ps4".equals(platform)?"O PS4 exige Android 12 ou mais recente.":"O PS3 exige Android 9 ou mais recente.");return;
        }
        if(!arm64()){fail("Este emulador exige um aparelho Android de 64 bits.");return;}
        preparation=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"StationOfflinePrepare");t.setDaemon(true);return t;});
        preparation.execute(()->{
            try{
                if("ps3".equals(platform))preparePs3(incoming.getData());
                else preparePs4(incoming.getData());
            }catch(PackageManager.NameNotFoundException unavailable){
                runOnUiThread(()->missingEmulator(platform));
            }catch(SecurityException denied){postFailure("O emulador não recebeu permissão para abrir este arquivo. Confira o arquivo e as permissões de armazenamento.");}
            catch(Exception invalid){postFailure(invalid.getMessage()==null?"Não foi possível preparar este jogo.":invalid.getMessage());}
        });
    }

    private static boolean arm64(){for(String abi:Build.SUPPORTED_ABIS)if("arm64-v8a".equals(abi))return true;return false;}
    private void installed(String packageName,String version,long versionCode,String expectedCertificate)throws Exception {
        PackageInfo info=getPackageManager().getPackageInfo(packageName,PackageManager.GET_SIGNING_CERTIFICATES);
        if(info.applicationInfo==null||!info.applicationInfo.enabled||info.signingInfo==null||info.signingInfo.hasMultipleSigners())throw new IOException("O aplicativo instalado não corresponde à edição oficial conferida.");
        android.content.pm.Signature[] signatures=info.signingInfo.getApkContentsSigners();
        if(signatures==null||signatures.length!=1||!StationSonyOfflinePolicy.signerMatches(hex(MessageDigest.getInstance("SHA-256").digest(signatures[0].toByteArray())),expectedCertificate))throw new IOException("A assinatura do emulador instalado não corresponde à versão oficial.");
        if(!StationSonyOfflinePolicy.versionMatches(info.versionName,version)||info.getLongVersionCode()!=versionCode)throw new IOException("Esta integração foi conferida com a versão "+version+". A versão instalada usa outro contrato de abertura.");
    }
    private static String hex(byte[] data){StringBuilder out=new StringBuilder(data.length*2);for(byte b:data)out.append(Character.forDigit((b>>>4)&15,16)).append(Character.forDigit(b&15,16));return out.toString();}
    private void component(String packageName,String className)throws PackageManager.NameNotFoundException,IOException {
        ActivityInfo info=getPackageManager().getActivityInfo(new ComponentName(packageName,className),0);
        if(!info.exported||!info.enabled)throw new IOException("A tela de abertura do emulador não está disponível.");
    }
    private void preparePs3(Uri source)throws Exception {
        installed(StationSonyOfflinePolicy.PS3_PACKAGE,StationSonyOfflinePolicy.PS3_VERSION,StationSonyOfflinePolicy.PS3_VERSION_CODE,StationSonyOfflinePolicy.PS3_CERT);
        component(StationSonyOfflinePolicy.PS3_PACKAGE,StationSonyOfflinePolicy.PS3_ACTIVITY);
        if(source==null||!"content".equals(source.getScheme())||!(getPackageName()+".turboeden.provider").equals(source.getAuthority()))throw new IOException("O jogo deve estar instalado na pasta de jogos da TurboStations.");
        String name=null;
        try(Cursor cursor=getContentResolver().query(source,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){
            if(cursor!=null&&cursor.moveToFirst())name=cursor.getString(0);
        }
        if(!StationSonyOfflinePolicy.supportedPs3Image(name))throw new IOException("A abertura direta de PS3 aceita imagem ISO. Instale o firmware no aPS3e e importe outros formatos pelo próprio emulador.");
        try(ParcelFileDescriptor descriptor=getContentResolver().openFileDescriptor(source,"r")){
            if(descriptor==null)throw new IOException("O arquivo do jogo não está disponível.");
        }
        Intent target=new Intent(StationSonyOfflinePolicy.PS3_ACTION);
        target.setComponent(new ComponentName(StationSonyOfflinePolicy.PS3_PACKAGE,StationSonyOfflinePolicy.PS3_ACTIVITY));
        target.putExtra("iso_uri",source.toString());
        target.setDataAndType(source,"application/octet-stream");
        target.setClipData(ClipData.newRawUri("Jogo PS3",source));
        target.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        runOnUiThread(()->confirm("PlayStation 3","O jogo abre no aPS3e oficial. Instale o firmware nele antes de jogar. Se já houver uma partida aberta no aPS3e, encerre-a primeiro.","Abrir jogo",target));
    }
    private void preparePs4(Uri source)throws Exception {
        installed(StationSonyOfflinePolicy.PS4_PACKAGE,StationSonyOfflinePolicy.PS4_VERSION,StationSonyOfflinePolicy.PS4_VERSION_CODE,StationSonyOfflinePolicy.PS4_CERT);
        component(StationSonyOfflinePolicy.PS4_PACKAGE,StationSonyOfflinePolicy.PS4_ACTIVITY);
        String name=displayName(source);
        final boolean pkg=".pkg".equals(StationSonyOfflinePolicy.lowerExtension(name));
        Intent target=new Intent(pkg?Intent.ACTION_VIEW:Intent.ACTION_MAIN);
        target.setComponent(new ComponentName(StationSonyOfflinePolicy.PS4_PACKAGE,StationSonyOfflinePolicy.PS4_ACTIVITY));
        if(pkg){
            readable(source);target.setDataAndType(source,"application/x-pkg");
            target.setClipData(ClipData.newRawUri("Jogo PS4",source));target.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        }
        // DirectLaunchActivity requires a genuine title ID already present in
        // the external game's private DB. A filename/Station item ID is not it.
        runOnUiThread(()->confirm("PlayStation 4",pkg?
            "O pacote será importado pelo Bachata S4 oficial. Depois da importação, escolha o jogo na biblioteca do emulador para jogar.":
            "Escolha o jogo já importado na biblioteca do Bachata S4 oficial. A abertura direta aqui aceita pacotes PKG.",pkg?"Importar jogo":"Abrir biblioteca",target));
    }
    private String displayName(Uri source)throws Exception {
        if(source==null||!"content".equals(source.getScheme())||!(getPackageName()+".turboeden.provider").equals(source.getAuthority()))throw new IOException("O jogo deve estar instalado na pasta de jogos da TurboStations.");
        try(Cursor cursor=getContentResolver().query(source,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){
            return cursor!=null&&cursor.moveToFirst()?cursor.getString(0):null;
        }
    }
    private void readable(Uri source)throws Exception {
        try(ParcelFileDescriptor descriptor=getContentResolver().openFileDescriptor(source,"r")){
            if(descriptor==null)throw new IOException("O arquivo do jogo não está disponível.");
        }
    }
    private void confirm(String title,String message,String action,Intent target){
        if(closed||isFinishing()||dispatched)return;
        new AlertDialog.Builder(this).setTitle(title).setMessage(message)
            .setPositiveButton(action,(d,w)->dispatch(target)).setNegativeButton("Voltar",(d,w)->finish()).setOnCancelListener(d->finish()).show();
    }
    private void dispatch(Intent target){
        if(closed||isFinishing()||dispatched)return;
        try{
            // aPS3e is singleTask and defines no result protocol. For-result can
            // cancel immediately. ClipData carries the temporary read grant
            // for the receiver's task, without a persistent grant or early revoke.
            dispatched=true;startActivity(target);finish();
        }catch(ActivityNotFoundException missing){dispatched=false;fail("O emulador oficial não está disponível neste aparelho.");}
        catch(SecurityException denied){dispatched=false;fail("O Android bloqueou a abertura do emulador. Confira sua instalação e as permissões.");}
        catch(RuntimeException invalid){dispatched=false;fail("Não foi possível abrir o emulador. Seus jogos e saves foram preservados.");}
    }
    private void postFailure(String text){runOnUiThread(()->{if(!closed&&!isFinishing())fail(text);});}
    private void missingEmulator(String platform){
        if(closed||isFinishing())return;
        final boolean ps3="ps3".equals(platform);
        final String release=ps3?"https://github.com/aenu1/aps3e/releases/tag/2.43":"https://github.com/JICA98/Bachata-S4/releases/tag/v0.2.4";
        new AlertDialog.Builder(this).setTitle("Emulador não instalado")
            .setMessage(ps3?"Instale o aPS3e oficial 2.43 antes de abrir um jogo de PS3.":"Instale o Bachata S4 oficial 0.2.4 antes de abrir a biblioteca de PS4.")
            .setPositiveButton("Obter emulador",(d,w)->{
                try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(release)));finish();}
                catch(ActivityNotFoundException missing){fail("Nenhum navegador está disponível para abrir a página oficial.");}
                catch(SecurityException denied){fail("O Android bloqueou a abertura da página oficial.");}
            }).setNegativeButton("Voltar",(d,w)->finish()).setOnCancelListener(d->finish()).show();
    }
    private void fail(String text){if(closed||isFinishing())return;new AlertDialog.Builder(this).setTitle("Jogar offline").setMessage(text).setPositiveButton("Voltar",(d,w)->finish()).setOnCancelListener(d->finish()).show();}
    @Override public void onSaveInstanceState(Bundle out){out.putBoolean("station.offline.dispatched",dispatched);super.onSaveInstanceState(out);}
    @Override public void onDestroy(){closed=true;if(preparation!=null){preparation.shutdownNow();preparation=null;}super.onDestroy();}
}
