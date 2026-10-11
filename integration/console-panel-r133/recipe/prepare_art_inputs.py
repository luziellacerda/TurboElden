"""Compile three unchanged official hardware photographs into local RGBA inputs.

This is an offline input compiler, not runtime downloading or a new renderer.
It only converts, proportionally resamples and pads the already transparent
photographs. It never paints, removes a background, recreates logos or crops
hardware. Raw photographs and generated pixels remain outside Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, __version__ as PILLOW_VERSION

SOURCES = {
    "psp": {
        "primaryPage": "https://www.playstation.com/en-us/playstation-history/2000-ps2-psp/",
        "assetUrl": "https://gmedia.playstation.com/is/image/SIEPDC/ps2-PSPlarge-image-block-01-en-18nov24?$1600px--t$",
        "sha256": "ecd1c3c878af94d35b88e37c08f28b866258cc0a2f07b36f03eecf85c24020a6",
        "bytes": 1516198, "dimensions": [1600, 812],
    },
    "ps3": {
        "primaryPage": "https://www.playstation.com/en-us/playstation-history/2007-ps3-ps-vita/",
        "assetUrl": "https://gmedia.playstation.com/is/image/SIEPDC/ps3-ConsoleSlim-image-block-01-en-09oct24?$1600px--t$",
        "sha256": "66f117f627f806dcc203064a503f15e87415495ff76838c4815b9a6e00e10609",
        "bytes": 2353287, "dimensions": [1600, 1739],
        "depictedHardwareVariant": "PlayStation 3 Slim",
    },
    "ps4": {
        "primaryPage": "https://www.playstation.com/en-us/playstation-history/2013-ps4-ps-vr/",
        "assetUrl": "https://gmedia.playstation.com/is/image/SIEPDC/ps4-console-image-block-01-en-09oct24?$1600px--t$",
        "sha256": "16ff2a69f7a1395c064c335afc9d252eefd5438e26d61a0d9d2234f0b721454b",
        "bytes": 648785, "dimensions": [1600, 607],
    },
}
SIDE = 512
RGBA_BYTES = SIDE * SIDE * 4


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def prepare(sources: dict[str, Path], out: Path) -> dict:
    if set(sources) != set(SOURCES):
        raise ValueError("Exactly PSP, PS3 and PS4 sources are required")
    if out.exists():
        raise ValueError("Refusing to replace prepared art inputs")
    inputs = {}
    outputs = {}
    # Validate and calculate all three before creating the output directory.
    for key, path in sources.items():
        raw = path.read_bytes()
        expected = SOURCES[key]
        if len(raw) != expected["bytes"] or digest(raw) != expected["sha256"]:
            raise ValueError("Exact official photograph required: " + key)
        with Image.open(path) as original:
            if original.format != "PNG" or original.mode != "RGBA":
                raise ValueError("Native transparent PNG required: " + key)
            if list(original.size) != expected["dimensions"]:
                raise ValueError("Original dimensions changed: " + key)
            if original.getchannel("A").getextrema() != (0, 255):
                raise ValueError("Do not synthesize or flatten transparency: " + key)
            scale = min(SIDE / original.width, SIDE / original.height)
            size = (round(original.width * scale), round(original.height * scale))
            resized = original.resize(size, Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (SIDE, SIDE), (0, 0, 0, 0))
            canvas.paste(resized, ((SIDE-size[0])//2, (SIDE-size[1])//2))
            pixels = canvas.tobytes()
            if len(pixels) != RGBA_BYTES or canvas.getchannel("A").getextrema() != (0, 255):
                raise ValueError("Prepared RGBA contract failed: " + key)
            inputs[key] = {
                **expected, "sourceSha256": expected["sha256"],
                "rgbaSha256": digest(pixels), "rgbaBytes": RGBA_BYTES,
                "width": SIDE, "height": SIDE,
                "nativeHardwareAlphaBounds": list(canvas.getchannel("A").getbbox()),
                "proportionalContentDimensions": list(size),
                "rgbaFile": key+".rgba", "previewFile": key+".png",
            }
            outputs[key] = (canvas, pixels)
    out.mkdir(parents=True, exist_ok=False)
    for key, (canvas, pixels) in outputs.items():
        (out/(key+".rgba")).write_bytes(pixels)
        canvas.save(out/(key+".png"), compress_level=9)
        inputs[key]["previewSha256"] = digest((out/(key+".png")).read_bytes())
    receipt = {
        "schema": "station.console.panel.art.v1", "revision": "R133",
        "inputCompilerSha256": digest(Path(__file__).read_bytes()),
        "pillowVersion": PILLOW_VERSION, "arts": inputs,
        "imageOperations": ["proportional-lanczos-resample", "transparent-padding", "rgba-export"],
        "hardwareOrLogosRedrawn": False, "backgroundRemoved": False,
        "runtimeNetworkRequests": False, "sourcePhotosIncludedInGit": False,
        "rawRgbaAdditionalBytes": 3 * RGBA_BYTES,
        "physicalValidation": False,
    }
    (out/"art-receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in SOURCES:
        parser.add_argument("--"+key, type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = prepare({key: getattr(args, key) for key in SOURCES}, args.out)
    print(json.dumps({key: {name: value for name, value in row.items()
                           if name in ("rgbaSha256", "rgbaBytes", "previewSha256", "nativeHardwareAlphaBounds")}
                      for key, row in receipt["arts"].items()}, indent=2))


if __name__ == "__main__":
    main()
