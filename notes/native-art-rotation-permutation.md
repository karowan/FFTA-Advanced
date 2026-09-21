# All-class first-visible rotation fix - September 18, 2026

Follow-up to31aa28d. User direction remains built-in imagegen only, technical
end-to-end integration first, final sprite refinement later. No new artwork,
external provider, publication, agents, game launch or installed package change.

## Current candidate

`6443725d256252afae127393945934961eb9abd6`, resolved through
`build/art/live-palette/all-classes-workspace-current.json`. Build with:

```powershell
& $fftaPython scripts/build-live-art-palette.py --history-slots 20 --all-classes --workspace-low-address --provisional-history --fast-rotation
```

Use the Python runtime declared in `Test Expansion.ps1`. Stage243876 bytes,
state11312, same12KiB RAM reservation and all-class mask1023. The existing
authenticated imagegen drafts and repeated transport poses remain unaccepted
production artwork. Default builds without the new flag retain old code.

`ffta_art_binding_rotate` previously shifted every color, target, interpolation
error and delta once per native step per matching history. The optional path
reduces steps modulo the range width, then moves each complete record once using
permutation cycles. Literal feed shifts only colors and fills the vacated range;
targets/errors/deltas remain untouched. Zero steps, one-color ranges, wrapping,
partial ranges, direction, active/inactive fade records and ABI are preserved.
There is no division helper, heap allocation, new state or history eviction.

## Passing evidence

Declared runner `20260918T122732.620056Z`, all three steps passed:

- `test-art-rotation-permutation`:168 whole-state comparisons with the prior
  f36376de compiled function. Twenty simultaneous histories, both directions,
  feed/no-feed, steps0/1/3/10/16/17/33, widths1/10/16, stack residues0/4,
  complete colors/targets/errors/deltas/display buffers/counters and fences.
  `build/art/rotation-permutation/20260918T122733.304194Z/report.json`.
- `test-live-art-workspace-native`:9797, byte-exact rebuild, native metadata,
  authenticated pixels and clear/reset boundaries.
  `build/art/live-palette/native/20260918T122733.584923Z/report.json`.
- `test-live-art-workspace-late-rotation`:1595, all eight actual rotate/cycle
  first-visible scenarios, active/completed phases and exact unowned hardware.
  `build/art/live-palette/fades/20260918T122737.239482Z/report.json`.

This closes the specific full-mask first-visible delay retained in the previous
checkpoint. No mask reduction, phase waiver or changed comparison was used.
Prior native rotation/dispatcher oracle evidence and unchanged heap/ownership/
mixed-entry evidence remain applicable within their existing scopes.

## Battle movement still fails

Declared `test-live-art-workspace-movement`, runner20260918T122830.087049Z,
failed at `ready full native palette shadow unchanged`. Actual complete Move
and cancel were retained before the fail-fast comparison:
`build/art/live-palette/battle/20260918T122830.712620Z/failed.json`.
The existing offline audit examined all1205 samples in `trace-audit.json`.

Both native shadow and unowned hardware phase mismatch in all1205 samples.
Move starts16 versus15, ends63 versus62,47 moving frames in both. Cancel starts25
versus22. Generated hardware colors, canonical units, memory fences, native
executable IWRAM and VBlank checks pass; maximum display line201. There are no
new unsupported operations, missing overlays or allocation failures. This is
not timing acceptance or a completed battle.

`test-art-rotation-only-compose-cost` reuses that exact-ROM ready state with
only the native compositor entry restored in a private control. No new fixture
or cross-ROM animation-pointer replay. Runner20260918T123407.611811Z;30 checks,
`build/art/compose-cost/20260918T123408.229113Z/report.json`. Active versus
bypass: Move16/63 versus16/63; cancel25 versus22. Diagnostic only.

## Rejected allocation-preparation trial

Private `ea499f7f734fdd5f4d5575d9e3d551f765c7b436` deferred absent baseline
eviction checks when every requested identity already had a history slot.
Invalid source-key checks and actual allocation/retention behavior remained.
Its component115 and rebuild9797 passed in runner20260918T123137.190993Z:
history-capacity/20260918T123137.804821Z and
live-palette/native/20260918T123138.649683Z.

Movement still FAILED in runner20260918T123214.384352Z:
`build/art/live-palette/battle/20260918T123215.060479Z/failed.json` and its audit.
Both phase comparisons fail1205 times; Move17/64,47 moving frames, cancel24.
Matched-state `test-art-fast-prepare-compose-cost` passed30 diagnostic checks
in runner20260918T123407.611811Z, report
`build/art/compose-cost/20260918T123411.259558Z/report.json`:
active versus bypass Move17/64 versus16/63; cancel24 versus22.

Across1200 retained active samples, prepare/plan means were1.566/11.892 scanlines
for6443725d and1.740/12.018 for the trial. Separate starting phases limit this
comparison; it establishes no reliable improvement. The trial source is removed.
Preserved private patch against31aa28d (includes the accepted rotation change):
`build/art/fast-prepare-trial/ea499f7f734fdd5f4d5575d9e3d551f765c7b436/rejected-source.patch`,
SHA256 `1e9d2b3347c3175e3d40276df882abbe8b15cec1d95e3d0f6c6f52b894cee5b5`.
Rebuilding after removal reproduced6443725d exactly. The removed trial test ID
remains in its runner's captured plan; the pinned cost diagnostic stays callable.

## Continue here

Remaining timing is primarily compositor work, with a separate entry-phase
difference even in its bypass control. The latest matched-state cancel delta is
three frames. Investigate native ownership/planning cost or the native display
schedule with these exact retained states; do not repeat the rejected preparation
trial or count fewer instructions as demonstrated timing improvement. The cost
reader now uses manifest RAM/profile offsets, including20-history layouts.

Samurai/Moogle mixed deployment, natural action/water/effect lifetimes, cross-bank
effects, worst-case heap, remaining assets and final delivery remain open.
All G01-G04 gates remain open. Installed preview, vanilla, existing player saves
and running session are unchanged. No broad integration suite ran.
