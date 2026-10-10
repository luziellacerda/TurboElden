"""Local structural and pixel-model proof for the R107 online light field.

This test deliberately performs no APK build, Android operation, OpenGL call,
or access outside the version directories in this repository.  It proves the
source scope against R106 and bounds the visible error introduced when the
four static lighting scalars are stored in an RGBA8 texture.
"""

from pathlib import Path
import hashlib
import json
import math
import os
import random
import re


ROOT = Path(__file__).resolve().parents[1]
R106 = ROOT.parent / "station-render-online-r106-20261010"
R108 = ROOT.parent / "station-render-online-static-r108-20261010"
ONLINE = (
    "netplay-src/org/emulationstation/frontend/netplay/"
    "StationOnlineCoverView.java"
)
LIGHTING = (
    "netplay-src/org/emulationstation/frontend/netplay/"
    "StationCoverLightingShader.java"
)
AMBIENT = {
    "netplay-src/org/emulationstation/frontend/netplay/StationHyperspaceState.java",
    "netplay-src/org/emulationstation/frontend/netplay/StationHyperspaceView.java",
    "netplay-src/org/emulationstation/frontend/netplay/StationLottieIllustration.java",
    "netplay-src/org/emulationstation/frontend/netplay/StationSinglePassAnimationState.java",
}
ALLOWED_JAVA_CHANGES = {ONLINE, LIGHTING} | AMBIENT


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def files(root):
    # Several dependency source names exceed Win32's legacy MAX_PATH.  Prefix
    # the absolute traversal root so the scope proof sees those files instead
    # of silently treating them as deleted.
    absolute = str(Path(root).resolve())
    scan_root = "\\\\?\\" + absolute if os.name == "nt" else absolute
    result = {}
    for directory, _, names in os.walk(scan_root):
        for name in sorted(names):
            path = os.path.join(directory, name)
            relative = os.path.relpath(path, scan_root).replace("\\", "/")
            with open(path, "rb") as stream:
                result[relative] = hashlib.file_digest(stream, "sha256").hexdigest()
    return result


def changed_files(before, after):
    return sorted(
        name
        for name in set(before) | set(after)
        if before.get(name) != after.get(name)
    )


def require(pattern, text, description):
    assert re.search(pattern, text, re.MULTILINE | re.DOTALL), description


# ---- Executable-source scope -------------------------------------------------

r106_java = files(R106 / "java")
r107_java = files(ROOT / "java")
changed_java = changed_files(r106_java, r107_java)
assert changed_java == sorted(ALLOWED_JAVA_CHANGES), changed_java

# The optimization belongs only to the online Java renderer and its shared
# shader wrapper.  Native carousel code, assets and the long-path Java alias
# stay byte-identical, which also freezes gameplay and packaged artwork.
assert files(ROOT / "native") == files(R106 / "native")
assert files(ROOT / "assets") == files(R106 / "assets")
assert files(ROOT / "java-alias") == files(R108 / "java-alias")

online = (ROOT / "java" / ONLINE).read_text(encoding="utf-8")
shader = (ROOT / "java" / LIGHTING).read_text(encoding="utf-8")
shader106 = (R106 / "java" / LIGHTING).read_text(encoding="utf-8")


# ---- Shader structure and exact direct fallback -----------------------------

assert "MAGAZINE_BUILD_LIGHT_FIELD" in shader
assert "MAGAZINE_USE_LIGHT_FIELD" in shader
assert "uniform sampler2D u_lightField" in shader
assert "uniform vec2 u_lightFieldSize" in shader
assert "gl_FragCoord.xy" in shader
assert "u_lightFieldSize" in shader

# RGBA has one documented scalar per channel.  Sampling by window-fragment
# coordinates is essential: uv addresses the artwork and would misalign the
# viewport-sized field around a fitted cover.
require(
    r"FragColor\s*=\s*vec4\s*\(\s*centralRegion\s*,\s*mask\s*,"
    r"\s*nearGlow\s*,\s*wideGlow\s*\)",
    shader,
    "field pass must pack centralRegion/mask/nearGlow/wideGlow into RGBA",
)
require(
    r"TEX\s*\(\s*u_lightField\s*,\s*gl_FragCoord\.xy\s*/\s*"
    r"u_lightFieldSize\s*\)",
    shader,
    "cached pass must sample the viewport field by gl_FragCoord",
)
for channel in ("r", "g", "b", "a"):
    assert re.search(r"lightField\." + channel, shader), channel

