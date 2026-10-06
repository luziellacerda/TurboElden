from pathlib import Path
import shutil,json
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
shutil.copy2('r39_metadata_lookup.h',N/'station_metadata_lookup.h');shutil.copy2('r39_lottie_decode.h',N/'station_lottie_decode.h')
p=N/'native_info.h';s=p.read_text('utf8').replace('#include "station_game_details.h"','#include "station_metadata_lookup.h"').replace('infoDetails=findStationGameDetails(id);','infoDetails=findStationGameDetailsForGame(id,key,heading);');p.write_text(s,'utf8')
p=N/'native_theme_switch.h';s=p.read_text('utf8');a=s.index('static bool stationLottieDecode(');b=s.index('static void drawStationLottie',a);s=s[:a]+'#include "station_lottie_decode.h"\n'+s[b:];s=s.replace('if(r.w<=0||r.h<=0','if(asset<0||asset>1||r.w<=0||r.h<=0').replace('offsets[frame],offsets[frame+1])','offsets[frame],offsets[frame+1],offsets[frames])');p.write_text(s,'utf8')
shutil.copy2(W/'temp/lottie-render/lottie-web-LICENSE.md',W/'assets/lottie-web-MIT-LICENSE.md')
for name in ['current-metadata-audit.json','current-metadata-pending.json','metadata-coverage.json']:
 shutil.copy2(W/'data'/name,W/'metadata-xml'/name)
p=W/'package_r39.py';s=p.read_text('utf8').replace("(W/'metadata-xml').glob('*.xml')","(p for p in (W/'metadata-xml').iterdir() if p.is_file())");p.write_text(s,'utf8')
print('Native metadata fallback wired; bounded Lottie decoder and provenance ready.')
