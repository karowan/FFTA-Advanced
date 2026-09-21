# Continuous paid recovery and repeat claim

Candidate `eabce3b98536510e40a8ec5893ecd9bd2996566c`; no gameplay bytes changed.
Run `20260917T044109.404300Z` completes the checkpoint chain with121 recorded
assertions, including retained earlier-phase checks. This is one continued
player-input timeline, resumed from authenticated captures after harness fixes.
It is not121 unique independent scenarios or a full-suite pass.

## Behavior verified

The initial disposable fixture supplies original game-clear/source22 eligibility,
50000gil, missing Materia Blade and level50 Ford. After that preparation, only
controller input changes gameplay. Native readers used for map coordinates and
eligibility run on separate copies; no returned state is injected into play.

1. Native Cyril pub selection charges the displayed15000gil and dispatches Ford.
2. Actual travel advances all20 dispatch days. Native return/reward confirmation
   gives one Materia Blade, releases Ford and charges nothing further.
3. The original shop Sell menu removes that blade and pays500gil. All other
   equipment counts remain unchanged; the missing-copy predicate requalifies.
4. Ordinary travel retires the native30-day cooldown. No free copy is granted.
5. A second pub selection charges another15000gil. Another20-day trip and
   native return yield exactly one blade and return Ford again.
6. Normal Save followed by a fresh core using SRAM only preserves exactly the
   roster/AP, inventory/AP extension, quest items/gift receipts and20500gil.
   The saved blade suppresses another offer. Original mission-completion flags
   are not borrowed by either return. The original seed file is unchanged.

The second reward screen and final Continue frame were also reviewed: correct
Materia Blade text/icon,0gil/0clan-point bonus and20500gil on the world map.

This closes I10's shared repeated-paid equipment transaction gap alongside the
existing six-route entitlement, pub/payment/stale, return and cold-save matrix.
It does not play the original source mission or certify every campaign event.
Quest-item second-payment/full-bag paths remain a separate A01/V05 obligation;
previous single-payment, rejection and reposting evidence is retained.

## Reproduction and checkpoints

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-paid-recovery-cycle
```

For a failed run, use `-Only test-paid-recovery-cycle-resume`. The script records
completed phases and authenticates the prior report, candidate, seed, RAM and
state before continuing. A completed prior run can be retained without replaying
its finished phases. Do not alter gameplay inputs to turn a failed outcome into
a pass. A checkpoint is a saved output of the previous real phase, not a new
fixture with timers, rewards or payment forced to desired values.

Reports live under the candidate's timestamped `paid-recovery-cycle-*` folders.
The private `paid-recovery-cycle-latest.json` points to the newest run.
Each report retains the prior report path/hash when resumed. Preserve the whole
chain when carrying this evidence forward. Final SRAM SHA1:
`d15601895d955ee9f630807b2d411c21fb86a0e0`.

## Failed harness runs retained

- `20260917T043833.434940Z` / consumer`043834.179284Z`: initial preparation
  passes; the acceptance observer stops at tentative member selection. Fix:
  require actual away flag and fee debit before treating it as committed.
- `20260917T043916.545040Z` / consumer`043917.265862Z`: first actual payment
  and20-day return pass. The fixed shop-tab sequence selects shields because
  the native UI skips empty categories. Fix: inspect at most six native lists
  to locate the known item instead of assuming two Right presses.
- `20260917T044024.272449Z` / consumer`044025.008279Z`: actual sale passes.
  Travel cannot start while the shopkeeper's farewell is open. Fix: confirm
  that ordinary dialogue before world navigation.
- `20260917T044109.404300Z` / consumer`044110.140297Z`: retained prefix plus
  cooldown, second payment, second return and cold persistence all pass.

No gameplay source fix was indicated by these harness failures. Only unfinished
phases were rerun; no full integration suite or new build was needed.
