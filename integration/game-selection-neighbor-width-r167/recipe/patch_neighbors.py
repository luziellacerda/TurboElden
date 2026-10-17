"""Widen only the smaller game-selection carousel cells by 10% from R165.

Apply to a separate copy of the exact R165 native overlay. The existing
coverSlot geometry also governs artwork mapping and touch bounds, so one
scoped header change keeps drawing and input aligned.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


R165_NATIVE = Path("E:/StationVisualR165Combined-20261015/native")
R165_RECEIPT_SHA256 = "3dd4cca1f17d0f7a6a438b2250f9b186b19548a2177362efd1315c1b75637c3b"
R165_CAROUSEL_SHA256 = "3f20f862bed0d73668fdbc0fa06e7009011cbf8ea32c2cfff96029c2b8f23fc8"
HEADER = "native_formation.h"
CHANGES = (
    (
        b"// On games, reduce each small card by 9% versus R163 despite the narrower hero.",
        b"// On games, widen the R165 neighbor cards by 10%; the selected cover is unchanged.",
    ),
    (
        b"float smallW=systemsMode?(right-stripX-5*gap)/6.f:(right-originalStripX-5*gap)/6.f*.91f;",
        b"float smallW=systemsMode?(right-stripX-5*gap)/6.f:(right-originalStripX-5*gap)/6.f*.91f*1.10f;",
    ),
    (
        b"smallW=oldProjected/stationCarouselGeometry::sideWidthRatio()*.91f;",
        b"smallW=oldProjected/stationCarouselGeometry::sideWidthRatio()*.91f*1.10f;",
    ),
    (
        b"float smallH=systemsMode?smallW:smallW/.72f;",
        b"float smallH=systemsMode?smallW:smallW/(.72f*1.10f);",
    ),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def geometry(width: int, height: int) -> dict:
    """Check both existing carousel styles on supported landscape viewports."""
    w, h = float(width), float(height)
    big_h = h * .940
    big_w = big_h * (.790 * .828 / .865) * .99
    big_x = w * .025
    strip_x = big_x + big_w + w * .022
    original_strip_x = big_x + big_h * (.790 * .828 / .865) + w * .022
    right = w * .965

    small_old = (right - original_strip_x - 5 * w * .012) / 6 * .91
    small_new = small_old * 1.10
    step = (right - strip_x - small_new) / 5
    side_projected_old = (right - original_strip_x - 9 * w * .008) / 10 * .91
    side_projected_new = side_projected_old * 1.10
    side_step = (right - strip_x - side_projected_new) / 9
    old_height = small_old / .72
    new_height = small_new / (.72 * 1.10)

    assert small_old > 0 and side_projected_old > 0
    assert abs(small_new / small_old - 1.10) < 1e-12
    assert abs(side_projected_new / side_projected_old - 1.10) < 1e-12
    assert abs(new_height - old_height) < 1e-9
    assert strip_x > big_x + big_w
    assert step > small_new and side_step > side_projected_new
    assert abs(strip_x + 5 * step + small_new - right) < 1e-9
    assert abs(strip_x + 9 * side_step + side_projected_new - right) < 1e-9
    return {
        "screen": [width, height],
        "selectedCover": [big_x, h * .040, big_w, big_h],
        "straightAndDiagonalNeighbor": [small_old, small_new, old_height, new_height],
        "sideProjectedNeighbor": [side_projected_old, side_projected_new],
        "remainingGaps": [step - small_new, side_step - side_projected_new],
    }


def patch(overlay_dir: Path) -> dict:
    overlay_dir = Path(overlay_dir).resolve(strict=True)
    source_dir = (R165_NATIVE / "overlay").resolve(strict=True)
    if not overlay_dir.is_dir() or overlay_dir == source_dir:
        raise ValueError("A separate copy of the R165 overlay is required")
    receipt_bytes = (R165_NATIVE / "native-receipt.json").read_bytes()
    if sha(receipt_bytes) != R165_RECEIPT_SHA256:
        raise ValueError("R165 native receipt differs")
    receipt = json.loads(receipt_bytes)
    if receipt.get("schema") != "station.r165.selection-native.v1" or \
       receipt.get("passed") is not True or \
       receipt.get("outputSha256") != R165_CAROUSEL_SHA256 or \
       sha_file(R165_NATIVE / "libturbo_carousel.so") != R165_CAROUSEL_SHA256:
        raise ValueError("Exact R165 carousel source is required")
    expected = receipt["headerSha256"]
    source_files = {p.name: p.read_bytes() for p in source_dir.iterdir() if p.is_file()}
    copy_files = {p.name: p.read_bytes() for p in overlay_dir.iterdir() if p.is_file()}
    if len(expected) != 14 or set(source_files) != set(expected) or \
       set(copy_files) != set(expected) or \
       any(sha(source_files[name]) != expected[name] or
           copy_files[name] != source_files[name] for name in expected):
        raise ValueError("R165 overlay copy differs from its 14-header receipt")

    before = copy_files[HEADER]
    after = before
    for old, new in CHANGES:
        if after.count(old) != 1 or new in after:
            raise ValueError("Expected exactly one R165 carousel geometry anchor")
        after = after.replace(old, new, 1)
    samples = [geometry(w, h) for w, h in
               ((2456, 1080), (2340, 1080), (1920, 1080), (1280, 720))]
    (overlay_dir / HEADER).write_bytes(after)
    return {
        "schema": "station.r167.selection-neighbor-width.patch.v1",
        "sourceCarouselSha256": R165_CAROUSEL_SHA256,
        "changedHeader": HEADER,
        "beforeSha256": expected[HEADER],
        "afterSha256": sha(after),
        "preservedHeaders": {name: value for name, value in expected.items() if name != HEADER},
        "selectedCoverAndNeighborHeightUnchanged": True,
        "newTimersThreadsWorkersAllocationsOrDraws": 0,
        "geometry": samples,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay", type=Path, required=True,
                        help="Separate copy of the R165 native overlay to modify")
    args = parser.parse_args()
    print(json.dumps(patch(args.overlay), ensure_ascii=False, indent=2))
