"""Build both DEX modules from the exact R67 composition plus recovery, never from R57."""
from pathlib import Path
import argparse,datetime,json,os,shutil,subprocess,zipfile
from source_composition import verified_composition,sha
p=argparse.ArgumentParser();p.add_argument('--android-jar',required=True);p.add_argument('--d8-jar')
p.add_argument('--jdk',help='JDK17 directory; required for reproducible DEX compilation')
p.add_argument('--output',required=True);p.add_argument('--api-check-only',action='store_true');a=p.parse_args()
out=Path(a.output).resolve();android=Path(a.android_jar).resolve()
if out.exists() or (os.name=='nt' and out.drive.upper()!='E:'):raise SystemExit('Use a new build directory; on Windows use E:')
if sha(android)!='6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad':raise SystemExit('Exact API34 jar required')
if not a.api_check_only and (not a.d8_jar or sha(a.d8_jar)!='d43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0'):raise SystemExit('Exact D8 build tools34 required')
jdk=Path(a.jdk).resolve() if a.jdk else None
java=str(jdk/'bin'/('java.exe' if os.name=='nt' else 'java')) if jdk else 'java'
javac=str(jdk/'bin'/('javac.exe' if os.name=='nt' else 'javac')) if jdk else 'javac'
javac_version=subprocess.check_output([javac,'-version'],stderr=subprocess.STDOUT,text=True).strip()
if not a.api_check_only and not javac_version.startswith('javac 17.'):raise SystemExit('Use JDK17 with this D8, including --release 8')
sources=verified_composition();out.mkdir(parents=True)
for name,path in sources.items():dst=out/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dst)
(out/'evidence').mkdir();(out/'temp').mkdir();env=dict(os.environ,TMP=str(out/'temp'),TEMP=str(out/'temp'))
def run(command,label):
    result=subprocess.run(list(map(str,command)),capture_output=True,env=env)
    (out/'evidence'/(label+'.log')).write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(label+' failed; inspect local build log')
def compile(name,prefixes,classpath):
    classes=out/(name+'-classes');classes.mkdir();argfile=out/(name+'.args')
    args=['--release','8','-encoding','UTF-8','-proc:none','-cp',classpath,'-d',str(classes)]+[str(out/path) for path in sorted(sources) if path.startswith(prefixes)]
    argfile.write_text('\n'.join('"'+value.replace('\\','/')+'"' for value in args))
    run([javac,'@'+str(argfile)],name+'-javac');jar=out/(name+'.jar')
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(classes.rglob('*.class')):info=zipfile.ZipInfo(path.relative_to(classes).as_posix(),(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,path.read_bytes())
    return jar
client=compile('client',('client/src/java/',),str(android));rooms=compile('rooms',('netplay-src/','dependency-src/'),str(android)+os.pathsep+str(client))
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseAPK':'d746cc02b602162b19509cd44ad7cf751e320de3b52199e7d48e86e9e897228f',
    'packageBaseAPK':'72ce7c2cbb3d7cf14ad122b0b98e42a41563114bbbc5c925caedbdee49ff66c3','packageOverlaySource':'c2a1a6d130552b4470b2be3f49db0d1ab72c37b5','sourceCount':len(sources),'sourceHashes':{name:sha(path) for name,path in sorted(sources.items())},'api34Java8Compiled':True,'javacVersion':javac_version,
    'clientJarSHA256':sha(client),'roomsJarSHA256':sha(rooms),'apiCheckOnly':a.api_check_only,'dexBuilt':False,'apkBuilt':False,'installed':False}
if not a.api_check_only:
    for name,jar in [('client',client),('rooms',rooms)]:
        dest=out/(name+'-dex');dest.mkdir();command=[java,'-cp',a.d8_jar,'com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',dest]
        if name=='rooms':command+=['--classpath',client]
        run(command+[jar],name+'-d8')
        if [p.name for p in dest.iterdir()]!=['classes.dex']:raise RuntimeError('Unexpected multi-DEX output')
        report[name+'DexSHA256']=sha(dest/'classes.dex')
    report['dexBuilt']=True
(out/'evidence/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({key:value for key,value in report.items() if key!='sourceHashes'}))
