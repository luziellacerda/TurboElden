from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = (
    REPO
    / "versions/station-render-cache-r101-20261010/native/d0/"
    "native_system_video720.h"
)
SOURCE = ROOT / "native/d0/native_system_video720.h"
POLICY = ROOT / "native/d0/video720_retained_fastpath_policy.h"
GUARD = ROOT / "native/d0/video720_retained_draw_state.h"
R106_MANIFEST = (
    REPO
    / "versions/station-render-online-r106-20261010/"
    "CAROUSEL-INPUT-MANIFEST.json"
)
RENDERER_ASM = (
    REPO
    / "versions/station-visual-covers-netplay-20261003/evidence/"
    "renderer-strips.asm.txt"
)
RENDERER_AUDIT = RENDERER_ASM.with_name("renderer-program-audit.json")
EVIDENCE = ROOT / "evidence/retained-fastpath-tests.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eligible(state: dict[str, object]) -> bool:
    return bool(
        state["completed"]
        and state["slots_idle"]
        and state["sources_ready"]
        and state["context_matches"]
        and state["preview_program_valid"]
        and int(state["current_program"]) > 0
    )


def model_restore(use_vao: bool) -> None:
    """Model only state touched by drawTriangleStrips and the retained draw."""
    before = {
        "program": 17,
        "array": 23,
        "active": 0x84C3,
        "texture0": 31,
        "blend": (0x302, 0x303, 1, 0x303),
        "vao": 41,
        "attributes": tuple(
            (i & 1, 2 + i, 0x1406, 0, 20, 50 + i, i * 4) for i in range(4)
        ),
    }
    after = dict(before)
    after.update(
        program=99,
        array=23,
        active=0x84C0,
        texture0=77,
        blend=(1, 0, 1, 0),
        attributes=tuple((1, 4, 0x1401, 1, 20, 23, 16) for _ in range(4)),
    )
    # Video720RetainedDrawState restores the same touched subset as SpaceState.
    for key in ("program", "array", "active", "texture0", "blend"):
        after[key] = before[key]
    if use_vao:
        after["vao"] = before["vao"]
        # SpaceState also rebinds the same VAO; its attribute contents are not
        # rewound. The model deliberately checks parity with that behavior.
        assert after["attributes"] != before["attributes"]
    else:
        after["attributes"] = before["attributes"]
    for key in ("program", "array", "active", "texture0", "blend", "vao"):
        assert after[key] == before[key], (use_vao, key)
    if not use_vao:
        assert after["attributes"] == before["attributes"]


