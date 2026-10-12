"""One-instruction fallback: finish the Activity after native accepts quit."""
from pathlib import Path
import shutil
import sys

source, destination = map(Path, sys.argv[1:3])
assert not destination.exists()
shutil.copytree(source, destination)
target = destination / "org/emulationstation/frontend/netplay/StationRetroActivity.smali"
raw = target.read_text(encoding="utf-8")
start = raw.index(".method private requestHumanExit()V")
end = raw.index(".end method", start) + len(".end method")
method = raw[start:end]
before = """    if-eqz v0, :cond_1

    return-void

    :catch_0"""
after = """    if-eqz v0, :cond_1

    # Native quit is only a queued request. Complete the Android Activity exit
    # even when the emulation thread has already ended and cannot consume it.
    goto :cond_1

    :catch_0"""
assert method.count(before) == 1
updated = raw[:start] + method.replace(before, after) + raw[end:]
assert updated.count("goto :cond_1") == raw.count("goto :cond_1") + 1
target.write_text(updated, encoding="utf-8", newline="\n")
