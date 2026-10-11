"""R122 recipe: verify exact R121, compile online/menu UI, preserve its manifest and engines.

Private media objects stay outside Git. This recipe never starts a phone, changes an
emulator engine, downloads an asset, or supplies a signing password.
"""
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

zipfile.ZIP64_LIMIT = (1 << 32) - 1
ROOT = Path(__file__).resolve().parent
BASE_SHA = "eadb83cc2b797eed7d6c3cbdcae09fae7fdfbff0004c3b9db791aaadf68113b0"
BASE_BYTES = 2217065864
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
CLANG_SHA = "1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3"
BASE_JAVA_MANIFEST_SHA = "35ba233c151b327489f730a5bd9fcff4098dd54a48f40287f9197313079ca10c"
BASE_CAROUSEL_MANIFEST_SHA = "bec43d6506abca9553791cbcb31fcdd6a2aa672392cefbbac2c417d7e6ba1137"
BASE_BUILD_RECEIPT_SHA = "c1f815e547dbbd6db0b5bb3532f241d6aa8e8d11af6d9b48a295efcbaddaa90c"
FACTORY = "org.emulationstation.frontend.station.StationComponentFactory"
BASE_MEMBERS = {
    "AndroidManifest.xml": "c4e9a6d69497bb928f53b35b49bef86d1b57a0b2b0bd5d0aa1953cfd5d9752a4",
    "classes28.dex": "30510f75305f346bca137327932f1a196af459f9ec406761b65398dae4bfb15b",
    "classes35.dex": "605d6de0bd16af2710e050744126d7aa9d7c6c4b08820b2e59c18b07d24a2a15",
    "lib/arm64-v8a/libstation_frontend.so": "a724caa8ac7c9422f494c1be82c95c500adc5730f8f17e05d49829bfc14761d6",
    "lib/arm64-v8a/libturbo_carousel.so": "22f3770343312b9d6b298f021ba94464b5d3de13f7d8499581668f9d7bec261a",
    "lib/arm64-v8a/libstation_retroarch.so": "81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc",
    "assets/station-online/engines.json": "d284c36c0784b2808c7379dc6af2f544c363548db446d1601de1cf171b2e1c18"
}
PRIVATE_INPUTS = (
    "d1/video720_posters.o", "d3/collection_previews.o", "d4/lottie_frames.o",
    "d5/installed_art.o", "d6/collection_previews.o", "d7/collection_previews.o",
    "d8/collection_previews.o", "d1/libc.so", "d1/libdl.so", "d1/liblog.so",
)
ALLOWED_PAYLOADS = (
    "classes28.dex", "classes35.dex", "lib/arm64-v8a/libturbo_carousel.so",
)
REQUIRED_CHANGES = set(ALLOWED_PAYLOADS)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def native_path(path):
    path = Path(path).resolve()
    return Path("\\\\?\\" + str(path)) if os.name == "nt" else path


