"""Verify compiled PS3 DEX against the exact pinned official native Java ABI."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

CONTRACT_SHA = "36d155d7cb1d918f4b4d3a8297eed34f64e3047deec94fae65335931188d70ad"
NATIVE_CLASSES = {
    "Laenu/emulator/Emulator;", "Laenu/emulator/Emulator$Config;", "Laenu/aps3e/Emulator;",
    "Laenu/hardware/ProcessorInfo;", "Laenu/lang/System;",
}
FIELD_CLASSES = {
    "Laenu/emulator/Emulator$Path;", "Laenu/aps3e/Emulator$MetaInfo;",
    "Laenu/aps3e/Emulator$CheatInfo;", "Laenu/aps3e/Emulator$GameTrophyInfo;",
    "Laenu/aps3e/Emulator$GameTrophyInfo$TrophyInfo;",
}

def verify(dex, contract_path):
    raw = Path(contract_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != CONTRACT_SHA:
        raise ValueError("Official PS3 ABI receipt was changed")
    contract = json.loads(raw)
    spec = importlib.util.spec_from_file_location("ps3_official_parser", Path(__file__).with_name("inspect_official.py"))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    expected = {row["class"]: row for row in contract["dex"]["jniClasses"]}
    actual_rows = module.dex_contract(Path(dex).read_bytes())
    actual = {row["class"]: row for row in actual_rows}
    checked = []
    for name in sorted(NATIVE_CLASSES):
        if name not in actual: raise ValueError("Missing PS3 JNI class: " + name)
        native = lambda row: sorted((method["name"], method["descriptor"], bool(method["accessFlags"] & 8))
                                    for method in row["nativeMethods"])
        if native(expected[name]) != native(actual[name]):
            raise ValueError("PS3 native registration signature mismatch: " + name)
        checked.append({"class": name, "nativeMethods": len(native(actual[name]))})
    for name in sorted(FIELD_CLASSES):
        if name not in actual: raise ValueError("Missing PS3 JNI structure: " + name)
        fields = lambda row: sorted((field["name"], field["type"], bool(field["accessFlags"] & 8))
                                    for field in row["fields"])
        if fields(expected[name]) != fields(actual[name]):
            raise ValueError("PS3 native structure layout mismatch: " + name)
        methods = {(method["name"],method["descriptor"]) for method in actual[name]["methods"]}
        if ("<init>","()V") not in methods: raise ValueError("Missing JNI constructor: " + name)
        checked.append({"class": name, "fields": len(fields(actual[name]))})
    if actual["Laenu/aps3e/Emulator;"]["super"] != "Laenu/emulator/Emulator;":
        raise ValueError("PS3 Emulator inheritance changed")
    return {"schema": "station.sony.ps3.compiled-jni.v1", "dexSha256": hashlib.sha256(Path(dex).read_bytes()).hexdigest(),
            "officialContractSha256": CONTRACT_SHA, "classes": checked, "nativeAbiMatchesOfficial": True,
            "nativeLibrariesRecompiled": False, "gameplayProof": False}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--dex",type=Path,required=True)
    parser.add_argument("--contract",type=Path,default=Path(__file__).resolve().parents[1]/"evidence/official-contract.json")
    parser.add_argument("--out",type=Path,required=True); args=parser.parse_args()
    result=verify(args.dex,args.contract)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"nativeAbiMatchesOfficial": True, "classes": len(result["classes"])}))

if __name__ == "__main__": main()
