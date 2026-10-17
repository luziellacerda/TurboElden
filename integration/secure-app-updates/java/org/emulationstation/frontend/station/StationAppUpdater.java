package org.emulationstation.frontend.station;

import android.app.*;
import android.content.*;
import android.content.pm.*;
import android.os.*;
import java.io.*;
import java.lang.ref.WeakReference;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;
import org.json.JSONObject;

/** One opt-in APK job; the OS installer owns replacement and signature verification. */
public final class StationAppUpdater {
    private static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static final ExecutorService WORK=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-app-update");t.setDaemon(true);return t;});
    private static final CopyOnWriteArrayList<Runnable> LISTENERS=new CopyOnWriteArrayList<>();
    private static volatile StationAndroid app;
    static volatile StationAppRelease offer;
    static volatile String message="Procurando atualização…";
    static volatile long received,total;
    static volatile boolean busy,checking,installing;
    private static volatile StationApi.Cancellation cancellation;
    private static volatile Intent pendingConfirmation;
    private static WeakReference<Activity> screen=new WeakReference<>(null);
    private static long lastProgress;
    private StationAppUpdater(){}

    static synchronized void initialize(StationAndroid value){
        boolean first=app==null;app=value;
        if(first)WORK.execute(()->{try{
            long expected=state().getLong("version",0);
            if(expected>0&&installed().getLongVersionCode()>=expected){
                StationAppUpdateFiles.prune(app.privateFiles.resolve("station-app-updates"),"");
                state().edit().clear().apply();
            }
        }catch(Exception unavailable){android.util.Log.w("StationUpdate","event=old-staging-cleanup-failed");}});
    }
    static void observe(Runnable listener){LISTENERS.add(listener);MAIN.post(listener);}
    static void forget(Runnable listener){LISTENERS.remove(listener);}
    static void screen(Activity value){screen=new WeakReference<>(value);launchConfirmation();}
    static void releaseScreen(Activity value){if(screen.get()==value)screen.clear();}
    private static void changed(){MAIN.post(()->{for(Runnable listener:LISTENERS)listener.run();});}
    private static android.content.SharedPreferences state(){return app.context.getSharedPreferences("station-app-update",Context.MODE_PRIVATE);}

