# Dolphin Station online R126 — native contract

## Identity and isolation

- Upstream: Dolphin `2609-7`, commit `5102a0339c2177575378107b76541e47cc52122d`.
- This candidate builds `libstation_dolphin_online.so` plus four uniquely named graphics hooks. It does not replace `libdolp.so` or any normal hook.
- Ordinary calls delegate to the real ENet implementation until `nativeConfigure` opts in. Offline preferences and save paths are not rewritten.
- Native build/probe success does not validate physical multiplayer gameplay or the effective production server registry. The final Java/DEX/manifest and APK packaging are now compiled and checked separately; see the actual receipts and STATUS.md.

## Launch and ownership

1. The private pending launch is validated in the main app. Select the online JNI library before the exclusive `:dolphin` process initializes `DolphinApplication`.
2. Complete original Dolphin initialization and directory initialization, then invoke `nativeConfigure`. Never call `Config::SetCurrent` before its original configuration system exists.
3. Hold one strong official `NetplaySession`, initialized with the exact local `GameFile`. Its native UI callback owns the original `BootSessionData`.
4. Run session operations on one worker. `nativeConnect` calls the actual official Android `nativeHost`/`nativeJoin`, not RetroArch. The host connects locally before admitting remote slots, ensuring native host PID 1.
5. Collect the official boot callback/launch flow, open the original `EmulationActivity`, and consume `BootSessionData` once using its existing `RunNetPlay` path.
6. Do not start a game until the host reports the exact authenticated roster and controller mapping, all official clients have the game, and the signed global barrier permits execution.

The native slot mask uses **bits 1–4**: slot 1 is `0x02`, slot 2 `0x04`, slot 3 `0x08`, slot 4 `0x10`. Convert app masks in bits 0–3 using `<< 1`. `nativeRegisteredSlots` returns the native convention. Masks must contain host/local slots and two to four slots. Epoch must be positive; initial epoch 1 is permitted before the fresh signed state arrives.

## Fixed native session options

These are `CurrentRun` overrides and never persisted into offline preferences:

| Upstream option | Value |
|---|---|
| TraversalChoice / UseUPNP / UseIndex / EnableQoS | `direct` / false / false / false |
| Address / HostPort / ConnectPort | `127.0.0.1` / caller's authenticated local port / same port |
| EnableChunkedUploadLimit | false |
| BufferSize / BufferSizeClient | 5 / 1; client buffer is also applied to the actual connected client |
| NetworkMode / GolfModeOverlay | `fixeddelay` / false |
| SyncSaves / WriteSaveData / SyncAllWiiSaves | true / true / false |
| SyncCodes / EnableCheats / RecordInputs | false / false / false |
| StrictSettingsSync / HideRemoteGBAs | true / false |

The actual upstream symbols are `NETPLAY_SAVEDATA_LOAD`, `NETPLAY_SAVEDATA_WRITE`, `NETPLAY_SAVEDATA_SYNC_ALL_WII`. The fixed profile must declare `settingsPolicy=official-pinned-gameini+host-synchronized-strict-v1`: original `SetupNetSettings` loads pinned GameINI, serializes Core/GFX/SYSCONF settings, and the official NetPlay configuration layer applies them to every peer. This policy does not claim that the host's remaining preferences are all replaced with hardcoded defaults. Original guest NetPlay save staging is retained; guest saves do not overwrite normal offline saves.

GameCube profiles must provide all four GC port entries; Wii profiles must provide four **emulated** Wii remote entries. Each entry is an authenticated slot or zero, not a guessed native PID. The native bridge resolves slots to connected PIDs and requires the mapping union to equal the authenticated roster. Official DesiredWiimoteState carries configured Nunchuk, Classic and MotionPlus state; their input configuration is retained, not arbitrarily removed. Code coverage is not physical compatibility validation of every game/controller. Remote GBA and real Wiimotes are not enabled by this profile.

## Framing and delivery

Station `station-stream.v3` host-star DATA contains one complete DPL1 datagram:

