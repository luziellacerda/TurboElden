"""Static presentation guards and actual Android-API compilation; no pixel/window test."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PKG = 'java/client/src/java/org/emulationstation/frontend/station/'
BASELINE_PANEL_SHA256 = '3c11f99961f14addfa11f00c25db4755689e3567a6710424501003c3e270e31f'
BASELINE_METHOD_SHA256 = {
    "public static boolean open(": "5a9d23b83cd0065aac79839a6daca8ab056790e5e78bd2fbda4a6f64ba8cfa78",
    "public static View createContent(": "8f645a53afb7464a0389a2a142b4c0963605580996a6f47c08e074ec6db6eb7f",
    "@Override protected void onCreate(": "623aa718a55348d500955c0f214270bfa5c6c5c79baa9bfaad6ebb7678db87bd",
    "@Override public void dismiss(": "ef331573959b0755cfc498b9246942f8ef1e354a5a947f7f5dd5ac85bc6a49c3",
    "@Override protected void onAttachedToWindow(": "aad2c80bf2fabe3ed76d883a080c2bbe19ae1234ae870f9bea847dad409c1e44",
    "@Override protected void onDetachedFromWindow(": "a5c36737682da90344db5e44b21deab81d6acb42d9d6522ae8619b864590d43e",
    "void disconnect(": "1de5d1607b5a5575709bcebd562c0788796354b6c7b83e6b67f9ea1f295806ed",
    "@Override public void onGraphicsChanged(": "db6d58b0e9610cdc588859a8a3de0ad5c39efa496cce183f9aa99f330c439cdd",
    "@Override public void onCarouselStyleChanged(": "b29f36bc6868b594b266f54f1b85ae3c745b9398254f13b63a78ea9262438313"
}

SURFACE_FIXTURE = r'''
import java.util.*;
public final class PanelSurfaceHost {
    static final class android {
        static final class graphics {
            static final class Color { static int alpha(int value){return value>>>24;} }
            static final class PixelFormat {static final int TRANSLUCENT=-3;}
            static final class ColorFilter {}
            static final class Rect {int left,top,right,bottom;Rect(int l,int t,int r,int b){left=l;top=t;right=r;bottom=b;}int height(){return bottom-top;}}
            static final class RectF {float left,top,right,bottom;void set(float l,float t,float r,float b){left=l;top=t;right=r;bottom=b;}}
            static final class Paint {
                static final int ANTI_ALIAS_FLAG=1;enum Style {FILL,STROKE} int color,alpha;Style style;
                Paint(int flags){}void setStyle(Style value){style=value;}void setColor(int value){color=value;alpha=value>>>24;}
                void setAlpha(int value){alpha=value;}void setStrokeWidth(float value){}void setColorFilter(ColorFilter filter){}
            }
            static final class Canvas {
                final ArrayList<int[]> calls=new ArrayList<>();
                void drawRoundRect(RectF rect,float x,float y,Paint paint){record(paint);}
                void drawRoundRect(float l,float t,float r,float b,float x,float y,Paint paint){record(paint);}
                void record(Paint paint){calls.add(new int[]{paint.color,paint.alpha,paint.style==Paint.Style.FILL?0:1});}
            }
            static final class drawable {
                abstract static class Drawable {
                    void setBounds(graphics.Rect rect){onBoundsChange(rect);}protected void onBoundsChange(graphics.Rect rect){}
                    public abstract void draw(graphics.Canvas canvas);public void setAlpha(int value){}
                    public void setColorFilter(graphics.ColorFilter filter){}public int getOpacity(){return 0;}void invalidateSelf(){}
                }
            }
        }
    }
__SURFACE__
    static int checks;static void check(boolean value){if(!value)throw new AssertionError();checks++;}
    public static void main(String[] args){
        int[] colors={0,0x0000ff00,0xff101a27,0x80123456,0x0146dbff,0x2046dbff};
        int[] alphas={0,1,64,128,255};
        for(int fill:colors)for(int rim:colors)for(int rail:colors)for(int alpha:alphas){
            ConsoleSurface surface=new ConsoleSurface(fill,rim,rail,2.5f);
            surface.setBounds(new android.graphics.Rect(0,0,400,120));surface.setAlpha(alpha);
            android.graphics.Canvas canvas=new android.graphics.Canvas();surface.draw(canvas);
            ArrayList<int[]> expected=new ArrayList<>();
            int[] channels={fill,rim,rail};
            for(int channel=0;channel<3;channel++){
                int value=(channels[channel]>>>24)*alpha/255;
                if(value>0)expected.add(new int[]{channels[channel],value,channel==1?1:0});
            }
            check(canvas.calls.size()==expected.size());
            for(int i=0;i<expected.size();i++)check(Arrays.equals(canvas.calls.get(i),expected.get(i)));
            // Repeated draws must not inherit a prior Paint alpha/color.
            surface.setAlpha(255);canvas.calls.clear();surface.draw(canvas);
            expected.clear();for(int channel=0;channel<3;channel++)if((channels[channel]>>>24)>0)expected.add(new int[]{channels[channel],channels[channel]>>>24,channel==1?1:0});
            check(canvas.calls.size()==expected.size());
            for(int i=0;i<expected.size();i++)check(Arrays.equals(canvas.calls.get(i),expected.get(i)));
        }
        System.out.println(checks);
    }
}
'''

def long_path(path):
    return Path('\\\\?\\' + os.path.abspath(path)) if os.name == 'nt' else Path(path)

def method(source, signature):
    begin = source.index(signature)
    brace = source.index('{', begin)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == '{': depth += 1
        elif source[index] == '}':
            depth -= 1
            if depth == 0: return source[begin:index+1]
    raise AssertionError('Unclosed method: ' + signature)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--jdk-bin', type=Path, required=True)
    parser.add_argument('--android-jar', type=Path, required=True)
    parser.add_argument('--client-jar', type=Path, required=True)
    parser.add_argument('--baseline-panel', type=Path)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    path = ROOT / PKG / 'StationGraphicsPanel.java'
    raw = long_path(path).read_bytes()
    source = raw.decode('utf-8').replace('\r\n', '\n')
    baseline = None
    if args.baseline_panel:
        baseline_raw = long_path(args.baseline_panel).read_bytes()
        assert hashlib.sha256(baseline_raw).hexdigest() == BASELINE_PANEL_SHA256
        baseline = baseline_raw.decode('utf-8').replace('\r\n', '\n')
    guards = []
    def check(name, value):
        assert value, name
        guards.append(name)
    for signature in ('public static boolean open(', 'public static View createContent(',
                      '@Override protected void onCreate(', '@Override public void dismiss(',
                      '@Override protected void onAttachedToWindow(', '@Override protected void onDetachedFromWindow(',
                      'void disconnect(', '@Override public void onGraphicsChanged(',
                      '@Override public void onCarouselStyleChanged('):
        check('unchanged lifecycle/API: '+signature, hashlib.sha256(method(source,signature).encode('utf-8')).hexdigest()==BASELINE_METHOD_SHA256[signature])
    for handler in (
        'master.setOnCheckedChangeListener((button,checked)->{if(!updating)preferences.setMasterDisabled(!checked);});',
        'masterSurface.setOnClickListener(v->master.setChecked(!master.isChecked()));',
        'backgrounds.setOnCheckedChangeListener((group,id)->{if(!updating&&id>=MODE_ID&&id<=MODE_ID+2)preferences.setBackgroundMode(id-MODE_ID);});',
        'toggle.setOnCheckedChangeListener((button,checked)->{if(!updating)preferences.setEnabled(effect,checked);});',
        'card.setOnClickListener(v->{if(toggle.isEnabled())toggle.setChecked(!toggle.isChecked());});'):
        check('preserved preference handler: '+handler.split('.')[0],handler in source and (baseline is None or handler in baseline))
    check('carousel third choice delegates existing setter', 'id<=STYLE_ID+2)carouselPreferences.setStyle(id-STYLE_ID)' in source)
    check('three exact carousel labels', 'String[] styleNames={"Reta","Diagonal","De lado"};' in source)
    check('three exact environment labels', 'String[] names={"Ondas","Céu","Desligado"};' in source)
    check('LATERAL hint uses coordinated enum', 'style==StationCarouselStylePreferences.LATERAL?"Perspectiva nas células sem destaque."' in source)
    check('option choices retained during economy', 'option.toggle.setChecked(chosen);option.toggle.setEnabled(!state.masterDisabled)' in source)
    check('style gate remains CELL_EFFECTS', 'boolean enabled=state.isEnabled(StationGraphicsPreferences.CELL_EFFECTS)' in source)
    check('no repeated visual state labels', 'option.value' not in source and 'masterValue' not in source)
    check('slim segment visible face, touch48', 'new android.graphics.drawable.InsetDrawable(states,0,dp(8),0,dp(8))' in source and 'new RadioGroup.LayoutParams(0,dp(48),1)' in source)
    check('switch touch48 retained', 'view.setMinHeight(dp(48))' in source and 'new LinearLayout.LayoutParams(dp(52),dp(48))' in source)
    check('flat compact rows', 'card.setMinimumHeight(dp(48))' in source and 'effectsList.addView(option(' in source)
    check('master48dp without vertical padding', 'masterSurface.setPadding(dp(12),0,dp(8),0);masterSurface.setMinimumHeight(dp(48))' in source)
    check('option48dp without vertical padding', 'card.setPadding(dp(4),0,dp(2),0);card.setMinimumHeight(dp(48))' in source)
    check('two responsive columns retained', 'columns.setOrientation(wide?HORIZONTAL:VERTICAL)' in source)
    check('scroll only overflow and no overscroll', 'scroll.setFillViewport(false)' in source and 'View.OVER_SCROLL_NEVER' in source)
    check('padding after segment background', source.index('button.setBackground(segmentStates());button.setPadding(')>source.index('private RadioButton choice('))
    check('static rounded surface no polygon', 'canvas.drawRoundRect' in source and 'outline.moveTo' not in source)
    check('source ARGB and drawable alpha composed', all('android.graphics.Color.alpha('+channel+')*alpha/255' in source and 'if('+channel+'Alpha>0)' in source for channel in ('fill','rim','rail')))
    check('no frame loop or background work', all(value not in source for value in ('postDelayed(', 'ValueAnimator', 'new Thread(', 'Timer(', 'requestLayout()')))
    check('unchanged graphics listener type', 'implements StationGraphicsPreferences.Listener, StationCarouselStylePreferences.Listener' in source)
    check('all six independent options present', all('StationGraphicsPreferences.'+name in source for name in ('LED','VIDEO','ICONS','CLOUDS','CELL_EFFECTS','UI_TRANSITIONS')))
    output = args.work / 'classes'
    output.mkdir(exist_ok=True)
    host = args.work/'PanelSurfaceHost.java'
    host.write_text(SURFACE_FIXTURE.replace('__SURFACE__',method(source,'private static final class ConsoleSurface extends')),encoding='utf-8')
    surface_compile=subprocess.run([str(args.jdk_bin/'javac.exe'),'-encoding','UTF-8','--release','8','-d',str(output),str(host)],capture_output=True,text=True)
    if surface_compile.returncode: raise RuntimeError(surface_compile.stdout+'\n'+surface_compile.stderr)
    surface_run=subprocess.run([str(args.jdk_bin/'java.exe'),'-cp',str(output),'PanelSurfaceHost'],capture_output=True,text=True)
    if surface_run.returncode: raise RuntimeError(surface_run.stdout+'\n'+surface_run.stderr)
    surface_checks=int(surface_run.stdout.strip())
    argfile = args.work / 'javac.args'
    arguments = ['-encoding','UTF-8','--release','8','-proc:none','-cp',str(args.android_jar)+os.pathsep+str(args.client_jar),'-d',str(output),str(path),str(ROOT/PKG/'StationCarouselStylePreferences.java')]
    argfile.write_text('\n'.join('"'+a.replace('\\','/').replace('"','\\"')+'"' for a in arguments)+'\n',encoding='utf-8')
    result = subprocess.run([str(args.jdk_bin/'javac.exe'),'@'+str(argfile)],capture_output=True,text=True)
    if result.returncode: raise RuntimeError(result.stdout+'\n'+result.stderr)
    receipt = {'revision':'R123','status':'PASS','utc':datetime.now(timezone.utc).isoformat(),
               'scope':'Static guards; actual ConsoleSurface class drawn against recording host stubs; actual two Java sources compiled against Android API34. No Android view measurement, screenshot, touch, GPU, gameplay or thermal validation.',
               'sourceSHA256':hashlib.sha256(raw).hexdigest(),'baselinePanelSHA256':BASELINE_PANEL_SHA256,
               'guards':len(guards),'guardNames':guards,'actualJavaCompiled':2,'androidAPI':34,'surfaceAlphaCases':1080,'surfaceAlphaChecks':surface_checks,
               'layout':{'segmentTouchDp':48,'segmentVisualFaceDp':32,'switchTouchDp':48,'optionMinimumDp':48,'columnsLandscape':2,'visibleStateWordRepeated':False},
               'generatedOutputsKeptOutsideSnapshot':True}
    destination=ROOT/'evidence/graphics-panel-compact-r123.json'
    long_path(destination).write_text(json.dumps(receipt,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'guards':len(guards),'actualJavaCompiled':2,'surfaceAlphaChecks':surface_checks,'sourceSHA256':receipt['sourceSHA256']}))

if __name__ == '__main__': main()
