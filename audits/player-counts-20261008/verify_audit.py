import json,collections,hashlib,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent
doc=json.loads((H/'catalogo-cruzado.json').read_text(encoding='utf8'))
rows=doc['records'];visible=[r for r in rows if r['visible']];summary=doc['summary'];checks=0
def check(condition,message):
 global checks
 checks+=1
 assert condition,message
check(len(rows)==3734 and len(visible)==3479,'full revision19 inventory')
check(len({r['itemId'] for r in rows})==3734,'unique IDs')
check(dict(collections.Counter(r['group'] for r in visible))==summary['groupsByMaximum'],'group totals')
check(sum(summary['groupsByMaximum'].values())==3479,'no missing/double grouped rows')
check(sum(summary['statusCounts'].values())==3479,'all evidence states counted')
for r in rows:
 check(r['onlineAdmission'].startswith('not-evaluated'),'never grants seats')
 check(len(r['artifactSHA256'])==64,'artifact binding')
 if r['status']=='divergente':check(r['maximumForList'] is None and r['group']=='pendente','no silent conflict choice')
 if r['status']=='sem-dado':check(r['maximumForList'] is None,'no default two')
 for e in r['evidence']:
  check(1<=e['maximum']<=16 and len(e['sources'])>0,'evidence limits and attribution')
  for source in e['sources']:check(source['url'].startswith('https://'),'source URL')
ids={r['itemId']:r for r in rows}
sb2=ids['station_df50d575815ab105084a79d68e0c8fb3'];sb3=ids['station_46fe7356ab5cc63a1438f720b9c7ce2d']
check(sb2['maximumForList']==4,'SB2 maximum4')
check(sb3['maximumForList']==5 and sb3['manualModes'][0]['humanCountsDocumentedForOriginal']==[1,2],'SB3 campaign2 vs battle5')
check(4 in sb3['manualModes'][1]['humanCountsDocumentedForOriginal'],'SB3 includes four')
check(ids['station_3f28d41c9e666e0080106eda728e89da']['maximumForList']==1,'Hero is solo')
check(ids['cbd83be3e89456758ad7c165907abd12']['maximumForList']==3,'Vikings Genesis3')
check(ids['station_3f0267d082d3d99218768e6f4088960b']['maximumForList']==4,'DC original local4')
check(any(r['name']=='The Simpsons (2 Players World, set 1)' and r['conflict'] and r['maximumForList'] is None for r in visible),'arcade edition discrepancy retained')
page=(H/'jogadores.html').read_text(encoding='utf8')
check('__AUDIT_DATA__' not in page,'data embedded')
check('innerHTML' not in page,'untrusted catalog rendered as text')
check('fetch(' not in page,'standalone offline report')
check(len(json.loads((H/'divergencias.json').read_text(encoding='utf8'))['records'])==141,'conflict ledger complete')
result={'checks':checks,'passed':checks,'fullCatalog':len(rows),'visible':len(visible),'testScope':'audit data and report invariants only; no Android gameplay','artifactSHA256':hashlib.sha256((H/'catalogo-cruzado.json').read_bytes()).hexdigest()}
(H/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result))
