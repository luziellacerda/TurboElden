from pathlib import Path
import hashlib,json,re,subprocess,zipfile
ROOT=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=ROOT/'native'
checks=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)});assert value,name
def body(text,signature):
 start=text.index(signature);opening=text.index('{',start);depth=1;i=opening+1
 while depth:
  if text[i]=='{':depth+=1
  if text[i]=='}':depth-=1
  i+=1
 return text[opening+1:i-1]
source=(N/'native_system_video720.h').read_text()
old=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003\native\native_system_video720.h').read_text()
check('fixed 80ms start delay removed','video720NextStart' not in source and 'now+80' in old)
pause=body(source,'static void pauseSystemVideo720()')
stop=body(source,'static void stopSystemVideo720()')
check('list pause retains frames','retireVideo720Slot(i,true)' in pause and 'clearVideo720Frames' not in pause)
check('emulation stop frees previews','clearVideo720Frames()' in stop and 'retireVideo720Slot(i,false)' in stop)
check('preview shader independent of removed scene','shipCompositeProgram' not in source)
check('retained shader initialized explicitly','ensureVideo720PreviewProgram()' in body(source,'static void drawSystemVideo720('))
check('GPU texture budget enforced','if(count>=video720TextureBudget)' in source and 'video720DeleteTexture(oldest->texture)' in source)
check('visible previews protected from eviction','!video720PaintedAsset(gui,candidate.asset)' in source)
check('context change clears stale textures','stopSystemVideo720();video720Context=context;video720PreviewProgram=0' in source)
check('no loop acceleration', 'video720Start' in source)
java=(ROOT/'video/java/org/emulationstation/frontend/SystemCardVideo720.java').read_text()
check('speed remains 1x, native loop','setLooping(true)' in java and 'setSpeed(1.0f)' in java)
check('only focus plays after first frame','!s.visible&&s.prepared&&!s.parked' in java and 's.player.pause()' in java)
check('background activity releases all players','foreground=false;stopAll();' in java)
check('real decode deadlines retained','Video first-frame timeout' in java and 'now-v.startedAt)>20000' in source)
main=(N/'native_carousel.cpp').read_text();settings=(N/'native_settings.h').read_text()
check('both attached settings labels excluded from child renderer','p==settingsBackText||p==settingsNetplayText' in main)
check('settings renderer does not draw while closed','if(!at<B>(p,0x2050))return;' in body(settings,'static void drawSettingsSkinHook('))
check('list entry pauses, does not flush','pauseSystemVideo720();lastSystem=' in main)
check('idle frame pacing unchanged',(N/'native_menu_power.h').read_bytes()==Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003\native\native_menu_power.h').read_bytes())
palette=(N/'laser_assets.h').read_text()
for name in ['Super Nintendo','Super Nintendo - BR']:
 check(name+' purple LED',f'{{"{name}",0xA855F7FF,0xF3E8FFFF' in palette)
e=json.loads((ROOT/'evidence/video-preview-inputs.json').read_text())
check('44 unique video frames',len(e['previews'])==44 and len({p['asset'] for p in e['previews']})==44)
for p in e['previews']:
 data=(ROOT/'video/previews'/(Path(p['asset']).stem+'.rgb565')).read_bytes()
 check(p['asset']+' exact frame integrity',len(data)==1036800 and hashlib.sha256(data).hexdigest()==p['previewSha256'])
 check(p['asset']+' frame contains image',len(set(memoryview(data).cast('H')))>16)
cpp=ROOT/'tests/video-policy-test.cpp'
cpp.write_text('''#include <cassert>
#include <cstdio>
#include "video720_policy.h"
int main(){
 static_assert(video720MaxRetainedBytes==8294400,"retained cache memory budget");
 assert(video720Older(1,2));assert(!video720Older(2,1));assert(!video720Older(2,2));
 assert(video720Older(0xfffffff0u,0x10u));assert(!video720Older(0x10u,0xfffffff0u));
 puts("5 unsigned age ordering checks, GPU budget assertion passed");
}
''')
exe=ROOT/'tests/video-policy-test.exe'
compiler=r'C:\Program Files\LLVM\bin\clang++.exe'
r=subprocess.run([compiler,'-std=c++17','-I'+str(N),str(cpp),'-o',str(exe)],capture_output=True,text=True);assert r.returncode==0,r.stderr
r=subprocess.run([str(exe)],capture_output=True,text=True);assert r.returncode==0,r.stderr
check('compiled cache policy wrap-around tests',r.returncode==0)
(ROOT/'evidence/r5-regressions.json').write_text(json.dumps({'checks':checks,'passed':True,'scope':'source regressions, frame payloads and host cache arithmetic; not Android timing','policyTest':r.stdout},indent=2)+'\n')
print(len(checks),'checks passed; Android playback and timings still require phone')
