"""Pinned, source-only N64 online Dynarec profile changes for R159 DEX35.

This module changes only the three classes that own CPU choice, launch profile,
and the host's synchronized CPU admission guard. Task lifecycle stays at R159.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


SESSION = Path("org/emulationstation/frontend/netplay/StationN64Bridge$Session.smali")
LAUNCH = Path("org/emulationstation/frontend/netplay/StationN64Launch.smali")
SERVER = Path("org/emulationstation/frontend/netplay/StationN64Server.smali")

BASE_SHA256 = {
    SESSION: "35a8341c5b9b8d90cf5b6bcbec26ff4ae950dc862105f3d722d08e1004d4f0d3",
    LAUNCH: "4790cf3dff9d3a9adb6ef5301acfad8dfdc188dca9d6f93280c3606cba768e8e",
    SERVER: "ea5d8c44a7fc9395e852a50f352ea49dc5b0806659992344c133548d8f317390",
}


def _replace(source: bytes, before: bytes, after: bytes, expected: int, label: str) -> bytes:
    actual = source.count(before)
    if actual != expected:
        raise ValueError(f"{label}: expected {expected} exact sites; found {actual}")
    return source.replace(before, after)


def patch(path: Path, source: bytes) -> bytes:
    expected = BASE_SHA256.get(path)
    if expected is None or hashlib.sha256(source).hexdigest() != expected:
        raise ValueError("Exact decoded R159 N64 class required: " + str(path))
    if path == SESSION:
        return _replace(source,
                        b'const-string v0, "r4300Emulator"\r\n\r\n    const-string v1, "1"',
                        b'const-string v0, "r4300Emulator"\r\n\r\n    const-string v1, "2"',
                        1, "Session CPU mode")
    if path == LAUNCH:
        return _replace(source, b"cpu=cached-interpreter", b"cpu=dynarec", 3,
                        "Pinned N64 launch options")
    if path == SERVER:
        # v8 is the method-wide constant one. Temporarily compare with two,
        # then restore it before entering the existing success path.
        before = (b"move-result v4\r\n\r\n    if-ne v4, v8, :cond_12\r\n\r\n"
                  b"    .line 62\r\n    monitor-enter p0")
        after = (b"move-result v4\r\n\r\n    const/4 v8, 0x2\r\n\r\n"
                 b"    if-ne v4, v8, :cond_12\r\n\r\n    const/4 v8, 0x1\r\n\r\n"
                 b"    .line 62\r\n    monitor-enter p0")
        return _replace(source, before, after, 1, "Host synchronized CPU guard")
    raise AssertionError(path)
