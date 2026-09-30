from pathlib import Path
import json,xml.etree.ElementTree as ET,zipfile,collections,re,unicodedata,urllib.parse,html
p=Path(__file__).parent
platforms={'3ds':'Nintendo 3DS','psx':'Sony Playstation','ps2':'Sony Playstation 2','psp':'Sony PSP','switch':'Nintendo Switch','wii':'Nintendo Wii','arcade':'Arcade','atari2600':'Atari 2600','atari7800':'Atari 7800','atomiswave':'Sammy Atomiswave','colecovision':'ColecoVision','cps1':'Arcade','cps2':'Arcade','cps3':'Arcade','dreamcast':'Sega Dreamcast','fds':'Nintendo Famicom Disk System','gameandwatch':'Nintendo Game & Watch','gamegear':'Sega Game Gear','gb':'Nintendo Game Boy','gba':'Nintendo Game Boy Advance','gbc':'Nintendo Game Boy Color','jaguar':'Atari Jaguar','mame':'Arcade','mastersystem':'Sega Master System','megadrive':'Sega Genesis','n64':'Nintendo 64','nds':'Nintendo DS','neogeo':'SNK Neo Geo AES','neogeocd':'SNK Neo Geo CD','nes':'Nintendo Entertainment System','odyssey2':'Magnavox Odyssey 2','pcengine':'NEC TurboGrafx-16','pcenginecd':'NEC TurboGrafx-CD','sega32x':'Sega 32X','snes':'Super Nintendo Entertainment System','supergrafx':'NEC SuperGrafx','fbneo':'Arcade'}
rows=json.loads((p/'theme-infos-mapping.json').read_text(encoding='utf-8'))
keyfolders={r['key']:r['folder'] for r in rows}
active={x['chave_filtro'] for x in json.loads((p/'device-original-platforms.json').read_text(encoding='utf-8'))}
active-={'colecovision','fds','gameandwatch','Gameboy','Odyssey 2'}
# Keep game identity/sequence numbers; discard only file packaging, release prefixes and region tags.
def namekey(s,loose=False):
 s=urllib.parse.unquote(html.unescape(s or '')).replace('\\','/').rsplit('/',1)[-1]
 s=re.sub(r'\.(zip|7z|rar|nsp|xci|3ds|cci|cia|iso|cso|chd|bin|cue|rom|a26|a78|nds|nes|smc|sfc|gba|gbc|gb|md|gen|sms|gg|32x|pce|j64|col|fds|n64|z64|v64)$','',s,flags=re.I)
 if loose:
  s=re.sub(r'\[[^]]*\]|\([^)]*\)',' ',s)
  s=re.sub(r'^\s*\d{4}\s*[-_]\s*','',s)
  s=re.sub(r'\s+(?:v\d+(?:\.\d+)*|PT[- ]?BR|USA|EUR|EUROPE|JAPAN|US|BR)$','',s,flags=re.I)
 s=s.strip()
 s=re.sub(r',\s*(the|a|an)(?=\s*[-:]|$)', '',s,flags=re.I)
 s=re.sub(r'^(the|a|an)\s+', '',s,flags=re.I)
 s=unicodedata.normalize('NFKD',s.lower());s=''.join(c for c in s if not unicodedata.combining(c))
 return re.sub('[^a-z0-9]','',s)
def aliases(s):return {namekey(s),namekey(s,True)}-{''}
def clean(s):return re.sub(r'\s+',' ',html.unescape(s or '').replace('\\n',' ')).strip()
records=[];index=collections.defaultdict(list)
def add(r,names):
 i=len(records);records.append(r)
 for n in names:
  for k in aliases(n):index[(r['platform'],k)].append(i)
local=json.loads((p/'game-xml-sources.json').read_text(encoding='utf-8'))
manifest=p/'metadata-sources/catalog-xml-manifest.json'
if manifest.exists():local+=json.loads(manifest.read_text(encoding='utf-8'))
for entry in local:
 if not entry.get('descriptions'):continue
 folder={'ps2br':'ps2'}.get(entry['platform'],entry['platform']);plat=platforms.get(folder)
 if not plat:continue
 file=entry['file']
 for g in ET.parse(file).getroot().findall('game'):
  desc=clean(g.findtext('desc',''))
  if len(desc)<20:continue
  rank=30 if entry.get('url') else 20 if r'G:\TURBORAMA\RetroBat' in file else 10
  add({'platform':plat,'name':g.findtext('name',''),'description':desc,'source':entry.get('url',file),'rank':rank,'genre':g.findtext('genre',''),'year':g.findtext('releasedate','')[:4],'developer':g.findtext('developer',''),'publisher':g.findtext('publisher',''),'players':g.findtext('players',''),'type':'local_xml'},[g.findtext('name',''),g.findtext('path','')])
