"""Derive the Dreamcast-only visual change from the explicit frozen R79 channel."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent.parent
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
BASE=BACKUP/'test-up-to-4-players-r79/carousel-inputs/d0'
WORK=Path(r'E:\ESTUDO APK\work\station-dreamcast-led-r80-20261008')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def change(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)

def main():
    source=(BASE/'premium-magazine-led-android.glsl').read_text('utf8')
    source=change(source,'float neoRegion(vec2 p);','float dreamcastRegion(vec2 p);\nfloat neoRegion(vec2 p);')
    source=change(source,'float region(vec2 p) {','float region(vec2 p) {\n    if(activeMagazineModel>3.5) return dreamcastRegion(p);')
    # Dreamcast shares the chromatic emitter recovery used by Neo Geo.
    # Its own entry point below avoids every N64/NeoGeo geometry/color decision.
    anchor='void main() {\n    vec4 base=TEX(u_tex,uv);'
    source=change(source,anchor,(ROOT/'native/dreamcast_led.glsl').read_text('utf8')+'\n'+anchor)
    source=change(source,'    vec2 p=vec2(uv.x,1.0-uv.y)*vec2(1024,1536);',
        '    vec2 p=vec2(uv.x,1.0-uv.y)*vec2(1024,1536);\n'
        '    if(magazineModel>3.5){activeMagazineModel=4.0;FragColor=dreamcastShade(base,p)*tint;return;}')
    source=change(source,'// 2: measured Nintendo 64 frame. Models 0/1 keep their original light engine.',
        '// 2: Nintendo 64; 3: Neo Geo/CD; 4: Dreamcast. Legacy models remain unchanged.')
    native=(BASE/'native_magazine.h').read_text('utf8')
    native=change(native,' else if(neoMagazineKey(key))model=3;',
        ' else if(neoMagazineKey(key))model=3;\n'
        ' else if(presentationKeyEqual(key,"Dreamcast")) {model=4;hue=0xFF6A00FF;}')
    files={'premium-magazine-led-android.glsl':source,
           'magazine_shader.h':'static const char magazineShaderSource[]=R"DCLED('+source+')DCLED";\n',
           'native_magazine.h':native}
    for name,text in files.items():
        for dest in (ROOT/'native'/name,WORK/'carousel-inputs/d0'/name):
            dest.write_text(text,encoding='utf8',newline='\n')
    receipt={'baseChannel':'test-4p','baseVersion':'R79','targetVersion':'R80',
             'sourceBase':{name:sha(BASE/name) for name in files},
             'sourceChanges':{name:sha(ROOT/'native'/name) for name in files},
             'noJavaRuntimeCoreManifestChanges':True,'menuFramePolicyChanged':False,
             'platformAndCollectionVideoEffectsAdded':False}
    (ROOT/'evidence/source-changes.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    print(json.dumps(receipt))
if __name__=='__main__':main()
