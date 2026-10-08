"""Apply the final game-action alignment and red download palette."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
src=WORK/'carousel-inputs/d0'
p=src/'station_bottom_action_layout.h';s=p.read_text('utf8')
start=s.index('// Left aligned: ten measured font spaces')
s=s[:start]+'''// Action text near the button center; rating/players anchored at the right rim.
struct StationPrimaryMetaLayout {
 StationActionRect label,stars,folder,count,person,players;float scale;
};
static StationPrimaryMetaLayout stationPrimaryMetaLayout(StationActionRect r,float inset,float labelWidth,float countWidth,float playersWidth,float threeSpaces,int playerIcons=1){
 if(r.w<=inset||r.h<=0)return {};
 float gap=threeSpaces,small=playersWidth>0?threeSpaces/3.f:0.f,star=r.h*.435f,stars=star*5.6f,icon=r.h*.32f;
 float available=r.w-inset-r.h*.16f;
 float people=icon*(playerIcons>0?1.f+(playerIcons-1)*.76f:0.f);
 float starsGap=gap*10.f/3.f;
 float group=stars+gap+people+small+playersWidth;
 float total=labelWidth+starsGap+group;
 if(available<=0||total<=0)return {};
 float scale=total>available?available/total:1.f;
 float right=r.x+r.w-r.h*.16f,x=right-group*scale;
 float labelX=r.x+r.w*.48f-labelWidth*scale*.5f;
 float limit=x-starsGap*scale-labelWidth*scale;
 if(labelX>limit)labelX=limit;
 if(labelX<r.x+inset)labelX=r.x+inset;
 StationPrimaryMetaLayout out{};out.scale=scale;
 out.label={labelX,r.y,labelWidth*scale,r.h};
 out.stars={x,r.y+(r.h-star*scale)*.5f,stars*scale,star*scale};x+=out.stars.w+gap*scale;
 out.person={x,r.y+(r.h-icon*scale)*.5f,people*scale,icon*scale};x+=(people+small)*scale;
 out.players={x,r.y,playersWidth*scale,r.h};return out;
}
''';p.write_text(s,'utf8')
p=src/'native_game_actions.h';s=p.read_text('utf8');needle=' if(confirming)a=0xFF5566ff;';assert needle in s
s=s.replace(needle,' if(slot==7)return {0xFF7885ff,0x7A1723ff,0x300A12ff}; // BAIXAR only.\n'+needle);p.write_text(s,'utf8')
p=ROOT/'build_native.py';s=p.read_text();s=s.replace("'native_formation.h','native_info.h'","'native_formation.h','native_game_actions.h','native_info.h'");p.write_text(s)
current=(WORK/'native').resolve();archived=(WORK/'native-eighth').resolve()
assert current.parent==WORK.resolve() and archived.parent==WORK.resolve() and not archived.exists()
current.rename(archived)
print('Download red; primary label near center; rating and players at the right')
