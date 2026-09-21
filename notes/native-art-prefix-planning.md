# Native OAM prefix planning: measured improvement, E01 still open

September18,2026 local / September19 UTC. Full engineering remains required;
only final artwork and authored frame content are deferred. Neither candidate
below is accepted for delivery. Installed7507ca5c, its immutable bundle/indexes,
default palettefa3d12b4 and player saves remain unchanged. No game launch,
publication, art generation or agents. All enclosing runners are terminal.

## What changed and what the evidence says

The scoped-frame trial moves fresh ownership validation and palette publication
to temporary ARM leaves in IWRAM. It does not reuse a prior frame's ownership,
plan or pixels. `art_scoped_build.py` compiles each pure C function separately,
rejects address/call relocations, verifies the harmless GNU V4BX annotation is
an actual position-independent BX instruction, extracts the section and emits
a bounded copying wrapper. Compiler stack-usage records set the bounds.

For20 histories the ownership leaf is656bytes with192bytes of stack; the
publish leaf is304bytes with24bytes of stack. After the wrapper's24-byte save,
minimum SPs are030072B8/030070B0 respectively, leaving512 interrupt bytes above
resident code ending03006D68. Deep/external stacks execute the identical ROM
leaf. Neither changes the11316-byte live state or12KiB reservation. Ownership
uses local scratch so even a final-object mismatch publishes no tags/bank masks.
Publication follows full validation and changes only allocated banks/owned attr2.

That trial alone does not materially improve the earlier ARM timing result:
`059d256a47daecefb5a160499e5cfd4faeb9bbd7`, stage248760bytes. Mean composition
22.76–24.14scanlines, versus roughly2.8 in its compositor-bypass diagnostic.
Move starts1frame late and lasts1frame longer; cancel is2frames late at both
offsets. Phase/deadline6226 passes; response rejects ten metrics.

Actual compiled call/return cycle observations then identify a recurring cost:
full OAM classification alone consumes about5.37scanlines, even with a mostly
empty native OAM tail. Variant preparation costs about2.95scanlines. These are
inclusive GBA cycle measurements, not host wall time or isolated instruction
counts. Nested call measurements must not be added twice.

The next private trial adds two current-input optimizations:

- Authenticate the complete native12BC producer, including literals, at
 12BC..14C8 (SHA2569b66e36f26b094d61539c4790834bd83d102e90433cf5b7e443c268cabbf8c64).
 It initializes all128 slots to00F800A8/0000, DMA-copies priority/UI/main/tail
 groups with native clipping, then writes only attr3 for affine matrices.
 Derive the actual copied prefix from its current counters. Scan that prefix;
 reserve bank0 for its omitted ordinary sentinels. Unknown counters use128.
 This is a same-invocation producer contract, not a cached lifetime assumption.
- When every demanded class/bank already matches its current identity history,
 and dormant keys remain valid, skip allocation/remapping work that would make
 no changes. New keys, split histories or corruption take the original path.

Combined candidate: `12562f6fcdcb21b98bd0e82c622490653e699f95`, stage249056bytes.
No memory reservation increase. `native_oam_prefix` and `scoped_frame` default
off and require private builds. The private build mode enables existing exact
bank/ARM classification options as well; it does not use repeat_frame or DMA
writer caching.

## Actual response and remaining defect

| Input offset | Action | Active start/end/duration | Bypass start/end/duration |
| --- | --- | --- | --- |
|0|Move|25 /72 /47|23 /70 /47|
|4|Move|23 /70 /47|23 /70 /47|
|0|Cancel|30 /30 /0|30 /30 /0|
|4|Cancel|30 /30 /0|29 /29 /0|

Move duration now matches at both offsets, and two action/offset pairs match
completely. However Move arrival is2frames late at offset0 and cancel1frame late
at offset4. The strict response gate fails four metrics. This is partial
improvement, not a performance fix or engineering completion.

Mean composition is18.78/18.93scanlines for Move and17.53/17.42 for cancel;
minimum14.71 and peak34.02. Fresh ownership remains3.86–3.90scanlines,
variant preparation0.88, confirmation0.43, prefix count0.20–0.21. Inclusive
plan/publication averages7.02–8.41 and is still the largest remaining block.
The native phase/deadline audit passes6226. No observed VBlank overrun in this
trial, unlike the rejected repeated-demand candidate.

