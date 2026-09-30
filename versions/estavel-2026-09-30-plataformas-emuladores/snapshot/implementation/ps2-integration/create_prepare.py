from pathlib import Path
import zipfile,struct,json,re
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'ps2-integration'
base=Path(r'E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk')
classes=set()
with zipfile.ZipFile(base) as z:
 for n in z.namelist():
  if not re.fullmatch(r'classes\d*\.dex',n):continue
  d=z.read(n);u=lambda p:struct.unpack_from('<I',d,p)[0];strings=[]
  for i in range(u(56)):
   p=u(u(60)+4*i)
   while d[p]&128:p+=1
   p+=1;end=d.index(b'\0',p);strings.append(d[p:end].decode('utf-8','replace'))
  types=[strings[u(u(68)+4*i)] for i in range(u(64))]
  for i in range(u(96)):
   name=types[u(u(100)+32*i)];classes.add(name[1:-1])
(R/'base-classes.json').write_text(json.dumps(sorted(classes)))
s=(P/'dolphin-integration/prepare.py').read_text()
s=s[:s.index('# Donor components stay')]
s=s.replace('dolphin-integration','ps2-integration').replace("D=R/'dolphin-decoded'","D=R/'current-decoded'").replace("return 'td_'","return 'tp_'")
a=s.index('# Remove only obsolete');b=s.index('def platform_class')
s=s[:a]+"shutil.copytree(F,M,dirs_exist_ok=True)\nfront_classes=set(json.loads((R/'base-classes.json').read_text()))\n"+s[b:]
s=s.replace("if old.startswith('org/dolphinemu/dolphinemu/') or platform_class(old):new=old", "if old.startswith(('com/armsx2/','kr/co/iefriends/pcsx2/','com/discord/')) or platform_class(old):new=old\n        elif old.startswith('org/libsdl/'):new=old.replace('org/libsdl/','org/p2sdl/',1)")
s=s.replace('tdolphin/','tps2core/').replace('tdolphin.','tps2core.').replace('org.dolphinemu.dolphinemu','com.armsx2').replace("'td_'","'tp_'").replace("start=10","start=15")
s=s.replace("if val=='com.armsx2':val='org.emulationstation.frontend'", "if val=='com.armsx2':val='org.emulationstation.frontend'")
s=s.replace("'_dolphin_preferences'","'_ps2_preferences'")
s=s.replace("'file_redirect_hook':'dile_redirect_hook'","'file_redirect_hook':'pile_redirect_hook'").replace("'gsl_alloc_hook':'dsl_alloc_hook'","'gsl_alloc_hook':'psl_alloc_hook'").replace("'hook_impl':'dhok_impl'","'hook_impl':'phok_impl'").replace("'main_hook':'dolp_hook'","'main_hook':'ps2x_hook',\n 'c++_shared':'p2c_shared'")
# Root-obfuscated classes with native entry points must retain their JNI names.
s=s.replace('dot_map={',"native_classes=set()\nfor f in D.rglob('*.smali'):\n text=f.read_text('utf-8')\n if re.search(r'^\\.method .*\\bnative\\b',text,re.M):\n  name=re.search(r'^\\.class .* (L[^;]+;)',text,re.M)[1][1:-1]\n  if not name.startswith('org/libsdl/'):\n   assert name not in front_classes, 'Native class collision: '+name\n   class_map[name]=name;native_classes.add(name)\n(R/'native-classes.json').write_text(json.dumps(sorted(native_classes)))\ndot_map={",1)
# Fix hard-coded provider authorities, without renaming JNI packages.
s=s.replace("if val=='.filesprovider':val='.dolphin.filesprovider'", "if val.startswith('com.armsx2.') and val.endswith(('provider','romlibrary','androidx-startup')):val=val.replace('com.armsx2.','org.emulationstation.frontend.ps2.',1)")
s=s.replace("if val=='.user':val='.dolphin.user'", "if val=='ARMSX2':val='TURBORAMA_PS2'")
s+='''
manifest=ET.parse(M/'AndroidManifest.xml');app=manifest.getroot().find('application')
app.set(A+'allowNativeHeapPointerTagging','false')
donor=ET.parse(D/'AndroidManifest.xml').getroot();donor_app=donor.find('application')
for e in donor_app:
 if e.tag not in ['activity','provider','service','receiver','uses-library']:continue
 name=e.get(A+'name','')
 if e.tag=='receiver' or 'profileinstaller' in name or 'PreviewActivity' in name:continue
 child=copy.deepcopy(e);xml_node(child)
 if e.tag!='uses-library':child.set(A+'process',':ps2');child.set(A+'exported','false')
 if e.tag=='activity':
  child.set(A+'theme',child.get(A+'theme','@style/tp_Theme.ARMSX2'))
  child.set(A+'enableOnBackInvokedCallback','false')
  child.set(A+'taskAffinity','org.emulationstation.frontend')
  for x in list(child):
   if x.tag=='intent-filter':child.remove(x)
 if e.tag=='provider':child.set(A+'authorities',child.get(A+'authorities','').replace('com.armsx2.','org.emulationstation.frontend.ps2.'))
 app.append(child)
permissions={e.get(A+'name') for e in manifest.getroot().findall('uses-permission')}
for e in donor.findall('uses-permission'):
 name=e.get(A+'name','')
 if name in permissions or name in ['android.permission.REQUEST_INSTALL_PACKAGES'] or name.startswith('com.armsx2.'):continue
 manifest.getroot().append(copy.deepcopy(e))
manifest.write(M/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
libdir=M/'lib/arm64-v8a';libdir.mkdir(parents=True,exist_ok=True)
replacements={b'androidx/':b'tps2core/',b'org/libsdl/':b'org/p2sdl/'}
for old,new in library_names.items():replacements[('lib'+old+'.so').encode()]=('lib'+new+'.so').encode()
for f in (D/'lib/arm64-v8a').glob('*.so'):
 b=f.read_bytes()
 for old,new in replacements.items():
  assert len(old)==len(new),(old,new)
  b=b.replace(old,new)
 name='lib'+library_names.get(f.name[3:-3],f.name[3:-3])+'.so'
 (libdir/name).write_bytes(b)
shutil.copytree(D/'assets',M/'assets',dirs_exist_ok=True)
notice=M/'assets/ps2-integration';notice.mkdir(exist_ok=True)
shutil.copy2(R/'upstream/COPYING.GPLv3',notice/'COPYING.GPLv3')
release=json.loads((R/'official-release.json').read_text('utf-8-sig'))
asset=next(a for a in release['assets'] if 'legacy-armv8.0' in a['name'])
import hashlib
record={'official_version':'2.7.2','source':'https://github.com/ARMSX2/ARMSX2/tree/2.7.2','official_apk':asset['browser_download_url'],'official_apk_sha256':hashlib.sha256((R/'armsx2-official-2.7.2.apk').read_bytes()).hexdigest(),'source_rebuilt':False,'integration':'Official Android engine and menus inside TurboramaStation, process :ps2; no external app required.'}
(notice/'provenance.json').write_text(json.dumps(record,indent=2))
(R/'class-map.json').write_text(json.dumps(class_map))
(R/'resource-map.json').write_text(json.dumps(resource_map))
print('Prepared',len(class_map),'classes;',len(idmap),'resources;',len(native_classes),'native classes preserved')
'''
(R/'prepare.py').write_text(s,encoding='utf-8')
print('PS2 preparation script created; base class count',len(classes))
