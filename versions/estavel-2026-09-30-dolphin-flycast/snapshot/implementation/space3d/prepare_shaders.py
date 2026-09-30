from pathlib import Path
P=Path(__file__).resolve().parent
common=(P/'scene-common.glsl').read_text()
parts=['// Generated F16 shaders; use prepare_shaders.py.']
for stem in ['ship','plume','depth','clouds']:
 for ext in ['vert','frag']:
  source='#version 100\nprecision highp float;\n'+common+'\n'+(P/(stem+'.'+ext)).read_text()
  parts.append('static const char* space3d_'+stem+'_'+ext+'=R"SHIP('+source+')SHIP";')
(P.parent/'space3d_shaders.h').write_text('\n'.join(parts),encoding='utf-8')
