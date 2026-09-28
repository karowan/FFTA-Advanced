# Fully learned AI planning target

The best accepted local candidate averages **4.1871 seconds** for fully learned
jobs, down from **5.2363 seconds** at the start of this task (20.0% faster).
**The requested under-four-second mean is not reached.** Vanilla averages
3.1295 seconds in this workload. Original starting skills now average 1.5557
seconds, versus 1.9198 at the prior checkpoint and 1.1929 in vanilla.

Final ROM SHA1: `7bbd46a45bcaab5482d45cb4d4965bb291045512`.
This is a local candidate on `codex/ai-forecast-followup`; no release, launcher
promotion, player-save modification or game launch was performed.

| Fully learned job | Candidate mean (s) |
| --- | ---: |
| Human Soldier | 3.3932 |
| Moogle Black Mage | 6.2506 |
| Nu Mou White Mage | 3.5215 |
| Viera Archer | 3.5829 |

Scope: four original jobs, seeds 0/5/18, twelve paired decisions per skill
profile on the fixed Giza fixture. One AI focus actor faces ten player-controlled
Wait units and the judge. This is not a campaign or 6-vs-5 average. Timing covers
native planning phases 0 through 8, excluding camera setup and attack playback.
The maximum fully learned candidate turn is 6.3287 seconds. Under four seconds
for every turn would be a different target; vanilla Black Mage itself averages
about 4.46 seconds. Available actions and final choices match in all 24 pairs
across the two profiles. Search breadth, abilities and timing budgets are intact.

## Final implementation and acceptance

The retained changes consolidate authenticated snapshot-bank and compound-copy
access, preserve frozen neutral snapshots, and bypass neutral modifier chains
only after proving every relevant live/captured flag empty. Real results,
deferred barriers and live Exposed behavior retain their existing calculations.
Copied terrain/trap scans use their exact owned cohorts; status scans can reject
an empty custom-icon record as a group. Aligned word transfers retain a byte
fallback. Stack-scoped ownership borrowing never caches values or admits a
forged interior heap pointer. The new four-byte transient root is explicitly
reserved and checked empty after cold load.

GCC O3/unrolling on measured hot modules plus LTO produces 148,868 bytes within
the 262,144-byte reservation. All 520 native exports remain, with 158 imports and
722 installed entry patches. Final LTO stack receipts show snapshot begin 248,
unit copy 216, evaluated init 104, native stage 96, neutral query 64 and trap
query 64 bytes. The existing guarded stack-result fallback remains 904 bytes;
the full native effects/fixture/save checks passed with the new linked code.
These receipts bound individual frames, not an exhaustive call-graph proof.

Final evidence (raw files remain ignored):

- Fully learned timing and exact-RAM profile replay:
  `build/expansion/test-runs/20260928T015443.784886Z/report.json`;
  `build/expansion/ai-timing/measure-20260928T015516.111824Z/report.json`.
- Eleven-step assembled effects, AI, movement, UI, learning, laws, status and
  cold-save acceptance:
  `build/expansion/test-runs/20260928T020350.355777Z/report.json`.
- Expanded binary equivalence, starting-skill timing and unchanged timing gate:
  `build/expansion/test-runs/20260928T020531.578106Z/report.json`;
  `build/expansion/ai-timing/budget-20260928T020623.711370Z/report.json`.
- Constructor/action-list exact replay passed in the first step of retained run
  `20260928T020453.754331Z`. Its next step rejected stale starting-skill evidence:
  the plan ran the budget gate before collecting the new profile. Move the gate
  after measurement in plan order; the final run above passes. No limit changed.

Equivalence covers 241 capture/inheritance variants, 240 full damage-stage cases,
36 absent-actor/target estimates, 1,456 status-carousel cases, 300 complete copy
comparisons plus six invalid-signature cases, 288 trap cases, and independent
copied-field outcomes. Nested ownership, freed/reused/forged copies, unaligned
sources, frozen values and parent restoration are checked directly.

The remaining largest per-job gap is Black Mage. The final read-only frame
profile still samples temporary-owner retirement, workspace lookup and heap
authentication, alongside native code and VBlank/main-loop waits. Samples are
leads, not exact time attribution. Further work should trace those allocations'
complete lifetimes before attempting broader reuse; removing ownership checks
or reducing the planner's candidate list is not an accepted shortcut.

## Experiment record

The user requested a mean below four seconds on the existing fully learned
benchmark. Start from local commit `c8bc3be` (5.2363 s; vanilla 3.1295 s).
Published v0.7.7 and its play/save channel remain unchanged.

## First experiment

