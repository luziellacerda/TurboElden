"""Read-only binary proof for the preserved native strip renderer.

The APK and extracted ELF stay private. The public receipt contains hashes,
function boundaries and aggregated call names only; it contains no binary data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import subprocess
import zipfile
from datetime import datetime, timezone


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--objdump", type=Path, default=Path(r"E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\llvm-objdump.exe"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    with zipfile.ZipFile(args.apk) as archive:
        data = archive.read("lib/arm64-v8a/libmain.so")
    assert sha(data) == "62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6"
    assert data[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", data, 18)[0] == 183
    shoff = struct.unpack_from("<Q", data, 40)[0]
    shsize, shnum = struct.unpack_from("<HH", data, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", data, shoff + i * shsize) for i in range(shnum)]

    def code(start, length):
        for section in sections:
            if section[1] != 8 and section[3] <= start and start + length <= section[3] + section[5]:
                offset = section[4] + start - section[3]
                return data[offset:offset + length]
        raise AssertionError("No mapped section")

    args.work.mkdir(parents=True, exist_ok=True)
    private_elf = args.work / "libmain-reference-private.so"
    private_elf.write_bytes(data)

    def disassemble(start, stop):
        result = subprocess.run([str(args.objdump), "-d", f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(private_elf)], capture_output=True, text=True, encoding="utf-8", check=True)
        return result.stdout

    draw = disassemble(0x2e5470, 0x2e55b0)
    helper = disassemble(0x2e4de0, 0x2e4ef4)
    setter = disassemble(0x2e55b0, 0x2e56d8)
    symbol = "_ZN8Renderer18drawTriangleStripsEPKNS_6VertexEjNS_5Blend6FactorES4_"
    assert f"00000000002e5470 <{symbol}>:" in draw
    calls = re.findall(r"\bbl\s+0x([0-9a-f]+)\s+<([^>]+)>", draw)
    external = [name for _, name in calls if name.endswith("@plt")]
    assert external == ["glVertexAttribPointer@plt"] * 3 + ["glBufferData@plt", "glBlendFunc@plt", "glDrawArrays@plt"]
    assert all(int(target, 16) == 0x2e4de0 for target, name in calls if not name.endswith("@plt"))
    assert re.search(r"2e55ac:.*\bb\s+0x2e4de0", draw)
    assert not re.search(r"\bblr?\s+x\d", draw + helper)
    assert "glUseProgram" not in draw + helper and "glUniform" not in draw + helper
    helper_gl = re.findall(r"\bbl\s+0x[0-9a-f]+\s+<(gl[^>]+)>", helper)
    assert helper_gl == ["glGetError@plt"]
    assert "glUniformMatrix4fv@plt" in setter
    assert b"u_mvp\0" in data and b"gl_Position = u_mvp * vec4(a_pos.xy, 0.0, 1.0);" in data
    receipt = {
        "version": "R123", "status": "PASS", "verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
        "source": "Preserved R122 APK lib/arm64-v8a/libmain.so", "elfSha256": sha(data), "elfBytes": len(data),
        "drawStrip": {"address": "0x2e5470", "bytes": 320, "symbol": symbol, "codeSha256": sha(code(0x2e5470, 320)), "directExternalCalls": external, "internalErrorCheckAddress": "0x2e4de0", "indirectCalls": 0},
        "errorCheck": {"address": "0x2e4de0", "bytes": 276, "codeSha256": sha(code(0x2e4de0, 276)), "directGlCalls": helper_gl, "changesGlProgramOrUniform": False},
        "matrixSetters": {"address": "0x2e55b0", "bytes": 296, "codeSha256": sha(code(0x2e55b0, 296)), "uniformWriteObservedOutsideStrip": True},
        "drawChangesProgram": False, "drawChangesMvp": False, "nativeMvpUniform": "u_mvp", "nativeVertexShaderMvpObserved": True,
        "objdumpSha256": sha(args.objdump.read_bytes()), "recipeSha256": sha(Path(__file__).read_bytes()),
        "limits": ["Static analysis of the exact preserved ELF; not execution on a GPU or telephone.", "Error-check helper has logging/unwind branches; its only direct GL call is glGetError.", "This proves the scope of Renderer::drawTriangleStrips, not arbitrary external shaders or drivers.", "Binary and disassembly files remain private and are not included in Git."]
    }
    (root / "evidence/renderer-mvp-r123.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: exact ELF, strip and error helper preserve program/MVP; setters are outside strip.")


if __name__ == "__main__":
    main()
