"""Host-only checks of the real wave View/preferences and native RGB helpers.

Android stubs exercise state/listener lifecycle, not Android rendering or JNI.
Temporary classes/executables stay outside the public snapshot.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "java/client/src/java/org/emulationstation/frontend/station"
STUBS = {
    "android/content/Context.java": """package android.content;
public class Context { public static final int MODE_PRIVATE=0; private final java.util.Map<String,SharedPreferences> files=new java.util.HashMap<>();
 public Context getApplicationContext(){return this;} public SharedPreferences getSharedPreferences(String name,int mode){return files.computeIfAbsent(name,k->new SharedPreferences());} }""",
    "android/content/SharedPreferences.java": """package android.content;
public class SharedPreferences { public interface OnSharedPreferenceChangeListener{void onSharedPreferenceChanged(SharedPreferences p,String key);}
 private final java.util.Map<String,Object> values=new java.util.HashMap<>(); public final java.util.Set<OnSharedPreferenceChangeListener> listeners=new java.util.HashSet<>(); public int reads;
 public int getInt(String k,int d){reads++;Object v=values.get(k);return v instanceof Integer?(Integer)v:d;}
 public long getLong(String k,long d){reads++;Object v=values.get(k);return v instanceof Long?(Long)v:d;}
 public boolean getBoolean(String k,boolean d){reads++;Object v=values.get(k);return v instanceof Boolean?(Boolean)v:d;}
 public Editor edit(){return new Editor();} public void registerOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener l){listeners.add(l);} public void unregisterOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener l){listeners.remove(l);}
 public class Editor {private final java.util.Map<String,Object> pending=new java.util.HashMap<>(); public Editor putInt(String k,int v){pending.put(k,v);return this;} public Editor putLong(String k,long v){pending.put(k,v);return this;} public Editor putBoolean(String k,boolean v){pending.put(k,v);return this;}
 public boolean commit(){values.putAll(pending);for(String k:pending.keySet())for(OnSharedPreferenceChangeListener l:new java.util.ArrayList<>(listeners))l.onSharedPreferenceChanged(SharedPreferences.this,k);return true;} public void apply(){commit();} }
}""",
    "android/os/Looper.java": "package android.os; public class Looper {public static Looper getMainLooper(){return new Looper();}}",
    "android/os/Handler.java": "package android.os; public class Handler {public Handler(Looper l){} public boolean post(Runnable r){r.run();return true;}}",
    "android/util/Log.java": "package android.util; public class Log {public static int w(String t,String m){return 0;}}",
    "android/graphics/Shader.java": "package android.graphics; public class Shader {public enum TileMode{CLAMP}}",
    "android/graphics/LinearGradient.java": "package android.graphics; public class LinearGradient extends Shader {public static int created;public final int top,bottom;public LinearGradient(float x,float y,float z,float w,int t,int b,TileMode mode){top=t;bottom=b;created++;}}",
    "android/graphics/Paint.java": "package android.graphics; public class Paint {public static final int ANTI_ALIAS_FLAG=1;public Shader shader;public Paint(int f){} public void setShader(Shader s){shader=s;}}",
    "android/graphics/Path.java": "package android.graphics; public class Path {public void reset(){} public void moveTo(float x,float y){} public void lineTo(float x,float y){} public void close(){}}",
    "android/graphics/Canvas.java": "package android.graphics; public class Canvas {public int color,paths;public void drawColor(int c){color=c;} public void drawPath(Path p,Paint b){paths++;}}",
    "android/view/View.java": """package android.view; import android.content.Context;import android.graphics.Canvas;
public class View {public static final int IMPORTANT_FOR_ACCESSIBILITY_NO=2,VISIBLE=0;public int width=800,height=400,invalidates;public boolean shown=true,focus=true;public final java.util.Set<Runnable> callbacks=new java.util.HashSet<>();
 public View(Context c){} public void setImportantForAccessibility(int i){} protected void onSizeChanged(int w,int h,int ow,int oh){width=w;height=h;} protected void onDraw(Canvas c){} protected void onAttachedToWindow(){} protected void onDetachedFromWindow(){}
 protected void onVisibilityChanged(View v,int i){} protected void onWindowVisibilityChanged(int i){} public void onWindowFocusChanged(boolean f){focus=f;}
 public int getHeight(){return height;} public int getWidth(){return width;} public boolean isShown(){return shown;}public int getWindowVisibility(){return VISIBLE;} public boolean hasWindowFocus(){return focus;}
 public boolean post(Runnable r){r.run();return true;} public boolean postDelayed(Runnable r,long t){if(t!=34L)throw new AssertionError("FPS changed");callbacks.add(r);return true;}public boolean removeCallbacks(Runnable r){callbacks.remove(r);return true;} public void invalidate(){invalidates++;}}
