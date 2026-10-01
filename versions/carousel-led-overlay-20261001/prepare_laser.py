from pathlib import Path
import json,re,xml.etree.ElementTree as ET
p=Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
t=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx')
source=(t/'_theme_inc/premium-selection-laser.glsl').read_text(encoding='utf-8-sig')
(p/'premium-selection-laser.glsl').write_bytes((t/'_theme_inc/premium-selection-laser.glsl').read_bytes())
(p/'premium-selection-glow.svg').write_bytes((t/'_theme_inc/images/premium-selection-glow.svg').read_bytes())
# Android shader is an editable source, not generated from the desktop approximation.
# Keep the supplied desktop file for provenance and the system colors/overrides below.
mobile=(p/'premium-selection-laser-android.glsl').read_text(encoding='utf-8')
rows=json.loads((p/'theme-infos-mapping.json').read_text(encoding='utf-8'))
sega={'mastersystem','megadrive','megadrivebr','genesis','megadrive-msu','gamegear','dreamcast','sega32x','segacd','saturn','naomi','atomiswave'}
overrides=json.loads((p/'laser-user-overrides.json').read_text(encoding='utf-8'))['colors'] if (p/'laser-user-overrides.json').exists() else {}
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
 secondary='00000000'
 if key in overrides:
  color=overrides[key][0];secondary=overrides[key][1] if len(overrides[key])>1 else '00000000';core=None;origin='explicit user palette; laser-user-overrides.json'
 if not core:
  rgb=[int(color[i:i+2],16) for i in (0,2,4)];core=''.join(f'{round(x*.10+255*.90):02X}' for x in rgb)+'FF'
 configs.append({'key':key,'folder':folder,'theme_file':str(file) if file.exists() else 'general.xml','color':color,'secondary':secondary,'core':core,'source':origin,'pos':[.053763441,-.031617647],'size':[.892473118,1.063235294]})
(p/'laser-system-colors.json').write_text(json.dumps(configs,ensure_ascii=False,indent=2),encoding='utf-8')
header='static const char laserShaderSource[]=R"LASER('+mobile+')LASER";\nstruct LaserConfig {const char*key;unsigned hue,core,secondary;};\nstatic const LaserConfig laserConfigs[]={\n'
header+=''.join('{'+json.dumps(c['key'])+',0x'+c['color']+',0x'+c['core']+',0x'+c['secondary']+'},\n' for c in configs)+'};\n'
(p/'laser_assets.h').write_text(header,encoding='utf-8')
print('Prepared native premium LED, true rounded perimeter and',len(configs),'system color mappings.')
print([(x['key'],x['color'],x['source']) for x in configs[:9]])
