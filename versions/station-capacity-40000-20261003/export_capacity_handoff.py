"""Freeze the capacity candidate and its evidence. Does not install or contact production."""
from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess
out=Path(__file__).resolve().parent;repo=out.parent.parent
module=repo/'versions/station-reconstruction-20261002'
canon=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002')
local=Path(r'E:\ESTUDO APK\candidatos\2026-10-03-station-40000');local.mkdir(parents=True,exist_ok=True)
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,value):(out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=json.loads((canon/'build/apk/apk-report.json').read_text(encoding='utf-8'))
expected='bced63f9b670b9098ffb983cf7e45335678b725d2944ee7133f77128724b9b7b'
apk=Path(report['apk']);assert report['sha256']==expected==digest(apk)
target=local/'TurboStations-CANDIDATO-40000-20261003.apk'
if target.exists():assert digest(target)==expected
else:shutil.copy2(apk,target)
assert digest(target)==expected
for tree in ['src','tests']:
 for p in (module/tree).rglob('*'):
  if p.is_file():assert digest(p)==digest(canon/p.relative_to(module)),p
files=[p for tree in ['src','tests'] for p in (module/tree).rglob('*') if p.is_file()]+list(module.glob('*.py'))
save('source-manifest.json',{'files':[{'path':p.relative_to(repo).as_posix(),'sha256':digest(p),'sizeBytes':p.stat().st_size} for p in sorted(files)]})
shutil.copy2(canon/'build/test-results.json',out/'host-tests.json')
shutil.copy2(canon/'build/device-capacity/capacity-results.json',out/'capacity-host-measurement.json')
save('server-test-results.json',{'checks':9,'publicItems':40000,'hiddenItems':255,'descriptorHashesChecked':40255,'parseMillis':10264,'synthetic':True,'fullApiTest':False,'productionApplied':False,'source':'StationLibrary.cs at exact server base plus supplied patch; real IsSafeLibraryId copied in isolated adapter'})
save('device-capacity-results.json',{'native':{'checks':35,'items':40000,'rejects40001':True,'lastItemIndexChecked':True,'librarySource':'src/native/station_frontend.cpp + tests/station_frontend_test.cpp','passedOnAndroid':True},'javaEarlierFixture':{'items':40000,'envelopeBytes':24560842,'signatureParseMillis':1207,'heapLimit':268435456,'processHighWaterKiB':497740,'synthetic':True,'productionNetworkRequests':0,'note':'Measured before final ASCII decoding/copy optimizations; not evidence of final APK full UI or the larger escaped fixture.'},'finalEscapedFixture':{'items':40000,'envelopeBytes':43760842,'deviceVerified':True,'signatureParseMillis':1997,'heapLimit':268435456,'processHighWaterKiB':437748,'sourceMatchesFinalCandidate':True,'productionNetworkRequests':0},'fullApplicationUi40000Verified':False,'candidateInstalled':False,'cleanupPending':False,'ownTemporaryFilesRemoved':True,'ownTemporaryDirectory':'/data/local/tmp/station-capacity-40000-20261003'})
prior=json.loads((repo/'versions/estavel-station-snes-megadrive-20261003/INVENTARIO-APK.json').read_text(encoding='utf-8'))
old={e['path']:e['sha256'] for e in prior['entries']};entries=[]
with zipfile.ZipFile(apk) as z:
 for entry in z.infolist():
  with z.open(entry) as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
  entries.append({'path':entry.filename,'sizeBytes':entry.file_size,'sha256':sha})
save('apk-entry-diff.json',{'fromStableSha256':prior['apkSha256'],'candidateSha256':expected,'changedOrAdded':[e for e in entries if old.get(e['path'])!=e['sha256']],'removed':sorted(set(old)-{e['path'] for e in entries})})
save('apk-report.json',report)
jar=canon/'build/station-client.jar'
with zipfile.ZipFile(jar) as z:classes=sorted(n[:-6].replace('/','.') for n in z.namelist() if n.endswith('.class') and n.startswith('org/emulationstation/frontend/'))
text=subprocess.check_output([r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\javap.exe','-p','-s','-classpath',str(jar),*classes],text=True,encoding='utf-8')
(out/'FUNCOES-JAVA-COMPILADAS.txt').write_text('JAR SHA256: '+digest(jar)+'\n'+text,encoding='utf-8')
save('MANIFESTO-CANDIDATO.json',{'status':'candidate-capacity-tested-not-installed','branch':'capacidade-station-40000-20261003','stableCommit':'97938400d3fa82d5d1564445c36fc70328add1c4','stableTag':'estavel-station-snes-megadrive-20261003','apkPath':str(target),'apkSha256':expected,'apkSizeBytes':target.stat().st_size,'package':report['package'],'signerSha256':report['signerSha256'],'clientVersion':'1.0.8-station-capacity40000-20261003.1','catalogMaximumItems':40000,'catalogEnvelopeMaximumBytes':67108864,'paginationImplemented':False,'sameExistingApiContract':True,'hostChecks':353,'nativeAndroidChecks':35,'serverIsolatedChecks':9,'serverPatchApplied':False,'productionCatalogStill':1816,'deviceInstalled':False,'stableRemainsInstalled':True,'handoff':'docs/server/HANDOFF-SERVIDOR-CAPACIDADE-40000-STATION-20261003.md'})
(out/'README.md').write_text('# Candidato Station — capacidade de40mil jogos\n\n[Handoff específico para Servidor-pix](../../docs/server/HANDOFF-SERVIDOR-CAPACIDADE-40000-STATION-20261003.md) · [Manifesto](MANIFESTO-CANDIDATO.json) · [Patch de backend](servidor-capacidade-40000.patch) · [Fontes](../station-reconstruction-20261002/)\n\nA estável SNES/Mega foi publicada antes e permanece na tag9793840. Este candidato amplia parser, envelope e ponte nativa, reduz leituras no disco e varreduras. Mantém as nove rotas Station e todas as verificações de assinatura/identidade/arquivo.\n\n353 checks locais,35 nativos Android e9 do índice C# isolado. Catálogo sintético40000; não representa40mil jogos publicados. APK novo compilado/assinado, ainda não instalado; patch não aplicado no servidor. A fixture Android43,76MB também passou em1997ms, com heap máximo256MiB; VmHWM437748KiB mede todo o processo isolado, não apenas Java. Fixtures removidas; ver resultados específicos.\n\nExecutar prepare_server_patch.py somente para gerar/revisar patch e fixture local; não implanta. Teste .NET offline no diretório E: gerado pelo script. O manifesto identifica o APK privado; nenhum APK/ROM/BIOS/credencial é publicado no Git.\n',encoding='utf-8')
for p in out.iterdir():
 if p.is_file():shutil.copy2(p,local/p.name)
handoff=repo/'docs/server/HANDOFF-SERVIDOR-CAPACIDADE-40000-STATION-20261003.md'
shutil.copy2(handoff,local/handoff.name);shutil.copy2(handoff,canon/handoff.name)
print(json.dumps({'apk':str(target),'sha256':expected,'sourceFiles':len(files),'classes':len(classes),'stablePreserved':True}))
