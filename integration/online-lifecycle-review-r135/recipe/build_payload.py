"""Build only the reviewed Java overlay. No DEX/APK/device/network operation."""
from pathlib import Path
import argparse,datetime,hashlib,json,struct,subprocess,zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
CLIENT_SHA='011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313'
PACKAGE='org/emulationstation/frontend/netplay/'
CLASSES={PACKAGE+name+'.class' for name in (
    'StationDolphinSession','StationDolphinSession$Session',
    'StationDolphinSession$Session$1','StationDolphinSession$Session$2',
    'StationDolphinSession$Session$Control','StationGameSession',
    'StationGameSession$1','StationGameSession$LaunchReturn','StationHumanDeparture')}
SOURCES=('StationDolphinSession.java','StationGameSession.java','StationHumanDeparture.java')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('out','jdk-bin','android-jar','rooms-jar','client-jar','input-hashes'):
        p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    inputs={'javac':a.jdk_bin/'javac.exe','androidJar':a.android_jar,
            'roomsJar':a.rooms_jar,'clientJar':a.client_jar}
    expected=json.loads(a.input_hashes.read_text(encoding='utf-8'))
    pins=json.loads((ROOT/'SOURCE-PINS.json').read_text(encoding='utf-8'))
    trusted=pins['inputsSha256']
    if expected.get('clientJar')!=CLIENT_SHA:raise ValueError('Exact unchanged R124 client required')
    for name,path in inputs.items():
        if name not in trusted or expected.get(name)!=trusted[name] or sha(path)!=trusted[name]:
            raise ValueError('Pinned tested R134/API34/JDK17 input required: '+name)
    for name,digest in pins['baselineSha256'].items():
        if sha(REPO/name)!=digest:raise ValueError('Baseline source changed: '+name)
    for name,digest in pins['overlaySha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Reviewed overlay changed: '+name)
    sources=[ROOT/'java'/PACKAGE/name for name in SOURCES]
    expected_sources={'java/'+PACKAGE+name for name in SOURCES}
    if set(pins['overlaySha256'])!=expected_sources:raise ValueError('Three exact productive sources required')
    # Reject old output rather than silently deleting files or carrying old classes.
    if a.out.exists() and any(a.out.iterdir()):raise ValueError('Use a new or empty output directory')
    a.out.mkdir(parents=True,exist_ok=True)
    classes=a.out/'classes';classes.mkdir()
    args=[str(inputs['javac']),'-encoding','UTF-8','--release','8','-proc:none',
          '-implicit:none','-sourcepath','', '-cp',';'.join(map(str,(a.android_jar,a.rooms_jar,a.client_jar))),
          '-d',str(classes),*map(str,sources)]
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',timeout=90)
    (a.out/'javac.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Productive compilation failed; see javac.log')
    files=sorted(classes.rglob('*.class'))
    names={path.relative_to(classes).as_posix() for path in files}
    if names!=CLASSES:raise ValueError('Exact nine productive classes required; no fixtures/dependencies permitted')
    if any(struct.unpack('>H',path.read_bytes()[6:8])[0]!=52 for path in files):
        raise ValueError('Java8 class major version52 required')
    jar=a.out/'online-lifecycle-overlay.jar'
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_STORED) as archive:
        for path in files:
            archive.writestr(zipfile.ZipInfo(path.relative_to(classes).as_posix(),(1980,1,1,0,0,0)),path.read_bytes())
    with zipfile.ZipFile(jar) as archive:
        if set(archive.namelist())!=CLASSES or len(archive.namelist())!=9:raise ValueError('Closed productive JAR required')
    for name,path in inputs.items():
        if sha(path)!=expected[name]:raise ValueError('Input changed during compilation: '+name)
    for name,digest in pins['baselineSha256'].items():
        if sha(REPO/name)!=digest:raise ValueError('Baseline changed during compilation: '+name)
    for name,digest in pins['overlaySha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Overlay changed during compilation: '+name)
    receipt={'status':'compiled-java-overlay-only','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'androidApi':34,'productionJavaTarget':8,'classMajorVersion':52,'classCount':9,
             'jarSha256':sha(jar),'inputsSha256':{name:expected[name] for name in inputs},
             'baselineSha256':pins['baselineSha256'],'sourcesSha256':pins['overlaySha256'],
             'classesSha256':{path.relative_to(classes).as_posix():sha(path) for path in files},
             'sourcePinsSha256':sha(ROOT/'SOURCE-PINS.json'),'recipeSha256':sha(Path(__file__)),
             'testsOrFixturesPackaged':False,'sdkOrDependenciesPackaged':False,
             'apkBuilt':False,'dexBuilt':False,'installed':False,'productionAccess':False}
    (a.out/'compile-production.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'classCount':9,'jarSha256':receipt['jarSha256'],'javaTarget':8,'apkBuilt':False}))

if __name__=='__main__':main()
