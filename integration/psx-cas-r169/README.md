# R169 — PSX compare-and-set call repair

R168 reaches the private PSX transport, then its DEX35 calls a method that its
own synthetic helper does not define. The caller requests
`m(AtomicReference,Object,Object)Z` from the synthetic helper for
`StationSinglePassVideo720$2`; that helper only defines
`m(AtomicReferenceArray,int,Object,Object)Z`. Android consequently throws
`NoSuchMethodError` on `WebSocketConnectReadThread` before gameplay.

`StationPsxSession.java` already says `desired.compareAndSet(old,next)`. The
R169 recipe replaces one compiled DEX instruction with the direct Android
`AtomicReference.compareAndSet(Object,Object)Z` call. Its existing outer loop
handles a false return. It changes three instruction bytes, then recalculates
the DEX header checksums. No session, transport, UI, N64 or background behavior
changes.

Run `recipe/patch_dex.py` against the exact signed R168 donor. It produces only
an unsigned `classes35.dex` and a scope receipt in a new isolated output
directory. Every other byte of DEX35 outside its header and all other 39 DEX
partitions stay intact. A successor APK requires separate
package, signature, engine identity, server registration and physical testing.
