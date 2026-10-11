"""Compile the current R126 overlay plus PSX; compile-only SDL ABI is not input DEX."""
from pathlib import Path
import argparse, hashlib, json, subprocess, shutil, zipfile, os

ROOT=Path(__file__).resolve().parents[1]
VERSIONS=ROOT.parents[1]/'versions'
CLIENT_SHA='011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313'

def native(path):return Path('\\\\?\\'+str(path.resolve())) if os.name=='nt' else path
def sha(path):return hashlib.sha256(native(path).read_bytes()).hexdigest()
def run(cmd,out,name):
    result=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,encoding='utf-8',errors='replace')
    (out/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(name+' failed; see '+str(out/(name+'.log')))

def sources():
    base=VERSIONS/'station-video-room-footer-r124-20261011'
    manifest=json.loads((base/'JAVA-SOURCE-MANIFEST.json').read_text(encoding='utf-8'));effective={}
    for name,digest in manifest.items():
        path=base/'java'/name
        if sha(path)!=digest:raise ValueError('R124 source changed: '+name)
        if name.startswith(('netplay-src/','dependency-src/')):effective[name]=path
    for root in (VERSIONS/'station-mupen-online-r125-20261011/java',VERSIONS/'station-dolphin-online-r126-20261011/java',ROOT/'java'):
        for path in root.rglob('*.java'):effective['netplay-src/'+path.relative_to(root).as_posix()]=path
    return effective

def main():
    p=argparse.ArgumentParser()
    for key in ('out','jdk','android-jar','d8-jar','client-jar','sdl-abi-jar'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    if sha(a.client_jar)!=CLIENT_SHA:raise ValueError('Exact unchanged client JAR required')
    effective=sources();frozen={name:sha(path) for name,path in sorted(effective.items())}
    classes=a.out/'classes'
    allowed=Path(r'G:\StationNormalOwnersR127\psx').resolve()
    if allowed not in a.out.resolve().parents or classes.resolve().parent!=a.out.resolve():raise ValueError('Use the single PSX working tree for compilation')
    # Only rebuild this recipe's class output, so removed/renamed nested classes
    # cannot leak from an earlier compilation into the current productive DEX.
    if classes.exists():shutil.rmtree(classes)
    classes.mkdir();alias=a.out/'source-alias';paths=[]
    for i,(name,path) in enumerate(sorted(effective.items())):
        target=alias/str(i)/path.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(native(path),target);paths.append(target)
    cp=';'.join(map(str,(a.android_jar,a.client_jar,a.sdl_abi_jar)))
    args=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]+list(map(str,paths))
    file=a.out/'javac.args';file.write_text('\n'.join('"'+x.replace('\\','/')+'"' for x in args)+'\n',encoding='utf-8')
    run([a.jdk/'javac.exe','@'+str(file)],a.out,'javac')
    if any(sha(path)!=frozen[name] for name,path in effective.items()):raise ValueError('Source changed during compilation')
    jar=a.out/'rooms.jar'
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_STORED) as archive:
        for path in sorted(classes.rglob('*.class')):
            name=path.relative_to(classes).as_posix()
            if name.startswith('org/libsdl/'):raise ValueError('Compile-only stub leaked into output')
            archive.writestr(zipfile.ZipInfo(name,(1980,1,1,0,0,0)),path.read_bytes())
    dex=a.out/'dex';dex.mkdir(exist_ok=True)
    run([a.jdk/'java.exe','-cp',a.d8_jar,'com.android.tools.r8.D8','--release','--min-api','28','--lib',a.android_jar,
         '--classpath',a.client_jar,'--classpath',a.sdl_abi_jar,'--output',dex,jar],a.out,'d8')
    files=list(dex.glob('*.dex'))
    if len(files)!=1:raise ValueError('Expected one rooms DEX')
    final=a.out/'classes35.dex';shutil.copyfile(files[0],final)
    receipt={'sourceCount':len(effective),'sources':frozen,
        'clientClasspathJarSha256':CLIENT_SHA,'compileOnlySdlJarSha256':sha(a.sdl_abi_jar),'compileOnlyStubsPackaged':False,
        'classes35Sha256':sha(final),'roomsJarSha256':sha(jar),'otherDexChanged':False,'physicalGameplayValidated':False}
    (a.out/'compile-java.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('sourceCount','classes35Sha256','compileOnlyStubsPackaged')}))
if __name__=='__main__':main()
