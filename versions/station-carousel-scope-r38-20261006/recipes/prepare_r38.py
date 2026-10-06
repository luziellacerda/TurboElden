from pathlib import Path
import shutil, json, hashlib

BASE=Path(r'E:\ESTUDO APK\work\station-final-details-r37-20261005')
W=Path(r'E:\ESTUDO APK\work\station-carousel-scope-r38-20261006')
D=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
assert not W.exists(), 'Never overwrite an existing revision'
W.mkdir()
for folder in ('evidence','tests','temp','device-evidence','data'): (W/folder).mkdir()
shutil.copytree(BASE/'native',W/'native')
N=W/'native'
def edit(name,old,new):
    p=N/name;s=p.read_text('utf8');assert s.count(old)==1,(name,old[:100],s.count(old));p.write_text(s.replace(old,new),'utf8',newline='\n')

# Platform and collection videos retain the existing plain 2D/OES path.
edit('native_system_video720.h','#include "native_neogeocd_square.h"\n','')
edit('native_system_video720.h','  if(r.index==cursor&&neoSquareVideoAsset(asset))\n   useNeoSquareProgram(live>=0,mvp,live>=0?matrices[live]:nullptr,now);\n','')
edit('native_magazine.h','if(systemsMode||count!=4','if(systemsMode||folderMode||count!=4')
edit('neogeo_led_profile.h','static bool neoSquareVideoAsset(const char*asset){\n return asset&&strcmp(asset,"turbo-system-videos/720-neogeocd.mp4")==0;\n}\n','')
for name in ('native_neogeocd_square.h','neogeocd-square.glsl'):(N/name).unlink()

# Draw each installed ribbon with the exact card transform and catalog index,
# in the same painting order as its artwork. No selected-card/stopped-animation gate.
shutil.copy2(D/'native_formation.h',N/'native_formation.h')
edit('native_formation.h','struct CoverRect {float x,y,w,h;int index;};','struct CoverRect {float x,y,w,h;int index;};\nstatic void drawInstalledCover(void*,U,const CoverRect&);')
edit('native_formation.h','mappingCover=false;mappingHero=false;mappingPlatform=nullptr;','mappingCover=false;mappingHero=false;mappingPlatform=nullptr;\n if(pos>=0&&r.x+r.w>0&&r.x<w)drawInstalledCover(p,index,r);')
edit('native_carousel.cpp','drawHeaderGameStars(p);drawInstalledTag(p);','drawHeaderGameStars(p);')
(N/'native_installed_tag.h').write_text('''// Installed state belongs to the catalog item, not the selected cursor.
// Called immediately after each visible original card, preserving its z order.
// Reuse one text layout at the hero reference width and scale it with the card.
#include "station_installed_ribbon.h"
static void*installedTagText;
static void drawInstalledCover(void*p,U index,const CoverRect&cover){
 if(systemsMode||folderMode||modal(p)||at<int>(p,0x370)<2||cover.w<=0||cover.h<=0)return;
 void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);
 if(!begin||!end||end<begin||index>=(U)(end-begin)/0xe8||!begin[index*0xe8+0xa8])return;
 float reference=coverSlot(p,0).w;if(reference<=0)return;
 float scale=cover.w/reference;
 StationRibbonMesh<Vertex> ribbon;
 stationBuildInstalledRibbon(ribbon,reference,fn<unsigned(*)()>(0x39e240)());
 if(!ribbon.count)return;
 NativeMatrix faceLocal{{scale,0,0,0,0,scale,0,0,0,0,1,0,cover.x,cover.y,0,1}};
 NativeMatrix faceMatrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(&formationMatrix,&faceLocal);
 fn<void(*)(const void*)>(0x2e5640)(&faceMatrix);fn<void(*)(unsigned)>(0x2e52e8)(0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(ribbon.vertices,ribbon.count,4,5);
 float c=.707106781f*scale;
 NativeMatrix textLocal{{c,-c,0,0,c,c,0,0,0,0,1,0,cover.x,cover.y+ribbon.reach*scale,0,1}};
 NativeMatrix textMatrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(&formationMatrix,&textLocal);
 static void*owner;static float oldLength,oldHalf;
 if(owner!=p){owner=p;installedTagText=createInfoText(p,0xF5FFF9ffu);setLongText(installedTagText,"INSTALADO");oldLength=0;}
 if(oldLength!=ribbon.length||oldHalf!=ribbon.half){
  oldLength=ribbon.length;oldHalf=ribbon.half;
  fitInfoText(installedTagText,{ribbon.half*1.55f,-ribbon.half*.82f,ribbon.length-ribbon.half*3.10f,ribbon.half*1.64f},1.22f,1);
 }
 fn<void(*)(void*,void*)>(0x2d2dc4)(installedTagText,&textMatrix);
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
}
''','utf8')

