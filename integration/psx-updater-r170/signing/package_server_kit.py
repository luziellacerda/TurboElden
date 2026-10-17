"""Build the private kit from the exact signed APK and received R169 authority.

No APK/ROM/BIOS/key/phone logs are packaged; no registration or deployment.
"""
from pathlib import Path
import argparse,copy,hashlib,json,zipfile

def digest(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def require(v,m):
 if not v:raise ValueError(m)
parser=argparse.ArgumentParser(description='Prepare an exact private R170 server kit without APK, key or deployment.')
parser.add_argument('--task',required=True,type=Path)
parser.add_argument('--r169-kit',required=True,type=Path)
args=parser.parse_args()
p=args.task.resolve()
apk=p/'final/TurboStations-Premium-R170.apk'
proof=json.loads((p/'final/final-apk-proof.json').read_text())
require(proof['passed'] and proof['v2'] and proof['v3'] and proof['zipAlignment16KiB'] and not proof['installed'],'Signed reviewed candidate required')
with apk.open('rb') as f:require(hashlib.file_digest(f,'sha256').hexdigest()==proof['apkSha256'],'Final APK hash changed')
basekit=args.r169_kit.resolve()
require(digest(basekit.read_bytes())=='859b33b156698abecadadf035f8117a4b2b680439c4fed32eb2001347dc6c832','Exact received R169 kit required')
with zipfile.ZipFile(basekit) as z:
 old={n:z.read(n) for n in z.namelist()}
 manifest=json.loads(old['MANIFESTO-ARQUIVOS.json'])
 for n,v in manifest['files'].items():require(len(old[n])==v['bytes'] and digest(old[n])==v['sha256'],'Parent kit manifest mismatch')
 incoming=json.loads(old['incoming.json']);policies=json.loads(old['profile-policies.json'])
 oldregistry=json.loads(old['engines-apk.json'])
rows=json.loads((p/'native/engines.json').read_text())
selected={v['platform']:v for v in rows['engines'] if v['platform'] in ['psx','n64','gamecube','wii']}
require(len(selected)==4 and len(rows['engines'])==13,'Four exact APK independent rows')
files={n:data for n,data in old.items() if n.startswith(('licenses/','references/'))}
files['references/r169-final-apk-proof.json']=old['proofs/final-apk-proof.json']
files['references/r169-kit-manifest.json']=old['MANIFESTO-KIT.json']
with zipfile.ZipFile(apk) as z:
 require(json.loads(z.read('assets/station-online/engines.json'))==rows,'Final APK engine asset differs')
 for n in old:
  if not n.startswith('artifacts/'):continue
  data=z.read('lib/arm64-v8a/'+Path(n).name)
  require(data[:6]==b'\x7fELF\x02\x01','Actual AArch64 ELF required')
  if Path(n).name not in ['libstation_psx_online.so','libstation_mupen64plus_runtime.so','libstation_dolphin_runtime.so']:
   require(data==old[n],'Core or dependency changed')
  files[n]=data
for row in incoming['engines']:
 actual=selected[row['platform']]
 strip=lambda e:{k:v for k,v in e.items() if k not in ['engineId','runtimeSha256','controllerProfiles','requireExplicitEngineModes']}
 require(strip(row)==strip(actual),'Unrequested engine policy change')
 row['engineId']=actual['engineId'];row['runtimeSha256']=actual['runtimeSha256']
 policy=policies['profiles'][row['platform']]
 require(policy['coreSha256']==row['coreSha256'],'Core policy changed')
 policy['engineId']=row['engineId'];policy['runtimeSha256']=row['runtimeSha256']
 require(digest(files['artifacts/'+row['runtimeLibrary']])==row['runtimeSha256'],'Actual runtime hash')
 require(digest(files['artifacts/'+row['library']])==row['coreSha256'],'Actual core hash')
 for n,h in row['dependencySha256'].items():require(digest(files['artifacts/'+n])==h,'Actual dependency hash')
files['engines-apk.json']=encoded(rows);files['incoming.json']=encoded(incoming);files['profile-policies.json']=encoded(policies)
for name,source in [('proofs/final-apk-proof.json',p/'final/final-apk-proof.json'),('proofs/compile-receipt.json',p/'compile/receipt.json'),('proofs/native-receipt.json',p/'native/receipt.json'),('proofs/native-abi-contract.json',p/'native/abi-contract.json'),('proofs/unsigned-package.json',p/'package/unsigned-package.json')]:files[name]=source.read_bytes()
files['LEIA-ME.txt']=('R170 candidata assinada: PSX por evento e retomada, atualizador privado.\nAPK SHA256 '+proof['apkSha256']+'\nBase R169 original e SDK26/34 preservados. Exatamente sete entradas substituidas; zero adicoes/remoções no ZIP.\nCadastrar quatro IDs aditivamente contra a autoridade R169 efetiva/fresca, preservando cada modo e recusa por edicao exata.\nO parentesco com R169 nao aprova jogo novo nem amplia numero de jogadores.\nEste kit nao publica APK ou API, nao reinicia servico e nao instala telefone.\nProva fisica de partida e instalador Android ainda pendente. Sem APK, ROM, BIOS, chave, senha ou logs brutos.\n').encode('utf-8')
meta={'schema':'station.r170.private-kit.v1','revision':'R170','sourceCommit':proof['sourceCommit'],'apkSha256':proof['apkSha256'],'apkBytes':proof['apkBytes'],'baselineApkSha256':proof['baseApkSha256'],'referenceKitR169Sha256':digest(basekit.read_bytes()),'independentEngineIds':{k:v['engineId'] for k,v in selected.items()},'binaryCount':6,'distinctDependencyCount':21,'elfCount':27,'changedApkEntries':proof['replacedEntries'],'preservedDexPartitions':38,'sdk':{'minimum':26,'target':34},'preservedCorePolicies':True,'exactModeApprovalRequired':True,'serverApplied':False,'physicalGameplayValidated':False,'installed':False,'productionUpdaterEnabled':False,'containsApkRomBiosKeySerialOrRawLogs':False,'filesSha256':{n:digest(data) for n,data in files.items() if n.startswith('artifacts/')}}
files['MANIFESTO-KIT.json']=encoded(meta)
filemeta={'schema':'station.private-kit.files.v1','revision':'R170','files':{n:{'bytes':len(data),'sha256':digest(data)} for n,data in sorted(files.items())}}
files['MANIFESTO-ARQUIVOS.json']=encoded(filemeta)
out=p/'private-server-kit';out.mkdir(exist_ok=False);target=out/'Kit-Servidor-TurboStations-R170-Independentes.zip'
with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,data in sorted(files.items()):z.writestr(n,data)
with zipfile.ZipFile(target) as z:
 require(set(z.namelist())==set(files) and len(z.namelist())==len(set(z.namelist())),'Exact unique kit entries')
 for n,data in files.items():require(z.read(n)==data,'Kit readback mismatch')
receipt={'schema':'station.r170.private-kit-receipt.v1','passed':True,'apkSha256':proof['apkSha256'],'zipSha256':digest(target.read_bytes()),'zipBytes':target.stat().st_size,'fileCount':len(files),'elfCount':27,'engineIds':meta['independentEngineIds'],'recipeSha256':digest(Path(__file__).read_bytes()),'serverApplied':False,'physicalGameplayValidated':False}
(out/'kit-receipt.json').write_bytes(encoded(receipt));print(json.dumps(receipt))
