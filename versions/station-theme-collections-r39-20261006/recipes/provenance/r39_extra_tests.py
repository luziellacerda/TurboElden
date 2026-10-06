from pathlib import Path
import subprocess,json,shutil,xml.etree.ElementTree as ET,csv,hashlib
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native';T=W/'tests'
shutil.copy2('r39_extra_tests.cpp',T/'r39_extra_tests.cpp')
for name in ['current-metadata-audit.json','current-metadata-pending.json','metadata-coverage.json']:shutil.copy2(W/'data'/name,W/'metadata-xml'/name)
c=[r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-I',str(N),str(T/'r39_extra_tests.cpp'),'-o',str(T/'r39_extra_tests.exe')]
r=subprocess.run(c,capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence/extra-tests-compile.log').write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,r.stderr[-5000:]
r=subprocess.run([str(T/'r39_extra_tests.exe')]+[str(W/'data/lottie'/(k+'.rle')) for k in ['switch','stars','chatbot','online']],capture_output=True,text=True);print(r.stdout+r.stderr,flush=True);assert r.returncode==0
coverage=json.loads((W/'data/metadata-coverage.json').read_text('utf8'));total=0;checks=0
for p in (W/'metadata-xml').glob('*.xml'):
 root=ET.parse(p).getroot();assert root.attrib['metadataOnly']=='true';items=root.findall('game');assert len(items)==coverage['platforms'][p.stem]['games'];total+=len(items)
 for g in items:
  assert g.find('path') is None and g.find('downloadUrl') is None and g.find('name').text;checks+=1
  rating=g.find('rating');players=g.find('players')
  if rating is not None:assert 0<=float(rating.text)<=1 and int(rating.attrib['votes'])>0;checks+=1
  if players is not None:assert 0<int(players.text)<1000;checks+=1
assert total==coverage['futureGames']
rows=json.loads((W/'data/current-metadata-audit.json').read_text('utf8'));assert len(rows)==2212 and len({r['itemId'] for r in rows})==2212
facts=json.loads(Path(r'G:\BAKUP SISTEMA APP 03-10-2026\metadata-publica-20261006\game-facts.json').read_text('utf8'));facts={g['DatabaseID']:g for g in facts}
for row in rows:
 if row['publicMatch']:
  f=facts[row['publicMatch']];assert row['votes']==int(f.get('CommunityRatingCount','0'))
  if row['ratingSource']=='launchbox_community':assert row['votes']>0 and row['ratingThousandths']==round(float(f['CommunityRating'])*200)
 checks+=1
result={'passed':True,'native':r.stdout.strip(),'xmlAndSourceChecks':checks,'xmlPlatforms':len(coverage['platforms']),'metadataGames':total,'currentMissingPlayers':coverage['currentMissingPlayers'],'currentMissingRatings':coverage['currentMissingRatings'],'deviceTest':False}
(W/'evidence/lottie-metadata-tests.json').write_text(json.dumps(result,indent=2),'utf8');print(json.dumps(result,indent=2))
