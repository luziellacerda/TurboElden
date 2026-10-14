# R151: SNES border gaps and complete cover transition

R151 extends the R150 single-pass cover effect. It maps the four dark inset gaps on each side of the 5120 x 7680 SNES cover into the existing lamp field and clock. There is no second sweep, texture, timer, or per-frame draw.

The R150 cache initially rendered the exact region but refined the emitter and halo four rows per frame. On a new cover this could appear to form gradually. For the SNES model, R151 bakes the narrow field in one framebuffer draw when the cover changes and commits it before display. Other model cache quotas remain unchanged.

The package builder uses the exact signed R149 APK as donor. Only the carousel library, three scoped color DEX partitions, three runtime identity libraries, and the engine registry may change. The DEX and native single-pass overlay from R150 are reused byte for byte; this revision changes the SNES geometry and field preparation. Build receipts verify all 13,860 APK entries and preserve 13,852 unchanged entries.

The user-facing result still requires installation and a physical transition check across several SNES covers.
