from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,collections
P=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\metadata-publica-20261006');games=[];aliases=[];counts=collections.Counter()
with zipfile.ZipFile(P/'Metadata.zip') as z:
 with z.open('Metadata.xml') as f:
  it=E.iterparse(f,events=('start','end'));_,root=next(it)
  for event,e in it:
   if event!='end':continue
   if e.tag=='Game':
    row={x.tag:x.text or '' for x in e if x.tag in ['Name','DatabaseID','Platform','MaxPlayers','CommunityRating','CommunityRatingCount','ReleaseType','Cooperative','ReleaseDate','ReleaseYear']}
    games.append(row);counts[row.get('Platform','')]+=1;e.clear();root.clear()
   elif e.tag=='GameAlternateName':
    aliases.append({x.tag:x.text or '' for x in e});e.clear();root.clear()
   elif e.tag in ['GameImage','PlatformImage','PlatformVideo','GameVideo']:e.clear();root.clear()
(P/'game-facts.json').write_text(json.dumps(games,ensure_ascii=False,separators=(',',':')),'utf8');(P/'alternate-names.json').write_text(json.dumps(aliases,ensure_ascii=False,separators=(',',':')),'utf8')
print('games',len(games),'aliases',len(aliases));print(json.dumps(dict(counts),ensure_ascii=False));print('alias sample',aliases[:2])
