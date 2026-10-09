from pathlib import Path
import re,hashlib,subprocess,json
import argparse
parser=argparse.ArgumentParser(description="Verify room setup labels directly extracted from the shipped Activity source.")
parser.add_argument('--output',type=Path,required=True,help="Build directory on E: for isolated Java fixtures and classes")
parser.add_argument('--jdk',type=Path,default=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin'))
args=parser.parse_args()
version=Path(__file__).resolve().parent.parent
work=args.output.resolve()
work.mkdir(parents=True,exist_ok=True)
rel='java/netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java'
source=Path('\\\\?\\'+str(version/rel)).read_text('utf8')
def extract(name):
    match=re.search(r'    private static [^\n{]+\b'+name+r'\([^\n]*\)\s*\{',source)
    assert match,name
    start=match.start();i=match.end();depth=1
    while depth:
        c=source[i];i+=1
        if c=='{':depth+=1
        if c=='}':depth-=1
    return source[start:i]
assert 'setTitle("Modo da partida").setItems' not in source
assert '.setSingleChoiceItems(choices,chosen[0]' not in source
assert 'prepareRoom(setupProfile,setupCapacity,setupContext);' in source
assert 'createVerifiedRoom(game,capacity);' in source
assert 'chosen.profileSha256.equals(verified.profileSha256)' in source
assert 'java.util.Arrays.equals(chosen.allowed,verified.allowed)' in source
assert 'if(!sameRoomSetupProfile(chosen,verified)||!verified.permits(capacity))' in source
assert 'if(next!=2)clearRoomSetup();' in source
assert 'codePanel("Tudo pronto para jogar",client.name(confirmedItem),confirmedItem,true)' in source
assert 'codePanel(heading,message,item,true)' in source
checks=work/'room-setup-check';checks.mkdir(exist_ok=True)
info=version/'java/netplay-src/org/emulationstation/frontend/netplay/StationGamePlayerInfo.java'
(checks/'StationGamePlayerInfo.java').write_text(Path('\\\\?\\'+str(info)).read_text('utf8'),'utf8')
methods='\n'.join(extract(n) for n in ['profileInfo','setupModeName','roomSetupDescription','sameRoomSetupProfile'])
fixture='''package org.emulationstation.frontend.netplay;
class StationMultiplayerProfile {
 String mode,controllerProfile,itemId="item",contentSha256="content",engineId="engine",coreSha256="core",runtimeSha256="runtime",profileId="profile",profileSha256="profile-hash";
 final int[] allowed;final int maximumPlayers;
 StationMultiplayerProfile(String m,int...a){mode=m;allowed=a;maximumPlayers=a[a.length-1];controllerProfile=maximumPlayers>2?"snes-multitap-port2-v1":"standard-2p-v1";}
 boolean permits(int n){for(int c:allowed)if(c==n)return true;return false;}
}
public class RoomSetupCheck {
 static int checks;
 static void check(boolean result,String message){if(!result)throw new AssertionError(message);checks++;}
METHODS
 public static void main(String[] args)throws Exception{
  StationMultiplayerProfile battle=new StationMultiplayerProfile("battle-single",2,3,4);
  for(int count=2;count<=4;count++){
   String text=roomSetupDescription(battle,count);
   check(text.startsWith("Sala para "+count+" jogadores:"),"chosen room size");
   check(text.contains((count-1)+(count==2?" convidado.":" convidados.")),"guest count matches host");
   check(text.contains("marque MAN nos "+count+" controles"),"instructions use chosen controls");
   check(!text.contains("2, 3 ou 4"),"description not combined capacity");
  }
  StationMultiplayerProfile gap=new StationMultiplayerProfile("battle-team",2,4);
  check(roomSetupDescription(gap,3).startsWith("Escolha uma quantidade permitida"),"no invented intermediate capacity");
  check(roomSetupDescription(gap,5).startsWith("Escolha uma quantidade permitida"),"no invented fifth seat");
  check(roomSetupDescription(gap,4).contains("Configure os 4 participantes e as equipes"),"selected team participants");
  check(setupModeName(battle).equals("Batalha individual"),"explicit battle mode");
  check(setupModeName(gap).equals("Batalha em equipes"),"distinct team mode");
  StationMultiplayerProfile unknown=new StationMultiplayerProfile("two-player",2);
  check(setupModeName(unknown).equals("Partida para dois"),"server two-player title");
  check(!roomSetupDescription(unknown,2).contains("Todos jogam ao mesmo tempo"),"do not invent simultaneous participation");
  check(setupModeName(new StationMultiplayerProfile("race-mode",2)).equals("Modo aprovado"),"unknown technical identifier not exposed");
  check(!setupModeName(new StationMultiplayerProfile("two-player-a",2)).equals(setupModeName(new StationMultiplayerProfile("two-player-b",2))),"server modes A and B remain distinguishable");
  check(setupModeName(new StationMultiplayerProfile("adventure-coop",2)).equals("Aventura cooperativa"),"server adventure mode title");
  check(setupModeName(new StationMultiplayerProfile("championship-2p",2)).equals("Campeonato para dois"),"server championship title");
  check(setupModeName(new StationMultiplayerProfile("vs-race",2)).equals("Corrida entre jogadores"),"server race title");
  check(sameRoomSetupProfile(battle,new StationMultiplayerProfile("battle-single",2,3,4)),"identical verified profile accepted");
  for(String field:new String[]{"itemId","contentSha256","engineId","coreSha256","runtimeSha256","profileId","profileSha256","mode","controllerProfile"}){
   StationMultiplayerProfile changed=new StationMultiplayerProfile("battle-single",2,3,4);
   java.lang.reflect.Field f=StationMultiplayerProfile.class.getDeclaredField(field);f.setAccessible(true);f.set(changed,"changed");
   check(!sameRoomSetupProfile(battle,changed),"changed identity rejected: "+field);
  }
  check(!sameRoomSetupProfile(battle,new StationMultiplayerProfile("battle-single",2,4)),"changed allowed counts rejected");
  check(!sameRoomSetupProfile(battle,new StationMultiplayerProfile("battle-single",2,3)),"changed maximum rejected");
  check(!sameRoomSetupProfile(null,battle),"missing selection rejected");
  check(!sameRoomSetupProfile(battle,null),"missing verified profile rejected");
  System.out.println("PASS "+checks);
 }
}
'''.replace('METHODS',methods)
(checks/'RoomSetupCheck.java').write_text(fixture,'utf8')
jdk=args.jdk
r=subprocess.run([str(jdk/'javac.exe'),'-encoding','UTF-8','-d',str(checks),str(checks/'StationGamePlayerInfo.java'),str(checks/'RoomSetupCheck.java')],capture_output=True,text=True)
assert r.returncode==0,r.stderr
r=subprocess.run([str(jdk/'java.exe'),'-cp',str(checks),'org.emulationstation.frontend.netplay.RoomSetupCheck'],capture_output=True,text=True)
assert r.returncode==0,r.stderr
assert r.stdout.strip()=='PASS 38',r.stdout
source_bytes=Path('\\\\?\\'+str(version/rel)).read_bytes()
digest=hashlib.sha256(source_bytes).hexdigest()
receipt={'sourceSHA256':digest,'scope':'StationRoomsActivity presentation and selected-profile consistency','descriptionChecks':24,'selectionBindingChecks':14,'sourceGuards':10,'result':'passed','physicalUIVerified':False,'fivePlayerSupportAdded':False,'contractProfilesEnginesUnchanged':True,'limitations':['Extracted production methods with synthetic profile fixtures; not full Activity interaction or gameplay.','Current signed profile parser still rejects capacities above four.']}
(version/'evidence/room-setup-selection-checks.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(receipt,ensure_ascii=False))
