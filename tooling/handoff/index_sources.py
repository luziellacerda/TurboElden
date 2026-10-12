from pathlib import Path
import hashlib, json, importlib.util, subprocess, argparse

p=argparse.ArgumentParser()
p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--out',type=Path,default=Path('work/handoff-inventory'))
p.add_argument('--jdk',type=Path,required=True,help='JDK 17 bin directory; compile-only source parsing')
a=p.parse_args(); repo=a.repo.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=repo/'versions/station-video-room-footer-r124-20261011'
manifest=read(base/'JAVA-SOURCE-MANIFEST.json')
files={}
for n,h in manifest.items():
    f=base/'java'/n
    assert sha(f)==h,n
    files[n]={'path':f.relative_to(repo).as_posix(),'sha256':h,'composition':'R124 baseline'}
for rel,label in [
  ('versions/station-mupen-online-r125-20261011/java','R125 netplay overlay'),
  ('versions/station-dolphin-online-r126-20261011/java','R126 netplay overlay'),
  ('integration/psx-online/java','R127 PSX and shared netplay overlay')]:
    for f in sorted((repo/rel).rglob('*.java')):
        key='netplay-src/'+f.relative_to(repo/rel).as_posix()
        files[key]={'path':f.relative_to(repo).as_posix(),'sha256':sha(f),'composition':label}
# Exact Java overlays from later recipes. Byte transforms of other classes are
# indexed separately as recipes, so baseline source is never falsely called final.
for rel,label in [('integration/sony-internal','R131 Sony hosts'),('integration/settings-refinement-r134','R134 settings overlay')]:
    for sub in ('java','composition/java','ps3/java','ps4/java'):
        for f in sorted((repo/rel/sub).rglob('*.java')):
            key=f.relative_to(repo/rel/sub).as_posix()
            matching=next((n for n in files if n.endswith(key)),None)
            key=matching or key
            files[key]={'path':f.relative_to(repo).as_posix(),'sha256':sha(f),'composition':label}
for f in sorted((repo/'integration/local-sony-demos/java').rglob('*.java')):
    key=f.relative_to(repo/'integration/local-sony-demos/java').as_posix()
    files[key]={'path':f.relative_to(repo).as_posix(),'sha256':sha(f),'composition':'R129 local Sony demos'}
paths=[str(repo/r['path']) for r in files.values()]
(out/'java-inputs.txt').write_text('\n'.join(paths)+'\n',encoding='utf-8')
classes=out/'parser-classes';classes.mkdir(exist_ok=True)
subprocess.run([str(a.jdk/'javac.exe'),'-encoding','UTF-8','-d',str(classes),str(Path(__file__).with_name('JavaSourceIndex.java'))],check=True,capture_output=True)
r=subprocess.run([str(a.jdk/'java.exe'),'-cp',str(classes),'JavaSourceIndex',str(out/'java-inputs.txt'),str(out/'methods-raw.json')],capture_output=True,text=True,encoding='utf-8')
if r.returncode:raise RuntimeError(r.stderr)
methods=read(out/'methods-raw.json')
for m in methods:
    m['file']=Path(m['file']).relative_to(repo).as_posix()
    m['sourceURL']='https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/'+m['file']+'#L'+str(m['line'])
write('java-source-composition.json',{'schema':'station.source.composition.index.v1','baselineCommit':'4f9039eb9ce13907ce043870bfe1f6e294888556','sourceCount':len(files),'files':files,'limitations':['Source syntax index, not byte proof of all packaged classes.','R130 StationFrontend and StationSinglePassVideo720 and R132 SwitchConfigPatcher include byte transformations described by recipes.','Generated private pins, compiled third party owners and sources unavailable in public inventory remain explicitly outside syntax index.']})
write('java-methods.json',{'schema':'station.java.syntax.methods.v1','methodCount':len(methods),'semanticTypeChecking':False,'includesConstructorsAndAnonymousMethods':True,'lambdaExpressionsIndexedAsMethods':False,'methods':methods})
recipes=[]
for root in [repo/'integration',repo/'tooling/release',repo/'versions/station-mupen-online-r125-20261011/recipes',repo/'versions/station-dolphin-online-r126-20261011/recipe']:
    for f in sorted(root.rglob('*')):
        if f.is_file() and f.suffix in ('.py','.java','.cpp','.c','.h') and '__pycache__' not in f.parts:
            recipes.append({'path':f.relative_to(repo).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
write('integration-build-source-index.json',{'schema':'station.build.source.index.v1','files':recipes})
counts={}
for v in files.values():counts[v['composition']]=counts.get(v['composition'],0)+1
write('inventory-summary.json',{'indexedJavaSources':len(files),'methodDeclarations':len(methods),'nativeDeclarations':sum(m['nativeDeclaration'] for m in methods),'integrationAndBuildFiles':len(recipes),'compositionCounts':counts})
print(json.dumps(read(out/'inventory-summary.json')))
