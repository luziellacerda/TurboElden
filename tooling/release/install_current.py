#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Inspect/update the explicit current APK on one authorized, idle USB phone.

Uses CURRENT -> sole-backup CURRENT -> desenvolvimento/ATUAL -> final evidence.
Never chooses a historical APK, installs companion emulators, removes tasks,
force-stops a game, uninstalls, clears data, changes Android settings or bypasses
Login. An already identical installation is reused. Official entry is observed
for at most 30 seconds and one stale-history Gallery retry is permitted only
after rechecking that no game/download/service is running.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("station_current_release", Path(__file__).with_name("compile_current.py"))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
PACKAGE = release.PACKAGE
LOGIN = release.LOGIN
FRONTEND = "org.emulationstation.frontend.ESActivity"
ROOMS = "org.emulationstation.frontend.netplay.StationRoomsActivity"
GALLERY = "paulscode.android.mupen64plusae.GalleryActivity"
IDLE_ACTIVITIES = frozenset((LOGIN, FRONTEND, ROOMS))
FLAG_LAUNCHED_FROM_HISTORY = 0x00100000
HEX_SHA = re.compile(r"[0-9a-f]{64}")


def require(ok, message):
    release.require(ok, message)


def own_component(line):
    match = re.search(re.escape(PACKAGE) + r"/([^\s}]+)", line)
    if not match:
        return None
    name = match.group(1).rstrip(",")
    return PACKAGE + name if name.startswith(".") else name


def activity_snapshot(text):
    """Parse live ActivityRecords only; cached Recents are not active games."""
    lines, records, task_counts = text.splitlines(), [], {}
    starts = [i for i, row in enumerate(lines) if re.search(r"\*\s*Hist\s+#\d+:", row)]
    for index, start in enumerate(starts):
        header = lines[start]
        header_task = re.search(r"\bt(\d+)\b", header)
        if header_task:
            task_id = int(header_task.group(1))
            task_counts[task_id] = task_counts.get(task_id, 0) + 1
        component = own_component(header)
        if component is None:
            continue
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        # Android's next task/stack header ends the current Hist record.
        for position in range(start + 1, end):
            if re.search(r"^\s*(?:\*\s*Task\{|Task\{|RootTask\{|Display #)", lines[position]):
                end = position
                break
        section = "\n".join(lines[start:end])
        task_header = ""
        for position in range(start - 1, -1, -1):
            if re.search(r"\b(?:Task|TaskRecord)\{", lines[position]):
                task_header = lines[position]
                break
        flags = re.findall(r"\bflg=0x([0-9a-fA-F]+)\b", section)
        hist = re.search(r"\bHist\s+#(\d+):", header)
        task = re.search(r"\bt(\d+)\b", header)
        user = re.search(r"\bu(\d+)\b", header)
        visibility = re.findall(r"\b(?:mVisibleRequested|mVisible|visible)=(true|false)\b", section)
        if not visibility:
            visibility = re.findall(r"\bvisible=(true|false)\b", task_header)
        visible = True if "true" in visibility else False if visibility else None
        records.append({"component": component, "hist": int(hist.group(1)),
                        "task": int(task.group(1)) if task else None,
                        "user": int(user.group(1)) if user else None,
                        "visible": visible,
                        "fromHistory": any(int(value, 16) & FLAG_LAUNCHED_FROM_HISTORY for value in flags)})
    top_lines = [row for row in lines if re.search(r"\btopResumedActivity\s*[:=]", row)]
    if not top_lines:
        top_lines = [row for row in lines if re.search(r"\bmResumedActivity\s*[:=]", row)]
    own_tops = {own_component(row) for row in top_lines if own_component(row)}
    top = next(iter(own_tops)) if len(own_tops) == 1 else None
    mixed_tops = bool(own_tops and any(own_component(row) is None for row in top_lines))
    return {"records": records, "top": top, "taskRecordCounts": task_counts,
            "ambiguousTop": len(own_tops) > 1 or mixed_tops,
            "otherApplicationResumed": bool(top_lines and not own_tops)}


class Adb:
    def __init__(self, executable, serial):
        self.executable, self.serial = Path(executable), serial

    def __call__(self, *command, timeout=60):
        require(self.executable.is_file(), "Preserved ADB tool is missing")
        # Arguments are passed directly: no shell expression or composed script.
        value = subprocess.run([str(self.executable), "-s", self.serial, *map(str, command)],
                               capture_output=True, timeout=timeout)
        require(value.returncode == 0, "Explicit device operation failed; no fallback phone was selected")
        output = value.stdout.decode("utf-8", "replace")
        require(not re.search(r"^\s*(?:Error:|error:|Exception)", output, re.M), "Android rejected the explicit operation")
        return output


