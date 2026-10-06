from pathlib import Path
import shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
shutil.copy2('r39_root_label.h',N/'station_root_label.h')
p=N/'native_info.h';s=p.read_text('utf8').replace('#include "station_info_layout.h"','#include "station_info_layout.h"\n#include "station_root_label.h"').replace('static char platformActionLabel[1024]','static int platformActionAlignment=1;\nstatic char platformActionLabel[1024]')
s=s.replace(' fitInfoText(t,platformActionRect,.92f,1);',''' platformActionAlignment=folderMode?1:0;
 if(!folderMode){float three=nativeInfoTextWidth(t,"   ",.92f);float measured=nativeInfoTextWidth(t,platformActionLabel,.92f);platformActionRect=stationMainButtonText(platformActionRect,measured,three);}
 fitInfoText(t,platformActionRect,.92f,platformActionAlignment);''')
s=s.replace('static float x=-1,y=-1,width=-1,height=-1;if(row.x!=x||','static void*labelOwner;static float x=-1,y=-1,width=-1,height=-1;if(labelOwner!=infoRatingUnknown||row.x!=x||').replace('height=row.h;fitInfoText(infoRatingUnknown','height=row.h;labelOwner=infoRatingUnknown;fitInfoText(infoRatingUnknown')
p.write_text(s,'utf8')
p=N/'native_carousel.cpp';s=p.read_text('utf8').replace('fitInfoText(p,platformActionRect,.92f,1)','fitInfoText(p,platformActionRect,.92f,platformActionAlignment)');p.write_text(s,'utf8')
print('Main platform name shifted left by three native measured spaces, clamped before the icon; collection labels unchanged.')
