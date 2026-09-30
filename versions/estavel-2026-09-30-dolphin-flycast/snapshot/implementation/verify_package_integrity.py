from pathlib import Path
import zipfile,hashlib,json
p=Path(__file__).parent
base=Path('E:\\ESTUDO APK\\work\\native-carousel\\implementation\\stable-reference-audit\\original-1.0.8-alignment-preserved.apk')
new=p/'TurboramaStation-ESTAVEL-6727ab7-design.apk'
def digest(z,n):
 h=hashlib.sha256()
 with z.open(n) as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
with zipfile.ZipFile(base) as a,zipfile.ZipFile(new) as b:
 old={n for n in a.namelist() if not n.startswith('META-INF/')}
 cur={n for n in b.namelist() if not n.startswith('META-INF/')}
 changed=[n for n in sorted(old&cur) if digest(a,n)!=digest(b,n)]
 result={'baseline':str(base),'apk':str(new),'files_preserved':len(old&cur)-len(changed),'changed':changed,'added':sorted(cur-old),'removed':sorted(old-cur)}
 assert changed==['classes5.dex'],changed
 expected={'lib/arm64-v8a/libturbo_carousel.so','assets/turbo-system-info/index.json','assets/turbo-system-info/mapping.json'}
 expected.update('assets/turbo-system-info/xml/'+f.name for f in (p/'theme-infos').glob('*.xml'))
 expected.update('assets/turbo-carousel/'+name for name in ['premium-selection-laser.glsl','premium-selection-laser-android.glsl','premium-selection-glow.svg','laser-system-colors.json'])
 expected.update('assets/turbo-carousel/'+name for name in ['premium-spacecraft-rear-v2.png','game-info-coverage-final.json','game-info-unmatched-final.json','game-title-aliases.json','turborama-palette.json'])
 expected.update('assets/turbo-game-info/'+f.name for f in (p/'game-info-xml').glob('*.xml'))
 expected.update('assets/turborama-policy/'+name for name in ['USO-E-ACESSO.md','NOTICE-TURBORAMA.txt','ai-access-policy.json','AGENTS.md','CLAUDE.md','GEMINI.md'])
 expected.update('assets/turbo-space3d/'+name for name in __import__('json').loads((p/'space3d/license-assets.json').read_text()))
 assert set(result['added'])==expected,result['added']
 for f in (p/'theme-infos').glob('*.xml'):assert digest(b,'assets/turbo-system-info/xml/'+f.name)==hashlib.sha256(f.read_bytes()).hexdigest()
 result['xml_files']=len(list((p/'theme-infos').glob('*.xml')))
 assert not result['removed'],result['removed']
 (p/'package-integrity-exact-stable.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps({k:(len(v) if k=='added' else v) for k,v in result.items()},indent=2))
