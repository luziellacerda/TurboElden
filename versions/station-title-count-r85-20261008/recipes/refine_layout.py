from pathlib import Path
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008');D=WORK/'carousel-inputs/d0';ROOT=Path(__file__).resolve().parents[1]
def edit(n,a,b):
 p=D/n;s=p.read_text();assert a in s,(n,a[:80]);p.write_text(s.replace(a,b),encoding='utf8')
edit('native_formation.h','systemsMode?.665f:.800f','systemsMode?.665f:.865f')
edit('native_formation.h','systemsMode?.135f:.105f','systemsMode?.135f:.040f')
edit('native_formation.h','CoverRect result{};result.y=top;','CoverRect result{};float move=d<0?0:d>1?1:d*d*(3-2*d);result.y=top+(!systemsMode?h*.065f*move:0);')
edit('station_collection_settings_layout.h',' return {headerX,0.f,width,height};',' if(!systems)return {w*.8775f-h*.05f,h*.455f,h*.10f,h*.075f};\n return {headerX,0.f,width,height};')
edit('native_lottie_gear.h','float w=oldRadius*6.54f,h=w*stationLottie_chatbot_height/stationLottie_chatbot_width;','float w=systemsMode?oldRadius*6.54f:at<float>(skinTopOwner,0x1418),h=w*stationLottie_chatbot_height/stationLottie_chatbot_width;')
edit('native_skin.h','bounds(p,0x698,w*.634f,stationTopbarActionY(h),h*.059f,h*.059f);','bounds(p,0x698,systemsMode?w*.634f:contentLeft(p),stationTopbarActionY(h),h*.059f,h*.059f);')
edit('native_skin.h','bounds(p,0x1420,w*.055f,h*.008f,w*.17f,h*.066f);','float avatarX=systemsMode?w*.055f:contentLeft(p)+h*.059f+w*.012f;\n bounds(p,0x1420,avatarX,h*.008f,systemsMode?w*.17f:w*.706f-avatarX,h*(systemsMode?.066f:.058f));')
edit('native_skin.h','float nameX=w*.055f+h*.066f+w*.012f;','float nameX=systemsMode?w*.055f+h*.066f+w*.012f:avatarX+h*.058f+w*.012f;')
edit('native_skin.h','if(profile)place(profile,nameX,h*.018f,w*.115f,h*.05f,.72f,0);','if(profile)place(profile,nameX,h*(systemsMode?.018f:.012f),systemsMode?w*.115f:w*.706f-nameX,h*.05f,.72f,0);')
edit('native_skin.h','float edge=stationTopbarBottom(height);rect(0,0,width,edge,0x080C09f5);rect(0,edge,width,1.5f,0x28E65870);','float edge=stationTopbarBottom(height),start=systemsMode?0:contentLeft(gui)-width*.012f;rect(start,0,width-start,edge,0x080C09f5);rect(start,edge,width-start,1.5f,0x28E65870);')
edit('native_skin.h','{y=stationTopbarBottom(height);h=1.5f;}','{y=stationTopbarBottom(height);h=1.5f;if(!systemsMode){x=contentLeft(gui)-width*.012f;w=width-x;}}')
edit('native_profile_name.h','StationInfoRect area{w*.055f+h*.066f+w*.012f,h*.018f,w*.115f,h*.05f};','float avatarX=systemsMode?w*.055f:contentLeft(gui)+h*.059f+w*.012f;\n float nameX=systemsMode?w*.055f+h*.066f+w*.012f:avatarX+h*.058f+w*.012f;\n StationInfoRect area{nameX,h*(systemsMode?.018f:.012f),systemsMode?w*.115f:w*.706f-nameX,h*.05f};')
edit('native_profile_name.h','bounds(gui,0x1420,w*.055f,h*.008f,settingsX-w*.067f,h*.066f);','bounds(gui,0x1420,avatarX,h*.008f,systemsMode?settingsX-w*.067f:w*.706f-avatarX,h*(systemsMode?.066f:.058f));')
edit('native_info.h','static char infoActionCount[48]={},infoActionPlayers[96]={};','static char infoActionCount[96]={},infoActionPlayers[96]={};')
edit('native_info.h','static char count[48]={},players[96]={};','static char count[96]={},players[96]={};')
edit('native_info.h',"char countLabel[48]={},digits[24]={};U remainingCount=visibleCount;int length=0;\n  do{digits[length++]=(char)('0'+remainingCount%10);remainingCount/=10;}while(remainingCount&&length<23);\n  for(int i=0;i<length;i++)countLabel[i]=digits[length-i-1];",'''char countLabel[96]={};unsigned countLength=0;
  auto appendNumber=[&](U number){char digits[24]={};unsigned n=0;do{digits[n++]=(char)('0'+number%10);number/=10;}while(number&&n<23);while(n)countLabel[countLength++]=digits[--n];};
  appendNumber((U)cursor+1);memcpy(countLabel+countLength," / ",3);countLength+=3;
  appendNumber(visibleCount);memcpy(countLabel+countLength," jogos",7);''')
