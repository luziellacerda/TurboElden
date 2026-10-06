from pathlib import Path
import json,csv,collections,re,unicodedata,xml.etree.ElementTree as E,hashlib
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native';P=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\metadata-publica-20261006')
games=json.loads((P/'game-facts.json').read_text('utf8'));aliases=json.loads((P/'alternate-names.json').read_text('utf8'))
# Explicit platform correspondence, never platform-independent title matching.
mapping={
'3do':'3DO Interactive Multiplayer','arcade':'Arcade','atari2600':'Atari 2600','atari5200':'Atari 5200','atari7800':'Atari 7800','jaguar':'Atari Jaguar','jaguarcd':'Atari Jaguar CD','lynx':'Atari Lynx','colecovision':'ColecoVision','intellivision':'Mattel Intellivision','odyssey2':'Magnavox Odyssey 2','pcengine':'NEC TurboGrafx-16','pcenginecd':'NEC TurboGrafx-CD','supergrafx':'PC Engine SuperGrafx','pcfx':'NEC PC-FX','nes':'Nintendo Entertainment System','fds':'Nintendo Famicom Disk System','gb':'Nintendo Game Boy','gbc':'Nintendo Game Boy Color','gba':'Nintendo Game Boy Advance','snes':'Super Nintendo Entertainment System','n64':'Nintendo 64','nds':'Nintendo DS','gamecube':'Nintendo GameCube','wii':'Nintendo Wii','gameandwatch':'Nintendo Game & Watch','virtualboy':'Nintendo Virtual Boy','atomiswave':'Sammy Atomiswave','sega32x':'Sega 32X','segacd':'Sega CD','dreamcast':'Sega Dreamcast','gamegear':'Sega Game Gear','megadrive':'Sega Genesis','mastersystem':'Sega Master System','model2':'Sega Model 2','model3':'Sega Model 3','naomi':'Sega Naomi','naomi2':'Sega Naomi 2','saturn':'Sega Saturn','sg1000':'Sega SG-1000','neogeo':'SNK Neo Geo AES','neogeocd':'SNK Neo Geo CD','ngp':'SNK Neo Geo Pocket','ngpc':'SNK Neo Geo Pocket Color','psx':'Sony Playstation','ps2':'Sony Playstation 2','ps3':'Sony Playstation 3','psp':'Sony PSP','xbox':'Microsoft Xbox','xbox360':'Microsoft Xbox 360',
# Existing newer platforms remain supported in a separate metadata group.
'3ds':'Nintendo 3DS','wiiu':'Nintendo Wii U','psvita':'Sony Playstation Vita','switch':'Nintendo Switch'}
nativeAliases={'Nintendinho':'nes','Super Nintendo':'snes','Super Nintendo - BR':'snes','snesbr':'snes','Nintendo 64':'n64','Nintendo 64 - BR':'n64','n64br':'n64','Gameboy':'gb','Gameboy Color':'gbc','Game Boy Color':'gbc','Nintendo DS':'nds','Gba':'gba','gc':'gamecube','MegaDrive - BR':'megadrive','megadrivebr':'megadrive','Master System':'mastersystem','megacd':'segacd','saturno':'saturn','Playstation 1':'psx','Playstation 2':'ps2','Playstation 2 - BR':'ps2','Playstation 3':'ps3','Psp - BR':'psp','pspbr':'psp','Neo Geo':'neogeo','Neo Geo CD':'neogeocd','Pc Engine':'pcengine','Pc Engine cd':'pcenginecd','Xbox 360':'xbox360','ps1':'psx','cps1':'arcade','cps2':'arcade','cps3':'arcade','fbneo':'arcade','mame':'arcade'}
ACCENTS={'À':'a','Á':'a','Â':'a','Ã':'a','Ä':'a','Å':'a','à':'a','á':'a','â':'a','ã':'a','ä':'a','å':'a','Ç':'c','ç':'c','È':'e','É':'e','Ê':'e','Ë':'e','è':'e','é':'e','ê':'e','ë':'e','Ì':'i','Í':'i','Î':'i','Ï':'i','ì':'i','í':'i','î':'i','ï':'i','Ñ':'n','ñ':'n','Ò':'o','Ó':'o','Ô':'o','Õ':'o','Ö':'o','ò':'o','ó':'o','ô':'o','õ':'o','ö':'o','Ù':'u','Ú':'u','Û':'u','Ü':'u','ù':'u','ú':'u','û':'u','ü':'u','Ý':'y','ý':'y','ÿ':'y'}
mapping.update({'astrocade':'Bally Astrocade','loopy':'Casio Loopy','pv1000':'Casio PV-1000','amigacd32':'Commodore Amiga CD32','arcadia':'Emerson Arcadia 2001','scv':'Epoch Super Cassette Vision','channelf':'Fairchild Channel F','vectrex':'GCE Vectrex','n64dd':'Nintendo 64DD','pokemonmini':'Nintendo Pokemon Mini','ngage':'Nokia N-Gage','cdi':'Philips CD-i','videopacplus':'Philips Videopac+','pico':'Sega Pico','gamecom':'Tiger Game.com','supervision':'Watara Supervision','wonderswan':'WonderSwan','wonderswancolor':'WonderSwan Color'})
nativeAliases.update({'ps2br':'ps2','sufami':'snes','ws':'wonderswan','wsc':'wonderswancolor'})
nativeAliases.update({v:k for k,v in mapping.items()})
def norm(s):
 out=[]
 for c in s:
  if c.isascii():
   if c.isalnum():out.append(c.lower())
  elif c in ACCENTS:out.append(ACCENTS[c])
  elif c in '\u0300\u0301\u0302\u0303\u0308\u0327\u2018\u2019\u201c\u201d\u2013\u2014\u2122\u00ae\u00a9':pass
  else:return '' # Do not collapse unsupported non-Latin titles onto ASCII homonyms.
 return ''.join(out)
