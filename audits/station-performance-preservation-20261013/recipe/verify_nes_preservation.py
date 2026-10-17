"""Read-only guard for the NES capacity patch on the actual R138 composition.

Rejects an older complete source replacement and every unrelated source edit.
This checks source composition, not DEX/ELF equivalence or an installed APK.
"""
from pathlib import Path
import argparse
import hashlib
import json

PINS = {
    "StationApi.java": "f70ad339cff8bc168c46ec400cd90b145fcb7a81834c2ae23e38ebeb9e923f67",
    "StationCatalog.java": "f8775fc40290a23167199205cb77ed45f7200942a903ec897b7a667befec74ea",
    "StationCatalogPlayerEvidence.java": "ad20a55c98552d7ae6e03799253f1b3ec69a80cdb7591e40e10903972fa45379",
    "StationCatalogPlayerEvidenceLoader.java": "c5e3b6e7f4f6c0ca6778181cc9e1abc2bec132a015100ba4c442d5943a3788d2",
    "StationCoverQueue.java": "11decbdb7db269a0fcd6894116d8fae8f876ff584185d684af43ee51c724340a",
}
FRONTEND_PIN = "817154dc40f45b86cd7629602b62940cc4f38b71f268116eb28a682ba2131867"
EDITS = {
    "StationCatalog.java": [(b"public static final int MAX_ITEMS = 4096;", b"public static final int MAX_ITEMS = 20000;")],
    "StationApi.java": [(b'"catalog?metadata=1"', b'"catalog?metadata=1&maximumItems="+StationCatalog.MAX_ITEMS')],
    "StationCatalogPlayerEvidence.java": [(b"catalog.length>4096", b"catalog.length>StationCatalog.MAX_ITEMS"),
                                          (b"values.size()>4096", b"values.size()>StationCatalog.MAX_ITEMS")],
    "StationCatalogPlayerEvidenceLoader.java": [(b"rows.length()>4096", b"rows.length()>StationCatalog.MAX_ITEMS")],
    "StationCoverQueue.java": [(b"MAX_PREFETCH_ITEMS=4096", b"MAX_PREFETCH_ITEMS=StationCatalog.MAX_ITEMS")],
}
NATIVE_EDITS = [(b"total>4096", b"total>20000"), (b"GetArrayLength(rows)>4096", b"GetArrayLength(rows)>20000")]
REQUIRED_EXPORTS = (b"API void StationLoading_graphicsReady(", b"API unsigned StationLoading_stage(")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def apply_allowed(raw, edits):
    candidate = raw
    for before, after in edits:
        require(candidate.count(before) == 1 and after not in candidate, "Capacity anchor differs")
        candidate = candidate.replace(before, after, 1)
    inverse = candidate
    for before, after in reversed(edits):
        require(inverse.count(after) == 1, "Capacity inverse differs")
        inverse = inverse.replace(after, before, 1)
    require(inverse == raw, "Unrelated source bytes changed")
    return candidate


def inventory(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*.java")}


def verify(before_root, after_root, frontend_before, frontend_after):
    before, after = inventory(before_root), inventory(after_root)
    require(set(before) == set(after), "Java sources added or removed")
    require(all(name in before for name in PINS), "Current Station source is incomplete")
    changed = []
    for name, original in before.items():
        if name in PINS:
            require(sha(original) == PINS[name], "Pinned current source differs: " + name)
        expected = apply_allowed(original, EDITS[name]) if name in EDITS else original
        require(after[name] == expected, "Unrelated Java change or source rollback: " + name)
        if expected != original:
            changed.append({"file": name, "beforeSha256": sha(original), "afterSha256": sha(expected)})
    original, candidate = frontend_before.read_bytes(), frontend_after.read_bytes()
    require(sha(original) == FRONTEND_PIN, "Current R132/R138 frontend differs or an old snapshot was selected")
    require(all(symbol in original and symbol in candidate for symbol in REQUIRED_EXPORTS),
            "Current startup/loading exports must be preserved")
    require(candidate == apply_allowed(original, NATIVE_EDITS), "Unrelated native frontend change or rollback")
    return {
        "schemaVersion": 1, "readOnly": True, "referenceInstalledRevision": "R138",
        "javaSourceCount": len(before), "changedJavaSources": changed,
        "preservedJavaSources": len(before) - len(changed),
        "nativeBeforeSha256": sha(original), "nativeAfterSha256": sha(candidate),
        "declaredJavaSubstitutions": sum(map(len, EDITS.values())), "declaredNativeSubstitutions": 2,
        "onlySevenLimitsAndOneQueryChanged": True, "startupExportsPreserved": True,
        "allOtherSourceBytesPreserved": True, "apkBuilt": False, "androidExecuted": False,
        "scope": "Source preflight only. Final DEX class scope, ELF, APK identities/signature and phone validation remain required.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("before-station", "after-station", "before-frontend", "after-frontend"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.before_station, args.after_station, args.before_frontend, args.after_frontend), indent=2))


if __name__ == "__main__":
    main()