edit('native_info.h','const float available=w*.965f-left,reserved=gap+icon+inner+countWidth;','const float available=w*.815f-left,reserved=gap+icon+inner+countWidth;')
# A closed search chip uses the gap below thumbnails instead of covering the profile.
edit('native_search_download.h','bounds(p,0x6a8,x,y,bw,bh);bounds(p,0x6b8,x+bw-bh,y,bh,bh);','if(!active&&!systemsMode){x=contentLeft(p);y=h*.405f;bw=w*.45f;bh=h*.042f;}\n bounds(p,0x6a8,x,y,bw,bh);bounds(p,0x6b8,x+bw-bh,y,bh,bh);')
edit('native_profile_name.h','static void*owner;static float oldW,oldH,textW,textH;','static void*owner;static float oldW,oldH,textW,textH,profileScale=.72f;')
edit('native_profile_name.h','fitGameTitleOneLine(text,*name?name:"JOGADOR",area,.72f);','float desired=nativeInfoTextWidth(text,*name?name:"JOGADOR",.72f);\n  profileScale=!systemsMode&&desired>area.w?.72f*area.w/desired:.72f;if(profileScale<.46f)profileScale=.46f;\n  fitGameTitleOneLine(text,*name?name:"JOGADOR",area,profileScale);')
edit('native_profile_name.h','float line=at<float>(text,0x58)*.72f;','float line=at<float>(text,0x58)*profileScale;')
edit('native_profile_name.h','0,0,.72f,0);textW=','0,0,profileScale,0);textW=')
edit('native_profile_name.h','float shownWidth=at<float>(text,0x54)*.72f;','float shownWidth=at<float>(text,0x54)*profileScale;')
# Keep the authored input/build declaration exact.
p=ROOT/'build_native.py';s=p.read_text();s=s.replace("['native_formation.h','native_info.h','native_skin.h','station_bottom_action_layout.h','station_compact_topbar.h']","['native_formation.h','native_info.h','native_lottie_gear.h','native_profile_name.h','native_search_download.h','native_skin.h','station_bottom_action_layout.h','station_collection_settings_layout.h','station_compact_topbar.h']");p.write_text(s)
p=ROOT/'recipes/package_candidate.py';s=p.read_text().replace("BASE_SHA='e42a3dc15d2badcad489520b00d6115b4e0047c9998393760c244c665f548235'","BASE_SHA='1818a502a40f2718f92e5e51a0bc42bb070fbd1875a1efc0237a7eba767f296e'");p.write_text(s)
p=ROOT/'recipes/refresh_candidate.py';s=p.read_text().replace("assert sha(apk)=='e42a3dc15d2badcad489520b00d6115b4e0047c9998393760c244c665f548235'","assert sha(apk)=='1818a502a40f2718f92e5e51a0bc42bb070fbd1875a1efc0237a7eba767f296e'");a=s.index('for rel in [');b=s.index('shutil.copyfile(WORK/',a);s=s[:a]+'''for rel in ['carousel-inputs/'+n for n in read(ROOT/'evidence/native-build.json')['changedSources']]+['carousel-command.json']:
 '''+s[b:];p.write_text(s)
for n in ['native','package']:
 src=(WORK/n).resolve();dst=(WORK/(n+'-third')).resolve();assert src.parent==WORK.resolve() and dst.parent==WORK.resolve() and not dst.exists();src.rename(dst)
print('Game header moved to search/avatar/name; compact settings over console; current/total count; taller hero')
