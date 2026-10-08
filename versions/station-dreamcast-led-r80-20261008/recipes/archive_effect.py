"""Keep the requested unused effect as one self-contained archive in the project backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile

ROOT=Path(__file__).resolve().parent.parent
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
WORK=Path(r'E:\ESTUDO APK\work\station-dreamcast-led-r80-20261008')
OUTPUT=BACKUP/'effects/Dreamcast-LED-estilo-TURBORAMA-R80.zip'
NATIVE_SHA='bfd8601f1c44e80dac0f30c345ab02c40a4f971e3ce206eb98b12afc117e1f3e'

RESTORE_SCRIPT=r'''from pathlib import Path
import argparse,hashlib,json,os,subprocess
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
root=Path(__file__).resolve().parent
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
manifest=json.loads((root/'MANIFEST.json').read_text('utf8'))
for name,data in manifest['files'].items():assert sha(root/name)==data['sha256'],name
c=json.loads((root/'BUILD.json').read_text('utf8'))
assert sha(Path(c['command'][0]))==c['compilerSHA256'],'Compiler differs'
assert a.output.is_absolute() and a.output.drive.upper()=='E:' and not a.output.exists()
a.output.parent.mkdir(parents=True,exist_ok=True)
temp=a.output.parent/'dreamcast-effect-temp';temp.mkdir(exist_ok=True)
command=[v.replace('{ARCHIVE}',str(root)).replace('{OUTPUT}',str(a.output)) for v in c['command']]
r=subprocess.run(command,env=dict(os.environ,TEMP=str(temp),TMP=str(temp)),capture_output=True)
(a.output.parent/'dreamcast-effect-build.log').write_bytes(r.stdout+r.stderr)
assert r.returncode==0,'Compile failed; see log'
assert sha(a.output)==c['expectedSHA256'],'Compiled bytes differ'
print('Effect reproduced; no APK or phone changed.')
'''

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    assert OUTPUT.resolve().is_relative_to(BACKUP.resolve()) and not OUTPUT.exists()
    compiled=WORK/'libturbo_carousel-dreamcast.so'
    assert sha(compiled)==NATIVE_SHA
    preview=json.loads((ROOT/'evidence/animated-preview.json').read_text('utf8'))
    # Explicit private preview from the verified run, never a file selected by date.
    animation=WORK/'visual-tests/preview-20261008-153612/sonic-adventure-2-dreamcast-led.webp'
    assert animation.is_file() and preview['passed']
    reference=Path(r'G:\TURBORAMA\RetroBat\roms\dreamcast\media\images\Sonic Adventure 2 (Europe) (En,Ja,Fr,De,Es).png')
    records={}
    def register(name,path):
        assert name not in records
        records[name]={'path':Path(path),'sha256':sha(path),'bytes':Path(path).stat().st_size}
    for path in sorted((WORK/'carousel-inputs').rglob('*')):
        if path.is_file():register('carousel-inputs/'+path.relative_to(WORK/'carousel-inputs').as_posix(),path)
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix in ('.py','.h','.glsl','.json','.md'):
            register('source/'+path.relative_to(ROOT).as_posix(),path)
    register('compiled/libturbo_carousel.so',compiled)
    register('preview/sonic-adventure-2-led.webp',animation)
    register('reference/white-dreamcast-frame.png',reference)
    config=json.loads((BACKUP/'test-up-to-4-players-r79/carousel-command.json').read_text('utf8'))
    config['command']=[v.replace('{BACKUP}/test-up-to-4-players-r79/carousel-inputs','{ARCHIVE}/carousel-inputs') for v in config['command']]
    config['expectedSHA256']=NATIVE_SHA
    readme='''# Backup do efeito LED Dreamcast — uso futuro

Guardado por pedido do mantenedor em 08/10/2026. Esta moldura branca TURBORAMA
não é a capa atualmente usada no app. Não aplicar automaticamente nem instalar
a biblioteca isolada em um APK diferente. Confirmar arte e base ao retomar.

Inclui fontes, dependências completas do carrossel, compilado ARM64, testes,
recibos, uma arte de referência e prévia animada real. Não contém APK ou licença.
Os perfis aprovados anteriores e o movimento SNES foram preservados nos testes
do PC; não houve conferência física deste efeito no Android.

Para reproduzir a biblioteca: extrair este ZIP em uma pasta de trabalho em E:
e executar BUILD.py --output E:/caminho/novo/libturbo_carousel.so com Python.
O NDK r28c original deve permanecer instalado no caminho indicado em BUILD.json.
MANIFEST.json confere cada arquivo; a reprodução exige a mesma biblioteca final.
Isso somente compila o efeito e não empacota/instala app nem altera servidor.

Arquivos de referência e prévia são privados locais e não devem ser publicados
no Git. Os dois instaladores do projeto continuam R76/R79.
'''
    extra={'BUILD.json':(json.dumps(config,indent=2)+'\n').encode(),
           'BUILD.py':RESTORE_SCRIPT.encode(),'LEIA-ME.md':readme.encode()}
    inventory={name:{k:v for k,v in record.items() if k!='path'} for name,record in records.items()}
    for name,data in extra.items():inventory[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    manifest={'status':'archived-for-future-use','integrateAutomatically':False,
              'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'compiledSHA256':NATIVE_SHA,'files':inventory}
    OUTPUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for name,record in records.items():z.write(record['path'],name)
        for name,data in extra.items():z.writestr(name,data)
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(OUTPUT) as z:
        assert set(z.namelist())==set(inventory)|{'MANIFEST.json'}
        for name,data in inventory.items():
            with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==data['sha256'],name
        assert json.loads(z.read('MANIFEST.json'))==manifest
    receipt={'archived':True,'integrateAutomatically':False,'archive':str(OUTPUT),
             'sha256':sha(OUTPUT),'bytes':OUTPUT.stat().st_size,'verifiedFiles':len(inventory),
             'nativeSHA256':NATIVE_SHA,'apkGenerated':False,'installed':False}
    (ROOT/'evidence/archive.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(receipt))
if __name__=='__main__':main()
