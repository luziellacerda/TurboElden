#!/usr/bin/env python3
"""Copy and patch exact integrated Dolphin partitions, leaving the donors intact.

Reads only classes10/classes12 from the base APK. Does not rebuild resources,
alter offline native libraries, build/sign an APK or register a server engine.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import zipfile

SELECTOR = "Lorg/emulationstation/frontend/netplay/StationDolphinSelector;"
SESSION = "Lorg/emulationstation/frontend/netplay/StationDolphinSession;"
DOLPHIN = "Lorg/dolphinemu/dolphinemu/"
EXPECTED_DEX = {
    "classes10.dex": "74492a53dee0db0990bf761ed011ad0d7f9ec597e95c83913a5e48b834b15d50",
    "classes12.dex": "e38e2406aa7a5e05e20a08b09c47fecb943cd3a88a4fbbd6df541721a3096884",
}
EXPECTED_TREES = {
    "core": (4991, "9d6ae3df381559141c44061dcacbc713e66893e7ab9389d4fe7fe35174299834"),
    "bootstrap": (5, "37988f0824ae8a0ffb90fd8c492aa1490f54bf9918777dc39301b4f69fc7f245"),
}
EXPECTED_FILES = {
    "core": {
        "org/dolphinemu/dolphinemu/DolphinApplication.smali": "c4f0ea69fb7228fa5b3d366765280fc687d8520c620ec60d3bcbb6d5d10a512b",
        "org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali": "7be37119ba40b5074ddd4c3c332c61b5765b35d64bb64d742551b50d88dd4608",
        "org/dolphinemu/dolphinemu/activities/EmulationActivity.smali": "bb53abdd5e998b1eb0485954b3cc23a3414e0c333212768f6b8f70dc27fd59da",
    },
    "bootstrap": {
        "org/emulationstation/frontend/DolphinBootstrap.smali": "8a5d01730c2584190a0a0f969fdfce154f4b7b4e66a066308a4409f0eafb7cbb",
        "org/emulationstation/frontend/DolphinEntryActivity.smali": "69c53207ed5ce9933dd681c6303daedbcda58f42a365336e084590a8292476b6",
    },
}

def fs(path: Path) -> Path:
    """Preserve long generated Kotlin names on Windows without changing paths."""
    value = str(path.resolve())
    return Path("\\\\?\\" + value) if os.name == "nt" and not value.startswith("\\\\?\\") else Path(value)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def tree(root: Path):
    files = sorted(root.rglob("*.smali"), key=lambda p: p.relative_to(root).as_posix())
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode() + b"\0" + hashlib.sha256(fs(path).read_bytes()).digest())
    return len(files), digest.hexdigest()

def once(text: str, anchor: str, replacement: str) -> str:
    if text.count(anchor) != 1:
        raise ValueError(f"Expected one anchor, found {text.count(anchor)}: {anchor[:120]}")
    return text.replace(anchor, replacement, 1)

def method(text: str, signature: str, transform) -> str:
    pattern = re.compile(r"(?ms)^\.method[^\n]* " + re.escape(signature) + r"\n.*?^\.end method$")
    found = list(pattern.finditer(text))
    if len(found) != 1:
        raise ValueError(f"Expected one method {signature}, got {len(found)}")
    match = found[0]; changed = transform(match.group())
    if changed == match.group():
        raise ValueError(f"Method was not changed: {signature}")
    return text[:match.start()] + changed + text[match.end():]

def prepend(body: str, code: str, locals_needed: int = 1) -> str:
    match = re.search(r"(?m)^    \.locals (\d+)\n", body)
    if match is None:
        raise ValueError("Missing locals directive")
    return body[:match.start()] + f"    .locals {max(locals_needed, int(match.group(1)))}\n\n" + code + "\n" + body[match.end():]

def consume(body: str, hook: str, signature: str, arguments: str, label: str) -> str:
    return prepend(body, f"""    invoke-static {{{arguments}}}, {SESSION}->{hook}{signature}
    move-result v0
    if-eqz v0, :{label}
    return-void
    :{label}""")

def close_guard(body: str, label: str) -> str:
    return prepend(body, f"""    invoke-static {{p0}}, {SESSION}->allowClose(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :{label}
    return-void
    :{label}""")

def patch_application(text: str) -> str:
    return method(text, "onCreate()V", lambda body: once(body, '    const-string v0, "dolp"',
        f"    invoke-static {{p0}}, {SELECTOR}->libraryName(Landroid/content/Context;)Ljava/lang/String;\n    move-result-object v0"))

def patch_netplay(text: str) -> str:
    # Native boot pointer must remain available for the real EmulationFragment.
    anchor = f"    iput-wide p2, p0, {DOLPHIN}features/netplay/NetplaySession;->bootSessionDataPointer:J"
    def boot(body):
        body = prepend(body, "", 1)
        return once(body, anchor, anchor + f"""

    invoke-static {{p0, p1}}, {SESSION}->onBootGame(Ljava/lang/Object;Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :station_dolphin_original_boot
    return-void
    :station_dolphin_original_boot""")
    text = method(text, "onBootGame(Ljava/lang/String;J)V", boot)
    for signature, hook, descriptor, arguments, label in [
        ("onStopGame()V", "onNativeStop", "(Ljava/lang/Object;)Z", "p0", "station_dolphin_original_stop"),
        ("onConnectionLost()V", "onConnectionLost", "(Ljava/lang/Object;)Z", "p0", "station_dolphin_original_lost"),
        ("onConnectionError(Ljava/lang/String;)V", "onConnectionError", "(Ljava/lang/Object;Ljava/lang/String;)Z", "p0, p1", "station_dolphin_original_error"),
    ]:
        text = method(text, signature, lambda body, h=hook, d=descriptor, a=arguments, l=label: consume(body, h, d, a, l))
    # finalize() invokes releaseNativeResources directly, bypassing closeBlocking.
    for signature, label in [("closeBlocking()V", "station_dolphin_original_close"),
                             ("releaseNativeResources()V", "station_dolphin_original_release")]:
        text = method(text, signature, lambda body, l=label: close_guard(body, l))
    return text

def patch_game(text: str) -> str:
    for signature, hook in [("onCreate(Landroid/os/Bundle;)V", "onGameCreate"),
                            ("onResume()V", "onGameResume"), ("onDestroy()V", "onGameDestroy")]:
        text = method(text, signature, lambda body, h=hook: prepend(body,
            f"    invoke-static/range {{p0 .. p0}}, {SESSION}->{h}(Landroid/app/Activity;)V"))
    if re.search(r"(?m)^\.method[^\n]* onPause\(\)V$", text):
        raise ValueError("Unexpected inherited onPause implementation")
    text += f"""

.method protected onPause()V
    .locals 0

    invoke-static {{p0}}, {SESSION}->onGamePause(Landroid/app/Activity;)V
    invoke-super {{p0}}, Ltdolphin/appcompat/app/AppCompatActivity;->onPause()V
    return-void
.end method
"""
    text = method(text, "handleMenuAction(I)V", lambda body: prepend(body, f"""    invoke-static/range {{p0 .. p1}}, {SESSION}->allowMenuAction(Landroid/app/Activity;I)Z
    move-result v0
    if-nez v0, :station_dolphin_original_menu
    return-void
    :station_dolphin_original_menu
    invoke-static/range {{p0 .. p1}}, {SESSION}->onMenuAction(Landroid/app/Activity;I)V"""))
    # Long BACK is another explicit human exit in the official Activity. This
    # branch is after KEYCODE_BACK validation and before p0 is overwritten.
    long_back = f"    iget-object p0, p0, {DOLPHIN}activities/EmulationActivity;->emulationFragment:{DOLPHIN}fragments/EmulationFragment;"
    text = method(text, "onKeyLongPress(ILandroid/view/KeyEvent;)Z", lambda body: once(body, long_back, f"""    const/16 v0, 0x16
    invoke-static {{p0, v0}}, {SESSION}->onMenuAction(Landroid/app/Activity;I)V

{long_back}"""))
    # Keep all original Bundle entries, omitting only the native temporary save.
    anchor = f"    invoke-static {{v0}}, {DOLPHIN}NativeLibrary;->SaveStateAs(Ljava/lang/String;)V"
    text = method(text, "onSaveInstanceState(Landroid/os/Bundle;)V", lambda body: once(body, anchor, f"""    invoke-static {{p0}}, {SESSION}->allowSaveState(Landroid/app/Activity;)Z
    move-result v1
    if-eqz v1, :station_dolphin_skip_temporary_state
{anchor}
    :station_dolphin_skip_temporary_state"""))
    return text

def patch_bootstrap(text: str) -> str:
    for signature, kind, label in [
        ("userDirectory(Landroid/content/Context;)Ljava/io/File;", "User", "station_dolphin_original_user"),
        ("internalDirectory(Landroid/content/Context;)Ljava/io/File;", "Internal", "station_dolphin_original_internal"),
        ("cacheDirectory(Landroid/content/Context;)Ljava/io/File;", "Cache", "station_dolphin_original_cache"),
    ]:
        text = method(text, signature, lambda body, k=kind, l=label: prepend(body, f"""    const-string v0, "{k}"
    invoke-static {{p0, v0}}, {SELECTOR}->directory(Landroid/content/Context;Ljava/lang/String;)Ljava/io/File;
    move-result-object v0
    if-eqz v0, :{l}
    return-object v0
    :{l}"""))
    text = method(text, "migrateLegacySaves(Landroid/content/Context;)V", lambda body: prepend(body, f"""    invoke-static {{p0}}, {SELECTOR}->skipLegacySaves(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :station_dolphin_original_migrate
    return-void
    :station_dolphin_original_migrate"""))
    return text

def patch_entry(text: str) -> str:
    # Android must receive super.onCreate even when a normal launch is rejected.
    anchor = "    invoke-super {p0, p1}, Ltdolphin/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V"
    return method(text, "onCreate(Landroid/os/Bundle;)V", lambda body: once(body, anchor, anchor + f"""

    invoke-static {{p0}}, {SELECTOR}->rejectOfflineLaunch(Landroid/app/Activity;)Z
    move-result v0
    if-eqz v0, :station_dolphin_original_entry
    return-void
    :station_dolphin_original_entry"""))

PATCHERS = {"DolphinApplication.smali": patch_application, "NetplaySession.smali": patch_netplay,
            "EmulationActivity.smali": patch_game, "DolphinBootstrap.smali": patch_bootstrap,
            "DolphinEntryActivity.smali": patch_entry}

def plan(sources: dict[str, Path], base_apk: Path):
    with zipfile.ZipFile(base_apk) as apk:
        for entry, expected in EXPECTED_DEX.items():
            info = apk.getinfo(entry)
            if info.file_size > 16 * 1024 * 1024 or sha(apk.read(entry)) != expected:
                raise ValueError(f"Unexpected base APK partition: {entry}")
    changes = []; patched = {}
    for group, source in sources.items():
        if tree(source) != EXPECTED_TREES[group]:
            raise ValueError(f"Complete donor smali tree differs: {group}")
        for relative, expected in EXPECTED_FILES[group].items():
            data = fs(source / relative).read_bytes()
            if sha(data) != expected:
                raise ValueError(f"Unexpected donor file: {relative}")
            decoded = data.decode("utf-8")
            if SELECTOR in decoded or SESSION in decoded:
                raise ValueError(f"Already patched donor: {relative}")
            newline = "\r\n" if "\r\n" in decoded else "\n"
            result = PATCHERS[Path(relative).name](decoded.replace("\r\n", "\n"))
            encoded = result.replace("\n", newline).encode("utf-8")
            patched[(group, relative)] = encoded
            changes.append({"partition": group, "path": relative, "sourceSha256": expected, "patchedSha256": sha(encoded)})
    return changes, patched

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-apk", type=Path, required=True)
    parser.add_argument("--input-core-smali", type=Path, required=True)
    parser.add_argument("--input-bootstrap-smali", type=Path, required=True)
    parser.add_argument("--output-core-smali", type=Path, required=True)
    parser.add_argument("--output-bootstrap-smali", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    sources = {"core": args.input_core_smali.resolve(strict=True), "bootstrap": args.input_bootstrap_smali.resolve(strict=True)}
    targets = {"core": args.output_core_smali.resolve(), "bootstrap": args.output_bootstrap_smali.resolve()}
    for target in targets.values():
        if target.exists():
            raise FileExistsError(target)
        for source in sources.values():
            if source == target or source in target.parents or target in source.parents:
                raise ValueError("In-place or nested patches are forbidden")
    if targets["core"] == targets["bootstrap"] or targets["core"] in targets["bootstrap"].parents or targets["bootstrap"] in targets["core"].parents:
        raise ValueError("Output trees must be disjoint")
    changes, patched = plan(sources, args.base_apk)
    # Complete validation and transforms precede all mutations.
    for group, target in targets.items():
        shutil.copytree(fs(sources[group]), fs(target))
    for (group, relative), data in patched.items():
        fs(targets[group] / relative).write_bytes(data)
    receipt = {"schema": "station-dolphin-smali-hooks-v1", "basePartitions": EXPECTED_DEX,
               "sourceTrees": {k: {"files": n, "sha256": h} for k, (n, h) in EXPECTED_TREES.items()},
               "modifiedFiles": changes, "sourceRoots": {k: str(v) for k, v in sources.items()},
               "outputRoots": {k: str(v) for k, v in targets.items()}, "donorModified": False,
               "offlineNativeLibrariesModified": False, "dexAssembled": False,
               "apkBuilt": False, "physicalGameplayValidated": False}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"modifiedFiles": len(changes), "receipt": str(args.receipt)}))

if __name__ == "__main__":
    main()
