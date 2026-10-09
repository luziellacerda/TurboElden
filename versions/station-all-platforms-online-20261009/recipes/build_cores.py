"""Rebuild the four delivered ARM64 cores from pinned corresponding sources.

Use NDK r28c and a fresh private work directory. Android runtime stays identical
to the complete five-player base. No APK installation or server change occurs.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, shutil, subprocess, tarfile

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def apply_patch(source,patch):
    lines=patch.read_text().splitlines(keepends=True);start=2
    file=source/lines[1].split(' b/',1)[1].strip();original=file.read_text();parts=[];cursor=0
    while start<len(lines):
        if not lines[start].startswith('@@ '):raise ValueError('Unsupported source patch')
        start+=1;old=[];new=[]
        while start<len(lines) and not lines[start].startswith('@@ '):
            line=lines[start];start+=1
            if line[0] in ' -':old.append(line[1:])
            if line[0] in ' +':new.append(line[1:])
        before=''.join(old);after=''.join(new);position=original.find(before,cursor)
        if position<cursor or original.find(before,position+1)!=-1:raise ValueError('Source patch context differs or is ambiguous')
        parts.append(original[cursor:position]);parts.append(after);cursor=position+len(before)
    parts.append(original[cursor:]);file.write_text(''.join(parts))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ndk',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--jobs',type=int,default=4)
    args=p.parse_args()
    if not 1<=args.jobs<=8:raise ValueError('Use 1 to 8 build jobs')
    if 'Pkg.Revision = 28.2.13676358' not in (args.ndk/'source.properties').read_text():raise ValueError('Pinned NDK r28c required')
    args.work.mkdir(mode=0o700,exist_ok=False);receipts=[]
    spec=json.loads((ROOT/'evidence/core-builds.json').read_text())
    for core in spec['cores']:
        archive=ROOT/core['sourceArchive']
        if sha(archive)!=core['sourceArchiveSHA256']:raise ValueError('Source archive drift')
        work=args.work/core['name'];work.mkdir();source=work/'source';source.mkdir()
        with tarfile.open(archive) as tar:tar.extractall(source,filter='data')
        source=next(source.iterdir())
        for patch in core.get('patches',[]):
            file=ROOT/patch['path']
            if sha(file)!=patch['sha256']:raise ValueError('Source patch drift')
            apply_patch(source,file)
        jni=source/('src/burner/libretro/jni' if core['name']=='fbneo' else 'jni')
        binary=args.ndk/('ndk-build.cmd' if os.name=='nt' else 'ndk-build')
        command=[binary,'-j'+str(args.jobs),'NDK_PROJECT_PATH='+str(source),'APP_BUILD_SCRIPT='+str(jni/'Android.mk'),'NDK_APPLICATION_MK='+str(jni/'Application.mk'),'NDK_OUT='+str(work/'obj'),'NDK_LIBS_OUT='+str(work/'libs'),'APP_ABI=arm64-v8a','APP_PLATFORM=android-26','APP_STL=c++_static','APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true','APP_LDFLAGS=-Wl,-z,max-page-size=16384']
        if core['name']=='pcsx':command+=['USE_ASYNC_CDROM=0','USE_ASYNC_GPU=0','USE_ASYNC_SPU=0','NDRC_THREAD=0']
        with (work/'build.private.log').open('wb') as log:result=subprocess.run(list(map(str,command)),cwd=source,stdout=log,stderr=log)
        if result.returncode:raise RuntimeError('Core build failed; inspect private log: '+core['name'])
        output=work/'libs/arm64-v8a/libretro.so'
        receipt={'name':core['name'],'compiled':True,'sha256':sha(output),'deliveredSHA256':core['sha256'],'byteIdentical':sha(output)==core['sha256'],'upstreamRevision':core['commit'],'physicalGameplayQualified':False}
        receipts.append(receipt);print(json.dumps(receipt),flush=True)
    (args.work/'receipt.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cores':receipts,'apkBuilt':False},indent=2)+'\n')

if __name__=='__main__':main()
