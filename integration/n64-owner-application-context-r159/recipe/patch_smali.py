"""Patch the single N64 owner handoff in the pinned R158 DEX35 decode.

The caller decodes classes35.dex and copies its tree to an isolated build
directory. This recipe changes only StationN64Bridge.propagate there.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re


BRIDGE = Path("org/emulationstation/frontend/netplay/StationN64Bridge.smali")
ORIGINAL_SHA256 = "c31cce96b483616dd05efb7a48c066774e57dbfb78aa757e8c149cf7e2b97fe6"
SIGNATURE = ".method public static propagate(Landroid/content/Context;Landroid/content/Intent;)V"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patch(raw: bytes) -> bytes:
    if sha(raw) != ORIGINAL_SHA256:
        raise ValueError("StationN64Bridge.smali is not the pinned R158 class")
    if b"\r\n" not in raw or raw.count(b"\r\n") != raw.count(b"\n"):
        raise ValueError("Unexpected donor smali line endings")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    match = re.search(r"(?ms)^" + re.escape(SIGNATURE) + r"\n.*?^\.end method$", text)
    if match is None or len(re.findall(r"(?m)^" + re.escape(SIGNATURE) + r"$", text)) != 1:
        raise ValueError("Expected one N64 propagate method")
    before = """.method public static propagate(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 1

    .line 31
    sget-object v0, Lorg/emulationstation/frontend/netplay/StationN64Bridge;->current:Lorg/emulationstation/frontend/netplay/StationN64Bridge$Session;

    if-eqz v0, :cond_0

    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationN64Bridge;->isStationContext(Landroid/content/Context;)Z

    move-result p0

    if-eqz p0, :cond_0
"""
    after = """.method public static propagate(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 3

    .line 31
    sget-object v0, Lorg/emulationstation/frontend/netplay/StationN64Bridge;->current:Lorg/emulationstation/frontend/netplay/StationN64Bridge$Session;

    if-eqz v0, :cond_0

    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationN64Bridge;->isStationContext(Landroid/content/Context;)Z

    move-result v1

    if-nez v1, :station_n64_verified_context

    iget-boolean v1, v0, Lorg/emulationstation/frontend/netplay/StationN64Bridge$Session;->closed:Z
    if-nez v1, :cond_0

    iget-object v1, v0, Lorg/emulationstation/frontend/netplay/StationN64Bridge$Session;->activity:Landroid/app/Activity;
    invoke-virtual {v1}, Landroid/app/Activity;->getApplicationContext()Landroid/content/Context;
    move-result-object v1
    if-ne p0, v1, :cond_0

    invoke-virtual {p1}, Landroid/content/Intent;->getComponent()Landroid/content/ComponentName;
    move-result-object v1
    if-eqz v1, :cond_0

    invoke-virtual {v1}, Landroid/content/ComponentName;->getClassName()Ljava/lang/String;
    move-result-object v2
    const-string p0, "paulscode.android.mupen64plusae.jni.CoreService"
    invoke-virtual {p0, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :cond_0

    invoke-virtual {v1}, Landroid/content/ComponentName;->getPackageName()Ljava/lang/String;
    move-result-object v1
    iget-object v2, v0, Lorg/emulationstation/frontend/netplay/StationN64Bridge$Session;->activity:Landroid/app/Activity;
    invoke-virtual {v2}, Landroid/app/Activity;->getPackageName()Ljava/lang/String;
    move-result-object v2
    invoke-virtual {v2, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :cond_0

    :station_n64_verified_context
"""
    method = match.group(0)
    if method.count(before) != 1:
        raise ValueError("R158 owner gate differs from the expected method")
    changed = method.replace(before, after, 1)
    if changed.count("->onServiceStart") or changed.count("->isStationContext") != 1:
        raise ValueError("Unexpected N64 owner method structure")
    result = (text[: match.start()] + changed + text[match.end() :]).replace("\n", "\r\n").encode("utf-8")
    if result == raw or result.count(b"station_n64_verified_context") != 2:
        raise ValueError("N64 owner gate not changed exactly once")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decoded-root", type=Path, required=True)
    args = parser.parse_args()
    path = args.decoded_root / BRIDGE
    original = path.read_bytes()
    updated = patch(original)
    path.write_bytes(updated)
    print("bridgeSha256=" + sha(updated))


if __name__ == "__main__":
    main()
