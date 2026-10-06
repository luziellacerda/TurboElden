from pathlib import Path
import subprocess,json,hashlib,xml.etree.ElementTree as ET,os
W=Path(__file__).resolve().parent;T=W/'tests';N=W/'native';os.environ['TEMP']=os.environ['TMP']=str(W/'temp');results={}
for name in ('r39_tests','r39_jni_tests','navigation','test_ui_r37','r39_search_tests','r39_extra_tests','test_ribbons'):
 cmd=[r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-include','initializer_list','-I',str(N),'-I',str(T),str(T/(name+'.cpp')),'-o',str(T/(name+'.exe'))]
 p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace');assert p.returncode==0,p.stderr
 args=[str(T/(name+'.exe'))]
 if name=='r39_extra_tests':args += [str(W/'data/lottie'/(k+'.rle')) for k in ('switch','stars','chatbot','online')]
 p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace');assert p.returncode==0,p.stdout+p.stderr
 results[name]=p.stdout;print(p.stdout,flush=True)
c=json.loads((W/'data/metadata-coverage.json').read_text('utf8'));count=0
for p in (W/'metadata-xml').glob('*.xml'):
 root=ET.parse(p).getroot();assert root.attrib['metadataOnly']=='true';games=root.findall('game');assert len(games)==c['platforms'][p.stem]['games']
 for g in games:
  assert g.find('path') is None and g.find('downloadUrl') is None
  rating=g.find('rating');players=g.find('players')
  if rating is not None:assert 0<=float(rating.text)<=1 and int(rating.attrib['votes'])>0
  if players is not None:assert 0<int(players.text)<1000
 count+=len(games)
assert count==c['futureGames'];results['XML games']=count
(W/'evidence/restored-tests.json').write_text(json.dumps(results,indent=2),'utf8')
