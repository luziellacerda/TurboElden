"""Compile two isolated R134 settings overlays over the exact signed R133.

No APK assembly, signing, installation, engine changes, or server operations.
Dependencies are compile-only; the explicit family delta is checked twice.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE_SHA = "945f7ded35e551d638135a05140c32218eb38277d10eaf21e3f83087d71da112"
BASE_BYTES = 2714971151
PARTITIONS = {
    "classes28.dex": dict(
        sha256="62d74741c096e0280133b4cb7b37f4b9c4b25bade682be44dae734f2554140e0",
        families=("Lorg/emulationstation/frontend/station/StationGraphicsPanel;",),
        sources=("java/org/emulationstation/frontend/station/StationGraphicsPanel.java",)),
    "classes40.dex": dict(
        sha256="f3dddbea9c8fcb80e3ecc6f6a255fe5b77a2f3572d4fdf657e31a4ebd6576a10",
        families=("Lorg/emulationstation/frontend/sony/Ps3Activity;",
                  "Lorg/emulationstation/frontend/sony/Ps4Activity;"),
        sources=("java/org/emulationstation/frontend/sony/Ps3Activity.java",
                 "java/org/emulationstation/frontend/sony/Ps4Activity.java")),
}
PINS = {
    "android_jar": "6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad",
    "d8_jar": "305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5",
    "lambda_stubs": "c8a21e0e653227d1fce74bd547c9e7278e17c016c405aa8e1f6c313b192ade31",
    "apktool": "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",
    "client_jar": "011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313",
    "graphics_dependencies_jar": "3a76446d21899722b29dcac298e7f9c16aea4c3467ff77c8eecf4a5298ad6ea4",
    "sony_host_jar": "9235d450a126acf8535fc3979210100d15ddb3271fb3a650fa436852719abba4",
    "bridge_jar": "8a4d6b2f0ae2da3bbe3252d8b5de3aaa2fa249168f2ed006605875e38ae6ef10",
}
JDK_PINS = {
    "java.exe": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "javac.exe": "9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549",
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def write(path, value):
    require(not path.exists(), "Refusing to overwrite a compiled receipt")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def source_map():
    result = {}
    for directory in ("java", "recipe"):
        for path in sorted((ROOT/directory).rglob("*")):
            if path.is_file() and path.suffix in {".java", ".py"}:
                require(not path.is_symlink(), "Symbolic productive input")
                result[path.relative_to(ROOT).as_posix()] = sha(path)
    return result


def verify_commit(commit, pins):
    require(re.fullmatch(r"[0-9a-f]{40}", commit), "Full executable-source commit required")
    git = ["git", "-c", "safe.directory="+REPO.as_posix(), "-C", str(REPO)]
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, checksum in pins.items():
        raw = subprocess.check_output(git+["show", commit+":"+prefix+"/"+name], stderr=subprocess.PIPE)
        require(digest(raw)==checksum, "Source differs from raw committed bytes: "+name)


def belongs(type_name, families):
    return any(type_name==family or type_name.startswith(family[:-1]+"$") for family in families)


def smali_types(root):
    result = {}
    for path in sorted(root.rglob("*.smali")):
        require(not path.is_symlink(), "Symbolic decoded source")
        type_name = "L"+path.relative_to(root).as_posix()[:-6]+";"
        require(type_name not in result, "Duplicate decoded type")
        result[type_name] = path
    return result


def class_count(raw):
    require(raw.startswith(b"dex\n") and len(raw)>=112, "Invalid DEX")
    return struct.unpack_from("<I", raw, 96)[0]


def run(command, out, label):
    environment = {**os.environ, "TMP": str(out/"temp"), "TEMP": str(out/"temp"),
                   "PYTHONDONTWRITEBYTECODE": "1",
                   "JAVA_TOOL_OPTIONS": '-Djava.io.tmpdir="'+str(out/"temp")+'" -XX:-UsePerfData'}
    result = subprocess.run(list(map(str, command)), capture_output=True, encoding="utf-8",
                            errors="replace", env=environment)
    (out/(label+".log")).write_text(result.stdout+result.stderr, encoding="utf-8")
    require(result.returncode==0, label+" failed; inspect private isolated diagnostics")
    return result.stdout.strip()


def container(path, partition, raw):
    require(not path.exists(), "Partition fixture already exists")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(zipfile.ZipInfo(partition, (1980,1,1,0,0,0)), raw)


def make_jar(classes, output, families):
    require(not output.exists(), "Overlay jar exists")
    with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as archive:
        for path in sorted(classes.rglob("*.class")):
            name = path.relative_to(classes).as_posix()
            require(belongs("L"+name[:-6]+";", families), "Foreign compile class: "+name)
            archive.writestr(zipfile.ZipInfo(name, (1980,1,1,0,0,0)), path.read_bytes())


def compile_overlay(args, name, spec, classpath, java, javac, helper_cp):
    classes=args.out/(name+"-classes"); classes.mkdir()
    boot=os.pathsep.join(map(str, (args.lambda_stubs, args.android_jar)))
    run([javac, "-encoding", "UTF-8", "-source", "8", "-target", "8", "-bootclasspath", boot,
         "-proc:none", "-implicit:none", "-sourcepath", args.out/"empty-sourcepath", "-cp", os.pathsep.join(map(str,classpath)),
         "-d", classes, *[ROOT/s for s in spec["sources"]]], args.out, name+"-javac")
    jar=args.out/(name+"-overlay.jar"); make_jar(classes,jar,spec["families"])
    dex=args.out/(name+"-overlay-dex"); dex.mkdir()
    command=[java,"-cp",args.d8_jar,"com.android.tools.r8.D8","--release","--min-api","28","--lib",args.android_jar]
    for path in classpath:
        command += ["--classpath",path]
    run(command+["--output",dex,jar],args.out,name+"-d8")
    require(sorted(dex.glob("*.dex"))==[dex/"classes.dex"],"Exactly one overlay DEX required")
    fixture=args.out/(name+"-overlay-container.zip"); container(fixture,"classes.dex",(dex/"classes.dex").read_bytes())
    smali=args.out/(name+"-overlay-smali")
    run([java,"-cp",helper_cp,"DecodeDolphinPartition",fixture,"classes.dex",sha(dex/"classes.dex"),smali],args.out,name+"-overlay-decode")
    types=smali_types(smali)
    require(types and all(belongs(t,spec["families"]) for t in types),"D8 emitted foreign type")
    require(set(spec["families"])<=set(types),"Overlay omitted a settings owner")
    return jar,smali


def merge_overlay(args, partition, spec, overlay, java, helper_cp):
    name=partition[:-4]
    donor=args.out/(name+"-donor-smali")
    run([java,"-cp",helper_cp,"DecodeDolphinPartition",args.donor,partition,spec["sha256"],donor],args.out,name+"-donor-decode")
    original=smali_types(donor)
    original_allowed={t:p for t,p in original.items() if belongs(t,spec["families"])}
    final_allowed=smali_types(overlay)
    require(set(spec["families"])<=set(original_allowed),"Donor owner root missing")
    outside={t:sha(p) for t,p in original.items() if t not in original_allowed}
    working=args.out/(name+"-working-smali"); shutil.copytree(donor,working)
    # Only these exact decoded old family members can be replaced or removed.
    for type_name in original_allowed:
        target=working/(type_name[1:-1]+".smali")
        require(target.is_file() and target.resolve().is_relative_to(working.resolve()),"Unsafe exact family member")
        target.unlink()
    for type_name,path in final_allowed.items():
        require(belongs(type_name,spec["families"]),"Unapproved class namespace")
        target=working/(type_name[1:-1]+".smali"); target.parent.mkdir(parents=True,exist_ok=True)
        require(not target.exists(),"Overlay would replace an unrelated class")
        shutil.copyfile(path,target)
    scope=args.out/(name+"-scope.properties")
    scope.write_text("\n".join(["schema=station.settings.scoped-types.r134.v1","partition="+partition,
        "donorSha256="+spec["sha256"],"families="+"|".join(sorted(spec["families"])),
        "originalAllowed="+"|".join(sorted(original_allowed)),"finalAllowed="+"|".join(sorted(final_allowed))])+"\n",encoding="utf-8")
    expected=(f"verifiedClasses={len(original)} finalClasses={len(outside)+len(final_allowed)} unchanged={len(outside)} "
              f"originalAllowed={len(original_allowed)} finalAllowed={len(final_allowed)} donorSHA={spec['sha256']}")
    actual=run([java,"-cp",helper_cp,"VerifyScopedPartition",args.donor,partition,spec["sha256"],working,scope],args.out,name+"-verify-source")
    require(actual==expected,"Unexpected strict family verification receipt")
    output=args.out/partition
    lines=run([java,"-cp",helper_cp,"AssembleScopedPartition",args.donor,partition,spec["sha256"],working,output,scope],args.out,name+"-assemble").splitlines()
    pattern=(rf"assembledClasses={len(outside)+len(final_allowed)} restoredInitializerArrays=([0-9]+) "
             rf"originalAllowed={len(original_allowed)} finalAllowed={len(final_allowed)} donorSHA={spec['sha256']}")
    check=re.fullmatch(pattern,lines[-1] if lines else "")
    require(len(lines)==2 and lines[0]==expected and check is not None,"Initializer-preserving assembly receipt missing")
    require(int(check.group(1))<=len(outside),"Initializer restoration escaped unchanged classes")
    fixture=args.out/(name+"-final-container.zip"); container(fixture,partition,output.read_bytes())
    actual_smali=args.out/(name+"-final-smali")
    run([java,"-cp",helper_cp,"DecodeDolphinPartition",fixture,partition,sha(output),actual_smali],args.out,name+"-final-decode")
    actual=run([java,"-cp",helper_cp,"VerifyScopedPartition",args.donor,partition,spec["sha256"],actual_smali,scope],args.out,name+"-verify-final")
    require(actual==expected,"Assembled unrelated classes changed")
    final=smali_types(actual_smali)
    require(set(final)==(set(outside)|set(final_allowed)),"Final exact class set differs")
    require({t:sha(final[t]) for t in outside}==outside,"Unrelated class projection bytes differ")
    require(class_count(output.read_bytes())==len(final),"DEX header class count differs")
    common=set(original_allowed)&set(final_allowed)
    receipt=dict(partition=partition,baselineDexSha256=spec["sha256"],allowedFamilies=list(spec["families"]),
        allowedFamilyRoots=list(spec["families"]),baselineClassSha256={t:sha(p) for t,p in original.items()},
        outputClassSha256={t:sha(p) for t,p in final.items()},unchangedClassSha256=outside,
        originalAllowedTypes=sorted(original_allowed),finalAllowedTypes=sorted(final_allowed),
        addedTypes=sorted(set(final_allowed)-set(original_allowed)),removedTypes=sorted(set(original_allowed)-set(final_allowed)),
        modifiedTypes=sorted(t for t in common if sha(original_allowed[t])!=sha(final[t])),
        originalClassCount=len(original),finalClassCount=len(final),unchangedClasses=len(outside),
        unrelatedClassesByteIdentical=True,classProjectionFormat="apktool-3.0.3-baksmali-locals-sequential-labels-debug-info",
        unrelatedClassProjectionSha256=outside,
        unrelatedProjectionCanonicalSha256=digest(canonical(outside)),classDeltaRestrictedToAllowedFamilies=True,
        staticInitializersPreserved=True,restoredInitializerArrays=int(check.group(1)),scopeDeclarationSha256=sha(scope),
        payload=dict(name=partition,path=str(output),bytes=output.stat().st_size,sha256=sha(output)))
    write(args.out/(name+"-receipt.json"),receipt)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("donor","jdk","android-jar","lambda-stubs","d8-jar","apktool","client-jar",
                "graphics-dependencies-jar","sony-host-jar","bridge-jar","out"):
        parser.add_argument("--"+key,type=Path,required=True)
    parser.add_argument("--source-commit",required=True)
    parser.add_argument("--check-inputs-only",action="store_true")
    args=parser.parse_args()
    args.out=args.out.resolve()
    require(args.out.drive.upper()=="G:" and ROOT not in args.out.parents and not args.out.exists(),
            "Use a new isolated G: build directory, never the backup or source tree")
    args.donor=args.donor.resolve(strict=True)
    require(args.donor.stat().st_size==BASE_BYTES and sha(args.donor)==BASE_SHA,"Exact signed R133 donor required")
    input_pins={}; input_files={}
    for name,checksum in PINS.items():
        path=getattr(args,name).resolve(strict=True)
        require(path.is_file() and not path.is_symlink() and sha(path)==checksum,"Pinned compile-only input differs: "+name)
        setattr(args,name,path);input_pins[name]=checksum
        input_files[name]=dict(path=str(path),bytes=path.stat().st_size,sha256=checksum)
    java=args.jdk/"bin/java.exe"; javac=args.jdk/"bin/javac.exe"
    for name,checksum in JDK_PINS.items():
        require(sha(args.jdk/"bin"/name)==checksum,"Pinned JDK executable differs")
        input_pins[name]=checksum
        path=(args.jdk/"bin"/name).resolve(strict=True)
        input_files[name]=dict(path=str(path),bytes=path.stat().st_size,sha256=checksum)
    with zipfile.ZipFile(args.lambda_stubs) as archive:
        stub_types=[n for n in archive.namelist() if n.endswith(".class")]
        require(stub_types and all(n.startswith("java/lang/invoke/") for n in stub_types),"Only SDK compiler lambda signatures allowed")
    expected_sources={s for spec in PARTITIONS.values() for s in spec["sources"]}
    actual_sources={p.relative_to(ROOT).as_posix() for p in (ROOT/"java").rglob("*.java")}
    require(actual_sources==expected_sources,"Exactly GraphicsPanel and Ps3/Ps4Activity source families required")
    frozen=source_map(); verify_commit(args.source_commit,frozen)
    donor_dex={}
    with zipfile.ZipFile(args.donor) as archive:
        for i in range(1,41):
            name="classes.dex" if i==1 else f"classes{i}.dex"
            donor_dex[name]=digest(archive.read(name))
        for name,spec in PARTITIONS.items():
            require(donor_dex[name]==spec["sha256"],"Pinned donor partition differs")
    if args.check_inputs_only:
        print(json.dumps(dict(passed=True,compiled=False,sourceCommit=args.source_commit,sourceSha256=frozen,
                              inputSha256=input_pins,baselineApkSha256=BASE_SHA,partitions=PARTITIONS)))
        return
    args.out.mkdir(parents=True);(args.out/"temp").mkdir();(args.out/"empty-sourcepath").mkdir()
    helpers=args.out/"tools"; helpers.mkdir()
    run([javac,"-encoding","UTF-8","--release","17","-cp",args.apktool,"-d",helpers,
         *[ROOT/"recipe"/n for n in ("DecodeDolphinPartition.java","VerifyScopedPartition.java","AssembleScopedPartition.java")]],args.out,"scoped-tools")
    helper_cp=os.pathsep.join(map(str,(helpers,args.apktool)))
    overlays=[]
    for partition,spec in PARTITIONS.items():
        dependencies=([args.graphics_dependencies_jar,args.client_jar] if partition=="classes28.dex"
                      else [args.sony_host_jar,args.bridge_jar])
        _,decoded=compile_overlay(args,partition[:-4],spec,dependencies,java,javac,helper_cp)
        overlays.append(merge_overlay(args,partition,spec,decoded,java,helper_cp))
    require(frozen==source_map(),"Productive sources changed during compilation")
    receipt=dict(schema="station.settings.refinement.java.r134.v1",revision="R134",passed=True,
        sourceCommit=args.source_commit,sourceSha256=frozen,sourceCanonicalSha256=digest(canonical(frozen)),
        baselineApkSha256=BASE_SHA,baselineApkBytes=BASE_BYTES,inputSha256=input_pins,inputFiles=input_files,partitions=overlays,
        preservedDexSha256={n:s for n,s in donor_dex.items() if n not in PARTITIONS},
        changedDexPartitions=list(PARTITIONS),unrelatedClassesByteIdentical=True,
        classDeltaRestrictedToAllowedFamilies=True,compileOnlyClassesPackaged=False,
        javaApiPolicy="android-sdk-bootclasspath-only",compilerLambdaStubsPackaged=False,
        nonSettingsClassesPreserved=True,engineNativeLibrariesChanged=False,
        runtimeProfileOptionsChanged=False,rendererVideoCacheEconomyChanged=False,
        apkAssembled=False,signed=False,installed=False,physicalGameplayValidated=False)
    write(args.out/"java-compilation.json",receipt)
    print(json.dumps(dict(compiled=True,changedPartitions=list(PARTITIONS),unrelatedDexPreserved=38,
                          addedTypes=sum(len(p['addedTypes']) for p in overlays),removedTypes=sum(len(p['removedTypes']) for p in overlays))))


if __name__=="__main__":
    main()
