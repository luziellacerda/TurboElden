"""Create a closed R133 console-art include overlay on the exact R132 source.

No compilation, packaging, native renderer changes or runtime downloads happen
here. The original 19 illustrations, alias rows and GL/layout bodies have exact
byte inverses. Only three static images and seven aliases are appended.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
R132_SOURCE_COMMIT = "56ba83b7fcc5c243ae50052fec9b6f4141e1b5f1"
R132_APK_SHA256 = "47a619a194c095e70738a4d191fb8491ee410d868e4c11742530ffcaaf844f20"
R132_CAROUSEL_SHA256 = "0dc370523a448f2966a53563d90a73b3dc1555648c2ab87c02ea1a17470053cb"
INPUT_SHA256 = {
    "native_carousel.cpp": "ffe60b497f7493d1c0d666c80ad499a6c94d271ee9009cd5e6a94c461313199b",
    "native_console.h": "ea38ab513788ae0bd5207b17648894214e4e84a15d4fcd12e4451bd891bce79d",
    "station_console_keys.h": "900529957c34c2d0796ad906d79cc9c67a8d2fb59613bf2b3d4f75b386a2ca63",
    "console_assets.h": "d252beffcdf89c7641d93c7aaaa104a5849560ef49cb9c81e3156505756cfc1a",
}
RGBA_SHA256 = {
    "psp": "f66ae0cb084fb47fc9c59a024f9e6919c60a862ba29cb5edebfe01bdc694ad47",
    "ps3": "336b86e2009a7e2506e71c863863f6f5f44d24868485dc662d23d4950ad789d9",
    "ps4": "986d4086a5ce411ac764cb141cec9bda2ac0ab9652a2a5a96dace5db954b1c72",
}
ORIGINAL_KEYS = (
    "snes", "megadrive", "n64", "neogeo", "neogeocd", "naomi", "naomi2",
    "dreamcast", "cps1", "cps2", "cps3", "gamecube", "wiiu", "switch",
    "psx", "wii", "saturn", "xbox360", "fbneo",
)
ADDED_ALIASES = (
    ("PSP", "psp"), ("Psp - BR", "psp"), ("pspbr", "psp"),
    ("Playstation 3", "ps3"), ("ps3", "ps3"),
    ("Playstation 4", "ps4"), ("ps4", "ps4"),
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(value, message: str) -> None:
    if not value:
        raise ValueError(message)


def replace_once(raw: bytes, old: bytes, new: bytes) -> bytes:
    require(raw.count(old) == 1 and new not in raw, "Exact original include anchor required")
    result = raw.replace(old, new, 1)
    require(result.replace(new, old, 1) == raw, "Include inverse differs")
    return result


def read_art_inputs(receipt_path: Path) -> tuple[dict[str, bytes], dict]:
    receipt_raw = receipt_path.read_bytes()
    receipt = json.loads(receipt_raw)
    require(receipt.get("schema") == "station.console.panel.art.v1" and receipt.get("revision") == "R133",
            "Exact R133 art receipt required")
    compiler_path = ROOT/"recipe/prepare_art_inputs.py"
    require(receipt.get("inputCompilerSha256") == sha(compiler_path.read_bytes()), "Art input compiler changed")
    spec = importlib.util.spec_from_file_location("station_r133_art_compiler", compiler_path)
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    require(set(receipt.get("arts", {})) == set(RGBA_SHA256), "Exactly three reviewed console arts required")
    require(receipt.get("hardwareOrLogosRedrawn") is False and receipt.get("backgroundRemoved") is False,
            "Original official hardware photographs must be retained")
    pixels = {}
    for key, checksum in RGBA_SHA256.items():
        row = receipt["arts"][key]
        original = compiler.SOURCES[key]
        for name in ("primaryPage", "assetUrl", "sha256", "bytes", "dimensions"):
            require(row.get(name) == original[name], "Official provenance changed: "+key)
        require(row.get("rgbaFile") == key+".rgba", "RGBA path must be the exact local leaf")
        require(row.get("width") == 512 and row.get("height") == 512 and row.get("rgbaBytes") == 1048576,
                "Original 512-square console art format required")
        path = receipt_path.parent/(key+".rgba")
        require(not path.is_symlink(), "RGBA symbolic inputs are refused")
        raw = path.read_bytes()
        require(len(raw) == 1048576 and sha(raw) == checksum and row.get("rgbaSha256") == checksum,
                "Exact prepared pixels required: "+key)
        require(min(raw[3::4]) == 0 and max(raw[3::4]) == 255, "Native alpha required: "+key)
        pixels[key] = raw
    return pixels, {"path": str(receipt_path.resolve()), "sha256": sha(receipt_raw), "arts": receipt["arts"]}


def emit_array(key: str, raw: bytes) -> bytes:
    rows = [b"static const unsigned char stationConsole_"+key.encode("ascii")+b"[]={\r\n"]
    for start in range(0, len(raw), 128):
        rows.append(b",".join(str(value).encode("ascii") for value in raw[start:start+128])+b",\r\n")
    rows.append(b"};\r\n")
    return b"".join(rows)


def patch(native_cpp: bytes, native_console: bytes, console_keys: bytes,
          console_assets: bytes, pixels: dict[str, bytes]) -> tuple[bytes, dict[str, bytes], dict]:
    inputs = dict(zip(INPUT_SHA256, (native_cpp, native_console, console_keys, console_assets)))
    for name, raw in inputs.items():
        require(sha(raw) == INPUT_SHA256[name], "Exact retained R132 input required: "+name)
    require(set(pixels) == set(RGBA_SHA256), "Exactly PSP, PS3 and PS4 inputs required")
    for key, raw in pixels.items():
        require(len(raw) == 1048576 and sha(raw) == RGBA_SHA256[key], "Reviewed RGBA pixels changed: "+key)

    cpp_old = b'#include "native_console.h"'
    cpp_new = b'#include "r133_native_console.h"'
    changed_cpp = replace_once(native_cpp, cpp_old, cpp_new)
    assets_old = b'#include "console_assets.h"'
    assets_new = b'#include "r133_console_assets.h"'
    keys_old = b'#include "station_console_keys.h"'
    keys_new = b'#include "r133_station_console_keys.h"'
    console_header = replace_once(native_console, assets_old, assets_new)
    console_header = replace_once(console_header, keys_old, keys_new)
    require(console_header.replace(keys_new, keys_old, 1).replace(assets_new, assets_old, 1) == native_console,
            "GL/layout/cache/lifecycle console body changed")

    original_rows = b",".join(b'{"'+key.encode()+b'",512,512,stationConsole_'+key.encode()+b'}'
                             for key in ORIGINAL_KEYS)
    table = b"static const StationConsoleAsset stationConsoleAssets[]={"+original_rows+b"};\r\n"
    require(console_assets.endswith(table) and console_assets.count(table) == 1, "Original 19-row art table changed")
    preserved_array_prefix = console_assets[:-len(table)]
    names = re.findall(rb"static const unsigned char stationConsole_([a-z0-9]+)\[\]=", preserved_array_prefix)
    require(names == [key.encode() for key in ORIGINAL_KEYS], "Original hardware array order changed")
    added_arrays = b"".join(emit_array(key, pixels[key]) for key in RGBA_SHA256)
    new_rows = b",".join(b'{"'+key.encode()+b'",512,512,stationConsole_'+key.encode()+b'}'
                        for key in RGBA_SHA256)
    changed_table = table[:-4]+b","+new_rows+b"};\r\n"
    assets_header = preserved_array_prefix+added_arrays+changed_table
    inverse_assets = assets_header[:len(preserved_array_prefix)]+table
    require(inverse_assets == console_assets, "Original 19 RGBA declarations or table bytes changed")
    require(assets_header[len(preserved_array_prefix):-len(changed_table)] == added_arrays,
            "Only the three new RGBA declarations may be inserted")

    aliases_anchor = b"\r\n};\r\nstatic const char*stationConsoleKey"
    added_aliases = b",\r\n "+b",".join(b'{"'+alias.encode()+b'","'+key.encode()+b'"}'
                                        for alias, key in ADDED_ALIASES)
    aliases_new = added_aliases+aliases_anchor
    keys_header = replace_once(console_keys, aliases_anchor, aliases_new)
    old_aliases = re.findall(rb'\{"([^"\r\n]+)","([^"\r\n]+)"\}', console_keys)
    new_aliases = re.findall(rb'\{"([^"\r\n]+)","([^"\r\n]+)"\}', keys_header)
    require(new_aliases == old_aliases+[(alias.encode(), key.encode()) for alias, key in ADDED_ALIASES],
            "Existing aliases changed or unexpected rows added")
    headers = {
        "r133_native_console.h": console_header,
        "r133_station_console_keys.h": keys_header,
        "r133_console_assets.h": assets_header,
    }
    receipt = {
        "schema": "station.console.panel.overlay.v1", "revision": "R133",
        "parentExecutableSourceCommit": R132_SOURCE_COMMIT,
        "parentApkSha256": R132_APK_SHA256, "parentCarouselSha256": R132_CAROUSEL_SHA256,
        "inputSha256": INPUT_SHA256, "nativeCppSha256": sha(changed_cpp),
        "outputHeaderSha256": {name: sha(raw) for name, raw in headers.items()},
        "recipeSha256": sha(Path(__file__).read_bytes()),
        "originalHardwareFamilies": list(ORIGINAL_KEYS), "addedHardwareFamilies": list(RGBA_SHA256),
        "addedAliases": [list(row) for row in ADDED_ALIASES],
        "original19RgbaDeclarationsByteIdentical": True, "original19ArtRowsByteIdentical": True,
        "originalAliasesByteIdentical": True, "nativeCppExactInverse": True,
        "consoleConsumerExactInverse": True, "sameNintendoPanelLayout": True,
        "sameProgramGlContextAndStateRestoration": True, "sameLazyTextureCreationAndContextInvalidation": True,
        "sameOneTimeAlphaBoundsAndVisibleHardwareFit": True,
        "sameCollectionAndSystemsModeVisibilityRules": True,
        "sameLoadingPrewarmBarrier": True,
        "preserved": ["all-40-DEX", "frontend", "manifest", "resources", "emulator-routes", "controllers",
                      "video", "LED", "economy", "background-effects", "cache", "30fps", "online-transports"],
        "resourceCosts": {
            "textureFamiliesBefore": 19, "textureFamiliesAfter": 22,
            "rawRgbaAdditionalBytes": 3145728, "additionalGpuBytesPerVisitedNewFamily": 1048576,
            "additionalGpuBytesIfAllThreeVisitedInOneContext": 3145728,
            "additionalDecoderCount": 0, "additionalThreads": 0, "additionalTimers": 0,
            "additionalShaders": 0, "additionalFramebufferObjects": 0,
            "firstVisitAlphaBoundsScanRemains": True, "firstVisitTextureUploadRemains": True,
            "thermalOrZeroCpuCostClaim": False,
        },
        "runtimeIdentityRenewalRequired": ["psx", "n64", "gamecube", "wii"],
        "sonyOnlineAdded": False, "compiled": False, "packaged": False, "physicalValidation": False,
    }
    return changed_cpp, headers, receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-cpp", type=Path, required=True)
    parser.add_argument("--native-console", type=Path, required=True)
    parser.add_argument("--console-keys", type=Path, required=True)
    parser.add_argument("--console-assets", type=Path, required=True)
    parser.add_argument("--art-receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Refusing to replace an overlay directory")
    pixels, art_info = read_art_inputs(args.art_receipt)
    changed_cpp, headers, receipt = patch(args.native_cpp.read_bytes(), args.native_console.read_bytes(),
                                          args.console_keys.read_bytes(), args.console_assets.read_bytes(), pixels)
    receipt["artInputs"] = art_info
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out/"native_carousel.cpp").write_bytes(changed_cpp)
    for name, raw in headers.items():
        (args.out/name).write_bytes(raw)
    (args.out/"overlay-receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"nativeCppSha256": receipt["nativeCppSha256"],
                      "outputHeaderSha256": receipt["outputHeaderSha256"],
                      "resourceCosts": receipt["resourceCosts"]}, indent=2))


if __name__ == "__main__":
    main()
