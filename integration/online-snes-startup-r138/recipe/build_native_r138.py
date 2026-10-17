"""Build the exact installed five-player source, then the lifecycle-only overlay."""
from pathlib import Path,PurePosixPath
import argparse,datetime,hashlib,json,os,shutil,struct,subprocess,tarfile
ARCHIVE_SHA='b8f7649a5edacbe9e913d5e50f66482c0aa082fbd2237f5fd7800d00723b735a'
MANIFEST_SHA='63049a133ed0a761133f4ffc36ce642870dc699e103a5a73ab0b7683a6d90f47'
OLD_RUNTIME='81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc'
SOURCE='RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
CHANGED='frontend/drivers/platform_unix.c'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def compare_elf(old,new):
    a=Path(old).read_bytes();b=Path(new).read_bytes()
    def sections(data):
        offset=struct.unpack_from('<Q',data,40)[0];size,count,index=struct.unpack_from('<HHH',data,58)
        heads=[struct.unpack_from('<IIQQQQIIQQ',data,offset+i*size) for i in range(count)]
        strings=heads[index];names=data[strings[4]:strings[4]+strings[5]]
        return {names[h[0]:].split(b'\0',1)[0].decode():(h,data[h[4]:h[4]+h[5]]) for h in heads if h[1]!=8}
    x,y=sections(a),sections(b);need(set(x)==set(y),'Rebuilt ELF section set differs')
    ignored={'.note.gnu.build-id','.comment'}
    # Compiler comments are nonallocated provenance strings. The GNU note's
    # descriptor is an identity; neither changes machine code or loaded data.
    need(x['.comment'][0][2]&2==0 and y['.comment'][0][2]&2==0,'Compiler comment unexpectedly allocated')
    note_a=x['.note.gnu.build-id'][1];note_b=y['.note.gnu.build-id'][1]
    need(len(note_a)==len(note_b)==36 and note_a[:16]==note_b[:16],'Unexpected GNU identity note')
    for name in set(x)-ignored:
        h,c=x[name];j,d=y[name]
        # Section file offsets can move for nonallocated metadata only.
        need(c==d and h[:4]==j[:4] and h[5:]==j[5:],'Rebuilt code/data/relocation section differs: '+name)
        if h[2]&2:need(h[4]==j[4],'Loaded section offset differs: '+name)
    need(a[:40]==b[:40] and a[48:64]==b[48:64],'ELF execution header differs')
    phoff=struct.unpack_from('<Q',a,32)[0];phsize,phcount=struct.unpack_from('<HH',a,54)
    need(a[phoff:phoff+phsize*phcount]==b[phoff:phoff+phsize*phcount],'ELF loading regions differ')
    return dict(wholeFileIdentical=a==b,productiveSectionsByteIdentical=True,
                excludedMetadataSections=sorted(ignored),originalBytes=len(a),rebuiltBytes=len(b),
                sectionSha256={n:hashlib.sha256(c).hexdigest() for n,(h,c) in x.items() if n not in ignored})
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('delivery','work','ndk'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--mode',choices=['baseline','candidate'],required=True)
    p.add_argument('--overlay',type=Path)
    p.add_argument('--jobs',type=int,default=4)
    a=p.parse_args();need(1<=a.jobs<=6,'Bounded workers required')
    archive=a.delivery/'native/retroarch-corresponding-source.tar.gz'
    manifest=a.delivery/'native/CORRESPONDING-SOURCE-MANIFEST.json'
    old=a.delivery/'native/runtime/libstation_retroarch.so'
    need(sha(archive)==ARCHIVE_SHA and sha(manifest)==MANIFEST_SHA and sha(old)==OLD_RUNTIME,'Installed native source receipt mismatch')
    need('Pkg.Revision = 28.2.13676358' in (a.ndk/'source.properties').read_text(),'NDK r28c required')
    expected=json.loads(manifest.read_text('utf-8'));source=a.work/SOURCE
    if a.mode=='baseline':
        need(a.work.is_absolute() and not a.work.exists(),'Fresh absolute build directory required')
        a.work.mkdir(parents=True)
        with tarfile.open(archive) as tar:
            for m in tar.getmembers():
                n=PurePosixPath(m.name)
                need(not n.is_absolute() and '..' not in n.parts and n.parts[0]==SOURCE and (m.isfile() or m.isdir()),'Unsafe archive entry')
            tar.extractall(a.work,filter='data')
    actual={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*') if p.is_file()}
    need(actual==expected,'Native source drift before compile')
    if a.mode=='candidate':
        need(a.overlay and a.overlay.is_file(),'Lifecycle overlay required')
        receipt=json.loads((a.work/'baseline.json').read_text('utf-8'))
        need(receipt['comparison']['productiveSectionsByteIdentical'],'Installed baseline reconstruction required')
        need(sha(a.work/'baseline.so')==receipt['runtimeSha256'],'Baseline output changed')
        shutil.copyfile(a.overlay,source/CHANGED)
    after={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*') if p.is_file()}
    changes=[n for n in expected if expected[n]!=after.get(n)]
    need(set(after)==set(expected) and changes==([CHANGED] if a.mode=='candidate' else []),'Source change outside requested lifecycle')
    jni=source/'pkg/android/phoenix-common/jni'
    cmd=[str(a.ndk/'ndk-build.cmd'),'NDK_PROJECT_PATH='+str(source/'pkg/android/phoenix-common'),
         'APP_BUILD_SCRIPT='+str(jni/'Android.mk'),'NDK_APPLICATION_MK='+str(jni/'Application.mk'),
         'NDK_OUT='+str(a.work/'obj'),'NDK_LIBS_OUT='+str(a.work/'lib'),
         'APP_ABI=arm64-v8a','TARGET_ABIS=arm64-v8a','APP_PLATFORM=android-26',
         'NDK_NO_GL_HEADER_VER=26','APP_CPPFLAGS=-std=c++17','APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true',
         'HAVE_VULKAN=0','HAVE_CHEEVOS=0','HAVE_SAF=0','GIT_VERSION=','-j'+str(a.jobs)]
    log=a.work/(a.mode+'.log')
    env={**os.environ,'SOURCE_DATE_EPOCH':'1791504000','PYTHONDONTWRITEBYTECODE':'1'}
    print('Building '+a.mode,flush=True)
    with log.open('wb') as f:r=subprocess.run(cmd,cwd=jni,env=env,stdout=f,stderr=subprocess.STDOUT)
    need(r.returncode==0,'Native compilation failed; inspect local log')
    binary=a.work/'lib/arm64-v8a/libretroarch-activity.so';final=a.work/(a.mode+'.so');shutil.copyfile(binary,final)
    data=final.read_bytes();need(data[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',data,18)[0]==183,'ARM64 ELF required')
    offset=struct.unpack_from('<Q',data,32)[0];size,count=struct.unpack_from('<HH',data,54)
    loads=[struct.unpack_from('<IIQQQQQQ',data,offset+i*size) for i in range(count)]
    alignment=min(h[7] for h in loads if h[0]==1);need(alignment>=16384,'ELF 16K alignment required')
    tools=a.ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin'
    symbols=subprocess.check_output([str(tools/'llvm-nm.exe'),'--defined-only','--dynamic',str(final)],text=True)
    exports=['stationRequestQuit','stationRecoveryStatus','stationMultiplayerConfigure','stationMultiplayerBind','stationMultiplayerUnbind']
    need(all('Java_org_emulationstation_frontend_netplay_StationRetroActivity_'+s in symbols for s in exports),'Native interface changed')
    need('STATION_MULTIPLAYER_MAX_PLAYERS 5U' in (source/'frontend/drivers/station_multiplayer.h').read_text(),'Five-player support must be preserved')
    report=dict(revision='R138',mode=a.mode,compiled=True,sourceArchiveSha256=ARCHIVE_SHA,sourceManifestSha256=MANIFEST_SHA,
                sourceFiles=len(expected),changedSourceFiles=changes,runtimeSha256=sha(final),runtimeBytes=final.stat().st_size,
                baseRuntimeSha256=OLD_RUNTIME,minimumLoadAlignment=alignment,maximumPlayers=5,
                sourceDateEpoch='1791504000',buildLogSha256=sha(log),recipeSha256=sha(__file__),
                utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),apkBuilt=False,installed=False,gameplayValidated=False)
    if a.mode=='baseline':report['comparison']=compare_elf(old,final)
    else:report['overlaySha256']=sha(a.overlay)
    (a.work/(a.mode+'.json')).write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report),flush=True)
if __name__=='__main__':main()
