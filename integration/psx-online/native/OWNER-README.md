# Original PSX owner adapter — isolated current work

This adapter hooks the original LibretroPlayer SDL owner only in a separately authorized PSX online process. It changes four in-memory GOT entries after verifying original owner/core SHA256 and their actual loaded executable segments. Neither original file is patched. This directory is the single temporary source/build tree; it is not an APK or a migrated productive route.

## Real boundary

`SDL_GetPerformanceCounter` return PCs `0x2ae600` and `0x2ae61c` bound the original native pause check and original `LibretroCore::run`. The checkpoint temporarily sets the original pause byte while waiting, keeps the original SDL loop/render/pacing responsive and permits only a real protocol lease to enter the core. The wrapped real `retro_run` emits the execution result only after returning. Network threads never call the core. A failed/missed lease is aborted without an executed commit.

CoreReady runs only after the original owner has loaded the game, installed the exact callbacks, validated the 59 compiled V2 defaults and read the real serialize size. RendererReady/CoreReady are preparation facts; they are not CPU pause ACK or READY. The real epoch/serial pause ACK, applied initial state, link drain and absence of native local menu pause are all still required.

Original SDL/touch/controller input is sampled once per protocol cursor. The signed productive PXL1 profile uses delay4: input sampled at N is scheduled for N+4, and only the first four synchronized frames after actual state/Ready use neutral pads. Original ports0/1 keep standard button IDs0..13. This neither enables analog/multitap nor changes user offline preferences.

Native local pause invokes the nonblocking local-pause callback. Java must withhold READY/resume and request the global barrier while it is true. The original menu save/load/exit rows are disabled before their effects. The separate Java human confirmation is the sole authorized exit; SDL_QUIT, core SHUTDOWN and lifecycle failures do not grant it.

## State and storage

Only the actual owner may serialize/unserialize. State length must equal the actual loaded core size (1..16MiB), and apply succeeds only on exact SHA/identity/epoch/serial plus a successful original callback. The protocol validates identity and state before the decoder; this does not prove nested decoder memory safety. Home/system/save directories are fresh confined session paths. HLE BIOS plus two Standard pads requires per-ROM approval; it is not a claim of universal PSX compatibility.

`CoreReady` returns a non-owning Session pointer. Its owner must retain it until all IO/JNI workers stop/process teardown. `ownerClose` marks it closed; it must not destroy the object beneath workers. Callback spans remain valid and immutable through callback return.

## Recipes and evidence

`probe_owner_abi.py` verifies the pinned original ELF call sites/GOT/21 actual dlsym names. `run_owner_probe.py` compiles the actual adapter implementation in an explicit host-fixture mode and exercises real Session integration with mock SDL/core callbacks; that mode cannot install hooks and is never packaged. `build_owner.py` compiles ARM64/API28 with 16KiB alignment, RELRO/NOW and no undefined symbols. Receipts are aggregate and contain no personal paths.

No Android process, ROM, physical gameplay, controller operation, thermal measurement, phone installation or server activation has been performed by these proofs. The offline original owner/core, frozen R126 and last installed R124 remain unchanged.
