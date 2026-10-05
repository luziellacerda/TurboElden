"""Build an isolated collection-video overlay after receiving the final R21 receipt."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, zipfile

parser=argparse.ArgumentParser()
parser.add_argument('--catalog-folders',required=True,help='Sanitized real Neo Geo folder evidence JSON')
parser.add_argument('--prepare-only',action='store_true',help='Prepare and test only the two new headers; do not use the R21 overlay or build Android')
parser.add_argument('--base-native')
parser.add_argument('--base-receipt')
parser.add_argument('--base-apk',help='Current path if the receipt APK was archived')
args=parser.parse_args()
W=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005'); N=W/'native'
B=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
if not args.prepare_only:
    assert args.base_native and args.base_receipt
    source=Path(args.base_native);receipt=json.loads(Path(args.base_receipt).read_text('utf8'))
    assert source.name=='native' and (source/'station_synopsis_scroll.h').is_file()
    assert receipt.get('allPackageEntriesVerified') is True, 'Final R21 APK verification required'
assert not (W/'evidence/integration.json').exists(), 'Do not overwrite a completed overlay'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
T=W/'tests';T.mkdir(exist_ok=True)
tmp=W/'temp';tmp.mkdir(exist_ok=True);os.environ['TEMP']=os.environ['TMP']=str(tmp)
def run(name,command):
    r=subprocess.run(list(map(str,command)),capture_output=True,text=True,encoding='utf8',errors='replace')
    (T/(name+'.log')).write_text(r.stdout+r.stderr,'utf8')
    assert r.returncode==0,(name,(r.stdout+r.stderr)[-2000:])
    return r.stdout.strip()

# Evidence contains only platform, catalog revision, folder names and counts.
evidence=json.loads(Path(args.catalog_folders).read_text('utf8'))
assert evidence['source'] in ('device-signed-catalog-cache','server-published-catalog-tsv')
actual={row['folderPath'] for row in evidence['folders']}
bindings=[('fatalfury','4 - FATAL FURY COLEÇÃO'),('metalslug','1 - METAL SLUG COLEÇÃO'),('samuraishodown','2 - SAMURAI SHODOWN COLEÇÃO')]
confirmed=[]
for key, label in bindings:
    paths=[p for p in actual if p.rsplit('/',1)[-1].strip(' #')==label]
    assert paths, ('No confirmed collection path',label,sorted(actual))
    confirmed.append({'key':key,'name':label,'folderPaths':paths})

if not args.prepare_only:
    originals={p.name:sha(p) for p in source.iterdir() if p.is_file()}
    native_receipt=json.loads((source.parent/'evidence/native-build.json').read_text('utf8'))
    assert originals==native_receipt['overlaySources'], 'R21 sources differ from its final build receipt'
    base_apk=Path(args.base_apk or receipt['apk'])
    assert sha(base_apk)==receipt['sha256']
    with zipfile.ZipFile(base_apk) as z, z.open('lib/arm64-v8a/libturbo_carousel.so') as f:
        assert hashlib.file_digest(f,'sha256').hexdigest()==native_receipt['soSHA256']
    for p in source.iterdir():
        if p.is_file():shutil.copyfile(p,N/p.name)
header=(B/'collection_video_policy.h').read_text('utf8')
assert 'collectionVideoFamily' not in header
header=header.replace('float aspect;};','float aspect;int family=0;};')
anchor='\n};\nstatic bool collectionVideoEqual'
assert header.count(anchor)==1
new_entries=''.join(',\n {"'+row['name']+'","turbo-system-videos/720-collection-neogeo-'+row['key']+'.mp4",1.f,1}' for row in confirmed)
header=header.replace(anchor,new_entries+anchor)
old=' if(!collectionVideoEqual(platform,"Super Nintendo")&&!collectionVideoEqual(platform,"Super Nintendo - BR")&&!collectionVideoEqual(platform,"snes")&&!collectionVideoEqual(platform,"snesbr"))return nullptr;'
assert header.count(old)==1
header=header.replace(old,''' int family=-1;
 if(collectionVideoEqual(platform,"Super Nintendo")||collectionVideoEqual(platform,"Super Nintendo - BR")||collectionVideoEqual(platform,"snes")||collectionVideoEqual(platform,"snesbr"))family=0;
 if(collectionVideoEqual(platform,"Neo Geo")||collectionVideoEqual(platform,"neogeo")||collectionVideoEqual(platform,"neo-geo"))family=1;
 if(family<0)return nullptr;''')
header=header.replace('for(const auto&v:collectionVideoDefinitions){','for(const auto&v:collectionVideoDefinitions){if(v.family!=family)continue;')
(N/'collection_video_policy.h').write_text(header,'utf8',newline='\n')
media=json.loads((W/'media-manifest.json').read_text('utf8'))
header=(B/'video720_posters.h').read_text('utf8')
assert 'station_neogeo_collection_' not in header
decl='\n'.join('extern const unsigned char '+r['symbol']+'[];' for r in media['videos'])
entries='\n'.join('{"'+r['asset'].removeprefix('assets/')+'",'+r['symbol']+'},' for r in media['videos'])
header=header.replace('extern "C" {','extern "C" {\n'+decl)
header=header.replace('static const Video720Poster video720Posters[]={','static const Video720Poster video720Posters[]={\n'+entries)
(N/'video720_posters.h').write_text(header,'utf8',newline='\n')
shutil.copyfile(Path(__file__).parent/'test_neogeo_collection_videos_r22.cpp',T/'routing.cpp')
cc=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
run('routes-compile',[cc,'-std=c++17','-Wall','-Wextra','-I',N,T/'routing.cpp','-o',T/'routing.exe'])
routes=run('routes',[T/'routing.exe']);print(routes,flush=True)
if args.prepare_only:
    (W/'evidence/routing-prepared.json').write_text(json.dumps({'routes':routes,'bindings':confirmed,'catalogEvidence':evidence,'androidBuilt':False},indent=2)+'\n','utf8')
    sys.exit(0)
ndk=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe')
command=[ndk,'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so','-I',B,N/'native_carousel.cpp',B/'video720_posters.o',W/'neogeo_previews.o','-L',B,'-lc','-ldl','-llog','-o',W/'libturbo_carousel.so']
run('android-build',command)
for name,digest in originals.items():assert sha(N/name)==digest, ('R21 overlay changed',name)
record={'baseReceipt':str(Path(args.base_receipt)),'baseApk':receipt['apk'],'baseSha256':receipt['sha256'],
 'baseNative':str(source),'baseNativeFiles':originals,'bindings':confirmed,'catalogEvidence':evidence,
 'newHeaders':['collection_video_policy.h','video720_posters.h'],'routes':routes,'command':list(map(str,command)),
 'soSHA256':sha(W/'libturbo_carousel.so'),'soBytes':(W/'libturbo_carousel.so').stat().st_size,
 'existingOverlayFilesUnchanged':True,'videoPolicyUnchanged':True,'onlyFocusedPlays':True}
(W/'evidence/integration.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
print(json.dumps({'nativeSha256':record['soSHA256'],'routes':routes}))
