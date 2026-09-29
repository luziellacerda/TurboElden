from pathlib import Path
import json,re,xml.etree.ElementTree as ET
p=Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
t=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx')
source=(t/'_theme_inc/premium-selection-laser.glsl').read_text(encoding='utf-8-sig')
(p/'premium-selection-laser.glsl').write_bytes((t/'_theme_inc/premium-selection-laser.glsl').read_bytes())
(p/'premium-selection-glow.svg').write_bytes((t/'_theme_inc/images/premium-selection-glow.svg').read_bytes())
# Keep the supplied phase/head/tail/color equations, replacing the desktop SVG sample
# with a transparent, rounded, pixel-sized outline matching the current native card.
mobile=source.replace('uniform sampler2D u_tex;', 'uniform vec2 canvasSize;\nuniform vec4 coverRect;\nuniform float coverRadius;')
mobile=mobile.replace('    vec4 border = SAMPLE(u_tex, v_tex);', '''    vec2 local=vec2(v_tex.x,1.0-v_tex.y)*canvasSize;
    vec2 halfSize=coverRect.zw*0.5;
    vec2 delta=abs(local-coverRect.xy-halfSize)-(halfSize-vec2(coverRadius));
    float sd=length(max(delta,vec2(0.0)))+min(max(delta.x,delta.y),0.0)-coverRadius;
    float edge=abs(sd);
    float stroke=1.0-smoothstep(1.1,2.5,edge);
    float glow=exp(-edge/7.0)*0.65;
    // Leave the cover interior clear; only the thin outline and outward glow are painted.
    vec4 border=vec4(1.0,1.0,1.0,max(stroke,glow)*smoothstep(-1.5,-0.25,sd));''')
mobile=mobile.replace('vec2 p = vec2(v_tex.x, 1.0-v_tex.y)*vec2(400.0,300.0)-vec2(14.0);','vec2 p = (local-coverRect.xy)/coverRect.zw*vec2(372.0,272.0);')
mobile=mobile.replace('headDistance/0.007','headDistance/0.014').replace('behind/0.100','behind/0.160').replace('0.18+2.2*tail+3.0*head','0.32+2.6*tail+4.0*head').replace('mix(hue,core,head)','mix(hue,core,min(1.0,head+0.20*tail))')
(p/'premium-selection-laser-android.glsl').write_text(mobile,encoding='utf-8')
rows=json.loads((p/'theme-infos-mapping.json').read_text(encoding='utf-8'))
sega={'mastersystem','megadrive','megadrivebr','genesis','megadrive-msu','gamegear','dreamcast','sega32x','segacd','saturn','naomi','atomiswave'}
configs=[]
for r in rows:
 folder=r['folder'];key=r['key'];alias={'Super Nintendo - BR':'snesbr','MegaDrive - BR':'megadrivebr','Playstation 2 - BR':'ps2br','Nintendo 64 - BR':'n64br'}.get(key,folder)
 file=t/'_theme_views/gamecarousel-systems'/f'{alias}.xml';v={}
 if file.exists():
  for group in ET.parse(file).getroot().findall('variables'):
   if not group.get('if'):
    for e in group:
     if e.text and not e.get('if'):v[e.tag]=e.text.strip()
 color=v.get('gc-laser-color');core=v.get('gc-laser-core');origin='gc-laser-color'
 if not color:
  if folder in sega:color='186CFFFF';core='E6F1FFFF';origin='general.xml: Sega rule'
  elif re.fullmatch('[0-9a-fA-F]{8}',v.get('gc-accent-b','')):color=v['gc-accent-b'];origin='system gc-accent-b'
  else:color='FF0911FF';core='FFE6EBFF';origin='general.xml: default'
 if not core:
  rgb=[int(color[i:i+2],16) for i in (0,2,4)];core=''.join(f'{round(x*.10+255*.90):02X}' for x in rgb)+'FF'
 configs.append({'key':key,'folder':folder,'theme_file':str(file) if file.exists() else 'general.xml','color':color,'core':core,'source':origin,'pos':[.053763441,-.031617647],'size':[.892473118,1.063235294]})
(p/'laser-system-colors.json').write_text(json.dumps(configs,ensure_ascii=False,indent=2),encoding='utf-8')
header='static const char laserShaderSource[]=R"LASER('+mobile+')LASER";\nstruct LaserConfig {const char*key;unsigned hue,core;};\nstatic const LaserConfig laserConfigs[]={\n'
header+=''.join('{'+json.dumps(c['key'])+',0x'+c['color']+',0x'+c['core']+'},\n' for c in configs)+'};\n'
(p/'laser_assets.h').write_text(header,encoding='utf-8')
print('Prepared supplied shader, Android rounded-border adaptation and',len(configs),'system color mappings.')
print([(x['key'],x['color'],x['source']) for x in configs[:9]])
