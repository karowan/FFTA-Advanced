# Palette-plan reuse trial — September 18, 2026

Follow-up to `da16841`. **Rejected for adoption:** a correct cache hit is slower
than the existing planner in the actual mixed battle. The implementation is
removed from production source. Current palette `5eff9a7044165dd639d47163b44e8f315a722ddd`
and connected `4a7d55ce09cd4a40965a0bb97de2701d276789c5` rebuild byte-exact. The
installed preview, launchers, player saves and session are unchanged. G01–G04
remain open; built-in imagegen only, final sprite refinement deferred.

## Implementation and bounded correctness

The trial added a 948-byte planning key inside the existing 12 KiB graphics
reservation. Total live state was 12,260 bytes, with twelve bytes remaining
before the separate sixteen-byte battle-menu heap root. No heap boundary moved.
It compared the prior plan, mapping mode, history count, object ownership and
relevant OAM attributes. Every required visible 8bpp tile was compared byte for
byte against the existing cache; missing entries, larger footprints and aliasing
between objects fall back to ordinary planning. No hash or palette-mask-only
equivalence was used. Current native colors were always backed up and current
displayed custom colors reapplied, including repeated native frames.

First trial palette `d4127f37` / connected `e8de1d97` used complete attributes.
Actual Move had only 45–46 hits among 127 measured transitions and lasted56–57
frames. The revised key excluded attributes that the original planner does not
consume, such as custom-body position/animation tile and unowned4bpp position.
It still accounted for disabled/affine/mosaic/shape/size, native bank occupancy,
8bpp geometry/source bytes and ownership. The first revision `ce7fc32d` failed a
real correctness check: disabled and enabled native bank-zero objects could
have equal keys. A distinct disabled marker fixed that collision. Neither
failed version is accepted or substituted for the final trial.

Final palette `8c988cf27b7bc11bbdb139cd2b501e5a230bc8cd` assembles to connected
`f48949dc677d4e2cd95eb3e278bc845b8e300c4a`. Its component test passes10,714 checks,
including every bit of every OAM attribute against the original function,
every visible byte across32 cached tiles, all owner/plan/cache-valid changes,
current native/custom colors, exact native backups, high history slots,
clipping/flips/affine/mosaic/larger footprints, multiple8bpp cache aliasing,
read-only validation, failed-plan invalidation and reset of an existing valid
key/counters. Full private rebuild/native clear checks pass9,814. These are
component and lifecycle claims, not battle-entry/timing/art acceptance.

## Actual matched-state comparison

Both actual entry tests fail the paired native palette-shadow comparison at
`candidate/ready`, after47 checks. Their complete captures remain retained.
This checkpoint does not reconcile or waive those phase failures; later entry
assertions were not executed.

The final timing comparison uses the final trial's own captured state, with
fresh cores and identical navigation in both branches. The private control
changes only the first eight bytes of aligned `ffta_art_palette_scene_apply`
to a Thumb jump into the same ROM's original `ffta_art_palette_live_apply`.
It keeps every native/custom graphics consumer enabled. The jump adds a small
control overhead; it is not literal byte/cycle identity with the older ROM.
The control never reads or updates the rejected scene cache.

`test-art-plan-key-frame-events` passes1,073 diagnostic checks. All1,024 observed
complete native states and framebuffers match ordinary emulation. Ordered
logical motion and canonical roster/inventory/AP are unchanged. Raw input,
palette phase, native frame, cycles and cache counters are retained without
alignment or normalization. Frame zero contains the first held input, including
eight press frames; each action then has120 idle frames.

| Extra idle | Trial Move start/end/duration | Original planner control | Trial/control cancel return |
| ---: | --- | --- | --- |
|0|25 /80 /55|25 /77 /52|33 /32|
|4|25 /80 /55|25 /76 /51|31 /32|

The corrected key reaches113 hits/14 misses during Move and116/11 during cancel
(127 transitions, excluding the first frame). Despite those89–91% hit rates,
composition averages35.56–35.63 scanlines for Move and34.69–34.85 for cancel,
versus29.88–29.92 and28.55–28.57 for the original planner. Even hit-only means
are34.76–34.85 and34.04–34.21. The cost of validating the key outweighs the
planning saved. Move is3–4 frames longer; cancel is one frame worse at offset0
and one frame better at offset4. Rejection does not depend solely on the
unresolved entry-phase assertion or on cross-ROM timing comparisons.

