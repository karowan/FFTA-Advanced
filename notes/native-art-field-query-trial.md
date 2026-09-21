# Current-query terrain optimization: useful but unaccepted

Full engineering remains required. Only final artwork content is deferred.
E01-E05 remain open. No installed ROM, launcher, save or public artifact changed.
All runners below are terminal. This is a private experiment, not a release.

## Current refinement: exact original fallback stack

The current private selector is **b35fa9e4178bbb281cde447db58702cdd15c9895**.
The a3937916 results below are retained historical evidence. The new dispatcher
restores the original caller stack/registers before tail-branching to the original
noncanonical query. Its temporary dispatch frame is24bytes, but the fallback
has **zero additional nesting**. Canonical queries still use the direct live-bank
scan. The stage uses808bytes at11E7900..11E7C28 plus the same12-byte entry.
No persistent memory/schema change or default-builder promotion is made.

The hook's absolute address is2mod4. Initial runner033737.024979Z failed because
assembler section-relative literal alignment produced the wrong hook length;
contract/entry were skipped. The corrected explicit PC-relative inline literal
matches the actual aligned ROM address. Build033828.089322Z passes.

Runner20260919T033827.332121Z passes **60,252** field/grid/copy checks:
build/art/field-query-contracts/20260919T033828.564742Z/report.json.
In addition to the earlier cases, every byte of both native unit arrays and the
intervening gap agrees with the actual original canonical predicate. Every
noncanonical query reaches the original body exactly once, with the same stack
address, arguments, preserved registers and return address. Uninitialized local
stack bytes are not compared as outputs. Broader AI/interrupt acceptance remains
separate; this closes the introduced fallback-nesting defect only.

The entry check still fails its ready palette-shadow comparison; later entry
assertions are skipped. Retained failure:
build/art/live-palette/battle/20260919T033834.466440Z/failed.json.
Runner20260919T034014.267885Z passes test-art-field-dispatch-frame-events
**31,042** and test-art-field-query-rebuild. Reports:

- build/art/native-frame-events/20260919T034014.966763Z/report.json;
  SHA256641ed4767b9ec5545b90219799930ccef2406c47992211158f22a20e2c3c8bfc.
- build/art/field-query-rebuild/20260919T034038.780006Z/report.json.

All1024 observed/ordinary complete states and framebuffers agree; current
ownership/demand/bounds are independently audited. The stage rebuild reproduces
the entire ROM and restores candidate/action/installed metadata exactly.

| Action / input offset | Active start/end/duration | Same-ROM bypass | Result |
|---|---|---|---|
|Move idle0|24 /73 /49|23 /70 /47|start+1, end+3, duration+2|
|Move idle4|25 /73 /48|24 /70 /46|start+1, end+3, duration+2|
|Cancel idle0|27 /27 /0|26 /26 /0|start/end+1|
|Cancel idle4|26 /26 /0|26 /26 /0|matches|

Runner20260919T034634.450863Z passes test-art-field-dispatch-phase **6226**:
build/art/native-phase-evidence/20260919T034635.292812Z/report.json.
It then fails test-art-field-dispatch-response with the **eight metrics** above:
build/art/response-budget/20260919T034635.905737Z/failed.json.
These results do not clear E01. No timing waiver, input realignment or installation.
All runners are terminal; action5a14e6c7/defaultfa3d12b4/installed7507ca5c and
player files remain unchanged. Continue reducing the actual rendering work;
faster foreground field queries alone do not solve interruption latency.

## Historical change and preservation

The preceding controller profile measured150 nonmatching field queries during
cancel, consuming4.36-4.47 inclusive video frames. Each rebuilt a36-pointer live
peer array and resolved the bank again. The new geomancer-field-fast.c validates
the current unit's canonical address, obtains the live bank through the original
accessor and scans its contiguous records directly. It constructs a caster
pointer only after a record's field kind and timer can match. There is no cached
field, map, ownership or generation state. Every noncanonical owner, including
independent evaluated copies, falls back to the complete original query.

The query preserves caster HP/Petrify, Charm/allegiance, both field kinds,
nonstacking overlap, timers, Manhattan cross, valid map cells and height bounds.
The original tile callback still controls terrain/occupancy/height and applies
Float/Surefoot rules. No saved-schema or persistent RAM reservation changes.

scripts/build-fast-field-query.py builds a separate optional stage over the
completed5a14e6c7 parent. It authenticates the gameplay integration, canonical/
copied ownership code and actual format-validator code/literals against1b070824.
Only the field function's12-byte entry and736 new bytes at11E7900..11E7BE0
change; the latter fit the existing integration reservation ending11E8000.
All unrelated ROM bytes, including the six completed Moogle action descriptors,
remain exact. The original function body is retained behind an exact prologue
trampoline for noncanonical owners. Compiler flags/source/hash, symbols, stack
usage, patches and authenticated regions are recorded in the private manifest.

Private candidate: **a393791609849abec6b55ba59c05c6963087b3e9**.
View: build/art/connected/a393791609849abec6b55ba59c05c6963087b3e9/live-palette-view.json.
Selector: build/art/performance/field-query/current.json.
The action-completion selector stays5a14e6c7, default palettefa3d12b4 and installed
bundle7507ca5c remain unchanged. This experiment is not applied by the default
integrated or connected builder; do not silently add it to final delivery.

