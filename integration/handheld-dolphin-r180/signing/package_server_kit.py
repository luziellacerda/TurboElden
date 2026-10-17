"""Build the private kit from the exact signed APK and received R179 authority.

No APK/ROM/BIOS/key/phone logs are packaged; no registration or deployment.
"""
from pathlib import Path
import argparse,copy,hashlib,json,zipfile

def digest(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def require(v,m):
 if not v:raise ValueError(m)
parser=argparse.ArgumentParser(description='Prepare an exact private R180 server kit without APK, key or deployment.')
parser.add_argument('--task',required=True,type=Path)
parser.add_argument('--r179-kit',required=True,type=Path)
args=parser.parse_args()
p=args.task.resolve()
apk=p/'final/TurboStations-Premium-R180.apk'
proof=json.loads((p/'final/final-apk-proof.json').read_text())
require(proof['passed'] and proof['v2'] and proof['v3'] and proof['zipAlignment16KiB'] and not proof['installed'],'Signed reviewed candidate required')
with apk.open('rb') as f:require(hashlib.file_digest(f,'sha256').hexdigest()==proof['apkSha256'],'Final APK hash changed')
basekit=args.r179_kit.resolve()
require(digest(basekit.read_bytes())=='c48fac7fb962bf74212a505b6b00c27ab2adce4fb99522a89cd2ccf2641d0615','Exact received R179 kit required')
with zipfile.ZipFile(basekit) as z:
 old={n:z.read(n) for n in z.namelist()}
 manifest=json.loads(old['MANIFESTO-ARQUIVOS.json'])
 for n,v in manifest['files'].items():require(len(old[n])==v['bytes'] and digest(old[n])==v['sha256'],'Parent kit manifest mismatch')
 incoming=json.loads(old['incoming.json']);policies=json.loads(old['profile-policies.json'])
 oldregistry=json.loads(old['engines-apk.json'])
rows=json.loads((p/'native/engines.json').read_text())
selected={v['platform']:v for v in rows['engines'] if v['platform'] in ['psx','n64','gamecube','wii','gba']}
require(len(selected)==5 and len(rows['engines'])==14,'Four independent owners and one actual GBA packet core')
files={n:data for n,data in old.items() if n.startswith(('licenses/','references/'))}
files['references/r179-final-apk-proof.json']=old['proofs/final-apk-proof.json']
files['references/r179-kit-manifest.json']=old['MANIFESTO-KIT.json']
with zipfile.ZipFile(apk) as z:
 require(json.loads(z.read('assets/station-online/engines.json'))==rows,'Final APK engine asset differs')
 for n in old:
  if not n.startswith('artifacts/'):continue
  data=z.read('lib/arm64-v8a/'+Path(n).name)
  require(data[:6]==b'\x7fELF\x02\x01','Actual AArch64 ELF required')
  if Path(n).name not in ['libstation_psx_online.so','libstation_mupen64plus_runtime.so','libstation_dolphin_runtime.so']:
   require(data==old[n],'Core or dependency changed')
  files[n]=data
with zipfile.ZipFile(apk) as z:
 for name in ['libgpsp_station_online.so','libstation_retroarch.so']:
  data=z.read('lib/arm64-v8a/'+name)
  require(data[:6]==b'\x7fELF\x02\x01','Exact new core/runtime ELF')
  files['artifacts/'+name]=data
for row in incoming['engines']:
 actual=selected[row['platform']]
 strip=lambda e:{k:v for k,v in e.items() if k not in ['engineId','runtimeSha256','controllerProfiles','requireExplicitEngineModes']}
 expected=copy.deepcopy(row)
 if row['platform']=='psx':require(expected['options'].count('inputDelayFrames=8\n')==1,'Preserve stable PSX input delay')
 if row['platform']=='gamecube':
  require(expected['options'].count('padBuffer=8\n')==1,'Exact GC eight-frame donor')
  expected['options']=expected['options'].replace('padBuffer=8\n','padBuffer=5\n')
  for definition in expected['controllerProfiles']:
   require(definition['configuration']['coreOptions'].count('padBuffer=8\n')==1,'Exact GC controller options')
   definition['configuration']['coreOptions']=definition['configuration']['coreOptions'].replace('padBuffer=8\n','padBuffer=5\n')
 require(strip(expected)==strip(actual),'Unrequested engine policy change')
 if row['platform'] in ('psx','gamecube'):row.update(options=expected['options'],controllerProfiles=expected['controllerProfiles'])
 row['engineId']=actual['engineId'];row['runtimeSha256']=actual['runtimeSha256']
 policy=policies['profiles'][row['platform']]
 require(policy['coreSha256']==row['coreSha256'],'Core policy changed')
 policy['engineId']=row['engineId'];policy['runtimeSha256']=row['runtimeSha256']
 if row['platform'] in ('psx','gamecube'):
  config=row['controllerProfiles'][0]['configuration']
  raw=json.dumps({k:config[k] for k in ['schemaVersion','controllerProfile','devices','coreOptions']},ensure_ascii=False,separators=(',',':')).replace('/','\\/').encode()
  policy['profileSha256']=digest(raw)
 require(digest(files['artifacts/'+row['runtimeLibrary']])==row['runtimeSha256'],'Actual runtime hash')
 require(digest(files['artifacts/'+row['library']])==row['coreSha256'],'Actual core hash')
 for n,h in row['dependencySha256'].items():require(digest(files['artifacts/'+n])==h,'Actual dependency hash')
gba=copy.deepcopy(selected['gba'])
gba.update(sourceRevision='5819380c2ffb0900219d700a382ee68c464ebb99',dependencySha256={})
gba['controllerProfiles']=[dict(controllerProfile='gba-gpsp-netpacket-v1',maximumPlayers=5,
 configuration=dict(schemaVersion=1,controllerProfile='gba-gpsp-netpacket-v1',devices=[1],coreOptions=gba['options']))]
require(digest(files['artifacts/'+gba['library']])==gba['coreSha256'] and digest(files['artifacts/'+gba['runtimeLibrary']])==gba['runtimeSha256'],'Exact GBA core/runtime binding')
incoming['engines'].append(gba)
config=gba['controllerProfiles'][0]['configuration']
profile_hash=digest(json.dumps(config,ensure_ascii=False,separators=(',',':')).replace('/','\\/').encode())
policies['profiles']['gba']=dict(controllerProfile='gba-gpsp-netpacket-v1',profileSha256=profile_hash,
 maximumPlayers=5,engineId=gba['engineId'],coreSha256=gba['coreSha256'],runtimeSha256=gba['runtimeSha256'])
files['references/gpsp-source.json']=encoded(dict(upstream='https://github.com/libretro/gpsp',
 commit='5819380c2ffb0900219d700a382ee68c464ebb99',buildRecipe='integration/handheld-dolphin-r180/recipe/build_gpsp.py',
 sourceCodeChanged=False,androidModuleName='gpsp_station_online',nativeNetpacketProtocol='gpSP v1.0'))
files['licenses/GPSp-NOTICE.txt']=b'gpSP for libretro, GPL-2.0. Upstream https://github.com/libretro/gpsp at 5819380c2ffb0900219d700a382ee68c464ebb99. Original COPYING.GPL-2.0 is included. Emulator source unchanged; Android module name and 16 KiB build recipe supplied in the app source repository. RetroArch runtime retained byte for byte under its existing GPL-3.0 notice.\n'
files['engines-apk.json']=encoded(rows);files['incoming.json']=encoded(incoming);files['profile-policies.json']=encoded(policies)
for name,source in [('proofs/final-apk-proof.json',p/'final/final-apk-proof.json'),('proofs/compile-receipt.json',p/'compile/receipt.json'),('proofs/native-receipt.json',p/'native/receipt.json'),('proofs/native-abi-contract.json',p/'native/abi-contract.json'),('proofs/unsigned-package.json',p/'package/unsigned-package.json')]:files[name]=source.read_bytes()
files['LEIA-ME.txt']=('R180 candidata assinada: GameCube restaura a politica anterior a R174/R177; Wii aceita os controles verificados; GBA usa gpSP netpacket com um GBA e P1 por aparelho.\n'
 'APK SHA256 '+proof['apkSha256']+'\nBase R179 exata: seis entradas substituidas, duas adicionadas e 39 DEX preservados.\n'
 'Os nucleos anteriores e as configuracoes PSX/N64/Wii permanecem exatos. O cadastro GBA exige modos de link por edicao, sem aprovar jogos automaticamente.\n'
 'Aplicacao no registro protegido e ativacao da API exigem autorizacao administrativa; este kit nao executa nem solicita autenticacao.\n'
 'Testes Android em dois aparelhos ainda sao necessarios. O experimento GameCube de oito quadros foi reprovado pelo proprietario.\n'
 'Nenhum APK, ROM, BIOS, chave, senha, serial ou log bruto esta neste arquivo.\n').encode('utf-8')
elf_count=sum(n.startswith('artifacts/') for n in files)
meta={'schema':'station.r180.private-kit.v1','revision':'R180','sourceCommit':proof['sourceCommit'],
 'apkSha256':proof['apkSha256'],'apkBytes':proof['apkBytes'],'baselineApkSha256':proof['baseApkSha256'],
 'referenceKitR179Sha256':digest(basekit.read_bytes()),'independentEngineIds':{k:v['engineId'] for k,v in selected.items()},
 'elfCount':elf_count,'changedApkEntries':proof['replacedEntries'],'addedApkEntries':proof['addedEntries'],
 'preservedDexPartitions':39,'sdk':{'minimum':26,'target':34},'preservedExistingCoreBinaries':True,
 'newGbaCore':True,'gamecubeCpuOverrideRemoved':True,'r173CpuSelectionPreserved':True,
 'gamecubePadBufferBefore':8,'gamecubePadBufferAfter':5,'wiiPadBuffer':5,'androidUpdaterFixPreserved':True,
 'psxInputDelayBefore':8,'psxInputDelayAfter':8,'gbaControllersPerPeer':1,'gbaExactModeApprovalRequired':True,
 'serverApplied':False,'physicalGameplayValidated':False,'installed':False,'productionUpdaterEnabled':False,
 'containsApkRomBiosKeySerialOrRawLogs':False,'filesSha256':{n:digest(data) for n,data in files.items() if n.startswith('artifacts/')}}
files['MANIFESTO-KIT.json']=encoded(meta)
filemeta={'schema':'station.private-kit.files.v1','revision':'R180','files':{n:{'bytes':len(data),'sha256':digest(data)} for n,data in sorted(files.items())}}
files['MANIFESTO-ARQUIVOS.json']=encoded(filemeta)
out=p/'private-server-kit';out.mkdir(exist_ok=False);target=out/'Kit-Servidor-TurboStations-R180-Independentes.zip'
with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,data in sorted(files.items()):z.writestr(n,data)
with zipfile.ZipFile(target) as z:
 require(set(z.namelist())==set(files) and len(z.namelist())==len(set(z.namelist())),'Exact unique kit entries')
 for n,data in files.items():require(z.read(n)==data,'Kit readback mismatch')
receipt={'schema':'station.r180.private-kit-receipt.v1','passed':True,'apkSha256':proof['apkSha256'],'zipSha256':digest(target.read_bytes()),'zipBytes':target.stat().st_size,'fileCount':len(files),'elfCount':elf_count,'engineIds':meta['independentEngineIds'],'recipeSha256':digest(Path(__file__).read_bytes()),'serverApplied':False,'physicalGameplayValidated':False}
(out/'kit-receipt.json').write_bytes(encoded(receipt));print(json.dumps(receipt))
