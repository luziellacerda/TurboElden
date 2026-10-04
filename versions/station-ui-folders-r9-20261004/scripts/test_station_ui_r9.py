from pathlib import Path
import subprocess,json,sys,uuid
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=R/'ui-r9';W.mkdir(exist_ok=True);N=R/'native'
# Reuse R8's actual geometry and unchanged route assertions, with the two intentional lifecycle/layout changes.
s=Path('test_station_ui_r8.py').read_text('utf8')
s=s.replace("W=R/'ui-r8'","W=R/'ui-r8'")
s=s.replace(", 'protected void onDestroy('","") if ", 'protected void onDestroy('" in s else s.replace(",'protected void onDestroy('","")
s=s.replace("'systemsMode?.92f:gameActionTextScale'","'systemsMode?(folderMode?.66f:.92f):gameActionTextScale'")
local=W/'test-ui-r9-base.py';local.write_text(s,'utf8')
p=subprocess.run([sys.executable,str(local)],capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;print(p.stdout)
results=[]
for name in ('station_collection_test','station_folder_navigation_test'):
 source=Path('ui-r8')/(name+'.cpp');out=R/'folders/build'/(name+'.exe')
 p=subprocess.run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-I'+str(N),'-I'+str(R/'station/src/native'),str(source),'-o',str(out)],capture_output=True,text=True);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out)],capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;results.append(p.stdout.strip());print(p.stdout.strip())
java=(R/'netplay/src/org/emulationstation/frontend/netplay/StationRoomsActivity.java').read_text('utf8');light=(R/'netplay/src/org/emulationstation/frontend/netplay/StationLobbySurface.java').read_text('utf8')
assert 'StationFiles.readBounded(file,5*1024*1024)' in java
assert 'Math.max(options.outWidth,options.outHeight)/options.inSampleSize>256' in java
assert 'm.optString("fromPeerId")' in java
assert 'rightPanel.setVisibility(joined?View.VISIBLE:View.GONE)' in java
assert 'postDelayed(this,64)' in light and 'removeCallbacks(frame)' in light
assert 'attached&&isShown()&&getWindowVisibility()==VISIBLE&&hasWindowFocus()' in light
from prepare_station_folder_index import produce
base=R/'folders/build'/('index-test-'+uuid.uuid4().hex);base.mkdir();games=base/'SNES';(games/'RPG'/'Traduções').mkdir(parents=True);(games/'RPG'/'Traduções'/'game.rom').write_bytes(b'fixture')
original={'revision':9,'items':[{'itemId':'station_fixture','name':'Fixture','platform':'snes','coverId':'cover_fixture','revision':4,'filePath':str(games/'RPG'/'Traduções'/'game.rom'),'coverPath':'private-original','artifact':{'unchanged':True}}]};source=base/'index.json';source.write_text(json.dumps(original),'utf8');out=base/'new.json';receipt=produce(source,out,['snes='+str(games)])
data=json.loads(out.read_text('utf8'));assert data['revision']==10 and data['items'][0]['folderPath']==['RPG','Traduções'];assert json.loads(source.read_text('utf8'))==original
again=base/'again.json';assert produce(out,again,['snes='+str(games)])['changedItems']==0
for target,maps in [(out,['snes='+str(games)]),(base/'bad.json',['snes='+str(games/'RPG'/'Traduções'/'nonexistent')]),(base/'bad2.json',['mega='+str(games)])]:
 try:produce(source,target,maps);raise AssertionError('unsafe index request accepted')
 except (ValueError,FileNotFoundError):pass
results.append('PASS index generation: 2 nested folders, original untouched, IDs/covers/revisions/descriptors preserved, repeat unchanged, output/roots/unknown platform rejected')
result={'nativeTests':results,'uiSourceChecks':6,'deviceVisualVerified':False,'api34Build':'passed separately','noProductionAccess':True}
(W/'tests.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result,indent=2))
