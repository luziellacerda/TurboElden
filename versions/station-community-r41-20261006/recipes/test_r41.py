from pathlib import Path
import subprocess,os
W=Path(__file__).resolve().parent
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
JSON=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
S=W/'netplay-src/org/emulationstation/frontend/netplay';T=W/'tests/java';O=T/'classes';O.mkdir(exist_ok=True)
def run(args,label):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence'/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf8');print(p.stdout+p.stderr);p.check_returncode()
sources=[S/n for n in ('StationSocial.java','StationRoomState.java','StationInvitationCode.java','StationPlayerModel.java','StationLaunchPolicy.java')]+list(T.glob('*.java'))
run([J/'javac.exe','--release','8','-encoding','UTF-8','-cp',JSON,'-d',O,*sources],'java-test-compile')
for name in ('StationSocialTest','StationJoinPlayerTest','StationCompactLobbyTest','StationLaunchPolicyTest'):run([J/'java.exe','-cp',str(O)+';'+str(JSON),'org.emulationstation.frontend.netplay.'+name],name)
os.environ.update(DOTNET_CLI_HOME=str(W/'temp/dotnet'),TEMP=str(W/'temp'),TMP=str(W/'temp'),DOTNET_CLI_TELEMETRY_OPTOUT='1')
for name in ('server','server-regression'):run([r'C:\Program Files\dotnet\dotnet.exe','run','--project',W/'tests'/name/'Tests.csproj','-c','Release'],name+'-tests')
