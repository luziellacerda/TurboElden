"""Stream R136's five entry replacements over the exact signed R135 donor."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = "f6abe89490e7ba5e2cdd432625888bed6f40aea115d730cf612d509ec6ca9896"
PARENT = "07754bea0ceabac68d59ee044600d012443d85c222c8f238574e63d607fa53cd"
OLD_DEX = "a7a66724f26c06075ec1833e11866a073f93ee056aeabf58301cab016f96a4f5"
MARKERS = ("libstation_psx_online.so", "libstation_mupen64plus_runtime.so", "libstation_dolphin_runtime.so")
REPLACED = frozenset({"classes35.dex", "assets/station-online/engines.json",
                      *("lib/arm64-v8a/" + name for name in MARKERS)})


def require(ok, label):
    if not ok:
        raise ValueError(label)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare(base, identity, dex, freeze):
    base, identity, dex, freeze = map(Path, (base, identity, dex, freeze))
    require(sha(base) == BASE and not freeze.exists(), "Wrong R135 donor or existing freeze")
    receipt = json.loads(identity.read_text("utf-8"))
    require(receipt["revision"] == "R136" and receipt["parentApkSha256"] == BASE and
            receipt["parentIdentitySha256"] == PARENT and receipt["previousDexSha256"] == OLD_DEX and
            receipt["dexSha256"] == sha(dex) and
            receipt["productiveTransformSha256"] == {
                "online-cover-anr-r136/recipe/patch_cover.py": sha(HERE / "patch_cover.py")},
            "R136 source, parent or DEX scope differs")
    files = {"classes35.dex": dex, "assets/station-online/engines.json": identity.parent / "engines.json"}
    for marker in receipt["markers"].values():
        name = marker["runtimeLibrary"]
        files["lib/arm64-v8a/" + name] = (identity.parent / "native" / name) if name == "libstation_psx_online.so" else (identity.parent / name)
    require(set(files) == REPLACED and all(path.is_file() for path in files.values()), "Five exact payload files required")
    for key, marker in receipt["markers"].items():
        path = files["lib/arm64-v8a/" + marker["runtimeLibrary"]]
        source = identity.parent / ("psx.fingerprint.json" if key == "psx" else marker["runtimeLibrary"] + ".fingerprint.json")
        raw = source.read_bytes().rstrip(b"\r\n")
        require(sha(path) == marker["runtimeSha256"] and
                hashlib.sha256(raw).hexdigest() == marker["fingerprintSha256"] and
                raw in path.read_bytes() and
                hashlib.sha256(raw).hexdigest().encode("ascii") in path.read_bytes(),
                "Runtime marker binding differs: " + key)
    require(sha(files["assets/station-online/engines.json"]) == receipt["enginesAssetSha256"],
            "Engine registry mismatch")
    with zipfile.ZipFile(base) as archive:
        require(hashlib.sha256(archive.read("classes35.dex")).hexdigest() == OLD_DEX,
                "R135 DEX changed")
        require(archive.namelist() and len(archive.namelist()) == len(set(archive.namelist())) == 13860,
                "R135 ZIP entry count changed")
        old = json.loads(archive.read("assets/station-online/engines.json"))
    new = json.loads(files["assets/station-online/engines.json"].read_text("utf-8"))
    require({k: v for k, v in old.items() if k != "engines"} ==
            {k: v for k, v in new.items() if k != "engines"} and
            len(old["engines"]) == len(new["engines"]), "Non-engine registry policy changed")
    for before, after in zip(old["engines"], new["engines"]):
        require(before["platform"] == after["platform"], "Engine order changed")
        if before["platform"] not in {"psx", "n64", "gamecube", "wii"}:
            require(before == after, "Other engine changed")
        else:
            require({k: v for k, v in before.items() if k not in ("engineId", "runtimeSha256")} ==
                    {k: v for k, v in after.items() if k not in ("engineId", "runtimeSha256")},
                    "Engine policy/core changed: " + before["platform"])
    require([row for row in new["engines"] if row["platform"] in {"psx", "n64", "gamecube", "wii"}] ==
            receipt["engines"], "Selected engine identities differ")
    frozen = dict(schemaVersion=1, revision="R136", parentApkSha256=BASE,
                  parentIdentitySha256=PARENT, identityReceiptSha256=sha(identity),
                  sourcePatchSha256=sha(HERE / "patch_cover.py"),
                  replacements={name: dict(path=str(path.resolve()), bytes=path.stat().st_size,
                                           sha256=sha(path)) for name, path in files.items()})
    freeze.write_text(json.dumps(frozen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return frozen


def assembler():
    path = REPO / "integration/psx-online/recipe/assemble_apk.py"
    spec = importlib.util.spec_from_file_location("r136_streaming_zip", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.BASE_SHA = BASE
    module.REPLACED = REPLACED
    module.ADDED = frozenset()
    module.PAYLOADS = REPLACED

    def inputs(base, freeze, identity):
        base, freeze, identity = map(Path, (base, freeze, identity))
        require(sha(base) == BASE, "R135 donor changed")
        frozen = json.loads(freeze.read_text("utf-8"))
        receipt = json.loads(identity.read_text("utf-8"))
        require(frozen["schemaVersion"] == 1 and frozen["revision"] == "R136" and
                frozen["parentApkSha256"] == BASE and frozen["parentIdentitySha256"] == PARENT and
                frozen["identityReceiptSha256"] == sha(identity) and
                frozen["sourcePatchSha256"] == sha(HERE / "patch_cover.py") and
                set(frozen["replacements"]) == REPLACED, "Freeze scope mismatch")
        files = {name: Path(value["path"]) for name, value in frozen["replacements"].items()}
        for name, record in frozen["replacements"].items():
            path = files[name]
            require(path.is_file() and path.stat().st_size == record["bytes"] and
                    sha(path) == record["sha256"], "Replacement payload changed: " + name)
        require(receipt["revision"] == "R136" and receipt["dexSha256"] ==
                frozen["replacements"]["classes35.dex"]["sha256"], "DEX receipt mismatch")
        for marker in receipt["markers"].values():
            name = "lib/arm64-v8a/" + marker["runtimeLibrary"]
            require(frozen["replacements"][name]["sha256"] == marker["runtimeSha256"],
                    "Native identity mismatch")
        require(frozen["replacements"]["assets/station-online/engines.json"]["sha256"] ==
                receipt["enginesAssetSha256"], "Engines identity mismatch")
        engines = json.loads(files["assets/station-online/engines.json"].read_text("utf-8"))
        return frozen, receipt, files, {name: value["sha256"] for name, value in frozen["replacements"].items()}, engines

    module.inputs = inputs
    return module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("base", "identity", "dex", "freeze", "out"):
        p.add_argument("--" + field, type=Path, required=True)
    a = p.parse_args()
    prepare(a.base, a.identity, a.dex, a.freeze)
    result = assembler().package(a.base, a.freeze, a.identity, a.out)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
