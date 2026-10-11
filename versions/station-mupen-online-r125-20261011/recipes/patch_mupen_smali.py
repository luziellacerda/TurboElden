"""Copy and patch the exact integrated AE DEX source; never modify its donor.

This recipe does not assemble a DEX, build an APK, register an engine, or run a
game. The caller must supply the verified StationN64Bridge and online core.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil


AE = "Lpaulscode/android/mupen64plusae/"
BRIDGE = "Lorg/emulationstation/frontend/netplay/StationN64Bridge;"
PREFIX = Path("paulscode/android/mupen64plusae")
EXPECTED = {
    "game/GameActivity.smali": "5728b3067a222e3f10d866e00939c3a0ac4f1319e382f63eb88134bd788d45f2",
    "jni/CoreService.smali": "808fa28c5163c0d88b6bc37ec2476eb33f5d6cf6ebce4639a03a333c9670788f",
    "jni/CoreService$ServiceHandler.smali": "04ab9a912ca709e6696fa151d352d9fe61949493e47e0c6e116511abeeb4f54c",
    "ActivityHelper.smali": "b0a8e16227d49cf9b6410550ce32cbff08d5f3d495a4dd1d2f39842a954756d7",
    "jni/CoreInterface.smali": "489cc104b4f0226cd047ea7c3883eea6fbdaf22bda49595115dce207455ec1d8",
    "persistent/GamePrefs.smali": "72f45913d4f0342b63a840caff46addf94560b5abe9f3b513a61b5ae09728097",
    "jni/CoreFragment.smali": "c095e9123fc4797ee4e3fa1857bfd9e7cbe3c31e9e7eeb0ea58302b7d76e79d3",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected one anchor, found {count}: {old[:150]!r}")
    return text.replace(old, new, 1)


def method(text: str, signature: str, transform) -> str:
    pattern = re.compile(r"(?ms)^\.method[^\n]* " + re.escape(signature) + r"\n.*?^\.end method$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"Expected one method {signature}, found {len(matches)}")
    found = matches[0]
    changed = transform(found.group(0))
    if changed == found.group(0):
        raise ValueError(f"Method not changed: {signature}")
    return text[:found.start()] + changed + text[found.end():]


def prepend(body: str, code: str, minimum_locals: int = 1) -> str:
    match = re.search(r"(?m)^    \.locals (\d+)\n", body)
    if match is None:
        raise ValueError("Expected .locals directive")
    count = max(int(match.group(1)), minimum_locals)
    directive = f"    .locals {count}\n"
    return body[:match.start()] + directive + "\n" + code + "\n" + body[match.end():]


def guard_return(body: str, hook: str, label: str) -> str:
    return prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->{hook}(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :{label}
    return-void
    :{label}""")


