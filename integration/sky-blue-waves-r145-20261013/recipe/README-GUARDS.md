# R145 packaging draft

Workspace preparation only. These recipes require the reviewed scope at
`integration/sky-blue-waves-r145-20261013` and a new full Git source commit.
The preparation directory deliberately cannot satisfy the productive source gate.
No old R144 source, package, device or server state is changed by this draft.

## Exact donor and changes

- R144 APK SHA256 `01427f4e73141b7d6a462c2420a9abeb018a8716102e7fb959bf9a1d69eccee0`, 2,715,024,399 bytes.
- Three DEX partitions: 28, 35 and 40. Actual donor counts 272/608/129; 1,009 classes accounted for.
- Seven classes and nine specified UI methods; ten exact background literals. Whole class/method inverse must recover the real donor.
- 37 other DEX partitions remain exact. DEX35 is no longer described as entirely unchanged: only the explicit UI background constants may differ; all gameplay/network methods and R143 repairs remain qualified by the inverse guard.
- Native carousel requires complete byte reproduction of R144 `67180bdd145cd03f456249b31b9163ee0baa3e66fb10b909e20831823accea10` using the pinned parent receipt and all 158 inherited inputs.
- Only the requested native sky backdrop, system palettes, band counts and widths may differ. Native loop/count/width changes are permitted; claiming the entire wave drawing function is unchanged would be incorrect.
- Bands are visual decorations, never a declaration of multiplayer capacity.
- Exactly eight APK replacements: DEX28/35/40, carousel, engines asset and three identity wrappers. 13,852 of 13,860 entries remain exact; no entries added or removed.

## Required producer contracts

`build_identity.py` contains the exact validators for the two producer receipts.
The DEX producer uses schema `station.r145.sky-blue-waves.dex.v1`; the native
producer uses `station.r145.native.sky-blue-bands.v1`. Source and declaration
pins must match the same newly frozen commit. Source-only review cannot stand
in for compiled DEX inversion or native donor reproduction.

`build_identity.py` and `assemble_apk.py` require `--dex-dir`, `--dex-receipt`,
`--native` and `--native-receipt`. The three DEX files must be directly under
the explicit DEX directory, with their original filenames. Final verification
requires those same inputs as well as `--base`, `--apk`, `--receipt`, the pinned
signature/alignment tools and an unused `--out` proof path.

Independent PSX/N64/GameCube/Wii IDs are renewed because all 345 payload hashes
are mandatory. Original owner policies, controller profiles, cores, libraries
and nine RetroArch descriptors are preserved. This does not apply a server kit,
approve new modes or solve the separate online investigation.

## Remaining gates

The root must review/stage the complete producer sources and all consumed
evidence, freeze a new source commit, reproduce native R144, assemble the three
DEX partitions and pass the exact inverse/class preservation checks before
these packaging recipes can accept any candidate. No productive build,
signature, installation or performance/visual acceptance is claimed here.
