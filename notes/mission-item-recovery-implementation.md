# Mission-item recovery implementation contract

Current follow-up: [`vanillaplus-final-paths.md`](vanillaplus-final-paths.md)
records the completed second paid recovery, full-bag rejection/replacement and
cold save on687ed5d4. The checkpoints below retain their original scope/hashes.

September 16, 2026. The 64-route recovery implementation is installed in
candidate `ea9ed600d38fb8b3a5662fc1f116852be8b97548`. It has bounded native
construction, dispatch, retirement, pub payment and cold-save evidence below;
actual five-day return/reward/full-bag/cold-save evidence below.
See `mission-item-dependencies.md` for the original
source ledger. This is part of approved VP-01, not completion of all A01.

## Preserve earned supply and legitimate costs

The64 finite/self-dependent candidates have only nonrepeatable original direct
reward sources and nonrepeatable consuming missions. Mission288 requires and
consumes two Magic Medals; all other candidate requirements use one copy per
mission. These properties were checked from the hash-verified512-slot ledger, not inferred from item names.
They permit recovery eligibility to use existing completion flags without a
new saved counter or a blanket consumption refund.

For each candidate item, compute:

- **Earned:** copies in fixed original rewards of completed source missions.
- **Spent:** consumed requirement slots in completed original missions.
- **Held:** copies in all64 native quest-inventory slots, including bound copies.
- **Required together:** maximum copies required by any incomplete or repeatable original
  dependent mission; zero if none remains. Stuffed Bear has a repeatable,
  nonconsuming dependent (383), so its completed flag cannot retire recovery.

A recovery offer needs `Held < min(max(Earned - Spent, 0), Required together)`.
For ordinary one-copy requirements this means no held copy, a positive earned
balance and unfinished dependent content. Magic Medal can recover its second
copy only after both original copies were earned. Return one copy at a time. If the player discards the replacement, the original
earned entitlement remains. After its legitimate use, the completed consumer
reduces the entitlement. A source that has not been completed contributes
nothing, even if its original posting has become visible. Do not use a generic
late-game flag as a substitute for earning the original item.

This distinguishes lost/rejected rewards from ordinary expenditure. Example:
completing one Adaman Alloy source and spending that alloy grants no early
replacement for the other original source. Losing that first alloy before
spending it does qualify. Two earned copies with one completed consumption
leave one recoverable entitlement. Quest-bound copies count as held. Never
ignore them to manufacture missing supply while dispatching. Wyrmstone remains unconsumed; Elda's Cup's
installed extra reward is retained unchanged. Their completed dependent missions
make further recovery unnecessary under this rule.

The24 independent repeatable-source candidates retain their ordinary sources;
their indirect input chains and actual availability still need review. The
above formula does not resolve link-only prerequisites, a never-completed
original opportunity that later disappears, or script-only item transfers.
Audit those separately before claiming VP-01 complete. In particular, Gold
Vessel, Eldagusto and Vermillion have original sources gated by flags1445/1446;
do not erase those conditions under the name of recovery.

## Installed native integration

Use a repeatable recovery dispatch with an explicit fee/duration and exactly
one quest reward. Preserve original sources, rewards, consumption and progress
flags. No automatic inventory deposit or silent replacement of another item.
Recovery should use ordinary native reward selection/full-inventory handling.
Recheck eligibility at acceptance as well as posting, since a cached pub offer
can outlive a new copy or changed quest state. Never affect an already accepted
dispatch's payment, outcome or reward merely because later state changes.

The original table has90 contiguous slots407..496 with zero bodies after their
ID halfwords, plus four at508..511. Slots497..507 contain disabled test data;
slot406 has real content. The routes occupy 407..470 and reserved ROM 0x1340000..0x135FFFF. They use no
new completion flags: both native completion hooks preserve original success writes
and skips those service IDs. The native explicit 300-mission list is unchanged.
All IDs fit both the cached 10-bit ID and dispatch-result 9-bit ID. Names use
original name pointers; a relocated second description bank preserves all 247
ordinary entries and appends native six-line descriptions. Central reservations
are in `shared-job-allocations.json`.

Posting, pre-list pruning and confirmation hooks recheck entitlement. Recovery
posting waits for a free native cache slot so it cannot invoke ordinary offer
eviction when all 64 slots are occupied. Linked
pruning removes only stale unaccepted offers in both displayed state1 and
undisplayed state2; accepted state0 and cooldown state3 retain native ownership.
Each service has a native base fee of 200 gil
(before ordinary town adjustments), five dispatch days, ten posting days and a
one-day cooldown after success, failure or cancellation. It supplies one quest item and no AP, gil or recruit reward.
There is no additional saved state.

## Targeted acceptance for the completed sweep

Implement the catalog, eligibility, posting/acceptance hooks, player text and
dispatch routes before running their combined focused checks. The retained
6,943-case native posting proof is reusable while its exact consumers remain
unchanged; it is not proof of the new feature.

The new deterministic plan should cover all64 entitlement rules and real native
consumption/completion transitions, both Magic Medal slots, original-only
controls, bound inventory,
no early copies, partial/multiple-source progress, legitimate spending,
lost/rejected replacements, completed consumers and stale offers. Add actual
native pub acceptance, successful/failed/canceled dispatch, full-inventory
reward confirmation, repeated recovery and ordinary save/cold load. Keep
source hashes and fixed input logs. This is one content milestone, not a reason
to repeat unrelated combat/AI suites.

## Retained evidence and remaining acceptance

