"""Execute the real exit panel with recording UI stubs; compile against API34.

Host-only callbacks/tree checks are not Android layout, gameplay or saves tests.
"""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGE='org/emulationstation/frontend/netplay'
SOURCE=ROOT/'java/netplay-src'/PACKAGE/'StationExitPanel.java'

STUBS={
'android/content/Context.java': '''package android.content; public class Context { public android.content.res.Resources getResources(){return null;} }''',
'android/content/DialogInterface.java': '''package android.content; public interface DialogInterface { interface OnShowListener {void onShow(DialogInterface d);} }''',
'android/content/res/Resources.java': '''package android.content.res; public class Resources {public final android.util.DisplayMetrics metrics=new android.util.DisplayMetrics(); public final Configuration config=new Configuration(); public android.util.DisplayMetrics getDisplayMetrics(){return metrics;} public Configuration getConfiguration(){return config;}}''',
'android/content/res/Configuration.java': '''package android.content.res; public class Configuration {public float fontScale=1;}''',
'android/util/DisplayMetrics.java': '''package android.util; public class DisplayMetrics {public float density=1;public int widthPixels=960,heightPixels=432;}''',
'android/app/Activity.java': '''package android.app; public class Activity extends android.content.Context {private final android.content.res.Resources r=new android.content.res.Resources();public android.content.res.Resources getResources(){return r;}}''',
'android/graphics/Typeface.java': '''package android.graphics; public class Typeface {public static Typeface create(String s,int style){return new Typeface();}}''',
'android/graphics/drawable/Drawable.java': '''package android.graphics.drawable; public class Drawable {}''',
'android/graphics/drawable/GradientDrawable.java': '''package android.graphics.drawable; public class GradientDrawable extends Drawable {public int fill,border;public float radius;public void setColor(int x){fill=x;}public void setStroke(int n,int x){border=x;}public void setCornerRadius(float x){radius=x;}}''',
'android/view/Gravity.java': '''package android.view; public class Gravity {public static final int CENTER_VERTICAL=16;}''',
'android/view/View.java': '''package android.view; public class View {public static final int IMPORTANT_FOR_ACCESSIBILITY_NO=2;public Object layout;public int backgroundColor,height=220;public android.graphics.drawable.Drawable background;public boolean focused;public OnClickListener click;public View(android.content.Context c){} public interface OnClickListener {void onClick(View v);}public void setBackground(android.graphics.drawable.Drawable d){background=d;}public void setBackgroundColor(int c){backgroundColor=c;}public void setImportantForAccessibility(int x){}public void setOnClickListener(OnClickListener l){click=l;}public void performClick(){if(click!=null)click.onClick(this);}public void requestFocus(){focused=true;}public void setContentDescription(String s){}public void setSystemUiVisibility(int n){}public void post(Runnable r){r.run();}public int getHeight(){return height;}public void setPadding(int a,int b,int c,int d){}}''',
'android/view/Window.java': '''package android.view; public class Window {public final View decor=new View(null);public int width,height;public float dim;public void setBackgroundDrawableResource(int n){}public void setDimAmount(float f){dim=f;}public void setLayout(int w,int h){width=w;height=h;}public View getDecorView(){return decor;}}''',
'android/widget/LinearLayout.java': '''package android.widget; public class LinearLayout extends android.view.View {public static final int VERTICAL=1,HORIZONTAL=0;public int orientation;public java.util.List<android.view.View> children=new java.util.ArrayList<>();public LinearLayout(android.content.Context c){super(c);}public void setOrientation(int n){orientation=n;}public void setGravity(int n){}public void addView(android.view.View v){children.add(v);}public void addView(android.view.View v,LayoutParams p){v.layout=p;children.add(v);}public static class LayoutParams {public int width,height,topMargin,leftMargin;public float weight;public LayoutParams(int w,int h){this(w,h,0);}public LayoutParams(int w,int h,float f){width=w;height=h;weight=f;}}}''',
'android/widget/ScrollView.java': '''package android.widget; public class ScrollView extends android.view.View {public android.view.View child;public ScrollView(android.content.Context c){super(c);}public void setFillViewport(boolean b){}public void setVerticalScrollBarEnabled(boolean b){}public void addView(android.view.View v){child=v;}}''',
'android/widget/TextView.java': '''package android.widget; public class TextView extends android.view.View {public String text;public float textSize;public int color;public TextView(android.content.Context c){super(c);}public void setText(String t){text=t;}public void setTextColor(int n){color=n;}public void setTextSize(float n){textSize=n;}public void setTypeface(android.graphics.Typeface f){}public void setIncludeFontPadding(boolean b){}public void setLetterSpacing(float f){}public void setLineSpacing(float x,float y){}}''',
'android/widget/ImageView.java': '''package android.widget; public class ImageView extends android.view.View {public android.graphics.drawable.Drawable image;public ImageView(android.content.Context c){super(c);}public void setImageDrawable(android.graphics.drawable.Drawable d){image=d;}}''',
'android/app/AlertDialog.java': '''package android.app; public class AlertDialog implements android.content.DialogInterface {public android.view.View content;private boolean showing;public int dismisses;public android.content.DialogInterface.OnShowListener listener;public final android.view.Window window=new android.view.Window();public void setOnShowListener(android.content.DialogInterface.OnShowListener l){listener=l;}public android.view.Window getWindow(){return window;}public boolean isShowing(){return showing;}public void dismiss(){showing=false;dismisses++;}public void show(){showing=true;if(listener!=null)listener.onShow(this);}public static class Builder {private final AlertDialog d=new AlertDialog();public Builder(Activity a){}public Builder setView(android.view.View v){d.content=v;return this;}public AlertDialog create(){return d;}}}''',
'android/R.java': '''package android;public final class R {public static final class color {public static final int transparent=0;}}''',
PACKAGE+'/StationActionButton.java': '''package org.emulationstation.frontend.netplay; final class StationActionButton extends android.view.View {static final int SECONDARY=0,PRIMARY=1,DANGER=2;final String label;final int tone,icon;StationActionButton(android.app.Activity a,String s,int t,int i){super(a);label=s;tone=t;icon=i;}}''',
PACKAGE+'/StationSocialIcon.java': '''package org.emulationstation.frontend.netplay;final class StationSocialIcon extends android.graphics.drawable.Drawable {static final int PLAY=8,EXIT=9;final int kind,size,color;StationSocialIcon(int k,int s,int c){kind=k;size=s;color=c;}}'''
}