""",
}

HARNESS = r"""package org.emulationstation.frontend.station;
import android.content.*;import android.graphics.*;import java.lang.reflect.*;
public final class WaveThemeR122Test {
 static int checks;static void check(boolean b,String m){checks++;if(!b)throw new AssertionError(m);}
 static Object field(Object v,String n)throws Exception{Field f=v.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(v);}
 static void call(Object v,String n,Class<?>[] t,Object... a)throws Exception{Method m=v.getClass().getDeclaredMethod(n,t);m.setAccessible(true);m.invoke(v,a);}
 static void attach(StationWaveBackground v)throws Exception{call(v,"onAttachedToWindow",new Class<?>[0]);}
 static void detach(StationWaveBackground v)throws Exception{call(v,"onDetachedFromWindow",new Class<?>[0]);}
 static Canvas draw(StationWaveBackground v)throws Exception{Canvas c=new Canvas();call(v,"onDraw",new Class<?>[]{Canvas.class},c);return c;}
 static int top(StationWaveBackground v,int i)throws Exception{return ((LinearGradient)((Paint[])field(v,"paints"))[i].shader).top;}
 public static void main(String[] unused)throws Exception {
  Context context=new Context();SharedPreferences saved=context.getSharedPreferences("station_appearance",0);
  StationGraphicsPreferences prefs=StationGraphicsPreferences.get(context);StationWaveBackground v=new StationWaveBackground(context);
  call(v,"onSizeChanged",new Class<?>[]{int.class,int.class,int.class,int.class},800,400,0,0);attach(v);
  check(!(Boolean)field(v,"blue"),"default follows existing black theme");check(draw(v).color==0xff000000,"dark fill");check(draw(v).paths==3,"three dark waves");check(top(v,0)==0x203b4b59,"dark gradient");check(saved.listeners.size()==1,"one appearance listener");check(v.callbacks.size()==1,"bounded 30fps callback");
  int reads=saved.reads,gradients=LinearGradient.created;for(int i=0;i<30;i++)draw(v);check(saved.reads==reads,"no preference read per draw");check(LinearGradient.created==gradients,"no gradient build per draw");
  saved.edit().putInt("theme",1).commit();check((Boolean)field(v,"blue"),"live blue preference");check(draw(v).color==0xff050a15,"original blue fill");check(top(v,0)==0x2029acff&&top(v,1)==0x185782ff&&top(v,2)==0x1838d9e8,"original blue gradients");check(v.callbacks.size()==1,"theme adds no callback loop");
  gradients=LinearGradient.created;for(int i=0;i<4;i++)saved.edit().putInt("theme",1).commit();check(LinearGradient.created==gradients,"same theme does not rebuild");
  reads=saved.reads;int invalidates=v.invalidates;saved.edit().putInt("unrelated",3).commit();check(saved.reads==reads&&v.invalidates==invalidates,"unrelated key ignored");
  detach(v);check(saved.listeners.isEmpty(),"detach removes preference listener");check(v.callbacks.isEmpty(),"detach cancels callback");check(!(Boolean)field(v,"framePending"),"detach clears pending frame");saved.edit().putInt("theme",0).commit();check((Boolean)field(v,"blue"),"detached view receives no callback");
  attach(v);check(!(Boolean)field(v,"blue"),"reattach reads persisted dark theme");check(draw(v).color==0xff000000,"reattach dark fill");check(saved.listeners.size()==1,"reattach listener once");
  StationWaveBackground second=new StationWaveBackground(context);call(second,"onSizeChanged",new Class<?>[]{int.class,int.class,int.class,int.class},800,400,0,0);check(!(Boolean)field(second,"blue")&&draw(second).color==0xff000000,"new view reads persisted theme");
  long revision=prefs.revision();saved.edit().putInt("theme",1).commit();check(prefs.revision()==revision,"theme does not mutate graphics revision");check(prefs.backgroundMode()==StationGraphicsPreferences.WAVES&&prefs.individualMask()==StationGraphicsPreferences.ALL,"background choice and mask preserved");
  prefs.setMasterDisabled(true);check(v.callbacks.isEmpty()&&!(Boolean)field(v,"allowed"),"economy still cancels waves");check(draw(v).paths==0,"no ribbons when economy off");saved.edit().putInt("theme",0).commit();check(v.callbacks.isEmpty(),"color cannot restart disabled animation");prefs.setMasterDisabled(false);check(v.callbacks.size()==1&&(Boolean)field(v,"allowed"),"economy restores original callback policy");
  v.onWindowFocusChanged(false);check(v.callbacks.isEmpty(),"focus loss cancels");v.onWindowFocusChanged(true);check(v.callbacks.size()==1,"focus gain restores");prefs.setBackgroundMode(StationGraphicsPreferences.SKY);check(v.callbacks.isEmpty(),"sky stops Java waves");check(saved.getInt("theme",-1)==0,"sky selection preserves theme");prefs.setBackgroundMode(StationGraphicsPreferences.OFF);check(v.callbacks.isEmpty(),"off stops Java waves");detach(v);check(saved.listeners.isEmpty(),"final detach releases listener");
  System.out.println("PASS "+checks);
 }
}
"""


def run(command):
    result = subprocess.run([str(value) for value in command], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def native_body(source, name):
    match = re.search(r"static unsigned " + re.escape(name) + r"\([^)]*\)\{", source)
    if not match:
        raise RuntimeError("Missing real helper: " + name)
    level = 1
    end = match.end()
    while level:
        if source[end] == "{": level += 1
        elif source[end] == "}": level -= 1
        end += 1
    return source[match.start():end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--clang", type=Path, required=True)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    jdk = args.jdk / "bin" if (args.jdk / "bin/javac.exe").exists() else args.jdk
    with tempfile.TemporaryDirectory(prefix="wave-theme-r122-", dir=args.work) as directory:
        work = Path(directory)
        paths = []
        for relative, content in STUBS.items():
            path = work / relative; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8"); paths.append(path)
        harness = work / "WaveThemeR122Test.java"; harness.write_text(HARNESS, encoding="utf-8"); paths.append(harness)
        paths += [JAVA / "StationGraphicsPreferences.java", JAVA / "StationWaveBackground.java"]
        response = work / "sources.args"
        response.write_text("\n".join('"' + str(p).replace('\\', '/') + '"' for p in paths), encoding="utf-8")
        run([jdk / "javac.exe", "--release", "8", "-encoding", "UTF-8", "-proc:none", "-d", work / "classes", "@" + str(response)])
        java_output = run([jdk / "java.exe", "-cp", work / "classes", "org.emulationstation.frontend.station.WaveThemeR122Test"])
        source = (ROOT / "native/d0/native_space.h").read_text(encoding="utf-8")
        cpp = "#include <cstdio>\nstatic int stationThemeId;\n" + "\n".join(native_body(source, name) for name in ["stationWaveTop", "stationWaveBottom", "stationWaveColor"])
        cpp += r"""