def patch_activity(text: str) -> str:
    text = method(text, "onCreate(Landroid/os/Bundle;)V", lambda body: prepend(body,
        f"    invoke-static/range {{p0 .. p0}}, {BRIDGE}->onCreate(Landroid/app/Activity;)V"))
    prefs = f"    iput-object v0, v1, {AE}game/GameActivity;->mGamePrefs:{AE}persistent/GamePrefs;"
    text = method(text, "onCreate(Landroid/os/Bundle;)V", lambda body: once(body, prefs, prefs + f"""

    invoke-virtual {{v1}}, Landroid/app/Activity;->getIntent()Landroid/content/Intent;
    move-result-object v2
    invoke-static {{v0, v2}}, {BRIDGE}->onGamePrefs(Ljava/lang/Object;Landroid/content/Intent;)V"""))
    text = method(text, "onNetplayReady()V", lambda body: prepend(body, f"""    iget-object v0, p0, {AE}game/GameActivity;->mCoreFragment:{AE}jni/CoreFragment;
    invoke-static {{p0, v0}}, {BRIDGE}->onReady(Landroid/app/Activity;Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :station_n64_original_ready
    return-void
    :station_n64_original_ready"""))
    for signature, label in (("onExitFinished()V", "station_n64_original_exit_finished"),
                             ("finishActivity()V", "station_n64_original_finish")):
        text = method(text, signature, lambda body, label=label: prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->onExit(Landroid/app/Activity;)Z
    move-result v0
    if-eqz v0, :{label}
    return-void
    :{label}"""))
    # p0 is reused for views later in onPause/onDestroy. Capture the real
    # Activity at method entry; these callbacks must never request native quit.
    for hook in ("onResume", "onPause", "onDestroy"):
        text = method(text, hook + "()V", lambda body, hook=hook: prepend(body,
            f"    invoke-static {{p0}}, {BRIDGE}->{hook}(Landroid/app/Activity;)V"))
    text = method(text, "onExitRequested(Z)V", lambda body: prepend(body, f"""    if-eqz p1, :station_n64_original_exit_request
    invoke-static {{p0}}, {BRIDGE}->authorizeHumanExit(Landroid/app/Activity;)V
    :station_n64_original_exit_request"""))
    new_intent = "    invoke-virtual {p0, p1}, Landroid/app/Activity;->setIntent(Landroid/content/Intent;)V"
    text = method(text, "onNewIntent(Landroid/content/Intent;)V", lambda body: once(body, new_intent,
        new_intent + f"\n\n    invoke-static {{p0, p1}}, {BRIDGE}->onNewIntent(Landroid/app/Activity;Landroid/content/Intent;)V"))
    text = method(text, "setPakTypeFromPrompt(I)V", lambda body:
        guard_return(body, "isStationContext", "station_n64_original_pak_prompt"))
    return text


def patch_helper(text: str) -> str:
    signature = f"startCoreService(Landroid/content/Context;Landroid/content/ServiceConnection;{AE}StartCoreServiceParams;)V"
    anchor = "    invoke-virtual {p0, v0}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;"
    return method(text, signature, lambda body: once(body, anchor,
        f"    invoke-static {{p0, v0}}, {BRIDGE}->propagate(Landroid/content/Context;Landroid/content/Intent;)V\n\n" + anchor))


def patch_service(text: str) -> str:
    text = method(text, "onStartCommand(Landroid/content/Intent;II)I", lambda body: prepend(body,
        f"    invoke-static {{p0, p1}}, {BRIDGE}->onServiceStart(Landroid/content/Context;Landroid/content/Intent;)V"))
    prefs = f"    iput-object v2, v3, {AE}jni/CoreService;->mGamePrefs:{AE}persistent/GamePrefs;"
    text = method(text, "onStartCommand(Landroid/content/Intent;II)I", lambda body: once(body, prefs, prefs +
        f"\n\n    invoke-static {{v3, v2}}, {BRIDGE}->onServicePrefs(Landroid/content/Context;Ljava/lang/Object;)V"))
    text = method(text, "autoSaveState(Z)V", lambda body: prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->skipAutoSave(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :station_n64_original_autosave
    if-eqz p1, :station_n64_no_autosave
    invoke-virtual {{p0}}, {AE}jni/CoreService;->shutdownEmulator()V
    :station_n64_no_autosave
    return-void
    :station_n64_original_autosave"""))
    for signature, label in (("copyGameContentsFromSdCard()V", "station_n64_original_import"),
                             ("copyGameContentsToSdCard()V", "station_n64_original_export")):
        text = method(text, signature, lambda body, label=label:
            guard_return(body, "skipExternalStorage", label))
    # The bridge classifies the already recorded human/failure reason; an
    # internal shutdown call is not itself proof of an explicit human request.
    text = method(text, "shutdownEmulator()V", lambda body: prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->isStationContext(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :station_n64_original_shutdown
    invoke-static {{p0}}, {BRIDGE}->allowShutdown(Landroid/content/Context;)Z
    move-result v0
    if-nez v0, :station_n64_authorized_shutdown
    return-void
    :station_n64_authorized_shutdown
    invoke-static {{p0}}, {BRIDGE}->requestHumanExit(Landroid/content/Context;)V
    :station_n64_original_shutdown"""))
    text = method(text, "forceExit()V", lambda body: prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->allowShutdown(Landroid/content/Context;)Z
    move-result v0
    if-nez v0, :station_n64_original_force_exit
    return-void
    :station_n64_original_force_exit"""))
    notification = "    invoke-static {p0, v2, v0, v4}, Landroid/app/PendingIntent;->getActivity(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;"
    text = method(text, "updateNotification()V", lambda body: once(body, notification,
        f"    invoke-static {{p0, v0}}, {BRIDGE}->propagate(Landroid/content/Context;Landroid/content/Intent;)V\n\n" + notification))
    for signature, label in (("restart()V", "station_n64_original_reset"),
                             ("advanceFrame()V", "station_n64_original_advance")):
        text = method(text, signature, lambda body, label=label:
            guard_return(body, "isStationContext", label))
    controller = f"updateControllerConfig(IZ{AE}jni/CoreTypes$PakType;)V"
    text = method(text, controller, lambda body: prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->isStationContext(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :station_n64_original_controller_config
    iget-object v0, p0, {AE}jni/CoreService;->mGamePrefs:{AE}persistent/GamePrefs;
    add-int/lit8 v1, p1, 0x1
    invoke-virtual {{v0, v1}}, {AE}persistent/GamePrefs;->getPakType(I){AE}jni/CoreTypes$PakType;
    move-result-object v0
    if-eq v0, p3, :station_n64_original_controller_config
    return-void
    :station_n64_original_controller_config""", minimum_locals=2))
    registration = f"    invoke-virtual {{p3, p2, p1}}, {AE}jni/CoreInterface;->netplaySetController(II)V"
    checked = f"""    invoke-static {{p0}}, {BRIDGE}->isStationContext(Landroid/content/Context;)Z
    move-result p4
    if-eqz p4, :station_n64_original_registration
    invoke-virtual {{p3, p2, p1}}, {AE}jni/CoreInterface;->stationNetplaySetController(II)Z
    move-result p3
    iput-boolean p3, p0, {AE}jni/CoreService;->mNetplayInitSuccess:Z
    goto :station_n64_registration_done
    :station_n64_original_registration
{registration}
    :station_n64_registration_done"""
    return method(text, "connectForNetplay(IILjava/lang/String;Ljava/lang/String;Ljava/net/InetAddress;I)V",
                  lambda body: once(body, registration, checked))


def patch_handler(text: str) -> str:
    first = f"    iget-object v0, p0, {AE}jni/CoreService$ServiceHandler;->this$0:{AE}jni/CoreService;"
    getter = f"    invoke-static {{v0}}, {AE}jni/CoreService;->-$$Nest$fgetmGameDataManager({AE}jni/CoreService;){AE}game/GameDataManager;"
    anchor = first + "\n\n" + getter
    guarded = first + f"""

    invoke-static {{v0}}, {BRIDGE}->skipLoadAutoSave(Landroid/content/Context;)Z
    move-result v0
    if-nez v0, :cond_1f
""" + "\n" + first + "\n\n" + getter
    return method(text, "handleMessage(Landroid/os/Message;)V", lambda body: once(body, anchor, guarded))


def patch_interface(text: str) -> str:
    # Both Native.load and AE bridge loadLibrary must resolve the same core.
    for register in ("v0", "v1"):
        literal = f'    const-string {register}, "mupen64plus-core"'
        text = once(text, literal, f"    invoke-static {{}}, {BRIDGE}->coreName()Ljava/lang/String;\n    move-result-object {register}")
    pattern = re.compile(r"(?ms)^\.method public netplaySetController\(II\)V\n.*?^\.end method$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError("Expected the original void registration API")
    body = matches[0].group(0).replace("netplaySetController(II)V", "stationNetplaySetController(II)Z", 1)
    command = f"    invoke-interface {{p0, p2, p1, v0}}, {AE}jni/CoreLibrary;->CoreDoCommand(IILcom/sun/jna/Pointer;)I"
    body = once(body, command, command + "\n    move-result v0")
    body = once(body, "    return-void", """    if-nez v0, :station_n64_registration_rejected
    const/4 v0, 0x1
    return v0
    :station_n64_registration_rejected
    const/4 v0, 0x0
    return v0""")
    return text + "\n\n" + body + "\n"


def patch_prefs(text: str) -> str:
    # AppData and its offline game root stay intact. A nullable override is
    # allowed only for the exact GamePrefs object registered by the bridge.
    text = method(text, "getGameDataDir()Ljava/lang/String;", lambda body: prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->gameDataDir(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v0
    if-eqz v0, :station_n64_original_game_data_dir
    return-object v0
    :station_n64_original_game_data_dir"""))
    return method(text, f"putPakType(I{AE}jni/CoreTypes$PakType;)V", lambda body: prepend(body, f"""    invoke-static {{p0}}, {BRIDGE}->gameDataDir(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v0
    if-eqz v0, :station_n64_original_pak_write
    return-void
    :station_n64_original_pak_write"""))


