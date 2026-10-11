"""Compile real geometry; guard original exit callbacks and verified pause ABI.

This is a host-only check. It does not prove Android layout, GPU, temperature or gameplay.
"""
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'java/netplay-src/org/emulationstation/frontend/netplay'
checks=[]
def check(label,value):
    checks.append(label)
    if not value:raise AssertionError(label)
def read(path):return path.read_text(encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

cover=read(JAVA/'StationCreateGameCard.java')
flow=read(JAVA/'StationFlowPanel.java')
exit_panel=read(JAVA/'StationExitPanel.java')
pause=read(ROOT/'native/d1/native_pause_menu.h')
check('cards do not size from display height','heightPixels' not in cover)
check('flow does not size from display height','heightPixels' not in flow)
check('own-room hero remains viewport gated','if(viewportBounded&&' in cover and 'StationCoverLayout.hero(' in cover)
check('room lists use compact thumbnail','StationCoverLayout.thumbnail(width,cover.aspect(),dp(76),dp(112),gap)' in cover)
check('existing card interface retained',all(x in cover for x in ['void setViewportBounded(boolean value)','void setPlatform(String platform)','void setCover(Bitmap bitmap)']))
check('artwork still uses original bitmap','cover.setImageBitmap(bitmap)' in cover and 'image.setImageBitmap(bitmap)' in flow)
check('flow still owns scroll content','scroll.addView(content,new ScrollView.LayoutParams(-1,-2))' in flow)
check('no new decode renderer network or timer',not re.search(r'BitmapFactory|MediaPlayer|egl|glCompileShader|postDelayed|StationApi',cover+flow+exit_panel))
check('exit callback occurs only once',exit_panel.count('exit.run();')==1)
check('human exit still follows dialog dismissal','dialog.dismiss();exit.run();' in exit_panel)
check('cancel resume dismisses only','0,stacked,()->dialog.dismiss()' in exit_panel)
check('create signature preserved','static AlertDialog create(Activity activity,Runnable exit)' in exit_panel)
check('confirmation accepts original callback','static AlertDialog confirm(Activity activity,Runnable exit)' in exit_panel)
check('shared focusable semantic buttons','new StationActionButton(a,title,tone,icon)' in exit_panel)
check('touch targets remain 48dp','Math.round(48*density)' in exit_panel)
check('large-font menu has stacked fallback','fontScale>1.25f' in exit_panel)
check('pause native vector bounds retained','(U)(end-begin)>56*16' in pause and 'r+=56' in pause)
check('pause font and original y retained','fn<void*(*)(void*,const void*,float,float,unsigned)>(0x2e9304)(font,text,x,y,color)' in pause)
check('pause row x-height ABI named correctly','rowX=at<float>(r,0x24),rowHeight=at<float>(r,0x30)' in pause)
check('pause text remains after icon','x=rowX+rowHeight*.88f' in pause)
check('pause enabled action IDs retained','at<B>(row,0x20)' in pause and 'at<int>(row,0)' in pause)
check('pause draw hooks do not request exit or save',not re.search(r'requestHumanExit|confirmExit|saveState|loadState|finish\(',pause))

jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
with tempfile.TemporaryDirectory(prefix='station-r121-geometry-') as out:
    compile_run=subprocess.run([str(jdk/'javac.exe'),'-d',out,str(JAVA/'StationCoverLayout.java'),str(ROOT/'tests/StationCoverLayoutR121Test.java')],capture_output=True,text=True,check=True)
    execution=subprocess.run([str(jdk/'java.exe'),'-cp',out,'org.emulationstation.frontend.netplay.StationCoverLayoutR121Test'],capture_output=True,text=True)
    if execution.returncode:raise AssertionError(execution.stderr.strip())
    result=execution.stdout.strip()
match=re.fullmatch(r'PASS checks=(\d+) cases=(\d+)',result)
check('compiled real geometry passes',match is not None)
files=[JAVA/'StationCoverLayout.java',JAVA/'StationCreateGameCard.java',JAVA/'StationFlowPanel.java',JAVA/'StationExitPanel.java',ROOT/'native/d1/native_pause_menu.h',ROOT/'tests/StationCoverLayoutR121Test.java',Path(__file__)]
receipt={'revision':'R121','scope':'host-only presentation arithmetic and source guards','status':'PASS','geometryChecks':int(match[1]),'geometryCases':int(match[2]),'sourceGuardChecks':len(checks),'guards':checks,'sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files},'pauseAbiEvidence':{'drawRectCaller':'0x2afe3c','rowXY':'ldp s0,s1,[row,#0x24]','rowWidthHeight':'ldp s2,s3,[row,#0x2c]','buildTextCacheCaller':'0x2bc1c8','meaning':'0x30 is row height, not width; old 0.88 alignment already followed the icon'},'limitations':['No Android layout/rendering executed','No gamepad, gameplay or network session exercised','No GPU/CPU or temperature measurement','OEM exit menus remain with their original owners']}
path=ROOT/'evidence/room-presentation-r121.json'
path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:receipt[k] for k in ['status','geometryChecks','geometryCases','sourceGuardChecks']},ensure_ascii=False))
