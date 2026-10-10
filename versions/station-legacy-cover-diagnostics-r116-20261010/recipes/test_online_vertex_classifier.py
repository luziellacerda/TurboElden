"""Structural proof for the R106 online-cover vertex classifier.

This test performs no APK build and no device operation. It proves that the
only source delta from R105 is StationOnlineCoverView, while the shared shader
and every native carousel source remain byte-identical.
"""

from pathlib import Path
import ast
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]
R105 = ROOT.parent / "station-render-classifier-r105-20261010"
ONLINE = (
    "netplay-src/org/emulationstation/frontend/netplay/"
    "StationOnlineCoverView.java"
)
LIGHTING = (
    "netplay-src/org/emulationstation/frontend/netplay/"
    "StationCoverLightingShader.java"
)
LONG_JAVA = (
    "dependency-src/org/emulationstation/frontend/relay/ws/extensions/"
    "permessage_deflate/PerMessageDeflateExtension.java"
)
MACRO = "MAGAZINE_VERTEX_CLASSIFIER"
BASE_SHA = "b27435ba4011337c1ae2cc62079efc2d37b9028b01f4268a4a1314b50644c00e"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def files(root):
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


r105_manifest = json.loads(
    (R105 / "JAVA-SOURCE-MANIFEST.json").read_text(encoding="utf-8")
)
current = {}
for name in r105_manifest:
    path = ROOT / "java" / name
    if name == LONG_JAVA:
        path = ROOT / "java-alias/PerMessageDeflateExtension.java"
    current[name] = sha(path)

changed = sorted(
    name for name, digest in current.items() if digest != r105_manifest[name]
)
assert changed == [ONLINE]
assert json.loads(
    (ROOT / "JAVA-SOURCE-MANIFEST.json").read_text(encoding="utf-8")
) == current

# Canonical shader, generated copies, native selector and all other carousel
# sources are frozen byte-for-byte at R105.
assert files(ROOT / "native") == files(R105 / "native")
assert (ROOT / "native/d0/premium-magazine-led-android.glsl").read_bytes() == (
    R105 / "native/d0/premium-magazine-led-android.glsl"
).read_bytes()
assert (ROOT / "native/d0/magazine_shader.h").read_bytes() == (
    R105 / "native/d0/magazine_shader.h"
).read_bytes()
assert (ROOT / "java" / LIGHTING).read_bytes() == (
    R105 / "java" / LIGHTING
).read_bytes()

online = (ROOT / "java" / ONLINE).read_text(encoding="utf-8")
query = online.index("GLES20.glGetIntegerv(0x8b4c,vertexTextureUnits,0)")
gate = online.index("if(vertexTextureUnits[0]>0)", query)
optimized = online.index("program=link(true)", gate)
fallback = online.index("if(program==0){program=link(false)", optimized)
ready = online.index("GLES20.glUseProgram(program)", fallback)
assert query < gate < optimized < fallback < ready

# Both stages receive the feature macro only through link(true); link(false)
# builds the exact R104-compatible fragment classifier from the same source.
assert 'String feature=optimized?"#define ' + MACRO + '\\n":"";' in online
assert '"#version 100\\n"+feature+"#define VERTEX\\n"' in online
assert '"#version 100\\n"+feature+"#define FRAGMENT\\n"' in online
assert "int link(boolean optimized)" in online
assert "if(v!=0)GLES20.glDeleteShader(v)" in online
assert "if(f!=0)GLES20.glDeleteShader(f)" in online
assert "if(candidate!=0)GLES20.glDeleteProgram(candidate)" in online
assert "GLES20.glDeleteShader(shader);throw new IllegalStateException(log)" in online
assert 'vertexClassifier?"vertex classifier active":"fragment classifier fallback active"' in online
assert online.count("program=link(true)") == 1
assert online.count("program=link(false)") == 1
assert online.count(MACRO) == 1

build = (ROOT / "build.py").read_text(encoding="utf-8")
ast.parse(build)
assert "TurboStations-Premium-R105-20261010.apk" in build
assert f'BASE_SHA = "{BASE_SHA}"' in build
assert 'payloads = {"classes35.dex": rooms_dex}' in build
assert 'expected_changes = ["classes35.dex"]' in build
assert 'assert files(ROOT / "native") == r105_native' in build
assert 'assert changed_java_from_r105 == [ONLINE_VIEW]' in build
assert 'assert changed_java_from_r102 == [LIGHTING_JAVA, ONLINE_VIEW]' in build
assert 'assert changed_java_from_r103 == [LIGHTING_JAVA, ONLINE_VIEW]' in build
assert '"carouselBinaryByteIdenticalToR105": True' in build

result = {
    "version": "R106",
    "baseVersion": "R105",
    "changedJavaFromR105": changed,
    "nativeSourcesByteIdenticalToR105": True,
    "sharedShaderByteIdenticalToR105": True,
    "capabilityGate": "GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS > 0",
    "optimizedVariant": MACRO,
    "fallback": "R104-equivalent fragment classifier",
    "partialCompileObjectsCleaned": True,
    "expectedAPKChanges": ["classes35.dex"],
    "networkRoomsControlsGameplayChanged": False,
    "compiled": False,
    "installed": False,
}
(ROOT / "evidence").mkdir(exist_ok=True)
(ROOT / "evidence/online-vertex-classifier-structural.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, indent=2))
