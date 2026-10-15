"""Patch only the R158 carousel overlay copy for the game-selection layout.

No APK, engine, network code or original backup is modified. The existing native
GuiStore actions retain their identifiers and touch rectangles.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


ACTIVE_R158 = Path(
    "E:/StationVisualR158UnifiedPsxFinal-20261014/combined-native-v8/overlay"
)
R145_NATIVE = Path(
    "F:/TurboStations-Backup-Completo-20261011/desenvolvimento/"
    "reconstrucao-atual/sky-blue-waves-r145-20261013/native-inputs/native/d0"
)
EXPECTED = {
    "native_formation.h": "06e3916afd8af22a1e3969863339b739efb25dfbec592b44e93008693db091b4",
    "native_skin.h": "0db3942ca17c58f5ae118707be3c978fd9e7faf0e47262b2abd7316574b8ddbf",
    "station_bottom_action_layout.h": "cca983aeea517a989692039243abf9b0d34cae29c4e14b37f7fa4542288b318f",
    "station_collection_settings_layout.h": "f536133890b87a3c4e48516b9a24527221302c3ba0195ed2c4d06f16a30bde84",
    "native_search_download.h": "53821c42d53da2fc663381ead04683a87d23c70f074b3eb8049f63617cf76cca",
}
FROM_R158 = frozenset(("native_formation.h", "native_skin.h"))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _replace(data: bytes, old: str, new: str, name: str) -> bytes:
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    before = old.encode("utf-8").replace(b"\n", newline)
    after = new.encode("utf-8").replace(b"\n", newline)
    count = data.count(before)
    if count != 1:
        raise ValueError(f"{name}: expected one anchor, found {count}")
    return data.replace(before, after, 1)


def patch(overlay_dir: Path) -> dict:
    """Patch a *copy* of the R158 overlay; preflight every input before writing."""
    overlay_dir = Path(overlay_dir).resolve(strict=True)
    if overlay_dir == ACTIVE_R158.resolve(strict=True) or not overlay_dir.is_dir():
        raise ValueError("A separate R158 overlay copy is required")

    original: dict[str, bytes] = {}
    for name, expected in EXPECTED.items():
        target = overlay_dir / name
        if name in FROM_R158:
            if not target.is_file():
                raise FileNotFoundError(target)
            data = target.read_bytes()
        else:
            if target.exists():
                raise FileExistsError(f"Refusing to replace an existing override: {target}")
            data = (R145_NATIVE / name).read_bytes()
        if _sha(data) != expected:
            raise ValueError(f"{name}: source SHA-256 differs from installed R162 lineage")
        original[name] = data

    changed = dict(original)
    # native_skin.h includes this header. Keep an identical copy in the overlay
    # so its quoted include resolves to the *same* bottom-action override that
    # native_carousel.cpp sees through -I, rather than a second baseline header.
    collection = original["station_collection_settings_layout.h"]
    if collection.count(b'#include "station_bottom_action_layout.h"') != 1:
        raise ValueError("station_collection_settings_layout.h: unexpected quoted include")
    bottom = original["station_bottom_action_layout.h"]
    if bottom.count(b"#pragma once") != 1 or not bottom.startswith(b"#pragma once"):
        raise ValueError("station_bottom_action_layout.h: expected one leading pragma once")
    name = "native_formation.h"
    changed[name] = _replace(
        changed[name],
        " float bigH=h*(systemsMode?.665f:.865f),bigW=systemsMode?bigH:h*.790f*.828f,bigX=w*(systemsMode?.035f:.025f),top=h*(systemsMode?.135f:.040f);",
        " // Only the selected game gains the space formerly occupied by JOGAR.\n"
        " float bigH=h*(systemsMode?.665f:.940f),bigW=systemsMode?bigH:bigH*(.790f*.828f/.865f),bigX=w*(systemsMode?.035f:.025f),top=h*(systemsMode?.135f:.040f);",
        name,
    )

    name = "station_bottom_action_layout.h"
    changed[name] = _replace(
        changed[name],
        " float bh=h*.065f,gap=w*.009f,x=w*.025f,hero=h*.790f*.828f;\n"
        " if(slot==0)return {x,h*.922f,hero,bh};\n"
        " float secondary=(w*.95f-hero-5*gap)/5.f;\n"
        " return {x+hero+gap+(slot-1)*(secondary+gap),h*.922f,secondary,bh};",
        " // Keep the original six action IDs; action 4 moves beside Search.\n"
        " // The other five share only the right-hand area below the small cards.\n"
        " float bh=h*.065f,gap=w*.007f,hero=h*.940f*(.790f*.828f/.865f);\n"
        " float left=w*.025f+hero+w*.022f;\n"
        " if(slot==4)return {left+h*.067f,h*.008f,h*.059f,h*.059f};\n"
        " float button=(w*.975f-left-4*gap)/5.f;\n"
        " if(!(button>0))return {};\n"
        " int column=slot<4?slot:slot-1;\n"
        " return {left+column*(button+gap),h*.922f,button,bh};",
        name,
    )
    if changed[name].count(b"#pragma once") != 1 or not changed[name].startswith(b"#pragma once"):
        raise ValueError("station_bottom_action_layout.h: patched guard was lost")

    name = "native_skin.h"
    changed[name] = _replace(
        changed[name],
        " if(owner==p&&oldW==w&&oldH==h&&oldMode==systemsMode&&oldFolder==folderMode&&oldNotice==notice&&at<float>(buttons,8)==h*(systemsMode?.851f:.922f))return;",
        " if(owner==p&&oldW==w&&oldH==h&&oldMode==systemsMode&&oldFolder==folderMode&&oldNotice==notice&&at<float>(buttons,8)==h*(systemsMode?.851f:.922f)&&\n"
        "     (systemsMode||at<float>(buttons+3*20,8)==h*.008f))return;",
        name,
    )
    changed[name] = _replace(
        changed[name],
        "  place((B*)p+labels[i],x+labelInset,h*(systemsMode?.851f:.922f),width-labelInset-(withIcon?buttonH*.16f:0),buttonH,systemsMode?.92f:gameActionTextScale,systemsMode?1:0);",
        "  if(!systemsMode&&i==3)place((B*)p+labels[i],-w,-h,0,0,gameActionTextScale,0); // Refresh is icon-only.\n"
        "  else place((B*)p+labels[i],x+labelInset,h*(systemsMode?.851f:.922f),width-labelInset-(withIcon?buttonH*.16f:0),buttonH,systemsMode?.92f:gameActionTextScale,systemsMode?1:0);",
        name,
    )
    changed[name] = _replace(
        changed[name],
        " if(offset==0xe00||offset==0xf30||offset==0x1190||offset==0x12c0)color=0xF3FFF6ff;",
        " if(!systemsMode&&offset==0x1190){fn<void(*)(void*,bool)>(0x277228)(t,false);return;} // No hidden label paint.\n"
        " if(offset==0xe00||offset==0xf30||offset==0x1190||offset==0x12c0)color=0xF3FFF6ff;",
        name,
    )
    changed[name] = _replace(
        changed[name],
        " if(!systemsMode){auto end=stationBottomGameAction(w,h,5);rounded(w*.014f,h*.914f,end.x+end.w-w*.014f+h*.012f,h*.084f,0x080C09e8);}",
        " if(!systemsMode){auto first=stationBottomGameAction(w,h,0),end=stationBottomGameAction(w,h,5);float left=first.x-w*.008f;rounded(left,h*.914f,end.x+end.w-left+h*.012f,h*.084f,0x080C09e8);}",
        name,
    )

    name = "native_search_download.h"
    changed[name] = _replace(
        changed[name],
        " if(!active&&!systemsMode){x=contentLeft(p);y=h*.405f;bw=w*.45f;bh=h*.042f;}",
        " if(!active&&!systemsMode){\n"
        "   // Compact results share the stars' height, so start after their widest bound.\n"
        "   x=contentLeft(p)+h*.205f;y=h*.405f;bw=w*.965f-x;bh=h*.042f;\n"
        "  }",
        name,
    )

    # Nothing is written until all anchors and checks pass. Existing R158 files
    # are modified only inside this supplied copy; the three base headers are added.
    for name in EXPECTED:
        target = overlay_dir / name
        if name not in FROM_R158 and target.exists():
            raise FileExistsError(target)
    for name in EXPECTED:
        (overlay_dir / name).write_bytes(changed[name])
    return {
        "sourceCarouselSha256": "7d2f2be22083c3fb2a27df9fd43c3b92cf63bc74f87e1f64955753910b00c025",
        "files": [
            {"name": name, "sourceSha256": EXPECTED[name], "patchedSha256": _sha(changed[name])}
            for name in EXPECTED
        ],
        "actionsPreserved": [0, 1, 2, 3, 4, 5],
        "newTimersThreadsWorkers": 0,
    }
