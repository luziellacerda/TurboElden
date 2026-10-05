from pathlib import Path
import os,subprocess,shutil,json
W=Path(r'E:\ESTUDO APK\work\station-netplay-20261004\internet-r12');T=W/'tests';T.mkdir(exist_ok=True)
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');D=r'C:\Program Files\dotnet\dotnet.exe'
os.environ.update(DOTNET_CLI_HOME=r'E:\StationNetplayWork\dotnet-home',TEMP=str(T),TMP=str(T),NUGET_PACKAGES=str(W/'nuget'))
def run(args,name):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(T/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');print((p.stdout+p.stderr)[-5000:],flush=True);assert p.returncode==0,name
project=W/'server-full/src/TurboRamaSuiteOnlineServer/TurboRamaSuiteOnlineServer.csproj'
for name in ['StationRelay.cs','StationOnline.cs','StationOnlineEndpoints.cs','StationOnlineRegistration.cs']:shutil.copyfile(W/'server'/name,project.parent/name)
for name in ['RelayIntegrationTests.cs','RelayBridgeTests.java']:shutil.copyfile(Path(name),T/name)
for name,source in [('regression','Program.cs'),('http','HttpTests.cs')]:
 out=T/name;out.mkdir(exist_ok=True);shutil.copyfile(Path(r'E:\StationNetplayWork\server')/source,out/source)
 (out/'Tests.csproj').write_text(f'<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup><ItemGroup><ProjectReference Include="{project}"/></ItemGroup></Project>','utf8')
 run([D,'run','--project',out/'Tests.csproj','-c','Release'],name)
import shutil
if (T/'org').exists():shutil.rmtree(T/'org') # Only disposable test classes within this fixed test directory.
run([J/'javac.exe','-encoding','UTF-8','--release','8','-cp',W/'app-build/netplay-internet.jar','-d',T,T/'RelayBridgeTests.java'],'javac-tests')
(T/'Tests.csproj').write_text(f'<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup><ItemGroup><Compile Include="RelayIntegrationTests.cs"/><ProjectReference Include="{project}"/></ItemGroup></Project>','utf8')
cp=str(T)+';'+str(W/'app-build/netplay-internet.jar')+';'+r'E:\ESTUDO APK\work\station-library-r10-build-20261004\station-client.jar'
run([D,'run','--project',T/'Tests.csproj','-c','Release','--',T,J/'java.exe',cp],'relay-integration')
(T/'result.json').write_text(json.dumps({'passed':True,'regressionLog':'regression.log','signedHttpLog':'http.log','tlsBridgeLog':'relay-integration.log','productionDeployed':False,'androidGameplay':False},indent=2)+'\n','utf8')
