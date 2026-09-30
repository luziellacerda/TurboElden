from pathlib import Path
import json,zipfile,hashlib,urllib.request,shutil,os,subprocess
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-xbox-pce-refresh'
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk'
with BASE.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='ca5556ac81e96e49d67ac0134533604908dd5122351c898ac2125d03a223cee7'
with zipfile.ZipFile(BASE) as z:
 (R/'before/entry-hashes.json').write_text(json.dumps({n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.startswith('META-INF/')}),encoding='utf-8')
 with zipfile.ZipFile(R/'modules.apk','w') as out:
  for n in ['AndroidManifest.xml','resources.arsc','classes.dex','classes8.dex']:out.writestr(n,z.read(n))
 print('Colliding donor libs',set(z.namelist()).intersection(zipfile.ZipFile(R/'X1BOX-1.2.8.apk').namelist()) & set(n for n in z.namelist() if n.startswith('lib/')))
 (R/'before/libmain.so').write_bytes(z.read('lib/arm64-v8a/libmain.so'))
for n in ['LICENSE','COPYING','COPYING.LIB']:
 (R/'upstream'/n).write_bytes(urllib.request.urlopen('https://raw.githubusercontent.com/izzy2lost/xemu/1.2.8/'+n).read())
# Adapt the already-used Android resource/namespace merger, never the old packager.
s=(P/'xbox360-integration/prepare.py').read_text(encoding='utf-8')
s=s.replace("R=Path(r'\\\\?\\E:\\ESTUDO APK\\work\\native-carousel\\implementation\\xbox360-integration')","R=Path(__file__).parent")
s=s.replace("D=R/'current-decoded'","D=R/'donor-decoded'").replace("front_classes=set(json.loads((R/'base-classes.json').read_text()))","front_classes=set()")
s=s.replace("'tx_'","'xc_'").replace('tx360cor','txbocore').replace('org/p2sdlx/','org/xbosdl/').replace("('xendroid/',)","('com/izzy2lost/x1box/',)").replace('xendroid.compose','com.izzy2lost.x1box').replace('start=21','start=26')
# Native methods in globally obfuscated classes must also be relocated; none exist except SDL/app native classes.
a=s.index('library_names={');b=s.index('\nfor n,root',a)
s=s[:a]+"library_names={'file_redirect_hook':'xbox_redirect_hook','gsl_alloc_hook':'xbo_alloc_hook','hook_impl':'xbox_impl','main_hook':'xbox_hook'}\n"+s[b:]
s=s.replace("if val=='ARMSX2':val='TURBORAMA_PS2'","# No PS2 edits.").replace("if val=='_preferences':val='_ps2_preferences'","# Preserve donor preference name x1box_prefs.")
s=s.replace(":xbox360emu",":xboxemu").replace(":xbox360",":xbox").replace('.xbox360.','.xbox.')
s=s.replace("if name.endswith('EmulatorHostActivity')","if name.endswith('.MainActivity')")
s=s.replace("if e.tag not in ['activity','provider','uses-library','service']:continue","if e.tag not in ['activity','provider','uses-library','service']:continue")
s=s.replace("replacements={b'androidx/':b'txbocore/',b'org/libsdl/':b'org/xbosdl/'}","replacements={b'androidx/':b'txbocore/',b'org/libsdl/':b'org/xbosdl/',b'org_libsdl_':b'org_xbosdl_'}")
a=s.index("notice=M/'assets/xbox360-integration'")
s=s[:a]+"""notice=M/'assets/xbox-classic';notice.mkdir(exist_ok=True)
for n in ['LICENSE','COPYING','COPYING.LIB']:shutil.copy2(R/'upstream'/n,notice/n)
(R/'class-map.json').write_text(json.dumps(class_map),encoding='utf-8');(R/'resource-map.json').write_text(json.dumps(resource_map),encoding='utf-8')
print('Prepared',len(class_map),'classes and',len(idmap),'resources')
"""
# Remove accidental inherited DocumentsProvider special handling; no added Xbox document provider.
s=s.replace("'com.izzy2lost.x1box.DocumentsProvider'","'xendroid.compose.DocumentsProvider'")
(R/'merge_xbox.py').write_text(s,encoding='utf-8')
note='''# Trabalho atual — PS2 parado por ordem expressa

Não modificar nem instalar outro PS2. ARMSX2 permanece idêntico à base ca5556ac.
Pedido ativo: vídeos SNES BR/MegaDrive BR/Xbox360/Xbox, Xbox clássico Android no mesmo APK, capas Jaguar/PCE CD e motor PCE CD.
Preparação em platform-xbox-pce-refresh; ainda NÃO empacotada/instalada. Base/telefone ca5556ac, recuperação integral F:/Turborama-build-archive/TurboramaStation-before-NetherSX2-ca5556ac.apk.
NetherSX2 em ps2-replacement foi cancelado e nunca instalado. Não executar suas receitas.
USB não detectada na última consulta. Preservar jogos/dados. Consulte HANDOFF.md desta revisão.

## Histórico superado onde conflita

'''
f=P/'AGENTS.md';t=f.read_text(encoding='utf-8')
if not t.startswith('# Trabalho atual — PS2 parado'):f.write_text(note+t,encoding='utf-8')
(R/'HANDOFF.md').write_text(note,encoding='utf-8')
shutil.copy2(__file__,R/'prepare_xbox_classic.py')
