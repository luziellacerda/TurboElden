from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1];W=Path(r'E:\ESTUDO APK\work\station-platform-led-r87-20261008');B=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r86')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(ok,name):assert ok,name;checks.append(name)
s=(W/'carousel-inputs/d0/premium-magazine-led-android.glsl').read_text('utf8');j=(W/'java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java').read_text('utf8');parts=re.findall(r'^\s*("(?:[^"\\]|\\.)*")\s*[+;]',j,re.M)
check(''.join(json.loads(x) for x in parts)==s,'Java/nativo GLSL identico')
check((W/'carousel-inputs/d0/magazine_shader.h').read_text('utf8')=='static const char magazineShaderSource[]=R"NEOMAG('+s+')NEOMAG";\n','Cabecalho GLSL identico')
a=(B/'carousel-inputs/d0/native_info.h').read_text('utf8');b=(W/'carousel-inputs/d0/native_info.h').read_text('utf8');check(b.replace('\n starSize*=.70f; // Requested 30% reduction after responsive fit.','')==a,'Somente escala das estrelas na sinopse')
for n in ['native_space.h','native_carousel.cpp','native_formation.h']:
 check(sha(W/'carousel-inputs/d0'/n)==sha(B/'carousel-inputs/d0'/n),'Preservado '+n)
p='java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineCoverView.java';a=(B/p).read_text('utf8');b=(W/p).read_text('utf8');extra='''        if(k.equals("gamecube")||k.equals("nintendogamecube")||k.equals("gc"))return 5;
        if(k.equals("wiiu")||k.equals("nintendowiiu"))return 6;
        if(k.equals("switch")||k.equals("nintendoswitch"))return 7;
        if(k.equals("playstation")||k.equals("playstation1")||k.equals("ps1")||k.equals("psx"))return 8;
''';check(b.replace(extra,'')==a,'Ciclo de vida e temporizadores online preservados')
check('postDelayed(frame,34)' in b,'Cadencia online preservada')
for k in ['gamecube','wiiu','switch','psx','wii','saturn','xbox360','fbneo']:
 check(('"'+k+'"') in (W/'carousel-inputs/d0/station_console_keys.h').read_text(),'Alias hardware '+k)
check(json.loads((R/'evidence/java-build.json').read_text())['clientDexSHA256']=='4696ad8c0be296e3a191b906b135d8393450e12a6de926cf26216e6fcb6e8c9c','Cliente online e autenticacao byte identicos')
(R/'evidence/scope.json').write_text(json.dumps(dict(passed=True,checks=checks,checksCount=len(checks)),indent=2)+'\n','utf8');print('scope checks',len(checks))
