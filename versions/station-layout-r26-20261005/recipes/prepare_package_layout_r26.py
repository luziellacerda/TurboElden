from pathlib import Path
C=Path(__file__).resolve().parent
s=(C/'package_console_panel_r25.py').read_text('utf8')
s=s.replace('station-console-panel-r25-20261005','station-layout-r26-20261005').replace('TurboStations-Console-Players-R25-20261005.apk','TurboStations-Layout-R26-20261005.apk')
s=s.replace('Packaging R24 laser + compact players/stars row and maximum console','Packaging R26: stars by status, folder count, narrower bottom actions')
s=s.replace("O = W / 'TurboStations-Layout-R26-20261005.apk'","O = Path(r'G:\\BAKUP SISTEMA APP 03-10-2026\\apks-candidatos-visuais\\TurboStations-Layout-R26-20261005.apk')")
s=s.replace("assert shutil.disk_usage(W).free > B.stat().st_size * 2 + 32 * 1024 * 1024","assert shutil.disk_usage(W).free > B.stat().st_size + 32 * 1024 * 1024\nassert shutil.disk_usage(O.parent).free > B.stat().st_size + 32 * 1024 * 1024")
s=s.replace("Path(r'G:\\BAKUP SISTEMA APP 03-10-2026\\binarios-compilados\\station-layout-r26-20261005\\libturbo_carousel.so')", "(W/'libturbo_carousel.so')")
(C/'package_layout_r26.py').write_text(s,'utf8',newline='\n')
s=(C/'install_console_panel_r25.py').read_text('utf8').replace('station-console-panel-r25-20261005','station-layout-r26-20261005').replace('base to R25','base to R26')
(C/'install_layout_r26.py').write_text(s,'utf8',newline='\n')
import json
W=Path(r'E:\ESTUDO APK\work\station-layout-r26-20261005')
p=W/'evidence/native-build.json';r=json.loads(p.read_text('utf8'))
r['baseAPK']=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Console-Players-R25-20261005.apk'
p.write_text(json.dumps(r,indent=2)+'\n','utf8')
print('R26 recipes prepared')