def patch_fragment(text: str) -> str:
    for signature, label in (("restart()V", "station_n64_original_reset_prompt"),
                             ("restartEmulator()V", "station_n64_original_restart_emulator")):
        text = method(text, signature, lambda body, label=label: prepend(body, f"""    iget-object v0, p0, {AE}jni/CoreFragment;->mCoreService:{AE}jni/CoreService;
    invoke-static {{v0}}, {BRIDGE}->isStationContext(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :{label}
    return-void
    :{label}"""))
    return text


PATCHERS = {
    "game/GameActivity.smali": patch_activity,
    "jni/CoreService.smali": patch_service,
    "jni/CoreService$ServiceHandler.smali": patch_handler,
    "ActivityHelper.smali": patch_helper,
    "jni/CoreInterface.smali": patch_interface,
    "persistent/GamePrefs.smali": patch_prefs,
    "jni/CoreFragment.smali": patch_fragment,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-smali", type=Path, required=True,
                        help="Unmodified integrated AE smali_classes36 root")
    parser.add_argument("--output-smali", type=Path, required=True,
                        help="New sibling/output tree; must not exist")
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    source = args.input_smali.resolve(strict=True)
    target = args.output_smali.resolve()
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Input and output must be disjoint; in-place patches are forbidden")
    if target.exists():
        raise FileExistsError(target)
    changes = []
    patched = {}
    # Complete validation and transformation before creating the output tree.
    for name, expected in EXPECTED.items():
        original = (source / PREFIX / name).read_bytes()
        if sha(original) != expected:
            raise ValueError(f"Input differs from pinned integrated AE source: {name}")
        decoded = original.decode("utf-8")
        if BRIDGE in decoded or "stationNetplaySetController" in decoded:
            raise ValueError(f"Input already patched: {name}")
        newline = "\r\n" if "\r\n" in decoded else "\n"
        normalized = decoded.replace("\r\n", "\n")
        result = PATCHERS[name](normalized)
        encoded = result.replace("\n", newline).encode("utf-8")
        patched[name] = encoded
        changes.append({"path": (PREFIX / name).as_posix(),
                        "sourceSha256": expected, "patchedSha256": sha(encoded)})
    shutil.copytree(source, target)
    for name, data in patched.items():
        (target / PREFIX / name).write_bytes(data)
    receipt = {"recipe": "station-mupen-online-r125", "sourceRoot": str(source),
               "outputRoot": str(target), "modifiedFiles": changes,
               "donorModified": False, "dexAssembled": False,
               "apkBuilt": False, "engineRegistered": False,
               "physicalGameplayValidated": False}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"modifiedFiles": len(changes), "receipt": str(args.receipt)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
