from pathlib import Path
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
REPO = ROOT.parents[1]
BASE_JAVA_MANIFEST = ROOT / "JAVA-SOURCE-MANIFEST-R115.json"
BASE_JAVA_MANIFEST_SHA = "dc9e59a18f46e211cd00456f32ea75079a5ad68af11f9e9767ecde95277f57c1"
WORK = Path(r"E:\ESTUDO APK\work\station-legacy-cover-diagnostics-r116-20261010")
BASE = Path(r"G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R115-20261010.apk")
FINAL = Path(r"G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R116-20261010.apk")
BASE_SHA = "290b9e237c8ad158aac443ce5c11959004f7a28ab4844c4c3453721a288f0dcc"
BASE_MEMBERS = {
    "classes28.dex": "283f1583f064c4e2058bada9a6bf9cc84a0bfb31b30d6b50043afcd0fe272961",
    "classes35.dex": "e89f74ece71570fb008a6f70e04db6979deea03ad22f9fa2ea309ebdd0e3128b",
    "lib/arm64-v8a/libturbo_carousel.so": "8b774382c71b18100fb2e70bd9d553307cabe615fcb6aaecc3047bb612d4b3a5",
    "lib/arm64-v8a/libstation_frontend.so": "3c9d6bfba6ef08ad4909c6e1338c7a2ccd5cf46f9bf0c9bf895910093d3c8b1e",
    "lib/arm64-v8a/libstation_retroarch.so": "81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc",
}
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
LONG_JAVA = "dependency-src/org/emulationstation/frontend/relay/ws/extensions/permessage_deflate/PerMessageDeflateExtension.java"
WINDOWS_LONG_JAVA = "dependency-src/org/emulationstation/frontend/relay/ws/server/SSLParametersWebSocketServerFactory.java"
EXTRA_LONG_JAVA = "dependency-src/org/emulationstation/frontend/relay/ws/exceptions/WebsocketNotConnectedException.java"
CHANGED_JAVA = sorted([
    "client/src/java/org/emulationstation/frontend/station/ExistingCoverCache.java",
    "client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java",
    "client/src/java/org/emulationstation/frontend/station/StationCoverStore.java",
    "client/src/java/org/emulationstation/frontend/station/StationDownloadPanel.java",
    "client/src/java/org/emulationstation/frontend/station/StationFrontend.java",
    "netplay-src/org/emulationstation/frontend/netplay/StationRoomArtwork.java",
    "netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java",
])


def native_path(path):
    path = Path(path)
    return Path("\\\\?\\" + str(path.resolve())) if os.name == "nt" else path


def sha(path):
    with native_path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def zip_sha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def signature(name):
    return name.startswith("META-INF/") and name.upper().endswith((".MF", ".SF", ".RSA", ".DSA", ".EC"))