Use `scripts/summarize-art-frame-events.py` on the retained final report to
reproduce those statistics without another runtime. Cache-counter statistics
exclude the first observed frame, whose prior counter is outside that action's
record. Do not label the control's non-hit frames as cache misses; the cache is
bypassed completely there.

## Runs and failures

All runtime work used the declared native-art plan through `Test Expansion.ps1`,
with IDs and purposes announced. All runners are terminal. Dates are20260918;
child paths below are relative to `build/art/`.

| Step / runner | Child evidence | Result |
| --- | --- | --- |
| initial component /194408.241356Z |plan-reuse/20260918T194408.853360Z/failed.json|**Failed fixture:** encoded32×16 but expected64×32; first unrelated byte correctly did not invalidate.|
| complete-key component /194448.323852Z |plan-reuse/20260918T194449.003875Z/report.json|5,320|
| complete-key native /same |live-palette/native/20260918T194449.319751Z/report.json|9,814|
| complete-key entry /194630.327027Z |live-palette/battle/20260918T194631.056358Z/failed.json|**Failed** native phase after47 checks.|
| complete-key event trace /194804.671381Z |native-frame-events/20260918T194805.391353Z/report.json|1,071; composition-bypass control, not original-planner control.|
| extra reset component /same |plan-reuse/20260918T194813.889132Z/report.json|5,322|
| reduced-key component /195029.747083Z |plan-reuse/20260918T195030.354831Z/failed.json|**Failed implementation:** object127 attr0 bit9 exposed disabled/bank-zero collision.|
| corrected component /195118.934529Z |plan-reuse/20260918T195119.638434Z/report.json|10,714|
| corrected native /same |live-palette/native/20260918T195121.226278Z/report.json|9,814|
| corrected entry /195221.332712Z |live-palette/battle/20260918T195222.114342Z/failed.json|**Failed** native phase after47 checks.|
| original-planner comparison /195411.059083Z |native-frame-events/20260918T195411.768283Z/report.json|1,073 diagnostic checks; timing regression retained.|
| retained compiled component /195718.209174Z |plan-reuse/20260918T195718.852973Z/report.json|10,714 after production source restoration.|

Fail-fast skipped the native step after each component failure. A first
connected-build invocation lacked the scripts import path and stopped before
assembly; the corrected invocation assembled successfully. No failed run is
erased or converted to a pass.

## Recovery and next boundary

The rejected five-file implementation patch is private at
`build/art/plan-reuse-trial/8c988cf27b7bc11bbdb139cd2b501e5a230bc8cd/rejected-source.patch`,
SHA256 `6248864c2e350746fe6cc196190907546b6d6b9a65562be5c94b7284edec4b7b`.
It preserves the builder flag, implementation and native rebuild adapter.
The retained component test explicitly takes the immutable compiled manifest;
it does not compile or enable the removed source. Rebuilding this rejected
trial requires its patch in an isolated checkout, not the restored builder.
The former native-rebuild test ID is removed from the active plan for that reason;
its terminal reports above remain evidence. Trial entry/trace IDs pin their
exact compiled candidates and states.

Production source was restored before rebuilding the current private candidate.
Restoration report:
`build/art/connected/rebuild/20260918T195706.168417Z/report.json`.
Current metadata was refreshed only after checking exact connected4a7d55ce;
no installed build, launch or player-save operation occurred. Reuse the existing
Status/world-menu and other applicable evidence; no broad suite was justified.

Do not repeat whole-frame key caching based on hit rate. Its hit path is the
measured problem. Next use the proven observer to identify the native foreground
subroutine/task intervals responsible for the long update spans in the restored
candidate. Also distinguish actual palette writes from native scheduler phase
before treating another entry-phase difference as a graphics corruption claim.
Any reconciliation must preserve raw failures and supply direct native-event
evidence; do not weaken a check simply to admit a faster trial. Larger encounter
and effect capacity, remaining natural consumers, final assembled acceptance
and reproducible playable delivery remain open.
