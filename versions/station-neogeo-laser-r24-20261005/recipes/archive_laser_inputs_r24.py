"""Archive only released compilation outputs, verifying copies before removing duplicates."""
from pathlib import Path
import hashlib,json,shutil
W=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005')
B=Path(r'E:\ESTUDO APK\work\station-game-details-r23-20261005')
G=Path(r'G:\BAKUP SISTEMA APP 03-10-2026')
record=W/'evidence/compiled-output-archives.json';prior=json.loads(record.read_text('utf8')) if record.exists() else []
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
entries=[(B/'TurboStations-Jogadores-Estrelas-R23-20261005.apk',G/'apks-candidatos-visuais/TurboStations-Jogadores-Estrelas-R23-20261005.apk','58c61a4d1e74396ffbefb2c5b6108e1c78a951164080a3b0f32de696330233e8'),
 (B/'libturbo_carousel.so',G/'binarios-compilados/station-game-details-r23b-20261005/libturbo_carousel.so','48eda90ac617b1dbd318f8932883386466d5f3cc8cb10ec6586a4b499d953fab')]
history=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\native-build\libturbo_carousel.so')
if history.exists():
    # Historical R16 compiled output; current compiler uses frontend-native/ dependencies.
    entries.append((history,G/'binarios-compilados/station-download-performance-20261005/native-build/libturbo_carousel.so',sha(history)))
if (W/'evidence/native-build.json').exists():
    r=json.loads((W/'evidence/native-build.json').read_text('utf8'))
    entries.append((W/'libturbo_carousel.so',G/'binarios-compilados/station-neogeo-laser-r24-20261005/libturbo_carousel.so',r['soSHA256']))
for src,dst,digest in entries:
    assert (src.resolve().parent in (W.resolve(),B.resolve()) or src.resolve()==history.resolve()) and dst.resolve().is_relative_to(G.resolve())
    if not src.exists():
        assert dst.exists() and sha(dst)==digest
        continue
    assert sha(src)==digest
    dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(src,dst)
    assert sha(dst)==digest and dst.stat().st_size==src.stat().st_size
    prior.append({'source':str(src),'archive':str(dst),'sha256':digest,'bytes':src.stat().st_size,'verifiedBeforeRemovingDuplicate':True})
    record.write_text(json.dumps(prior,indent=2)+'\n','utf8')
    src.unlink()
print(json.dumps({'archives':prior,'freeE':shutil.disk_usage(W).free}),flush=True)