def device_identity(adb):
    text = adb("shell", "dumpsys", "package", PACKAGE)
    fields = {}
    for key in ("firstInstallTime", "lastUpdateTime", "dataDir"):
        match = re.search(r"^\s*" + key + r"=(.+)$", text, re.M)
        require(match is not None, "Installed package identity is incomplete; fresh-install handling requires a separate request")
        fields[key] = match.group(1).strip()
    rows = adb("shell", "cmd", "package", "list", "packages", "--user", "0", "-U", PACKAGE)
    uid = re.search(r"^package:" + re.escape(PACKAGE) + r"\s+uid:(\d+)\s*$", rows, re.M)
    require(uid is not None, "Package is not installed for the authorized user0")
    fields["uid"] = uid.group(1)
    require(fields["dataDir"].endswith("/" + PACKAGE), "Installed data directory has another owner")
    return fields


def installed_sha(adb):
    rows = adb("shell", "pm", "path", "--user", "0", PACKAGE).strip().splitlines()
    require(len(rows) == 1 and rows[0].startswith("package:/data/app/"), "Unexpected installed APK layout; split/fresh packages require reviewed handling")
    path = rows[0][8:]
    require(re.fullmatch(r"[A-Za-z0-9/_+=.~-]+", path) and path.endswith("/base.apk"), "Unexpected installed APK path")
    value = adb("shell", "sha256sum", path, timeout=240).split()
    require(value and HEX_SHA.fullmatch(value[0]), "Phone did not provide the integral APK SHA256")
    return value[0]


def stale_gallery(row, snapshot, *, invisible_required):
    return (row["component"] == GALLERY and row["hist"] == 0 and row["user"] == 0 and
            row["fromHistory"] and row["task"] is not None and
            (not invisible_required or row["visible"] is False) and
            snapshot["taskRecordCounts"].get(row["task"]) == 1)


def idle_snapshot(adb, *, retry_history_tasks=None, deadline=None):
    def timeout():
        if deadline is None:
            return 60
        remaining = deadline - time.monotonic()
        require(remaining > 0, "Entry observation deadline ended before idle revalidation")
        return min(5, remaining)
    snapshot = activity_snapshot(adb("shell", "dumpsys", "activity", "activities", timeout=timeout()))
    for row in snapshot["records"]:
        require(row["user"] == 0, "An app Activity belongs to another Android user")
        permitted = row["component"] in IDLE_ACTIVITIES
        if row["component"] == GALLERY:
            permitted = stale_gallery(row, snapshot, invisible_required=retry_history_tasks is None)
            if retry_history_tasks is not None:
                permitted = permitted and row["task"] in retry_history_tasks
        require(permitted, "An emulator, unknown panel or game is open; exit it manually before updating")
    services = adb("shell", "dumpsys", "activity", "services", PACKAGE, timeout=timeout())
    require("ServiceRecord{" not in services, "An app service/download is active; wait or exit manually before updating")
    if retry_history_tasks is not None:
        gallery = [row for row in snapshot["records"] if row["component"] == GALLERY]
        require(snapshot["top"] == GALLERY and len(gallery) == 1,
                "Unexpected Gallery is not one stale own leaf task; automatic retry refused")
    return snapshot


def local_preflight(context):
    """Verify the explicit current bytes/signature/entry and scoped source bindings."""
    current, apk, final, tools = context["current"], context["apk"], context["final"], context["tools"]
    require(apk.stat().st_size == current["bytes"] and release.sha(apk) == current["sha256"], "Actual installer differs from CURRENT")
    if current["revision"] in ("R131", "R132", "R133", "R134"):
        # Internal owners and subsequent scoped overlays require their actual
        # compilation/asset/source guards and exact reviewed assembly before
        # any phone operation, not merely a signed APK receipt.
        release.source_guard(context)
    for name, recorded in final.get("verificationTools", {}).items():
        table = {"java": tools / "jdk17/bin/java.exe", "apksignerJar": tools / "android-build-tools-35/lib/apksigner.jar",
                 "zipalign": tools / "android-build-tools-35/zipalign.exe"}
        require(name in table and release.sha(table[name]) == recorded["sha256"], "Verification tool differs from final evidence: " + name)
    entry = release.manifest_entry(apk, context["repo"])
    stdout, _ = release.run([tools / "jdk17/bin/java.exe", "-jar", tools / "android-build-tools-35/lib/apksigner.jar",
                             "verify", "--verbose", "--print-certs", apk], timeout=900, env=release.env_for_tools(context))
    signer = re.search(r"^Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]{64})\s*$", stdout, re.M)
    require(signer and signer.group(1).lower() == release.CERT, "Actual installer certificate differs from the original app")
    require(not re.search(r"^Signer #[2-9]\d* certificate", stdout, re.M), "Unexpected additional signer")
    for scheme in ("v2", "v3"):
        require(re.search(r"^Verified using " + scheme + r" scheme.*: true\s*$", stdout, re.M), "Actual signature scheme missing: " + scheme)
    release.run([tools / "android-build-tools-35/zipalign.exe", "-P", "16", "-c", "4", apk], timeout=300)
    return entry


