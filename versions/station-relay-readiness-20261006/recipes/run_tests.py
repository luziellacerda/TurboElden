"""Run real TCP and Java/C# TLS relay tests in a new, private output directory."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,xml.sax.saxutils

p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
p.add_argument('--server-project',required=True)
p.add_argument('--java',default='java');p.add_argument('--javac',default='javac')
p.add_argument('--dotnet',default='dotnet')
a=p.parse_args();snapshot=Path(__file__).resolve().parent.parent
base=snapshot.parent/'station-community-r41-20261006'
out=Path(a.output).resolve()
if out.exists():raise SystemExit('Use a new output directory; no previous result is overwritten')
os.umask(0o077);out.mkdir(parents=True)
classes=out/'java';classes.mkdir()
env=dict(os.environ,DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_CLI_HOME=str(out/'dotnet-home'))
results={}
def run(args,name,timeout=120):
    r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace',env=env,timeout=timeout)
    (out/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
    print((r.stdout+r.stderr)[-3000:],flush=True)
    if r.returncode:raise SystemExit(f'{name} failed; private log: {out/(name+".log")}')
    results[name]={'passed':True}
    return r.stdout

src=snapshot/'netplay-src/org/emulationstation/frontend/netplay'
config=base.parent/'station-performance-offline-r16-20261005/client/src/java/org/emulationstation/frontend/station/StationConfig.java'
sources=list((base/'dependency-src').rglob('*.java'))+[config,src/'StationHostConnector.java',src/'StationRelayTunnel.java',base/'netplay-src/org/emulationstation/frontend/netplay/StationRelayTls.java',snapshot/'tests/StationHostConnectorTest.java',snapshot/'tests/RelayBridgeTests.java']
run([a.javac,'--release','8','-encoding','UTF-8','-d',classes,*sources],'java-compile')
connector=run([a.java,'-cp',classes,'org.emulationstation.frontend.netplay.StationHostConnectorTest'],'host-connector')
results['host-connector']=json.loads(connector.strip().splitlines()[-1])
project=out/'relay-tests';project.mkdir()
shutil.copyfile(snapshot/'tests/RelayIntegrationTests.cs',project/'Program.cs')
ref=xml.sax.saxutils.escape(str(Path(a.server_project).resolve()),{'"':'&quot;'})
(project/'Tests.csproj').write_text(f'<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup><ItemGroup><ProjectReference Include="{ref}"/></ItemGroup></Project>',encoding='utf8')
run([a.dotnet,'run','--project',project/'Tests.csproj','-c','Release','--',out,a.java,classes],'tls-relay',180)
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'results':results,
        'sourceFiles':{str(f.relative_to(snapshot if f.is_relative_to(snapshot) else base.parent)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources},
        'productionModified':False,'androidExecuted':False,'twoAndroidGameplayVerified':False,
        'scope':'Actual loopback sockets, pinned TLS, real Java tunnel and current C# relay, synthetic identities'}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:report[k] for k in ['passed','productionModified','androidExecuted','twoAndroidGameplayVerified']}))
