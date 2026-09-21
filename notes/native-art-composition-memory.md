# Reduce composition memory work; all-class history demand

September18,2026; follows `5974c60`. Current private candidate:
`05c66b387e415d59d519ca409d911311b39019d8` via
`build/art/live-palette/poc.json`. Stage161244/state8096; the heap reservation,
palette algorithms, generated pixels and save schema are unchanged. No package,
launcher, player save or session changes. Built-in imagegen only; final sprite
refinement remains deferred. All G gates remain open.

## Retained implementation

Ownership composition compares each object's three meaningful attributes
directly before publishing any tags. Aligned output clears128 tag bytes using
32 word stores; unaligned output retains byte stores. Palette application skips
four authenticated unowned tags together, without reading/writing their OAM.
Other tags retain the existing disabled-object check and palette assignment.
Full palette-conflict validation still precedes all application writes.
The aligned word type explicitly permits aliasing the byte tags. Adding that
compiler contract after review reproduced05c66b38 byte-exact, so the same tested
machine code and its runtime evidence remain applicable.

On the same raw battle input, ownership composition falls2361→1455 instructions
and application820→395. These are instruction counts, not hardware cycles.
Actual exact-ROM timing also improves within the measured scope below.

Ownership tests now use TI925T ARMv4T before memory mapping and explicitly check
all four output alignments, exact128-byte canaries and unchanged hardware OAM.
The previously stat-only modified test file had no substantive diff before this
turn; only this CPU-model/alignment verification change is committed.

Runner `20260918T103424.951334Z` passes:

| Test | Checks | Report under build/art |
| --- | ---: | --- |
| test-native-art-compose-profile |286|compose-isolation/20260918T103425.602895Z/report.json|
| test-native-art-compose-isolation-current |3912|compose-isolation/20260918T103425.810080Z/report.json|
| test-live-art-palette-native |1153|live-palette/native/20260918T103426.032939Z/report.json|
| test-art-palette-owners, before added alignment cases |496|palette-owners/20260918T103428.640090Z/report.json|
| test-art-palette-plan |48009|palette-plan/20260918T103429.241026Z/report.json|

The final ownership712 checks pass in `20260918T103536.596957Z`, at
`build/art/palette-owners/20260918T103606.191759Z/report.json`.
The current-ROM native rebuild is byte-exact. Full composition checks cover
seven native phases, fresh/skipped DMA and both stack residues, including the
previous unseen-rotation latch condition. Reuse prior actual rotation/setter
evidence for unchanged effect semantics; this is not a claim those tests ran
on the current hash.

## Actual timing and retained failure

Runner `20260918T103536.596957Z` **FAILED** its last battle step. Earlier completed
steps remain usable within their actual scopes:

- Ready capture: `build/art/live-palette/battle/20260918T103537.206819Z/observed.json`.
- Exact-state cost30: `build/art/compose-cost/20260918T103555.774795Z/report.json`.
- Menu transitions2933: `build/art/live-palette/transitions/20260918T103558.956802Z/report.json`.
- Expanded ownership712 as above.
- Failed `test-live-art-palette-status-control`:
  `build/art/live-palette/battle/20260918T103606.805416Z/failed.json`.
  The retained `trace-audit.json` evaluates all1205 samples after fail-fast.

| Current05c66b38 comparison | Move starts | Move ends | Moving frames | Cancel starts |
| --- | ---: | ---: | ---: | ---: |
| Exact-state active |17|64|47|24|
| Exact-state compositor bypass |16|63|47|23|
| Separate status-only native control |15|62|47|22|

Matched-state compositor overhead is1 frame before Move, zero extra moving
frames and1 before cancel; preceding2908487c measured1/1/3. Across1200 retained
active timing samples, planner duration `(profile[3]-profile[2]) mod228` averages
11.4767 scanlines (range7..17), versus13.152 (8..19) in2908487c's
`build/art/compose-cost/20260918T101353.995131Z/report.json`.

The separate full battle still has native shadow and unowned hardware color
phase mismatches in all1205 samples, and2-frame Move/cancel response delays.
All generated hardware colors, unit records, memory fences and native executable
IWRAM remain exact. No allocation failure, missing overlay, new unsupported
operation or scan/display wrap; maximum display line199. Keep this measurable
work reduction without claiming complete timing/phase acceptance.

## Rejected ARM-mode trial

Private `a18f87f89b5ad6ee4045cd265779b26cb0723698` compiled five hot internal
routines in ARM mode with Thumb interfaces. Component profile286/isolation3912/
native1153/planner48009 passed in `20260918T102807.987395Z`. Exact-ROM fixture/
cost30 passed in `20260918T102838.543498Z`, report
`build/art/compose-cost/20260918T102857.219225Z/report.json`.

It removed the matched-state extra movement frame, but planner duration rose to
18.315 scanlines (13..24). Lower instruction count did not yield faster planning;
this experiment does not isolate ROM fetch from other timing costs.
Actual menu transitions2933 passed, but `20260918T102946.109713Z` failed full
battle at `build/art/live-palette/battle/20260918T102953.699691Z/failed.json`:
496 shadow-phase and497 unowned-color mismatches, response delays1/3, movement47
versus47; maximum display line212. Its derived audit remains beside the failure.

The ARM-mode changes are removed. Retain their private patch:
`build/art/arm-compose-trial/a18f87f89b5ad6ee4045cd265779b26cb0723698/rejected-source.patch`,
SHA256 `1b01dc455848df8c7fb5b3abf921aa02a1a1a25c55389061098dcfa2b6f1e775`.
Do not repeat this trial based on instruction counts alone.

## Concrete all-class capacity issue

New read-only `scripts/audit-art-palette-capacity.py` authenticates original
class references and captured native palette shadows. Report:
`build/art/palette-capacity-audit/20260918T103843.456261Z/report.json`.
It derives17 distinct `(class,native bank)` histories at deployment entry10:
seven classes match normal bank0 and dim bank9; three match normal bank1.
Later ready observations have13 possible histories. The compiled/current headers
provide10 slots. Current enabled mask2 means only Human Dark Knight is enabled.

This is **potential full-range effect pretracking demand when all ten classes
are enabled**, not17 simultaneously visible characters or an observed all-class
runtime failure. The limit must be addressed before all-class enablement. Ten
hardware palette allocations and historical color states are separate concepts;
do not silently evict absent transformed histories or claim maximum capacity
from a one-class test. The audit records exact hashes and does not create a game
fixture or replay deployment.

Next: resolve this concrete all-class history-capacity issue, then enable and
prove mixed-class palettes. Keep natural scene/effect lifetimes, cross-bank
identities and the timing/phase failure explicit. Final artwork and complete
reproducible delivery remain open. No broad integration suite ran this turn.
