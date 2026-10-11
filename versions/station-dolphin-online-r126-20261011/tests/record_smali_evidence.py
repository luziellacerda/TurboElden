"""Check copied donors and real DEX hooks, recording isolated build evidence."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("recipe",ROOT/"recipe/patch_dolphin_smali.py")
recipe=importlib.util.module_from_spec(spec);spec.loader.exec_module(recipe)

def digest(path):return hashlib.sha256(recipe.fs(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    for arg in ("base-apk","core","bootstrap","stage","java-build","jdk","apktool","receipt"):
        p.add_argument("--"+arg,type=Path,required=True)
    for arg in ("output-core","output-bootstrap","dex10"):
        p.add_argument("--"+arg,type=Path)
    a=p.parse_args();sources={"core":a.core,"bootstrap":a.bootstrap}
    changes,planned=recipe.plan(sources,a.base_apk)
    outputs={"core":a.output_core or a.stage/"station-smali10-patched","bootstrap":a.output_bootstrap or a.stage/"station-smali12-patched"}
    dex10=a.dex10 or a.stage/"station-classes10.dex"
    untouched=modified=0
    for group,source in sources.items():
        original_files={path.relative_to(source).as_posix():path for path in source.rglob("*.smali")}
        actual_files={path.relative_to(outputs[group]).as_posix():path for path in outputs[group].rglob("*.smali")}
        assert original_files.keys()==actual_files.keys(),"complete copied donor tree required"
        for relative,path in original_files.items():
            expected=planned.get((group,relative))
            if expected is None:expected=recipe.fs(path).read_bytes();untouched+=1
            else:modified+=1
            assert recipe.fs(actual_files[relative]).read_bytes()==expected,relative
    assert untouched==4991 and modified==5
    command=[str(a.jdk/"java.exe"),"-Xmx1536m","-cp",str(a.stage/"station-smali-tools")+";"+str(a.apktool),
             "DolphinDexHookProbe",str(dex10),str(a.stage/"station-classes12.dex"),
             str(a.java_build/"classes35.dex"),str(a.base_apk)]
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace")
    if result.returncode:raise RuntimeError(result.stdout)
    dex=json.loads(result.stdout.splitlines()[0]);calls={}
    for line in result.stdout.splitlines()[1:]:
        count,descriptor=line.split(" ",1);calls[descriptor]=int(count)
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    result_receipt={"schema":"station-dolphin-smali-assembly-v1","basePartitionHashes":recipe.EXPECTED_DEX,
        "sourceTrees":recipe.EXPECTED_TREES,"modifiedFiles":changes,
        "copiedSmaliFiles":{"unchangedByteForByte":untouched,"patchedAsPlanned":modified},
        "artifacts":{name:{"path":str(path),"bytes":path.stat().st_size,"sha256":digest(path)} for name,path in {
            "classes10.dex":dex10,"classes12.dex":a.stage/"station-classes12.dex",
            "classes35.dex":a.java_build/"classes35.dex"}.items()},
        "tools":{"apktoolJar":str(a.apktool),"apktoolSha256":digest(a.apktool),"jdk":str(a.jdk)},
        "dexProbe":dex,"actualDexHooks":calls,
        "sourceRecipeHashes":{name:digest(ROOT/name) for name in ["recipe/patch_dolphin_smali.py","recipe/DecodeDolphinPartition.java","recipe/AssembleDolphinPartition.java","tests/DolphinDexHookProbe.java","tests/probe_dolphin_smali.py","tests/record_smali_evidence.py"]},
        "donorModified":False,"offlineNativeLibrariesModified":False,"apkBuiltByThisRecipe":False,
        "physicalGameplayValidated":False,"productionRegistryValidated":False}
    a.receipt.write_text(json.dumps(result_receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"unchangedFiles":untouched,"patchedFiles":modified,"actualDexChecks":dex["checks"],"receipt":str(a.receipt)}))

if __name__=="__main__":main()