def sha(path):
    with native_path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def zip_sha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path):
    return json.loads(native_path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    native_path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def signature(name):
    return name.startswith("META-INF/") and name.upper().endswith((".MF", ".SF", ".RSA", ".DSA", ".EC"))


def walk_files(directory):
    directory = Path(directory).resolve()
    for parent, _, names in os.walk(native_path(directory)):
        for name in names:
            path = Path(parent) / name
            relative = path.relative_to(native_path(directory)).as_posix()
            yield relative, directory / relative


def tool_directory(value, tool, nested):
    root = Path(value).resolve()
    candidate = root if (root / tool).is_file() else root / nested
    require((candidate / tool).is_file(), "Missing tool: " + str(candidate / tool))
    return candidate


def source_inventory(args):
    base_java_path = ROOT / "JAVA-SOURCE-MANIFEST-R121.json"
    base_native_path = ROOT / "CAROUSEL-INPUT-MANIFEST-R121.json"
    base_build_path = ROOT / "evidence/build-r121.json"
    require(sha(base_java_path) == BASE_JAVA_MANIFEST_SHA, "Frozen R121 Java manifest changed")
    require(sha(base_native_path) == BASE_CAROUSEL_MANIFEST_SHA, "Frozen R121 native manifest changed")
    require(sha(base_build_path) == BASE_BUILD_RECEIPT_SHA, "Frozen R121 build receipt changed")
    baseline_java, baseline_native = read_json(base_java_path), read_json(base_native_path)
    baseline_build = read_json(base_build_path)
    java_manifest = read_json(ROOT / "JAVA-SOURCE-MANIFEST.json")
    require(len(baseline_java) == 232 and set(baseline_java).issubset(java_manifest), "R121 Java sources missing")
    java_paths = {name: path for name, path in walk_files(ROOT / "java") if name.endswith(".java")}
    require(set(java_paths) == set(java_manifest), "Finalize JAVA-SOURCE-MANIFEST.json before compiling")
    java_hashes = {name: sha(path) for name, path in sorted(java_paths.items())}
    require(java_hashes == java_manifest, "Java bytes differ from the finalized manifest")
    require(all(name.startswith(("client/src/java/", "netplay-src/", "dependency-src/")) for name in java_paths), "Unknown Java module")
    for name in ("StationComponentFactory.java", "StationControllerPresence.java"):
        require("client/src/java/org/emulationstation/frontend/station/" + name in java_paths, "Missing preserved R121 controller/factory source: " + name)

    current_native = read_json(ROOT / "CAROUSEL-INPUT-MANIFEST.json")
    require(set(baseline_native).issubset(current_native), "R121 native inputs missing from current manifest")
    native_paths = {}
    for name, expected in sorted(current_native.items()):
        path = ROOT / "native" / name
        if not native_path(path).is_file():
            path = args.native_inputs / name
        require(native_path(path).is_file(), "Missing native input: " + name)
        require(sha(path) == expected, "Native bytes differ from the finalized manifest: " + name)
        native_paths[name] = path
    for name in PRIVATE_INPUTS:
        require(name in baseline_native and sha(native_paths[name]) == baseline_native[name], "Private R121 object/stub changed: " + name)
    pause_source = ROOT / "native/d1/native_pause_menu.h"
    require(native_path(pause_source).is_file() and native_paths.get("d1/native_pause_menu.h") == pause_source,
            "R122 must include its public native_pause_menu.h instead of restoring the old private header")
    native_hashes = {name: sha(path) for name, path in sorted(native_paths.items())}
    frontend_paths = {
        name: path for name, path in walk_files(ROOT / "frontend")
        if Path(name).suffix in (".h", ".hpp", ".cpp")
        and not any(part in ("baseline", "tests", "test", "__pycache__") for part in Path(name).parts)
    }
    require("station_frontend.cpp" in frontend_paths, "Missing current frontend source")
    frontend_hashes = {name: sha(path) for name, path in sorted(frontend_paths.items())}
    require(frontend_hashes == baseline_build["inputs"]["frontend"], "R122 must preserve every R121 frontend source")
    engine_path = ROOT / "assets/station-online/engines.json"
    require(native_path(engine_path).is_file(), "Missing current engine policy asset")
    require(sha(engine_path) == BASE_MEMBERS["assets/station-online/engines.json"], "R122 must preserve the R121 engine registry")
    inputs = {
        "java": java_hashes, "native": native_hashes, "frontend": frontend_hashes,
        "engines": sha(engine_path), "javaManifest": sha(ROOT / "JAVA-SOURCE-MANIFEST.json"),
        "nativeManifest": sha(ROOT / "CAROUSEL-INPUT-MANIFEST.json"),
        "baselineJavaManifest": BASE_JAVA_MANIFEST_SHA, "baselineNativeManifest": BASE_CAROUSEL_MANIFEST_SHA,
        "baselineBuildReceipt": BASE_BUILD_RECEIPT_SHA,
        "recipe": sha(ROOT / "build.py"),
    }
    return inputs, java_paths, native_paths, frontend_paths, baseline_java


def verify_base(args):
    require(native_path(args.base).is_file(), "Missing R121 APK")
    require(native_path(args.base).stat().st_size == BASE_BYTES, "Base APK size must match final R121")
    require(sha(args.base) == BASE_SHA, "Base APK must be the exact final R121 artifact")
    with zipfile.ZipFile(native_path(args.base)) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())), "Duplicate base ZIP entries")
        for name, digest in BASE_MEMBERS.items():
            require(zip_sha(archive, name) == digest, "Unexpected R121 payload: " + name)
        require(set(ALLOWED_PAYLOADS).issubset(archive.namelist()), "Missing replacement entry")


