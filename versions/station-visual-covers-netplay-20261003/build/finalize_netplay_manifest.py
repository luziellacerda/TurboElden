from pathlib import Path
import shutil
root=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
shutil.copy2(root/'netplay/native_netplay.h',root/'native/native_netplay.h')
p=root/'manifest-project/AndroidManifest.xml';s=p.read_text('utf-8')
start=s.index('<activity android:name="org.emulationstation.frontend.netplay.StationDolphinNetplayActivity"')
end=s.index('/>',start)+2
section=s[start:end]
assert (section.count('@style/td_Theme.Dolphin.Main')+section.count('@android:style/Theme.Material.NoActionBar'))==1
s=s[:start]+section.replace('@style/td_Theme.Dolphin.Main','@android:style/Theme.Material.NoActionBar')+s[end:]
p.write_text(s,'utf-8')
print('Finalized two internal networking Activities; existing Dolphin theme untouched.')