Consolidate snapshot extension/medicine array access around a single validated
workspace view. The view is local to a synchronous getter/setter and retains
the current manager, allocation, pool and exact snapshot-owner checks. It is
never cached across calls or mutation. Group a new record's three flag writes
and its enablement reads. Compile the measured ownership/snapshot plumbing at
`-O2`, retaining the native ABI, binary reservation and stack-usage receipts.

Candidate: `dbe3dce6ddb25eac4abccc89216bf5b115fde0a4`.

Before runtime verification: run `cp-effects` for real snapshot, cross-class
modifier and barrier consumers; `cp-fixture` for cold native construction and
stack/rendering integrity. Then run `ai-forecast-fast` for frozen projections,
binary equivalence and forged/freed/reused copies, `ai-timing-fixtures` to
create independent native states, and `ai-timing-original-jobs` to measure
the exact fully learned workload. Further changes depend on those results.
Final acceptance must cover both skill profiles and `ai-timing-budget` without
loosening existing budgets, plus affected copy/save lifetimes.

The first experiment passed those targeted checks and measured 5.0117 s.
Evidence: `build/expansion/test-runs/20260928T003600.566611Z/report.json` and
`build/expansion/test-runs/20260928T003646.304586Z/report.json`.

## Scoped temporary-unit ownership

The second experiment borrows an authenticated evaluated-unit container during
one synchronous provider/formula group. Its scope lives on the current stack;
the root at `0x0203ff88` is outside the inventory and existing transient roots.
The original heap-chain check admits the container before publication. Every
read retains stack/self, exact unit and container-tag checks. No status value
is cached. Scope exit restores its parent; copy, free, allocation and owner
reset invalidate the chain so an old scope cannot resurrect it. Use only
around the audited synchronous flag capture and damage modifier calculations,
never around native execution or an allocator.

Re-run `cp-effects`, `cp-fixture`, `ai-forecast-fast`, `ai-timing-fixtures` and
`ai-timing-original-jobs` for this changed lifetime. The equivalence check now
also covers independent nested views, live record reads, copy/free invalidation,
no resurrection on exit, and rejection of a forged interior container.

Candidate `cf714a7dbebb9485d4626b717a25ac001fb42334` measured 5.0298 s;
borrowing solely around formula/provider groups did not improve the mean.
The first fixture run stopped at its old `ff88` canary: the explicitly reserved
four-byte root now occupies those bytes. The guard now starts at `ff8c`; cold
save acceptance additionally requires the new root to be zero.

The next revision groups source/destination ownership during the copy hook's
own fixed record writes (after invalidating caller scopes), and source reads
before initializing an evaluated unit. It also proves when the full snapshot
providers must be zero: no native status, no custom support/reaction, no owned
effect bytes, Exposed/Wound or Refuge. Movement-ledger bytes alone cannot
enable a modifier without a custom support. Preserve Spotter adjacency capture
even on the fast path and retain full capture for every uncertain case.
Use the same targeted checks, plus direct full-provider versus captured-flag
comparisons for empty state, all effect bytes, native statuses and R/S rows.

This candidate measured 4.9084 s after correcting a benchmark input boundary.
The retained constructor trace proves a main-loop RNG call can occur after
the frame-sampled phase-zero seed and before candidate construction. It changes
native random ability inclusion. `ai_planner_seed.py` now applies the declared
seed at native constructor entry, once, without skipping instructions or
changing subsequent RNG. The timer still includes all phase-zero setup work.
All twelve vanilla frame counts remain exactly the previous workload; all
paired action lists and decisions now agree. No budget was loosened.

The next experiment retains neutral query snapshots instead of dropping them
when all job modifiers are zero. Otherwise every subsequent factor re-runs
full providers on the same units. Capture, copy inheritance, nested queries
and retirement keep the existing lifetime. Verify effects, fixture and full
provider equivalence before paired timing; zero-provider captures now also
exercise a real active frame.

Retaining neutral frames alone measured 5.0382 s. Bypassing the neutral
modifier chain for original-action QUERY consumers lowered that to 4.6670 s.
The proof checks both exact captured units and all four modifier banks. Physical
forecasts still read live Exposed, as the pre-existing factor does. Real RESULT
and deferred-barrier consumers never take this shortcut. Complete Fire, Throw
and Hurl stage outputs match the old binary, including post-capture Exposed.

The next grouped revision authenticates a copied terrain cohort once and
traverses its explicit record stride, preserving the same 1/2/13-unit owner
domains without copied-to-live fallback. Original physical actions reject the
custom-definition lookup immediately; generated assertions prove every table
row is outside the original action range. Compile the sampled damage/terrain
hot modules for speed within the fixed ROM and stack limits. Before timing,
run effects/fixture/forecast checks, including old/new copied-field queries.