def tool_hashes(args):
    paths = {
        "javac": args.jdk / "javac.exe", "java": args.jdk / "java.exe",
        "androidJar": args.android_jar, "d8Jar": args.d8_jar,
        "clang": args.ndk / "clang++.exe", "nm": args.ndk / "llvm-nm.exe",
        "readelf": args.ndk / "llvm-readelf.exe",
        "aapt": args.aapt,
    }
    for name, path in paths.items():
        require(path.is_file(), "Missing " + name + ": " + str(path))
    hashes = {name: sha(path) for name, path in paths.items()}
    require(hashes["clang"] == CLANG_SHA, "Use the pinned NDK r28c compiler")
    return hashes


def changed_native_from_base(inventory):
    baseline = read_json(ROOT / "CAROUSEL-INPUT-MANIFEST-R121.json")
    return sorted(name for name, digest in inventory["native"].items() if baseline.get(name) != digest)


def verify_manifest_views(args, candidate, run):
    original = run([args.aapt, "dump", "xmltree", args.base, "AndroidManifest.xml"], "manifest-base-xmltree")
    actual = run([args.aapt, "dump", "xmltree", candidate, "AndroidManifest.xml"], "manifest-candidate-xmltree")
    original_lines, actual_lines = original.splitlines(), actual.splitlines()
    indexes = [index for index, line in enumerate(original_lines) if "appComponentFactory(0x0101057a)=" in line]
    require(len(indexes) == 1 and FACTORY in original_lines[indexes[0]], "Final R121 must already use StationComponentFactory")
    require(actual_lines == original_lines, "The entire R121 manifest XML tree must remain unchanged")
    application = re.search(r"^\s*E: application\b.*?\n(?P<attributes>(?:\s+A:.*\n)+)", original + "\n", re.M)
    require(application is not None, "Missing original Application XML view")
    application_name = re.search(r"^\s*A: android:name\(0x01010003\)=(.*)$", application.group("attributes"), re.M)
    require(application_name is not None, "Missing original Application class attribute")
    return {"applicationFactory": FACTORY, "originalApplicationPreserved": True,
            "entireXMLTreeIdentical": True, "manifestPatchApplied": False,
            "manifestSHA256": BASE_MEMBERS["AndroidManifest.xml"],
            "originalApplicationAttribute": application_name.group(1)}


def prepare(args):
    verify_base(args)
    inventory, _, _, _, baseline_java = source_inventory(args)
    tools = tool_hashes(args)
    stage = args.work / "prepare-verification"
    require(not stage.exists(), "Prepare verification directory exists; use a new --work path")
    stage.mkdir(parents=True)
    run, _ = runner(stage)
    manifest_evidence = verify_manifest_views(args, args.base, run)
    receipt = {
        "version": "R122-candidate", "phase": "prepare", "utc": utc(), "baseSHA256": BASE_SHA,
        "inputs": inventory, "toolSHA256": tools, "sourceCount": len(inventory["java"]),
        "changedJavaFromR121": sorted(name for name, digest in inventory["java"].items() if baseline_java.get(name) != digest),
        "changedNativeFromR121": changed_native_from_base(inventory),
        "manifestPreservedSHA256": BASE_MEMBERS["AndroidManifest.xml"],
        "manifestChecks": manifest_evidence,
        "compiled": False, "signed": False, "installed": False,
        "compileWork": str(args.work), "packageWork": str(args.package_work),
        "privateObjectsPreserved": True, "runtimeSHA256": BASE_MEMBERS["lib/arm64-v8a/libstation_retroarch.so"],
    }
    require(source_inventory(args)[0] == inventory, "Sources changed while preparing")
    write_json(args.work / "prepare-r122.json", receipt)
    print(json.dumps({"phase": "prepare", "passed": True, "javaSources": receipt["sourceCount"], "receipt": str(args.work / "prepare-r122.json")}))


