from pathlib import Path
import subprocess,os,json,hashlib
W=Path(r'E:\ESTUDO APK\work\station-online-recovery-r34-20261005');T=W/'tests/relay';T.mkdir(exist_ok=True)
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004\internet-r12\tests')
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');D=Path(r'C:\Program Files\dotnet\dotnet.exe')
os.environ.update(TEMP=str(T),TMP=str(T),DOTNET_CLI_HOME=r'E:\StationNetplayWork\dotnet-home')
logs={}
def run(cmd,name):
 r=subprocess.run([str(v) for v in cmd],cwd=T,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=90)
 (W/'evidence'/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');print((r.stdout+r.stderr)[-1800:],flush=True);r.check_returncode();logs[name]=r.stdout.strip()
for label in ['regression','http']:run([D,R/label/'bin/Release/net8.0/Tests.dll'],'relay-'+label)
jar=W/'build/final/netplay.jar'
run([J/'javac.exe','-encoding','UTF-8','--release','8','-cp',jar,'-d',T,R/'RelayBridgeTests.java'],'relay-javac')
classpath=str(T)+';'+str(jar)+';'+r'E:\ESTUDO APK\work\station-library-r10-build-20261004\station-client.jar'
run([D,R/'bin/Release/net8.0/Tests.dll',T,J/'java.exe',classpath],'relay-integration')
(W/'evidence/relay-tests.json').write_text(json.dumps({'passed':True,'scope':'Isolated C# real room service and WSS relay plus current R29 production Java tunnel; synthetic identities and TCP endpoints. Not production network or Android gameplay.','logs':logs,'javaJarSHA256':hashlib.sha256(jar.read_bytes()).hexdigest()},indent=2)+'\n','utf8')