REGIONS={'usa','europe','world','japan','brazil','br','usa, europe','europe, usa','japan, usa','usa, japan','japan, europe','japan, usa, europe'}
def cleanTitle(s):
 s=s.strip()
 m=re.search(r'\s*\(([^()]*)\)$',s)
 if m and m[1].lower() in REGIONS:s=s[:m.start()].rstrip()
 m=re.search(r', (The|A|An)$',s,re.I)
 if m:s=m[1]+' '+s[:m.start()]
 return s
platformAliases={norm(k):v for k,v in nativeAliases.items()};platformAliases.update({norm(k):k for k in mapping})
reverse={v:k for k,v in mapping.items()};selected={g['DatabaseID']:g for g in games if g.get('Platform') in reverse}
index=collections.defaultdict(set)
for id,g in selected.items():index[(reverse[g['Platform']],norm(cleanTitle(g['Name'])))].add(id)
for a in aliases:
 if a.get('DatabaseID') in selected:
  g=selected[a['DatabaseID']];index[(reverse[g['Platform']],norm(cleanTitle(a['AlternateName'])))].add(g['DatabaseID'])
def facts(g):
 p=g.get('MaxPlayers','');p=p if re.fullmatch(r'[1-9][0-9]{0,2}',p) else ''
 try:r=float(g.get('CommunityRating',''));votes=int(g.get('CommunityRatingCount','0'))
 except ValueError:r=-1;votes=0
 rating=round(r*200) if 0<=r<=5 and votes>0 else -1
 return p,rating,votes
q=lambda s:json.dumps(s,ensure_ascii=False)
base=N/'station_game_details.h';original=(W.parent/'station-carousel-scope-r38-20261006/native/station_game_details.h').read_text('utf8');details={}
for line in original.splitlines():
 if line.startswith('{"'):
  id,p,r=json.loads('['+line.strip().rstrip(',')[1:-1]+']');details[id]=[p,r]
