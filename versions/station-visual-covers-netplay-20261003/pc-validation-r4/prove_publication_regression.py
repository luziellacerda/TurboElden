from pathlib import Path
import json,subprocess,hashlib
R=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
OUT=R/'publication-regression';OUT.mkdir(exist_ok=True)
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
old=R/'history/8ece6384/station/src/java/org/emulationstation/frontend/station/StationCoverQueue.java'
current=R/'station/build/host-classes'
output=OUT/'baseline-classes';output.mkdir(exist_ok=True)
subprocess.run([JDK/'javac.exe','--release','11','-encoding','UTF-8','-cp',current,'-d',output,old],check=True)
main='org.emulationstation.frontend.station.StationCoverPublicationTest'
baseline=subprocess.run([JDK/'java.exe','-cp',str(output)+';'+str(current),main],capture_output=True,text=True,timeout=20)
(OUT/'baseline.log').write_text(baseline.stdout+baseline.stderr,'utf8')
assert baseline.returncode!=0 and 'Every old request must finish before JNI publishes a catalog' in baseline.stderr
fixed=subprocess.run([JDK/'java.exe','-cp',current,main],capture_output=True,text=True,timeout=20)
(OUT/'fixed.log').write_text(fixed.stdout+fixed.stderr,'utf8')
assert fixed.returncode==0 and 'PASS 180' in fixed.stdout
report={'baselineR3Sha256':'8ece6384b83f565ec54615186a5940c6e5c47f79d4f03027332181799c4fb807','baselineSourceSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'baselineFailed':True,'failure':'Every old request must finish before JNI publishes a catalog','currentPassed':True,'checks':180,'raceIterations':20,'scope':'actual Java queue with simulated native inbox publication; native C++ policy is separately compiled/run; no Android runtime claim'}
(R/'evidence/publication-red-green.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report,indent=2))