def official_launch(adb, limit_seconds, history_tasks):
    """Observe official entry, without resuming/removing arbitrary tasks."""
    deadline = time.monotonic() + limit_seconds
    retried, stable_frontend, last, refused = False, 0, None, None

    def remaining():
        value = deadline - time.monotonic()
        require(value > 0, "Official-entry observation deadline ended")
        return value

    def enter():
        adb("shell", "am", "start", "-W", "-a", "android.intent.action.MAIN",
            "-c", "android.intent.category.LAUNCHER", "-n", PACKAGE + "/" + LOGIN,
            timeout=min(10, remaining()))

    enter()
    while time.monotonic() < deadline:
        try:
            snapshot = activity_snapshot(adb("shell", "dumpsys", "activity", "activities", timeout=min(5, remaining())))
        except (subprocess.TimeoutExpired, ValueError):
            break
        last = snapshot["top"]
        if last == FRONTEND and not snapshot["ambiguousTop"]:
            stable_frontend += 1
            if stable_frontend >= 2:
                return {"launchOutcome": "frontend", "officialFrontendObserved": True,
                        "officialEntryRequested": True, "staleHistoryRetryPerformed": retried,
                        "authenticatedSessionChecked": False, "physicalGameplayValidated": False}
        else:
            stable_frontend = 0
        if last == GALLERY and not retried:
            try:
                idle_snapshot(adb, retry_history_tasks=history_tasks, deadline=deadline)
                if remaining() <= 2:
                    break
                enter()
                retried = True
                continue
            except (ValueError, subprocess.TimeoutExpired):
                refused = "retry-idle-check-failed"
                break
        if last not in (None, LOGIN, FRONTEND, GALLERY):
            refused = "unexpected-own-emulator-or-panel"
            break
        time.sleep(min(.5, max(0, deadline - time.monotonic())))
    outcome = "authentication-pending" if last == LOGIN else "unexpected-emulator" if last == GALLERY or refused else "unobserved"
    return {"launchOutcome": outcome, "officialFrontendObserved": False,
            "officialEntryRequested": True, "staleHistoryRetryPerformed": retried,
            "launchRetryBlocked": refused is not None, "authenticatedSessionChecked": False,
            "physicalGameplayValidated": False}