def runner(out):
    temporary = out / "temp"
    temporary.mkdir(exist_ok=True)
    environment = dict(os.environ, TEMP=str(temporary), TMP=str(temporary))

    def run(command, label):
        result = subprocess.run(list(map(str, command)), capture_output=True, env=environment)
        (out / (label + ".log")).write_bytes(result.stdout + result.stderr)
        require(result.returncode == 0, label + " failed; inspect " + str(out / (label + ".log")))
        return result.stdout.decode("utf-8", "replace")
    return run, environment


def write_jar(classes, destination):
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(classes.rglob("*.class")):
            info = zipfile.ZipInfo(path.relative_to(classes).as_posix(), (2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())


def compile_sources(args):
    verify_base(args)
    inventory, java_paths, native_paths, _, baseline_java = source_inventory(args)
    tools = tool_hashes(args)
    out = args.work / "compiled-final"
    require(not out.exists(), "Compile directory already exists; use a new --work path")
    out.mkdir(parents=True)
    run, _ = runner(out)
    manifest_evidence = verify_manifest_views(args, args.base, run)
    prepared_receipt = args.work / "prepare-r122.json"
    if prepared_receipt.exists():
        prepared = read_json(prepared_receipt)
        require(prepared["inputs"] == inventory and prepared["baseSHA256"] == BASE_SHA, "Prepared sources/base changed before compilation")
        require(prepared["toolSHA256"] == tools, "Prepared build tools changed before compilation")
        require(prepared["manifestPreservedSHA256"] == BASE_MEMBERS["AndroidManifest.xml"], "Prepared manifest identity differs from R121")
    aliases = {}
    for index, (name, path) in enumerate(sorted(java_paths.items())):
        alias = out / "source-alias" / str(index) / Path(name).name
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.write_bytes(native_path(path).read_bytes())
        aliases[name] = alias

    def compile_module(module, prefixes, extra_classpath=None):
        classes = out / (module + "-classes")
        classes.mkdir()
        classpath = str(args.android_jar) + (os.pathsep + str(extra_classpath) if extra_classpath else "")
        options = ["-encoding", "UTF-8", "--release", "8", "-proc:none", "-cp", classpath, "-d", str(classes)]
        options += [str(aliases[name]) for name in sorted(aliases) if name.startswith(prefixes)]
        response = out / (module + ".args")
        response.write_text("\n".join('"' + value.replace("\\", "/") + '"' for value in options), encoding="utf-8")
        run([args.jdk / "javac.exe", "@" + str(response)], module + "-javac")
        jar = out / (module + ".jar")
        write_jar(classes, jar)
        destination = out / (module + "-dex")
        destination.mkdir()
        command = [args.jdk / "java.exe", "-cp", args.d8_jar, "com.android.tools.r8.D8", "--min-api", "26", "--lib", args.android_jar]
        if extra_classpath:
            command += ["--classpath", extra_classpath]
        run(command + ["--output", destination, jar], module + "-d8")
        require(sorted(path.name for path in destination.glob("*.dex")) == ["classes.dex"], module + " unexpectedly produced multiple DEX files")
        return destination / "classes.dex", jar

    client_dex, client_jar = compile_module("client", ("client/src/java/",))
    rooms_dex, _ = compile_module("rooms", ("netplay-src/", "dependency-src/"), client_jar)
    stage = out / "native-inputs"
    for name, path in native_paths.items():
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(native_path(path), destination)
    frontend = out / "libstation_frontend.so"
    carousel = out / "libturbo_carousel.so"
    common = [args.ndk / "clang++.exe", "--target=aarch64-linux-android26", "-std=c++17", "-shared", "-fPIC", "-O2", "-Wl,-z,max-page-size=16384", "-Wl,--no-undefined"]
    run(common + ["-fvisibility=hidden", "-Wall", "-Wextra", "-Werror", "-Wno-return-type-c-linkage", "-static-libstdc++", "-Wl,--exclude-libs,ALL", "-I", ROOT / "frontend", ROOT / "frontend/station_frontend.cpp", "-ldl", "-llog", "-o", frontend], "frontend-clang")
    run(common + ["-nostdlib", "-fno-exceptions", "-fno-rtti", "-fno-stack-protector", "-fno-builtin", "-Wl,-soname,libturbo_carousel.so", "-I", stage / "d2", "-I", stage / "d1", stage / "d0/native_carousel.cpp", stage / "d1/video720_posters.o", stage / "d3/collection_previews.o", stage / "d4/lottie_frames.o", "-L", stage / "d1", "-lc", "-ldl", "-llog", stage / "d5/installed_art.o", "-o", carousel, stage / "d6/collection_previews.o", stage / "d7/collection_previews.o", stage / "d8/collection_previews.o"], "carousel-clang")

    def exports(path, label):
        result = run([args.ndk / "llvm-nm.exe", "--dynamic", "--defined-only", path], label)
        return {line.split()[-1] for line in result.splitlines() if len(line.split()) >= 3}

    export_checks = {}
    with zipfile.ZipFile(native_path(args.base)) as archive:
        for short, built in (("frontend", frontend), ("carousel", carousel)):
            name = "lib/arm64-v8a/" + built.name
            base_library = out / ("base-" + built.name)
            with archive.open(name) as source, base_library.open("wb") as target:
                shutil.copyfileobj(source, target, 1024 * 1024)
            old_exports, new_exports = exports(base_library, short + "-base-exports"), exports(built, short + "-new-exports")
            require(old_exports.issubset(new_exports), "Removed native exports: " + short)
            headers = run([args.ndk / "llvm-readelf.exe", "-lW", built], short + "-program-headers")
            alignments = re.findall(r"^\s*LOAD\s+.*\s(0x[0-9a-fA-F]+)\s*$", headers, re.M)
            require(alignments and all(int(value, 16) >= 16384 for value in alignments), "Native LOAD alignment below 16KiB: " + short)
            export_checks[short] = {"oldExportsPreserved": True, "addedExports": sorted(new_exports - old_exports), "loadAlignment16KiB": True}
            base_library.unlink()
    payloads = {"classes28.dex": client_dex, "classes35.dex": rooms_dex, "lib/arm64-v8a/libturbo_carousel.so": carousel}
    require(set(payloads) == set(ALLOWED_PAYLOADS), "Unexpected R122 compiled payload")
    require(all(sha(payloads[name]) != BASE_MEMBERS[name] for name in REQUIRED_CHANGES), "One required R122 payload remained R121")
    require(sha(frontend) == BASE_MEMBERS["lib/arm64-v8a/libstation_frontend.so"], "Unchanged frontend must remain byte-identical to R121")
    require(source_inventory(args)[0] == inventory, "Sources changed while compiling; discard this candidate and compile finalized sources")
    receipt = {
        "version": "R122-candidate", "phase": "compile", "utc": utc(), "baseSHA256": BASE_SHA,
        "inputs": inventory, "toolSHA256": tools, "javaSourceCount": len(aliases),
        "changedJavaFromR121": sorted(name for name, digest in inventory["java"].items() if baseline_java.get(name) != digest),
        "changedNativeFromR121": changed_native_from_base(inventory),
        "payloads": {name: {"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size} for name, path in payloads.items()},
        "nativeExportChecks": export_checks, "privateObjectsPreserved": True,
        "manifestChecks": manifest_evidence, "unchangedFrontendSHA256": sha(frontend),
        "manifestPreservedSHA256": BASE_MEMBERS["AndroidManifest.xml"],
        "runtimeSHA256": BASE_MEMBERS["lib/arm64-v8a/libstation_retroarch.so"],
        "compiled": True, "signed": False, "installed": False, "physicalVerified": False,
        "testsExecutedByThisRecipe": False,
    }
    write_json(out / "compile-receipt.json", receipt)
    write_json(ROOT / "evidence/build-r122.json", receipt)
    print(json.dumps({"phase": "compile", "passed": True, "javaSources": len(aliases), "receipt": str(out / "compile-receipt.json")}))


def package(args):
    verify_base(args)
    out = args.work / "compiled-final"
    compile_receipt = read_json(out / "compile-receipt.json")
    require(compile_receipt.get("version") == "R122-candidate" and compile_receipt.get("compiled") is True and compile_receipt.get("baseSHA256") == BASE_SHA, "Missing R122 compilation receipt")
    require(source_inventory(args)[0] == compile_receipt["inputs"], "Compiled sources changed before packaging")
    require(tool_hashes(args) == compile_receipt["toolSHA256"], "Compiled build tools changed before packaging")
    payloads = {name: Path(item["path"]) for name, item in compile_receipt["payloads"].items()}
    for name, path in payloads.items():
        require(sha(path) == compile_receipt["payloads"][name]["sha256"], "Compiled payload changed: " + name)
    require(set(payloads) == set(ALLOWED_PAYLOADS), "Unexpected replacement payload")
    require(args.zipalign and args.apksigner and args.keystore and args.key_alias, "Packaging requires explicit signing tools, keystore, and alias")
    require(args.zipalign.is_file() and args.apksigner.is_file() and args.keystore.is_file(), "Missing explicit signing tool or keystore")
    require(os.environ.get(args.ks_pass_env) and os.environ.get(args.key_pass_env), "Supply signing passwords through the selected environment variables; no password default is supplied")
    require(not args.output.exists(), "Final output exists; refusing to overwrite an artifact")
    require(not args.package_work.exists(), "Package work exists; select a new --package-work path")
    require(args.package_work != args.work and args.package_work not in args.output.parents, "Package temporary directory must be separate from the final output and compile work")
    args.package_work.mkdir(parents=True)
    run, environment = runner(args.package_work)
    certificate = subprocess.run([str(args.jdk / "keytool.exe"), "-exportcert", "-keystore", str(args.keystore), "-alias", args.key_alias, "-storepass:env", args.ks_pass_env], capture_output=True, env=environment)
    require(certificate.returncode == 0 and hashlib.sha256(certificate.stdout).hexdigest() == CERT_SHA, "Signing key must match the installed R121 certificate")
    unsigned, aligned, signed = (args.package_work / name for name in ("unsigned.apk", "aligned.apk", "signed.apk"))
    with zipfile.ZipFile(native_path(args.base)) as old, zipfile.ZipFile(unsigned, "w", allowZip64=True) as new:
        for info in old.infolist():
            if signature(info.filename):
                continue
            item = copy.copy(info)
            item.extra = b""
            source = native_path(payloads[item.filename]).open("rb") if item.filename in payloads else old.open(info)
            if item.filename in payloads:
                item.file_size = payloads[item.filename].stat().st_size
            with source, new.open(item, "w", force_zip64=False) as target:
                shutil.copyfileobj(source, target, 1024 * 1024)
    run([args.zipalign, "-P", "16", "-f", "4", unsigned, aligned], "zipalign")
    unsigned.unlink()
    run([args.jdk / "java.exe", "-jar", args.apksigner, "sign", "--v4-signing-enabled", "false", "--ks", args.keystore, "--ks-key-alias", args.key_alias, "--ks-pass", "env:" + args.ks_pass_env, "--key-pass", "env:" + args.key_pass_env, "--out", signed, aligned], "sign")
    verification = run([args.jdk / "java.exe", "-jar", args.apksigner, "verify", "--verbose", "--print-certs", signed], "verify")
    require(re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([a-f0-9]{64})\s*$", verification, re.M) == [CERT_SHA], "APK signer certificate changed")
    require("Verified using v2 scheme (APK Signature Scheme v2): true" in verification and "Verified using v3 scheme (APK Signature Scheme v3): true" in verification, "APK v2/v3 verification failed")
    run([args.zipalign, "-c", "-P", "16", "4", signed], "alignment")
    changes = []
    preserved = 0
    with zipfile.ZipFile(native_path(args.base)) as old, zipfile.ZipFile(signed) as new:
        old_names = {name for name in old.namelist() if not signature(name)}
        new_names = {name for name in new.namelist() if not signature(name)}
        require(new_names == old_names and len(new.namelist()) == len(set(new.namelist())), "APK entry set changed")
        for name in sorted(new_names):
            original, actual = zip_sha(old, name), zip_sha(new, name)
            if name in payloads:
                require(actual == sha(payloads[name]), "Replacement mismatch: " + name)
                if actual != original:
                    changes.append(name)
            else:
                require(actual == original, "Unexpected APK content change: " + name)
                preserved += 1
        require(REQUIRED_CHANGES.issubset(changes) and set(changes).issubset(ALLOWED_PAYLOADS), "Only two DEX modules and carousel UI may change in R122; rooms/carousel changes are required")
        require(zip_sha(new, "AndroidManifest.xml") == BASE_MEMBERS["AndroidManifest.xml"], "R121 manifest changed; no factory patch is permitted in R122")
        require(zip_sha(new, "lib/arm64-v8a/libstation_retroarch.so") == BASE_MEMBERS["lib/arm64-v8a/libstation_retroarch.so"], "Emulator runtime changed")
        require(zip_sha(new, "lib/arm64-v8a/libstation_frontend.so") == BASE_MEMBERS["lib/arm64-v8a/libstation_frontend.so"], "Frontend library changed")
        require(zip_sha(new, "assets/station-online/engines.json") == BASE_MEMBERS["assets/station-online/engines.json"], "Engine policy changed")
    manifest_evidence = verify_manifest_views(args, signed, run)
    require(compile_receipt["manifestPreservedSHA256"] == BASE_MEMBERS["AndroidManifest.xml"], "Missing R121 manifest preservation identity")
    require(source_inventory(args)[0] == compile_receipt["inputs"], "Sources changed while packaging")
    expected_sha = sha(signed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(signed, args.output)
    require(sha(args.output) == expected_sha, "Final APK copy hash mismatch")
    signed.unlink()
    aligned.unlink()
    receipt = {
        "version": "R122-candidate", "phase": "package", "utc": utc(), "sourceBaseVersion": "R121",
        "baseSHA256": BASE_SHA, "apk": str(args.output), "sha256": expected_sha, "bytes": args.output.stat().st_size,
        "certificateSHA256": CERT_SHA, "signatureV2V3Passed": True, "zipAlignment16KiBPassed": True,
        "changedEntries": changes, "preservedEntries": preserved, "allOtherEntriesByteIdentical": True,
        "manifestChecks": manifest_evidence, "manifestPreservedByteIdentical": True,
        "frontendPreservedByteIdentical": True, "engineRegistryPreservedByteIdentical": True,
        "runtimeSHA256": BASE_MEMBERS["lib/arm64-v8a/libstation_retroarch.so"],
        "compileReceiptSHA256": sha(out / "compile-receipt.json"), "javaSourceCount": compile_receipt["javaSourceCount"],
        "compiled": True, "signed": True, "installed": False, "physicalVerified": False, "gameplayValidated": False,
    }
    write_json(ROOT / "evidence/package-r122.json", receipt)
    write_json(args.package_work / "package-receipt.json", receipt)
    print(json.dumps(receipt, indent=2))


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--compile", action="store_true")
    mode.add_argument("--package", action="store_true")
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--package-work", type=Path, required=True)
    parser.add_argument("--jdk", type=Path, required=True, help="JDK root or bin directory")
    parser.add_argument("--android-jar", type=Path, required=True)
    parser.add_argument("--d8-jar", type=Path, required=True)
    parser.add_argument("--aapt", type=Path, required=True, help="Pinned Android aapt.exe for binary manifest XML-tree verification")
    parser.add_argument("--ndk", type=Path, required=True, help="NDK root or LLVM bin directory")
    parser.add_argument("--native-inputs", type=Path, default=ROOT / "native", help="Existing private inputs; current ROOT/native files take precedence")
    parser.add_argument("--zipalign", type=Path)
    parser.add_argument("--apksigner", type=Path, help="apksigner.jar")
    parser.add_argument("--keystore", type=Path)
    parser.add_argument("--key-alias")
    parser.add_argument("--ks-pass-env", default="STATION_KS_PASS")
    parser.add_argument("--key-pass-env", default="STATION_KEY_PASS")
    args = parser.parse_args()
    for name in ("base", "work", "output", "package_work", "android_jar", "d8_jar", "aapt", "native_inputs", "zipalign", "apksigner", "keystore"):
        value = getattr(args, name)
        if value is not None:
            setattr(args, name, value.resolve())
    args.jdk = tool_directory(args.jdk, "javac.exe", "bin")
    args.ndk = tool_directory(args.ndk, "clang++.exe", "toolchains/llvm/prebuilt/windows-x86_64/bin")
    require(args.output != args.base, "Output must not overwrite the base APK")
    return args


def main():
    args = arguments()
    if args.prepare:
        prepare(args)
    elif args.compile:
        compile_sources(args)
    else:
        package(args)


if __name__ == "__main__":
    main()
