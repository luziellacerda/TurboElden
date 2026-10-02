from pathlib import Path
import hashlib,json,urllib.request,os
r=Path(__file__).resolve().parent
url='https://repo.maven.apache.org/maven2/org/json/json/20250517/json-20250517.jar'
manifest=json.loads((r/'tools/json-dependency.json').read_text(encoding='utf-8'))
cache=Path(os.environ.get('STATION_TOOLS_DIR',r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools'));cache.mkdir(parents=True,exist_ok=True)
path=cache/'json-20250517.jar'
if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==manifest['sha256']:
 print('Verified host JSON dependency already present')
else:
 data=urllib.request.urlopen(url,timeout=40).read()
 if hashlib.sha256(data).hexdigest()!=manifest['sha256']:raise RuntimeError('JSON dependency digest mismatch')
 path.write_bytes(data);print('Downloaded and verified host JSON dependency')