The C frame uses48 stack bytes; its installed entry adds8. The noncanonical
fallback therefore has56 additional bytes of nesting before the original query.
Both tested stack alignments and owned-copy fixtures pass, but worst-case AI/
native nesting and interrupt headroom are not established. A dispatch that
restores the caller stack before taking the original fallback is a possible
next refinement. Do not describe this as accepted full-game stack coverage.

## Component and consumer results

test-art-field-query-contract passes **44,795** checks at
build/art/field-query-contracts/20260919T032624.758203Z/report.json in runner
20260919T032624.080467Z. It authenticates the detached native battle memory and
both actual ROMs, then executes their real query and tile routines:

- Every36 canonical slot, both field kinds and all eight timer encodings;
  party/enemy allegiance and both tested stack alignments.
- Complete native map comparisons with independent geometry/eligibility oracle,
  HP/Petrify, Charm, overlap and both field kinds.
- Invalid coordinates/kinds, bank magic, save-format magic/version and foreign
  pointers; full EWRAM remains unchanged by every isolated query.
- Actual explicitly owned evaluated copies, independent fields and retirement;
  no borrowing a live caster's field when it is absent from the copy.
- Explicit height differences0/2/3/6 and invalid field centers.
- Eighteen complete native movement grids across Rime/Refuge/none, grounded/
  innate flight/timed Updraft and confirmed native Surefoot support fixtures.
  The entire EWRAM agrees between original and optimized grid executions.

An instruction observer confirms each canonical query calls the current bank
accessor once and never builds peers or takes the original fallback. This is
native consumer execution on detached raw memory, not a resumed game or final
AI/campaign/law/cold-save acceptance. Original state/framebuffer timing is
measured separately below.

## Actual timing: still fails

The same runner's test-art-field-query-entry reaches the ready capture but fails
its paired native palette-shadow comparison. Later entry assertions are skipped.
The complete failed record remains:
build/art/live-palette/battle/20260919T032627.561296Z/failed.json.

test-art-field-query-frame-events passes **31,055** in terminal runner
20260919T032734.017481Z. Report:
build/art/native-frame-events/20260919T032734.672429Z/report.json, SHA256
b6e084f8c504435d5d38798b7c26a6f7d0e16e4d59784a0af261c4fd4ed27633.
All1024 observed/ordinary framebuffers and complete states match; current OAM,
ownership, demands and producer bounds are independently audited. Same-ROM
compositor bypass remains an isolated diagnostic, not a shipped option.

The expensive cancel call08093BF2 ->0809A5E0 is now6.005/5.688 inclusive video
frames at idle0/4, versus9.265/9.082 in the earlier e1 profile. Current bypass
costs5.526/5.425. This is a substantial decrease in that callback, not proof of
equivalent full-game response: the before/after ready phases also differ.

| Action / input offset | Active start/end/duration | Same-ROM bypass | Result |
|---|---|---|---|
|Move idle0|25 /73 /48|23 /70 /47|start+2, end+3, duration+1|
|Move idle4|24 /72 /48|23 /70 /47|start+1, end+2, duration+1|
|Cancel idle0|27 /27 /0|27 /27 /0|matches|
|Cancel idle4|27 /27 /0|26 /26 /0|start/end+1|

Runner20260919T033033.899256Z passes test-art-field-query-phase **6226** and
test-art-field-query-rebuild, then fails test-art-field-query-response with
**eight metrics**. Phase report:
build/art/native-phase-evidence/20260919T033034.853346Z/report.json.
It proves the independent original native color rotation, exact hardware DMA
phase, unchanged object shadow and every observed display return within VBlank.
Response failure: build/art/response-budget/20260919T033036.022805Z/failed.json.
This preserves the earlier entry failure; it does not claim its skipped checks ran.

Rebuild report: build/art/field-query-rebuild/20260919T033035.467538Z/report.json.
The complete candidate ROM reproduces byte-for-byte, and all prior candidate,
action and installed indexes/manifests are restored exactly. No runtime occurs
in that build check. This proves the isolated optional stage, not final E05
reconstruction of the entire release from clean inputs.

## Retained failures and next work

- Build runners031622.753350Z and031752.520975Z failed overbroad authentication:
  the first included intentionally replaced art/job tables; the second included
  the established art heap-clear hook at11D0714. The corrected guard covers the
  actual query/accessor/format dependencies. Build031902.419805Z passes.
- Contract032213.185709Z and diagnostic032321.475499Z stopped on absent accessor
  counts after preflight had already translated the code. The observer needed
  Unicorn's documented-in-project translation-cache refresh, also used in the
  earlier field test. The ROM did not change. Entry dependencies were skipped.
- Contract032450.811804Z passed canonical and map cases, then rejected the
  simulated owner below the active stack. The corrected fixture places it above
  the stack, as the actual ownership contract requires. Failure remains retained.
- The failed entry/response results above remain unwaived. No broad integration
  was justified or run for this bounded experiment.

Continue E01 by reducing the remaining per-interrupt compositor work; faster
field queries alone do not resolve custom-rendering latency. Do not blindly
skip repeated-frame overlays: native compose overwrites OAM even on skipped
palette-DMA frames. Prior cache experiments and their writer/lifetime limitations
remain applicable. If this optional field optimization is retained, reconcile the direct
AI/Refuge/path consumers. The current dispatcher removes extra fallback nesting,
as verified above; broader native-call depth coverage is still separate. E02-E05 remain open; reuse their applicable evidence.
