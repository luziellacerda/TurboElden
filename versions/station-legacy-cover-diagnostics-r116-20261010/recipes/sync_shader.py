from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
GLSL = ROOT / "native/d0/premium-magazine-led-android.glsl"
HEADER = ROOT / "native/d0/magazine_shader.h"
JAVA = ROOT / "java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java"

shader = GLSL.read_text(encoding="utf-8").replace("\r\n", "\n")
if not shader.endswith("\n"):
    shader += "\n"

HEADER.write_text(
    'static const char magazineShaderSource[]=R"NEOMAG(' + shader + ')NEOMAG";\n',
    encoding="utf-8",
    newline="\n",
)

lines = [
    "package org.emulationstation.frontend.netplay;",
    "/** Identical shared carousel GLSL. */",
    "final class StationCoverLightingShader {",
    "    static final String SOURCE =",
]
shader_lines = shader.splitlines(keepends=True)
for index, line in enumerate(shader_lines):
    suffix = ";" if index == len(shader_lines) - 1 else " +"
    lines.append("        " + json.dumps(line, ensure_ascii=False) + suffix)
lines.append("}")
JAVA.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print(f"Synced {len(shader.encode('utf-8'))} shader bytes")