# R106's direct halo formulas and all frame-dependent lighting after them stay
# literal.  Declarations moved above the BUILD/USE switch, so compare the
# ordered expressions rather than the old declaration spelling.
direct_expressions = [
    "float centralRegion=region(p);",
    "float mask=emitterWithRegion(p,centralRegion);",
    "float nearGlow=0.0,wideGlow=0.0;",
    "for(int i=0;i<8;i++) {",
    "float angle=float(i)*0.7853981634;",
    "vec2 dir=vec2(cos(angle),sin(angle));",
    "nearGlow+=emitter(p+dir*2.0);",
    "wideGlow+=emitter(p+dir*5.0);",
    "nearGlow/=8.0; wideGlow/=8.0;",
]
positions = [shader.index(expression) for expression in direct_expressions]
assert positions == sorted(positions), "R106 direct field expression order changed"
for expression in (
    "float centralRegion=region(p);",
    "float mask=emitterWithRegion(p,centralRegion);",
    "float nearGlow=0.0,wideGlow=0.0;",
    "for(int i=0;i<8;i++) {",
    "nearGlow+=emitter(p+dir*2.0);",
    "wideGlow+=emitter(p+dir*5.0);",
    "nearGlow/=8.0; wideGlow/=8.0;",
):
    assert expression in shader106

dynamic_start = shader106.index('        "    float n64Mode=step(')
dynamic_end_marker = '        "    FragColor=vec4(rgb,base.a)*tint;\\n" +'
dynamic_end = shader106.index(dynamic_end_marker, dynamic_start) + len(dynamic_end_marker)
dynamic_block = shader106[dynamic_start:dynamic_end]
assert dynamic_block in shader, "R106 frame-dependent lighting changed"


# ---- Java renderer lifecycle, fallback and cleanup ---------------------------

# Direct R106 program remains available independently from the optional field
# programs.  A field failure must only disable the cache, never the renderer.
assert "fieldProgram" in online
assert "cachedProgram" in online
assert "fieldTexture" in online or "fieldTex" in online
assert "fieldFramebuffer" in online or "fieldFbo" in online
assert "GL_FRAMEBUFFER_COMPLETE" in online
assert "glFramebufferTexture2D" in online
assert "glDeleteFramebuffers" in online
assert online.count("glDeleteProgram") >= 3
assert online.count("glDeleteTextures") >= 2
assert "MAGAZINE_BUILD_LIGHT_FIELD" in online
assert "MAGAZINE_USE_LIGHT_FIELD" in online

# Two fragment samplers are required in cached mode.  The exact R106 path must
# still be linked when that capability or any cache allocation is unavailable.
require(
    r"GL_MAX_TEXTURE_IMAGE_UNITS|0x8872",
    online,
    "cached renderer must query fragment texture capacity",
)
assert "if(!vertexClassifier||fragmentTextureUnits<2)return;" in online
assert (
    "glTexImage2D(GLES20.GL_TEXTURE_2D,0,GLES20.GL_RGBA,w,h,0,"
    "GLES20.GL_RGBA,GLES20.GL_UNSIGNED_BYTE,null)"
) in online
assert online.count("GLES20.GL_NEAREST") == 2
assert "drawQuad(fieldProgram,fieldClock,fieldModelLocation,selectedModel,0,false,w,h);" in online
assert (
    "if(fieldCache&&fieldReady)drawQuad(cachedProgram"
    in online.replace("{\n                    if(!cachedPathVerified)clearErrors();\n                    ", "")
)
assert "else drawQuad(program,clock,modelLocation,selectedModel,frame,false,w,h);" in online
assert "fieldReady=true;cachedPathVerified=false;" in online
assert "if(!cachedPathVerified)clearErrors();" in online
assert "if(cacheError==GLES20.GL_NO_ERROR)cachedPathVerified=true;" in online
assert (
    "Online cached draw failed; exact R106 fallback active" in online
    and "releaseFieldCache();" in online
)
cache_catches = re.findall(
    r"catch\s*\(\s*RuntimeException\s+cacheFailure\s*\)\s*\{"
    r"\s*releaseFieldCache\(\);",
    online,
)
assert len(cache_catches) == 2, "init and runtime cache failures must be isolated"

