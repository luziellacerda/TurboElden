from pathlib import Path
import json,xml.etree.ElementTree as ET,re,collections,textwrap
p=Path(__file__).parent
source=json.loads((p/'game-synopses.json').read_text(encoding='utf-8'))
# The native export is authoritative for which ROMs the existing catalog actually displays.
export=p/'native-catalog.tsv'
if export.exists():
 rows=[line.split('\t') for line in export.read_text(encoding='utf-8-sig').splitlines() if line]
 native={(r[1],r[0]) for r in rows if len(r)==5}
 source=[r for r in source if (r['system'],r['id']) in native]
keys=sorted({x['system'] for x in source});out=p/'game-info-xml';out.mkdir(exist_ok=True)
header=['struct GameInfo {const char*system;const char*id;const char*name;const char*pages;const char*source;int pageCount;};','static const GameInfo gameInfos[]={']
coverage={}
for key in keys:
 games=[x for x in source if x['system']==key]
 root=ET.Element('gameList',{'system':key,'source':'TurboramaStation metadata merge'})
 for r in games:
  node=ET.SubElement(root,'game',{'id':r['id'],'metadataStatus':r['type']})
  for k,v in {'path':'./'+r['filename'],'name':r['name'],'desc':r['description'],'source':r['source'],'matchedName':r['matched_name'],'genre':r.get('genre',''),'releasedate':r.get('year',''),'developer':r.get('developer',''),'publisher':r.get('publisher',''),'players':r.get('players','')}.items():ET.SubElement(node,k).text=str(v)
  desc=r['description'] or 'Sinopse ainda não localizada para esta edição.'
  pages=textwrap.wrap(desc,width=440,break_long_words=False,break_on_hyphens=False) or ['']
  strings=[r['system'],r['id'],r['name'],'\f'.join(pages),r['source']]
  header.append('{'+','.join(json.dumps(v,ensure_ascii=False) for v in strings)+','+str(len(pages))+'},')
 slug=re.sub(r'[^a-z0-9]+','-',key.lower()).strip('-')
 ET.indent(root);ET.ElementTree(root).write(out/(slug+'.xml'),encoding='utf-8',xml_declaration=True)
 coverage[key]={'total':len(games),'description':sum(bool(x['description']) for x in games),'missing':sum(not x['description'] for x in games)}
header+=['};','static constexpr int NGAMEINFOS=sizeof(gameInfos)/sizeof(gameInfos[0]);']
(p/'game_infos.h').write_text('\n'.join(header),encoding='utf-8')
report={'catalogIdentity':'native export' if export.exists() else 'candidate catalog files','systems':len(keys),'total':len(source),'description':sum(bool(x['description']) for x in source),'missing':sum(not x['description'] for x in source),'platforms':coverage}
(p/'game-info-coverage-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'game-info-unmatched-final.json').write_text(json.dumps([x for x in source if not x['description']],ensure_ascii=False,indent=2),encoding='utf-8')
print({k:v for k,v in report.items() if k!='platforms'})