cache=p/'metadata-sources/launchbox-games-relevant.json'
if cache.exists():db=json.loads(cache.read_text(encoding='utf-8'))
else:
 db=[];ids={};othernames=[];allplatforms=collections.Counter();wanted=set(platforms.values())
 z=zipfile.ZipFile(p/'metadata-sources/LaunchBox-Metadata.zip')
 iterator=ET.iterparse(z.open('Metadata.xml'),events=('start','end'));root=next(iterator)[1];depth=1
 for event,e in iterator:
  if event=='start':depth+=1;continue
  if depth==2:
   if e.tag=='Game':
    plat=e.findtext('Platform','');allplatforms[plat]+=1
    if plat in wanted:
     r={k:e.findtext(k,'') for k in ['Name','Platform','Overview','ReleaseDate','ReleaseYear','Developer','Publisher','Genres','MaxPlayers','DatabaseID']};r['aliases']=[];ids[r['DatabaseID']]=r;db.append(r)
   elif e.tag=='GameAlternateName':othernames.append({c.tag:c.text for c in e})
   e.clear();root.clear()
  depth-=1
 for n in othernames:
  key=n.get('DatabaseID') or n.get('GameID');value=n.get('AlternateName') or n.get('Name')
  if key in ids and value:ids[key]['aliases'].append(value)
 cache.write_text(json.dumps(db,ensure_ascii=False),encoding='utf-8')
 (p/'metadata-sources/launchbox-platforms.json').write_text(json.dumps(allplatforms,indent=2),encoding='utf-8')
 print('External metadata parsed',len(db),'games; alternate names',len(othernames),flush=True)
for g in db:
 desc=clean(g['Overview']);kind='database_xml'
 if not desc:
  # Original factual summary only when authoritative fields exist, not an invented plot.
  details=[]
  if g['Genres']:details.append('Gênero: '+g['Genres']+'.')
  year=(g['ReleaseDate'] or g['ReleaseYear'])[:4]
  if year:details.append('Lançamento: '+year+'.')
  if g['Developer']:details.append('Desenvolvimento: '+g['Developer']+'.')
  if g['Publisher']:details.append('Publicação: '+g['Publisher']+'.')
  desc=' '.join(details);kind='metadata_summary'
 if not desc:continue
 add({'platform':g['Platform'],'name':g['Name'],'description':desc,'source':'https://gamesdb.launchbox-app.com/games/details/'+g['DatabaseID'],'rank':3 if kind=='database_xml' else 1,'genre':g['Genres'],'year':(g['ReleaseDate'] or g['ReleaseYear'])[:4],'developer':g['Developer'],'publisher':g['Publisher'],'players':g['MaxPlayers'],'type':kind},[g['Name'],*g['aliases']])
# Arcade filename -> title aliases supplied by MAME metadata.
z=zipfile.ZipFile(p/'metadata-sources/LaunchBox-Metadata.zip');mame={}
for event,e in ET.iterparse(z.open('Mame.xml'),events=('end',)):
 if e.tag=='MameFile':
  mame[e.findtext('FileName','').lower()]={'name':e.findtext('Name',''),'parent':e.findtext('CloneOf','')};e.clear()
manual_aliases=json.loads((p/'game-title-aliases.json').read_text(encoding='utf-8'))
overrides=json.loads((p/'game-description-overrides.json').read_text(encoding='utf-8'))
for r in overrides:
 add(dict(r,rank=40,genre='',year='',developer='',publisher='',players='',type='official_summary'),r['aliases'])
out=[];missing=[];stats=collections.defaultdict(collections.Counter)
catalog=json.loads((p.parent/'catalog-baseline.json').read_text(encoding='utf-8-sig'))
for cat in catalog:
 key=cat.get('Name');folder=keyfolders.get(key)
 if key not in active:continue
 plat=platforms.get(folder,'')
 for game in cat.get('Files',[]):
  title=game.get('DisplayName','');url=game.get('Url','');filename=urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit('/',1)[-1]);names=[title,filename]
  names += manual_aliases.get(key,{}).get(title,[])
  if Path(filename).suffix.lower() in {'.txt','.xml','.pdf','.mp4','.png','.jpg','.jpeg','.webp','.svg','.mp3','.srm','.ips','.ups','.dat','.ini','.tmp','.rar'}:continue
  if game.get('Oculto'):continue
  stats[key]['total']+=1
  if plat=='Arcade':
   rom=filename.rsplit('.',1)[0].lower();m=mame.get(rom)
   if m:names+=[m['name'],m['parent']]
  candidates=set()
  for n in names:
   for alias in aliases(n):candidates.update(index.get((plat,alias),[]))
  # Never fuzzy-match unrelated titles; prefer the local XML and strongest exact alias.
  found=max((records[i] for i in candidates),key=lambda r:(r['rank'],len(r['description'])),default=None)
  item={'id':game['Id'],'system':key,'folder':folder,'name':title,'filename':filename,'description':found['description'] if found else '', 'matched_name':found['name'] if found else '', 'source':found['source'] if found else '', 'type':found['type'] if found else 'missing'}
  if found:
   item.update({k:found[k] for k in ['genre','year','developer','publisher','players']});stats[key][found['type']]+=1
  else:missing.append(item);stats[key]['missing']+=1
  out.append(item)
(p/'game-synopses.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'game-synopses-missing.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'game-synopses-coverage.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL',len(out),'matched',len(out)-len(missing),'missing',len(missing))
for key,s in stats.items():print(key,dict(s))
