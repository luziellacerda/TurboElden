from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1];W=Path(r'E:\ESTUDO APK\work\station-online-cover-led-r86-20261008');P=W/'java/netplay-src/org/emulationstation/frontend/netplay';N=W/'carousel-inputs/d0'
checks=0
def check(value):
 global checks
 assert value;checks+=1
shader=(N/'premium-magazine-led-android.glsl').read_text()
java=(P/'StationCoverLightingShader.java').read_text()
body=java.split('static final String SOURCE =',1)[1]
actual=''.join(json.loads(line.strip().removesuffix('+').removesuffix(';').strip()) for line in body.splitlines() if line.strip().startswith('"'))
check(actual==shader)
check((N/'magazine_shader.h').read_text()=='static const char magazineShaderSource[]=R"NEOMAG('+shader+')NEOMAG";\n')
view=(P/'StationOnlineCoverView.java').read_text()
for text in ['GLES20.glShaderSource','StationCoverLightingShader.SOURCE','resumed&&isAttachedToWindow()&&isShown()','getGlobalVisibleRect','hasWindowFocus()','removeCallbacks(frame)','queued.compareAndSet(false,true)','eglDestroyContext','source.release()','postDelayed(frame,34)','uploaded!=image'] :check(text in view)
for text in ['RuntimeShader','MASKS','mask_tex','scheduleAtFixedRate']:check(text not in view)
info=(N/'native_info.h').read_text()
check('download?gameActionTextScale*1.30f' in info)
check('infoPlayStars={contentLeft(gui),starsTop' in info)
check('for(int i=0;i<infoPlayerIcons;i++)drawDetailsPerson' not in info)
check('bold.values[12]' in (N/'native_carousel.cpp').read_text())
keys=(N/'station_console_keys.h').read_text()
for system in ['dreamcast','cps1','cps2','cps3']:check('"'+system+'"' in keys)
base=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r85')
for name in ['station_info_layout.h','station_synopsis_scroll.h','native_space.h','native_installed.h','native_game_actions.h']:
 if (base/'carousel-inputs/d0'/name).exists():check((N/name).read_bytes()==(base/'carousel-inputs/d0'/name).read_bytes())
for h in [480,720,1080,1440]:
 for ratio in [16/9,19.5/9,20/9,21/9]:
  width=h*.790*.828;check(0<width<h)
  bottom=h*.105+(h*ratio*.965-(h*ratio*.025+width+h*ratio*.022)-5*h*ratio*.012)/6/.72
  top=bottom+h*.008;size=max(0,min(h*.042,h*.454-top-h*.008))
  check(size>=0 and top+size<=h*.454-h*.0079);check(top>bottom)
record=dict(passed=True,checks=checks,scope='Shared-shader identity, source/lifecycle guards and geometry arithmetic; not gameplay',shaderSHA256=hashlib.sha256(shader.encode()).hexdigest())
(R/'evidence/scope.json').write_text(json.dumps(record,indent=2)+'\n','utf8');print(json.dumps(record))