```
offset 0: "DPL1"        4 bytes
offset 4: source slot   uint8 (1..4)
offset 5: target slot   uint8 (1..4)
offset 6: payload size  uint16 big-endian
offset 8: ENet UDP datagram, 1..1392 bytes
```

Only host↔guest links are accepted. No guest-to-guest route is created. Native send/receive wrappers preserve packet boundaries, synthesize loopback peer addresses, and bound pending bytes to 256 KiB per link/endpoint. The real core/ENet still performs its own protocol, channel, and controller processing.

`nativeDeliver` returns 1 when accepted/idempotently queued, 0 for temporary attachment/backpressure, and -1 for invalid identity/frame. **1 is not a Station delivery ACK.** Call `nativeAwaitDelivery` with the same unique ID; true proves the entire datagram was copied to the actual ENet receive operation. Only then acknowledge the outer DATA byte offset. IDs must be unique across links. Preserve outer replay deduplication even after a consumed native receipt is removed. False on a bounded wait means keep waiting; it does not authorize closing or rebuilding the engine.

## Recovery barrier

- Immediately on authenticated paused state or WSS loss, the control thread invokes `nativeSuspendTransport(epoch)`. This call is independent of a blocked Connect. It freezes virtual ENet time and requests CPU break, but **does not prove CPU idle**.
- The session worker invokes `nativePauseAtEpoch(session, epoch)`: requests CPU break, wakes native input waits, synchronizes CPU idle with `PauseAndLock`, and retains the exact epoch. No game frame is advanced to flush MODE or drain transport.
- Drain complete DATA delivery receipts, native queues, outer send queues and all server link windows. `nativeDrained` alone is insufficient for the global barrier.
- Publish each accepted control using `nativeControl(epoch, serial, pause)` immediately. Serial is positive and strictly increases for every accepted Java AtomicReference revision, including same-epoch controls. An older serial is rejected; it is supersession, not a fatal engine error.
- Report READY/pausedAtEpoch only after native pause ACK and global contract prerequisites. Invoke `nativeResumeAtEpoch(epoch, serial)` only for a fresh signed, exact-epoch global state with `paused=false` covering all expected links. The native transport rechecks the latest exact serial/epoch/permit under its mutex; a newer same-epoch pause blocks an older resume. A short CPU break/run arbitration prevents an obsolete pause from breaking the CPU after a newer successful resume.
- `nativeFail` is independent of Connect, accepts only a small categorical diagnostic, freezes the core/ENet, and makes resume impossible until explicit human teardown. It does not close a running engine.
- Boot/unpause CPU requests are retained behind the gate. ENet timers exclude suspension time. A real ENet peer reset is a permanent native failure: pause and show a meaningful error; do not pretend the old peer can resume or silently create a new peer.

Status flags: ACTIVE 1, HOST 2, CLIENT_CONNECTED 4, SERVER_CONNECTED 8, CORE_RUNNING 16, CPU_STEPPING 32, SUSPENDED 64, FAILED 128, LOCAL_DRAINED 256, EXACT_HOST_ROSTER 512. CORE_RUNNING includes normal paused cores. Only successful pause ACK establishes CPU idle.

## Human exit

Automatic ENet loss, received Stop/Disable packets, native client stop helpers, Android stop callbacks and `Core::Stop` are gated while Station is active. They record failure and suspend; they do not terminate the emulation session. The unchanged offline core is unaffected.

Only the explicit human Exit/Cancel action invokes `nativeAuthorizeHumanExit(session)`. Then close transport to cancel a pending Connect, await its worker, release the official session using `closeBlocking`, stop emulation, return RESULT, and terminate the exclusive process. Never release native session pointers while Connect or another operation is using them. A new normal launch uses the original library in a fresh process. Never restart or terminate an already active offline game to obtain exclusivity.

## Server contract

The existing v3 opaque DATA relay does not need to interpret DPL1. It needs immutable Dolphin GC/Wii engine identities and compatible catalog/controller profiles with the exact final binary/options hashes. The inspected server snapshot had no GC/Wii v3 engine/profile records. Legacy EngineRegistryFile is not a substitute; it only accepts the legacy/v2 registry. No server service was deployed, restarted, or verified by this candidate.
