from pathlib import Path
import json,hashlib,subprocess,datetime,os
W=Path(r'E:\ESTUDO APK\work\station-game-details-r23-20261005')
B=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005')
N=W/'native';E=W/'evidence';os.environ['TEMP']=os.environ['TMP']=str(W)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(cmd,name):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace')
 (E/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-4000:]
 return r.stdout.strip()
base=json.loads((W/'evidence/base-overlay.json').read_text('utf8'))
changes=[k for k,v in base['files'].items() if sha(N/k)!=v]
assert changes==['native_info.h'],changes
extra=sorted(p.name for p in N.iterdir() if p.name not in base['files'])
assert extra==['station_game_details.h','station_game_panel_layout.h'],extra
prior=json.loads((B/'evidence/integration.json').read_text('utf8'))
cmd=[str(x).replace(str(B/'native/native_carousel.cpp'),str(N/'native_carousel.cpp')).replace(str(B/'libturbo_carousel.so'),str(W/'libturbo_carousel.so')) for x in prior['command']]
# Inputs include legacy49 posters AND the three new Neo Geo collection posters.
assert str(B/'neogeo_previews.o') in cmd
print('Compiling R23 with verified W22 base and 52 preserved preview objects',flush=True)
run(cmd,'android-compile')
r={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseRevision':'R22',
 'baseAPKHash':'f7dfc90f0614644548f16cfc7a518ba869589c815adacd6adb9f411f6a97de29',
 'command':cmd,'changedSources':changes,'addedSources':extra,'soSHA256':sha(W/'libturbo_carousel.so'),
 'soBytes':(W/'libturbo_carousel.so').stat().st_size,'androidCompile':True,
 'overlaySources':{p.name:sha(p) for p in N.iterdir() if p.is_file()},
 'metadataEvidence':'game-details-build.json','panelTests':'../tests/panel_layout_result.json'}
(E/'native-build.json').write_text(json.dumps(r,indent=2),'utf8')
print(json.dumps({k:r[k] for k in ['soSHA256','soBytes','changedSources','addedSources']},indent=2),flush=True)
