"""Compile-time checks of the real layout body, including narrow screens."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
src=WORK/'carousel-inputs/d0/station_bottom_action_layout.h'
out=WORK/'tests/primary-geometry';out.mkdir(exist_ok=True)
s=src.read_text('utf8').replace('static StationPrimaryMetaLayout stationPrimaryMetaLayout(', 'static constexpr StationPrimaryMetaLayout stationPrimaryMetaLayout(')
(out/'layout.h').write_text(s,'utf8')
lines=['#include "layout.h"'];checks=0
for w,h in [(2400,1080),(2340,1080),(1920,1080),(1280,720),(2560,1600)]:
 for icons in range(6):
  for label in [.95,1.4,2.8]:
   n=f'g{checks}';r=f'stationBottomGameAction({w}.f,{h}.f,0)'
   lines.append(f'constexpr auto {n}=stationPrimaryMetaLayout({r},{r}.h*1.1f,{r}.h*{label}f,0.f,{r}.h*{.22 if icons==0 else 0.0}f,{r}.h*.18f,{icons});')
   for expr in [f'{n}.label.x>={r}.x',f'{n}.label.x+{n}.label.w<={n}.stars.x+.01f',f'{n}.stars.x+{n}.stars.w<={n}.person.x+.01f',f'{n}.players.x+{n}.players.w<={r}.x+{r}.w+.01f',f'{n}.scale>0.f&&{n}.scale<=1.f',f'{n}.stars.y>={r}.y',f'{n}.stars.y+{n}.stars.h<={r}.y+{r}.h+.01f']:
    lines.append(f'static_assert({expr},"primary action bounds and ordering");');checks+=1
(out/'check.cpp').write_text('\n'.join(lines)+'\n')
clang=r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe'
r=subprocess.run([clang,'--target=aarch64-linux-android26','-std=c++17','-fsyntax-only',str(out/'check.cpp')],capture_output=True)
assert r.returncode==0,r.stderr.decode('utf8','replace')
receipt={'passed':True,'compileTimeAssertions':checks,'viewports':5,'playerIconCounts':[0,1,2,3,4,5],'scope':'layout only, not Android rendering','sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest()}
(ROOT/'evidence/primary-action-geometry.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
