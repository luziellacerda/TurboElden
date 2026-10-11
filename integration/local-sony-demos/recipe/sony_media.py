"""Prepare two private owner-provided Sony clips for the existing video engine.

No APK, public media, decoder, renderer or runtime policy is produced here.
The original 24 fps silent clips are copied unchanged; two first-frame RGB565
posters and additive native headers/data object use the established engine.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
R124 = REPO / "versions/station-video-room-footer-r124-20261011"
DEFAULT_MEDIA_ROOT = Path(r"G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas")
FFMPEG_SHA = "57c56e369d5b4873b4d93fc1a1d833cb7cd8bc9325c14b05c34ce60b22842d8a"
FFPROBE_SHA = "afe05347caaabe479b3c4eae71992b6ec1e11c57266a1d665deb0f9fe9847208"
CLIPS = {
    "ps3": {"key": "Playstation 3", "sha256": "d6fb573d754c5a21edc633cf1b3ce61fd4c2f5d2615881178aee9427f8354ff9", "bytes": 394498},
    "ps4": {"key": "Playstation 4", "sha256": "4162ed5331876ab0749fc5abe287f419af0b90b980ecafd32947422ee13643ae", "bytes": 392306},
}
HEADERS = {
    "d0/native_system_video720.h": "6a5bdc4e6a83e2dd490ee7a52e69bbd02c1ea9433155b3cfb1144dc86d5d0a78",
    "d0/video720_posters.h": "1b2474f0b6793368d28c7826ac1aa83537760ac85b7445f4d142cc861a42529f",
    "d1/system_video720_assets.h": "2d0e351bed93dd3f26548f6b92157f232b81a3df9586cd65c0900f1ce1df3cf5",
}
OLD_NATIVE_INCLUDE = b'#include "native_system_video720.h"'
NEW_NATIVE_INCLUDE = b'#include "sony_native_system_video720.h"'
FRAME_BYTES = 720 * 720 * 2


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def regular(path):
    """Reject links/reparse points at the file and its existing ancestors."""
    path = Path(os.path.abspath(path))
    for candidate in (path, *path.parents):
        info = candidate.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError("Linked/reparse input is not accepted: " + str(candidate))
    if not path.is_file():
        raise ValueError("A regular input file is required: " + str(path))
    return path


def pinned_file(path, digest, size=None):
    path = regular(path)
    if sha(path) != digest or (size is not None and path.stat().st_size != size):
        raise ValueError("Private input differs from the audited source: " + str(path))
    return path


def source_inputs(native_inputs):
    resolved = {}
    for name, digest in HEADERS.items():
        public = R124 / "native" / name
        selected = public if public.is_file() else Path(native_inputs) / name
        resolved[name] = pinned_file(selected, digest)
        shadow = Path(native_inputs) / name
        if shadow.exists():
            pinned_file(shadow, digest)
    return resolved


def execute(args, *, cwd=None, timeout=120):
    result = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True,
                            encoding="utf-8", errors="replace", timeout=timeout)
    if result.returncode:
        raise RuntimeError("Sony media preparation failed: " + Path(args[0]).name + "\n" + result.stderr[-4000:])
    return result.stdout


def probe(ffprobe, source):
    value = json.loads(execute([ffprobe, "-v", "error", "-show_entries",
        "format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,pix_fmt",
        "-of", "json", source]))
    streams = value.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    if len(videos) != 1 or any(s.get("codec_type") != "video" for s in streams):
        raise ValueError("The Sony platform clip must contain exactly one video stream and no audio")
    video = videos[0]
    if (video.get("codec_name"), video.get("width"), video.get("height"), video.get("pix_fmt")) != ("hevc", 720, 720, "yuv420p"):
        raise ValueError("Unexpected Sony video codec/resolution/pixel format")
    if Fraction(video.get("avg_frame_rate", "0")) != 24 or Fraction(video.get("r_frame_rate", "0")) != 24:
        raise ValueError("Only the audited original 24 fps Sony clips are accepted")
    if abs(float(value.get("format", {}).get("duration", "0")) - 6.041667) > 0.000002:
        raise ValueError("Sony clip duration differs from the audited source")
    return value


def add_rows(raw, marker, rows, expected_count):
    """Append table entries while retaining the complete original prefix."""
    if raw.count(marker) != 1:
        raise ValueError("Native table declaration changed")
    start = raw.index(marker) + len(marker)
    end = raw.rfind(b"};")
    if end < start or raw[end + 2:].strip():
        raise ValueError("Native table termination changed")
    entries = re.findall(rb'^\{"[^"\r\n]+",[^\r\n]+\},\r?$', raw[start:end], re.M)
    if len(entries) != expected_count:
        raise ValueError("Existing native table entry count changed")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    addition = newline.join(rows) + newline
    changed = raw[:end] + addition + raw[end:]
    if changed[:end] != raw[:end] or changed[end + len(addition):] != raw[end:]:
        raise ValueError("An original table byte changed")
    return changed, addition


def headers(resolved):
    original_map = resolved["d1/system_video720_assets.h"].read_bytes()
    original_posters = resolved["d0/video720_posters.h"].read_bytes()
    for name in CLIPS:
        asset = ('turbo-system-videos/720-' + name + '.mp4').encode("ascii")
        if asset in original_map or asset in original_posters:
            raise ValueError("Sony media must not replace an existing entry")
    map_rows = [('{"' + info["key"] + '","turbo-system-videos/720-' + name + '.mp4"},').encode("ascii")
                for name, info in CLIPS.items()]
    updated_map, map_addition = add_rows(original_map,
        b"static const SystemVideo720Def systemVideo720Definitions[]={", map_rows, 44)
    poster_rows = [('{"turbo-system-videos/720-' + name + '.mp4",station_video_sony_' + name + '},').encode("ascii") for name in CLIPS]
    updated_posters, poster_addition = add_rows(original_posters,
        b"static const Video720Poster video720Posters[]={", poster_rows, 58)
    newline = b"\r\n" if b"\r\n" in original_posters else b"\n"
    external_anchor = b"}" + newline + b"static const Video720Poster video720Posters[]={"
    externs = newline.join(('extern const unsigned char station_video_sony_' + name + '[];').encode("ascii") for name in CLIPS) + newline
    if updated_posters.count(external_anchor) != 1:
        raise ValueError("Original C-linkage poster declaration changed")
    updated_posters = updated_posters.replace(external_anchor, externs + external_anchor, 1)
    if updated_map.replace(map_addition, b"", 1) != original_map or updated_posters.replace(externs, b"", 1).replace(poster_addition, b"", 1) != original_posters:
        raise ValueError("Original map/poster entries are not exactly retained")
    original_engine = resolved["d0/native_system_video720.h"].read_bytes()
    updated_engine = original_engine
    includes = ((b'"system_video720_assets.h"', b'"sony_system_video720_assets.h"'),
                (b'"video720_posters.h"', b'"sony_video720_posters.h"'))
    for old, new in includes:
        if updated_engine.count(b"#include " + old) != 1:
            raise ValueError("Original video engine include changed")
        updated_engine = updated_engine.replace(b"#include " + old, b"#include " + new, 1)
    restored = updated_engine
    for old, new in reversed(includes):
        restored = restored.replace(b"#include " + new, b"#include " + old, 1)
    if restored != original_engine:
        raise ValueError("A video engine method changed")
    return {"sony_system_video720_assets.h": updated_map,
            "sony_video720_posters.h": updated_posters,
            "sony_native_system_video720.h": updated_engine}


def patch_native(raw):
    """Select the additive header explicitly, without changing a C++ method."""
    if raw.count(OLD_NATIVE_INCLUDE) != 1 or NEW_NATIVE_INCLUDE in raw:
        raise ValueError("The original carousel video include changed")
    result = raw.replace(OLD_NATIVE_INCLUDE, NEW_NATIVE_INCLUDE, 1)
    if result.replace(NEW_NATIVE_INCLUDE, OLD_NATIVE_INCLUDE, 1) != raw:
        raise ValueError("Unexpected carousel source modification")
    return result


def result_for(out, receipt):
    result = dict(receipt)
    result["payloads"] = {name: {**info, "path": str(out / info["path"])}
                          for name, info in receipt["payloads"].items()}
    result["includeDirectory"] = str(out / receipt["includeDirectory"])
    result["extraObjects"] = [str(out / name) for name in receipt["extraObjects"]]
    result["receiptPath"] = str(out / "sony-media.json")
    result["sourceTransform"] = patch_native
    return result


def prepare(native_inputs, ndk_bin, out, ffmpeg, ffprobe, *, media_root=None):
    """Return private payloads, includeDirectory, extraObjects and sourceTransform.

    Reuse is admitted only after all source pins, tools and every generated file
    match. Existing partial/foreign output is never removed or overwritten.
    """
    out = Path(os.path.abspath(out))
    if out == ROOT or ROOT in out.parents or out in ROOT.parents:
        raise ValueError("Private media outputs must stay outside the source tree")
    media_root = Path(media_root) if media_root is not None else DEFAULT_MEDIA_ROOT
    resolved = source_inputs(Path(native_inputs))
    ffmpeg = pinned_file(ffmpeg, FFMPEG_SHA)
    ffprobe = pinned_file(ffprobe, FFPROBE_SHA)
    clang = regular(Path(ndk_bin) / "clang.exe")
    readelf = regular(Path(ndk_bin) / "llvm-readelf.exe")
    media = {name: pinned_file(media_root / (name + ".mp4"), info["sha256"], info["bytes"])
             for name, info in CLIPS.items()}
    pins = {"recipe/sony_media.py": sha(Path(__file__)),
            "headers": {name: sha(path) for name, path in resolved.items()},
            "videos": {name: sha(path) for name, path in media.items()},
            "tools": {"ffmpeg": sha(ffmpeg), "ffprobe": sha(ffprobe), "clang": sha(clang), "llvm-readelf": sha(readelf)}}
    if out.exists():
        receipt_path = out / "sony-media.json"
        if not receipt_path.is_file():
            raise ValueError("Existing output has no complete Sony media receipt")
        receipt = json.loads(regular(receipt_path).read_text(encoding="utf-8"))
        if receipt.get("passed") is not True or receipt.get("sourcePins") != pins:
            raise ValueError("Existing Sony media source pins differ; do not reuse")
        expected = set(receipt["files"])
        found = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file() and p != receipt_path}
        if expected != found:
            raise ValueError("The prepared Sony media file set changed")
        for name, info in receipt["files"].items():
            pinned_file(out / name, info["sha256"], info["bytes"])
        return result_for(out, receipt)
    if not out.parent.is_dir():
        raise ValueError("The private output parent must already exist")
    for candidate in (out.parent, *out.parent.parents):
        info = candidate.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError("Linked output directories are not accepted")
    header_data = headers(resolved)
    metadata = {name: probe(ffprobe, path) for name, path in media.items()}
    out.mkdir()
    for directory in ("include", "posters", "assets/turbo-system-videos"):
        (out / directory).mkdir(parents=True, exist_ok=True)
    for name, raw in header_data.items():
        (out / "include" / name).write_bytes(raw)
    payloads = {}
    for name, original in media.items():
        asset_name = "assets/turbo-system-videos/720-" + name + ".mp4"
        target = out / asset_name
        shutil.copyfile(original, target)
        pinned_file(target, CLIPS[name]["sha256"], CLIPS[name]["bytes"])
        payloads[asset_name] = {"path": asset_name, "sha256": sha(target), "bytes": target.stat().st_size}
        frame = out / "posters" / ("station_video_sony_" + name + ".rgb565")
        execute([ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-threads", "1", "-i", original,
                 "-map", "0:v:0", "-an", "-frames:v", "1", "-filter_threads", "1",
                 "-vf", "vflip,format=rgb565le", "-fflags", "+bitexact", "-flags", "+bitexact",
                 "-f", "rawvideo", "-n", frame])
        if frame.stat().st_size != FRAME_BYTES:
            raise ValueError("The RGB565 poster must be exactly 720×720×2 bytes")
    assembly = []
    for name in CLIPS:
        symbol = "station_video_sony_" + name
        assembly += ['.section .rodata.' + symbol + ',"a",%progbits', '.p2align 4',
                     '.global ' + symbol, '.hidden ' + symbol, '.type ' + symbol + ',%object',
                     symbol + ':', '.incbin "posters/' + symbol + '.rgb565"',
                     '.size ' + symbol + ',.-' + symbol]
    assembly += ['.section .note.GNU-stack,"",%progbits']
    source = out / "sony_video720_posters.S"
    source.write_text("\n".join(assembly) + "\n", encoding="ascii", newline="\n")
    object_path = out / "sony_video720_posters.o"
    execute([clang, "--target=aarch64-linux-android26", "-c", "-x", "assembler",
             source.name, "-o", object_path.name], cwd=out)
    object_info = execute([readelf, "-h", "-sW", object_path])
    if not re.search(r"Machine:\s+AArch64", object_info):
        raise ValueError("Sony posters object is not AArch64")
    for name in CLIPS:
        if not re.search(r"\b" + str(FRAME_BYTES) + r"\s+OBJECT\s+GLOBAL\s+HIDDEN\s+\d+\s+station_video_sony_" + name + r"\b", object_info):
            raise ValueError("The RGB565 object symbol contract changed")
    if pins["recipe/sony_media.py"] != sha(Path(__file__)) or any(sha(path) != HEADERS[name] for name, path in resolved.items()) or any(sha(path) != CLIPS[name]["sha256"] for name, path in media.items()):
        raise ValueError("A Sony media source changed during preparation")
    files = {p.relative_to(out).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size}
             for p in sorted(out.rglob("*")) if p.is_file()}
    receipt = {"schemaVersion": 1, "passed": True, "sourcePins": pins,
               "sourceMedia": metadata, "payloads": payloads, "files": files,
               "includeDirectory": "include", "extraObjects": [object_path.name],
               "systemMappingsBefore": 44, "systemMappingsAfter": 46,
               "posterEntriesBefore": 58, "posterEntriesAfter": 60,
               "existingMapAndPosterEntriesByteIdentical": True,
               "nativeVideoMethodsByteIdentical": True, "onlyNativeIncludeChanges": True,
               "posterFormat": "720x720 RGB565 little-endian, bottom row first",
               "originalSilentVideoBytesPreserved": True, "sourceFPS": 24, "maximumRenderFPS": 30,
               "decoderCountChanged": False, "singlePassChanged": False,
               "stopTwoFramesBeforeEndChanged": False, "graphicsEconomyChanged": False,
               "textureBudgetChanged": False, "gpuFrameWorkAdded": False,
               "apkProduced": False, "physicalVisualValidation": False}
    temporary = out / ".sony-media.json.tmp"
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, out / "sony-media.json")
    return result_for(out, receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("native-inputs", "ndk-bin", "out", "ffmpeg", "ffprobe"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--media-root", type=Path, default=DEFAULT_MEDIA_ROOT)
    args = parser.parse_args()
    result = prepare(args.native_inputs, args.ndk_bin, args.out, args.ffmpeg,
                     args.ffprobe, media_root=args.media_root)
    print(json.dumps({key: value for key, value in result.items() if key != "sourceTransform"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
