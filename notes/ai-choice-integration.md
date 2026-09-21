# Native AI choice transport

The available-action lists at133F70/134094 remain deduplicated action IDs.
Both native callers allocate40 halfwords; expanding these into menu options
would change their capacity and every downstream consumer. The later per-target
records are20 bytes each, inside an808-byte block with40 record slots.

## Forecast and publication

`C2618(row, actorWrapper, targetWrapper, action, extra, flags)` constructs one
native score record. It stores action/extra at0/2, effect count atA, and a signed
effect value atC. The native caller atC2816 appends only an applicable record.
The replacement retains one record for Forbidden Dance, evaluates its four
options using the original constructor, and keeps the greatest absolute native
effect value. A zero effect count has zero value. Native forecasts give all four
statuses the same default weight and do not discount an already-present ailment.
The wrapper therefore discards those refreshes and allied targets before
comparing rows. Ties follow menu order.
Native target/action ranking, MP and mastery filtering remain downstream or
upstream as before. This is an anchor-target heuristic, not an exhaustive search
for the globally best status across every possible cross.

`C01D0` copies the selected score record's action/extra into node8/A. Its caller
`C09B0` is a call site inside theC045C coroutine, not a standalone function.
The selected node is at02015488. `C0B46` publishes node8/A into manager54BE/54C0;
`9399C` and `939A8` read those into the battle managerA6/A8. The existingA447A
choice hook then carries the extra into actual action execution without Item
semantics. No extra AI publication hook or saved choice is necessary.
During the interval after scoring, the forecast getter can read the completed
native decision only when mode8, successful node, published action/extra,
active wrapper and exact actor all agree. It also requires an AI-side unit.
This prevents the option disappearing while the AI finishes movement and
prepares its cast. Player-controlled units cannot borrow that decision.

NativeBDECC forecasts additional recipients while searching. It normally obtains
weapon operands, so the chosen option must be supplied to the existing chance
and magnitude hooks. Its wrapper admits only the current node's exact actor
wrapper, action and valid option; the same choice applies to every recipient.

## Ownership

The transient pointer at0203F728..0203F72B occupies unused reserved space after
the808-byte job bank and before inventory storage at0203F800. It points to a
synchronous IWRAM stack token with magic, self, actor, action and choice. The
getter requires an aligned live stack address, exact token identity and exact
actor/action. The wrapper restores the previous pointer on return. It does not
add saved bytes or write unit AP/status to transport a choice. Copied units
cannot borrow live-unit choices through a race/job/name match.

The Geomancer extension adds an explicitly scoped proposed position and a
previous-scope link. Its token has28 bytes; the root still has4 bytes. Position
bit16 identifies a supplied grid coordinate. Neither the actor's unit coordinates
nor its wrapper are edited while forecasting. After native publication, the
exact authenticated decision supplies the committed endpoint. Native planning
publishes before movement; using the departing wrapper here would temporarily
remove an element available only at the destination. UnitF6/F7 remain unchanged
until the native executor synchronizes them.

## Geomancer search implementation

The guarded hook atBEF28 replaces the generic center search only for376/381.
Other actions replay the native prologue and resumeBEF34. C01D0 still allocates
the node, movement map and4096-byte area buffer. NativeBE074 determines usable
origins; B4A1C constructs range and area lists, including terrain/height rules.
One usable origin is evaluated per callback; invalid origins are skipped
synchronously rather than spending a scheduler interval on every rejected tile. Node1B8 owns the bounded cursor and1C
the best utility. Successful candidates use the original1AC..1B1 coordinates,
facing and success flag, andA holds the chosen operand. C0B46 and the existing
native cast setup publish and execute those values.

Recipients come from the two native cohort blocks, each bounded to13 wrappers
and deduplicated by exact unit pointer. C48A4,12DBA8 and130200 retain native
target permission, chance and signed damage. The score caps damage at current
HP and healing at missing HP, weights by chance and penalizes allied HP loss
at twice the corresponding enemy benefit. Each option is shared across the
whole area. Gaia derives available elements independently at each proposed
origin. Torrent uses the same native98E7C collision helper as execution, with
a small spacing preference only after positive forecast damage and Water.
The scorer never consumes RNG or pays MP. Ties prefer less grid displacement.

This is a tactical heuristic, not globally optimal play. Upstream native action
ranking still selects an anchor/action record; the search optimizes that action. Gaia's preliminary row discovers each
potential element once within the native movement allowance, then uses native
forecasts to choose a beneficial row. This is deliberately optimistic about
paths; detailed movement-map acceptance is mandatory before publication. It
prevents an absorbed or ineffective departure-tile Wind forecast from hiding a
useful element available after moving.
Displacement forecasts use current occupancy, so simultaneous pushes and the
vacated caster tile are conservative estimates. Path-cost ties and multi-turn
positioning are not optimized. Full autonomous checks must demonstrate actual
choice, execution, payment and turn handoff, separately from synthetic movement
maps used to isolate the search contract.

