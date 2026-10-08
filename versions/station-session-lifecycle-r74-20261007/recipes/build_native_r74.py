"""Build the reviewed R74 Android lifecycle delta over a verified R73 tree."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, shutil, subprocess

PIN='69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
OLD_RUNTIME='9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True)
    p.add_argument('--output',default=r'E:\R74fixed');p.add_argument('--jobs',type=int,default=4)
    p.add_argument('--delta',required=True);p.add_argument('--incremental',action='store_true');a=p.parse_args()
    out=Path(a.output);repo=Path(a.repo);delta=Path(a.delta)
    require(out.drive.upper()=='E:' and ' ' not in str(out),'E: path without spaces required')
    require(1<=a.jobs<=8,'Bounded compilation jobs required')
    source=out/('RetroArch-'+PIN)
    if not out.exists():
        subprocess.run([r'C:\Python314\python.exe','-X','utf8','-B',str(repo/'versions/station-recovery-handshake-r73-20261007/recipes/build_native_r73.py'),'--output',str(out),'--prepare-only'],check=True)
    require(source.is_dir(),'Missing verified prepared R73 source')
    prepared=json.loads((out/'source-receipt.json').read_text('utf8'))
    require(prepared['upstreamCommit']==PIN and prepared['frontendSHA256']=='3dea62f27a197f2f4fa7c689a0ed09bbe8840ff1e00bf74edb299a2f40d40afa','Wrong R73 reconstruction')
    receipt=json.loads((delta/'OVERLAY-MANIFEST.json').read_text('utf8'))
    require(receipt['baseRuntimeSHA256']==OLD_RUNTIME,'Wrong native baseline')
    require(receipt['files'] and all('..' not in Path(n).parts and not Path(n).is_absolute() for n in receipt['files']),'Invalid source paths')
    previous=json.loads((out/'result.json').read_text('utf8')) if a.incremental and (out/'result.json').exists() else None
    for name,values in receipt['files'].items():
        dest=source/name;overlay=delta/'source'/name
        allowed={values['beforeSHA256']}
        if previous:
            allowed.add(previous.get('sourceDelta',{}).get(name,{}).get('afterSHA256'))
            allowed.add(values['afterSHA256'])
        require(sha(dest) in allowed,'Prepared baseline differs: '+name)
        require(sha(overlay)==values['afterSHA256'],'Reviewed overlay differs: '+name)
        shutil.copyfile(overlay,dest)
    frontend=(source/'network/netplay/netplay_frontend.c').read_text('utf8')
    start=frontend.index('bool station_netplay_recovery_poll(void)\n{')
    end=frontend.index('\n}\n#endif',start)+2
    flush_sha=hashlib.sha256(frontend[start:end].encode()).hexdigest()
    require(flush_sha=='d3a42419124dda592fea217088ed4e4687bf63718f657299ac8d73ad9fa41e12','Preserve R73 handshake flush')
    ndk=Path(r'E:\TurboEdenEngine\android-ndk-r28c');jni=source/'pkg/android/phoenix-common/jni'
    require('Pkg.Revision = 28.2.13676358' in (ndk/'source.properties').read_text(),'Wrong NDK')
    env=dict(os.environ,TEMP=str(out),TMP=str(out),PYTHONDONTWRITEBYTECODE='1')
    cmd=[str(ndk/'ndk-build.cmd'),'NDK_PROJECT_PATH='+str(source/'pkg/android/phoenix-common'),
      'APP_BUILD_SCRIPT='+str(jni/'Android.mk'),'NDK_APPLICATION_MK='+str(jni/'Application.mk'),
      'NDK_OUT='+str(out/'obj'),'NDK_LIBS_OUT='+str(out/'lib'),'APP_ABI=arm64-v8a','TARGET_ABIS=arm64-v8a',
      'APP_PLATFORM=android-26','NDK_NO_GL_HEADER_VER=26','APP_CPPFLAGS=-std=c++17',
      'APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true','HAVE_VULKAN=0','HAVE_CHEEVOS=0','HAVE_SAF=0','GIT_VERSION=','-j'+str(a.jobs)]
    print('Compiling R74 lifecycle and input recovery runtime',flush=True)
    with (out/'build.log').open('w',encoding='utf8') as f:r=subprocess.run(cmd,cwd=jni,env=env,stdout=f,stderr=subprocess.STDOUT)
    require(r.returncode==0,'Native compile failed; inspect build.log')
    final=out/'libstation_retroarch.so';shutil.copyfile(out/'lib/arm64-v8a/libretroarch-activity.so',final)
    tool=ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin'
    headers=subprocess.check_output([str(tool/'llvm-readelf.exe'),'-h','-l',str(final)],text=True)
    symbols=subprocess.check_output([str(tool/'llvm-nm.exe'),'--defined-only','--dynamic',str(final)],text=True)
    (out/'elf-headers.txt').write_text(headers,'utf8');(out/'elf-exports.txt').write_text(symbols,'utf8')
    alignment=[int(l.split()[-1],16) for l in headers.splitlines() if l.strip().startswith('LOAD ')]
    exports=['ANativeActivity_onCreate']+['Java_org_emulationstation_frontend_netplay_StationRetroActivity_'+n for n in receipt['jniMethods']]
    require('AArch64' in headers and min(alignment)>=16384,'Invalid ELF ABI/alignment')
    require(all(re.search(r'\b'+n+r'\b',symbols) for n in exports),'Missing JNI export')
    require(all(sha(source/n)==v['afterSHA256'] for n,v in receipt['files'].items()),'Source changed during compile')
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compiled=True,
      baseRuntimeSHA256=OLD_RUNTIME,runtimeSHA256=sha(final),runtimeBytes=final.stat().st_size,runtimePath=str(final),
      sourceFolder=str(source),upstreamCommit=PIN,sourceDelta=receipt['files'],manifestSHA256=sha(delta/'OVERLAY-MANIFEST.json'),
      minimumLoadAlignment=min(alignment),exportsVerified=exports,architecture='AArch64',minAPI=26,
      command=cmd,recipeSHA256=sha(__file__),buildLogSHA256=sha(out/'build.log'),
      recoveryProtocol='station-stream.v2',r73HandshakePreserved=True,handshakeFunctionSHA256=flush_sha,serverRegistryAdditionsRequired=True,
      serverDeployed=False,apkBuilt=False,installed=False,androidExecuted=False)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps({k:report[k] for k in ('compiled','runtimeSHA256','runtimeBytes','minimumLoadAlignment')},indent=2))
if __name__=='__main__':main()
