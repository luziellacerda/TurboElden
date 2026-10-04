from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile

BASE=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
ROOT=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
APK=BASE/'TurboStations-Capas4-Sinopses-LED-Netplay-R4-20261003.apk'
sha=lambda p:hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
assert sha(APK)=='17e9b87bf268c2349874d1767d5ab315862eb09fb2705f9b79a7e307c0c63c77'
ROOT.mkdir(exist_ok=True)
for part in ('native','evidence','video/java/org/emulationstation/frontend','tests','upstream','server'):
    (ROOT/part).mkdir(parents=True,exist_ok=True)
for p in (BASE/'native').iterdir():
    if p.is_file() and p.suffix in ('.h','.cpp','.so','.glsl'):
        target=ROOT/'native'/p.name
        if not target.exists():shutil.copy2(p,target)
video=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\system-videos')
for name in ('SystemCardVideo720.java','MenuRetroMusic.java'):
    target=ROOT/'video/java/org/emulationstation/frontend'/name
    if not target.exists():shutil.copy2(video/'java/org/emulationstation/frontend'/name,target)
# Preserve the previous candidate before freeing the exact duplicate from E:.
old=BASE/'TurboStations-Capas4-Sinopses-LED-Netplay-R2-20261003.apk'
if old.exists():
    archive=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais')/old.name
    archive.parent.mkdir(parents=True,exist_ok=True)
    digest=sha(old)
    assert digest=='31ab80ef2c77e9c5dff294d6f63807ab1e6d6cded81c2beec7aee171067f46d8'
    if not archive.exists():shutil.copy2(old,archive)
    assert sha(archive)==digest
    (ROOT/'evidence/r2-archive.json').write_text(json.dumps({'source':str(old),'archive':str(archive),'sha256':digest},indent=2)+'\n')
    old.unlink()
(ROOT/'evidence/base.json').write_text(json.dumps({'apk':str(APK),'sha256':sha(APK),'scope':'R5 video navigation, SNES purple; netplay separate work in progress','installed':False},indent=2)+'\n')
print(ROOT)
print('E free',shutil.disk_usage(ROOT).free)
