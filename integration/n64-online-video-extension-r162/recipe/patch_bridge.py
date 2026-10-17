"""Scoped R162 VideoExt patch for exact decoded R161 N64 owners.

The online activity selects the isolated AE bridge before CoreService creates
CoreInterface. Offline continues to use the original AE bridge. A native status
check fails startup if the online core did not accept its Android VideoExt.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


BRIDGE = "Lorg/emulationstation/frontend/netplay/StationN64Bridge;"
CORE = "Lpaulscode/android/mupen64plusae/jni/CoreInterface;"
AE_LIBRARY = "Lpaulscode/android/mupen64plusae/jni/AeBridgeLibrary;"
STATION = Path("org/emulationstation/frontend/netplay/StationN64Bridge.smali")
INTERFACE = Path("paulscode/android/mupen64plusae/jni/CoreInterface.smali")

# These are checked in addition to the R161 APK/DEX hashes in build_dex.py.
BASE_CLASS_SHA256 = {
    STATION: "686b94662c43ada06e7f527361d724ba2a0137e0f858c96ef3fdf4f8f2111a51",
    INTERFACE: "728cfd547224b43c87edbc14ac821f80cb2f1acfa7c076b5f7bc48ac4a415bad",
}


def once(text: str, before: str, after: str) -> str:
    count = text.count(before)
    if count != 1:
        raise ValueError(f"Expected one R161 anchor, found {count}: {before[:100]!r}")
    return text.replace(before, after, 1)


def method(text: str, signature: str, transform) -> str:
    pattern = re.compile(r"(?ms)^\.method[^\n]* " + re.escape(signature) + r"\n.*?^\.end method$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"Expected one R161 method {signature}; found {len(matches)}")
    match = matches[0]
    changed = transform(match.group(0))
    if changed == match.group(0):
        raise ValueError("R162 patch did not change " + signature)
    return text[:match.start()] + changed + text[match.end():]


def patch_station(text: str) -> str:
    core_pattern = re.compile(r"(?ms)^\.method public static coreName\(\)Ljava/lang/String;\n.*?^\.end method$")
    matches = list(core_pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError("Expected one R161 coreName")
    original = matches[0].group(0)
    if (original.count("mupen64plus-core") != 1 or
            original.count("station_mupen64plus_core") != 1 or
            original.count("->current:") != 1):
        raise ValueError("R161 owner selector changed")
    bridge = original.replace("coreName", "bridgeName", 1)
    bridge = bridge.replace('"mupen64plus-core"', '"ae-bridge"', 1)
    bridge = bridge.replace('"station_mupen64plus_core"', '"station_ae_bridge"', 1)
    status = f""".method public static videoOverrideReady()Z
    .locals 2

    sget-object v0, {BRIDGE}->current:Lorg/emulationstation/frontend/netplay/StationN64Bridge$Session;
    if-nez v0, :station_video_check
    const/4 v0, 0x1
    return v0

    :station_video_check
    :try_start_station_video
    const-string v0, "station_ae_bridge"
    invoke-static {{v0}}, Lcom/sun/jna/NativeLibrary;->getInstance(Ljava/lang/String;)Lcom/sun/jna/NativeLibrary;
    move-result-object v0
    const-string v1, "stationVideoOverrideReady"
    invoke-virtual {{v0, v1}}, Lcom/sun/jna/NativeLibrary;->getFunction(Ljava/lang/String;)Lcom/sun/jna/Function;
    move-result-object v0
    const/4 v1, 0x0
    new-array v1, v1, [Ljava/lang/Object;
    invoke-virtual {{v0, v1}}, Lcom/sun/jna/Function;->invokeInt([Ljava/lang/Object;)I
    move-result v0
    :try_end_station_video
    .catch Ljava/lang/Throwable; {{:try_start_station_video .. :try_end_station_video}} :station_video_error

    const/4 v1, 0x1
    if-ne v0, v1, :station_video_not_ready
    return v1

    :station_video_not_ready
    const/4 v0, 0x0
    return v0

    :station_video_error
    move-exception v0
    const/4 v0, 0x0
    return v0
.end method"""
    if "videoOverrideReady()Z" in text or "bridgeName()Ljava/lang/String;" in text:
        raise ValueError("R161 StationN64Bridge was already patched")
    return text[:matches[0].end()] + "\n\n" + bridge + "\n\n" + status + text[matches[0].end():]


def patch_interface(text: str) -> str:
    def static_init(body: str) -> str:
        if (body.count('const-string v0, "ae-bridge"') != 1 or
                body.count("Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V") != 1 or
                body.count("return-void") != 1 or
                body.count("invoke-") != 1):
            raise ValueError("R161 CoreInterface static initialization changed")
        return ".method static constructor <clinit>()V\n    .locals 0\n    return-void\n.end method"

    text = method(text, "<clinit>()V", static_init)

    def constructor(body: str) -> str:
        if re.search(r"\bv6\b", body):
            raise ValueError("R161 constructor uses v6")
        body = once(body, "    .locals 6", "    .locals 7")
        super_call = "    invoke-direct {p0}, Ljava/lang/Object;-><init>()V"
        selection = f"""{super_call}

    invoke-static {{}}, {BRIDGE}->bridgeName()Ljava/lang/String;
    move-result-object v6
    invoke-static {{v6}}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V"""
        body = once(body, super_call, selection)
        return once(body, '    const-string v1, "ae-bridge"', "    move-object v1, v6")

    text = method(text, "<init>()V", constructor)

    def startup(body: str) -> str:
        override = f"    invoke-interface {{p2}}, {AE_LIBRARY}->overrideAeVidExtFuncs()V"
        checked = f"""{override}

    if-nez p1, :station_video_override_done
    invoke-static {{}}, {BRIDGE}->videoOverrideReady()Z
    move-result p2
    if-nez p2, :station_video_override_done
    const/16 p1, 0xc
    return p1

    :station_video_override_done"""
        return once(body, override, checked)

    return method(text, "coreStartup(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I", startup)


def patch(path: Path, source: bytes) -> bytes:
    expected = BASE_CLASS_SHA256.get(path)
    if expected is None or hashlib.sha256(source).hexdigest() != expected:
        raise ValueError("Exact decoded R161 N64 class required: " + str(path))
    text = source.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    normalized = text.replace("\r\n", "\n")
    patched = patch_station(normalized) if path == STATION else patch_interface(normalized)
    return patched.replace("\n", newline).encode("utf-8")
