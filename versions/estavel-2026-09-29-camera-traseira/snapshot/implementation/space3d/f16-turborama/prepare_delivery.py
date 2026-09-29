"""Prepare notices and matching editable model sources for the private test APK."""
from pathlib import Path
import json,zipfile,shutil,hashlib
F=Path(__file__).resolve().parent;D=F.parent;P=D.parent;S=D/'f16-source'
shutil.copy2(S/'LICENSE',D/'LICENSE-F16.md')
(D/'AUTHORS-F16.txt').write_text((S/'copyright.txt').read_text()+'\n\n'+(S/'authors.txt').read_text(),encoding='utf-8')
(D/'NOTICE.md').write_text('''# F-16 TURBORAMA — modelo visual e materiais

Geometria original: FlightGear F-16, https://github.com/NikolaiVChr/f16, commit 0d0d3d425a9a852b9cd6a764dedee7c9c72cdf51. Copyright e autores em AUTHORS-F16.txt; licença GPL-2.0-or-later integral em LICENSE-F16.md. Os direitos dessa licença permanecem aplicáveis ao modelo visual derivado e seus materiais. A política privada Turborama não restringe esses direitos.

Adaptação em 29/09/2026: exterior em posição de voo, trem removido/portas fechadas, cabine/piloto/assento incluídos, bocal Pratt & Whitney montado com 16 pétalas reais, efeitos planos antigos removidos; escala 1/7.5. Geometria 3D real, não uma imagem girada. Não reivindicamos autoria da geometria original; não incorporamos lógica de voo ou de armamentos.

Pintura: textura grafite derivada do mapa de cor original com image_gen, refinamento PBR e marca TURBORAMA aplicada no material. A imagem conceitual aprovada foi referência visual, não uma fonte de geometria. Os sombreadores implementam iluminação aproximada para tempo real, vidro com mistura alfa, e um efeito volumétrico preso ao bocal com oclusão por distância. Não é ray tracing ou simulação física de gases.

Fontes editáveis correspondentes do recurso visual: f16-model-source.zip, junto deste aviso no APK. Inclui arquivos AC3D/texturas originais, conversor GLB, gerador do atlas, materiais derivados e shaders utilizados. Não inclui ROMs, firmware, chaves ou código privado do catálogo. Geometria/glass ordenada e atlas com 4 mapas 2048x2048, 30.508 vértices e 40.210 triângulos no renderer.

A antiga nave BabylonJS Space Pirates foi substituída. Sua licença anterior foi mantida como aviso histórico; seu modelo não entra no render ativo do F-16.
''',encoding='utf-8')
prompt='''Edit original F-16 UV atlas, keeping island positions, proportions and fine seams. Apply realistic dark graphite aerospace coating inspired by approved F-16 TURBORAMA concept, with metal grain, subtle wear and local panel variation. Do not add text or change UV layout. Preserve small auxiliary engine/cockpit texture blocks. Generated using built-in image_gen with Models/f16.png and f16-turborama-conceito-v1.png as references; output f16-graphite-albedo-v1.png. Typography/green accents are separate native PBR material operations.
'''
(F/'MATERIAL-PROMPT.md').write_text(prompt,encoding='utf-8')
sources=[S/x['path'] for x in json.loads((S/'source-manifest.json').read_text())['files']]
sources += [S/n for n in ['source-manifest.json','convert_exterior.py','inspect_ac.py','conversion-report.json','nozzle-alignment.json','README-TURBORAMA.md']]
sources += [F/n for n in ['prepare_f16.py','ac3d.py','f16-graphite-albedo-v1.png','wordmark.png','MATERIAL-PROMPT.md']]
sources += [D/n for n in ['scene-common.glsl','ship.vert','ship.frag','plume.vert','plume.frag','depth.vert','depth.frag','clouds.vert','clouds.frag','prepare_shaders.py','model-manifest.json','NOTICE.md','LICENSE-F16.md','AUTHORS-F16.txt']]
with zipfile.ZipFile(D/'f16-model-source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in dict.fromkeys(sources):
  assert f.resolve().is_relative_to(D.resolve()) and f.is_file(),f
  z.write(f,str(f.relative_to(D)).replace('\\','/'))
licenses=['LICENSE-SpacePirates.md','LICENSE-F16.md','AUTHORS-F16.txt','NOTICE.md','model-manifest.json','f16-model-source.zip']
(D/'license-assets.json').write_text(json.dumps(licenses,indent=2),encoding='utf-8')
def replace_once(path,a,b):
 s=path.read_text();assert s.count(a)==1,(path,a[:80]);path.write_text(s.replace(a,b),encoding='utf-8')
B=P/'build_native.py'
old="model_inputs=[p/'space3d/prepare_model.py',p/'space3d/valkyrie_mesh.glb']"
if old in B.read_text():
 replace_once(B,old,"model_inputs=[p/'space3d/f16-turborama/prepare_f16.py',p/'space3d/f16-source/f16-exterior-original.glb',p/'space3d/f16-turborama/f16-graphite-albedo-v1.png']")
 replace_once(B,"str(p/'space3d/prepare_model.py')","str(p/'space3d/f16-turborama/prepare_f16.py')")
for path in [P/'package_apk.py',P/'verify_package_integrity.py']:
 s=path.read_text();old="['LICENSE-SpacePirates.md','NOTICE.md','model-manifest.json']"
 if old in s:s=s.replace(old,"__import__('json').loads((p/'space3d/license-assets.json').read_text())")
 path.write_text(s,encoding='utf-8')
A=P/'AGENTS.md';s=A.read_text();s=s.replace('- Nave atual: native_space3d.h e space3d/. Preservar origem/licença Apache-2.0 do modelo BabylonJS/SpacePirates. A nave PNG anterior foi rejeitada e não está no render ativo. Prévia de computador não equivale a validação no Android.','- Nave atual em preparação: F-16 3D, native_space3d.h e space3d/. Preservar GPL-2.0-or-later, autores e fontes editáveis do modelo FlightGear/NikolaiVChr. Conceito PNG aprovado é referência visual, não geometria. Prévia no PC não equivale a teste no Android; consultar handoff/build para saber qual APK foi instalado. Licença da antiga nave SpacePirates mantida como histórico.')
A.write_text(s,encoding='utf-8')
r=json.loads((F/'asset-manifest.json').read_text());r['user_visual_approval']=True;r['approval_scope']='Raster concept; user requested actual 3D integration next';(F/'asset-manifest.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('F16 source archive:',(D/'f16-model-source.zip').stat().st_size,'bytes; notices/build/package updated.')
