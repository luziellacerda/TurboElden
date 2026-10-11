"""Insert only the two verified offline mappings into existing class initializer."""
from pathlib import Path
import argparse, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
ANCHOR='    invoke-static {v0}, Ljava/util/Collections;->unmodifiableMap(Ljava/util/Map;)Ljava/util/Map;'
TYPE='Lorg/emulationstation/frontend/station/StationPlatforms$Platform;'
CTOR=TYPE+'-><init>(Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationPlatforms$1;)V'

def block(platforms):
 lines=['    # Offline-only PS3/PS4 catalogue aliases. All previous mappings stay intact.','    const/4 v3, 0x0','']
 for item in platforms:
  lines+=['    new-instance v1, '+TYPE,'    const-string v2, '+json.dumps(item['label']),'    const-string v4, '+json.dumps(item['folder']),'    invoke-direct {v1, v2, v4, v3}, '+CTOR]
  for alias in item['aliases']:
   lines+=['    const-string v2, '+json.dumps(alias),'    invoke-interface {v0, v2, v1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;']
  lines+=['']
 return '\n'.join(lines)+'\n'

def patch(raw):
 text=raw.decode('utf-8')
 if not text.startswith('.class public final Lorg/emulationstation/frontend/station/StationPlatforms;') or text.count(ANCHOR)!=1:raise ValueError('Unexpected platform class')
 if '    .locals 25' not in text.splitlines() or '<clinit>()V' not in text:raise ValueError('Current register layout changed')
 data=json.loads((ROOT/'catalog-platforms.json').read_text(encoding='utf-8'));addition=block(data['platforms'])
 for item in data['platforms']:
  for alias in item['aliases']:
   if any(line.endswith(', '+json.dumps(alias)) for line in text.splitlines()):raise ValueError('Alias already exists')
 result=text.replace(ANCHOR,addition+ANCHOR,1).encode('utf-8')
 if result.decode('utf-8').replace(addition,'',1).encode('utf-8')!=raw:raise ValueError('Other class methods changed')
 return result,addition

def main():
 p=argparse.ArgumentParser();p.add_argument('--smali',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
 raw=a.smali.read_bytes();out,addition=patch(raw);a.out.write_bytes(out)
 record={'sourceSha256':hashlib.sha256(raw).hexdigest(),'patchedSha256':hashlib.sha256(out).hexdigest(),'changedMethods':['StationPlatforms.<clinit>'],'exactInverse':True,'addedAliases':json.loads((ROOT/'catalog-platforms.json').read_text())['platforms'],'onlineApprovalAdded':False}
 a.receipt.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))
if __name__=='__main__':main()
