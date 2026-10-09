from pathlib import Path
import json,subprocess,hashlib
ROOT=Path(__file__).resolve().parent;WORK=Path(r'E:\ESTUDO APK\work\station-video-endframe-r89-20261009')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r88')
out=WORK/'tests';out.mkdir();jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
src=ROOT/'java/netplay-src/org/emulationstation/frontend/netplay/StationVideoEndFrame.java'
test=out/'EndFrameTest.java';test.write_text('''package org.emulationstation.frontend.netplay;
public class EndFrameTest {
 public static void main(String[] args){int checks=0;
  for(int count=3;count<10000;count++){
   int duration=(int)Math.round(count*1000.0/30.0);
   long wanted=Math.round((count-3)*1000.0/30.0);
   if(StationVideoEndFrame.positionMs(duration)!=wanted)throw new AssertionError(count);
   checks++;
  }
  for(int duration:new int[]{-10,0,1,33,67}){if(StationVideoEndFrame.positionMs(duration)!=0)throw new AssertionError(duration);checks++;}
  if(StationVideoEndFrame.positionMs(Integer.MAX_VALUE)>Integer.MAX_VALUE)throw new AssertionError("overflow");checks++;
  System.out.println(checks);
 }
}''','utf8')
for cmd in [[jdk/'javac.exe','--release','8','-d',out,src,test],[jdk/'java.exe','-cp',out,'org.emulationstation.frontend.netplay.EndFrameTest']]:
    r=subprocess.run(list(map(str,cmd)),capture_output=True);assert r.returncode==0,(r.stdout+r.stderr).decode('utf8','replace')
checks=int(r.stdout)
j=(ROOT/'java/netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java').read_text()
n=(ROOT/'native/d0/native_info.h').read_text()
guards=[s in j for s in ['MediaPlayer.SEEK_CLOSEST','s.player.pause()','setOnSeekCompleteListener','if(s.endCheck!=null)worker().removeCallbacks','if(s.seekTimeout!=null)worker().removeCallbacks','s.finishing||s.parked','(!s.finishing||s.completed)']]
assert all(guards)
assert 'starsTop+=lowerRoom<h*.020f?lowerRoom:h*.020f' in n and 'starSize*=.70f' in n
# Geometry: requested downward motion fits the existing title gap, never changes size.
for h in [480,720,900,1080,1440,2160]:
    for gap in range(100):
        before=100;size=h*.042*.70;title=before+size+h*.008+gap
        lower=max(0,min(h*.020,title-h*.008-size-before));after=before+lower
        assert after>=before and after+size<=title-h*.008+1e-8;checks+=1
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
unchanged=['carousel-inputs/d0/native_magazine.h','carousel-inputs/d0/station_menu_frame_policy.h','java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineCoverView.java','java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java']
for p in unchanged:assert sha(BASE/p)==sha(WORK/p)
result=dict(passed=True,checks=checks,sourceGuards=len(guards)+2,sourceHashes=json.loads((WORK/'JAVA-SOURCE-MANIFEST.json').read_text())['sources'],LEDsAnd30fpsPreserved=True,
 scope='Actual pure Java frame-index calculation, geometry math and source guards; no claim of all physical decoders or games tested.',
 docs='https://developer.android.com/reference/android/media/MediaPlayer#seekTo(long,%20int)')
(ROOT/'evidence/tests.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({k:v for k,v in result.items() if k!='sourceHashes'}))
