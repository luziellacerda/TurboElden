"""Seal verified settings DEX28/40 and the two-label carousel patch; no APK."""
from pathlib import Path
import argparse
import hashlib
import json
import re

import build_java_payloads as java
import patch_settings_labels as labels


def checked(record):
    java.require(isinstance(record,dict) and set(record)=={"path","bytes","sha256"},"Exact artifact record required")
    path=Path(record["path"])
    java.require(path.is_absolute() and path.is_file() and not path.is_symlink() and
                 type(record["bytes"]) is int and record["bytes"]>0 and
                 re.fullmatch(r"[0-9a-f]{64}",record["sha256"]) and
                 path.stat().st_size==record["bytes"] and java.sha(path)==record["sha256"],"Pinned artifact differs")
    return path.resolve(strict=True)


def record(path):
    path=path.resolve(strict=True)
    return dict(path=str(path),bytes=path.stat().st_size,sha256=java.sha(path))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java-receipt",type=Path,required=True)
    parser.add_argument("--labels-receipt",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    compiled=json.loads(args.java_receipt.read_bytes()); patched=json.loads(args.labels_receipt.read_bytes())
    java.require(compiled["schema"]=="station.settings.refinement.java.r134.v1" and compiled["revision"]=="R134" and compiled["passed"] is True,
                 "Verified Java receipt required")
    java.require(compiled["baselineApkSha256"]==java.BASE_SHA and compiled["baselineApkBytes"]==java.BASE_BYTES,
                 "Exact R133 Java donor required")
    java.require(compiled["sourceSha256"]==java.source_map() and
                 compiled["sourceCanonicalSha256"]==java.digest(java.canonical(compiled["sourceSha256"])),"Compiled source freeze differs")
    java.verify_commit(compiled["sourceCommit"],compiled["sourceSha256"])
    java.require(compiled["changedDexPartitions"]==list(java.PARTITIONS) and
                 compiled["unrelatedClassesByteIdentical"] is True and compiled["classDeltaRestrictedToAllowedFamilies"] is True and
                 compiled["compileOnlyClassesPackaged"] is False and compiled["compilerLambdaStubsPackaged"] is False and
                 compiled["javaApiPolicy"]=="android-sdk-bootclasspath-only","Exact scoped Android boot compilation required")
    java.require(compiled["inputSha256"]=={**java.PINS,**java.JDK_PINS},"Pinned compile inputs differ")
    for name,value in compiled["inputFiles"].items():
        checked(value); java.require(value["sha256"]==compiled["inputSha256"][name],"Compile input seal differs")
    java.require(set(compiled["inputFiles"])==set(compiled["inputSha256"]),"Missing compile input path")
    expected_preserved={"classes.dex" if i==1 else f"classes{i}.dex" for i in range(1,41)}-set(java.PARTITIONS)
    java.require(set(compiled["preservedDexSha256"])==expected_preserved,"Exactly 38 unrelated DEX records required")
    payloads={}; scopes={}
    for row in compiled["partitions"]:
        name=row["partition"]
        java.require(name in java.PARTITIONS and name not in payloads and
                     row["baselineDexSha256"]==java.PARTITIONS[name]["sha256"] and
                     row["allowedFamilies"]==list(java.PARTITIONS[name]["families"]),"Partition scope differs")
        java.require(row["unrelatedClassesByteIdentical"] is True and row["classDeltaRestrictedToAllowedFamilies"] is True and
                     row["staticInitializersPreserved"] is True,"Unrelated class guard required")
        before,after=set(row["originalAllowedTypes"]),set(row["finalAllowedTypes"])
        original_map,output_map,unchanged=row["baselineClassSha256"],row["outputClassSha256"],row["unchangedClassSha256"]
        java.require(row["allowedFamilyRoots"]==list(java.PARTITIONS[name]["families"]) and
                     {t for t in original_map if java.belongs(t,row["allowedFamilies"])}==before and
                     {t for t in output_map if java.belongs(t,row["allowedFamilies"])}==after and
                     set(original_map)-before==set(output_map)-after==set(unchanged) and
                     {t:original_map[t] for t in unchanged}=={t:output_map[t] for t in unchanged}==unchanged,
                     "Complete donor/final class maps exceed scoped delta")
        java.require(all(re.fullmatch(r"[0-9a-f]{64}",s) for s in [*original_map.values(),*output_map.values()]) and
                     len(original_map)==row["originalClassCount"] and len(output_map)==row["finalClassCount"],
                     "Pinned complete class hash maps required")
        java.require(set(row["addedTypes"])==after-before and set(row["removedTypes"])==before-after and
                     set(row["modifiedTypes"])<=before&after and
                     all(java.belongs(t,row["allowedFamilies"]) for t in before|after),"Explicit family delta inconsistent")
        java.require(row["originalClassCount"]-len(before)==row["unchangedClasses"]==row["finalClassCount"]-len(after) and
                     len(row["unrelatedClassProjectionSha256"])==row["unchangedClasses"] and
                     row["unrelatedClassProjectionSha256"]==unchanged and
                     java.digest(java.canonical(row["unrelatedClassProjectionSha256"]))==row["unrelatedProjectionCanonicalSha256"],
                     "Unrelated class inventory differs")
        artifact={k:row["payload"][k] for k in ("path","bytes","sha256")}; checked(artifact)
        java.require(row["payload"]["name"]==name,"Payload partition differs")
        payloads[name]=artifact; scopes[name]={k:v for k,v in row.items() if k!="payload"}
    java.require(set(payloads)==set(java.PARTITIONS),"Both settings partitions required")
    java.require(patched["schema"]=="station.settings.labels.r134.v1" and patched["passed"] is True and
                 patched["baselineCarouselSha256"]==labels.CAROUSEL_SHA and
                 all(patched[k] is True for k in ("exactInversePassed","allOtherBytesIdentical","equalSizeReplacements",
                                                "elfHeaderPreserved","original16KiBAlignmentPreserved","artAndShadersByteIdentical")),
                 "Exact native two-label guard required")
    artifact={k:patched["payload"][k] for k in ("path","bytes","sha256")}; native=checked(artifact).read_bytes()
    java.require(patched["payload"]["name"]==labels.LIBRARY_ENTRY and patched["payloadSha256"]==artifact["sha256"] and
                 patched["payloadBytes"]==len(native) and len(patched["changedLabels"])==2,"Native payload seal differs")
    inverse=bytearray(native)
    for row,(old,new) in zip(patched["changedLabels"],labels.LABELS):
        at=row["offset"]
        java.require(row["bytes"]==22 and row["fromText"]==old and row["toText"]==new and
                     native[at:at+22]==new.encode("utf8"),"Native label declaration differs")
        inverse[at:at+22]=old.encode("utf8")
    original=bytes(inverse)
    java.require(java.digest(original)==labels.CAROUSEL_SHA,"Native inverse baseline differs")
    replay,_=labels.patch(original)
    java.require(replay==native,"Native patch replay differs")
    payloads[labels.LIBRARY_ENTRY]=artifact
    result=dict(schema="station.settings.refinement.payloads.v1",revision="R134",passed=True,
        sourceCommit=compiled["sourceCommit"],sourceSha256=compiled["sourceSha256"],sourceCanonicalSha256=compiled["sourceCanonicalSha256"],
        baseApkSha256=java.BASE_SHA,baseApkBytes=java.BASE_BYTES,
        baselinePayloadSha256={**{n:s["sha256"] for n,s in java.PARTITIONS.items()},labels.LIBRARY_ENTRY:labels.CAROUSEL_SHA},
        payloads=payloads,dexScopes=scopes,inputSha256=compiled["inputSha256"],inputFiles=compiled["inputFiles"],
        approvedScopes=["graphics-settings-grouped-pages","sony-emulator-settings-and-return","native-sony-settings-action-labels"],
        javaReceipt=record(args.java_receipt),labelsReceipt=record(args.labels_receipt),
        preservedDexSha256=compiled["preservedDexSha256"],classDeltaRestrictedToAllowedFamilies=True,
        unrelatedClassesByteIdentical=True,labelPatchInversePassed=True,allOtherNativeBytesIdentical=True,
        original16KiBAlignmentPreserved=True,javaApiPolicy=compiled["javaApiPolicy"],compileOnlyClassesPackaged=False,
        compilerLambdaStubsPackaged=False,apkAssembled=False,signed=False,installed=False,physicalGameplayValidated=False)
    output=args.out.resolve()
    java.require(output.drive.upper()=="G:" and not output.exists(),"Use new isolated G: receipt")
    output.parent.mkdir(parents=True,exist_ok=True);java.write(output,result)
    print(json.dumps(dict(sealed=True,sourceCommit=result["sourceCommit"],payloads=3,unrelatedDexPreserved=38,sha256=java.sha(output))))


if __name__=="__main__":
    main()