catalog=Path('work/TurboElden-git/versions/station-final-details-r37-20261005/data/synopses-catalog-14.tsv')
rows=list(csv.DictReader(catalog.open(encoding='utf-8-sig',newline=''),delimiter='\t'));audit=[]
curated={
('megadrive','Blockout (World)'):('3877','Canonical Blockout spelling, released Mega Drive record; do not use duplicate Block Out score.'),
('megadrive','Congo'):('130516','Congo: The Game, unreleased Mega Drive title.'),
('megadrive','Super Mario Bros.'):('156904','Taiwan unlicensed port in artifact filename and existing description; not the mairtrus hack.'),
('megadrive','Super Mario Bros. 2 1998'):('156903','Same title, explicit release year 1998 and platform.'),
('megadrive','Super Mario World'):('451348','Existing description identifies Squirrel King hack by Chuanpu/Jazz Dark; not World 64.'),
('megadrive','The Lion King 3'):('141319','Same unlicensed Genesis title; article difference.'),
('megadrive','Thunderbolt 2'):('34110','Genesis title with Arabic versus Roman numeral.'),
('megadrive','Water Margin : The Tales of Clouds and Winds'):('34107','Pluralized catalog subtitle for the same Genesis title.'),
('megadrivebr','Water Margin : The Tales of Clouds and Winds'):('34107','Base-game rating; translation does not have a separate community score.'),
('megadrivebr','Robocop vs Terminator (BR)'):('4600','Versus abbreviation; base-game rating, not translation-specific.'),
('megadrivebr','Sonic Hedgehog 3D Blast (BR)'):('2284','Catalog expands Sonic name; base game, not Directors Cut.'),
('megadrivebr','Super Street Fighter 2 - The New Challengers (BR)'):('2585','II numeral and full subtitle; base-game community rating.'),
('neogeocd','Bang\u00b2 Busters'):('164942','Superscript 2 spells Bang Bang in the source title.'),
('neogeocd','Metal Slug 2: Super Vehicle - 001/II'):('127412','Same Neo Geo CD release with subtitle.'),
('neogeocd',"Ninja Master's"):('137354','Neo Geo CD release with full Haou Ninpou Chou subtitle; other duplicate has no facts.'),
('neogeocd','Real Bout Special'):('136843','Short name of Real Bout Fatal Fury Special, Neo Geo CD.'),
('neogeocd','The Last Blade 2: Heart of the Samurai'):('136829','Same Neo Geo CD release, subtitle omitted by source.'),
('snes','Super Metroid - Zero Mission'):('138378','ArtifactLaunchPath is Metroid Super Zero Mission.smc; existing synopsis identifies this hack.')}
# The alternate ROM is explicitly identified by the catalog's actual launch path.
zelda=[g['DatabaseID'] for g in selected.values() if g['Platform']=='Nintendo 64' and g['Name']=='The Legend of Zelda: Ocarina of Time']
assert len(zelda)==1
curated[('n64','The Legend of Zelda: Ocarina of Time (ROM alternativa)')]=(zelda[0],'Launch path Legend of Zelda, The - Ocarina of Time.rom; base title, alternate ROM explicitly identified by catalog.')
for row in rows:
 id=row['itemId'];platform=platformAliases.get(norm(row['platform']),'');title=norm(cleanTitle(row['name']));matches=index.get((platform,title),set()) if title else set();before=details.get(id,['',-1]);result=before[:];src='existing_catalog_xml';lb=None
 manual=curated.get((row['platform'],row['name']))
 if manual:
  matches={manual[0]};assert reverse[selected[manual[0]]['Platform']]==platform
 if len(matches)==1:
  lb=selected[next(iter(matches))];p,r,votes=facts(lb)
  if not result[0] and p:result[0]=p
  if r>=0:result[1]=r;src='launchbox_community'
 details[id]=result;audit.append({'itemId':id,'platform':row['platform'],'name':row['name'],'players':result[0],'ratingThousandths':result[1],'ratingSource':src if result[1]>=0 else 'unavailable','publicMatch':lb['DatabaseID'] if lb else None,'matchingCandidates':len(matches),'before':before,'votes':facts(lb)[2] if lb else None,'reviewedAlias':manual[1] if manual else None,'ratingScope':'base_game_for_translation' if row['platform'].endswith('br') else 'platform_release','sourceUrl':'https://gamesdb.launchbox-app.com/Metadata.zip' if lb else None})
