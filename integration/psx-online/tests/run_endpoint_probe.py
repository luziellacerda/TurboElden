#!/usr/bin/env python3
"""Isolated JVM PSX PXL1 tests plus the unchanged R126 Dolphin/TCP regressions."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

def native(path):
    return Path("\\\\?\\" + str(path.resolve())) if __import__("os").name == "nt" else path

def sha(path):
    return hashlib.sha256(native(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument("--jdk",type=Path,required=True);p.add_argument("--classes-jar",type=Path,required=True);p.add_argument("--wire",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    here=Path(__file__).resolve().parent;module=here.parent;repo=module.parent.parent
    old=repo/"versions/station-dolphin-online-r126-20261011";java=module/"java/org/emulationstation/frontend/netplay"
    files=[java/"StationMultiplayerEndpoint.java",java/"StationMultiplayerTunnel.java",java/"StationPsxEndpoint.java",
           here/"StationPsxEndpointProbe.java",here/"fixtures/org/emulationstation/frontend/netplay/StationPsxBridge.java",
           old/"tests/StationDolphinEndpointProbe.java",java/"StationMultiplayerSession.java",a.wire]
    files.extend(sorted((old/"tests/fixtures").rglob("*.java")))
    sources=a.out/"sources";classes=a.out/"classes";sources.mkdir(parents=True,exist_ok=True);classes.mkdir(parents=True,exist_ok=True)
    aliases=[]
    for i,source in enumerate(files):
        dest=sources/str(i)/source.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(native(source).read_bytes());aliases.append(dest)
    command=[a.jdk/"javac.exe","-encoding","UTF-8","-cp",a.classes_jar,"-d",classes,*aliases]
    result=subprocess.run(list(map(str,command)),capture_output=True,text=True,encoding="utf-8");(a.out/"javac.log").write_text(result.stdout+result.stderr,encoding="utf-8")
    if result.returncode: raise RuntimeError("JVM endpoint compilation failed: "+result.stderr)
    outputs={}
    for name in ["StationDolphinEndpointProbe","StationPsxEndpointProbe"]:
        r=subprocess.run([str(a.jdk/"java.exe"),"-cp",str(classes)+";"+str(a.classes_jar),"org.emulationstation.frontend.netplay."+name],capture_output=True,text=True,encoding="utf-8")
        (a.out/(name+".log")).write_text(r.stdout+r.stderr,encoding="utf-8")
        if r.returncode: raise RuntimeError(name+" failed: "+r.stdout+r.stderr)
        outputs[name]=r.stdout.strip()
    receipt={"result":"passed","tests":outputs,"classpath":{"sha256":sha(a.classes_jar)},"sources":{x.resolve().relative_to(repo).as_posix():sha(x) for x in files},"physicalGameplayValidated":False,"fixtureShipped":False}
    (a.out/"endpoint-probe.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"result":"passed","tests":outputs,"receipt":str(a.out/"endpoint-probe.json")},indent=2))
if __name__=="__main__": main()
