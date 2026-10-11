"""Host-only listener and presentation checks; Android/gameplay is not exercised."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'java/client/src/java/org/emulationstation/frontend/station/StationControllerPresence.java'
STUBS = {
 'android/content/Context.java': '''package android.content; public class Context {public static final String INPUT_SERVICE="input"; public Object getSystemService(String key){return null;}}''',
 'android/os/Bundle.java': 'package android.os; public class Bundle {}',
 'android/os/Looper.java': 'package android.os; public class Looper {public static Looper getMainLooper(){return new Looper();}}',
 'android/os/Handler.java': 'package android.os; public class Handler {public Handler(Looper l){} public boolean post(Runnable r){r.run(); return true;}}',
 'android/os/SystemClock.java': 'package android.os; public class SystemClock {public static long uptimeMillis(){return 1;}}',
 'android/view/MotionEvent.java': 'package android.view; public class MotionEvent {public static final int ACTION_CANCEL=3; public static MotionEvent obtain(long a,long b,int c,float d,float e,int f){return new MotionEvent();} public void recycle(){}}',
 'android/view/InputDevice.java': '''package android.view; public class InputDevice {public static final int SOURCE_GAMEPAD=1025,SOURCE_JOYSTICK=16777232; final int sources; final boolean virtual; public InputDevice(int s,boolean v){sources=s;virtual=v;} public int getSources(){return sources;}public boolean isVirtual(){return virtual;}}''',
 'android/hardware/input/InputManager.java': '''package android.hardware.input; import android.view.InputDevice; import android.os.Handler; import java.util.*; public class InputManager {public interface InputDeviceListener {void onInputDeviceAdded(int i);void onInputDeviceRemoved(int i);void onInputDeviceChanged(int i);}public Map<Integer,InputDevice> devices=new HashMap<>();public InputDeviceListener listener; public int registers,unregisters;public int[] getInputDeviceIds(){return devices.keySet().stream().mapToInt(x->x).toArray();}public InputDevice getInputDevice(int i){return devices.get(i);}public void registerInputDeviceListener(InputDeviceListener l,Handler h){listener=l;registers++;}public void unregisterInputDeviceListener(InputDeviceListener l){if(listener==l)listener=null;unregisters++;}public void add(int id,InputDevice d){devices.put(id,d);if(listener!=null)listener.onInputDeviceAdded(id);}public void remove(int id){devices.remove(id);if(listener!=null)listener.onInputDeviceRemoved(id);}public void changed(int id,InputDevice d){devices.put(id,d);if(listener!=null)listener.onInputDeviceChanged(id);}}''',
 'android/view/ViewTreeObserver.java': '''package android.view; public class ViewTreeObserver {public interface OnGlobalLayoutListener{void onGlobalLayout();}public OnGlobalLayoutListener listener;public void addOnGlobalLayoutListener(OnGlobalLayoutListener l){listener=l;}public void removeOnGlobalLayoutListener(OnGlobalLayoutListener l){if(listener==l)listener=null;}public boolean isAlive(){return true;}public void layout(){if(listener!=null)listener.onGlobalLayout();}}''',
 'android/view/View.java': '''package android.view; public class View {public static final int VISIBLE=0,INVISIBLE=4,GONE=8;private int visibility=VISIBLE;private final ViewTreeObserver observer=new ViewTreeObserver(); public int cancels;public int getVisibility(){return visibility;}public void setVisibility(int v){visibility=v;}public boolean dispatchTouchEvent(MotionEvent e){cancels++;return true;}public ViewTreeObserver getViewTreeObserver(){return observer;}}''',
 'android/view/ViewGroup.java': '''package android.view; import java.util.*;public class ViewGroup extends View {public List<View> children=new ArrayList<>();public int getChildCount(){return children.size();}public View getChildAt(int i){return children.get(i);}}''',
 'android/view/Window.java': 'package android.view; public class Window {public final ViewGroup decor=new ViewGroup();public View getDecorView(){return decor;}}',
 'android/app/Activity.java': '''package android.app;import android.content.Context;import android.hardware.input.InputManager;import android.view.Window;public class Activity extends Context {public final InputManager input=new InputManager();public final Window window=new Window();@Override public Object getSystemService(String k){return input;}public Window getWindow(){return window;}}''',
 'android/app/Application.java': '''package android.app;import android.content.Context;import android.os.Bundle;import java.util.*;public class Application extends Context {public interface ActivityLifecycleCallbacks {void onActivityCreated(Activity a,Bundle b);void onActivityStarted(Activity a);void onActivityResumed(Activity a);void onActivityPaused(Activity a);void onActivityStopped(Activity a);void onActivityDestroyed(Activity a);void onActivitySaveInstanceState(Activity a,Bundle b);}public List<ActivityLifecycleCallbacks> callbacks=new ArrayList<>();public void registerActivityLifecycleCallbacks(ActivityLifecycleCallbacks l){callbacks.add(l);}@Override public Object getSystemService(String k){throw new IllegalStateException("Application not attached");}}''',
 'org/dolphinemu/dolphinemu/activities/EmulationActivity.java': 'package org.dolphinemu.dolphinemu.activities;public class EmulationActivity extends android.app.Activity {}',
 'org/dolphinemu/dolphinemu/overlay/InputOverlay.java': '''package org.dolphinemu.dolphinemu.overlay; public class InputOverlay extends android.view.View {public int releases,refreshes;public boolean failRelease;public void onDestroy(){if(failRelease)throw new IllegalStateException("fake unavailable native");releases++;}public void refreshControls(){refreshes++;}}''',
}
TEST = r'''package org.emulationstation.frontend.station;
import android.app.*;import android.view.*;import org.dolphinemu.dolphinemu.activities.EmulationActivity;import org.dolphinemu.dolphinemu.overlay.InputOverlay;
public class PresenceTest {
static int checks; static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
static InputDevice pad(){return new InputDevice(InputDevice.SOURCE_GAMEPAD,false);}
public static void main(String[] args){
 int[] rejects={0,1,257,513,4098,8194,2,16,1024,16777216};
 for(int s:rejects){check(!StationControllerPresence.isController(s,false));check(!StationControllerPresence.isController(s,true));}
 int[] accepts={1025,16777232,1025|257,1025|16777232};
 for(int s:accepts){check(StationControllerPresence.isController(s,false));check(!StationControllerPresence.isController(s,true));}
 check(!StationControllerPresence.shouldHide(false,1));check(!StationControllerPresence.shouldHide(true,0));check(StationControllerPresence.shouldHide(true,1));check(StationControllerPresence.shouldHide(true,4));
 Application app=new Application();StationControllerPresence.install(app);StationControllerPresence.install(app);check(app.callbacks.size()==1);
 Application.ActivityLifecycleCallbacks cb=app.callbacks.get(0);Activity unrelated=new Activity();cb.onActivityResumed(unrelated);check(unrelated.input.registers==0);
 EmulationActivity a=new EmulationActivity();View game=new View();InputOverlay o=new InputOverlay();a.window.decor.children.add(game);a.window.decor.children.add(o);
 cb.onActivityResumed(a);check(a.input.registers==1);check(o.getVisibility()==View.VISIBLE);check(o.releases==0);
 a.input.add(1,new InputDevice(257,false));check(o.getVisibility()==View.VISIBLE);a.input.add(2,new InputDevice(1025,true));check(o.getVisibility()==View.VISIBLE);
 a.input.add(3,pad());check(o.getVisibility()==View.INVISIBLE);check(o.releases==1);check(o.cancels==1);check(game.getVisibility()==View.VISIBLE);
 for(int i=0;i<1000;i++)a.window.decor.getViewTreeObserver().layout();check(o.releases==1);check(o.cancels==1);check(o.refreshes==0);
 cb.onActivityResumed(a);check(a.input.registers==1);check(o.releases==1);
 a.input.add(4,new InputDevice(16777232,false));a.input.remove(3);check(o.getVisibility()==View.INVISIBLE);check(o.refreshes==0);
 a.input.remove(4);check(o.getVisibility()==View.VISIBLE);check(o.refreshes==1);check(game.cancels==0);
 a.input.add(5,pad());check(o.releases==2);a.input.changed(5,new InputDevice(257,false));check(o.getVisibility()==View.VISIBLE);check(o.refreshes==2);
 a.input.changed(5,pad());check(o.releases==3);cb.onActivityPaused(a);check(o.getVisibility()==View.VISIBLE);check(o.refreshes==3);check(a.input.listener==null);check(a.window.decor.getViewTreeObserver().listener==null);
 cb.onActivityDestroyed(a);check(o.refreshes==3);
 cb.onActivityResumed(a);check(o.getVisibility()==View.INVISIBLE);check(o.releases==4);o.setVisibility(View.GONE);a.input.remove(5);check(o.getVisibility()==View.GONE);cb.onActivityPaused(a);
 o.setVisibility(View.VISIBLE);o.failRelease=true;a.input.add(6,pad());cb.onActivityResumed(a);check(o.getVisibility()==View.VISIBLE);check(o.releases==4);check(o.refreshes==5);cb.onActivityPaused(a);
 System.out.println("PASS "+checks+" checks (host stubs, no Android/gameplay)");
}}
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    jdk = args.jdk / 'bin' if (args.jdk / 'bin/javac.exe').is_file() else args.jdk
    with tempfile.TemporaryDirectory(prefix='station-presence-r120-') as work:
        work = Path(work)
        for name, source in STUBS.items():
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding='utf-8')
        target = work / 'org/emulationstation/frontend/station/StationControllerPresence.java'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(SOURCE.read_bytes())
        (target.parent / 'PresenceTest.java').write_text(TEST, encoding='utf-8')
        response = work / 'sources.txt'
        response.write_text('\n'.join('"' + str(p).replace('\\', '/') + '"' for p in work.rglob('*.java')), encoding='utf-8')
        subprocess.run([str(jdk / 'javac.exe'), '-d', str(work / 'classes'), '@' + str(response)], check=True)
        output = subprocess.check_output([str(jdk / 'java.exe'), '-cp', str(work / 'classes'), 'org.emulationstation.frontend.station.PresenceTest'], text=True).strip()
    print(output)
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps({'scope':'host-only Android API stubs; no phone or gameplay', 'result':output, 'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'recipeSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'productionSourceCompiledUnmodified':True}, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()