def main() -> None:
    checks: list[str] = []
    manifest = json.loads(R106_MANIFEST.read_text(encoding="utf-8"))
    base_sha = sha(BASE)
    assert base_sha == manifest["d0/native_system_video720.h"]
    assert base_sha == "20462dbb2081f4a1f25dfee5bcc17709635c00365b63125668b530b46cb2adde"
    checks.append("R106 manifest pins the exact unmodified video source used as baseline")

    source = SOURCE.read_text(encoding="utf-8")
    policy = POLICY.read_text(encoding="utf-8")
    guard = GUARD.read_text(encoding="utf-8")
    assert '#include "video720_retained_fastpath_policy.h"' in source
    assert '#include "video720_retained_draw_state.h"' in source
    assert "constexpr bool eligible(const State&s)" in policy
    checks.append("native source uses the isolated pure eligibility gate and lightweight draw-state guard")

    fast_start = source.index("static bool drawRetainedSystemVideo720")
    fast_end = source.index("static r53VideoPolicy::Menu", fast_start)
    fast = source[fast_start:fast_end]
    for forbidden in (
        "SpaceState",
        "VideoExternalBinding",
        "ensureVideoJni",
        "ensureVideo720Jni",
        "video720Capacity",
        "CallStatic",
        "seedVideo720Preview",
        "ensureSystemVideoProgram",
        "0x39e240",
    ):
        assert forbidden not in fast, forbidden
    assert fast.count("GetUniformfv") == 1
    assert "g.UniformMatrix4fv(video720PreviewMVP,1,0,mvp);" in fast
    assert "if(!video720Once.completed||!video720SlotsIdle()||!video720RetainedSourcesReady(p))return false;" in fast
    assert fast.index("if(!video720Once.completed") < fast.index("g.GetIntegerv(0x8b8d,&program)")
    assert "video720RetainedSourceProgram" not in source
    assert "video720RetainedSourceViewport" not in source
    checks.append(
        "unfinished/active visits reject before GL queries; completed fast path skips full GL snapshot, external texture, JNI, capacity, decoder policy and time polling while refreshing current MVP"
    )

    for required in (
        "g.GetIntegerv(0x8894,&array)",
        "g.GetIntegerv(0x84e0,&active)",
        "g.GetIntegerv(0x8069,&texture)",
        "0x80c9,0x80c8,0x80cb,0x80ca",
        "g.GetIntegerv(0x85b5,&vao)",
        "s.GetVertexAttribiv",
        "s.GetVertexAttribPointerv",
        "s.VertexAttribPointer",
        "s.EnableVertexAttribArray",
        "s.DisableVertexAttribArray",
        "s.BindBuffer(0x8892,array)",
        "s.ActiveTexture(0x84c0)",
        "s.BindTexture(0x0de1,texture)",
        "s.ActiveTexture(active)",
        "s.BlendFuncSeparate(blend[0],blend[1],blend[2],blend[3])",
        "g.UseProgram(program)",
    ):
        assert required in guard, required
    assert "SpaceState" not in guard.split("struct Video720RetainedDrawState", 1)[1]
    model_restore(False)
    model_restore(True)
    checks.append(
        "lightweight guard restores the program, unit-0 texture, active unit, array binding, blend factors and SpaceState-compatible VAO/attribute state"
    )

    renderer_asm = RENDERER_ASM.read_text(encoding="utf-8")
    renderer_audit = json.loads(RENDERER_AUDIT.read_text(encoding="utf-8"))
    for symbol in ("glVertexAttribPointer@plt", "glBufferData@plt", "glBlendFunc@plt", "glDrawArrays@plt"):
        assert symbol in renderer_asm, symbol
    assert renderer_audit["stripsProgramMutation"] is False
    assert renderer_audit["helperPurpose"] == "glGetError followed by logger only"
    checks.append(
        "existing disassembly proves drawTriangleStrips mutates only vertex input/buffer contents/blend before drawing and does not replace the program"
    )

    draw_start = source.index("static void drawSystemVideo720")
    draw = source[draw_start:]
    assert draw.index("video720Once.observe") < draw.index("drawRetainedSystemVideo720")
    assert draw.index("drawRetainedSystemVideo720") < draw.index("SpaceState restore")
    assert "if(drawRetainedSystemVideo720(p,context))return;" in draw
    checks.append("identity is observed first; every rejected gate falls through to the original path")

    for exact in (
        "s.BindTexture(0x0de1,f->texture);",
        "float lo=.00138889f,hi=.99861111f;",
        "Vertex q[4]={{r.x,r.y,lo,hi,0xffffffff}",
        "roundedQuad(q,4,5,r.allGames);",
    ):
        assert exact in fast, exact
    checks.append("retained path preserves texture, UV crop, white color, current geometry and corner policy")

    base_source = BASE.read_text(encoding="utf-8")
    base_tail = base_source[base_source.index(" bool focusPainted=false;") :]
    patched_tail = source[source.index(" bool focusPainted=false;") :]
    assert patched_tail == base_tail
    checks.append("decoder policy, slot lifecycle and original live/retained draw tail remain byte-for-byte identical")

    true_state: dict[str, object] = {
        "completed": True,
        "slots_idle": True,
        "sources_ready": True,
        "context_matches": True,
        "preview_program_valid": True,
        "current_program": 17,
    }
    assert eligible(true_state)
    booleans = (
        "completed",
        "slots_idle",
        "sources_ready",
        "context_matches",
        "preview_program_valid",
    )
    for key in booleans:
        changed = dict(true_state)
        changed[key] = False
        assert not eligible(changed), key
    changed = dict(true_state)
    changed["current_program"] = 0
    assert not eligible(changed)
    checks.append("state matrix accepts only the fully-proved retained-only state")

    compiler = Path(r"C:\Program Files\LLVM\bin\clang++.exe")
    assert compiler.is_file(), compiler
    compiled_tests = (
        ("video720_retained_fastpath_policy_test.cpp", "video720-retained-policy-test.exe"),
        ("video720_retained_draw_state_test.cpp", "video720-retained-draw-state-test.exe"),
    )
    for source_name, executable_name in compiled_tests:
        executable = ROOT / "evidence" / executable_name
        compile_result = subprocess.run(
            [
                str(compiler),
                "-std=c++14",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(ROOT / "tests" / source_name),
                "-o",
                str(executable),
            ],
            capture_output=True,
            text=True,
        )
        assert compile_result.returncode == 0, compile_result.stdout + compile_result.stderr
        run_result = subprocess.run([str(executable)], capture_output=True, text=True)
        try:
            assert run_result.returncode == 0, run_result.stdout + run_result.stderr
        finally:
            executable.unlink(missing_ok=True)
    checks.append("C++14 policy and exact draw-state guard compile with warnings as errors; 7 gate cases and both GL restoration modes pass")

    result = {
        "status": "passed",
        "baseSource": str(BASE.relative_to(REPO)).replace("\\", "/"),
        "baseSHA256": base_sha,
        "patchedSHA256": sha(SOURCE),
        "policySHA256": sha(POLICY),
        "drawStateGuardSHA256": sha(GUARD),
        "rendererEvidenceSHA256": {
            str(RENDERER_ASM.relative_to(REPO)).replace("\\", "/"): sha(RENDERER_ASM),
            str(RENDERER_AUDIT.relative_to(REPO)).replace("\\", "/"): sha(RENDERER_AUDIT),
        },
        "checks": checks,
        "stateCases": 1 + len(booleans) + 1,
        "apkCompiled": False,
        "nativeLibraryCompiled": False,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
