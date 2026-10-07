"""Source/lifecycle guards only; this does not claim to render an Android Dialog."""
from pathlib import Path
import hashlib

snapshot=Path(__file__).resolve().parents[1]
versions=snapshot.parent
name='org/emulationstation/frontend/netplay/StationRetroActivity.java'
old=(versions/'station-native-registration-r72-20261007/java/netplay-src'/name).read_text('utf8')
current=(snapshot/'java/netplay-src'/name).read_text('utf8')
tunnel=(snapshot/'java/netplay-src/org/emulationstation/frontend/netplay/StationRecoveryTunnel.java').read_text('utf8')
checks=0
def check(value,message):
    global checks
    checks+=1
    if not value:raise AssertionError(message)
def method(text,start):
    pos=text.index(start);begin=text.index('{',pos);level=0
    for end in range(begin,len(text)):
        if text[end]=='{':level+=1
        if text[end]=='}':
            level-=1
            if level==0:return text[pos:end+1]
    raise AssertionError('unterminated method '+start)

create=method(current,'private void createRecoveryPanel(')
draw=method(current,'private void drawRecovery(')
dismiss=method(current,'private void dismissRecoveryPanel(')
check('new Dialog(this)' in create,'application Dialog owns a separate window')
check('setOwnerActivity(this)' in create,'Dialog is owned by the native Activity')
check('setContentView(recoveryPanel)' in create,'waiting panel belongs to Dialog window')
check('addContentView(recoveryPanel' not in current,'waiting panel is not an EGL-window child')
check('FLAG_NOT_FOCUSABLE' in create,'waiting window preserves native focus and Back ownership')
check('FLAG_NOT_TOUCHABLE' not in create,'human exit button remains touchable')
check('setCancelable(false)' in create and 'setCanceledOnTouchOutside(false)' in create,'no implicit outside/Back cancellation')
check('exit.setOnClickListener(v->confirmExit())' in create,'waiting exit still requires human confirmation')
for guard in ['!visible','!recoveryWaiting','sessionFinished','isFinishing()','isDestroyed()']:
    check(guard in draw, 'visibility guard '+guard)
check(draw.index('dismissRecoveryPanel();return;')<draw.index('createRecoveryPanel();'),'guards precede allocation/show')
check('if(!recoveryDialog.isShowing())' in draw,'repeated status callbacks do not repeatedly show window')
for ref in ['recoveryDialog','recoveryPanel','recoveryText','recoveryProgress']:
    check(ref+'=null' in dismiss,'release '+ref)
check('dialog.dismiss()' in dismiss,'release attached window on hide')
check('close(' not in dismiss and 'finish(' not in dismiss and 'sessionEvents' not in dismiss,'visual dismissal cannot end or signal session')
stop=method(current,'@Override protected void onStop(')
check(stop.index('visible=false')<stop.index('drawRecovery()'),'onStop makes dialog dismiss without exiting session')
check('dismissRecoveryPanel();' in method(current,'@Override protected void onDestroy('),'destroy also drops window references')
for signature in ['@Override protected void onStart(', 'private synchronized void closeSession(', '@Override public void finish(', '@Override public void onBackPressed(', '@Override public boolean dispatchKeyEvent(', 'private void installOnlineMenuButton(', 'private void showExitMenu(', 'private void confirmExit(']:
    check(method(old,signature)==method(current,signature),'preserve original behavior '+signature)
check('System.loadLibrary("station_retroarch");stationRecoveryStatus();stationRecoveryStalled();' in current,'R72 JNI registration retained')
trace=method(tunnel,'private void traceWaiting(')
check('catch(RuntimeException ignored)' in trace and 'fatal(' not in trace,'diagnostics are non-terminal')
for field in ['!foreground','!welcome','!remote.isOpen()','!waitDiagnostics.due(now)']:
    check(field in trace,'diagnostics skipped for '+field)
check('pump();traceWaiting(now);' in tunnel,'transport pumping remains independent and first')
check('if(state==2)waitDiagnostics.reset()' in tunnel,'playing transition resets diagnostic budget')
print(f'wait_panel_source_test: {checks} checks passed; Android visual rendering remains unverified')
