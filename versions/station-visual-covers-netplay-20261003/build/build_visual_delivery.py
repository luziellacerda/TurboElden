"""Rebuild and package the reviewed Station visual/cover/netplay source on E:."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile
ROOT=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
BASE=Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003\TurboStations-SNES-Mega-HUD-LZGames-R2-20261003.apk')
BASE_SHA='6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b'
OUT=ROOT/'TurboStations-Capas4-Sinopses-LED-Netplay-R2-20261003.apk'
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
SIGNER='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
os.environ['TEMP']=os.environ['TMP']=str(ROOT)
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
    with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.RSA','.DSA','.EC','.SF'))
def run(args,log):
    result=subprocess.run(list(map(str,args)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (ROOT/log).write_text(result.stdout,encoding='utf-8')
    if result.returncode:raise RuntimeError(log+': '+result.stdout[-6000:])
    return result.stdout
def classes(d):
    def u(o):return struct.unpack_from('<I',d,o)[0]
    strings=[]
    for i in range(u(56)):
        o=u(u(60)+4*i)
        while d[o]&128:o+=1
        o+=1;strings.append(d[o:d.index(0,o)].decode('utf-8',errors='replace'))
    types=[strings[u(u(68)+4*i)] for i in range(u(64))]
    return [types[u(u(100)+32*i)] for i in range(u(96))]
def native():
    n=ROOT/'native'
    run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26',
       '--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot',
       '-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2',
       '-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs',
       '-Wl,-soname,libturbo_carousel.so',n/'native_carousel.cpp','-L',n,'-lc','-ldl','-llog',
       '-o',n/'libturbo_carousel.so'],'native-build.log')
    print('Native carousel rebuilt:',sha(n/'libturbo_carousel.so'))

def manifest():
    run([JDK/'java.exe','-jar',r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar',
        'b',ROOT/'manifest-project','-p',r'E:\ESTUDO APK\work\station-snes-explus-20261003\framework',
        '-o',ROOT/'manifest-module.apk'],'manifest-build.log')
    print('Manifest module rebuilt:',sha(ROOT/'manifest-module.apk'))
def package():
    assert sha(BASE)==BASE_SHA,'Wrong base'
    assert not OUT.exists(),'Preserve existing output'
    assert shutil.disk_usage(ROOT).free>2*BASE.stat().st_size+250*1024*1024,'Insufficient build space'
    replacements={
        'classes28.dex':ROOT/'station/build/dex/classes.dex',
        'lib/arm64-v8a/libstation_frontend.so':ROOT/'station/build/native/arm64-v8a/libstation_frontend.so',
        'lib/arm64-v8a/libturbo_carousel.so':ROOT/'native/libturbo_carousel.so',
    }
    with zipfile.ZipFile(ROOT/'manifest-module.apk') as z:
        manifest=ROOT/'AndroidManifest.compiled';manifest.write_bytes(z.read('AndroidManifest.xml'))
    replacements['AndroidManifest.xml']=manifest
    with zipfile.ZipFile(BASE) as z:
        old=set(z.namelist());dexes=[n for n in old if n.startswith('classes') and n.endswith('.dex')]
        highest=max(1 if n=='classes.dex' else int(n[7:-4]) for n in dexes)
    newdex='classes'+str(highest+1)+'.dex'
    additions={newdex:ROOT/'netplay/build/dex/classes.dex'}
    for p in (ROOT/'assets').rglob('*'):
        if p.is_file():additions[p.relative_to(ROOT).as_posix()]=p
    assert not old.intersection(additions),'Must preserve existing assets'
    assert set(replacements)<=old
    definitions={}
    with zipfile.ZipFile(BASE) as z:
        for n in sorted(set(dexes)|{newdex}):
            d=(replacements.get(n) or additions.get(n)).read_bytes() if n in replacements or n in additions else z.read(n)
            for c in classes(d):
                assert c not in definitions,('Duplicate DEX class',c,n,definitions.get(c))
                definitions[c]=n
        assert 'Lcom/imagine/BaseActivity;' in definitions and 'Lcom/mdimagn/BaseActivity;' in definitions
        for c in ('StationNetplayActivity','StationDolphinNetplayActivity'):
            assert definitions['Lorg/emulationstation/frontend/netplay/'+c+';']==newdex
    notice={'base':str(BASE),'baseSha256':BASE_SHA,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'expectedChanged':list(replacements),'netplayDex':newdex,'serverDeploymentModified':False,
       'nativeHudAndEnginesPreserved':True,'fixedInterCoverDelayMs':0,'coverWorkers':4,
       'installed':False,'deviceVisualVerified':False,'twoDeviceNetplayVerified':False,'promotedToStable':False,
       'supersedesUninstalledApkSha256':'62068502f2081c4ad61f33c5203bcf87dcfcf724be18f8e6bb308478366bac9f',
       'serverHandoffCommit':'54bba11c52f35695fd47eabc7145f42af9990426'}
    (ROOT/'BUILD-NOTICE.json').write_text(json.dumps(notice,indent=2)+'\n')
    additions['assets/station-visual-covers/BUILD-NOTICE.json']=ROOT/'BUILD-NOTICE.json'
    unsigned=ROOT/'unsigned.apk';aligned=ROOT/'aligned.apk'
    assert not unsigned.exists() and not aligned.exists(),'Review previous temporary output first'
    with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(unsigned,'w',allowZip64=True) as b:
        for info in a.infolist():
            n=info.filename
            if signature(n):continue
            oi=copy.copy(info);oi.extra=b''
            if n in replacements:b.writestr(oi,replacements[n].read_bytes())
            else:
                with a.open(info) as src,b.open(oi,'w') as dst:shutil.copyfileobj(src,dst,1024*1024)
        for n,p in additions.items():b.write(p,n,compress_type=zipfile.ZIP_STORED if n.endswith('.dex') else zipfile.ZIP_DEFLATED)
    run([BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned],'zipalign-build.log')
    unsigned.unlink() # Exact disposable output produced above; no directory deletion.
    run([JDK/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false',
        '--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android',
        '--out',OUT,aligned],'sign-build.log')
    assert SIGNER in run([JDK/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',OUT],'signature-check.log')
    run([BT/'zipalign.exe','-c','-P','16','4',OUT],'alignment-check.log')
    preserved=0;changed=[]
    with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
        prior={n for n in a.namelist() if not signature(n)};after={n for n in b.namelist() if not signature(n)}
        assert len(b.namelist())==len(set(b.namelist()))
        assert prior<=after and after-prior==set(additions)
        for n in sorted(prior):
            oldhash,newhash=zsha(a,n),zsha(b,n)
            if oldhash!=newhash:
                assert n in replacements,('Unplanned changed entry',n)
                assert sha(replacements[n])==newhash;changed.append(n)
            else:preserved+=1
        assert set(changed)==set(replacements)
        for n,p in additions.items():assert zsha(b,n)==sha(p)
    aligned.unlink()
    report={**notice,'apk':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,'changed':changed,'added':sorted(additions),
        'preservedEntries':preserved,'wholeZipPayloadGate':True,'duplicateClasses':0,'classDefinitions':len(definitions)}
    (ROOT/'build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:report[k] for k in ('apk','sha256','bytes','changed','preservedEntries')},indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['native','manifest','package']);args=parser.parse_args()
    {'native':native,'manifest':manifest,'package':package}[args.action]()
