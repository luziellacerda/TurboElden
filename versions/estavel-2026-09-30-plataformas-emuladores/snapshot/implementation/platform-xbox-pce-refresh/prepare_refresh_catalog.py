from pathlib import Path
import json,re,zipfile,hashlib,urllib.parse,urllib.request,shutil,xml.etree.ElementTree as ET
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-xbox-pce-refresh';M=R/'merged'
def norm(s):
 s=re.sub(r'\([^)]*\)|\[[^]]*\]','',s).casefold().replace(', the','').strip()
 s=re.sub(r'^(the|a) ','',s)
 return re.sub('[^a-z0-9]','',s)
def gamestem(f):return Path(urllib.parse.unquote(urllib.parse.urlparse(f['Url']).path)).stem
with zipfile.ZipFile(P/'TurboramaStation-Plataformas-Organizadas.apk') as z:before=z.read('assets/turboretro/catalog.json');cat=json.loads(before)
assetdir=M/'assets/platform-refresh/covers';assetdir.mkdir(parents=True,exist_ok=True)
base=Path(r'G:\RETROBAT TESTES\Retrobat-V8.1.2-160GB\RetroBat\roms')
manifest=[];missing=[];hidden=[]
aliases={'towersii':'towersiiplightofthestargazer','protector-specialedition':'protectorspecialedition'}
for key,folder in [('jaguar','jaguar'),('Pc Engine cd','pcenginecd')]:
 c=next(c for c in cat if c['Name']==key)
 viable=[]
 for f in c['Files']:
  ext=Path(urllib.parse.urlparse(f['Url']).path).suffix.lower()
  if ext not in ['.zip','.7z','.j64','.jag','.abs','.rom','.bin','.chd','.cue','.ccd','.pce']:
   hidden.append({'category':key,'id':f['Id'],'name':f['DisplayName'],'reason':'metadata_or_media_not_game'});continue
  viable.append(f)
  name=norm(gamestem(f));name=aliases.get(name,name)
  candidates=[]
  for p in (base/folder/'images').glob('*'):
   stem=re.sub(r'-(thumb|image|boxart)$','',p.stem)
   if norm(stem)==name and p.suffix.lower() in ['.png','.jpg','.jpeg'] and p.stem.endswith(('-thumb','-image','-boxart')):
    candidates.append(p)
  candidates.sort(key=lambda p:(not p.stem.endswith('-thumb'),str(p)))
  if not candidates:missing.append({'category':key,'id':f['Id'],'name':f['DisplayName'],'normalized':name});continue
  src=candidates[0];dest=assetdir/(f['Id']+src.suffix.lower());shutil.copy2(src,dest)
  manifest.append({'category':key,'id':f['Id'],'name':f['DisplayName'],'source':str(src),'asset':'platform-refresh/covers/'+dest.name,'local':'/data/data/org.emulationstation.frontend/files/turbo-game-covers/'+dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 c['Files']=viable
source=json.loads(Path(r'H:\ARQUIVOS DLL SAMBOX\CATALOGO_ORIGINAL_LINKS_E_JOGOS.json').read_text(encoding='utf-8-sig'))
xbox=next(c for c in source if c['Name']=='Xbox')
xbox.update({'Name':'xbox','CatalogLabel':'roms','R2Pasta':'xbox','Android':True,'AndroidPackage':xbox['RequiredPackage'],'AndroidDemo':xbox['Demo'],'AndroidMensal':xbox['Mensal'],'Oculta':False})
# Original game's IDs, URLs and access rules are retained.
cat.append(xbox)
(R/'catalog-before.json').write_bytes(before)
(R/'catalog-refresh.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'covers-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'covers-missing.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'catalog-hidden-metadata.json').write_text(json.dumps(hidden,ensure_ascii=False,indent=2),encoding='utf-8')
print('Local covers',len(manifest),'metadata hidden',len(hidden),'Xbox items',len(xbox['Files']),'Missing',missing)
