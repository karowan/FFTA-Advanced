# Five further native color effects — September 18, 2026

Follow-up to `f8aa286`. Current private candidate is
`f637b43f4e7f9cffd2a997dc9b408ce074e2fd01`, resolved through
`build/art/live-palette/poc.json`. Stage158652 bytes, state8096 unchanged.
No installed package, launcher, player save or session change. Built-in imagegen
only; final sprite refinement remains deferred. All G gates remain open.

## Installed behavior

| Original setter | Behavior | Generated conversion |
| --- | --- | --- |
|08147D94|Weighted mix with one RGB555 color|Original pure08147830;16-bit color and8-bit weights. |
|08147EC8|Brighten by a supplied fraction|Original pure081478DC;8-bit amount. |
|08147F50|Darken by a supplied fraction|Original pure08147958;8-bit amount. |
|0814731C|Uniform exposure-style multiplier|Raise each current channel to at least3, then original08148384 with one16-bit coefficient for all channels. |
|081473E4|Per-channel exposure-style multipliers|Same immediate source floor, then original08148384 with three16-bit coefficients. |

The exposure names describe the observed arithmetic, not recovered native symbol
names. These setters change the native starting shadow before interpolation;
the generated binding now changes its own current colors and contiguous display
source at that same boundary. The hardware latch remains governed by native DMA.
Targets, interruption and remaining callbacks use the existing exact fade primitive.
Baseline identity remains available for the explicit palette-restore operation.

All five use the previous late-entry tracking. No state, save schema, resource
ID or palette capacity change. Native/unowned colors still come from the original
setters. Partial banks, unknown table targets and duration above255 retain their
explicit refusal boundaries.

## Verification

Runner `20260918T090522.809485Z` on currentf637:

| Test ID | Checks | Scope |
| --- | --- | --- |
|test-native-art-extended-colors|13000|ARMv4T actual installed setters versus original engine using native and generated sources. Exact immediate sources/targets, every callback, interruptions, duration0/1/8/17, both stack alignments,8/16-bit argument truncation, boundary/unowned refusal, native state and outside gameplay memory. |
|test-live-art-extended-colors|854|Actual mGBA callbacks/hardware for all five, interrupted darken-to-exposure and final baseline restore; exact paired native/unowned colors and canonical units. |
|test-live-art-palette-native|1145|Authenticated installed entries, byte-exact rebuild and existing reservation checks. |

Reports:
`build/art/color-operations/20260918T090523.414180Z/report.json`,
`build/art/live-palette/fades/20260918T090539.469985Z/report.json`,
`build/art/live-palette/native/20260918T090547.071207Z/report.json`.
The per-channel-exposure midpoint screenshot was visually inspected; it remains
an unaccepted transport draft. Controlled setter inputs do not establish natural
campaign triggers or every scene lifetime.

Runner `20260918T090642.283879Z` passed expanded
`test-native-art-late-entry`4146 and `test-native-art-palette-binding`32.
Late-entry now includes all twelve implemented setters, normal/dim inputs and
first appearance at0/3/17 callbacks. Reports:
`build/art/late-entry/20260918T090642.907755Z/report.json` and
`build/art/palette-binding/20260918T090648.202084Z/report.json`.
The builder-only argument-preservation assertion was added afterward; a static
rebuild reproduced the samef637 bytes and refreshed source provenance. No broad
suite or repeated unrelated campaign/save test was justified.

## Failure retained and corrected

First candidate `eaa3c00f49f86436910602681e479ca5a2028887` failed at brighten0,
duration0, before any live run. Runner20260918T090408.073291Z and
`build/art/color-operations/20260918T090408.768414Z/failed.json` remain retained.
Three four-argument entries used an8-byte jump that overwrote r3. Corrected to
authenticated16-byte argument-preserving entry stubs and complete displaced
prologues. The builder now explicitly rejects short entries for every setter
that needs the fourth argument. All positive parameter/truncation and ABI checks
above exercise the corrected path; no failed result is counted as acceptance.

## Remaining native paths and next work

Static inspection of the original1465E8..148788 palette code identifies two
unhooked setters using the same146E54 fade setup:

-081474BC: exposure target from an explicit source palette table. It floors
  source channels in its calculation without writing that source table.
-08147E28: weighted blend target from an explicit source palette table.

Authenticate/remap known table sources per class and brightness, preserving
unknown-table refusal, all caller-stack arguments and original native outputs.
Their callback interpolation is shared with the now-supported twelve setters.

Other task constructors146FB8/147068/147124/1471E0 and wrappers147FD8/148034/
148084/1480C4, cancellation146DC8 and task-control helpers14846C..148738 need
separate lifetime/callback analysis. Palette rotation is not automatically a
generated-class operation merely because the existing native BG/OBJ phase
diagnostics pass. Direct conversion/copy consumers remain separately scoped.

Natural scene/heap/stack lifetimes, maximum mixed-class/variant capacity, all
remaining assets, native response/phase failures, final art and playable
packaging remain open. Reuse prior exact reload/deployment/transition evidence
where inputs and affected behavior are unchanged.
