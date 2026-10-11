#!/usr/bin/env python3
"""Read-only generator/JNI/pin consistency checks; not emulator gameplay."""
import argparse, hashlib, importlib.util, json, pathlib, re
HERE=pathlib.Path(__file__).resolve().parent.parent
def main():
    p=argparse.ArgumentParser(); p.add_argument("--clone",required=True); p.add_argument("--stage",required=True); a=p.parse_args()
    stage=pathlib.Path(a.stage); checks=0
    def check(value):
        nonlocal checks
        checks+=1
        if not value: raise AssertionError("check "+str(checks))
    spec=importlib.util.spec_from_file_location("station_generator",HERE/"recipe"/"generate_source.py")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    clone=pathlib.Path(a.clone)
    check(module.git(clone,"rev-parse","HEAD").decode().strip()==module.PIN)
    check(not module.git(clone,"status","--porcelain").strip())
    first=module.patched_sources(clone); second=module.patched_sources(clone); check(first==second)
    receipt=json.loads((stage/"station-r126-source-receipt.json").read_text())
    check(receipt["upstream"]==module.PIN); check(len(first)==15)
    for record in receipt["patchedFiles"]:
        check(hashlib.sha256(module.git(clone,"show",module.PIN+":"+record["path"])).hexdigest()==record["upstreamSha256"])
        check(hashlib.sha256((stage/record["path"]).read_bytes()).hexdigest()==record["patchedSha256"])
        check((stage/record["path"]).read_bytes().decode("utf-8")==first[record["path"]])
    for record in receipt["addedFiles"]:
        check(hashlib.sha256((stage/record["path"]).read_bytes()).hexdigest()==record["sha256"])
    check(first["Source/Core/Core/NetPlayClient.cpp"].count("!m_is_running.IsSet() || Common::StationDolphin::Suspended()")==5)
    check("Common::StationDolphin::DeferCPURun()" in first["Source/Core/Core/HW/CPU.cpp"])
    check(first["Source/Core/Core/HW/CPU.cpp"].count("Common::StationDolphin::DeferCPURun()")==3)
    check("else if (unpause_on_unlock && !Common::StationDolphin::DeferCPURun())" in first["Source/Core/Core/HW/CPU.cpp"])
    check('env->FindClass("tdolphin/core/util/Pair")' in first["Source/Android/jni/AndroidCommon/IDCache.cpp"])
    check("libdolp.so" not in first["Source/Android/jni/CMakeLists.txt"])
    check("station_dolphin_online" in first["Source/Android/jni/CMakeLists.txt"])
    java=(HERE/"java"/"org"/"emulationstation"/"frontend"/"netplay"/"StationDolphinBridge.java").read_text()
    cpp=(HERE/"native"/"StationDolphinBridge.cpp").read_text()
    javadecls=set(re.findall(r"\bnative\s+\w+(?:\[\])?\s+(native\w+)\(",java))
    jnidecls=set(re.findall(r"Java_org_emulationstation_frontend_netplay_StationDolphinBridge_(native\w+)\(",cpp))
    check(javadecls==jnidecls); check(len(javadecls)==21)
    check("nativeStatus" in javadecls); check("nativeAcknowledgedEpoch" in javadecls)
    check("nativeAuthorizeHumanExit" in javadecls)
    check("nativeSuspendTransport" in javadecls)
    check("nativeFail" in javadecls)
    check("nativeControl" in javadecls)
    check(first["Source/Core/Core/NetPlayClient.cpp"].count("StationService(m_client")==2)
    check(first["Source/Core/Core/NetPlayClient.cpp"].count("BlockAutomaticStop")==6)
    check("BlockAutomaticStop" in first["Source/Core/Core/Core.cpp"])
    check("BlockAutomaticStop" in first["Source/Android/jni/MainAndroid.cpp"])
    check("BlockAutomaticStop" in first["Source/Android/jni/NetPlay/NetPlayUICallbacks.cpp"])
    lock=json.loads((HERE/"recipe"/"dependencies.lock.json").read_text()); check(len(lock["modules"])==34)
    check(sum(m["android"] for m in lock["modules"])==25)
    deps=json.loads((stage/"station-r126-dependency-receipt.json").read_text()); check(deps["complete"])
    check(len(deps["archives"])==28)
    for record in deps["archives"]: check(len(record["commit"])==40 and len(record["sha256"])==64)
    hooks=json.loads((stage/"station-r126-hook-receipt.json").read_text())
    for record in hooks["files"]: check(hashlib.sha256((stage/record["path"]).read_bytes()).hexdigest()==record["patchedSha256"])
    result={"checks":checks,"passed":True,"upstreamCloneUnchanged":True,"generatorDeterministic":True,"nativeGamePlay":False,"scope":"pinned generator, stage, JNI names, source gate coverage, dependency/hook receipts"}
    (HERE/"evidence"/"generator-probe-r126.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__": main()