# Retain exact current IDs and expose a sorted metadata-only fallback for future real games.
start=original.index('static const StationGameDetails stationGameDetails[] = {');end=original.index('\n};',start)+3
array='static const StationGameDetails stationGameDetails[] = {\n'+''.join('{'+q(id)+','+q(p)+','+str(r)+'},\n' for id,(p,r) in sorted(details.items()))+'};'
original=original.replace('// XML rating is a catalog score in [0,1], not an average of user reviews.','// Ratings: LaunchBox community means when matched with votes; otherwise retained catalog XML.\n// Per-item sources, votes, reviewed aliases and missing fields are in current-metadata-audit.json.')
start=original.index('static const StationGameDetails stationGameDetails[] = {');end=original.index('\n};',start)+3
base.write_text(original[:start]+array+original[end:],'utf8')
unique=[]
for (platform,title),ids in sorted(index.items()):
 if len(ids)!=1 or not title:continue
 id=next(iter(ids));p,r,v=facts(selected[id]);
 if p or r>=0:unique.append((platform+'|'+title,id,p,r))
unique.sort(key=lambda row:row[0]) # Full serialized key ordering differs from tuple ordering (gb| versus gba|).
lines=['#pragma once\n// Public factual metadata, exact unique platform/title/alternate-name matches only.\nstruct StationFutureDetails {const char*key;StationGameDetails details;};\nstatic const StationFutureDetails stationFutureDetails[]={\n']
for key,id,p,r in unique:lines.append('{'+q(key)+',{'+q('launchbox:'+id)+','+q(p)+','+str(r)+'}},\n')
lines.append('};\nstruct StationMetadataPlatformAlias {const char*key;const char*platform;};\nstatic const StationMetadataPlatformAlias stationMetadataPlatformAliases[]={\n')
for key,p in sorted(platformAliases.items()):lines.append('{'+q(key)+','+q(p)+'},\n')
lines.append('};\n');(N/'station_future_metadata.h').write_text(''.join(lines),'utf8')
out=W/'metadata-xml';out.mkdir(exist_ok=True);coverage={}
for slug,platform in mapping.items():
 root=E.Element('gameList',{'metadataOnly':'true','platform':slug,'source':'LaunchBox Games Database','retrieved':'2026-10-06'})
 items=[g for g in selected.values() if g['Platform']==platform];ready=0;ratingMissing=0;playersMissing=0
 for g in sorted(items,key=lambda g:(g['Name'],int(g['DatabaseID']))):
  p,r,v=facts(g);game=E.SubElement(root,'game',{'id':'launchbox:'+g['DatabaseID']});E.SubElement(game,'name').text=g['Name'];E.SubElement(game,'sourceUrl').text='https://gamesdb.launchbox-app.com/Metadata.zip'
  if p:E.SubElement(game,'players',{'kind':'maximum_reported'}).text=p
  else:playersMissing+=1
  if r>=0:E.SubElement(game,'rating',{'kind':'community_average','votes':str(v),'scale':'0..1'}).text=f'{r/1000:.3f}'
  else:ratingMissing+=1
  if p and r>=0:ready+=1
  E.SubElement(game,'metadataStatus').text='complete' if p and r>=0 else 'source_missing_fields'
  if g.get('ReleaseType'):E.SubElement(game,'releaseType').text=g['ReleaseType']
 E.indent(root);E.ElementTree(root).write(out/(slug+'.xml'),encoding='utf-8',xml_declaration=True)
 coverage[slug]={'games':len(items),'complete':ready,'missingRatings':ratingMissing,'missingPlayers':playersMissing}
(W/'data/current-metadata-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),'utf8')
missing=[a for a in audit if not a['players'] or a['ratingThousandths']<0]
(W/'data/current-metadata-pending.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),'utf8')
summary={'publicSource':'https://gamesdb.launchbox-app.com/Metadata.zip','catalogItems':len(rows),'currentMissingPlayers':sum(not a['players'] for a in audit),'currentMissingRatings':sum(a['ratingThousandths']<0 for a in audit),'currentUniquePublicMatches':sum(a['publicMatch'] is not None for a in audit),'currentChanged':sum(a['before']!=[a['players'],a['ratingThousandths']] for a in audit),'futureLookupKeys':len(unique),'futureGames':len(selected),'platforms':coverage,'matching':'Unique exact normalized platform and title or published alternate name; punctuation and accents ignored; no fuzzy or cross-platform joins. XMLs are metadata-only, not downloadable catalog entries.'}
(W/'data/metadata-coverage.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:v for k,v in summary.items() if k!='platforms'},indent=2));print('Pending sample',[(m['platform'],m['name'],m['players'],m['ratingThousandths']) for m in missing[:16]])