def save(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=release.REPO_DEFAULT)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--expected-model", required=True)
    parser.add_argument("--expected-installed-sha256")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--allow-update", action="store_true")
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--launch-timeout-seconds", type=int, default=30)
    args = parser.parse_args()
    require(re.fullmatch(r"[A-Za-z0-9._-]+", args.serial) and "._tcp" not in args.serial,
            "Use the explicit authorized USB serial, never a network address or automatic device")
    require(5 <= args.launch_timeout_seconds <= 30, "Official entry observation must be limited to 5..30 seconds")
    context = release.resolve_current(args.current.resolve(strict=True), args.repo.resolve(strict=True))
    local_preflight(context)
    adb = Adb(context["tools"] / "platform-tools/adb.exe", args.serial)
    require(adb("get-state").strip() == "device", "Explicit USB device is not authorized")
    require(adb("get-serialno").strip() == args.serial, "ADB resolved another device")
    require(adb("shell", "am", "get-current-user").strip() == "0", "Foreground Android user is not the authorized user0")
    model = adb("shell", "getprop", "ro.product.model").strip()
    require(model.casefold() == args.expected_model.strip().casefold(), "Connected model differs from the explicitly inspected phone")
    initial_idle = idle_snapshot(adb)
    history_tasks = {row["task"] for row in initial_idle["records"]
                     if stale_gallery(row, initial_idle, invisible_required=True)}
    before, previous = device_identity(adb), installed_sha(adb)
    pointer = release.read(args.current)
    known = {row["sha256"] for row in pointer.get("installedHistory", [])}
    for name in ("lastInstalled", "currentDevelopmentCandidate"):
        if name in pointer:
            known.add(pointer[name]["sha256"])
    if args.expected_installed_sha256:
        expected_previous = args.expected_installed_sha256.lower()
        require(HEX_SHA.fullmatch(expected_previous) and previous == expected_previous,
                "Installed integral APK differs from the explicit inspected baseline")
    else:
        require(previous in known, "Installed APK is not an explicit known baseline; inspect its SHA256 before authorizing an update")
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {"schemaVersion": 1, "revision": context["current"]["revision"], "package": PACKAGE,
              "deviceModel": model, "sourceCommit": context["current"]["sourceCommit"],
              "startedUTC": started, "apkSHA256": context["current"]["sha256"],
              "apkBytes": context["current"]["bytes"], "previousAPK_SHA256": previous,
              "currentResolvedFromExplicitPointer": True, "androidUser": 0,
              "activeEmulatorBeforeInstall": False, "activeDownloadBeforeInstall": False,
              "signatureCertificateSHA256": release.CERT, "originalInstallerCertificateVerified": True,
              "installed": False, "installPerformed": False, "launchRequested": False,
              "officialFrontendObserved": False, "authenticatedSessionChecked": False,
              "serverActivationVerified": False, "physicalGameplayValidated": False,
              "externalEmulatorsInstalledByThisProcedure": False,
              "uninstalledOrClearedData": False, "deviceSettingsChanged": False,
              "tasksRemoved": False, "appForceStopped": False,
              "containsDeviceSerialOrPersonalSessionData": False}
    save(args.receipt, record)
    if previous != context["current"]["sha256"]:
        require(args.allow_update, "Inspection passed; updating requires explicit --allow-update")
        # The expensive hash/preflight above must not leave an old idle snapshot.
        fresh_context = release.resolve_current(args.current.resolve(strict=True), args.repo.resolve(strict=True))
        require(fresh_context["current"] == context["current"] and fresh_context["final"] == context["final"],
                "Current installer pointer/evidence changed during inspection")
        require(device_identity(adb) == before, "Installed identity changed during inspection")
        latest_idle = idle_snapshot(adb)
        history_tasks |= {row["task"] for row in latest_idle["records"]
                          if stale_gallery(row, latest_idle, invisible_required=True)}
        result = adb("install", "--streaming", "--no-incremental", "-r", "--user", "0", context["apk"], timeout=600)
        require(re.search(r"^Success\s*$", result, re.M), "Android did not confirm the update; receipt does not claim installation")
        record["installPerformed"] = True
    after, actual = device_identity(adb), installed_sha(adb)
    for name in ("uid", "firstInstallTime", "dataDir"):
        require(before[name] == after[name], "Original package identity/data preservation check failed")
    require(actual == context["current"]["sha256"], "Device integral APK differs from the exact current installer")
    record.update(installed=True, deviceAPK_SHA256=actual, installedAPKHashMatchesPackage=True,
                  originalUIDPreserved=True, originalInstallTimePreserved=True,
                  dataDirectoryPreserved=True, dataPreserved=True,
                  sameSigningIdentityAcceptedByAndroid=True,
                  directStreamingUpdate=record["installPerformed"], extraAPKCopyOnPhone=False,
                  completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(args.receipt, record)
    if args.launch:
        # Never move an active game/download merely to improve an install receipt.
        entry_idle = idle_snapshot(adb)
        history_tasks |= {row["task"] for row in entry_idle["records"]
                          if stale_gallery(row, entry_idle, invisible_required=True)}
        record["launchRequested"] = True
        save(args.receipt, record)
        try:
            record.update(official_launch(adb, args.launch_timeout_seconds, history_tasks))
        except (ValueError, subprocess.TimeoutExpired):
            record.update(launchOutcome="unobserved", officialFrontendObserved=False,
                          launchOperationFailed=True)
        record["entryObservationCompletedUTC"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save(args.receipt, record)
    print(json.dumps({"revision": record["revision"], "installed": record["installed"],
                      "installPerformed": record["installPerformed"],
                      "launchOutcome": record.get("launchOutcome", "not-requested"),
                      "officialFrontendObserved": record["officialFrontendObserved"]}))


if __name__ == "__main__":
    main()
