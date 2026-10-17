"""Increase only the selected game cover width by 10% from R164.

Apply to a separate copy of the exact R164 native overlay. The cover slot is
also the source of artwork mapping and touch bounds; the action layout keeps
its independent hero anchor in sync. No render loop or worker is added.
"""

from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path


R164_NATIVE = Path("E:/StationVisualR164SelectionActions-20261015/native")
R164_RECEIPT_SHA256 = "c39fc9350cb643cd64bd227a874b9bee2d29bde914a963d6d5e153633e16c3eb"
R164_CAROUSEL_SHA256 = "bd3222558a43f8998d51b0b72010ecb8a94c7ae62a14d34b39863d13737a10d0"
HERO_RATIO = .790 * .828 / .865
OLD_SCALE = .90
NEW_SCALE = .99  # exactly 1.10 times the R164 selected-cover width
CHANGES = {
    "native_formation.h": (
        b"bigW=systemsMode?bigH:bigH*(.790f*.828f/.865f)*.90f",
        b"bigW=systemsMode?bigH:bigH*(.790f*.828f/.865f)*.99f",
    ),
    "station_bottom_action_layout.h": (
        b"hero=h*.940f*(.790f*.828f/.865f)*.90f;",
        b"hero=h*.940f*(.790f*.828f/.865f)*.99f;",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def geometry(width: int, height: int) -> dict:
    """Numerical audit of the two native constants on phone-sized viewports."""
    w, h = float(width), float(height)
    old_hero = h * .940 * HERO_RATIO * OLD_SCALE
    hero = h * .940 * HERO_RATIO * NEW_SCALE
    cover_x, cover_y, cover_h = w * .025, h * .040, h * .940
    left, right, gap = w * .047 + hero, w * .975, w * .007
    old_left = w * .047 + old_hero
    original_strip_x = w * .047 + h * .940 * HERO_RATIO
    small = (w * .965 - original_strip_x - 5 * w * .012) / 6 * .91
    small_step = (w * .965 - left - small) / 5
    projected = (w * .965 - original_strip_x - 9 * w * .008) / 10 * .91
    side_step = (w * .965 - left - projected) / 9
    search = (left, h * .008, h * .059, h * .059)
    refresh = (left + h * .079, h * .008, h * .059, h * .059)
    query = (left + h * .205, h * .405, w * .965 - left - h * .205, h * .042)
    if w < h * 2.03:
        online_width = h * .260
        secondary = (right - left - online_width - 3 * gap) / 3
        online = (left, h * .904, online_width, h * .065)
        primary = (left + online_width + gap, h * .831,
                   right - left - online_width - gap, h * .065)
        secondary_boxes = [
            (primary[0] + i * (secondary + gap), h * .904,
             secondary, h * .065) for i in range(3)
        ]
        buttons = [online, *secondary_boxes]
    else:
        button_width = (right - left - 4 * gap) / 5
        buttons = [(left + i * (button_width + gap), h * .904,
                    button_width, h * .065) for i in range(5)]
        primary, online = buttons[:2]
    assert abs(hero / old_hero - 1.10) < 1e-10
    assert abs(cover_x + hero + w * .022 - left) < 1e-6
    assert abs(cover_y + cover_h - h * .980) < 1e-6
    assert all(box[2] > h * .15 and box[3] > 0 for box in buttons)
    assert primary[2] > h * .15 and online[2] > h * .15
    assert buttons[-1][0] + buttons[-1][2] <= right + 1e-6
    assert refresh[0] - (search[0] + search[2]) >= h * .019
    assert query[2] > h * .15 and query[1] + query[3] < h * .454
    assert small > 0 and projected > 0 and small_step > small and side_step > projected
    assert abs(left + 5 * small_step + small - w * .965) < 1e-6
    assert abs(left + 9 * side_step + projected - w * .965) < 1e-6
    assert left > old_left and left < w * .965
    return {
        "screen": [width, height],
        "r164CoverWidth": old_hero,
        "candidateCover": [cover_x, cover_y, hero, cover_h],
        "coverWidthIncreasePercent": 100 * (hero / old_hero - 1),
        "firstCardX": left,
        "smallCardWidthUnchanged": small,
        "smallCardStep": small_step,
        "sideProjectedCardWidthUnchanged": projected,
        "sideCardStep": side_step,
        "primary": list(primary),
        "online": list(online),
        "bottomButtons": [list(box) for box in buttons],
        "search": list(search),
        "refresh": list(refresh),
        "compactQuery": list(query),
    }


def patch(overlay_dir: Path) -> dict:
    """Pin every R164 header, preflight both anchors, then modify the copy."""
    overlay_dir = Path(overlay_dir).resolve(strict=True)
    if not overlay_dir.is_dir() or overlay_dir == (R164_NATIVE / "overlay").resolve(strict=True):
        raise ValueError("A separate copy of the R164 overlay is required")
    receipt_bytes = (R164_NATIVE / "native-receipt.json").read_bytes()
    if sha(receipt_bytes) != R164_RECEIPT_SHA256:
        raise ValueError("R164 native receipt differs")
    receipt = json.loads(receipt_bytes)
    if receipt.get("schema") != "station.r164.selection-actions.native.v1" or \
       receipt.get("passed") is not True or \
       receipt.get("outputSha256") != R164_CAROUSEL_SHA256 or \
       sha_file(R164_NATIVE / "libturbo_carousel.so") != R164_CAROUSEL_SHA256:
        raise ValueError("Exact R164 carousel source is required")
    expected = receipt["headerSha256"]
    actual_files = {path.name: path.read_bytes() for path in overlay_dir.iterdir() if path.is_file()}
    if set(actual_files) != set(expected) or \
       any(sha(data) != expected[name] for name, data in actual_files.items()):
        raise ValueError("R164 overlay copy differs from the approved 14 headers")
    replacements = {}
    for name, (old, new) in CHANGES.items():
        data = actual_files[name]
        if data.count(old) != 1 or new in data:
            raise ValueError(f"{name}: expected one original hero anchor")
        replacements[name] = data.replace(old, new, 1)
    samples = [geometry(w, h) for w, h in
               ((2456, 1080), (2340, 1080), (1920, 1080), (1280, 720))]
    for name, data in replacements.items():
        (overlay_dir / name).write_bytes(data)
    return {
        "schema": "station.r165.selection-main-width.patch.v1",
        "sourceCarouselSha256": R164_CAROUSEL_SHA256,
        "changedHeaders": [
            {"name": name, "before": expected[name], "after": sha(data)}
            for name, data in replacements.items()
        ],
        "preservedHeaders": {name: expected[name] for name in expected if name not in CHANGES},
        "geometry": samples,
        "newTimersThreadsWorkersOrPerFrameDraws": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay", type=Path, required=True,
                        help="Separate copy of the R164 native overlay to modify")
    arguments = parser.parse_args()
    print(json.dumps(patch(arguments.overlay), ensure_ascii=False, indent=2))
