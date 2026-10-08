from pathlib import Path
import shutil
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r84')
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
assert not WORK.exists();WORK.mkdir()
for folder in ['java','carousel-inputs']:shutil.copytree(BASE/folder,WORK/folder)
p=WORK/'carousel-inputs/d0'
def edit(name,a,b):
 f=p/name;s=f.read_text();assert a in s,(name,a[:70]);f.write_text(s.replace(a,b),encoding='utf8')
edit('station_compact_topbar.h','h*.085f','h*.075f')
edit('station_compact_topbar.h','h*.014f','h*.008f')
edit('native_skin.h','else place((B*)p+0xcb8,w*.522f,stationTopbarActionY(h),w*.105f,h*.059f,.64f,1);','// Game counter is painted beside the title; never beside search.\n else place((B*)p+0xcb8,0,0,0,0,.64f,1);')
edit('native_info.h','static void*infoListCountText;static StationInfoRect infoListCountViewport{};','static void*infoListCountText;static StationInfoRect infoListCountViewport{},infoListFolder{};')
edit('native_info.h','infoPlayersViewport={};infoListCountViewport={};infoHeaderStars={};','infoPlayersViewport={};infoListCountViewport={};infoListFolder={};infoHeaderStars={};')
edit('native_info.h','''  // Title alone above the synopsis; counts remain in the primary action.
  infoTitleViewport={left,infoViewport.y,w*.965f-left,h*.076f};
  fitGameTitleOneLine(infoTitle,heading,infoTitleViewport);''','''  // One measured line: title, five font spaces, folder and visible game count.
  const float rowHeight=h*.076f,icon=h*.039f;
  const float countWidth=nativeInfoTextWidth(infoListCountText,countLabel,stationGameMetadataScale);
  const float gap=nativeInfoTextWidth(infoTitle,"     ",stationGameMetadataScale);
  const float inner=nativeInfoTextWidth(infoTitle," ",stationGameMetadataScale);
  const float available=w*.965f-left,reserved=gap+icon+inner+countWidth;
  infoTitleViewport={left,infoViewport.y,available-reserved,rowHeight};
  float titleWidth=fitGameTitleOneLine(infoTitle,heading,infoTitleViewport);
  float folderX=left+titleWidth+gap;
  infoListFolder={folderX,infoViewport.y+(rowHeight-icon)*.5f,icon,icon};
  infoListCountViewport={folderX+icon+inner,infoViewport.y,countWidth+.5f,rowHeight};
  fitGameTitleOneLine(infoListCountText,countLabel,infoListCountViewport,stationGameMetadataScale);''')
edit('native_info.h','  infoPlayersViewport={};infoListCountViewport={};','  infoPlayersViewport={};')
edit('native_info.h','static bool isSystemInfoText(void*t){return t==infoActionCountText','static bool isSystemInfoText(void*t){return (gui&&!systemsMode&&t==(B*)gui+0xcb8)||t==infoActionCountText')
edit('native_info.h',' float countWidth=nativeInfoTextWidth(infoActionCountText,count,metadataScale);',' float countWidth=0; // Folder/count now belongs to the title row.')
edit('native_info.h',' fitGameTitleOneLine(infoActionCountText,count,{layout.count.x,layout.count.y,layout.count.w+.1f,layout.count.h},metadataScale*layout.scale);',' // No duplicate folder/count inside JOGAR or BAIXAR.')
edit('native_info.h',' auto folder=infoPrimaryMeta.folder;drawActionIcon(folder.x,folder.y,folder.h,6,0x62F49Bff);',' // Player pictograms remain beside the stars.')
edit('native_info.h',' fn<void(*)(void*,void*)>(0x2d2dc4)(infoActionCountText,&formationMatrix);','')
edit('native_info.h',' if(infoDescription&&infoViewport.w>0&&infoViewport.h>0){',''' if(!systemsMode&&!folderMode&&infoGameDetailsVisible&&infoListFolder.w>0){
  fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
  auto f=infoListFolder;drawActionIcon(f.x,f.y,f.h,6,0x62F49Bff);
  clipSynopsis(infoListCountViewport);fn<void(*)(void*,void*)>(0x2d2dc4)(infoListCountText,&formationMatrix);fn<void(*)()>(0x2e2aac)();
 }
 if(infoDescription&&infoViewport.w>0&&infoViewport.h>0){''')
edit('station_bottom_action_layout.h',' float total=labelWidth+4*gap+stars+icon+people+2*small+countWidth+playersWidth;',' float total=labelWidth+3*gap+stars+people+small+playersWidth;')
edit('station_bottom_action_layout.h',' out.folder={x,r.y+(r.h-icon*scale)*.5f,icon*scale,icon*scale};x+=(icon+small)*scale;\n out.count={x,r.y,countWidth*scale,r.h};x+=out.count.w+gap*scale;',' // Folder/count are rendered next to the title, not in this action.')
print('Prepared R85 from the complete canonical R84 source; four native headers changed.')

# Physical verification: explicit count text must be visible when manually rendered.
edit('native_info.h','fn<void(*)(void*,bool)>(0x277228)(infoListCountText,false);','fn<void(*)(void*,bool)>(0x277228)(infoListCountText,infoGameDetailsVisible);')

# Follow-up: five measured spaces after the action icon, ten before rating.
edit('native_info.h','r.h*.79f+threeSpaces,labelWidth,countWidth,playersWidth,threeSpaces,infoPlayerIcons','r.h*.79f+threeSpaces*5.f/3.f,labelWidth,countWidth,playersWidth,threeSpaces,infoPlayerIcons')
edit('native_info.h','Text follows by three real font spaces.','Text follows by five real font spaces.')
edit('station_bottom_action_layout.h','six measured font spaces','ten measured font spaces')
edit('station_bottom_action_layout.h','float total=labelWidth+3*gap+stars+people+small+playersWidth;','float starsGap=gap*10.f/3.f;\n float total=labelWidth+starsGap+gap+stars+people+small+playersWidth;')
edit('station_bottom_action_layout.h','x+=out.label.w+2*gap*scale;','x+=out.label.w+starsGap*scale;')
# Move the hero up while preserving width, footer alignment and the ribbon.
edit('native_formation.h','float bigH=h*(systemsMode?.665f:.790f),bigW=systemsMode?bigH:bigH*.828f,bigX=w*(systemsMode?.035f:.025f),top=h*(systemsMode?.135f:.115f);','float bigH=h*(systemsMode?.665f:.800f),bigW=systemsMode?bigH:h*.790f*.828f,bigX=w*(systemsMode?.035f:.025f),top=h*(systemsMode?.135f:.105f);')
