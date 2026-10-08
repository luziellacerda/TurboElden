"""Prepare the pinned Mercury archive in the R77 work area without altering the base."""
from pathlib import Path, PurePosixPath
import hashlib,json,subprocess,zipfile
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008\snes')
ARCHIVE=Path(r'E:\ESTUDO APK\work\station-netplay-20261004\upstream\libretro--bsnes-mercury-79d7f9de218b.zip')
ARCHIVE_SHA='c7392855556c20c164d1a9793a23664fddfaee369939cd24bb21e59d861ec428'
PATCH_SHA='69f07c900cab4e4562257bc1e9954e9b358444f24156228405164abbd982c934'
WRAPPER='target-libretro/libretro.cpp'
ORIGINAL_SHA='90bfb5826f9e2e85a05d11137eeeebdbc05359b7eba3632d4296e87c5dae007a'
PATCHED_SHA='e0d95df5f51a215457a9dc693d1797450e1e41179b96229b04c738a0277fa3c7'
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    patch=HERE/'multitap-input.patch';assert sha(patch.read_bytes())==PATCH_SHA
    assert sha(ARCHIVE.read_bytes())==ARCHIVE_SHA
    source=WORK/'source';source.mkdir(parents=True,exist_ok=True)
    files={}
    with zipfile.ZipFile(ARCHIVE) as archive:
        roots={PurePosixPath(i.filename).parts[0] for i in archive.infolist()};assert len(roots)==1
        for item in archive.infolist():
            if item.is_dir():continue
            parts=PurePosixPath(item.filename).parts[1:]
            assert parts and all(p not in ('..','.') and ':' not in p for p in parts)
            rel=PurePosixPath(*parts).as_posix();dest=source.joinpath(*parts)
            assert dest.resolve().is_relative_to(source.resolve())
            original=archive.read(item);files[rel]=sha(original)
            if dest.exists():
                allowed={files[rel]}
                if rel==WRAPPER:allowed.add(PATCHED_SHA)
                assert sha(dest.read_bytes()) in allowed,'unexpected local change: '+rel
            else:
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(original)
    wrapper=source/WRAPPER
    if sha(wrapper.read_bytes())==ORIGINAL_SHA:
        subprocess.run(['git','apply','--check','--no-index',str(patch)],cwd=source,check=True)
        subprocess.run(['git','apply','--no-index',str(patch)],cwd=source,check=True)
    assert sha(wrapper.read_bytes())==PATCHED_SHA
    changed=[r for r,s in files.items() if sha((source/r).read_bytes())!=s]
    assert changed==[WRAPPER],changed
    result={'utc':datetime.now(timezone.utc).isoformat(),'upstreamCommit':'79d7f9de218b6ffa65a80bbdc5828532bc239232',
      'upstreamUrl':'https://github.com/libretro/bsnes-mercury/archive/79d7f9de218b6ffa65a80bbdc5828532bc239232.zip',
      'archiveSHA256':ARCHIVE_SHA,'patchSHA256':PATCH_SHA,'baselineWrapperSHA256':ORIGINAL_SHA,
      'patchedWrapperSHA256':PATCHED_SHA,'archiveFilesVerified':len(files),'changedSourceFiles':changed,
      'recipeSHA256':sha(Path(__file__).read_bytes()),'originalSourceModified':False}
    (WORK/'source-receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))

if __name__=='__main__':main()