# Collections: primary equals the focused cell; Back follows with an actual gap.
edit('station_bottom_action_layout.h',' return stationCompactActionRect({x+(back?width*.55f:0),y,width*(back?.45f:.52f),height});',' if(!(width>0&&height>0))return {};\n return {x+(back?width+height*.24f:0),y,back?height*3.f:width,height};')
edit('native_skin.h','systemsMode?(folderMode?.66f:.92f):gameActionTextScale','systemsMode?.92f:gameActionTextScale')
edit('native_info.h','static char platformActionLabel[192]="ABRIR";','static char platformActionLabel[1024]="ABRIR";')
edit('native_info.h',' auto button=stationCompactActionRect({w*.035f,h*.851f,coverSlot(p,0).w,bh});',' auto button=folderMode?stationCollectionAction(w*.035f,h*.851f,coverSlot(p,0).w,bh,false):stationCompactActionRect({w*.035f,h*.851f,coverSlot(p,0).w,bh});')
edit('native_info.h',' void*t=(B*)p+0xe00;const char*label=stationButtonFullName(key,title);\n if(nativeInfoTextWidth(t,label,.92f)>platformActionRect.w)label=stationButtonShortName(key,label);',' void*t=(B*)p+0xe00;char collectionLabel[1024]={};\n const char*label=stationButtonFullName(key,title);\n if(folderMode){\n  memcpy(collectionLabel,"ABRIR ",6);U n=strlen(title);if(n>1011)n=1011;\n  while(n&&((B)title[n]&0xc0)==0x80)n--;memcpy(collectionLabel+6,title,n);label=collectionLabel;\n }else if(nativeInfoTextWidth(t,label,.92f)>platformActionRect.w)label=stationButtonShortName(key,label);')
edit('native_info.h','if(n>187)n=187;','if(n>sizeof(platformActionLabel)-5)n=sizeof(platformActionLabel)-5;')
edit('native_info.h','heading=strData(folderItems+index*0xe8+0x18);describeFolder(index,folderText,sizeof(folderText));body=folderText;','heading=strData(folderItems+index*0xe8+0x18);describeFolder(index,folderText,sizeof(folderText));body=folderText;\n  preparePlatformActionLabel(p,folderPlatform,heading);')
edit('native_info.h','if(strcmp(systemInfos[i].key,key)==0)','if(presentationKeyEqual(systemInfos[i].key,key))')
edit('native_info.h','if(infoTitle&&(folderMode||(!systemsMode&&infoTitleViewport.w>0)))','if(infoTitle&&!systemsMode&&infoTitleViewport.w>0)')
edit('native_carousel.cpp','if(systemsMode&&(U)p-(U)gui==0xe00){if(folderMode)replacement="ABRIR";else{updateSystemInfo(gui);replacement=platformActionLabel;}}','if(systemsMode&&(U)p-(U)gui==0xe00){updateSystemInfo(gui);replacement=platformActionLabel;}')
edit('native_carousel.cpp','if(systemsMode&&!folderMode&&textOffset==0xe00)','if(systemsMode&&textOffset==0xe00)')

r=json.loads((BASE/'evidence/native-build-input.json').read_text('utf8'))
r['baseAPK']=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R37-20261005.apk'
r['baseSHA256']='75fd8b5806c6aa683796e1301fa8a92e3236f106a8837a0279b6d0ae094999fc'
r['baseNative']=str(BASE/'native')
r['baseSources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'native').iterdir() if p.is_file()}
r['command']=[s.replace(str(BASE),str(W)) for s in r['command']]
r['r24LedSourcesUnchanged']=False
(W/'evidence/native-build-input.json').write_text(json.dumps(r,indent=2),'utf8')
for name in ('test_ui_r37.cpp',):shutil.copy2(BASE/'tests'/name,W/'tests'/name)
s=(BASE/'build_r37.py').read_text('utf8').replace("r['baseSources'][n]!=r['overlaySources'][n]","n not in r['overlaySources'] or r['baseSources'][n]!=r['overlaySources'][n]")
(W/'build_r38.py').write_text(s,'utf8')
s=(BASE/'package_r37.py').read_text('utf8').replace(str(BASE),str(W)).replace('TurboStations-Visual-R37-20261005.apk','TurboStations-Carrossel-R38-20261006.apk')
s=s.replace(", 'lib/arm64-v8a/libstation_frontend.so':W/'frontend/build/libstation_frontend.so'",'')
s=s.replace("assert sha(replacements['lib/arm64-v8a/libstation_frontend.so'])=='d3bc8ef6fcd88a5cf16b577fdba83e5242a75f1d946a17019075ab56a9fe95ad'\n",'')
s=s.replace('Packaging R37: inline metadata with two-space gaps, equal secondary buttons and server display name','Packaging R38: cover-only Neo CD lighting, collection action, visible installed ribbons and system synopses')
(W/'package_r38.py').write_text(s,'utf8')
print('R38 source prepared',W)