The causal finding remains added per-interrupt composition delaying foreground
progress/input handling. There is no proof this is an unsolvable hardware limit.
Do not waive residual response delays, disguise them through frame realignment,
or mistake a passing observation report for timing acceptance.

## Reproducible evidence and failures

All IDs run through Test Expansion.ps1 and scripts/native-art-test-plan.json.
Paths below are under build/art unless identified as runner timestamps; every
timestamp below has20260919T prefix. Existing applicable evidence is reused.

| Runner | Scope/result and child evidence |
| --- | --- |
|004836.155101Z|Scoped owners stopped before emulation: initial relocation guard rejected GNU V4BX. Complete log retained; publish skipped. Guard corrected to verify only BX-register compatibility annotations.|
|004915.646206Z|Owners6356: palette-owners/004916.333432Z/report.json. Publish49221: palette-plan/004917.897157Z/report.json.|
|004950.800422Z|Scoped build8; isolation/profile292 at compose-isolation/005004.006787Z/report.json. Entry fails paired native shadow at live-palette/battle/005004.251197Z/failed.json; subsequent assertions skipped.|
|005100.374833Z|Scoped full observation5175, native-frame-events/005101.065293Z/report.json. SHA25673d947c7bcb14d07451ab81d3903e9e9233e0913d737c82b508bb946979ccaf6.|
|005232.293758Z|Scoped phase6226 at native-phase-evidence/005232.983927Z/report.json; response fails ten metrics at response-budget/005233.272549Z/failed.json.|
|005635.468624Z|Cost-observer post-processing fails at native-frame-events/005641.012522Z/failed.json AFTER5175 observation checks and all four branches. A loop branches to a shared instruction after a conditional copy call. It is not another invocation. Corrected summarizer explicitly counts/excludes unpaired shared-target arrivals; never invents call durations. Raw failed evidence retained.|
|010214.764141Z|Prefix owners7904, planner70504, variants25; private build8 and profile292 pass. Exact child paths below. Entry fails paired native shadow at live-palette/battle/010235.990470Z/failed.json. Later assertions remain skipped.|
|010406.404338Z|Prefix full observation7232 at native-frame-events/010407.155396Z/report.json. All1024 native states/framebuffers match ordinary execution. All512 active prefix applications independently check current counters and the COMPLETE omitted hardware/tag tail. Corrected cost summaries pass.|
|010733.367273Z|Twenty-history/high-slot differential368 at frame-high-slots/010734.128994Z/report.json. Stronger actual affine-tail/count proof8660 at palette-owners/010734.949013Z/report.json.|
|010816.054585Z|Prefix phase6226 at native-phase-evidence/010816.915753Z/report.json. Response fails four metrics,13 authentication checks pass: response-budget/010817.407344Z/failed.json.|

Initial prefix component reports are palette-owners/20260919T010215.556386Z,
palette-plan/20260919T010217.776652Z and
palette-variants/20260919T010222.201487Z, each report.json. Profile is
compose-isolation/20260919T010235.738939Z/report.json. Native-counter coverage
executes756 combinations of both producer buffers and front/UI/main/tail limits;
reported prefix equals the actual native DMA destination extent. Nonzero affine
data changes the final hardware slot's attr3 while omitted attr0..2 remain exact.

Prefix trace SHA256:
`b2ed9e1cd73e37f512ea60669f8feda99f1ce661a7e63165badff779b157a94f`.
Its immutable frame/phase/response IDs use that candidate and retained entry.
Mutable `test-art-prefix-build/profile/entry` steps remain in dependency order.
The build reproduces defaultfa3d12b4 and restores installed/source indexes.

## Continue

E01–E05 remain open. Continue from the prefix candidate and actual cycle data,
not another generic repeated-frame key/cache or another unmeasured scan loop.
If changing code, preserve this immutable trace and use a new candidate-specific
event ID. Maintain current native ownership, palette phases, all omitted-tail
proofs, and direct response/deadline gates. Reuse the unaffected component and
capacity/animation evidence. Native action/effect, maximum capacity, campaign/
save reconciliation and final assembled release acceptance are still required.

The reduced instruction count, phase pass and narrower latency are not grounds
to promote the private build. Full-game engineering remains incomplete.
