"""Isolated component delegation and exact R119 binary-manifest checks.

Compiles only unmodified StationComponentFactory/StationControllerPresence and host
fixtures. Temporary stubs/classes never enter production manifests, DEX or APKs.
"""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "java/client/src/java/org/emulationstation/frontend/station"
BASE_SHA = "f5d0e434cb383a7103c77fd1e853b9f4721d283c30941860a21f1831bf6be674"
MANIFEST_SHA = "3a821dccd8a9853acd345f106614ec955bbf66b681b7690f907348569e8bef0d"
OLD = "androidx.core.app.CoreComponentFactory"
NEW = "org.emulationstation.frontend.station.StationComponentFactory"
ATTRIBUTE = 0x0101057A

EXTRA_STUBS = {
    "android/content/Intent.java": "package android.content; public class Intent {}",
    "android/content/BroadcastReceiver.java": "package android.content; public class BroadcastReceiver {}",
    "android/content/ContentProvider.java": "package android.content; public class ContentProvider {}",
    "android/content/pm/ApplicationInfo.java": "package android.content.pm; public class ApplicationInfo {}",
    "android/app/Service.java": "package android.app; public class Service {}",
    "android/app/AppComponentFactory.java": """package android.app;
import android.content.*;import android.content.pm.ApplicationInfo;
public class AppComponentFactory {
 public ClassLoader instantiateClassLoader(ClassLoader l,ApplicationInfo i){throw new AssertionError("unexpected superclass fallback");}
 public Application instantiateApplication(ClassLoader l,String n)throws InstantiationException,IllegalAccessException,ClassNotFoundException{throw new AssertionError("unexpected superclass fallback");}
 public Activity instantiateActivity(ClassLoader l,String n,Intent i)throws InstantiationException,IllegalAccessException,ClassNotFoundException{throw new AssertionError("unexpected superclass fallback");}
 public Service instantiateService(ClassLoader l,String n,Intent i)throws InstantiationException,IllegalAccessException,ClassNotFoundException{throw new AssertionError("unexpected superclass fallback");}
 public BroadcastReceiver instantiateReceiver(ClassLoader l,String n,Intent i)throws InstantiationException,IllegalAccessException,ClassNotFoundException{throw new AssertionError("unexpected superclass fallback");}
 public ContentProvider instantiateProvider(ClassLoader l,String n)throws InstantiationException,IllegalAccessException,ClassNotFoundException{throw new AssertionError("unexpected superclass fallback");}
} """,
    "androidx/core/app/CoreComponentFactory.java": """package androidx.core.app;
import android.app.*;import android.content.*;import android.content.pm.ApplicationInfo;import java.util.concurrent.atomic.AtomicInteger;
public class CoreComponentFactory extends AppComponentFactory {
 public static final AtomicInteger constructions=new AtomicInteger();
 public static Application application=new Application();public static final Activity activity=new Activity();public static final Service service=new Service();
 public static final BroadcastReceiver receiver=new BroadcastReceiver();public static final ContentProvider provider=new ContentProvider();
 public static final ClassLoader resultLoader=new ClassLoader(){};public static ClassLoader lastLoader;public static String lastName;public static Intent lastIntent;public static ApplicationInfo lastInfo;
 public static InstantiationException failure;public static RuntimeException loaderFailure;
 public CoreComponentFactory(){constructions.incrementAndGet();}
 private static void arguments(ClassLoader l,String n,Intent i)throws InstantiationException{lastLoader=l;lastName=n;lastIntent=i;if(failure!=null)throw failure;}
 @Override public ClassLoader instantiateClassLoader(ClassLoader l,ApplicationInfo i){lastLoader=l;lastInfo=i;if(loaderFailure!=null)throw loaderFailure;return resultLoader;}
 @Override public Application instantiateApplication(ClassLoader l,String n)throws InstantiationException{arguments(l,n,null);return application;}
 @Override public Activity instantiateActivity(ClassLoader l,String n,Intent i)throws InstantiationException{arguments(l,n,i);return activity;}
 @Override public Service instantiateService(ClassLoader l,String n,Intent i)throws InstantiationException{arguments(l,n,i);return service;}
 @Override public BroadcastReceiver instantiateReceiver(ClassLoader l,String n,Intent i)throws InstantiationException{arguments(l,n,i);return receiver;}
 @Override public ContentProvider instantiateProvider(ClassLoader l,String n)throws InstantiationException{arguments(l,n,null);return provider;}
} """,
}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def presence_stubs():
    recipe = ROOT / "tests/verify_controller_presence_r120.py"
    tree = ast.parse(recipe.read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "STUBS" for target in node.targets):
            return ast.literal_eval(node.value), sha(recipe)
    raise RuntimeError("Missing isolated Android API fixtures")