def write_jar(classes, destination):
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(Path(classes).rglob("*.class")):
            info = zipfile.ZipInfo(path.relative_to(classes).as_posix(), (2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())


def main():
    assert ROOT.name == "station-legacy-cover-diagnostics-r116-20261010"
    assert sha(BASE) == BASE_SHA and not FINAL.exists()
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / "compiled-final"
    assert not out.exists()
    out.mkdir()
    temporary = out / "temp"
    temporary.mkdir()
    environment = dict(os.environ, TEMP=str(temporary), TMP=str(temporary))

    def run(command, label, cwd=None):
        result = subprocess.run(list(map(str, command)), cwd=cwd, capture_output=True, env=environment)
        (out / (label + ".log")).write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(label + " failed: " + (result.stdout + result.stderr).decode("utf-8", "replace")[-5000:])
        return result.stdout.decode("utf-8", "replace")

    assert sha(BASE_JAVA_MANIFEST) == BASE_JAVA_MANIFEST_SHA
    base_manifest = json.loads(BASE_JAVA_MANIFEST.read_text(encoding="utf-8"))
    source_paths, source_hashes = {}, {}
    for name in sorted(base_manifest):
        path = ROOT / "java" / name
        if name == LONG_JAVA:
            path = ROOT / "java-alias/PerMessageDeflateExtension.java"
        elif name == EXTRA_LONG_JAVA:
            path = ROOT / "java-alias/WebsocketNotConnectedException.java"
        elif name == WINDOWS_LONG_JAVA:
            alias = WORK / "source-alias/SSLParametersWebSocketServerFactory.java"
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.write_bytes(native_path(path).read_bytes())
            path = alias
        source_paths[name] = path
        source_hashes[name] = sha(path)
    assert len(source_hashes) == 226 and set(source_hashes) == set(base_manifest)
    changed_java = sorted(name for name in source_hashes if source_hashes[name] != base_manifest[name])
    assert changed_java == CHANGED_JAVA
    frontend_java = (ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java").read_text(encoding="utf-8")
    cover_java = (ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationCoverStore.java").read_text(encoding="utf-8")
    assert "catch(java.io.InterruptedIOException cancelled)" in frontend_java and "throw cancelled;" in frontend_java
    assert "images.prefetchCatalog(coldCovers.values())" in frontend_java
    download_panel_java = (ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationDownloadPanel.java").read_text(encoding="utf-8")
    assert "StationFrontend.coverWork" in download_panel_java
    assert "delayedCoverRetries" in download_panel_java and "main.removeCallbacks(retry)" in download_panel_java
    assert "StationFrontend.coverWork" in (ROOT / "java/netplay-src/org/emulationstation/frontend/netplay/StationRoomArtwork.java").read_text(encoding="utf-8")
    assert "WARM_REMOTE_ATTEMPTS_PER_LAUNCH=64" in cover_java and "WARM_WALL_NANOS=TimeUnit.SECONDS.toNanos(20)" in cover_java

    jdk = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin")
    android = Path(r"G:\Android\Sdk\platforms\android-34\android.jar")
    d8 = Path(r"G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar")

    def compile_module(module, prefixes, extra_classpath=None):
        classes = out / (module + "-classes")
        classes.mkdir()
        classpath = str(android) + (os.pathsep + str(extra_classpath) if extra_classpath else "")
        options = ["-encoding", "UTF-8", "--release", "8", "-proc:none", "-cp", classpath, "-d", str(classes)]
        options += [str(source_paths[name]) for name in sorted(source_hashes) if name.startswith(prefixes)]
        args = out / (module + ".args")
        args.write_text("\n".join('"' + value.replace("\\", "/") + '"' for value in options), encoding="utf-8")
        run([jdk / "javac.exe", "@" + str(args)], module + "-javac")
        jar = out / (module + ".jar")
        write_jar(classes, jar)
        return classes, jar

    client_classes, client_jar = compile_module("client", ("client/src/java/",))
    _, rooms_jar = compile_module("rooms", ("netplay-src/", "dependency-src/"), client_jar)

    def dex(module, jar, classpath=None):
        destination = out / (module + "-dex")
        destination.mkdir()
        command = [jdk / "java.exe", "-cp", d8, "com.android.tools.r8.D8", "--min-api", "26", "--lib", android]
        if classpath:
            command += ["--classpath", classpath]
        command += ["--output", destination, jar]
        run(command, module + "-d8")
        result = destination / "classes.dex"
        assert result.is_file()
        return result

    client_dex = dex("client", client_jar)
    rooms_dex = dex("rooms", rooms_jar, client_jar)

    test_classes = out / "test-classes"
    test_classes.mkdir()
    tests = [ROOT / "tests/StationResourceBundleTest.java", ROOT / "tests/StationCoverWarmStartTest.java",
             ROOT / "tests/ExistingCoverCacheDiagnosticsTest.java", ROOT / "tests/StationCoverPrefetchTest.java"]
    test_compile_cp = str(client_classes) + os.pathsep + str(android)
    run([jdk / "javac.exe", "-encoding", "UTF-8", "--release", "8", "-proc:none", "-cp", test_compile_cp, "-d", test_classes] + tests, "java-tests-javac")
    test_cp = str(client_classes) + os.pathsep + str(test_classes) + os.pathsep + str(android)
    resource_output = run([jdk / "java.exe", "-cp", test_cp, "org.emulationstation.frontend.station.StationResourceBundleTest", out / "resource-fixture"], "resource-test").strip()
    warm_output = run([jdk / "java.exe", "-cp", test_cp, "org.emulationstation.frontend.station.StationCoverWarmStartTest", out / "warm-fixture"], "warm-java-test").strip()
    diagnostics_output = run([jdk / "java.exe", "-cp", test_cp, "org.emulationstation.frontend.station.ExistingCoverCacheDiagnosticsTest", out / "legacy-diagnostics-fixture"], "legacy-diagnostics-test").strip()
    prefetch_output = run([jdk / "java.exe", "-cp", test_cp, "org.emulationstation.frontend.station.StationCoverPrefetchTest"], "cover-prefetch-test").strip()
    assert resource_output.startswith("PASS ")
    assert warm_output.startswith("PASS ") and "legacy-direct=executed" in warm_output
    assert diagnostics_output.startswith("PASS ") and "aggregate legacy-cover diagnostics" in diagnostics_output
    assert prefetch_output.startswith("PASS ") and "one-lane cover prefetch" in prefetch_output

    host = Path(r"C:\Program Files\LLVM\bin")
    native_test = out / "warm_cover_test.exe"
    run([host / "clang++.exe", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-I", ROOT / "frontend", ROOT / "frontend/tests/warm_cover_test.cpp", "-o", native_test], "warm-native-compile")
    native_warm_output = run([native_test], "warm-native-test").strip()
    assert native_warm_output == "PASS 26 native warm-cover checks"

    with zipfile.ZipFile(BASE) as base_zip:
        for name, digest in BASE_MEMBERS.items():
            assert zip_sha(base_zip, name) == digest
    payloads = {"classes28.dex": client_dex, "classes35.dex": rooms_dex}
    assert all(sha(path) != BASE_MEMBERS[name] for name, path in payloads.items())

    tools = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
    key = Path(r"C:\Users\Admin\.android\debug.keystore")
    environment["STATION_KS_PASS"] = environment.get("STATION_KS_PASS", "android")
    environment["STATION_KEY_PASS"] = environment.get("STATION_KEY_PASS", "android")
    certificate = subprocess.run([jdk / "keytool.exe", "-exportcert", "-keystore", key, "-alias", "androiddebugkey", "-storepass:env", "STATION_KS_PASS"], capture_output=True, env=environment)
    assert certificate.returncode == 0 and hashlib.sha256(certificate.stdout).hexdigest() == CERT_SHA
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    package = FINAL.parent / "r116-build-temp"
    assert not package.exists()
    package.mkdir()
    unsigned, aligned, signed = package / "unsigned.apk", package / "aligned.apk", package / "signed.apk"
    with zipfile.ZipFile(BASE) as old, zipfile.ZipFile(unsigned, "w", allowZip64=True) as new:
        for info in old.infolist():
            if signature(info.filename):
                continue
            item = copy.copy(info)
            item.extra = b""
            source = payloads[item.filename].open("rb") if item.filename in payloads else old.open(info)
            with source, new.open(item, "w") as destination:
                shutil.copyfileobj(source, destination, 1024 * 1024)
    run([tools / "zipalign.exe", "-P", "16", "-f", "4", unsigned, aligned], "zipalign")
    unsigned.unlink()
    run([jdk / "java.exe", "-jar", tools / "lib/apksigner.jar", "sign", "--v4-signing-enabled", "false", "--ks", key, "--ks-key-alias", "androiddebugkey", "--ks-pass", "env:STATION_KS_PASS", "--key-pass", "env:STATION_KEY_PASS", "--out", signed, aligned], "sign")
    verify = run([jdk / "java.exe", "-jar", tools / "lib/apksigner.jar", "verify", "--verbose", "--print-certs", signed], "verify")
    assert re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([a-f0-9]{64})\s*$", verify, re.M) == [CERT_SHA]
    assert "Verified using v2 scheme (APK Signature Scheme v2): true" in verify and "Verified using v3 scheme (APK Signature Scheme v3): true" in verify
    run([tools / "zipalign.exe", "-c", "-P", "16", "4", signed], "alignment")

    changes = []
    with zipfile.ZipFile(BASE) as old, zipfile.ZipFile(signed) as new:
        old_names = {name for name in old.namelist() if not signature(name)}
        new_names = {name for name in new.namelist() if not signature(name)}
        assert new_names == old_names
        for name in sorted(new_names):
            original, actual = zip_sha(old, name), zip_sha(new, name)
            if name in payloads:
                assert actual == sha(payloads[name]) and actual != original
                changes.append(name)
            else:
                assert actual == original, name
        assert zip_sha(new, "lib/arm64-v8a/libstation_retroarch.so") == BASE_MEMBERS["lib/arm64-v8a/libstation_retroarch.so"]
    assert changes == sorted(payloads)
    signed.replace(FINAL)
    aligned.unlink()
    shutil.rmtree(package)
    receipt = {
        "version": "R116-candidate", "sourceBaseVersion": "R115", "baseAPK": str(BASE), "baseSHA256": BASE_SHA,
        "apk": str(FINAL), "sha256": sha(FINAL), "bytes": FINAL.stat().st_size, "certificateSHA256": CERT_SHA,
        "changes": changes, "allOtherEntriesByteIdentical": True, "changedJavaFromR115": changed_java,
        "javaSourceCount": len(source_hashes), "javaTests": [resource_output, warm_output, diagnostics_output, prefetch_output], "nativeWarmPathTest": native_warm_output,
        "legacyDiagnostics": {"aggregateOnly": True, "containsIdsOrPaths": False, "canonicalMissingIsNotLegacyProof": True},
        "coverWarmup": {"networkConcurrency": 1, "maximumRemoteAttemptsPerLaunch": 64, "wallBudgetSeconds": 20, "persistedSuccessesAreNotRedownloaded": True},
        "coverCompletion": {"postPublication": True, "networkConcurrency": 1, "visiblePreemptsBackground": True, "atomicExactCoverIdRevision": True, "lifecycleBound": True, "terminalPassResults": ["offline", "401", "403", "404"], "rateLimitRetriesPerPass": 1},
        "coverConsumers": {"carousel": "one-lane", "online": "one-lane", "downloadPanelArtwork": "one-lane", "gameDownloadExecutorChanged": False},
        "warmRoots": ["/data/data/org.turboramastation.frontend/no_backup/", "/data/user/0/org.turboramastation.frontend/no_backup/"],
        "publication": {"privateFullMap": True, "visibleWindow": 9, "revealIntervalMs": 80, "heroImmediate": True},
        "led": {"baseCoverVisibleWhilePending": True, "prewarmSameCarouselContext": True, "incrementalRowsPerFrame": 4, "atomicCommit": True, "qualityChanged": False},
        "classes28DexSHA256": sha(client_dex), "classes35DexSHA256": sha(rooms_dex), "frontendSHA256": BASE_MEMBERS["lib/arm64-v8a/libstation_frontend.so"], "carouselSHA256": BASE_MEMBERS["lib/arm64-v8a/libturbo_carousel.so"],
        "runtimeSHA256": BASE_MEMBERS["lib/arm64-v8a/libstation_retroarch.so"], "signatureV2V3Passed": True, "zipAlignment16KiBPassed": True,
        "installed": False, "physicalVerified": False, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence/package.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (ROOT / "JAVA-SOURCE-MANIFEST.json").write_text(json.dumps(source_hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
