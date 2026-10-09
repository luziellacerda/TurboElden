"""Compile-time execution of actual native policies; explicit Java/native integration guards."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-single-pass-r88-20261009')
out=WORK/'tests';out.mkdir(exist_ok=True)
code='''#include "station_video_once_policy.h"
#include "station_rating_animation.h"
#include "station_menu_frame_policy.h"
constexpr bool visits(){
 StationVideoOncePolicy p;int owner=0,other=1;
 if(!p.observe(&owner,0,10,false,"a")||p.completed)return false;
 p.finish();if(!p.completed)return false;
 for(int i=0;i<1000;i++)if(p.observe(&owner,0,10,false,"a")||!p.completed)return false;
 if(!p.observe(&owner,1,11,false,"a")||p.completed)return false;
 p.finish();if(!p.observe(&owner,0,10,false,"a")||p.completed)return false;
 p.finish();if(!p.observe(&owner,0,12,false,"a")||p.completed)return false;
 p.finish();if(!p.observe(&owner,0,12,true,"a")||p.completed)return false;
 p.finish();if(!p.observe(&other,0,12,true,"a")||p.completed)return false;
 p.finish();if(!p.observe(&other,0,12,true,"b")||p.completed)return false;
 p.finish();p.reset();if(!p.observe(&other,0,12,true,"b")||p.completed)return false;
 if(!p.observe(&other,0,12,true,nullptr))return false;
 p.finish();if(p.observe(&other,0,12,true,nullptr)||!p.completed)return false;
 return true;
}
static_assert(visits(),"selection lifecycle");
'''
checks=1
for bits in range(8):
    code+=f'static_assert(stationMenuFramePolicy::target({bits&1},{(bits>>1)&1},{(bits>>2)&1})==30,"menu30");\n';checks+=1
for ms in list(range(0,5001,5))+[0xffffffff]:
    expected=min(79,ms*60//1000)
    code+=f'static_assert(stationRatingLoopFrame({ms}u)=={expected}u,"single rating pass");\n';checks+=1
src=out/'policies.cpp';src.write_text(code,'utf8')
compiler=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe')
r=subprocess.run([str(compiler),'-std=c++17','-fsyntax-only','-I'+str(ROOT/'native/d0'),str(src)],capture_output=True)
(out/'policies.log').write_bytes(r.stdout+r.stderr);assert r.returncode==0,r.stderr.decode('utf8','replace')
java=ROOT/'java/netplay-src/org/emulationstation/frontend/netplay'
video=(java/'StationSinglePassVideo720.java').read_text();rating=(java/'StationGameRatingView.java').read_text();cover=(java/'StationOnlineCoverView.java').read_text()
native=(ROOT/'native/d0/native_system_video720.h').read_text()
guards=[
 'setLooping(true)' not in video,'setLooping(false)' in video,'seekTo(' not in video,
 's.completed=true' in video,'s.hasFrame?2:3' in video,'s.valid=false;releaseSurfaces(s)' in video,
 'players>=decoderCapacity' in video,'decoderCapacity=1' in video,'onActivityPaused' in video,
 'video720Once.completed?nullptr:focusedAsset' in native,'result[i]==2' in native,
 'result[i]==3' in native,'video720Once.reset()' in native,
 native.index('if(first||!f||!f->ready||result[i]==2)retainVideo720Frame(v)')<native.index('if(result[i]==2){video720Once.finish()'),
 'StationSinglePassVideo720' in native,'v.stopPending||selectionChanged?nullptr:v.asset' in native,
 'Math.min(79,elapsed*60/1000)' in rating,'if(elapsed<DURATION_MS)postDelayed' in rating,
 'visible()&&elapsed<DURATION_MS' in rating,'if(next!=rating){elapsed=0' in rating,
 'TextureView' in cover,'HandlerThread' in cover,'FIT_CENTER' in cover,
 hashlib.sha256((ROOT/'native/d0/native_magazine.h').read_bytes()).hexdigest()==hashlib.sha256(Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r87\carousel-inputs\d0\native_magazine.h').read_bytes()).hexdigest(),
]
assert all(guards),[i for i,v in enumerate(guards) if not v]
manifest=json.loads((WORK/'JAVA-SOURCE-MANIFEST.json').read_text())
result=dict(passed=True,checks=checks,sourceGuards=len(guards),sourceHashes=manifest['sources'],
 scope='Actual native compile-time policy assertions plus source integration guards. Android Java compiled separately; no gameplay or physical consumption proof.',
 scenarios=['complete without restart','1000 idle observations','same clip on different cell','return selection','changed mapping','folder entry','owner change','asset change','lifecycle reset','null asset','30 fps all menu states','star final frame clamp and unsigned edge'])
(ROOT/'evidence/tests.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({k:v for k,v in result.items() if k!='sourceHashes'}))