def run(command, label, directory):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, encoding="utf-8", errors="replace")
    (directory / (label + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(label + " failed: " + result.stderr)
    return result.stdout


def java_checks(args, directory):
    stubs, stubs_sha = presence_stubs()
    stubs.update(EXTRA_STUBS)
    for name, source in stubs.items():
        path = directory / "src" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
    source_sha = {}
    for name in ("StationComponentFactory.java", "StationControllerPresence.java"):
        original = SOURCE_ROOT / name
        target = directory / "src/org/emulationstation/frontend/station" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original.read_bytes())
        source_sha[name] = sha(original)
        assert sha(target) == source_sha[name]
    fixture = ROOT / "tests/fixtures/ComponentFactoryR120Test.java"
    fixture_target = directory / "src/org/emulationstation/frontend/station/ComponentFactoryR120Test.java"
    fixture_target.write_bytes(fixture.read_bytes())
    response = directory / "sources.args"
    response.write_text('\n'.join('"' + str(path).replace("\\", "/") + '"' for path in sorted((directory / "src").rglob("*.java"))), encoding="utf-8")
    jdk = args.jdk / "bin" if (args.jdk / "bin/javac.exe").is_file() else args.jdk
    run([jdk / "javac.exe", "--release", "8", "-encoding", "UTF-8", "-proc:none", "-d", directory / "classes", "@" + str(response)], "factory-javac", directory)
    output = run([jdk / "java.exe", "-cp", directory / "classes", "org.emulationstation.frontend.station.ComponentFactoryR120Test"], "factory-java", directory).strip()
    match = re.fullmatch(r"PASS (\d+) checks \(real factory/presence; host API stubs; no Android/gameplay\)", output)
    if not match:
        raise RuntimeError("Unexpected component factory fixture result")
    for name, digest in source_sha.items():
        assert sha(SOURCE_ROOT / name) == digest, "Production source changed during verification"
    return {"checks": int(match.group(1)), "result": output, "sourceSHA256": source_sha,
            "fixtureSHA256": sha(fixture), "reusedAndroidStubRecipeSHA256": stubs_sha,
            "realFactoryAndPresenceCompiledUnmodified": True}


def factory_attributes(data, patch):
    chunks = list(patch["chunks"](data))
    pools = [chunk for chunk in chunks if chunk[1] == 1]
    resources = [chunk for chunk in chunks if chunk[1] == 0x180]
    if len(pools) != 1 or len(resources) != 1:
        raise RuntimeError("Ambiguous AXML pool/resource map")
    pool = pools[0]
    strings = patch["string_pool"](data, pool[0])
    ro, _, rh, rs = resources[0]
    ids = struct.unpack_from("<" + "I" * ((rs - rh) // 4), data, ro + rh)
    targets = []
    for offset, kind, header, size in chunks:
        if kind != 0x102 or strings[struct.unpack_from("<I", data, offset + 20)[0]] != "application":
            continue
        start, width, count = struct.unpack_from("<HHH", data, offset + 24)
        if width != 20:
            raise RuntimeError("Unexpected AXML attribute width")
        for index in range(count):
            attr = offset + 16 + start + index * width
            resource_index = struct.unpack_from("<I", data, attr + 4)[0]
            if resource_index < len(ids) and ids[resource_index] == ATTRIBUTE:
                value_index = struct.unpack_from("<I", data, attr + 16)[0]
                targets.append((attr, strings[value_index]))
    return chunks, pool, strings, targets


def manifest_checks(args, directory):
    checks = 0
    def check(value, message):
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(message)
    check(sha(args.base) == BASE_SHA, "Exact R119 APK required")
    patch_path = ROOT / "recipes/patch_component_factory.py"
    patch = {"__name__": "isolated_factory_manifest", "__file__": str(patch_path)}
    exec(compile(patch_path.read_bytes(), str(patch_path), "exec"), patch)
    check(patch["OLD"] == OLD and patch["NEW"] == NEW, "Factory identities differ")
    with zipfile.ZipFile(args.base) as archive:
        original = archive.read("AndroidManifest.xml")
        check(hashlib.sha256(original).hexdigest() == MANIFEST_SHA, "Exact R119 manifest required")
        patched = patch["patch_manifest"](original)
        before, old_pool, old_strings, old_targets = factory_attributes(original, patch)
        after, new_pool, new_strings, new_targets = factory_attributes(patched, patch)
        check(len(old_targets) == 1 and old_targets[0][1] == OLD, "Original must have one application factory")
        check(len(new_targets) == 1 and new_targets[0][1] == NEW, "Candidate must have one application factory")
        check(new_strings[:-1] == old_strings and new_strings[-1] == NEW, "Existing strings changed")
        check(len(before) == len(after), "AXML chunk count changed")
        restored_chunks = []
        changed_non_pool = 0
        for old_chunk, new_chunk in zip(before, after):
            old_offset, old_kind, old_header, old_size = old_chunk
            new_offset, new_kind, new_header, new_size = new_chunk
            check(old_kind == new_kind and old_header == new_header, "AXML chunk kind/header changed")
            old_bytes = original[old_offset:old_offset + old_size]
            new_bytes = bytearray(patched[new_offset:new_offset + new_size])
            if old_kind == 1:
                restored_chunks.append(old_bytes)
                continue
            check(old_size == new_size, "Non-pool AXML chunk size changed")
            if old_offset <= old_targets[0][0] < old_offset + old_size:
                changed_non_pool += int(bytes(new_bytes) != old_bytes)
                relative = new_targets[0][0] - new_offset
                new_bytes[relative:relative + 20] = original[old_targets[0][0]:old_targets[0][0] + 20]
            check(bytes(new_bytes) == old_bytes, "Non-factory AXML bytes changed")
            restored_chunks.append(bytes(new_bytes))
        restored = bytearray(patched[:8] + b"".join(restored_chunks))
        struct.pack_into("<I", restored, 4, len(restored))
        check(bytes(restored) == original, "Independent reverse identity failed")
        check(changed_non_pool == 1, "More than one component chunk changed")
        try:
            patch["patch_manifest"](patched)
        except AssertionError:
            check(True, "Already changed factory rejected")
        else:
            check(False, "Already changed factory was accepted")
        probe = directory / "manifest-probe.apk"
        with zipfile.ZipFile(probe, "w", zipfile.ZIP_STORED) as candidate:
            candidate.writestr("AndroidManifest.xml", patched)
            candidate.writestr("resources.arsc", archive.read("resources.arsc"))
    original_tree = run([args.aapt, "dump", "xmltree", args.base, "AndroidManifest.xml"], "manifest-original-aapt", directory).splitlines()
    candidate_tree = run([args.aapt, "dump", "xmltree", probe, "AndroidManifest.xml"], "manifest-candidate-aapt", directory).splitlines()
    factory_lines = [i for i, line in enumerate(original_tree) if "appComponentFactory(0x0101057a)=" in line]
    check(len(factory_lines) == 1, "Original XML tree factory is ambiguous")
    expected_tree = list(original_tree)
    expected_tree[factory_lines[0]] = expected_tree[factory_lines[0]].replace(OLD, NEW)
    check(candidate_tree == expected_tree, "Only one attribute line may change in aapt XML tree")
    check(sum(a != b for a, b in zip(original_tree, candidate_tree)) == 1, "Unexpected XML tree change count")
    return {"checks": checks, "baseAPK_SHA256": BASE_SHA, "originalManifestSHA256": MANIFEST_SHA,
            "patchedManifestSHA256": hashlib.sha256(patched).hexdigest(), "manifestBytesDelta": len(patched) - len(original),
            "independentBinaryReverseIdentityPassed": True, "allOtherXMLTreeLinesIdentical": True,
            "onlyApplicationFactoryAttributeChanged": True, "patchSHA256": sha(patch_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--aapt", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError("Python assertion guards must remain enabled")
    args.work = args.work.resolve()
    args.work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="factory-isolated-r120-", dir=args.work) as temporary:
        directory = Path(temporary).resolve()
        if not directory.is_relative_to(args.work):
            raise RuntimeError("Temporary directory escaped intended verification work")
        java = java_checks(args, directory)
        manifest = manifest_checks(args, directory)
    evidence = {"version": "R120", "scope": "Isolated host API stubs and exact R119 AXML; no phone/gameplay",
                "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "passed": True, "java": java, "manifest": manifest,
                "totalChecks": java["checks"] + manifest["checks"],
                "recipeSHA256": sha(Path(__file__)), "aaptSHA256": sha(args.aapt),
                "temporaryStubsExcludedFromProductionSourcesAndAPK": True}
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "javaChecks": java["checks"], "manifestChecks": manifest["checks"],
                      "totalChecks": evidence["totalChecks"], "manifestBytesDelta": manifest["manifestBytesDelta"],
                      "evidence": str(args.evidence)}))


if __name__ == "__main__":
    main()
