# Palette timing follow-up and saved-state identity

September18,2026; follows `130b684`. Current private candidate:
`2908487c5de59274b03b71c59add5ab828bcba34`, resolved through
`build/art/live-palette/poc.json`. Stage161196/state8096 bytes. No package,
launcher, save-schema, player-save or running-session changes. Built-in imagegen
only; final sprite refinement stays deferred. All G gates remain open.

## Implemented changes

Background-only type2/type4 callbacks now take an authenticated assembly entry
path to the original native callback without entering generated-art bookkeeping.
Ranges crossing OBJ color256 still enter the generated path. On retained native
BG162..168 and169..175 cases, three type2 callbacks execute2535 instructions
instead of4344; type4 executes432 instead of2244. Complete native output, caller
return and stack/register ABI match. The entire art reservation stays unchanged.
These are ARMv4T instruction counts, not measured hardware cycles or frame gains.

Palette-bank backup, application and restoration use the existing aligned ARM
block-copy helper, moved to shared scan assembly. Each bank is exactly8 words.
Native palette shadow is never a copy destination. Fresh-DMA latching copies only
occupied variant slots; acquisition initializes a new slot's first visible phase.

Source review found a correctness gap: type2/type4 history can exist with no fade
starts and no emitted actor. The prior compose guard consequently failed to latch
off-screen rotation history. Current2908487c updates every occupied slot on fresh
native palette DMA, regardless of fade counters or emissions. Skipped DMA holds
the previous phase; no overlay is fabricated while the actor is absent.

## Timing diagnostic correction — invalid reports retained

The initial new `--current` cost mode reused the old29453 ready state after
checking RAM layout and image-source identity. That was insufficient: saved
actors contain absolute ROM sequence/OAM pointers into relocated generated data.
For example saved02020A60 contains09FB2A00 and saved02020A54 contains09FB25F4.
The data at these addresses moves when the compiled stage changes size.
Native wait-PC and RAM-layout equality do not establish compatible actor state.

The following reports said passed but **their timing conclusions are invalid**:

- `build/art/compose-cost/20260918T095203.228375Z/report.json` (1fdf40a6)
- `build/art/compose-cost/20260918T095323.077953Z/report.json` (21f24d6f)
- `build/art/compose-cost/20260918T095806.198641Z/report.json` (9d577c53)

Do not use their zero-Move/one-cancel overhead or scan-line averages as acceptance
or optimization evidence. Preserve the reports and runner logs. Earlier pinned
same-ROM diagnostics from the preceding checkpoints are unaffected. Pure palette
components using captured RAM/VRAM as explicit inputs do not execute saved actor
animation pointers and retain their stated bounded validity.

The corrected workflow captures a ready state through the declared native route
and writes a `cost-fixture.json` beside that exact private ROM. The index records
ROM, observed report, state, RAM and IWRAM hashes. Cost replay requires exact ROM
identity and authenticates each file. It compares the active build against a
private copy restoring only the original eight-byte compositor entry. Both load
identical current state; the bypass's missing generated overlay is diagnostic
only and never deliverable. No old timing trace is claimed reproduced by a newer
ROM. The two existing pinned diagnostic modes retain their original checks.

Corrected runner `20260918T100152.677044Z` passed:

- `test-live-art-palette-cost-fixture`: actual9d577c53 native route to ready;
  `build/art/live-palette/battle/20260918T100153.398543Z/observed.json`.
- `test-live-art-palette-current-cost`:30 checks;
  `build/art/compose-cost/20260918T100211.213672Z/report.json`.

| Exact9d577c53 state | Move starts | Move ends | Moving frames | Cancel starts |
| --- | ---: | ---: | ---: | ---: |
| Active | 17 | 64 | 47 | 26 |
| Compositor bypass | 16 | 62 | 46 | 23 |

This demonstrates remaining compositor overhead in that state:1 frame before
Move,1 additional moving frame,3 before cancel. It does not demonstrate an
improvement over21f24d6f, and it is not a timing measurement of current2908487c's
subsequent unseen-history latch fix. A changed candidate needs its own matching
capture when timing is next measured; never bypass the identity guard.

## Real battle failure remains open

Runner `20260918T095444.611884Z` tested1fdf40a6 against the matched status-only
control. `test-live-art-palette-status-control` **FAILED** strict ready-state
native palette-shadow equality. Retain:
`build/art/live-palette/battle/20260918T095446.350897Z/failed.json` and its
`trace-audit.json`, reproducible with `scripts/audit-live-art-battle-trace.py`.

All1205 samples have exact generated hardware colors, preserved units/fences,
no missing overlay, new unsupported event, allocation failure or display wrap.
Maximum display line204. Native shadow/unowned hardware phase differs throughout.
Move begins18 versus15, both take47 frames; cancel begins24 versus22. This narrow
battle replay was justified by changed background callbacks and unresolved input
timing, not by the ROM hash alone. No broad integration suite was run.

## Passing evidence and reuse

Current2908487c runner `20260918T100407.302722Z`:

| ID | Checks | Private report under build/art |
| --- | ---: | --- |
| test-native-art-compose-isolation-current | 3912 | compose-isolation/20260918T100408.026385Z/report.json |
| test-native-art-late-entry | 4834 | late-entry/20260918T100408.270408Z/report.json |
| test-live-art-palette-native | 1153 | live-palette/native/20260918T100414.350888Z/report.json |

Composition covers all seven native BG phases, fresh/skipped DMA and both stack
alignments, exact native/OAM/VRAM/unowned colors and outside-RAM preservation.
The added12 checks cover rotation and literal cycling before any emission/fade:
changed colors, skipped-DMA hold, fresh-DMA latch and absent overlay. DMA is modeled
synchronously; actual first appearance after unseen rotation is still a live
consumer gate. Both compositor and planner components now select TI925T ARMv4T
before mapping memory.

Reuse9d577c53 runner `20260918T095805.340695Z` for unchanged bank-copy behavior:
planner47961 atpalette-plan/20260918T095825.346214Z, actual live rotation1297 at
live-palette/fades/20260918T095809.551664Z. Its layout-only cost result is invalid
as stated above; other tests remain applicable. Reuse1fdf40a6 background304 at
background-cycle/20260918T095445.240851Z and rotation38146 at
rotation/20260918T095206.444322Z for unchanged entry dispatch and permutation.
Each report retains exact candidate/source hashes; this is explicit evidence
reuse, not a claim that every test ran on current2908487c.

## Next

Keep the timing/phase failure explicit. Investigate actual foreground/VBlank
handoff and compositor work from an exact matching ready state. Do not repeat
discarded counted-tail/multirow trials or reuse cross-ROM saved actor state.
Finish actual unseen-rotation appearance, natural script/scene/heap lifetimes,
maximum mixed-class capacity and cross-bank mapping. Remaining asset consumers,
all-class final artwork and reproducible packaging are also open.
