from pathlib import Path
import configparser,hashlib,io,json,shutil,urllib.request,zipfile
ROOT=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
folder=ROOT/'upstream/Clownacy--clownmdemu-libretro-d43c2708b0a3'
records=[]
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TurboStations-source-audit/1'}),timeout=60) as r:return r.read()
def recurse(repo,commit,dest,depth=0):
 assert depth<8
 modules=dest/'.gitmodules'
 if not modules.exists():return
 config=configparser.ConfigParser();config.read(modules)
 tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'))
 assert not tree.get('truncated')
 pins={e['path']:e['sha'] for e in tree['tree'] if e['type']=='commit'}
 for section in config.sections():
  path=config[section]['path'];url=config[section]['url']
  # The libretro target does not build the standalone SDL desktop frontend.
  if path.startswith('frontend/'):continue
  assert url.startswith('https://github.com/')
  childrepo=url.removeprefix('https://github.com/').removesuffix('.git');assert childrepo.split('/')[0] in ('Clownacy','libretro')
  child=(dest/path).resolve();assert child.is_relative_to(folder.resolve())
  # .gitmodules can contain obsolete entries; only actual pinned gitlinks are dependencies.
  if path not in pins:
   print('No gitlink in pinned tree:',repo,path,flush=True)
   continue
  pin=pins[path]
  if not (child/'CMakeLists.txt').exists() and not (child/'include/libretro.h').exists():
   data=get(f'https://codeload.github.com/{childrepo}/zip/{pin}')
   with zipfile.ZipFile(io.BytesIO(data)) as z:
    for member in z.infolist():
     parts=Path(member.filename).parts[1:]
     if not parts:continue
     p=(child/Path(*parts)).resolve();assert p.is_relative_to(child)
     if member.is_dir():p.mkdir(parents=True,exist_ok=True)
     else:
      p.parent.mkdir(parents=True,exist_ok=True)
      with z.open(member) as a,p.open('wb') as b:shutil.copyfileobj(a,b)
   digest=hashlib.sha256(data).hexdigest()
  else:digest=None
  records.append({'repo':childrepo,'commit':pin,'path':str(child.relative_to(folder)),'archiveSha256':digest})
  print(childrepo,pin,flush=True)
  recurse(childrepo,pin,child,depth+1)
recurse('Clownacy/clownmdemu-libretro','d43c2708b0a31c285ce16724b6c4a2e92af07346',folder)
(ROOT/'evidence/clown-submodules.json').write_text(json.dumps(records,indent=2)+'\n')