    static PackageInfo installed()throws Exception{
        return app.context.getPackageManager().getPackageInfo(StationAppRelease.PACKAGE,PackageManager.GET_SIGNING_CERTIFICATES);
    }
    static String certificate(PackageInfo info)throws Exception{
        if(info.signingInfo==null||info.signingInfo.hasMultipleSigners())throw new IOException("UPDATE_SIGNER");
        android.content.pm.Signature[] signatures=info.signingInfo.getApkContentsSigners();
        if(signatures==null||signatures.length!=1)throw new IOException("UPDATE_SIGNER");
        return StationAppUpdateFiles.hex(MessageDigest.getInstance("SHA-256").digest(signatures[0].toByteArray()));
    }
    private static boolean arm64(){for(String abi:Build.SUPPORTED_ABIS)if("arm64-v8a".equals(abi))return true;return false;}
    private static JSONObject request(boolean authorize,String id)throws Exception{
        PackageInfo info=installed();
        JSONObject result=new JSONObject().put("schemaVersion",1)
            .put("domain","TurboRamaStationAndroid/"+(authorize?"request-app-update-download":"request-app-update-check")+"/v1")
            .put("productId",StationConfig.PRODUCT).put("applicationId",StationConfig.APPLICATION)
            .put("deviceId",app.api.deviceId()).put("requestId",UUID.randomUUID().toString().replace("-",""))
            .put("packageName",StationAppRelease.PACKAGE).put("versionCode",info.getLongVersionCode())
            .put("androidSdk",Build.VERSION.SDK_INT).put("abi",arm64()?"arm64-v8a":"unsupported")
            .put("certificateSha256",certificate(info));
        if(authorize)result.put("releaseId",id);
        return result;
    }
    static synchronized void check(Runnable completion){
        if(app==null||busy||checking||!app.api.available()){
            if(app!=null&&!busy&&!checking)message="Sem internet para consultar atualizações.";
            if(completion!=null)MAIN.post(completion);return;
        }
        checking=true;
        WORK.execute(()->{
            try(StationSessions.Lease lease=app.sessions.acquire(new StationApi.Cancellation())){
                JSONObject reply=app.api.appUpdates(lease.session,false,request(false,null),new StationApi.Cancellation());
                Object available=reply.get("available");if(!(available instanceof Boolean))throw new IOException("UPDATE_METADATA");
                StationAppRelease next=(Boolean)available?StationAppRelease.parse(reply.getJSONObject("release")):null;
                if(!(Boolean)available&&!reply.isNull("release"))throw new IOException("UPDATE_METADATA");
                PackageInfo info=installed();
                if(next!=null&&!next.eligible(info.getLongVersionCode(),Build.VERSION.SDK_INT,certificate(info),arm64()))throw new IOException("UPDATE_INCOMPATIBLE");
                offer=next;message=next==null?"O aplicativo está atualizado.":"Atualização disponível: "+next.versionName;
            }catch(Exception failure){
                // Old servers can return 404 until this additive feature is deployed.
                // Offline/failed checks never block login or installed games.
                message="Não foi possível consultar atualizações agora.";
                android.util.Log.w("StationUpdate","event=check-failed type="+failure.getClass().getSimpleName());
            }finally{checking=false;changed();if(completion!=null)MAIN.post(completion);}
        });
    }
    static synchronized boolean begin(Context context){
        if(busy||offer==null)return false;
        if(StationFrontend.activeCount()>0){message="Aguarde os downloads de jogos terminarem para atualizar.";changed();return false;}
        busy=true;installing=false;received=0;total=offer.sizeBytes;message="Iniciando atualização…";
        cancellation=new StationApi.Cancellation();changed();
        try{context.startForegroundService(new Intent(context,StationAppUpdateService.class));return true;}
        catch(RuntimeException unavailable){busy=false;message="Não foi possível iniciar a atualização. Tente novamente.";changed();return false;}
    }
    static void cancel(){StationApi.Cancellation active=cancellation;if(active!=null&&!installing)active.cancel();}
    static void run(StationAppUpdateService service){WORK.execute(()->download(service));}
    private static void progress(long bytes,long all){
        received=bytes;total=all;long now=SystemClock.elapsedRealtime();
        if(now-lastProgress>=250||bytes==all){lastProgress=now;changed();}
    }
    private static void download(StationAppUpdateService service){
        int installSession=-1;boolean committed=false;
        try{
            StationAppRelease selected=offer;if(selected==null)throw new IOException("UPDATE_CHANGED");
            StationApi.Cancellation cancel=cancellation;cancel.check();
            Path root=StationAppUpdateFiles.root(app.privateFiles.resolve("station-app-updates"));
            StationAppUpdateFiles.prune(root,selected.sha256+".apk");
            message="Conferindo atualização…";changed();
            Path file=StationAppUpdateFiles.cached(root,selected,cancel);cancel.check();
            long required=(file==null?selected.sizeBytes*2:selected.sizeBytes)+128L*1024*1024;
            if(Files.getFileStore(root).getUsableSpace()<required)throw new IOException("UPDATE_STORAGE_FULL");
            if(file==null){
                message="Baixando atualização…";changed();
                StationApi.Response response;
                try(StationSessions.Lease lease=app.sessions.acquire(cancel)){
                    JSONObject grant=app.api.appUpdates(lease.session,true,request(true,selected.id),cancel);
                    if(!selected.same(StationAppRelease.parse(grant.getJSONObject("release"))))throw new IOException("UPDATE_CHANGED");
                    // Keep the same session through authorization and GET headers;
                    // renewals are free to proceed after the server admits the stream.
                    response=app.api.openAppUpdate(lease.session,grant.getString("grantId"),selected.sizeBytes,cancel);
                }
                try(StationApi.Response owned=response){file=StationAppUpdateFiles.receive(owned.body,root,selected,cancel,StationAppUpdater::progress);}
            }
            cancel.check();message="Preparando atualização…";received=0;total=selected.sizeBytes;changed();
            PackageManager manager=app.context.getPackageManager();
            PackageInfo archive=manager.getPackageArchiveInfo(file.toString(),PackageManager.GET_SIGNING_CERTIFICATES);
            PackageInfo current=installed();
            if(archive==null||!StationAppRelease.PACKAGE.equals(archive.packageName)||archive.getLongVersionCode()!=selected.versionCode||
                !certificate(archive).equals(selected.certificateSha256)||!certificate(current).equals(selected.certificateSha256)||
                selected.versionCode<=current.getLongVersionCode())throw new IOException("UPDATE_SIGNER_OR_VERSION");
            PackageInstaller installer=manager.getPackageInstaller();
            int previous=state().getInt("session",-1);
            if(previous>=0)try{installer.abandonSession(previous);}catch(RuntimeException gone){/* only this updater's recorded session */}
            PackageInstaller.SessionParams parameters=new PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL);
            parameters.setAppPackageName(StationAppRelease.PACKAGE);parameters.setSize(selected.sizeBytes);
            if(Build.VERSION.SDK_INT>=31)parameters.setRequireUserAction(PackageInstaller.SessionParams.USER_ACTION_REQUIRED);
            installSession=installer.createSession(parameters);
            try(PackageInstaller.Session session=installer.openSession(installSession);
                InputStream input=Files.newInputStream(file,LinkOption.NOFOLLOW_LINKS)){
                try(OutputStream output=session.openWrite("base.apk",0,selected.sizeBytes)){
                    byte[] buffer=new byte[256*1024];long count=0;int n;
                    while((n=input.read(buffer))>=0){cancel.check();if(n>0){output.write(buffer,0,n);count+=n;progress(count,selected.sizeBytes);}}
                    if(count!=selected.sizeBytes)throw new IOException("UPDATE_LENGTH");session.fsync(output);
                }
                cancel.check();String nonce=UUID.randomUUID().toString();
                if(!state().edit().putInt("session",installSession).putString("nonce",nonce)
                    .putLong("version",selected.versionCode).putString("apk",file.getFileName().toString()).commit())throw new IOException("UPDATE_STORAGE");
                Intent result=new Intent(app.context,StationAppUpdateReceiver.class).setAction(StationAppRelease.PACKAGE+".APP_UPDATE")
                    .setData(android.net.Uri.parse("station-update://session/"+installSession)).putExtra("nonce",nonce);
                int flags=PendingIntent.FLAG_UPDATE_CURRENT|(Build.VERSION.SDK_INT>=31?PendingIntent.FLAG_MUTABLE:0);
                PendingIntent callback=PendingIntent.getBroadcast(app.context,installSession,result,flags);
                installing=true;message="Confirme a atualização na tela do Android.";changed();
                session.commit(callback.getIntentSender());committed=true;
            }
        }catch(Exception failure){
            if(committed){
                // Ownership has already passed to the platform. A resource
                // close error cannot turn an accepted install into a retry.
                message="Aguardando a confirmação do Android.";changed();
                android.util.Log.w("StationUpdate","event=installer-handoff-close type="+failure.getClass().getSimpleName());
            }else{
            boolean cancelled=failure instanceof InterruptedIOException;
            String reason=failure.getMessage();
            String category=reason!=null&&reason.matches("UPDATE_[A-Z_]{1,48}")?reason:"UPDATE_FAILED";
            if(failure instanceof StationApi.Failure&&"STATION_UPDATE_CHANGED".equals(((StationApi.Failure)failure).code)){
                offer=null;category="UPDATE_CHANGED";
            }
            message=cancelled?"Atualização cancelada.":"UPDATE_STORAGE_FULL".equals(failure.getMessage())?
                "Libere espaço no telefone para atualizar.":"UPDATE_CHANGED".equals(category)?
                "A versão disponível mudou. Verifique novamente para continuar.":"Não foi possível concluir a atualização. Tente novamente.";
            android.util.Log.w("StationUpdate","event=update-failed category="+category+" type="+failure.getClass().getSimpleName());
            busy=false;installing=false;changed();
            }
        }finally{
            if(!committed){
                if(installSession>=0)try{app.context.getPackageManager().getPackageInstaller().abandonSession(installSession);}catch(RuntimeException ignored){}
                service.finishJob();
            }else MAIN.post(()->{service.finishJob();Intent pending=pendingConfirmation;if(pending!=null)StationAppUpdateService.pendingNotice(app.context,pending);});
        }
    }
    static void installerResult(Context context,Intent intent){
        try{
            initialize(StationAndroid.get(context));
            if(!Objects.equals(state().getString("nonce",null),intent.getStringExtra("nonce"))||
                !intent.hasExtra("nonce")||intent.getIntExtra(PackageInstaller.EXTRA_SESSION_ID,-2)!=state().getInt("session",-1))return;
            int status=intent.getIntExtra(PackageInstaller.EXTRA_STATUS,PackageInstaller.STATUS_FAILURE);
            android.util.Log.i("StationUpdate","event=installer-result status="+status);
            if(status==PackageInstaller.STATUS_PENDING_USER_ACTION){
                Intent confirmation=intent.getParcelableExtra(Intent.EXTRA_INTENT);
                if(confirmation==null)throw new IOException("UPDATE_CONFIRMATION");
                pendingConfirmation=confirmation;message="Confirme a atualização no Android.";changed();MAIN.post(StationAppUpdater::launchConfirmation);
                StationAppUpdateService.pendingNotice(context,confirmation);
                return;
            }
            busy=false;installing=false;pendingConfirmation=null;state().edit().remove("nonce").remove("session").apply();
            message=status==PackageInstaller.STATUS_SUCCESS?"Aplicativo atualizado.":
                status==PackageInstaller.STATUS_FAILURE_ABORTED?"Atualização cancelada.":
                status==PackageInstaller.STATUS_FAILURE_STORAGE?"Libere espaço no telefone para concluir a atualização.":
                status==PackageInstaller.STATUS_FAILURE_BLOCKED?"O Android bloqueou a instalação. Confira a permissão de atualização do aplicativo.":
                status==PackageInstaller.STATUS_FAILURE_INCOMPATIBLE?"Esta atualização não é compatível com o aparelho.":
                "O Android não concluiu a atualização. Tente novamente.";
            changed();context.stopService(new Intent(context,StationAppUpdateService.class));
            StationAppUpdateService.clearNotice(context);
        }catch(Exception rejected){android.util.Log.w("StationUpdate","event=installer-result-failed type="+rejected.getClass().getSimpleName());}
    }
    static void launchConfirmation(){
        Activity activity=screen.get();Intent confirmation=pendingConfirmation;
        if(activity==null||activity.isFinishing()||activity.isDestroyed()||!activity.hasWindowFocus()||confirmation==null)return;
        try{activity.startActivity(confirmation);pendingConfirmation=null;}
        catch(RuntimeException unavailable){message="Toque em Concluir atualização para abrir a confirmação do Android.";changed();}
    }
    static boolean confirmationPending(){return pendingConfirmation!=null;}
}
