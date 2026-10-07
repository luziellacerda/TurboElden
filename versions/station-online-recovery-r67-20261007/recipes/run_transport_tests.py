"""Run real private TLS .NET/Java interop; kill only the subprocess owned by this recipe."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess, time
from source_composition import verified_composition, sha

p=argparse.ArgumentParser()
for name in ('server-root','java-build','android-jar','json-jar','jdk','output'):p.add_argument('--'+name,required=True)
a=p.parse_args();snapshot=Path(__file__).resolve().parent.parent
out=Path(a.output).resolve();build=Path(a.java_build).resolve();server=Path(a.server_root).resolve();jdk=Path(a.jdk).resolve()
if out.exists():raise SystemExit('Use a new isolated test output directory')
j=json.loads((build/'evidence/build.json').read_text())
if not j['dexBuilt'] or j['sourceHashes']!={name:sha(path) for name,path in verified_composition().items()}:raise SystemExit('Test the exact DEX source composition')
if sha(a.android_jar)!='6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad' or sha(a.json_jar)!='3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796':raise SystemExit('Exact JVM test dependencies required')
out.mkdir();classes=out/'classes';classes.mkdir()
cp=os.pathsep.join(map(str,[a.json_jar,a.android_jar,build/'client.jar',build/'rooms.jar']))
suffix='.exe' if os.name=='nt' else ''
subprocess.run([str(jdk/('bin/javac'+suffix)),'--release','17','-cp',cp,'-d',str(classes)]+[str(path) for path in sorted((snapshot/'tests').glob('*.java'))],check=True)
java=[str(jdk/('bin/java'+suffix)),'-cp',str(classes)+os.pathsep+cp]
def check(command,label):
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    (out/(label+'.log')).write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(label+' failed; inspect the synthetic test log')
    return json.loads(next(line for line in reversed(result.stdout.splitlines()) if line.startswith('{')))
vectors=check(java+['org.emulationstation.frontend.netplay.StationRecoveryVectorsTest',str(snapshot/'tests/contract-vectors.json')],'vectors')
fixture=out/'private-fixture.properties'
with (out/'server.log').open('w') as log:
    process=subprocess.Popen(['dotnet','run','--project','tests/StationRecovery/Http.Tests.csproj','-c','Release','--',str(fixture)],cwd=server,stdout=log,stderr=subprocess.STDOUT)
    try:
        until=time.monotonic()+45
        while not fixture.exists():
            if process.poll() is not None or time.monotonic()>until:raise RuntimeError('Private TLS harness did not start')
            time.sleep(.1)
        transport=check(java+['org.emulationstation.frontend.netplay.StationRecoveryTransportTest',str(fixture)],'transport')
    finally:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        fixture.unlink(missing_ok=True)
report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),vectors=vectors,transport=transport,
    clientJarSHA256=sha(build/'client.jar'),roomsJarSHA256=sha(build/'rooms.jar'),
    clientDexSHA256=j['clientDexSHA256'],roomsDexSHA256=j['roomsDexSHA256'],sourceCount=j['sourceCount'],
    productionTouched=False,privateFixtureRemoved=not fixture.exists(),twoDeviceGameplayVerified=False)
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
