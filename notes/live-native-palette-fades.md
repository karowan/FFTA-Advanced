# Live native palette fade bindings

September 17, 2026 local. Previous checkpoint 496e86e was progress. This
continuation installs the previously isolated fade primitive for a bounded
set of real native effects and verifies callback-to-hardware playback.

Current private candidate: `267d310f031d375f513548a95ef94660e79cc3ad`.
Resolve `build/art/live-palette/poc.json`. Parent remains 0fa7d170; the packaged
a6d883b5 build and player ROMs, saves, launchers and sessions are unchanged.
No new artwork, external provider, publication or game window was used.
All G gates remain open; the generated Dark Knight is still an unaccepted draft.

## Implementation and native ownership

New `art-palette-binding.c/.h` owns ten 252-byte binding records and a contiguous
generated-color cache. Each record contains the exact native-compatible fade
state, recorded native colors, original palette bank and native effect task
address. Before remapping OAM, the live compositor captures the original bank.
Only Dark Knight owner 1 remains enabled by this private stage's configuration.

Native entry hooks:

| Address | Purpose |
| --- | --- |
| 08146E54 | Common fade setup; invalidate stale/overlapping task bindings. |
| 08147A7C | Fade a range to black. |
| 08147AD0 | Fade a range to white. |
| 08147D2C | Fade to an explicit palette table. |
| 08148740 | Original native callback; advance a binding only when native progress advances. |

Explicit table targets are supported when a complete owned bank is uniform,
or when it exactly matches that binding's recorded native baseline. The latter
maps to the generated palette's own baseline. No approximate color ratio is
used. Unknown operations, unmatched table targets and partial banks are counted
as unsupported; they do not silently become successful custom fades. Native
effects still execute normally. An unsupported custom target freezes its last
colors, so this is visibly incomplete behavior, not an acceptable final fallback.

Setup invalidation covers both original palette overlap and reused native task
addresses. Native callback progress drives the sidecar's exact integer rounding;
completion clears the binding. A new recognized effect can interrupt an existing
fade using its current generated colors. Native palette shadows remain untouched
by the custom renderer; only the allocated hardware bank receives custom colors.

Four-argument setup/table hooks preserve r3 through their 16-byte entry veneers.
Trampolines preserve original prologues and use r12 for continuation when r3
still carries native state. The callback trampoline also preserves its task
register. The direct native tests verify table pointers and flag values, not
merely that a helper returns.

## RAM and build scope

The private transient reservation is now **0203D000..0203F000**, 8 KiB. All three
native heap-limit veneers use the new end; no apparent free bytes were borrowed.
The live structure is 5,596 bytes, with bindings at offset 2,740. Existing local
observation field offsets remain unchanged. Test scripts now obtain the base
address from the candidate manifest instead of hardcoding the previous page.
Original F000/F400 clear endpoints and the new D000 endpoint are covered.

This is not a save-schema change. It is an additional 4 KiB reduction versus the
previous private stage and still needs scene/battle allocation-capacity acceptance.
The stage uses 152,344 bytes of its existing ROM reservation. Clean assembly and
conversion reproduce the exact current ROM. The independent interpolation oracle
now pins the pre-hook 19c8d9e0 candidate so future comparisons continue executing
original native callbacks, not the new hook being tested.

## Live evidence

`test-live-art-palette-fades` reuses the authenticated isolated showcase save.
It executes the real native setter on a paused-state clone, checks every changed
byte, and transfers back only native palette/effect state and the private binding
reservation. Input scratch and clone stack are never transferred. This installs
the effect command, not an expected output. The actual mGBA game then runs its
native callbacks, OAM composition and palette DMA.

The paired parent/candidate sequence covers black, white, explicit baseline
restoration, interruption of an unfinished black fade by white, restoration
again, then a completed black fade through cancel/header/reopen. Original native
callbacks on an independent pinned ROM produce both native-color and generated-
color reference sequences. The saved original hardware bank identifies the exact
visible phase; custom hardware colors must match that same phase.

The final run has 77 samples per machine and 610 checks. Native shadow colors,
every hardware color outside the allocated bank and canonical unit data match
the parent. Six initial commands have five completions and one interruption;
the final lifecycle fade brings totals to seven starts/six completions with zero
unsupported events. On this actual menu path the native bank stays black through
reopening, and the custom bank correctly stays black too. It does **not** prove
a native palette reload after reopening.

The normal transition suite again covers 571 frames per machine and 205 active
overlays. Maximum observed scan and native display-enable line are both 221.
Its 2,915 checks include exact generated colors on unfaded samples. The menu
trace still has zero observed fade endpoints; separate controlled native-command
playback supplies the bounded fade proof.

## Passing reports

All runtime checks used the declared plan and `Test Expansion.ps1 -Only`, with
IDs and purpose announced first. No full integration or campaign replay ran.

| ID | Runner | Checks | Report |
| --- | --- | --- | --- |
| test-live-art-palette-native | 20260918T034822.102538Z | 1127 | build/art/live-palette/native/20260918T034822.687479Z/report.json |
| test-live-art-palette-menu | 20260918T034822.102538Z | 99 | build/art/live-palette/menu/20260918T034832.789681Z/report.json |
| test-live-art-palette-fades | 20260918T035053.625516Z | 610 | build/art/live-palette/fades/20260918T035054.216846Z/report.json |
| test-live-art-palette-transitions | 20260918T035053.625516Z | 2915 | build/art/live-palette/transitions/20260918T035102.493824Z/report.json |
| test-native-art-palette-binding | 20260918T035513.513304Z | 32 | build/art/palette-binding/20260918T035514.114068Z/report.json |

The earlier live fade 592-check pass in 034822 is retained, superseded by the
610-check lifetime extension. Unchanged planner426 and interpolation7284 passes
are reused. Native binding controls cover unowned ranges, partial ranges,
unrecognized weighted-grayscale setup, baseline/uniform explicit tables, native
fourth arguments and stale task-address registration. Refusal tests document
unfinished kinds; they do not accept those effects' visual behavior.

## Retained failures and remaining gates

- Compile directory `build/art/live-palette/compile/20260918T034202.336707Z`:
  zero-initializing a local array introduced an unavailable libc `memset`.
  Explicit volatile stores restored freestanding compilation.
- Runner `20260918T034425.124067Z`, native component
  `build/art/live-palette/native/20260918T034425.790153Z`: an unnecessary previous-
  private-stage E000 endpoint compatibility check placed its canary inside the
  new owned reservation. That compatibility path was removed. The actual parent
  endpoints and new D000 boundary pass. The selected menu step did not run after
  this failure. Private failed candidate 0bd8cf63 remains retained.

Still open: naturally triggered scene/campaign fades; grayscale, tint, cycling
and other native target operations; palette reloads; late appearance during an
already-running fade; original-bank changes and simultaneous same-class palette
variants; all enabled-class coverage; battle/weapon/effect coexistence; enlarged
heap capacity; worst-case timing. Current observation resets to the generated
baseline when the original bank changes and cannot claim to preserve those
unimplemented color variants. The recorded native baseline is only known unfaded
in the tested setup; do not generalize first-observation capture to late entry.

Next exercise actual battle coexistence/scene lifetime on this candidate, then
implement the remaining native color operations and variant/late-entry handling
from measured consumers. Promote through the existing reproducible package only
after those required gates pass. Final art and animation acceptance remain deferred.
