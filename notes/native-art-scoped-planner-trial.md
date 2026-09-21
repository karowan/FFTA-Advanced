# Scoped planner experiment and matched-state timing

September18,2026, follow-up to a56dac6. The verified connected candidate remains
**d9acd7234186a77561a2fb4ee91fdae2197c197d**, palette parent **ff6a50ea**.
No installed build, launcher, vanilla, player save or visible session changed.
G01-G04 remain open; built-in imagegen only, final sprite refinement deferred.

## Experiment

The preferred-bank validator, unowned8bpp checks, native-bank backup and palette/
OAM application were compiled from the same source at `03007100`. The1344-byte
image ran from temporary IWRAM below the caller's saved stack. There was no
persistent reservation or history eviction. A152-byte conservative hot-call
stack bound plus512 interrupt bytes kept native code through `03006D68` intact.
Deep or non-IWRAM stacks used the existing ROM path. The final guard checked the
pre-wrapper stack against `03007F00`, keeping BIOS/SVC space clear too.

The first variant **b04a0389534cc04d299e7e9c52c3250835dacafd** copied the image with
an ARM loop. The intermediate BIOS-copy variant **80c093b33c64044cdd1d8019d427fa6140fa3273**
then used native CpuFastSet. The final variant **dfdc2e9ce57cbbabf95e5d9c7c656c60804b4f10**
added the stricter upper-stack guard. All used the same20-history validator image,
SHA256 `565832a1d3c86dff064b1b73cbfd775e4560460b41dd54a9686201e4fb06b27b`.
The existing10-history boundary matrix separately compiled its matching layout.

## Component evidence and retained host failure

- First20-history equivalence208: runner `20260918T175228.230579Z`,
  `build/art/scoped-planner/20260918T175228.922985Z/report.json`. Two retained
  single/mixed inputs, both stack residues, deep/non-IWRAM fallbacks, conflicts,
  malformed inputs, ABI, full palette/OAM and EWRAM outside declared call scratch.
- The same runner's boundary step hit a host Unicorn access violation after30,559
  checks. Retained `build/art/palette-plan/20260918T175230.048275Z/failed.json`.
  The following native test was unrun. Flushing the host translated-code cache
  between independent bank-vector groups bounds repeated self-modifying-code
  translation without changing emulated registers, memory or test inputs.
- Boundary matrix48,009 and native/rebuild9811 then pass in runner
  `20260918T175405.854448Z`: `palette-plan/20260918T175406.464121Z/report.json` and
  `live-palette/native/20260918T175428.231654Z/report.json`, both under `build/art`.
- Intermediate BIOS-copy208/native9811 pass in `20260918T180018.668095Z`, children
  `scoped-planner/20260918T180019.365022Z/report.json` and
  `live-palette/native/20260918T180020.134215Z/report.json`.
- Final upper-bound and native checks pass256/9811 in runner
  `20260918T180303.642226Z`: `scoped-planner/20260918T180307.341236Z/report.json` and
  `live-palette/native/20260918T180308.207743Z/report.json`.

Component BIOS modeling authenticates the actual SWI opcode, exact image source,
IWRAM destination and multiple-of-eight word count. Actual timing is measured by
mGBA below; modeled component execution is not BIOS or VBlank cycle evidence.
The unchanged validator's full boundary evidence is reused for the copy change.

## Actual movement still fails

Both actual `test-art-scoped-movement` runs complete all retained Move/cancel
samples, then fail the existing ready native-shadow comparison:

| Variant | Runner | Raw battle directory under build/art/live-palette/battle |
| --- | --- | --- |
| ARM copy b04a0389 |20260918T175507.750084Z|20260918T175508.427174Z|
| BIOS copy dfdc2e9c |20260918T180123.179646Z|20260918T180123.840471Z|

Each adjacent `trace-audit.json` evaluates all1205 captured samples. Both have1205
native-shadow and unowned-color phase mismatches; Move starts16 vs15 and lasts48
vs47 frames, cancel starts24 vs22. Generated colors, canonical units, fences,
native executable IWRAM, allocation/ownership and unsupported-operation checks
remain within their tested contracts. Maximum display line203/201 respectively.
The second runner selected movement first by declared plan order; later component
steps were unrun there and were explicitly completed in180303 above.

The ordinary exact-state compositor-bypass diagnostic passes30 checks for each:

- b04a0389: `build/art/compose-cost/20260918T175656.060313Z/report.json`, runner
  `20260918T175655.443591Z`. Active Move16..64 (48), bypass16..63 (47);
  cancel24 vs23. Planner averages11.002 scanlines across1200 active samples.
- dfdc2e9c: `build/art/compose-cost/20260918T180304.253517Z/report.json`, runner
  `20260918T180303.642226Z`. Active Move16..64 (48), bypass16..62 (46);
  cancel24 vs23. This removes the whole custom compositor, not only this change.

## Direct optimization comparison and rejection

New `--planner-bypass` in the existing cost diagnostic disables only the optional
scoped-planner call. It validates the Thumb BL destination and following branch,
replacing four bytes with `movs r0,#0; nop`. The already compiled full ROM planner
then executes with the entire custom compositor still enabled. All assets,
serialized pointers, initial RAM/IWRAM, inputs and final gameplay records remain
matched. This is a sharper control for this optimization than removing12BC.

`test-art-scoped-vs-rom-cost` passes32 diagnostic checks in runner
`20260918T180449.906198Z`, report
`build/art/compose-cost/20260918T180450.560378Z/report.json`:

| Matched dfdc2e9c state | Move start/end | Moving frames | Cancel start | Mean planner scanlines |
| --- | --- | ---: | ---: | ---: |
| Scoped BIOS-copy planner |16/64|48|24|9.3941667|
| Existing ROM planner |15/63|48|24|11.8625|

The new path is faster within the planner yet responds to Move one frame later,
with no cancel or movement-duration improvement. It is **rejected**, not adopted
on lower cost counts. Neither comparison supplies complete timing acceptance.
Next investigate native scheduling and entry-phase coupling rather than repeat
this trial merely because its scanline count is smaller.

## Recovery and current state

Trial engine/build/boundary-test changes and new helper files were removed.
The existing cost diagnostic keeps its optional precise-control mode and three
pinned historical test IDs. Recover the full final experiment against a56dac6
from ignored `build/art/scoped-planner-trial/dfdc2e9ce57cbbabf95e5d9c7c656c60804b4f10/rejected-source.patch`,
SHA256 `12db6bbecfd8ec1a9f1ec13e056106801efbaeddbc65eda5c829f38f04269d0b`.
The retained compile products, ROMs, captured plans, logs and failures remain local.
The rejected private `scoped-current.json` index is historical, not the candidate.

Rebuilding restored the prior palette parentff6a50ea and connected d9acd723
byte-exact: `build/art/connected/rebuild/20260918T180611.064186Z/report.json`.
Reuse applicable passing menu, keyboard and other evidence; no broad integration
or repeated gameplay run was used just to reconfirm the restored hash. All test
runners are terminal. Native scheduler/entry timing, worst-case encounter/menu
capacity, remaining natural consumers, assembled acceptance and delivery remain.