Run `20260916T171534.772846Z` passed all four selected steps on the candidate
above: 5,213 recovery cases and 6,111 ordinary pub controls. The new recovery
matrix covers every source/use completion combination, held/bound copies,
native posting, field queries, actual description decoding, original text
preservation, mixed 64-node queues, both native acceptance stack alignments and
original-only completion writes. Reports: `build/reports/mission-recovery.json`
and `build/reports/mission-pub-gates.json`; immutable run logs remain ignored.

This proves boundaries and predicates, not a playable dispatch lifecycle.
Actual queue construction/list capacity, successful/failed/canceled dispatch,
reward rejection/full inventory, rendered text and save/cold load still require
their focused deterministic scenarios. The first run `20260916T171421.843417Z`
built successfully but failed a test oracle that confused mission mode selector
2 with rank selector 4; the corrected run reused unchanged assembly.

## Native lifecycle milestone

Candidate `84c9f8bfd94b0494c3746b5deb68039bbc3601fa` passes the final native batch:

- `20260916T173134.870891Z`: seven selected steps, including assembly and
  5,542 recovery cases. This adds 128 last-free/full-cache controls and 201
  checks of the second completion handler to the original matrix.
- `20260916T173204.830772Z`: four selected steps, 6,111 original pub controls
  and 326 lifecycle cases. All 64 routes use the full native generator and pub
  enumerator, retain their one fixed reward, assign a real saved roster unit,
  move to the linked queue tail, cancel and finish cooldown. Native day updates
  return each route on day five, never on a no-day update. Both success/failure
  retirement return the unit, preserve original progress flags, and permit a
  later missing-copy recovery after one cooldown day. Six native consumption
  cases cover both Magic Medals, Elda's Cup and retained Wyrmstone.

Successful retirement receives a controlled success argument. These cases do
not navigate the result screen, confirm acquisition, pay through the pub UI,
or save/cold-load a live dispatch. Those remain explicit next checks, including
full quest inventory and reward rejection. No campaign-completion claim follows.

Review found and fixed the separate cached-result flag writer at D1E9C; the
first event-result hook alone did not cover it. Success cooldown uses record
byte 3F, distinct from failure/cancel byte 40. Both are now one day. The static
ROM-delta script verifies no gameplay changes outside the declared recovery
hooks/data except equivalent linker veneer relocation. Full native dispatch
quality and reward confirmation still require player-flow evidence.

## Pub payment and cold-save milestone

Candidate `ea9ed600d38fb8b3a5662fc1f116852be8b97548` passes seven assembly/native
steps (5,542 cases) in `20260916T174834.698235Z` and four focused steps in
`20260916T174915.206391Z`. The latter covers actual pub selection, rendered
details, the displayed 300-gil town-adjusted payment, assignment of the selected
generic member, stale confirmation rejection, and 34 cold-save assertions.
Normal Save/fresh Continue preserves three accepted routes, including a second
Magic Medal and full quest inventory. This does not certify reward collection.

Real UI playback exposed payment at 5EA70 before the former acknowledgment
hook at 5EF18. The hook now checks the actual Yes branch at 5EE20 before debit;
rejection follows native No at 5EDE8. A copy acquired in slot63 after the final
dialog opens prevents payment and assignment, preserves the copy, and removes
the stale posting through ordinary list refresh. Native enumeration changes
state2 offers to displayed state1; pruning must cover both. Earlier assumptions
about that state and payment ordering were wrong and are superseded here.

Private reports retain fixed inputs, screenshots, save-state/RAM hashes and
candidate hashes. Failed diagnostic runs remain retained. The static ROM-delta
audit accounts for all 65,775 changed bytes against the prior combat candidate,
including seven equivalent veneers and 18 unchanged final call destinations.
No unrelated combat regression was rerun. Next acceptance covers actual return
dialogs, item collection/rejection/full inventory and repeated recovery.

## Actual return, reward decisions and repeat availability

On the unchanged candidate, `20260916T175913.817698Z` passes 22 assertions in
the focused return batch. A hashed actual pub acceptance capture travels from
Sprohm to Giza and Cyril using ordinary inputs, advances five native days, and
reaches the real success/reward screen. Ford returns, one Elda's Cup is awarded,
gil remains 4,700 after the original 300 fee, and all 512 mission-completion
flags remain unchanged. Ordinary world/dispatch flags are allowed to advance.

Two controlled full-bag variants start at that real reward boundary with 64
distinct valid other quest items. Native Swap/OK either replaces the explicitly
selected Magic Trophy with the Cup or discards the Cup and preserves every
held item. Both confirm Yes explicitly (native default is No), return the unit,
charge nothing further, and retain their exact inventory/roster/gil through
normal Save and fresh-core Continue. No native success call or reward injection
is used. Full bag setup is a declared inventory fixture, not a natural campaign.

`20260916T180047.442147Z` adds 14 assertions using those hashed cold captures.
Ordinary Giza/Cyril travel advances cooldown. The real pub offers recovery407
again after rejection and suppresses it while the Cup is held; no gameplay RAM
writes or forced posting calls occur. This proves repeat availability, not a
second paid dispatch through every menu. Native lifecycle matrices separately
cover all 64 routes. Remaining A01 work includes original Caravan Guard's
returned reward, the 24 indirect renewable chains, never-earned opportunities,
link/script cases and campaign reachability. Do not infer full A01 completion.

Reproduce via `Test Expansion.ps1 -Plan scripts/integration-test-plan.json`
with `-Only test-mission-recovery-return-cached`, followed by
`-Only test-mission-recovery-repeat-cached`. Both validate current assembly;
the first requires the same-ROM pub acceptance capture, the second its
successful hashed return/cold captures. Failed navigation/confirmation oracle
runs are retained; they did not require shipping changes or wider regression.
