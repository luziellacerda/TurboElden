from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "java/netplay-src/org/emulationstation/frontend/netplay/StationLottieIllustration.java"
STATE = ROOT / "java/netplay-src/org/emulationstation/frontend/netplay/StationSinglePassAnimationState.java"
PROBE = ROOT / "recipes/StationSinglePassAnimationStateProbe.java"

source = JAVA.read_text(encoding="utf-8")
checks = {
    "terminal per-view load gate": "!fallbackPlayback.beginLoad()" in source,
    "process negative cache": "UNAVAILABLE.contains(asset)" in source and "UNAVAILABLE.add(asset)" in source,
    "GIF fallback after WebP failure": "if(next==null)" in source and 'asset+".gif"' in source,
    "native AnimatedImageDrawable loop": "setRepeatCount(AnimatedImageDrawable.REPEAT_INFINITE)" in source,
    "native lifecycle start": "if(play&&!animation.isRunning())animation.start()" in source,
    "native lifecycle stop": "else if(!play&&animation.isRunning())animation.stop()" in source,
    "detach stops native loop": "if(drawable instanceof Animatable)((Animatable)drawable).stop()" in source,
    "fallback renders only while running": "if(fallbackPlayback.shouldContinue())postInvalidateDelayed(34)" in source,
    "decode worker expires": "new ThreadPoolExecutor(" in source and "0,1,1L,TimeUnit.SECONDS" in source,
    "failure logs only on first process failure": "if(UNAVAILABLE.add(asset))android.util.Log.w" in source,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("structural failures: " + ", ".join(failed))

with tempfile.TemporaryDirectory(prefix="station-illustration-state-") as out:
    subprocess.run(["javac", "-d", out, str(STATE), str(PROBE)], check=True)
    result = subprocess.run(
        ["java", "-cp", out, "org.emulationstation.frontend.netplay.StationSinglePassAnimationStateProbe"],
        check=True, capture_output=True, text=True,
    )
    print(result.stdout.strip())
print(f"Station illustration lifecycle: {len(checks)} structural checks passed")
