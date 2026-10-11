from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "java" / "netplay-src" / "org" / "emulationstation" / "frontend" / "netplay"


def require(text: str, value: str, label: str) -> None:
    if value not in text:
        raise AssertionError(f"missing {label}: {value}")


def forbid(text: str, value: str, label: str) -> None:
    if value in text:
        raise AssertionError(f"forbidden {label}: {value}")


def structural_checks() -> None:
    hyperspace = (JAVA / "StationHyperspaceView.java").read_text(encoding="utf-8")
    lottie = (JAVA / "StationLottieIllustration.java").read_text(encoding="utf-8")

    for value, label in (
        ("extends View", "normal static view"),
        ("background=renderBackground(renderWidth,renderHeight)", "one-time size rasterization"),
        ("Static PSP-style waves", "static PSP visual"),
        ("void setResumed(boolean value){}", "compatible no-op lifecycle API"),
        ("StationHyperspaceState.renderWidth", "bounded render size"),
    ):
        require(hyperspace, value, label)
    for value, label in (
        ("Handler", "background handler"),
        ("Thread", "background thread"),
        ("Runnable", "background runnable"),
        ("SystemClock", "background clock"),
        ("ValueAnimator", "background animator"),
        ("postDelayed", "background delayed loop"),
        ("postAtTime", "background timed loop"),
        ("invalidate()", "background invalidation loop"),
        ("TextureView", "background texture producer"),
        ("space-nebula", "old animated-space asset"),
    ):
        forbid(hyperspace, value, label)

    for value, label in (
        ("setRepeatCount(AnimatedImageDrawable.REPEAT_INFINITE)", "visible robot loop"),
        ("decoder.setTargetSize", "decode at display size"),
        ("fallbackPlayback.beginLoad()", "terminal decode gate"),
        ("UNAVAILABLE.contains(asset)", "process negative cache"),
        ("ANIMATOR_DURATION_SCALE", "animation-scale observer"),
    ):
        require(lottie, value, label)
    forbid(lottie, "postDelayed", "native robot polling loop")


def state_probe() -> None:
    javac = shutil.which("javac")
    java = shutil.which("java")
    if not javac or not java:
        raise RuntimeError("JDK is required for the deterministic state probe")
    sources = [
        JAVA / "StationHyperspaceState.java",
        ROOT / "recipes" / "StationAmbientStateProbe.java",
    ]
    with tempfile.TemporaryDirectory(prefix="station-ambient-") as directory:
        subprocess.run([javac, "-encoding", "UTF-8", "-d", directory, *map(str, sources)], check=True)
        subprocess.run(
            [java, "-cp", directory, "org.emulationstation.frontend.netplay.StationAmbientStateProbe"],
            check=True,
        )


if __name__ == "__main__":
    structural_checks()
    state_probe()
    print("Online ambient patch checks: PASS")
