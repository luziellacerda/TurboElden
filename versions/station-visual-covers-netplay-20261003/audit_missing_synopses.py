"""Read-only exact search for missing synopses; no normalized/fuzzy title matching."""
from pathlib import Path, PurePosixPath
import collections,hashlib,json,re,xml.etree.ElementTree as ET
from prepare_visual_metadata import ROOT,OLD,ROMS,clean
def stem(text):
 return PurePosixPath((text or '').replace('\\','/')).stem
def main(rows=None):
 inv=json.loads((ROOT/'evidence/xml-source-inventory.json').read_text('utf8'))
 roots={family:ET.parse(ROMS/family/'gamelist.xml').getroot().findall('game') for family in ['snes','megadrive']}
 if rows is None:rows=json.loads((ROOT/'assets/station-metadata/station-synopses.json').read_text('utf8'))
 missing=[row for row in rows if not clean(roots[row['sourcePlatform']][row['sourceOrdinal']-1].findtext('desc',''))]
 platform={}
 for file in [OLD/'game-xml-sources.json',OLD/'metadata-sources/catalog-xml-manifest.json']:
  for row in json.loads(file.read_text('utf8')):
   if row.get('file') and row.get('platform'):platform[str(Path(row['file']))]=row['platform']
 entries=[];files=[]
 for row in inv:
  if row['status']!='imported':continue
  file=Path(row['source']);root=ET.parse(file).getroot()
  # Historical merged game-info XML used fuzzy matching. It remains archived,
  # but its generated names cannot prove exact identity for missing entries.
  if 'metadata merge' in root.attrib.get('source',''):
   files.append({'source':str(file),'searched':False,'reason':'derived historical merge cannot prove identity'});continue
  family=platform.get(str(file))
  if family is None:
   try:family=file.relative_to(ROMS).parts[0]
   except ValueError:pass
  files.append({'source':str(file),'searched':bool(family in ('snes','megadrive')),'platform':family})
  if family not in ('snes','megadrive'):continue
  for ordinal,game in enumerate(root.findall('game'),1):
   desc=clean(game.findtext('desc',''))
   if desc:entries.append({'source':str(file),'sha256':row['sha256'],'ordinal':ordinal,'platform':family,'name':game.findtext('name',''),'stem':stem(game.findtext('path','')),'description':desc})
 results=[]
 for item in missing:
  game=roots[item['sourcePlatform']][item['sourceOrdinal']-1];originalStem=stem(game.findtext('path',''))
  matches=[]
  for candidate in entries:
   if candidate['platform']!=item['sourcePlatform']:continue
   reasons=[]
   if candidate['name']==item['name']:reasons.append('exact-name')
   if originalStem and candidate['stem']==originalStem:reasons.append('exact-ROM-stem')
   if reasons:matches.append(dict(candidate,match=reasons))
  distinct={m['description'] for m in matches}
  results.append({'itemId':item['itemId'],'platform':item['platform'],'name':item['name'],'originalStem':originalStem,'status':'unique-description' if len(distinct)==1 else 'ambiguous' if distinct else 'missing','matches':matches})
 report={'policy':'Same platform plus exact full name OR exact ROM stem. No normalization or fuzzy match. Historical merged XML excluded as authority. Different descriptions remain ambiguous.','searchedFiles':files,'counts':dict(collections.Counter(r['status'] for r in results)),'items':results}
 (ROOT/'evidence/missing-synopses-exact-search.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return report
if __name__=='__main__':
 report=main();print(json.dumps({'counts':report['counts'],'results':[{k:v for k,v in r.items() if k!='matches'} for r in report['items']]},ensure_ascii=False,indent=2))
