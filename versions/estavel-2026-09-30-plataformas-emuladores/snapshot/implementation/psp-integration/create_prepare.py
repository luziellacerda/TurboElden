from pathlib import Path
import json,zipfile,struct,hashlib,shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'psp-integration';base=P/'TurboramaStation-PS2-ARMSX2-2.7.2.apk';classes=set()
with zipfile.ZipFile(base) as z:
 for name in z.namelist():
  if not(name.startswith('classes') and name.endswith('.dex')):continue
  data=z.read(name);u=lambda off:struct.unpack_from('<I',data,off)[0]
  for i in range(u(96)):
   idx=u(u(100)+32*i);sid=u(u(68)+4*idx);off=u(u(60)+4*sid)
   while data[off]&128:off+=1
   off+=1;end=data.index(0,off);classes.add(data[off:end].decode()[1:-1])
(R/'base-classes.json').write_text(json.dumps(sorted(classes)))
s=(P/'ps2-integration/prepare.py').read_text();s=s.replace('ps2-integration','psp-integration').replace('tps2core','tpspcore').replace("return 'tp_'","return 'ts_'").replace("'tp_'","'ts_'").replace('tp_Theme.ARMSX2','ts_ppsspp_style').replace("start=15","start=17")
s=s.replace("('com/armsx2/','kr/co/iefriends/pcsx2/','com/discord/')","('org/ppsspp/ppsspp/',)").replace('com.armsx2','org.ppsspp.ppsspp')
s=s.replace('pile_redirect_hook','sile_redirect_hook').replace('psl_alloc_hook','ssl_alloc_hook').replace('phok_impl','shok_impl').replace('ps2x_hook','pspx_hook').replace('p2c_shared','psc_shared').replace(':ps2',':psp').replace('frontend.ps2','frontend.psp')
a=s.index('for e in donor_app:');b=s.index('permissions=',a)
s=s[:a]+'''for e in donor_app:
 if e.tag not in ['activity','provider','uses-library']:continue
 name=e.get(A+'name','')
 if 'ShortcutActivity' in name or 'profileinstaller' in name:continue
 child=copy.deepcopy(e);xml_node(child)
 if e.tag!='uses-library':child.set(A+'process',':psp');child.set(A+'exported','false')
 if e.tag=='activity':
  child.set(A+'enableOnBackInvokedCallback','false');child.set(A+'taskAffinity','org.emulationstation.frontend')
  if name.endswith('PpssppActivity'):child.set(A+'launchMode','standard')
  for x in list(child):
   if x.tag=='intent-filter':child.remove(x)
 if e.tag=='provider':child.set(A+'authorities',child.get(A+'authorities','').replace('org.ppsspp.ppsspp.','org.emulationstation.frontend.psp.'))
 app.append(child)
'''+s[b:]
a=s.index("shutil.copy2(R/'upstream/COPYING.GPLv3'");s=s[:a]+'''shutil.copy2(R/'upstream/LICENSE.TXT',notice/'LICENSE.TXT')
import hashlib
record={'official_version':'1.20.4','source':'https://github.com/hrydgard/ppsspp/tree/v1.20.4','official_apk':'https://www.ppsspp.org/files/1_20_4/ppsspp.apk','official_apk_sha256':hashlib.sha256((R/'ppsspp-official-1.20.4.apk').read_bytes()).hexdigest(),'source_rebuilt':False,'integration':'Official engine and menus embedded in process :psp; own storage, native launch arguments.'}
(notice/'provenance.json').write_text(json.dumps(record,indent=2))
(R/'class-map.json').write_text(json.dumps(class_map));(R/'resource-map.json').write_text(json.dumps(resource_map))
print('Prepared',len(class_map),'classes and',len(idmap),'resources')
'''
(R/'prepare.py').write_text(s,encoding='utf-8')
B=R/'before';B.mkdir(exist_ok=True)
for name in ['native_carousel.cpp','libturbo_carousel.so']:
 if not(B/name).exists():shutil.copy2(P/name,B/name)
s=(P/'native_ps2.h').read_text().replace('ps2','psp').replace('Ps2','Psp').replace('PS2','PSP').replace('flycast','ps2').replace('ARMSX2 2.7.2','PPSSPP 1.20.4')
a=s.index('static bool pspCore');b=s.index('static jclass',a);s=s[:a]+'static bool pspCore(const void*id){return uiContains(strData(id),"ppsspp")||uiContains(strData(id),"PPSSPP");}\n'+s[b:]
(P/'native_psp.h').write_text(s,encoding='utf-8')
p=P/'native_carousel.cpp';s=p.read_text()
if '#include "native_psp.h"' not in s:
 s=s.replace('#include "native_ps2.h"','#include "native_ps2.h"\n#include "native_psp.h"')
 for n in ['Run','Fresh','Bundled','Installed','Assets','Pack','Definitions','Settings']:s=s.replace('(void*)ps2'+n+'Hook','(void*)psp'+n+'Hook')
 p.write_text(s,encoding='utf-8')
print('PSP scripts and native routing prepared')
