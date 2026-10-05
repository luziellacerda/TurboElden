from pathlib import Path
import os,re,xml.etree.ElementTree as ET
W=Path(os.environ["STATION_N64_WORK"])
p=W/'merged/smali_classes36/paulscode/android/mupen64plusae/GalleryActivity.smali';s=p.read_text('utf8')
s,n=re.subn(r'    invoke-static \{[^}]+\}, Lpaulscode/android/mupen64plusae/task/SyncProgramsJobService;->syncProgramsForChannel\(Landroid/content/Context;J\)V','    # Station does not publish or scan Android TV channels.',s)
assert n==2;p.write_text(s,'utf8')
p=W/'merged/AndroidManifest.xml';t=ET.parse(p);A='{http://schemas.android.com/apk/res/android}';count=0
for provider in t.getroot().find('application').findall('provider'):
 if provider.get(A+'process')==':n64':
  for e in list(provider):
   if e.get(A+'name','').endswith('.ProfileInstallerInitializer'):provider.remove(e);count+=1
assert count==1;ET.register_namespace('android',A[1:-1]);t.write(p,encoding='utf-8',xml_declaration=True)
print('Final Android TV and profile adaptations applied. Rebuild resources/DEX next.')
