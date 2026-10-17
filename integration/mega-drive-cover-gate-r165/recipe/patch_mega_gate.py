"""Split the Mega Drive cover's new/legacy coarse gates without altering light output.

Run this against the SHA-pinned R164 magazine shader. It prepares a source
overlay for the next combined app build; it does not package or sign an APK.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


R164_SHADER_SHA256 = "35e81ef35a825441f303f93fe70d80afce6b272be2c6407fd32d937a2e00287a"
R164_SHADER = Path("E:/StationVisualR164SelectionActions-20261015/native/overlay/magazine_shader.h")
NEW_GUARD_BEGIN = "bool megaSupport(vec2 p) {"
NEW_GUARD_END = "bool n64Support(vec2 p) {"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_replace(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"Missing or ambiguous exact Mega Drive anchor: {old[:80]!r}")
    return source.replace(old, new, 1)


def rectangles(function: str, pattern: str) -> list[tuple[int, int, int, int]]:
    result = [tuple(map(int, match)) for match in re.findall(pattern, function)]
    if not result:
        raise ValueError("No measured rectangles found")
    return result


def in_any(rects: list[tuple[int, int, int, int]], x: int, y: int) -> bool:
    return any(left <= x <= right and top <= y <= bottom
               for left, top, right, bottom in rects)


def validate_support(old: str, new: str) -> dict:
    """Check the measured mask with the real 5 px two-halo footprint."""
    region = old.split("float megaNewRegion(vec2 p){", 1)[1].split("float megaRegion(vec2 p)", 1)[0]
    new_guard = new.split("bool megaNewSupport(vec2 p) {", 1)[1].split("bool megaSupport(vec2 p) {", 1)[0]
    legacy_guard = new.split("bool megaSupport(vec2 p) {", 1)[1].split(NEW_GUARD_END, 1)[0]
    boxes = rectangles(region, r"box\(p,vec2\((\d+),(\d+)\),vec2\((\d+),(\d+)\)\)")
    bounds = rectangles(new_guard, r"supportBox\(p,vec2\((\d+),(\d+)\),vec2\((\d+),(\d+)\)\)")
    legacy = rectangles(legacy_guard, r"supportBox\(p,vec2\((\d+),(-?\d+)\),vec2\((\d+),(\d+)\)\)")
    if len(boxes) != 7 or len(bounds) != 7 or len(legacy) != 9:
        raise ValueError("Expected seven mapped emitters, seven new bounds and nine legacy bounds")
    # Six pixels of support around each exact map box cover every +/-5 px halo
    # sample and the +/-3 px white-core lookup. This catches omitted SEGA support.
    for left, top, right, bottom in boxes:
        for x, y in ((left - 5, top - 5), (right + 5, top - 5),
                     (left - 5, bottom + 5), (right + 5, bottom + 5)):
            if not in_any(bounds, x, y):
                raise ValueError(f"New Mega mask clips an emitter or halo at ({x},{y})")
    if not in_any(bounds, 777, 40) or not in_any(bounds, 908, 89):
        raise ValueError("SEGA letters are missing from the new coarse gate")
    original_guard = old.split(NEW_GUARD_BEGIN, 1)[1].split(NEW_GUARD_END, 1)[0]
    original_old = original_guard.split("    return supportBox(p,vec2(154,-8)", 1)[1]
    original_old = "    return supportBox(p,vec2(154,-8)" + original_old
    if legacy_guard.lstrip("\n") != original_old:
        raise ValueError("Legacy Mega support changed")

    old_only = new_only = common = 0
    for y in range(1536):
        for x in range(1024):
            is_old = in_any(legacy, x, y)
            is_new = in_any(bounds, x, y)
            if is_old and is_new:
                common += 1
            elif is_old:
                old_only += 1
            elif is_new:
                new_only += 1
    if (old_only, new_only, common) != (196916, 102465, 73865):
        raise ValueError(f"Measured legacy/new support footprint changed: "
                         f"{(old_only, new_only, common)}")
    return {
        "referenceSize": [1024, 1536], "newEmitters": len(boxes),
        "newSupportPixels": new_only + common,
        "legacySupportPixels": old_only + common,
        "legacyOnlyPixelsSkippedForNewCover": old_only,
        "unionPixelsBefore": old_only + new_only + common,
        "segaNameSupported": True, "haloRadiusPixels": 5,
    }


def patch(source: bytes) -> tuple[bytes, dict]:
    if sha(source) != R164_SHADER_SHA256:
        raise ValueError("Exact R164 native shader required")
    if source.count(b"\r\n") != source.count(b"\n"):
        raise ValueError("Mixed line endings in pinned R164 shader")
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    before = source.replace(b"\r\n", b"\n").decode("utf-8")
    old_guard = before.split(NEW_GUARD_BEGIN, 1)[1].split(NEW_GUARD_END, 1)[0]
    old_guard = NEW_GUARD_BEGIN + old_guard
    if before.count(NEW_GUARD_BEGIN) != 1 or before.count(NEW_GUARD_END) != 1:
        raise ValueError("Mega gate scope is ambiguous")
    legacy_begin = "    return supportBox(p,vec2(154,-8)"
    if old_guard.count(legacy_begin) != 1:
        raise ValueError("Legacy Mega support anchor changed")
    legacy_tail = legacy_begin + old_guard.split(legacy_begin, 1)[1]
    new_guard = """bool megaNewSupport(vec2 p) {
    // Exactly the seven frame elements of the Sonic-era magazine, with six
    // pixels of slack for the existing 5 px halo and 3 px hot-core samples.
    return supportBox(p,vec2(9,187),vec2(50,1229))
        || supportBox(p,vec2(977,187),vec2(1018,1229))
        || supportBox(p,vec2(51,16),vec2(710,43))
        || supportBox(p,vec2(95,66),vec2(680,132))
        || supportBox(p,vec2(771,34),vec2(914,95))
        || supportBox(p,vec2(158,1397),vec2(262,1500))
        || supportBox(p,vec2(516,1397),vec2(622,1500));
}
bool megaSupport(vec2 p) {
""" + legacy_tail
    after = unique_replace(before, old_guard, new_guard)
    old_dispatch = "    if(model>0.5) return megaSupport(p);"
    new_dispatch = """    if(model>0.5) {
#ifdef MAGAZINE_VERTEX_CLASSIFIER
        // The texture-derived profile already exists as a uniform varying.
        // Select one frame map, without an extra sample or second draw.
        if(magazineClassifier.y>1.125&&magazineClassifier.y<1.5)
            return megaNewSupport(p);
        return megaSupport(p);
#else
        // R104 fragment-classifier fallback cannot know the profile yet.
        return megaNewSupport(p)||megaSupport(p);
#endif
    }"""
    introduced_code = "\n".join(line.split("//", 1)[0]
                                for line in (new_guard + new_dispatch).splitlines())
    calls = set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", introduced_code))
    if calls - {"if", "vec2", "supportBox", "megaNewSupport", "megaSupport"}:
        raise ValueError(f"Unexpected call in Mega gate: {sorted(calls)}")
    if any(token in introduced_code for token in
           ("FrameCount", "pthread", "thread", "malloc", "calloc", "TexImage", "DrawArrays")):
        raise ValueError("Mega gate introduced work outside fixed support checks")
    after = unique_replace(after, old_dispatch, new_dispatch)
    if after.count("return megaNewRegion(p);") != 1 or after.count("return megaRegion(p);") != 1:
        raise ValueError("The two existing exclusive Mega light maps changed")
    if after.count("activeModel=1.25") != 1 or after.count("activeMagazineModel=1.25") != 1:
        raise ValueError("The new Mega classifier changed")
    # Invert every edit and pin the result, so no unrelated shader source moves.
    restored = unique_replace(after, new_dispatch, old_dispatch)
    restored = unique_replace(restored, new_guard, old_guard)
    if sha(restored.encode("utf-8").replace(b"\n", newline)) != R164_SHADER_SHA256:
        raise ValueError("Mega gate patch failed exact inverse check")
    footprint = validate_support(before, after)
    result = after.encode("utf-8").replace(b"\n", newline)
    return result, {
        "schema": "station.r165.mega-drive-cover-gate.patch.v1",
        "passed": True, "sourceSha256": R164_SHADER_SHA256,
        "outputSha256": sha(result), "changedFile": "magazine_shader.h",
        "onlyChanges": ["Mega Drive coarse support", "profile-aware coarse dispatch"],
        "profile10LegacyPreserved": True, "profile125MapPreserved": True,
        "newTimersThreadsTexturesDraws": 0,
        "newTimersThreadsWorkersOrPerFrameDraws": 0,
        "artworkProbeAndAnimationPreserved": True,
        "footprint": footprint,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    result, receipt = patch(R164_SHADER.read_bytes())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(result)
    out.with_suffix(".receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", "utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