int main(){int checks=0;for(int theme=0;theme<2;theme++){stationThemeId=theme;
 const unsigned blue[]={0x65BFF030u,0x6587DE26u,0x9DCBDD1Eu},dark[]={0x8193A630u,0x59677526u,0x9DA8B11Eu};
 if(stationWaveTop()!=(theme?0x050A15ffu:0x000000ffu))return 1;checks++;
 if(stationWaveBottom()!=(theme?0x081827ffu:0x07090Dffu))return 2;checks++;
 for(int i=0;i<3;i++){if(stationWaveColor(i)!=(theme?blue[i]:dark[i]))return 3;checks++;if((stationWaveColor(i)&255u)!=(blue[i]&255u))return 4;checks++;}}
 std::printf("PASS %d\n",checks);}
"""
        native = work / "waves.cpp"; native.write_text(cpp, encoding="utf-8")
        run([args.clang, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", native, "-o", work / "waves.exe"])
        native_output = run([work / "waves.exe"])
        java_checks = int(re.fullmatch(r"PASS (\d+)", java_output)[1]); native_checks = int(re.fullmatch(r"PASS (\d+)", native_output)[1])
    files = ["native/d0/native_space.h", "native/d0/native_settings.h", "java/client/src/java/org/emulationstation/frontend/station/StationWaveBackground.java", "tests/verify_wave_theme_r122.py"]
    receipt = {"version":"R122", "utc":datetime.datetime.now(datetime.timezone.utc).isoformat(), "passed":True,
               "javaStateAndLifecycleChecks":java_checks, "nativePaletteChecks":native_checks,
               "sourceSHA256":{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
               "existingAppearancePreference":"station_appearance/theme", "newPreference":False,
               "limits":["Host-only Android stubs; not visual rendering on a phone.","Native palette helpers are extracted verbatim; not a complete GLES renderer.","No physical, thermal or gameplay validation."]}
    destination = ROOT / "evidence/wave-theme-r122.json"
    destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"passed":True,"javaChecks":java_checks,"nativeChecks":native_checks,"receipt":str(destination)},ensure_ascii=False))


if __name__ == "__main__":
    main()