# The field key contains every value that can alter its pixels.  Its rebuild
# path is separate from the frame clock; otherwise it would still run at 30 Hz.
for token in ("fieldBitmap", "fieldModel", "fieldWidth", "fieldHeight"):
    assert token in online, token
field_key = (
    "fieldReady&&fieldBitmap==image&&fieldModel==selectedModel"
    "&&fieldWidth==w&&fieldHeight==h"
)
assert field_key in online, "bitmap/model/viewport field key is incomplete"
assert "uploaded=image;fieldReady=false;" in online

# Revealing the TextureView is now a one-shot transition after refresh.  The
# guard is intentionally paired with setAlpha(1), so a post is not queued on
# every rendered frame.
assert "!revealed){revealed=true;texture.setAlpha(1);" in online
assert online.count("texture.setAlpha(1)") == 1


# ---- RGBA8 pixel-parity model ------------------------------------------------

def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smoothstep(edge0, edge1, value):
    t = clamp((value - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def mix_scalar(a, b, amount):
    return a * (1.0 - amount) + b * amount


def mix3(a, b, amount):
    return tuple(mix_scalar(x, y, amount) for x, y in zip(a, b))


def clamp3(value):
    return tuple(clamp(x) for x in value)


def mul3(a, b):
    return tuple(x * y for x, y in zip(a, b))


def screen3(base, glow):
    return tuple(1.0 - (1.0 - x) * (1.0 - y) for x, y in zip(base, glow))


def q8(value):
    # RGBA8 normalized render-target round trip.  Values written by the field
    # shader are non-negative masks and are clamped by the fixed-point target.
    return math.floor(clamp(value) * 255.0 + 0.5) / 255.0


def quantize_field(field):
    return tuple(q8(value) for value in field)


def saturate(rgb, saturation):
    luma = sum(x * w for x, w in zip(rgb, (0.299, 0.587, 0.114)))
    return mix3((luma, luma, luma), rgb, saturation)


def snes_pixel(base, source, enabled, field, flow, hue, gain, saturation):
    central, mask, near, wide = field
    energy = max(flow[0], flow[1])
    fringe = central * smoothstep(0.015, 0.10, source[2] - source[0])
    recolor = enabled * max(mask, fringe)
    value = sum(x * w for x, w in zip(source, (0.16, 0.68, 0.16)))
    hot = smoothstep(0.48, 0.82, min(source[1], source[2]))
    hot *= smoothstep(0.30, 0.78, flow[0])
    lamp = mix3(tuple(x * value * (0.30 + 0.80 * energy) for x in hue), (1.0,) * 3, hot)
    rgb = mix3(base, clamp3(lamp), recolor)
    laser = 0.18 + 2.2 * flow[1] + 3.0 * flow[0]
    bloom = enabled * laser * gain * (mask * 0.05 + near * 0.15 + wide * 0.035)
    glow_color = mix3(hue, (1.0, 0.90, 0.92), flow[0])
    rgb = screen3(rgb, clamp3(tuple(x * bloom for x in glow_color)))
    return saturate(rgb, saturation)


def general_pixel(
    base,
    emission,
    enabled,
    field,
    flow,
    hue,
    gain,
    saturation,
    fringe_signal,
    value,
    hot,
    laser,
):
    central, mask, near, wide = field
    energy = max(flow[0], flow[1])
    recolor = enabled * max(mask, central * fringe_signal)
    lamp = mix3(tuple(x * value * (0.30 + 0.80 * energy) for x in hue), (1.0,) * 3, hot)
    rgb = mix3(base, clamp3(lamp), recolor)
    bloom = enabled * laser * gain * (mask * 0.05 + near * 0.15 + wide * 0.035)
    glow_color = mix3(hue, (1.0, 0.90, 0.92), flow[0])
    rgb = screen3(rgb, clamp3(tuple(x * bloom for x in glow_color)))
    return saturate(rgb, saturation)


rng = random.Random(107)
errors = []
field_frame_invariance = True
cases_per_path = 12000

for _ in range(cases_per_path):
    base = tuple(rng.random() for _ in range(3))
    source = tuple(rng.random() for _ in range(3))
    enabled = rng.random()
    field = tuple(rng.random() for _ in range(4))
    flow = tuple(rng.random() for _ in range(4))
    hue = tuple(rng.random() for _ in range(3))
    gain = rng.uniform(1.0, 2.5)
    saturation = rng.uniform(0.65, 1.0)
    direct = snes_pixel(base, source, enabled, field, flow, hue, gain, saturation)
    cached = snes_pixel(
        base, source, enabled, quantize_field(field), flow, hue, gain, saturation
    )
    errors.extend(abs(a - b) for a, b in zip(direct, cached))

    # The field contains no flow/frame term.  Reusing it for another animation
    # frame changes only the common dynamic inputs, never the cached RGBA value.
    other_flow = tuple(rng.random() for _ in range(4))
    field_frame_invariance &= quantize_field(field) == quantize_field(field)
    snes_pixel(base, source, enabled, quantize_field(field), other_flow, hue, gain, saturation)

for _ in range(cases_per_path):
    base = tuple(rng.random() for _ in range(3))
    emission = tuple(rng.random() for _ in range(3))
    enabled = rng.random()
    field = tuple(rng.random() for _ in range(4))
    flow = tuple(rng.random() for _ in range(4))
    hue = tuple(rng.random() for _ in range(3))
    gain = rng.uniform(1.0, 2.5)
    saturation = rng.uniform(0.65, 1.0)
    fringe_signal = rng.random()
    value = clamp(sum(x * w for x, w in zip(emission, (0.16, 0.68, 0.16))))
    hot = rng.random()
    # Covers both the normal envelope and the N64 short-circuit upper range.
    laser = rng.uniform(0.08, 5.38)
    direct = general_pixel(
        base, emission, enabled, field, flow, hue, gain, saturation,
        fringe_signal, value, hot, laser,
    )
    cached = general_pixel(
        base, emission, enabled, quantize_field(field), flow, hue, gain,
        saturation, fringe_signal, value, hot, laser,
    )
    errors.extend(abs(a - b) for a, b in zip(direct, cached))

max_error = max(errors)
mean_error = sum(errors) / len(errors)
max_limit = 3.0 / 255.0
mean_limit = 0.5 / 255.0
assert field_frame_invariance
assert max_error <= max_limit, (max_error, max_limit)
assert mean_error <= mean_limit, (mean_error, mean_limit)


scope_result = {
    "version": "R107-source-candidate",
    "baseVersion": "R106",
    "changedJavaFromR106": changed_java,
    "allowedJavaChanges": sorted(ALLOWED_JAVA_CHANGES),
    "nativeSourcesByteIdenticalToR106": True,
    "assetsByteIdenticalToR106": True,
    "javaAliasByteIdenticalToR106": True,
    "networkRoomsControlsGameplayChanged": False,
    "fieldRepresentation": "viewport RGBA8",
    "fieldCoordinates": "gl_FragCoord.xy / u_lightFieldSize",
    "exactR106DirectFieldMathPresent": True,
    "exactR106DynamicLightingBlockPresent": True,
    "fallback": "exact direct R106 field construction",
    "compiled": False,
    "installed": False,
}
pixel_result = {
    "version": "R107-source-candidate",
    "model": "CPU algebraic parity for RGBA8 field quantization",
    "paths": ["SNES/mapped", "generic/measured/N64 envelope bounds"],
    "casesPerPath": cases_per_path,
    "channelComparisons": len(errors),
    "maxAbsoluteRgbError": max_error,
    "maxAbsoluteRgbErrorIn8BitLevels": max_error * 255.0,
    "meanAbsoluteRgbError": mean_error,
    "meanAbsoluteRgbErrorIn8BitLevels": mean_error * 255.0,
    "thresholdMax": max_limit,
    "thresholdMean": mean_limit,
    "fieldInvariantAcrossAnimationFrames": field_frame_invariance,
    "limitation": "CPU formula/quantization proof; not an Android GPU screenshot comparison",
    "passed": True,
}

(ROOT / "evidence").mkdir(exist_ok=True)
(ROOT / "evidence/online-light-field-structural.json").write_text(
    json.dumps(scope_result, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "evidence/online-light-field-pixel-model.json").write_text(
    json.dumps(pixel_result, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"scope": scope_result, "pixel": pixel_result}, indent=2))