The dedicated code section091ED600..091EFFFF follows the112x12-byte masks at
091ED000 and ends before the material catalog at091F0000. The linker and builder
check both code bounds and mask overlap, emit the two code sections separately,
and reject writable globals. Unused libgcc unwind metadata is discarded; this
freestanding ROM has no exception unwinder. No new RAM bank or save schema is
introduced. Native table-pointer relocation scans include both code sections.

## Reproduction

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite choice-ai`.
The row test uses native status eligibility and all16 combinations of preexisting
ailments, both stack alignments and several weapons. The full AI test starts
from the existing isolated native battle fixture, declares the actor's job,
mastery, formation and seed, and waits through native AI planning/execution.
It never injects an action, selected choice, path, score or effect result.
Existing player-choice and Passing Step AI tests run alongside it. The new cast
logger records MP immediately before the native executor: observing the start
of an AI turn is too early because native turn-start MP recovery follows.

Accepted combined run `20260915T233009.230130Z` passes65/65 steps with
unchanged inputs on ROM `12125306bbb0e786ab9067df7b45a54dfd41254b`.
The native row/ownership suite passes598 assertions and selects each of the
four options under its fixed ailment combinations. The full AI suite passes58
assertions: three learned turns select Blind, execute once, pay14 MP and hand
off; the unlearned control uses Fight. Full autonomous turns for the other
three options, broader tactical utility and terrain-dependent choices remain
separate coverage. Full-expansion status is inIMPLEMENTATION-STATE.md.


## Compiled table relocation safeguard

Do not scan a compiled instruction stream for address-shaped words without
its ELF classification. A real failure paired `ldr r1,[sp,#16]` with
`lsrs r2,r4,#4`: the aligned word09229904 fell inside a relocated job table.
The old scanner changed the instructions at11ED698 and destroyed the search's
node argument on subsequent iterations. `ELFData` now reads ARM mapping symbols
with `nm --special-syms` and explicit ELF OBJECT extents. Each compiled module's
table references are rewritten only at classified four-byte data locations.
Skipped instruction collisions and applied literal relocations are recorded
in the candidate manifest. September17 correction: the original-ROM broad scan
also corrupted139 data words. It is now constrained by authenticated native
load/literal provenance in native_table_literals.py, despite the absence of an
original ELF. See notes/native-status-equipment-transport.md for the repair,
retained failures and still-open assembled acceptance.

`test-integration-relocations.py` compares the two emitted integration binaries
against the candidate and rejects any changed word outside classified data.
It also verifies every recorded skipped collision still has its original bytes.
The search regression exercises the affected loop with native movement calls.
Run the `geomancer-ai` suite for this gate, callback geometry and full AI turns.


## Accepted Geomancer checkpoint

Combined run `20260916T001635.833530Z` passes68/68 steps with unchanged
inputs on candidate `15715d35dbe3c61b2ac95564df12cf012dcf97ec`.
The isolated search suite passes196 assertions, including all element and
cardinal choices, mixed-area friendly-fire avoidance, blocked/unreachable and
absorbed cases, original-action forwarding, exact endpoint forecasts and
unchanged unit/RNG data. Six native AI turns pass96 checks: two Torrent casts,
two Gaia Wind casts, a Gaia Fire cast after moving into a heat neighborhood,
and the unlearned Fight control. Learned casts pay exactly once, cause actual
enemy HP loss across the declared seeds, and hand off without player input.
All54 native player casts also pass1,873 assertions. The compiled relocation
check compares7,950 words. The earlier erroneous instruction collision is in
retained failing evidence; its exact offset is not a permanent code-layout
contract. Current code allocations are30,392 central bytes and1,408 Geo AI bytes.

The full-turn report binds each case to one of two private frozen instrumented
ROM hashes, rather than reporting only the last variant. Those ROMs, states,
images and raw logs remain ignored. This checkpoint accepts this implementation
batch; remaining expansion gates are recorded inIMPLEMENTATION-STATE.md.

Final review added a fixed assembly regression containing the identical word
as both two Thumb instructions and a real data literal. Classification must
reject the instruction location and accept the literal, independent of future
production code layout. Targeted run `20260916T003408.040786Z` passes7/7
steps on the identical candidate with unchanged inputs (7,950 candidate words
plus two fixed classification checks). The earlier combined evidence remains
applicable; no gameplay code changed after that full run.
