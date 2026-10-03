# Station: continuous cover delivery, 03 October 2026

## Base and scope

Source copied from frozen app commit `97938400d3fa82d5d1564445c36fc70328add1c4`. The installed HUD R2 retains the stable Station DEX/native bridge. This source does **not** import the separate 40,000-item candidate; maximum catalog remains 4,096.

Build root: `E:\ESTUDO APK\work\station-visual-covers-20261003\station`. No server change, APK packaging or phone action was performed by this task. Artifact identities and exact validation scope are in `build/cover-delivery-result.json`.

## Behavior

- `StationCoverQueue` has four actual workers, a bounded waiting queue, item deduplication and immediate replacement as each operation completes. There is no 2,100 ms interval or other pacing after success.
- `StationCoverStore` caches existing `<coverId>-<revision>.img` files persistently, validates contents, commits with the existing atomic writer and locks only the individual cache key during image IO. Short locks protect bounded metadata maps. Different images transfer concurrently.
- Native `queueCovers` maintains four pending operations. `station_cover_plan.hpp` preserves the renderer's visible priorities, then prepares all remaining items of the same selected platform and folder in order. A completed response immediately resets the sweep; the one-second exhausted-plan check performs no successful-request pacing. Texture rendering and Item/Catalog ABI remain unchanged.
- Hiding the frontend cancels active and queued images and stops native submission. Cancellation is distinct from missing artwork and can resume immediately. A failed image does not permanently stop following images.
- `images.invalidate()` runs before publication of a catalog replacement. Each task captures a generation. A stale completion is converted to cancellation, so previous-revision artwork cannot overwrite the current catalog. A short publication monitor orders completion/removal/new requests and avoids lost wakeups.

## Sessions and grants

The server revokes earlier sessions on renewal. `StationSessions.Lease` counts active users; renewal waits until all users release. Login/profile/catalog, covers and the download authorization-to-GET-header window pin the same bearer. No global cover monitor is held through its network request. A download retains its lease through local reuse checking and GET acceptance; its potentially long response body may then run alongside renewed sessions and other covers. Late denial only clears the matching rejected session, never a newer one. Authentication, signature, TLS pin, IDs and grant one-use semantics remain intact.

## Errors and rate limit

Server return `54bba11c52f35695fd47eabc7145f42af9990426` reports API commit `4bb77ed2b8fb01fe967b90dc18ec3fbd1ee5d58b` published in production. Its current cover budgets are 4,096 requests/minute per license + device and 16,384/minute per origin; renewal does not reset the device budget. Activation, sessions, download authorization and artifacts retain their separate 30/minute/origin budget. The old 30/minute cover policy is historical. Current reported catalog revision is 4 with 1,816 public games. The server measured 48 covers, four at a time, with HTTP 200 and exact bytes in 4,546.55 ms over HTTPS from Linux. These are reported server results; this task did not measure production or the phone.

The client assumes no new endpoint or JSON field. A successful response has zero deliberate wait. On a real 429 the optional standard `Retry-After` response header accepts seconds or HTTP date; absent/invalid headers use 60 seconds. Parsing is bounded to 24 hours. Cache hits remain available during backoff. Native speculative prefetch pauses globally until that deadline; only bounded visible priorities can consult local cache. A successful sibling request cannot shorten the backoff. 404 is per image and retried after 60 seconds. Other transient failures use two seconds. Background/user cancellation has no failure cooldown.

## Comparison with upstream client 1dc8c381

Read-only comparison used TurboElden commit `1dc8c381e49e60ccbe0f84c97dcfe5be3e1d85f3`, branch `feat/station-transfer-speed-20261003`. No cherry-pick, checkout change or upstream build was substituted for this stable-based source.

- Ported `StationHttp` response reuse: reaching EOF with the announced Content-Length satisfied (or an unannounced length) permits the platform connection pool to reuse the completed response. Partial, truncated, failed or cancelled responses disconnect before close. A failed close also disconnects. Certificate trust, hostname validation, SPKI pinning, response validation and redirect rejection remain active. Local tests prove the close/disconnect policy; actual Android TLS reuse and its speed still require device measurement.
- Ported `StationExistingArtifact` exact-name priority: verify the signed size and SHA-256 of the exact target before any directory walk. A wrong hash may use the existing bounded fallback search. Total eight-candidate and hash-byte budgets, depth six, 4,096 visited entries, no-follow rules and cancellation remain enforced. Tests use a deterministic directory-walker seam to prove valid exact files avoid traversal entirely.
- Retained this implementation's borrower-count session leases. Upstream snapshots session/catalog outside the global lock; this implementation additionally prevents session renewal from revoking concurrent cover requests or the download authorization-to-GET-header window.
- Retained explicit native cancellation completions and generation guards. Upstream's pending-cover reset around deferred catalog publication addresses its dropped cancellation callbacks; here cancelled tasks publish CANCELLED and release native slots even while an active download defers catalog application. Its nine native lines were reviewed but were not applied over this behavior. No native ABI or catalog capacity change was needed for this follow-up.

## Native and Java contract

Private callback `publishCoverResult(itemId, pathBytes, result, retryMillis)` carries success, cancellation, transient failure, missing image, rate limit or authentication denial. `publishForeground(boolean)` controls native submission atomically. The old native publishCover export remains only for the existing isolated JNI fixture. No renderer ABI field or legacy HTTP route is added.

`StationFrontend.installedPathsFor(String platform)` is a separate local helper requested by the Netplay integration. It requires a background thread and authorized initialized catalog, resolves existing platform aliases, reads verified installed receipts and returns launch paths. It performs no HTTP or guessed-directory scan. Missing readiness throws IllegalStateException; an empty array means no verified installed files.

## Build and evidence

384 host checks passed on the final `1.0.8-station-covers-20261003.4` sources: 368 existing checks plus 16 TLS-response/exact-artifact checks. Coverage includes four simultaneously entered synthetic HTTP requests, automatic eight-item refill, persistent cache after reconstruction, same-key deduplication, four-reader session renewal, artifact-header versus body races, cancellation/foreground resume, 429/Retry-After, 404 isolation, rejected-session recovery, late old-session invalidation and old-catalog result cancellation. The new checks cover EOF/length eligibility, partial/truncated/cancelled/read-failed/close-failed responses, exact-file lookup without traversal, cancellation and fallback budgets. Eighteen C++ native prefetch/retry policy checks passed on the host. Full Java source compiled against Android API 34, D8 min API 26; native bridge compiled arm64 with NDK r28c and 16 KiB alignment.

The upstream follow-up changes Java only. Native `libstation_frontend.so` remains SHA-256 `4da25d5bc91d74628944b6a8ec1d8b5fdc31c7dff8314852b05164a164676ed2`. Final native/DEX identities are authoritative in the receipt. These are local synthetic/build results, not proof of live-server throughput or device rendering.

Reproduce with `run_tests.py`, `build_frontend.py`, `build_module.py`; build defaults are this isolated tree. Existing SDK/JDK/NDK and test JSON jar paths remain prerequisites. Replace only classes28.dex and libstation_frontend.so in the exact HUD R2 base when parent packaging assembles this change alongside its other features. Preserve signer, package, data, licenses, games and saves.
