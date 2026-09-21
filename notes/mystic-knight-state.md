# Mystic Knight state and damage foundation

September 15, 2026 Pacific. This is a bounded implementation checkpoint,
not acceptance of the complete job or expansion.

## Implemented behavior

The existing 22-byte owned job record now uses bytes20–21 for an enchant
kind1–11, ordered primary item ID and Spellweave's previous category. Sabers
and rapiers qualify. An enchant is valid only while its original primary item
remains equipped and the unit is alive and not petrified. Replacement,
Dispel, job/battle/reset/KO lifecycle paths clear the appropriate state.
Enchantment grants preserve the sequence and are tagged as beneficial.

Spellweave distinguishes action sequence from damage type. Fight and
Spellbreak sequence as Physical; enchantments, Release and Break sequence
as Magic. Original healing/status spells receive explicit Magic tags rather
than depending on their native damage field. Wait and unclassified actions
retain the sequence. Forced actions, native reactions and combos do not gain
the voluntary alternation bonus. Opposite categories multiply direct HP damage
by27/20, without multiplying healing or status accuracy.

Arcane Ward applies3/4 to eligible incoming direct magical HP damage when the
frozen MP total is positive and at least half maximum. It spends no MP. Both
supports participate in the shared single-rounding damage calculation. The
integer ratio helper handles overflowing intermediate products/denominators
and saturates only an unrepresentable final64-bit result.

The 820-byte action frame,824-byte external result slot and260-byte extra
slot retain their ABIs. Eight separately reserved arrays of64 halfwords at
`0203CA40..0203CE3F` store frozen bits0..9 and claims16..21. They share the
existing extra slot's exact live owner; copies, nested scopes and retirement
preserve that ownership. Unsupported bits are rejected. The native heap limit
is `0203CA40`; no save-schema enlargement was needed. The coordinated address
and bit reservations are in `shared-job-allocations.json`.

Root integration links the extended shared snapshot implementation and Mystic
helpers into ROM offsets `1300000..132FFFF`, with an erased-space assertion
and size boundary. Public callers in the older modules are explicitly rebound;
ELF mapping symbols distinguish instructions from literal data. The future
Mystic help region at1330000 is reserved only.

## Regression diagnosis and correction

The initial shared scaling changes passed arithmetic and direct native-call
tests but broke real menu timing and native Dancer/Passing Step AI selection.
The full70-step run `20260916T011822.908474Z` failed five playback/AI checks.
Reducing the new storage bank alone did not fix them.

Early isolation runs before `20260916T015753.567496Z` are invalid as ablation
evidence: nested fixture source reloaded the current manifest. The comparison
script now asserts the actual loaded ROM hash against each intended variant.
The corrected run reproduced a passing prior candidate
`15715d35dbe3c61b2ac95564df12cf012dcf97ec` and a failing candidate
`5201db25c63e6d2da9730d905386afe2fd73f067`. Disabling Mystic flags/storage,
restoring the old heap limit, or substituting the earlier snapshot code did
not restore the AI scenarios. Run `20260916T020040.659060Z` restored only the
old shared damage-scaling routine: all three learned Dancer scenarios selected
Forbidden Dance, paid14MP and handed off, while the unlearned control used Fight.

The corrected production path uses a support-only accessor for unsnapshotted
forecasts. It checks the equipped support before resolving owned state, skips
irrelevant enchant/reaction queries, and returns immediately when Spellweave
cannot apply. Inside an action it still reads the exact frozen snapshot,
including copied units. No acceptance timings, button inputs, seed sets or
nonvacuous AI requirements were relaxed. The affected22-step run
`20260916T020305.733856Z` passes on
`29dd2384abff25f23827274bb0976b0f587f6c9c`; its input manifest is unchanged.
This establishes the practical correction; it is not an instruction-cycle
profile or proof of the native AI's internal time-budget policy.

## Deterministic reproduction

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite combined`
for the assembled regression. The `test-mystic-knight-state` step covers560
fixed arbitrary-precision arithmetic vectors,11 enchant lifecycle matrices,
weapon replacement, frozen/copy/claim ownership and96 cross-class factor
configurations with seven magnitudes each. It also executes36 real native
Fight/Cure/Fire transactions with payment, damage, sequence and retirement
checks. The range/claim tests include the highest packed bit and rejection of
unsupported upper bits. Fast support queries must agree with the frozen
snapshot even after live equipment and MP change.

`diagnose-mystic-isolation` is an analysis-only step in the same plan. It creates
private hash-identified variants, retains the actual AI inputs, checks the
loaded variant hash, and catches expected scenario failures in its report.
A successful diagnostic process means evidence was collected, not that every
variant passed. Its default controls compare the accepted baseline, current
candidate and old damage routine. Other declared variants can be selected with
its `--variants` option through a declared analysis plan. Historical source
controls use commit8547a9c; compiling ablations assumes the current build's
matching ELF files. Never combine an old ROM with overwritten current ELFs.
Raw variant images, fixtures, logs and reports stay ignored.

The assembled70/70 run `20260916T021136.790340Z` passes with
`inputsUnchanged=true` on the same independently rehashed candidate
`29dd2384abff25f23827274bb0976b0f587f6c9c`. The expanded Mystic step passes2,368
assertions and36 native casts. Full reaction playback, Dancer/Passing Step
menus and AI, Geomancer playback/AI/field cold saves, cross-class checks and
linked-code relocation checks all pass. This supersedes the earlier failing
assembled candidates for this bounded source batch. Root reviewed the exact
ratio math, snapshot ownership/packing, support-query equivalence, builder
bindings and actual test scope; unresolved items below remain open.

## Remaining implementation and acceptance

The14 native command implementations, enchanted primary Fight carrier,
Magic Shell and Spell Parry effects, native descriptions/menus, lesson AI,
laws and dedicated cold-save/campaign scenarios remain unfinished. Readiness
flags and action classification are foundations, not implemented abilities.
No new command rows are claimed by this batch.

Spellweave currently commits at each native A433C action transaction. Whole
Doublecast grouping still needs implementation: both subcasts must use the
previous voluntary action's category and update the sequence once. Static
native inspection finds A433C called by A8194; the Doublecast controller calls
A8194 at95B60, versus95BB8 for an ordinary action. Its selected action is at
controller+A6, subcast indexAF and selected subactionsAA+2*index. These are
investigation pointers, not an authenticated grouping hook or acceptance.

Fresh-game/name-entry heap acceptance remains required. The earlier audit in
`ap-copy-storage-review.md` found that even the battle heap constructor is used
by the name screen and that large global reservations can suppress its keyboard
allocation. This batch's battle fixtures do not close that issue. A future
allocation design must prove the opening, menus and campaign as well as combat;
unchanged memory guards alone cannot prove successful native allocations.
