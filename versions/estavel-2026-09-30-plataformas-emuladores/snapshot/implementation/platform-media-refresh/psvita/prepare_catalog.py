from pathlib import Path
import json,hashlib,zipfile,subprocess,os,shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-media-refresh';V=R/'psvita';V.mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
apk=P/'TurboramaStation-Plataformas-Organizadas.apk'
with zipfile.ZipFile(apk) as z:
    original=z.read('assets/turboretro/catalog.json');catalog=json.loads(original)
    matches=[g for g in catalog if g.get('Name')=='Psvita'];assert len(matches)==1
    vita=matches[0];assert len(vita['Files'])==23 and vita['CatalogLabel']=='emulador'
    before=json.loads(json.dumps(vita))
    vita['CatalogLabel']='roms'
    new=json.dumps(catalog,ensure_ascii=False,indent=2).encode('utf-8')
    (V/'catalog-before.json').write_bytes(original);(V/'catalog-with-psvita.json').write_bytes(new)
    with zipfile.ZipFile(V/'catalog-module.apk','w') as o:
        for name in ['AndroidManifest.xml','resources.arsc']:o.writestr(name,z.read(name))
        o.writestr('classes.dex',z.read('classes8.dex'))
oldhash=hashlib.sha256(original).hexdigest();newhash=hashlib.sha256(new).hexdigest()
java=r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe'
tool=r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar'
subprocess.run([java,'-jar',tool,'d','-r','-f',str(V/'catalog-module.apk'),'-o',str(V/'catalog-decoded')],check=True)
f=V/'catalog-decoded/smali/org/emulationstation/frontend/catalog/CatalogData.smali';s=f.read_text();assert oldhash in s;f.write_text(s.replace(oldhash,newhash),encoding='utf-8')
subprocess.run([java,'-jar',tool,'b',str(V/'catalog-decoded'),'-o',str(V/'catalog-module-built.apk')],check=True)
with zipfile.ZipFile(V/'catalog-module-built.apk') as z:(V/'classes8.dex').write_bytes(z.read('classes.dex'))
record={'platform':'Psvita','games':23,'covers':sum(bool(f.get('CoverImage')) for f in vita['Files']),
        'change':{'CatalogLabel':{'before':'emulador','after':'roms'}},'files_and_access_fields_unchanged':True,
        'source_catalog_sha256':oldhash,'catalog_sha256':newhash,'video_asset':'turbo-system-videos/720-psvita.mp4',
        'engine_in_apk_before':False,'all_downloads_rar':True,'runtime_verified':False}
check=json.loads(json.dumps(vita));check['CatalogLabel']='emulador';assert check==before
(V/'catalog-change.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(__file__),V/'prepare_catalog.py')
print(json.dumps(record,ensure_ascii=False))
