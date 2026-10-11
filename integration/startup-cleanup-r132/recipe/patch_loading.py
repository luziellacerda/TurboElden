"""Closed loading overlay for the exact R131/R130 inherited GuiStore.

Produces two sources plus one helper; never compiles, signs, installs, cleans or
changes its inputs. R124/R131 trees remain frozen. The expensive existing GLES
preparation stays on SDL/GL, after a black loading frame and before menu entry.
No reduction of total driver compilation time is claimed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

RECIPE = Path(__file__).resolve().parent
REPO = RECIPE.parents[2]
BASE = REPO / "versions/station-video-room-footer-r124-20261011"
NATIVE_SHA = "eb9a7e14bc50e7fac66fee14f9a98ef8b7f109860720c6564ab5da34dea7723b"
SYNOPSIS_NATIVE_SHA = "2678d5679d9d37cba927784289d6d4c7e564fff49c22093eee52cd1955973e91"
FRONTEND_SHA = "603f63e33bfcbb0c81b88f37213999cc0d874d140fa224591fae72737679eefd"
OWNER_SHA = "62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6"
RELOCATION_SHA = "60f13ed591beeaf1ade34ddf5b6331af7855ea99cc23a43950d18dd7c530e08e"
INTRO_ADDRESS = 0x2291B0
INTRO_GOT = 0x3C15C0
INTRO_PROLOGUE = 0xB9437008

NATIVE_REPLACEMENTS = (
    (b'#include "native_magazine.h"\n',
     b'#include "native_magazine.h"\n#include "r132_startup_loading.h"\n'),
    (b' gui=p;if(at<int>(p,0x370)!=0&&stationGraphicsEnabled(1))prewarmMagazinePrograms();syncModel(p);refreshFolderNavigation(p);\n',
     b' gui=p;startupLoadingBeforeUpdate(p);syncModel(p);refreshFolderNavigation(p);\n'),
    (b'    at<unsigned>((void*)base,0x2e4f78)!=0xd10683ff){log("ERROR unsupported baseline ABI; untouched");return;}\n',
     b'    at<unsigned>((void*)base,0x2e4f78)!=0xd10683ff||\n'
     b'    at<unsigned>((void*)base,0x2291b0)!=0xb9437008){log("ERROR unsupported baseline ABI; untouched");return;}\n'),
    (b' U page=(U)sysconf(39);if(page!=4096&&page!=16384)page=4096;int count=0;\n',
     b' if(!startupLoadingBridgeAvailable()){log("ERROR missing paired startup loading bridge; untouched");return;}\n'
     b' U page=(U)sysconf(39);if(page!=4096&&page!=16384)page=4096;int count=0;\n'
     b' // Verified updateIntro PLT/GOT: install the phase barrier before other hooks.\n'
     b' void**startupSlot=(void**)(base+0x3c15c0);U startupPage=(U)startupSlot&~(page-1);\n'
     b' if((U)*startupSlot!=base+0x2291b0||mprotect((void*)startupPage,page,3)){log("ERROR startup intro relocation unavailable; untouched");return;}\n'
     b' *startupSlot=(void*)startupIntroHook;count++;\n'
     b' if(mprotect((void*)startupPage,page,1))log("ERROR startup intro relocation protection restore failed");\n'),
)

FRONTEND_REPLACEMENTS = (
    (b'void* loadingOwner=nullptr;void* loadingLabels[4]{};std::string loadingTexts[4];float shownPercent=0,lastDrawTime=0;\n',
     b'void* loadingOwner=nullptr;void* loadingLabels[4]{};std::string loadingTexts[4];float shownPercent=0,lastDrawTime=0;\n'
     b'// Loading-stage fields are read/written only by GuiStore on its SDL thread.\n'
     b'void* loadingGraphicsOwner=nullptr;bool loadingGraphicsPrepared=false,loadingSurfaceDrawn=false,loadingCompletionDrawn=false;\n'),
    (b'API void StationLoading_draw(void* gui,const void* matrix){\n',
     b'API void StationLoading_graphicsReady(void* gui,bool ready){\n'
     b' if(loadingGraphicsOwner!=gui||!ready){loadingGraphicsOwner=gui;loadingSurfaceDrawn=false;loadingCompletionDrawn=false;}\n'
     b' loadingGraphicsPrepared=ready;\n'
     b'}\n'
     b'API unsigned StationLoading_stage(void* gui){\n'
     b' if(!gui||loadingGraphicsOwner!=gui)return 0;\n'
     b' return (loadingSurfaceDrawn?1u:0u)|(loadingCompletionDrawn?2u:0u);\n'
     b'}\n'
     b'API void StationLoading_draw(void* gui,const void* matrix){\n'),
    (b' const int done=preparedItems.load(),total=preparationTotal.load();const bool committed=preparationCommitted.load();\n'
     b' const float target=committed?100.0f:(total?100.0f*done/(total+1):0.0f);\n',
     b' if(loadingGraphicsOwner!=gui)StationLoading_graphicsReady(gui,false);\n'
     b' const int done=preparedItems.load(),total=preparationTotal.load();const bool committed=preparationCommitted.load();\n'
     b' const bool complete=committed&&loadingGraphicsPrepared;\n'
     b' // Two real terminal milestones: native catalog publication and graphics preparation.\n'
     b' const float units=float(std::max(0,std::min(done,total)))+(committed?1.0f:0.0f)+(loadingGraphicsPrepared?1.0f:0.0f);\n'
     b' const float target=complete?100.0f:(total>0?100.0f*units/(float(total)+2.0f):0.0f);\n'),
    (b' shownPercent=std::min(target,shownPercent+elapsed*.16f);\n',
     b' shownPercent=complete?100.0f:std::min(target,shownPercent+elapsed*.16f);\n'),
    (b' if(failed)loadingText(gui,2,"N\xc3\xa3o foi poss\xc3\xadvel carregar. Verifique a conex\xc3\xa3o e tente novamente.",matrix,w*.18f,h*.538f,w*.64f,h*.06f,.64f,0xffb2a8ff);\n}\n',
     b' if(failed)loadingText(gui,2,"N\xc3\xa3o foi poss\xc3\xadvel carregar. Verifique a conex\xc3\xa3o e tente novamente.",matrix,w*.18f,h*.538f,w*.64f,h*.06f,.64f,0xffb2a8ff);\n'
     b' // Keep the original terminal catalog-error transition; never claim 100% on failure.\n'
     b' loadingSurfaceDrawn=true;loadingCompletionDrawn=loadingGraphicsPrepared&&(complete||failed);\n}\n'),
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def transform(raw: bytes, pins: tuple[str, ...], replacements: tuple) -> bytes:
    require(digest(raw) in pins, "Pinned loading input changed")
    require(b"\r" not in raw, "Only the pinned LF sources are accepted")
    result = raw
    for before, after in replacements:
        require(result.count(before) == 1 and after not in result, "Exact loading anchor changed")
        result = result.replace(before, after, 1)
    inverse = result
    for before, after in reversed(replacements):
        require(inverse.count(after) == 1, "Loading inverse is ambiguous")
        inverse = inverse.replace(after, before, 1)
    require(inverse == raw and digest(inverse) in pins, "Unrelated loading source byte changed")
    return result


def patch(native_cpp: bytes, frontend_cpp: bytes) -> tuple[dict[str, bytes], dict]:
    """Pure in-memory transform, accepting only current CPP or the closed Sony overlay."""
    native = transform(native_cpp, (NATIVE_SHA, SYNOPSIS_NATIVE_SHA), NATIVE_REPLACEMENTS)
    frontend = transform(frontend_cpp, (FRONTEND_SHA,), FRONTEND_REPLACEMENTS)
    helper = (RECIPE / "r132_startup_loading.h").read_bytes()
    outputs = {"native/native_carousel.cpp": native, "native/r132_startup_loading.h": helper,
               "frontend/station_frontend.cpp": frontend}
    receipt = {"schema": 1, "revision": "R132-loading-overlay", "compiled": False,
        "inputSha256": {"nativeCarousel": digest(native_cpp), "frontend": digest(frontend_cpp)},
        "outputSha256": {name: digest(raw) for name, raw in outputs.items()},
        "exactByteInverse": True, "nativeReplacementCount": len(NATIVE_REPLACEMENTS),
        "frontendReplacementCount": len(FRONTEND_REPLACEMENTS),
        "sourceParents": {"nativeR131Generated": NATIVE_SHA, "closedSonySynopsisOverlay": SYNOPSIS_NATIVE_SHA,
            "frontendR124": FRONTEND_SHA},
        "phaseBarrier": {"originalFunction": "GuiStore::updateIntro(float)",
            "address": "0x2291b0", "relocationSlot": "0x3c15c0", "prologue": "0xb9437008",
            "loadingPhase": 0, "firstBlackFrameBeforePreparation": True,
            "terminalCatalogAndGraphicsFrameBeforeMenu": True,
            "catalogFailureUsesOriginalIntroTransitionAfterErrorFrame": True,
            "pairedFrontendExportsRequiredBeforeHooking": ["StationLoading_graphicsReady", "StationLoading_stage"]},
        "preserved": {"sameSDLAndGLContext": True, "existingShadersAndFallbacks": True,
            "effectsOffGate": True, "contextRevalidation": True, "catalogStateContract": True,
            "coverReadinessAndWelcomeAfterBarrier": True, "maximumMenuFPS": 30,
            "videoLoopPreferenceAndSingleFocusedDecoder": True, "collectionsSinglePass": True,
            "coversAndDownloadsAndCache": True, "emulatorAndOnlineRoutes": True},
        "limits": {"totalShaderTimeReduced": False, "binaryProgramCacheImplemented": False,
            "genuineDriverFailureCompletesWithExistingFallback": True, "physicalStartupValidated": False,
            "apkBuiltOrInstalled": False}}
    return outputs, receipt


def verify_bindings(owner: bytes, relocations: bytes) -> dict:
    require(digest(owner) == OWNER_SHA, "Pinned GuiStore owner changed")
    require(int.from_bytes(owner[INTRO_ADDRESS:INTRO_ADDRESS+4], "little") == INTRO_PROLOGUE,
            "GuiStore intro ABI changed")
    require(digest(relocations) == RELOCATION_SHA, "Pinned relocation table changed")
    require(relocations.count(b"{0x3c15c0,0x2291b0},") == 1, "Intro GOT target is missing or ambiguous")
    return {"ownerSha256": OWNER_SHA, "relocationTableSha256": RELOCATION_SHA,
            "introABIAndRelocationChecked": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-source", type=Path, required=True)
    parser.add_argument("--frontend-source", type=Path, default=BASE / "frontend/station_frontend.cpp")
    parser.add_argument("--owner", type=Path, required=True)
    parser.add_argument("--relocations", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    outputs, receipt = patch(args.native_source.read_bytes(), args.frontend_source.read_bytes())
    receipt["verifiedBindings"] = verify_bindings(args.owner.read_bytes(), args.relocations.read_bytes())
    if args.check_only:
        require(args.out is None, "Check-only does not accept an output directory")
    else:
        require(args.out is not None, "Choose an explicit isolated output directory")
        target = args.out.resolve()
        protected = (REPO.resolve(), args.native_source.resolve().parent, args.frontend_source.resolve().parent)
        require(all(target != p and p not in target.parents for p in protected),
                "Overlay output must be outside the source and historical trees")
        require(not target.exists(), "Overlay output must be new; no replacement or deletion")
        target.mkdir(parents=True)
        for name, raw in outputs.items():
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        (target / "loading-patch.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
