"""Renew R136 runtime markers after the one-class R137 exit correction."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
R135 = REPO / "integration/online-lifecycle-review-r135/recipe"
sys.path.insert(0, str(R135))
import build_runtime_identity as inherited

BASE = "fd14c522f51e717a636febf1ab9dee1970217339f37880421238eb2f30ce7b05"
PARENT = "863fde9c8c52adf63c3f8bb6cb0426833a43c31a8d5014ef8b3fd0fccb934409"
OLD_DEX = "84b8aa3935a8e84eb69f8f7cc45885ac693e38bf1f26cfb07b811d3df60b8c05"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def archive_sha(archive, name):
    value = hashlib.sha256()
    with archive.open(name) as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(part)
    return value.hexdigest()


def build(args):
    require(not args.out.exists(), "Identity output already exists")
    require(sha(args.base) == BASE and sha(args.parent / "runtime-identity.json") == PARENT,
            "Exact R136 signed donor and private identity required")
    parent = json.loads((args.parent / "runtime-identity.json").read_text("utf-8"))
    require(parent["revision"] == "R136" and len(parent["payloadSha256"]) == 345 and
            parent["payloadSha256"]["classes35.dex"] == OLD_DEX and
            sha(args.dex) != OLD_DEX and args.dex.name == "classes35.dex", "Wrong DEX identity")
    with zipfile.ZipFile(args.base) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())) == 13860,
                "Unexpected donor ZIP entries")
        for name, expected in parent["payloadSha256"].items():
            require(archive_sha(archive, name) == expected, "Inherited payload changed: " + name)
        require(archive_sha(archive, "assets/station-online/engines.json") == sha(args.parent / "engines.json"),
                "Inherited engine registry changed")
        original = json.loads(archive.read("assets/station-online/engines.json"))
        previous = {}
        for kind, (library, _, _) in inherited.MARKERS.items():
            name = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
            raw = (args.parent / name).read_bytes().rstrip(b"\r\n")
            binary = archive.read("lib/arm64-v8a/" + library)
            require(raw == inherited.canonical(json.loads(raw)) and raw in binary and
                    inherited.digest(raw).encode("ascii") in binary and
                    inherited.digest(binary) == parent["markers"][kind]["runtimeSha256"],
                    "Inherited runtime marker mismatch: " + kind)
            previous[kind] = json.loads(raw)
    require({k: v["productiveTransforms"] for k, v in previous.items()} ==
            {k: previous["psx"]["productiveTransforms"] for k in previous},
            "Inherited productive source maps differ")
    expected = {**parent["payloadSha256"], "classes35.dex": sha(args.dex)}
    transforms = dict(previous["psx"]["productiveTransforms"])
    source_name = "online-exit-r137/recipe/patch_exit.py"
    require(source_name not in transforms, "R137 patch already in source chain")
    transforms[source_name] = sha(HERE / "patch_exit.py")
    require(inherited.policy(previous["psx"]) == inherited.policy({**previous["psx"],
            "baseApkSha256": BASE, "payloadSha256": expected, "productiveTransforms": transforms}),
            "PSX policy changed")
    inherited.native_tools(args.ndk)
    args.out.mkdir(parents=True)
    markers = {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE, payloadSha256=expected, productiveTransforms=transforms)
    raw = inherited.canonical(psx)
    (args.out / "psx.fingerprint.json").write_bytes(raw + b"\n")
    identity_source = args.out / "StationPsxIdentity.cpp"
    identity_source.write_text(
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + inherited.digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n',
        encoding="ascii")
    native = args.out / "native"
    subprocess.run([sys.executable, "-B", str(inherited.PSX / "recipe/build_entry.py"),
                    "--ndk", str(args.ndk), "--owner", str(inherited.PSX / "native"),
                    "--protocol", str(inherited.PSX / "native"),
                    "--pinned-options", str(inherited.PSX / "native"),
                    "--identity-source", str(identity_source), "--out", str(native)],
                   check=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    psx_binary = native / "libstation_psx_online.so"
    require(raw in psx_binary.read_bytes(), "PSX marker embedding failed")
    markers["psx"] = dict(runtimeLibrary=psx_binary.name, runtimeSha256=sha(psx_binary),
                          runtimeBytes=psx_binary.stat().st_size, fingerprintSha256=inherited.digest(raw))
    primitive = inherited.module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r136_marker_builder")
    for kind in ("n64", "dolphin"):
        value = copy.deepcopy(previous[kind])
        library = inherited.MARKERS[kind][0]
        old_runtime = parent["markers"][kind]["runtimeSha256"]
        old_fingerprint = parent["markers"][kind]["fingerprintSha256"]
        value.update(baseApkSha256=BASE, payloadSha256=expected, productiveTransforms=transforms,
                     parentFingerprintSha256=old_fingerprint, parentRuntimeSha256=old_runtime,
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        require(inherited.policy(value) == inherited.policy(previous[kind]), "Runtime policy changed: " + kind)
        (args.out / (library + ".fingerprint.json")).write_bytes(inherited.canonical(value) + b"\n")
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, args.ndk, args.out)
    updated, selected = inherited.expected_engines(original, markers)
    (args.out / "engines.json").write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    profile = (args.parent / "psx-controller-profile.json").read_bytes()
    (args.out / "psx-controller-profile.json").write_bytes(profile)
    receipt = dict(schema="station.online-exit.identity.r137.v1", revision="R137",
                   parentApkSha256=BASE, parentIdentitySha256=PARENT,
                   changedDexEntry="classes35.dex", previousDexSha256=OLD_DEX,
                   dexSha256=sha(args.dex), payloadSha256=expected,
                   productiveTransformSha256={source_name: transforms[source_name]},
                   markers=markers, engines=selected, enginesAssetSha256=sha(args.out / "engines.json"),
                   psxControllerProfileSha256=sha(args.out / "psx-controller-profile.json"),
                   inheritedPayloadCount=len(expected), gameplayValidated=False, serverRegistered=False)
    (args.out / "runtime-identity.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("base", "parent", "dex", "ndk", "out"):
        p.add_argument("--" + field, type=Path, required=True)
    result = build(p.parse_args())
    print(json.dumps({"revision": result["revision"], "dexSha256": result["dexSha256"],
                      "markerSha256": {k: v["runtimeSha256"] for k, v in result["markers"].items()}}))
