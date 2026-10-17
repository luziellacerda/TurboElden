# R158 candidate: PSX and Mega Drive selected game covers

Base: owner-approved R157 (`563625c40bfce77def6770a67448f83e2206e67a07023c58359ad2a0de4eee34`).
The R157 native carousel is reproduced byte for byte before applying either
artwork map. The attached PSX and Mega Drive images are measurement references;
they are not bundled in the APK.

The PSX covers have common red side rails at logical x 8–39 and 984–1020,
two red bars under TURBORAMA, the red top of the PlayStation P, narrow outer
header/lower contours, PlayStation lettering and a red neon download panel.
The lower contour follows two measured paths outside the CD case. Its former
wide rectangular mask reached red details inside the CD artwork; that mask is
removed. The old PSX map sampled x 52/970 in the artwork and sometimes
remained active on the new covers. One shared model-8 PSX map now selects only
these frame elements using the artwork's red/white pixels; the old PSX map and
the 8.25 subprofile are removed. There is no separate whole-cover brightness
test for PSX, so the darker Alien Trilogy rails use this same map. The existing
SNES complete-on-selection field bake removes the four-row build-up. Red-channel
energy feeds the same SNES light equation, with the existing light clock set to
five passes per 625 frames for PSX only. No second effect loop is added.

The Mega Drive artwork has blue rails at x 15–44 and 983–1012, y 193–1223.
Its blue top rim, blue TURBORAMA lettering, the upper SEGA name and two lower blue controls are
included in the same light field. The title region is a box for coarse
geometry only; the existing blue pixel detector illuminates individual blue
letters, not a solid rectangle. A rail and title signature selects subprofile
1.25; other Mega Drive covers retain model 1. Mega Drive also uses the SNES
complete-on-selection field bake. The new profile feeds the blue channel into
the same light equation, including the blue TURBORAMA letters.

The follow-up visual candidate lights the measured upper SEGA letters at
logical x 777–908/y 40–89. Its existing sweep advances four times per 625
frames instead of three and lets the peak rise above the resting glow. The
existing SNES 16-vertex, 1.8% corner strip is reused by every selected game
cover, including PSX and Mega Drive. The touch boundary uses the same radius.
System carousel corners retain their own shape. This revision remains a visual
candidate pending physical approval.

Both maps reuse the existing selected-cover shader, static field cache,
single draw, and light clock. No new timer, thread, texture or per-frame draw
is introduced. Only `magazine_shader.h`, the field-bake policy in
`native_magazine_field.h`, and selected-cover geometry in `native_formation.h`
change. All APK entries except the carousel, its
three bound runtime markers and `engines.json` must be byte identical to R157.
R157 remains the stable rollback until physical approval.

## Current test package (14 October 2026)

The current candidate is `E:\StationVisualR158UnifiedPsxFinal-20261014\final-v8\TurboStations-Premium-R158-psx-sega-cantos-20261014.apk`, SHA256
`fc1d2d983deb5179979a4aebac7fa64b1740da1c62ae46bfc0d1f4c11eb46cf0`.
It is signed with the original certificate and installed on the Galaxy A56 with
data preserved; see `recibos-usb/instalacao-20261014T204327609Z-4589c2a3.json`.
The Edge 30 was detected by the installer on USB without a repeat install.
The visual result on the physical phone still awaits user confirmation.

The EXE in `final-v8` contains the current installer. It detects the USB phone
at opening, confirms the APK before installation, displays measured percentage
while hashing the APK in one pass, and shows an indeterminate bar with the
current stage while Android installs or verifies it. It uses the same PowerShell
backend and does not change the app or its runtime cost. The manifest pins the
APK hash; see `evidence/usb-installer-r158.json` for exact installer hashes and
the detection/validation checks. No final-v8 APK was installed on the Edge 30.
