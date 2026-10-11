"""Add the DEMO guard and a human, no-game Sony settings hand-off.

The settings operation reuses the audited package/version/signer guards. Its
external Intent is a fresh official launcher request, never a file import or a
game launch. Package, signer, hardware, URI and demonstration guards remain.
Valid games dispatch directly; upstream firmware/import readiness is separate.
"""
from __future__ import annotations
import hashlib

SOURCE_SHA='e7701a030ed54a16dabdd7e66fb8cc785112722ebc747fc686e12d0ba16a5d88'

def patch(original:bytes)->bytes:
    if hashlib.sha256(original).hexdigest()!=SOURCE_SHA:
        raise ValueError('Exact audited R128 Sony Activity required')
    text=original.decode('utf-8')
    old='''            try{
                if("ps3".equals(platform))preparePs3(incoming.getData());'''
    new='''            try{
                if("settings".equals(incoming.getStringExtra("station.operation"))){
                    prepareSettings(platform);return;
                }
                if(org.emulationstation.frontend.station.StationLocalSonyDemos.isMarkedDemo(this,incoming.getData(),platform)){
                    runOnUiThread(()->demonstration(platform));return;
                }
                if("ps3".equals(platform))preparePs3(incoming.getData());'''
    if text.count(old)!=1:raise ValueError('Original Sony preparation anchor changed')
    text=text.replace(old,new,1)
    old='    private static boolean arm64()'
    new='''    /** Called only by the native settings action, with no game or URI. */
    public static boolean openSettings(Activity activity,String platform){
        if(activity==null||activity.isFinishing()||activity.isDestroyed()||
                !StationSonyOfflinePolicy.supportedPlatform(platform))return false;
        // Post the Android UI hand-off; never wait on the native rendering thread.
        activity.runOnUiThread(()->{
            if(activity.isFinishing()||activity.isDestroyed())return;
            try{
                Intent request=new Intent(activity,StationSonyOfflineActivity.class);
                request.putExtra("station.platform",platform);
                request.putExtra("station.operation","settings");
                activity.startActivity(request);
            }catch(RuntimeException unavailable){
                new AlertDialog.Builder(activity).setTitle("Configurar emulador")
                    .setMessage("Não foi possível abrir as configurações do emulador. Seus jogos e saves foram preservados.")
                    .setPositiveButton("Voltar",null).show();
            }
        });
        return true;
    }
    private void prepareSettings(String platform)throws Exception {
        final boolean ps3="ps3".equals(platform);
        final String packageName=ps3?StationSonyOfflinePolicy.PS3_PACKAGE:StationSonyOfflinePolicy.PS4_PACKAGE;
        final String launcher=ps3?"aenu.aps3e.QuickStartActivity":StationSonyOfflinePolicy.PS4_ACTIVITY;
        installed(packageName,ps3?StationSonyOfflinePolicy.PS3_VERSION:StationSonyOfflinePolicy.PS4_VERSION,
            ps3?StationSonyOfflinePolicy.PS3_VERSION_CODE:StationSonyOfflinePolicy.PS4_VERSION_CODE,
            ps3?StationSonyOfflinePolicy.PS3_CERT:StationSonyOfflinePolicy.PS4_CERT);
        component(packageName,launcher);
        // Settings screens are private upstream. Open the public launcher so
        // the user can configure the emulator there. Never copy the incoming
        // game Intent: no URI, MIME, extras, ClipData or permission grants.
        Intent target=new Intent(Intent.ACTION_MAIN);
        target.addCategory(Intent.CATEGORY_LAUNCHER);
        target.setComponent(new ComponentName(packageName,launcher));
        runOnUiThread(()->dispatch(target));
    }
    private void demonstration(String platform){
        if(closed||isFinishing())return;
        new AlertDialog.Builder(this).setTitle("Demonstração "+("ps3".equals(platform)?"PS3":"PS4"))
            .setMessage("Este arquivo é apenas um exemplo visual, identificado como DEMO. Não contém um jogo e não será enviado ao emulador. Para jogar, use seu próprio jogo.")
            .setPositiveButton("Voltar",(d,w)->finish()).setOnCancelListener(d->finish()).show();
    }
    private static boolean arm64()'''
    if text.count(old)!=1:raise ValueError('Original Sony method anchor changed')
    text=text.replace(old,new,1)
    old='''            .setMessage(ps3?"Instale o aPS3e oficial 2.43 antes de abrir um jogo de PS3.":"Instale o Bachata S4 oficial 0.2.4 antes de abrir a biblioteca de PS4.")'''
    new='''            .setMessage("settings".equals(getIntent().getStringExtra("station.operation"))?
                (ps3?"Instale o aPS3e oficial 2.43 para configurar o emulador de PS3.":"Instale o Bachata S4 oficial 0.2.4 para configurar o emulador de PS4."):
                (ps3?"Instale o aPS3e oficial 2.43 antes de abrir um jogo de PS3.":"Instale o Bachata S4 oficial 0.2.4 antes de abrir a biblioteca de PS4."))'''
    if text.count(old)!=1:raise ValueError('Original missing-emulator message changed')
    text=text.replace(old,new,1)
    old='new AlertDialog.Builder(this).setTitle("Jogar offline").setMessage(text)'
    new='new AlertDialog.Builder(this).setTitle("settings".equals(getIntent().getStringExtra("station.operation"))?"Configurar emulador":"Jogar offline").setMessage(text)'
    if text.count(old)!=1:raise ValueError('Original failure-title anchor changed')
    text=text.replace(old,new,1)
    # The user already selected Jogar. Do not add a second app confirmation or
    # repeat firmware setup instructions on every valid game launch. Upstream
    # first-run setup/import remains upstream; signer/URI/DEMO guards stay intact.
    launch='''        runOnUiThread(()->confirm("PlayStation 3","O jogo abre no aPS3e oficial. Instale o firmware nele antes de jogar. Se já houver uma partida aberta no aPS3e, encerre-a primeiro.","Abrir jogo",target));'''
    if text.count(launch)!=1:raise ValueError('Exact guarded PS3 game handoff changed')
    text=text.replace(launch,'        runOnUiThread(()->dispatch(target));',1)
    launch='''        runOnUiThread(()->confirm("PlayStation 4",pkg?
            "O pacote será importado pelo Bachata S4 oficial. Depois da importação, escolha o jogo na biblioteca do emulador para jogar.":
            "Escolha o jogo já importado na biblioteca do Bachata S4 oficial. A abertura direta aqui aceita pacotes PKG.",pkg?"Importar jogo":"Abrir biblioteca",target));'''
    if text.count(launch)!=1:raise ValueError('Exact guarded PS4 import handoff changed')
    text=text.replace(launch,'        runOnUiThread(()->dispatch(target));',1)
    return text.encode('utf-8')
