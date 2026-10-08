from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-player-facts-r82-20261008')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r81')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def patch(p,old,new):
 s=p.read_text(encoding='utf8');assert s.count(old)==1,(p.name,s.count(old),old[:60]);p.write_text(s.replace(old,new),encoding='utf8',newline='\r\n')
def main():
 assert not (WORK/'java').exists(),'Fresh working tree required'
 sources=json.loads((BASE/'JAVA-SOURCE-MANIFEST.json').read_text())['sources']
 for name,digest in sources.items():
  src=BASE/'java'/name;assert sha(src)==digest
  dst=WORK/'java'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 client=WORK/'java/client/src/java/org/emulationstation/frontend/station'
 shutil.copyfile(ROOT/'source-additions/StationGamePlayerFacts.java',client/'StationGamePlayerFacts.java')
 patch(client/'StationCatalogPlayerEvidence.java',
       'return result==null?UNKNOWN.clone():result.compact.getBytes(StandardCharsets.UTF_8);',
       'return result==null?StationGamePlayerFacts.labelFor(itemId):result.compact.getBytes(StandardCharsets.UTF_8);')
 patch(client/'StationCatalogPlayerEvidenceLoader.java',
       'StationCatalogPlayerEvidence.publish(bindings,confirmed);',
       'StationCatalogPlayerEvidence.publish(bindings,confirmed);\n        StationGamePlayerFacts.publish(catalog);')
 room=WORK/'java/netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java'
 patch(room,'    private final int green=',
       '    private String heroFactSummary="",heroFactDetail="",heroOnlineDetail="",heroOnlinePlayers="";\n    private final int green=')
 patch(room,'headerRating.setRating(-1);headerPlayers.setText("Jogadores a confirmar");',
       'heroFactSummary="";heroFactDetail="";heroOnlineDetail="";heroOnlinePlayers="";headerRating.setRating(-1);headerPlayers.setText("Jogadores a confirmar");')
 patch(room,'String name=item.name,platform=item.platform;',
       'String name=item.name,platform=item.platform;\n                final StationGamePlayerFacts.Fact facts=StationGamePlayerFacts.forItem(item);')
 patch(room,'subtitle.setText(name);gamePlatform.setText(platform);',
       'subtitle.setText(name);gamePlatform.setText(platform);heroFactSummary=facts==null?"":facts.summary;heroFactDetail=facts==null?"":facts.detail;renderHeroPlayerInfo();')
 patch(room,'headerPlayers.setText(b);headerPlayers.setContentDescription(b);if(createInfo!=null)createInfo.setText(d);',
       'heroOnlinePlayers=b;heroOnlineDetail=d;renderHeroPlayerInfo();')
 patch(room,'if(active&&generation==epoch&&target.equals(heroRequestId)&&createInfo!=null)createInfo.setText(StationOnlineClient.message(unavailable));',
       'if(active&&generation==epoch&&target.equals(heroRequestId)){heroOnlineDetail=StationOnlineClient.message(unavailable);renderHeroPlayerInfo();}')
 patch(room,'    private void loadHeroProfile(final String target){',
       '''    private void renderHeroPlayerInfo(){
        String label=heroFactSummary.isEmpty()?(heroOnlinePlayers.isEmpty()?"Jogadores a confirmar":"Online: "+heroOnlinePlayers):heroFactSummary;
        headerPlayers.setText(label);headerPlayers.setContentDescription(label);
        String online=heroOnlineDetail.isEmpty()?StationGamePlayerInfo.pending().detail:heroOnlineDetail;
        if(createInfo!=null)createInfo.setText((heroFactDetail.isEmpty()?"":heroFactDetail+"\\n\\n")+"Online: "+online);
    }
    private void loadHeroProfile(final String target){''')
 (ROOT/'evidence').mkdir(exist_ok=True)
 print('Prepared R82 from all '+str(len(sources))+' verified R81 sources, plus one descriptive helper.')
if __name__=='__main__':main()
