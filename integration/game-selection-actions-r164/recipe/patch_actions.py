"""Apply the R164 game-selection geometry to a copy of the R163 native overlay.

Only existing presentation and touch geometry changes. The signed R163 package,
its overlay, Android logic, timers, workers, and network code remain untouched.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


R163_OVERLAY = Path("E:/StationVisualR163SelectionN64-20261015/native/overlay")
R145_NATIVE = Path(
    "F:/TurboStations-Backup-Completo-20261011/desenvolvimento/"
    "reconstrucao-atual/sky-blue-waves-r145-20261013/native-inputs/native/d0"
)
EXPECTED = {
    "native_formation.h": "70d1839939b54cb0701a04e24bbc5c08e0277af5096db6d737544c4045a13b2f",
    "station_bottom_action_layout.h": "210ec6d6e0f68cf4d273bbefd4052fa6458aec01e3089a1a37f6c755822a3be3",
    "native_skin.h": "979ca395c3f9d6112ebabffa6792ce33852e7c83a1dc6b67fc33840d82958631",
    "native_search_download.h": "2237e8a10058bfe4c1aafcc71f0730539d0325f5ef40d44fe0e1a38362307559",
    "r132_native_info.h": "af31da6851bb2ce6742aca553b361fdb5beccab87c68a4874a6c6febbb89b0b6",
    "station_collection_settings_layout.h": "f536133890b87a3c4e48516b9a24527221302c3ba0195ed2c4d06f16a30bde84",
}
NETPLAY_SHA = "355605d71eeadfe80a3adf8520801c3b1ecc31f2d665e6c2c797104562f38640"
MODIFIED = ("native_formation.h", "station_bottom_action_layout.h", "native_skin.h")


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


def _geometry(w: int, h: int) -> dict:
    """Build-time audit of the same constants as the native geometry."""
    hero = h * .940 * (.790 * .828 / .865) * .90
    cover = (w * .025, h * .040, hero, h * .940)
    left = w * .047 + hero
    right = w * .975
    gap = w * .007
    bottom_y = h * .904
    bh = h * .065
    if w < h * 2.03:
        online = h * .260
        secondary = (right - left - online - 3 * gap) / 3
        if secondary <= 0:
            raise ValueError(f"Action row too narrow at {w}x{h}")
        primary = (left + online + gap, h * .831, right - left - online - gap, bh)
        online_box = (left, bottom_y, online, bh)
        others = [(primary[0] + i * (secondary + gap), bottom_y, secondary, bh)
                  for i in range(3)]
        bottom = [online_box, *others]
    else:
        width = (right - left - 4 * gap) / 5
        if width <= 0:
            raise ValueError(f"Action row too narrow at {w}x{h}")
        bottom = [(left + i * (width + gap), bottom_y, width, bh)
                  for i in range(5)]
        primary = bottom[0]
        online_box = bottom[1]
    search = (left, h * .008, h * .059, h * .059)
    refresh = (left + h * .079, h * .008, h * .059, h * .059)
    query = (left + h * .205, h * .405, w * .965 - left - h * .205, h * .042)
    original_strip = w * .047 + hero / .90
    original_small = (w * .965 - original_strip - 5 * w * .012) / 6
    small = original_small * .91
    small_step = (w * .965 - left - small) / 5
    original_side_projected = (w * .965 - original_strip - 9 * w * .008) / 10
    side_projected = original_side_projected * .91
    side_step = (w * .965 - left - side_projected) / 9
    cover_bottom = cover[1] + cover[3]
    strip_bottom = h * (.896 + .084)
    assert abs(cover_bottom - strip_bottom) < 1e-6 * h
    assert bottom[0][1] == bottom_y and bottom[-1][0] + bottom[-1][2] <= right + 1e-3
    assert refresh[0] - search[0] - search[2] >= h * .019
    assert query[0] > left and query[1] + query[3] < h * .454
    assert small > 0 and side_projected > 0
    assert abs(left + 5 * small_step + small - w * .965) < 1e-5 * w
    assert abs(left + 9 * side_step + side_projected - w * .965) < 1e-5 * w
    if w < h * 2.03:
        assert primary[1] >= h * .830 and primary[1] + primary[3] <= h * .896 + 1e-3
        assert primary[0] > online_box[0] + online_box[2]
        assert online_box[2] - h * .065 * 1.14 > h * .18
    return {
        "screen": [w, h], "cover": list(cover), "coverBottom": cover_bottom,
        "strip": [left - w * .008, h * .896, right - left + w * .020, h * .084],
        "primary": list(primary), "online": list(online_box),
        "bottomButtons": [list(box) for box in bottom],
        "search": list(search), "refresh": list(refresh), "compactQuery": list(query),
        "smallCardR163Width": original_small, "smallCardR164Width": small,
        "smallCardR164Step": small_step,
        "sideProjectedR163Width": original_side_projected,
        "sideProjectedR164Width": side_projected,
        "sideProjectedR164Step": side_step,
    }


def patch(overlay_dir: Path) -> dict:
    """Preflight all pins/anchors, then write only to a supplied R163 overlay copy."""
    overlay_dir = Path(overlay_dir).resolve(strict=True)
    if overlay_dir == R163_OVERLAY.resolve(strict=True) or not overlay_dir.is_dir():
        raise ValueError("A separate copy of the R163 native overlay is required")
    if (overlay_dir / "native_netplay.h").exists():
        raise FileExistsError("Refusing to replace an existing netplay override")

    source: dict[str, bytes] = {}
    for name, expected in EXPECTED.items():
        data = (overlay_dir / name).read_bytes()
        if _sha(data) != expected:
            raise ValueError(f"{name}: source SHA-256 differs from R163")
        source[name] = data
    netplay = (R145_NATIVE / "native_netplay.h").read_bytes()
    if _sha(netplay) != NETPLAY_SHA:
        raise ValueError("native_netplay.h: baseline SHA-256 differs")

    changed = {name: source[name] for name in MODIFIED}
    name = "native_formation.h"
    changed[name] = _replace(
        changed[name],
        "bigW=systemsMode?bigH:bigH*(.790f*.828f/.865f)",
        "bigW=systemsMode?bigH:bigH*(.790f*.828f/.865f)*.90f",
        name,
    )
    changed[name] = _replace(
        changed[name],
        " float stripX=systemsMode?w*.365f:bigX+bigW+w*.022f,gap=w*.012f,smallW=(w*.965f-stripX-5*gap)/6;\n"
        " bool side=d!=0&&stationCarouselGeometry::neighborCount(effectiveStyle<0?stationCarouselStyle():effectiveStyle,stationGraphicsEnabled(16))==10;\n"
        " float step=smallW+gap;\n"
        " if(side){\n"
        "  gap=w*.008f;float projectedWidth=(w*.965f-stripX-9*gap)/10;\n"
        "  smallW=projectedWidth/stationCarouselGeometry::sideWidthRatio();step=projectedWidth+gap;\n"
        "  stripX-=smallW*stationCarouselGeometry::sideLeftInset();\n"
        " }",
        " float right=w*.965f,stripX=systemsMode?w*.365f:bigX+bigW+w*.022f,gap=w*.012f;\n"
        " float originalStripX=bigX+bigH*(.790f*.828f/.865f)+w*.022f;\n"
        " // On games, reduce each small card by 9% versus R163 despite the narrower hero.\n"
        " float smallW=systemsMode?(right-stripX-5*gap)/6.f:(right-originalStripX-5*gap)/6.f*.91f;\n"
        " bool side=d!=0&&stationCarouselGeometry::neighborCount(effectiveStyle<0?stationCarouselStyle():effectiveStyle,stationGraphicsEnabled(16))==10;\n"
        " float step=systemsMode?smallW+gap:(right-stripX-smallW)/5.f;\n"
        " if(side){\n"
        "  gap=w*.008f;\n"
        "  if(systemsMode){\n"
        "   float projectedWidth=(right-stripX-9*gap)/10.f;\n"
        "   smallW=projectedWidth/stationCarouselGeometry::sideWidthRatio();step=projectedWidth+gap;\n"
        "  }else{\n"
        "   float oldProjected=(right-originalStripX-9*gap)/10.f;\n"
        "   smallW=oldProjected/stationCarouselGeometry::sideWidthRatio()*.91f;\n"
        "   float projectedWidth=smallW*stationCarouselGeometry::sideWidthRatio();\n"
        "   step=(right-stripX-projectedWidth)/9.f;\n"
        "  }\n"
        "  stripX-=smallW*stationCarouselGeometry::sideLeftInset();\n"
        " }",
        name,
    )

    name = "station_bottom_action_layout.h"
    changed[name] = _replace(
        changed[name],
        "float bh=h*.065f,gap=w*.007f,hero=h*.940f*(.790f*.828f/.865f);",
        "float bh=h*.065f,gap=w*.007f,hero=h*.940f*(.790f*.828f/.865f)*.90f;",
        name,
    )
    changed[name] = _replace(
        changed[name],
        "if(slot==4)return {left+h*.067f,h*.008f,h*.059f,h*.059f};",
        "if(slot==4)return {left+h*.079f,h*.008f,h*.059f,h*.059f}; // Icon only, with .020h gap after Search.",
        name,
    )
    changed[name] = _replace(
        changed[name],
        " float button=(w*.975f-left-4*gap)/5.f;\n"
        " if(!(button>0))return {};\n"
        " int column=slot<4?slot:slot-1;\n"
        " return {left+column*(button+gap),h*.922f,button,bh};",
        " float right=w*.975f;\n"
        " if(w<h*2.03f){\n"
        "  // On 16:9, the online robot occupies the upper-left column; JOGAR is beside it.\n"
        "  float online=h*.260f,secondary=(right-left-online-3*gap)/3.f;\n"
        "  if(!(secondary>0))return {};\n"
        "  if(slot==0)return {left+online+gap,h*.831f,right-left-online-gap,bh};\n"
        "  if(slot==1)return {left,h*.904f,online,bh};\n"
        "  int column=slot<4?slot-2:slot-3;\n"
        "  return {left+online+gap+column*(secondary+gap),h*.904f,secondary,bh};\n"
        " }\n"
        " float button=(right-left-4*gap)/5.f;\n"
        " if(!(button>0))return {};\n"
        " int column=slot<4?slot:slot-1;\n"
        " return {left+column*(button+gap),h*.904f,button,bh};",
        name,
    )
    if not changed[name].startswith(b"#pragma once") or changed[name].count(b"#pragma once") != 1:
        raise ValueError("station_bottom_action_layout.h: guard lost")

    name = "native_skin.h"
    changed[name] = _replace(
        changed[name],
        "at<float>(buttons,8)==h*(systemsMode?.851f:.922f)",
        "at<float>(buttons,8)==(systemsMode?h*.851f:stationBottomGameAction(w,h,0).y)",
        name,
    )
    changed[name] = _replace(
        changed[name],
        "else place((B*)p+labels[i],x+labelInset,h*(systemsMode?.851f:.922f),width-labelInset-(withIcon?buttonH*.16f:0),buttonH,systemsMode?.92f:gameActionTextScale,systemsMode?1:0);",
        "else place((B*)p+labels[i],x+labelInset,compact.y,width-labelInset-(withIcon?buttonH*.16f:0),buttonH,systemsMode?.92f:gameActionTextScale,systemsMode?1:0);",
        name,
    )
    changed[name] = _replace(
        changed[name],
        "if(!systemsMode){auto first=stationBottomGameAction(w,h,0),end=stationBottomGameAction(w,h,5);float left=first.x-w*.008f;rounded(left,h*.914f,end.x+end.w-left+h*.012f,h*.084f,0x080C09e8);}",
        "if(!systemsMode){auto first=stationBottomGameAction(w,h,0),end=stationBottomGameAction(w,h,5);if(first.y<h*.904f)first=stationBottomGameAction(w,h,1);float left=first.x-w*.008f;rounded(left,h*.896f,end.x+end.w-left+h*.012f,h*.084f,0x080C09e8);}",
        name,
    )
    changed[name] = _replace(
        changed[name],
        "   bool confirming=action==2&&selected>=0&&at<int>(p,0x16c)==selected;\n"
        "   drawGameAction(x,y,bw,bh,action==0?0:action+1,disabled,focused,confirming,installed);continue;",
        "   bool confirming=action==2&&selected>=0&&at<int>(p,0x16c)==selected;\n"
        "   if(action==3){float s=bh*.56f;drawActionIcon(x+(bw-s)*.5f,y+(bh-s)*.5f,s,4,focused?0xFFFFFFFFu:0xFFD17Cffu);continue;} // Refresh: standalone icon, original action/hitbox.\n"
        "   drawGameAction(x,y,bw,bh,action==0?0:action+1,disabled,focused,confirming,installed);continue;",
        name,
    )

    name = "native_netplay.h"
    netplay = _replace(
        netplay,
        "float w=at<float>(p,0x54),h=at<float>(p,0x58);auto bounds=stationBottomGameAction(w,h,1);float x=bounds.x,bw=bounds.w;\n"
        " fn<void(*)(const void*)>(0x2e5640)(matrix);drawGameAction(x,h*.922f,bw,h*.065f,1,false,false,false);\n"
        " float labelInset=actionLabelInset(h*.065f);\n"
        " place(onlineActionText,x+labelInset,h*.922f,bw-labelInset-h*.065f*.16f,h*.065f,gameActionTextScale,0);",
        "float w=at<float>(p,0x54),h=at<float>(p,0x58);auto action=stationBottomGameAction(w,h,1);\n"
        " fn<void(*)(const void*)>(0x2e5640)(matrix);drawGameAction(action.x,action.y,action.w,action.h,1,false,false,false);\n"
        " float labelInset=actionLabelInset(action.h);\n"
        " place(onlineActionText,action.x+labelInset,action.y,action.w-labelInset-action.h*.16f,action.h,gameActionTextScale,0);",
        name,
    )
    netplay = _replace(
        netplay,
        "float w=at<float>(p,0x54),h=at<float>(p,0x58);auto bounds=stationBottomGameAction(w,h,1);float x0=bounds.x,bw=bounds.w;\n"
        " float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);\n"
        " bool inside=x>=x0&&x<=x0+bw&&y>=h*.922f&&y<=h*.987f;",
        "float w=at<float>(p,0x54),h=at<float>(p,0x58);auto action=stationBottomGameAction(w,h,1);\n"
        " float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);\n"
        " bool inside=x>=action.x&&x<=action.x+action.w&&y>=action.y&&y<=action.y+action.h;",
        name,
    )

    # Validate measured layouts before any write. All source pins and anchors
    # have passed; the signed R163 overlay is never a write target.
    samples = [_geometry(2456, 1080), _geometry(1920, 1080), _geometry(1280, 720)]
    for filename in MODIFIED:
        (overlay_dir / filename).write_bytes(changed[filename])
    (overlay_dir / name).write_bytes(netplay)
    return {
        "schema": "station.r164.selection-actions.patch.v1",
        "sourceCarouselSha256": "788ff4a8eb30add5f5352cf8f0820a73c5b94bd78f42c7ee184ac20d7ecf5d09",
        "changedHeaders": list(MODIFIED),
        "addedHeaders": [name],
        "changed": [
            {"name": filename, "sourceSha256": EXPECTED[filename], "outputSha256": _sha(changed[filename])}
            for filename in MODIFIED
        ],
        "added": [{"name": name, "sourceSha256": NETPLAY_SHA, "outputSha256": _sha(netplay)}],
        "unchangedDependencies": [
            {"name": filename, "sha256": EXPECTED[filename]}
            for filename in EXPECTED if filename not in MODIFIED
        ],
        "geometry": samples,
        "actionsPreserved": [0, 1, 2, 3, 4, 5],
        "newTimersThreadsWorkers": 0,
    }
