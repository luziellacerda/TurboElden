from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-game-indicator-r83-20261008')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r82')
def patch(p,a,b):
    s=p.read_text('utf8');assert s.count(a)==1,(p.name,a[:60],s.count(a));p.write_text(s.replace(a,b),'utf8')
def main():
    assert not WORK.exists();WORK.mkdir()
    sources=json.loads((BASE/'JAVA-SOURCE-MANIFEST.json').read_text())['sources']
    for n,d in sources.items():
        p=BASE/'java'/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==d
        out=WORK/'java'/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
    shutil.copytree(BASE/'carousel-inputs',WORK/'carousel-inputs')
    client=WORK/'java/client/src/java/org/emulationstation/frontend/station'
    p=client/'StationGamePlayerFacts.java'
    patch(p,'private static volatile Map<String,Fact> published=Collections.emptyMap();',
          'private static volatile Map<String,Fact> published=Collections.emptyMap();\n    private static volatile int generation;\n    public static int generation(){return generation;}\n    private static String diagnostic="";')
    patch(p,'published=Collections.unmodifiableMap(values);', '''published=Collections.unmodifiableMap(values);
        generation++;
        StringBuilder state=new StringBuilder("facts="+values.size());
        if(catalog!=null)for(int i=0;i<ENTRIES.length;i++)for(StationCatalog.Item item:catalog.items)if(ENTRIES[i].id.equals(item.itemId)){
            Entry e=ENTRIES[i];state.append(" row").append(i).append(":rev=").append(item.revision)
              .append(",title=").append(e.name.equals(item.name)).append(",platform=").append(e.platform.equals(item.platform))
              .append(",digest=").append(item.contentSha256.isEmpty()||e.contentDigest.isEmpty()||e.contentDigest.equals(item.contentSha256))
              .append(",invalidated=").append(invalidated.contains(item.itemId));
        }
        String next=state.toString();if(!next.equals(diagnostic)){diagnostic=next;android.util.Log.i("StationPlayers",next);}''')
    p=client/'StationCatalogPlayerEvidence.java'
    patch(p,'public static byte[] labelFor(String itemId) {','public static int generation(){return StationGamePlayerFacts.generation();}\n    public static byte[] labelFor(String itemId) {')
    d=WORK/'carousel-inputs/d0'
    p=d/'native_formation.h';patch(p,'systemsMode?.665f:.740f','systemsMode?.665f:.790f')
    p=d/'station_bottom_action_layout.h';s=p.read_text('utf8').replace('h*.740f','h*.790f').replace('h*.908f','h*.922f');p.write_text(s,'utf8')
    patch(p,'float playersWidth,float threeSpaces){','float playersWidth,float threeSpaces,int playerIcons=1){')
    patch(p,'float total=labelWidth+4*gap+stars+2*icon+2*small+countWidth+playersWidth;',
          'float people=icon*(playerIcons>0?1.f+(playerIcons-1)*.76f:0.f);\n float total=labelWidth+4*gap+stars+icon+people+2*small+countWidth+playersWidth;')
    patch(p,'out.person={x,r.y+(r.h-icon*scale)*.5f,icon*scale,icon*scale};x+=(icon+small)*scale;',
          'out.person={x,r.y+(r.h-icon*scale)*.5f,people*scale,icon*scale};x+=(people+small)*scale;')
    p=d/'native_skin.h';s=p.read_text('utf8').replace(':.908f',':.922f');p.write_text(s,'utf8')
    patch(p,'place((B*)p+0xcb8,coverSlot(p,0).x,h*(systemsMode?.814f:.865f),coverSlot(p,0).w,h*.026f,.68f,1);',
          'if(systemsMode)place((B*)p+0xcb8,coverSlot(p,0).x,h*.814f,coverSlot(p,0).w,h*.026f,.68f,1);\n else place((B*)p+0xcb8,w*.522f,stationTopbarActionY(h),w*.105f,h*.059f,.64f,1);')
    p=d/'native_netplay.h';s=p.read_text('utf8').replace('h*.908f','h*.922f').replace('h*.973f','h*.987f');p.write_text(s,'utf8')
    p=d/'native_info.h'
    patch(p,'static bool infoSinglePlayer;', 'static bool infoSinglePlayer;static int infoPlayerIcons;')
    patch(p,'infoSinglePlayer=strcmp(players,"1")==0;', '''infoSinglePlayer=strcmp(players,"1")==0;
  infoPlayerIcons=stationPlayerPictogramCount(players);''')
    patch(p,'float playersWidth=nativeInfoTextWidth(infoActionPlayersText,players,metadataScale);',
          'const char*playerCaption=infoPlayerIcons>0?"":players;\n float playersWidth=nativeInfoTextWidth(infoActionPlayersText,playerCaption,metadataScale);')
    patch(p,'labelWidth,countWidth,playersWidth,threeSpaces);','labelWidth,countWidth,playersWidth,threeSpaces,infoPlayerIcons);')
    patch(p,'fitGameTitleOneLine(infoActionPlayersText,players,','fitGameTitleOneLine(infoActionPlayersText,playerCaption,')
    patch(p,'''if(infoSinglePlayer)drawDetailsPerson(person.x,person.y,person.h,0x62F49Bff);
 else{drawDetailsPerson(person.x+person.w*.22f,person.y,person.h*.88f,0xA6DAB9ff);drawDetailsPerson(person.x,person.y+person.h*.18f,person.h*.76f,0x62F49Bff);}''',
          'for(int i=0;i<infoPlayerIcons;i++)drawDetailsPerson(person.x+i*person.h*.76f,person.y,person.h,0x62F49Bff);')
    patch(p,'bool changed=selectionChanged||oldVisibleCount!=visibleCount||oldRevision!=rev||oldW!=w||oldH!=h;',
          'static int oldPlayersGeneration=-1;int playersGeneration=systemsMode?oldPlayersGeneration:stationPlayersGeneration();\n bool changed=selectionChanged||oldPlayersGeneration!=playersGeneration||oldVisibleCount!=visibleCount||oldRevision!=rev||oldW!=w||oldH!=h;\n oldPlayersGeneration=playersGeneration;')
    p=d/'station_catalog_player_label.h'
    p.write_text(p.read_text('utf8')+'''
// Show human silhouettes only for a known simultaneous count; never turn alternation into seats.
static inline int stationPlayerPictogramCount(const char*value){
 if(!value)return 0;
 if(std::strcmp(value,"1")==0)return 1;
 if(value[0]>='2'&&value[0]<='5'&&std::strcmp(value+1," sim.")==0)return value[0]-'0';
 return 0;
}
''','utf8')
    print('R83 full source staged; native refresh bridge needs generation implementation.')
if __name__=='__main__':main()
