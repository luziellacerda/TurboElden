from pathlib import Path
import xml.etree.ElementTree as ET,json,re,hashlib,shutil
p=Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
src=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx2\_theme_inc\infos')
dst=p/'theme-infos';dst.mkdir(exist_ok=True)
index={};manifest=[]
def select(node):
 if node is None:return '',None
 options=node.findall('text')
 e=next((x for x in options if 'pt' in x.get('lang','').split(',')),None)
 if e is None:e=next((x for x in options if not x.get('lang')),options[0] if options else None)
 if e is None:return '',None
 return '\n\n'.join(' '.join(s.split()) for s in ''.join(e.itertext()).strip().split('\n\n') if s.strip()),e.get('lang','default')
for f in sorted(src.glob('*.xml')):
 raw=f.read_bytes();shutil.copyfile(f,dst/f.name);r=ET.fromstring(raw)
 fields={n.get('name'):n for n in r.findall('.//text[@name]') if not n.get('region')}
 title,tl=select(fields.get('system_name',fields.get('system_namee')))
 description,language=select(fields.get('system_description'))
 index[f.stem.casefold()]={'file':f.name,'name':title,'description':description,'language':language}
 manifest.append({'file':f.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
rows=json.loads((p.parent/'mapa-sistemas-agrupados.json').read_text(encoding='utf-8'))
alias={'ps2br':'ps2','n64br':'n64','megadrivebr':'megadrive','snesbr':'snes','pcenginecd':'pcenginecd','snes-msu1':'snes'}
header=['struct SystemInfo {const char* key;const char* title;const char* description;const char* file;};','static const SystemInfo systemInfos[]={']
mapping=[]
for row in rows:
 folder=row['pastas'][0].rsplit('/',1)[-1].lower();folder=alias.get(folder,folder)
 aliases={'Gameboy':'gb','Gameboy Color':'gbc','Master System ':'mastersystem','MegaDrive - BR':'megadrive','Nintendo 64':'n64','Nintendo 64 - BR':'n64','Nintendo DS':'nds','Neo Geo':'neogeo','Neo Geo CD':'neogeocd','Nintendinho':'nes','Odyssey 2':'odyssey2','Pc Engine':'pcengine','Pc Engine cd':'pcenginecd','Super Nintendo':'snes','Super Nintendo - BR':'snes'}
 folder=aliases.get(row['chave_filtro'],folder)
 info=index.get(folder) or index.get(row['chave_filtro'].strip().lower()) or {}
 desc=info.get('description','')
 # Keep complete XML/index; screen excerpt omits accidentally mixed-language tails in source paragraphs.
 excerpt=re.split(r'\n\n(?:Italiano:|Ingl[eê]s:|English:)',desc)[0]
 if len(excerpt)>600:excerpt=excerpt[:597].rsplit(' ',1)[0]+'…'
 title=info.get('name') or row['plataforma'] or row['chave_filtro']
 header.append('{'+','.join(json.dumps(x,ensure_ascii=False) for x in [row['chave_filtro'],title,excerpt,info.get('file','')])+'},')
 mapping.append({'key':row['chave_filtro'],'folder':folder,'file':info.get('file'),'language':info.get('language'),'has_description':bool(desc)})
header.append('};\nstatic constexpr int NINFOS=sizeof(systemInfos)/sizeof(systemInfos[0]);')
(p/'system_infos.h').write_text('\n'.join(header),encoding='utf-8')
(p/'theme-infos-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'theme-infos-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'theme-infos-mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
print('Imported XMLs',len(manifest),'bytes',sum(x['bytes'] for x in manifest))
print('Mapped',sum(bool(x['file']) for x in mapping),'of',len(mapping),'descriptions',sum(x['has_description'] for x in mapping))
print('Missing or non-Portuguese',[(x['key'],x['folder'],x['file'],x['language']) for x in mapping if not x['file'] or x['language']!='pt'])