That batch measured 4.5484 s with unchanged paired lists/choices. Next replace
byte-at-a-time clearing of aligned owned snapshots and copying of aligned
evaluated-unit bodies with explicit alias-safe word transfers. Unaligned
sources keep the original byte path. Verify exact body copies and full native
effects/fixture/forecast tests before another paired timing/profile run.

Word transfers measured 4.4912 s. The next build uses GCC link-time optimization
while explicitly retaining every exported native hook. No saved ABI or native
planner budget changes. Inspect final LTO stack-usage output and run the same
effects/fixture/equivalence/timing checks; a successful candidate additionally
requires assembled copy/save/mixed-class acceptance before a commit.

LTO measured 4.4271 s. The next candidate authenticates each transfer's two
complete state views once, preserving canonical, evaluated and ordinary copy
layouts. Unknown/uninitialized sources retain the old clearing path. Non-unit
transfers reject before owner authentication. Run cp-effects/cp-fixture,
ai-forecast-fast (300 cross-domain transfer comparisons, full EWRAM), then
fresh paired timing. No test or engine change while those runners hash inputs.

The complete-copy candidate f482cc733d5240d123014864fa81183b4322bdb5 passed
300 byte-identical EWRAM transfer checks and measured 4.4201 s. Next avoid
live-provider calculation for inherited snapshot records that are immediately
overwritten. Copy all frozen banks through one source/target pool view. The
forecast test now checks 241 buff/status/lesson variants through copy, self-copy,
nested inheritance and parent restoration. Run the same targeted checks and
paired timing/profile; do not change the search or measured workload.

Inherited-bank optimization preserves all tested values but timing stays 4.4201 s.
The next batch covers the actual unsnapshotted native spell finalizer: prove
empty live modifiers only if there is no active snapshot; never fall back from
an active unrecorded unit. Trap scans authenticate one canonical/copied cohort
per tile and skip empty trap records before unit queries. Validate full stages
with and without snapshots, 288 trap/domain/timer/status cases against the old
binary, cp-effects/cp-fixture/cp-movement and paired timing/profile.

The next candidate measured 4.3810 s. A retained-turn instruction trace identifies
638 plain-unit checks, 99 unpaired native estimates, and 128 status-carousel tail
queries costing 2.6 million cycles in Black Mage seed 5. Extend the neutral proof
to absent actor/recipient (remaining units still checked), tighten equivalent
zero-byte scans, and return the original Exposed/Wound status tail when a record
proves all custom icons absent. Check null-pair full-stage equivalence, 1456
status-carousel cases, effects/fixture/status records and timing. LTO artifacts
now use the ignored build directory as cwd, avoiding a Windows wrapper-args
filename accidentally emitted into the repository root.

The tightened candidate 991ec258617e4551bdc9e475f082fb8ae0558bc5 measured 4.2457 s.
Its status, null-pair, movement and full-provider equivalence checks pass. Try
O3/loop unrolling for measured hot modules within the same ROM reservation,
with compiler output and final LTO stack review. Run effects/fixture/forecast
and paired timing. Keep only if faster and final assembled tests pass. Timing
harness cleanup now restores the seed controller on exceptions and requires
one declared constructor seed in the acceptance gate; diagnostic replay supports
both historical and corrected-boundary reports.

O3/unrolling measured 4.1871 s with all targeted checks passing. The next batch
borrows temporary-unit ownership during unsnapshotted neutral checks and avoids
re-reading Updraft after the complete record was already proven zero. Field
queries defer native map geometry until a live nearby field can match. Run
cp-effects/cp-fixture/cp-movement, forecast equivalence (including copied fields
and absent actor/target), then paired timing/profile before final acceptance.

The last experiment measured 4.1940 s, slightly slower than 4.1871 s; revert
its engine changes and retain the O3 candidate. Rebuild must reproduce SHA1
7bbd46a45bcaab5482d45cb4d4965bb291045512 before reusing its full-skill timing.
Final acceptance: run the eleven-step chemist-progression suite. This completed
milestone changes shared snapshot admission, compound copies, transient owner
lifetimes and linked compiler output; effects, AI, UI, movement, laws and cold
save consumers are all affected. Then run ai-forecast-fast (including invalid
storage/bank signatures), ai-timing-starting-jobs, ai-timing-action-list-audit
and ai-timing-budget. The first 12-pair full-skill timing remains applicable to
the identical final ROM; do not rerun it merely for documentation edits.