HOST='''package org.emulationstation.frontend.netplay;
import android.app.*;import android.view.*;import android.widget.*;
public final class ExitPanelHost {
 static int cases,checks;static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
 static AlertDialog make(Activity a,boolean confirm,int[] exits){return confirm?StationExitPanel.confirm(a,()->exits[0]++):StationExitPanel.create(a,()->exits[0]++);}
 public static void main(String[] args){
  for(float density:new float[]{1,1.5f,2.5f,3})for(int widthDp:new int[]{280,320,360,392,432,640,960})for(float font:new float[]{1,1.25f,1.3f,1.5f,2})for(boolean confirm:new boolean[]{false,true}){
   cases++;Activity a=new Activity();a.getResources().metrics.density=density;a.getResources().metrics.widthPixels=Math.round(widthDp*density);a.getResources().config.fontScale=font;
   int[] exits={0};AlertDialog d=make(a,confirm,exits);LinearLayout surface=(LinearLayout)d.content;
   check(surface.orientation==LinearLayout.VERTICAL);check(surface.children.size()==3);check(surface.children.get(0) instanceof ScrollView);check(!(surface.children.get(2) instanceof ScrollView));
   ScrollView scroll=(ScrollView)surface.children.get(0);check(((LinearLayout.LayoutParams)scroll.layout).weight==1);LinearLayout body=(LinearLayout)scroll.child;
   check(body.children.size()==4);check(body.children.get(0) instanceof LinearLayout);check(((LinearLayout)body.children.get(0)).children.get(1) instanceof ImageView);
   check(((TextView)body.children.get(1)).text.equals(confirm?"Sair da partida?":"Partida online"));check(((TextView)body.children.get(2)).textSize==14);check(((TextView)body.children.get(3)).textSize==12);
   LinearLayout footer=(LinearLayout)surface.children.get(2);check(footer.children.size()==2);int expectedWidth=Math.min(Math.round(420*density),Math.max(1,a.getResources().metrics.widthPixels-Math.round(32*density)));
   boolean stacked=expectedWidth<Math.round(360*density)||font>1.25f;check(footer.orientation==(stacked?LinearLayout.VERTICAL:LinearLayout.HORIZONTAL));
   StationActionButton back=(StationActionButton)footer.children.get(0),exit=(StationActionButton)footer.children.get(1);check(back.tone==StationActionButton.PRIMARY);check(exit.tone==StationActionButton.DANGER);check(back.label.equals("Continuar"));check(exit.label.equals(confirm?"Sair da partida":"Voltar às salas"));check(exits[0]==0);
   LinearLayout.LayoutParams b=(LinearLayout.LayoutParams)back.layout,e=(LinearLayout.LayoutParams)exit.layout;check(stacked?b.height==Math.round(48*density):b.weight==1&&e.weight==1);check(stacked?e.topMargin==Math.round(8*density):e.leftMargin==Math.round(8*density));
   d.show();check(back.focused);check(d.window.width==expectedWidth);check(d.window.dim==.72f);back.performClick();check(exits[0]==0);check(!d.isShowing());
   d=make(a,confirm,exits);d.show();footer=(LinearLayout)((LinearLayout)d.content).children.get(2);((StationActionButton)footer.children.get(1)).performClick();check(!d.isShowing());check(d.dismisses==1);check(exits[0]==1);
   d=make(a,confirm,exits);d.show();d.dismiss();check(exits[0]==1);
  }
  System.out.println("PASS cases="+cases+" checks="+checks);
 }
}'''

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    p=subprocess.run(args,capture_output=True,text=True)
    if p.returncode:raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--jdk-bin',type=Path,required=True);parser.add_argument('--android-jar',type=Path,required=True);parser.add_argument('--client-jar',type=Path,required=True);parser.add_argument('--rooms-jar',type=Path,required=True);args=parser.parse_args()
    source=SOURCE.read_text(encoding='utf-8');guards=[]
    def guard(name,yes):
        if not yes:raise AssertionError(name)
        guards.append(name)
    guard('Exit callback remains a single call',source.count('exit.run();')==1)
    guard('Dismiss before caller-owned exit','dialog.dismiss();exit.run();' in source)
    guard('Continue only dismisses','0,stacked,()->dialog.dismiss()' in source)
    guard('Create API retained','static AlertDialog create(Activity activity,Runnable exit)' in source)
    guard('Confirm API retained','static AlertDialog confirm(Activity activity,Runnable exit)' in source)
    guard('Footer is outside text scroll','surface.addView(actions,actionSize)' in source and 'body.addView(actions' not in source)
    guard('Information precedes footer',source.index('if(!note.isEmpty())')<source.index('surface.addView(actions,actionSize)'))
    guard('No new renderer/network/timer',not any(s in source for s in ('BitmapFactory','MediaPlayer','postDelayed','StationApi','egl','saveState','loadState','requestHumanExit(','finish(')))
    guard('No promise of saved progress',not any(s in source.lower() for s in ('progresso salvo','jogo salvo','save automático','salvar automaticamente')))
    guard('Explicit title and human consequence','Você encerra sua participação e volta às salas.' in source)
    with tempfile.TemporaryDirectory(prefix='station-exit-refinement-') as directory:
        temporary=Path(directory);paths=[]
        for relative,value in STUBS.items():
            p=temporary/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,encoding='utf-8');paths.append(p)
        host=temporary/PACKAGE/'ExitPanelHost.java';host.write_text(HOST,encoding='utf-8');paths.extend((host,SOURCE));classes=temporary/'host-classes';classes.mkdir()
        run([str(args.jdk_bin/'javac.exe'),'-encoding','UTF-8','--release','8','-d',str(classes),*map(str,paths)])
        output=run([str(args.jdk_bin/'java.exe'),'-cp',str(classes),'org.emulationstation.frontend.netplay.ExitPanelHost'])
        production=temporary/'production-classes';production.mkdir()
        run([str(args.jdk_bin/'javac.exe'),'-encoding','UTF-8','--release','8','-proc:none','-cp',os.pathsep.join(map(str,(args.android_jar,args.client_jar,args.rooms_jar))),'-d',str(production),str(SOURCE)])
    counts=dict(item.split('=') for item in output.split()[1:])
    receipt={'status':'PASS','scope':'Real StationExitPanel source compiled/executed against recording host UI stubs; real source also compiled against Android API34 and unchanged room/client dependencies. No Android pixel rendering, gameplay, native shutdown, networking or saves validation.','cases':int(counts['cases']),'checks':int(counts['checks']),'sourceGuards':guards,'javaApi34Compile':True,'sha256':{'exitPanel':digest(SOURCE),'recipe':digest(Path(__file__)),'androidApi34':digest(args.android_jar),'clientJar':digest(args.client_jar),'roomsJar':digest(args.rooms_jar)},'limits':['Stub tree checks do not reproduce Android measurement or window focus delivery.','Physical layout, font-scale behavior and successful engine exit remain to be observed.','Menus owned by other emulator processes are preserved.']}
    (ROOT/'evidence/exit-panel-refinement.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(output);print('PASS sourceGuards='+str(len(guards))+' javaApi34Compile=true')

if __name__=='__main__':main()
