"""Compose a public static audit from read-only APK/source observations."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
TARGET = ROOT / "audits/station-runtime-cleanup-r132-20261011/execution-roots.json"
components = json.loads((HERE / "package-components.json").read_text(encoding="utf-8"))
startup = json.loads((HERE / "startup-roots.json").read_text(encoding="utf-8"))

def ref(relative, meaning, lines=None):
    data = (ROOT / relative).read_bytes()
    value = {"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "meaning": meaning}
    if lines is not None: value["lines"] = lines
    return value

CLIENT = "versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/"
NETPLAY = "versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/"
PSX = "integration/psx-online/java/org/emulationstation/frontend/netplay/"
SONY = "integration/sony-internal/"
refs = [
    ref("audits/station-r131-component-lifecycle-20261011/package-components.json", "All current manifest components, actual DEX definitions and engine manifest"),
    ref("audits/station-r131-component-lifecycle-20261011/startup-roots.json", "Actual manifest metadata and 728 targeted DEX method bodies; direct references, constants and selected branches"),
    ref("audits/station-r131-component-lifecycle-20261011/sandbox-literals.json", "DEX/native sandbox string search; presence is not a creator proof"),
    ref("audits/station-r131-component-lifecycle-20261011/packaged-config-search.json", "Non-Sony XML/JSON/config asset token and path search"),
    ref("audits/station-r131-component-lifecycle-20261011/native-class-literals.json", "Native references to existing online and Sony bridge class names"),
    ref("audits/station-r131-component-lifecycle-20261011/fixture-markers.json", "No packedprobe/testroots marker in standard native libraries or DEX"),
    ref(SONY + "java/org/emulationstation/frontend/sony/StationSonyComponentFactory.java", "Sony process-specific Application and replacement of the external Activity implementation"),
    ref("integration/psx-online/recipe/patch_factory_optin.py", "Actual classes28 Application factory opt-in for private PSX, absent from the original R124 Java input"),
    ref(PSX + "StationRoomsActivity.java", "Current online dispatch and Activity lifecycle", [454, 456, 1091, 1102]),
    ref(CLIENT + "DownloadService.java", "Event-driven foreground service, idle stop and active-job wake lock", [17, 56]),
    ref(CLIENT + "station/StationDownloadUi.java", "Notices owned only by foreground ESActivity", [76, 101]),
    ref(CLIENT + "station/StationControllerPresence.java", "Input callbacks active only in actual Dolphin EmulationActivity", [46, 95]),
    ref(NETPLAY + "StationSessionService.java", "Private bound session owner and Binder release"),
    ref(NETPLAY + "StationGameSession.java", "Per-session heartbeat and explicit human leave, not a generic idle loop", [17, 108]),
    ref(NETPLAY + "StationPresence.java", "Foreground social presence and its eligibility/cancellation gates", [24, 49]),
    ref(CLIENT + "station/StationFrontend.java", "Storage root, bounded queues and foreground-gated catalog polling", [45, 100]),
    ref(CLIENT + "station/StationInstaller.java", "Transaction directories, failed-install cleanup and preservation of old committed generations", [35, 84]),
    ref(CLIENT + "station/StationPlatforms.java", "Fixed verified mapping; no remote URL hostname converted into arbitrary platform folder", [95, 107]),
    ref(CLIENT + "station/StationPublication.java", "Unsupported platform accounting without arbitrary fallback mapping", [15, 22]),
    ref(PSX + "StationPsxLaunch.java", "Fresh per-launch HOME and consumed/discarded descriptor; home is not deleted by discard", [49, 89, 145, 169]),
    ref(PSX + "StationPsxSession.java", "Human-authorized exit closes transport/Binder and preserves no-auto-kill rule", [149, 165]),
    ref(NETPLAY + "StationRetroLaunch.java", "Shared overlays/autoconfig, per-room saves/states and secret clearing", [21, 27, 71, 82]),
    ref(SONY + "composition/java/org/emulationstation/frontend/sony/StationSonyAssets.java", "Verified module extraction cached in-process and exact private paths", [61, 81, 265, 328]),
    ref(SONY + "ps3/java/org/emulationstation/frontend/sony/Ps3Application.java", "PS3 Application does no extraction/JNI/firmware work"),
    ref(SONY + "ps3/java/org/emulationstation/frontend/sony/Ps3Bootstrap.java", "PS3 owner singleton and persistent userdata paths"),
    ref(SONY + "ps4/java/org/emulationstation/frontend/sony/Ps4Application.java", "Minimal PS4 Application"),
    ref(SONY + "ps4/java/org/emulationstation/frontend/sony/Ps4Runtime.java", "397-file runtime extraction or validation; staging cleanup", [17, 77, 96, 103]),
    ref(SONY + "ps4/java/org/emulationstation/frontend/sony/Ps4Activity.java", "On-demand native preparation and per-game IPC session", [81, 118, 175, 192, 224, 228]),
]

findings = [
    {"id": "ROOT-01", "confidence": "confirmed-current-APK", "classification": "required-owner-dispatch", "finding": "There are 40 DEX and 51,578 distinct defined class descriptors, with no duplicate defined descriptors. Every manifest component has a DEX definition. Historical source folders are not evidence of simultaneous runtime instances.", "removalSafe": False, "action": "Keep owner and JNI definitions; remove a class only after its Java/native/manifest/reflection callers are replaced or proved unreachable."},
    {"id": "ROOT-02", "confidence": "confirmed-current-APK-branches", "classification": "startup-work-candidate", "finding": "The Application remains YuzuApplication in the main process. Its onCreate executes guards for each system and returns early when a guard selects an emulator process. The main branch subsequently invokes PlatformAssets.install, BootstrapAssets.installKeys, Freedreno config, driver/input initialization and NativeLibrary device information. The guards do not initialize every emulator. PSX is intercepted by classes28's factory, and Sony has minimal private Applications.", "removalSafe": False, "action": "Measure main-process cold-start work separately. A later lazy Switch bootstrap must preserve original Application globals, driver/input readiness and Switch launch, including provider-first startup. This audit makes no temperature or CPU percentage claim."},
    {"id": "ROOT-03", "confidence": "confirmed-current-APK-and-source", "classification": "old-implementation-diverted-required-component-name", "finding": "StationSonyOfflineActivity is declared and referenced by the native carousel, but StationSonyComponentFactory substitutes StationSonyLaunchActivity when Android instantiates that name. The old external implementation therefore is not the ordinary R131 Sony launch path. Its presence is not evidence that an external emulator runs alongside the internal owner.", "removalSafe": False, "action": "If consolidating, replace the existing implementation under its compatible component name or patch every native caller and manifest together. Do not simply delete the declaration/class name."},
    {"id": "ROOT-04", "confidence": "confirmed-current-bytecode-and-native-literals", "classification": "legacy-path-still-referenced", "finding": "StationNetplayActivity is referenced in the native carousel. Its bytecode still constructs StationDolphinNetplayActivity. These are separate from StationRoomsActivity's current native-owner dispatch. Neither route is proved globally unreachable merely because the Rooms path does not use it.", "removalSafe": False, "action": "Retain pending exact native callsite and menu-option migration. A class-name literal is a possible reference, not proof that it is executing."},
    {"id": "ROOT-05", "confidence": "confirmed-source-and-current-lifecycle-bytecode", "classification": "functional-background-work", "finding": "StationRoomsActivity stops artwork, polling, graphic listeners and pending UI requests onStop, then closes artwork and executor queues onDestroy. DownloadService stops itself when ACTIVE becomes empty and returns START_NOT_STICKY. StationSessionService is bound and releases anchors on unbind/destroy. No BOOT_COMPLETED receiver exists; the only receiver is the DUMP-protected profile installer.", "removalSafe": False, "action": "Keep download resume, room membership and Binder ownership. Investigate a leak only with an unfinished task/anchor or resumed-state contradiction, rather than removing all services."},
    {"id": "ROOT-06", "confidence": "confirmed-current-manifest", "classification": "process-startup-providers", "finding": "The package declares 20 providers, including 10 namespaced startup providers. Initializers include lifecycle, emoji/profile installation and the Wii U OkHttp platform initializer. They are process roots when the corresponding process is created, not 20 continuously running workers.", "removalSafe": False, "action": "Changing initializers needs an owner-by-owner dependency review. File/DocumentProviders and namespace SDK copies support distinct emulator imports and settings."},
    {"id": "ROOT-07", "confidence": "confirmed-source", "classification": "retained-session-directory-candidate", "finding": "StationPsxLaunch creates files/station-psx-online/<launch>/home for every launch and writes presentation resources/settings there. Its consume/discard delete only the launch descriptor. Human-exit cleanup closes transport/Binder/native owner but does not remove the home. This proves no per-home retention cleanup in the audited launch/exit paths, not that the directory contains disposable data.", "removalSafe": False, "action": "Separate presentation cache from saves. Only remove an exact app-owned completed launch after owner/descriptor/transport completion and preserve/migrate saves. Do not sweep active, pending or unknown homes."},
    {"id": "ROOT-08", "confidence": "confirmed-source", "classification": "intentional-persistent-data", "finding": "Retro online directories retain per-room saves/states and shared BIOS/autoconfig/overlays. Overlay preparation reads and compares packaged data before skipping identical writes. PS3 userdata includes firmware and saves. PS4 module/runtime and shader/cache paths are validated and reused; session IPC is closed at native-run return. These private directories are functional, not inherently obsolete sandboxes.", "removalSafe": False, "action": "Optimize verified shared preparation/cache only with identity- and lifecycle-aware reuse. Keep firmware, games, saves, shader cache, current native assets and pending transfer transactions."},
    {"id": "ROOT-09", "confidence": "confirmed-search-negative-with-bounded-scope", "classification": "sandbox-creator-not-yet-proven", "finding": "No Java DEX literal sandbox, no packaged template/path roms/sandbox, no packedprobe/testroots marker and no path-like sandbox value were found in standard libraries, DEX or non-Sony packaged text assets. Native sandbox matches are QEMU options, SDL APIs, Yuzu filesystem symbols and game metadata. Remote catalog and deleted-device directory evidence were not read in this subtask.", "removalSafe": False, "action": "Capture the exact recreated path and creation window, then trace the native-supplied ROM root and runtime catalog/publication. Do not attribute it to a library just because it contains the word sandbox."},
    {"id": "ROOT-10", "confidence": "confirmed-source", "classification": "transactional-storage-required", "finding": "StationInstaller confines game generations under roms/.station-v2/<verified platform>/<item>/<install generation>/content and deletes only uncommitted failed generations. StationPublication skips unsupported platforms, StationPlatforms.resolve uses a fixed mapping, and StationFrontend prepares the application-supplied root; these paths do not derive a new root folder from a remote hostname.", "removalSafe": False, "action": "Preserve .station-v2, private install receipts and download staging. Orphan-generation cleanup needs a complete receipt/queue reachability set and must exclude active transactions and last committed generation."},
]

routes = [
    {"scope": "main launcher", "root": "LoginActivity MAIN/LAUNCHER -> ESActivity", "process": "main", "owner": "Station frontend + native carousel", "status": "declared-and-called", "preserve": ["authentication", "catalogue", "downloads", "graphics lifecycle", "original Switch Application globals"]},
    {"scope": "normal SNES / Mega Drive", "root": "com.imagine.BaseActivity / com.mdimagn.BaseActivity", "process": ":snes / :megadrive", "status": "separate-manifest-owners-with-bootstrap-guards"},
    {"scope": "normal Nintendo 64", "root": "N64EntryActivity -> Mupen GameActivity/CoreService", "process": ":n64 / :n64core", "status": "required-Activity-and-service-family"},
    {"scope": "normal GameCube/Wii", "root": "DolphinEntryActivity -> official Dolphin EmulationActivity", "process": ":dolphin", "status": "required-native-owner"},
    {"scope": "normal Dreamcast/Atomiswave/Naomi", "root": "com.flycast.emulator.NativeGLActivity", "process": ":flycast", "status": "required-native-owner"},
    {"scope": "normal PS2", "root": "com.armsx2.*", "process": ":ps2", "status": "required-native-owner-and-settings"},
    {"scope": "normal PSP", "root": "org.ppsspp.ppsspp.PpssppActivity", "process": ":psp", "status": "required-native-owner-and-result-proxies"},
    {"scope": "normal Wii U", "root": "WiiUEntryActivity -> info.cemu.cemu.*", "process": ":wiiu", "status": "required-native-owner-and-documents"},
    {"scope": "normal Xbox 360", "root": "Xbox360EntryActivity/Xbox360GameEntryActivity -> xendroid.compose.*", "process": ":xbox360 / :xbox360emu", "status": "required-native-owner", "note": "MainAliveService has only constructor/onBind bytecode; no poll/start worker is proved by its declaration."},
    {"scope": "normal PS Vita", "root": "VitaEntryActivity -> org.vita3k.emulator.*", "process": ":psvita", "status": "required-native-owner-and-install-service"},
    {"scope": "normal Saturn", "root": "SaturnActivity", "process": ":saturn", "status": "required-native-owner"},
    {"scope": "normal Xbox", "root": "XboxEntryActivity -> com.izzy2lost.x1box.*", "process": ":xbox / :xboxemu", "status": "required-native-owner-and-setup-library"},
    {"scope": "normal MAME/arcade", "root": "MameEntryActivity -> com.seleuco.mame4droid.MAME4droid", "process": ":mame", "status": "required-native-owner-and-input-preferences"},
    {"scope": "normal Switch", "root": "org.yuzu.yuzu_emu.activities.EmulationActivity", "process": "main", "status": "required-native-owner; App initialization must not be removed wholesale"},
    {"scope": "normal PS3/PS4", "root": "StationSonyOfflineActivity component name -> Sony factory substitute -> StationSonyLaunchActivity -> Ps3Activity/Ps4Activity", "process": "main dispatcher -> :station_ps3 / :station_ps4", "status": "internal-offline-owner-on-demand"},
    {"scope": "online Nintendo 64", "root": "StationRoomsActivity -> StationN64Activity -> Mupen GameActivity/CoreService", "process": "main -> :n64core", "status": "current-system-native-backend"},
    {"scope": "online GameCube/Wii", "root": "StationRoomsActivity -> StationDolphinActivity -> StationDolphinOnlineActivity -> official Dolphin EmulationActivity", "process": "main -> :dolphin", "status": "current-system-native-backend"},
    {"scope": "online PSX", "root": "StationRoomsActivity -> StationPsxOnlineActivity -> SDL normal LibretroPlayer owner + station_psx_online adapter", "process": ":station_psx_online", "status": "current-system-owner; minimal private Application"},
    {"scope": "online SNES/Mega Drive/Neo Geo CD/FBNeo/CPS", "root": "StationRoomsActivity -> StationRetroActivity", "process": ":station_netplay", "status": "still-selected-online-engine; removal-would-break-supported-paths"},
    {"scope": "online PS2/Saturn/Geolith", "root": "policy/engine readiness gate", "status": "automatic-integration-disabled-or-engine-launchReady-false", "note": "Readiness gating does not make the corresponding normal emulator removable."},
]

background = [
    {"owner": "StationDownloadUi", "activation": "ESActivity resumed/window focused + error notice", "release": "pause/stop/destroy", "timer": "none; event-driven"},
    {"owner": "StationControllerPresence", "activation": "official Dolphin EmulationActivity resumed", "release": "pause/stop/destroy", "timer": "InputManager/layout callbacks, not polling all emulators"},
    {"owner": "DownloadService", "activation": "active download/preparation jobs only", "release": "ACTIVE empty -> stopSelf; destruction releases wake lock", "timer": "notification throttling; six-hour bounded wake acquisition for specific busy phases", "review": "Verify an awaiting-authorization job cannot remain busy without productive work; no observed leak asserted."},
    {"owner": "StationPresence", "activation": "eligible foreground screen; excluded auth, Rooms and station_netplay", "release": "foreground false/cancellation/generation gates", "timer": "heartbeat 20 s, blocking events, retries while active", "purpose": "online status/invites while app is open"},
    {"owner": "StationGameSession + StationSessionService", "activation": "one verified room launch/anchor", "release": "human leave/anchor teardown/unbind", "timer": "session heartbeat 20 s", "purpose": "session authority remains alive while native emulator is foreground"},
    {"owner": "StationRoomsActivity", "activation": "onStart", "release": "onStop polling/artwork/requests; onDestroy workers", "timer": "multiplayer poll lifecycle-owned"},
    {"owner": "PSX/Dolphin sessions and MultiplayerTunnel", "activation": "native online session only", "release": "human-authorized cleanup/closed transport", "timer": "native status 50 ms; tunnel control 250 ms", "purpose": "synchronization and recovery, not a carousel task"},
    {"owner": "StationFrontend catalog refresh", "activation": "configured and foreground, authorized, no active download/cover requests", "release": "foreground/catalog cancellation gates", "timer": "initial 5 s, subsequent 60 s"},
    {"owner": "StationSinglePassVideo720", "activation": "native video open for visible foreground cell", "release": "stopAll/lifecycle/player release", "timer": "one lazy HandlerThread and active watchdog; no idle watchdog after completed/stopped sessions", "note": "R130 adds optional principal-cell looping; preserve that option and single-pass collection behavior."},
    {"owner": "PS3/PS4 internal owners", "activation": "explicit Sony launch/settings/prepare action in a private process", "release": "owner shutdown/native return; process retirement guards", "timer": "no automatic carousel extraction/JNI/firmware task"},
]

result = {
    "schema": "station.runtime-cleanup.execution-roots.v1",
    "auditBaseRevision": "R131",
    "plannedConsumerRevision": "R132",
    "sourceCommit": components["sourceCommit"],
    "apkSha256": components["apkSha256"],
    "apkBytes": components["apkBytes"],
    "actualManifestSha256": components["actualManifestSha256"],
    "artifactScope": {"assembly": "G:/StationNormalOwnersR127/sony-internal/correction/assembly", "freezePayloads": 305, "DEX39FromR130Preserved": True, "pointersWereCompared": 3, "fullApkDigestRecomputed": True},
    "counts": {**components["componentCounts"], "DEX": components["dexCount"], "definedClasses": components["definedClasses"], "duplicateDefinedClassDescriptors": len(components["duplicateDefinedClassDescriptors"]), "manifestMetadataRows": len(startup["manifestMetadata"]), "targetedDexMethods": len(startup["targetedDexMethods"]), "manifestComponentsMissingDexDefinition": 0},
    "method": ["Read current binary AndroidManifest and DEX class definitions", "Read targeted current DEX instructions with instruction-boundary checks", "Read current composition recipes and inherited Java inputs", "Read-only strings from standard native libraries and non-Sony packaged configs", "Compare exact artifact/pointer/source-freeze evidence"],
    "runtimeMeasurementPerformed": False,
    "phoneOperatedByThisAudit": False,
    "serverContactedByThisAudit": False,
    "productiveSourceChanged": False,
    "compilationOrTestsRun": False,
    "limitations": ["Static reachability is incomplete across native callbacks/reflection/resources and runtime server catalog", "No CPU/temperature/gameplay/heap/thread measurement", "No exact recreated sandbox path or creator syscall was observed by this audit", "No class or data directory is approved for blanket deletion"],
    "findings": findings,
    "executionRoutes": routes,
    "backgroundRoots": background,
    "safeCleanupNow": {"provedUnusedProductiveClasses": [], "provedDisposableDeviceDirectories": [], "historicalCodePresenceAloneAuthorizesDeletion": False, "mustPreserve": ["saves", "games", "licenses/authentication", "firmware", "current verified modules", "install receipts", "pending/paused download queues", "active session/Binder/transport ownership", "retained stable donor required by reconstruction"]},
    "engineReadinessFromActualPackage": [{k: row[k] for k in ["platform", "engineId", "backend", "launchReady", "maximumPlayers"] if k in row} for row in components["engineManifest"]["engines"]],
    "sourceAndEvidenceReferences": refs,
    "privateMaterialIncluded": False,
    "tokensPersonalIdsLogsOrScreenshotsIncluded": False,
}
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"output": str(TARGET), "findings": len(findings), "routes": len(routes), "backgroundRoots": len(background), "references": len(refs)}))
