# Tactical AI evaluation baseline

This is the evaluation-first checkpoint requested before improving general AI.
No gameplay code, enemy scaling, ROM, release channel or player save changed.
The reference remains `8d7439c`, ROM SHA1
`7bbd46a45bcaab5482d45cb4d4965bb291045512`.

## Initial findings

The [scenario specification](../scripts/ai-tactics-cases.json) contains 12
situations with seeds 0, 5 and 18: 36 native planner decisions, 90 individual
assertions. The reference passes 32 decisions and 85 assertions. Remaining
failures are desired policy improvements, not automatically proven engine bugs:

| Scenario | Passing seeds | Remaining result |
| --- | --- | --- |
| Melee finish against the sole surviving 1-HP enemy | 0, 5, 18 | None |
| Caster favors stronger magic | 0, 5 | Seed 18 chooses Fight |
| Caster conserves MP for a free finish | 18 | Seeds 0/5 choose Thundaga/Blizzaga |
| No-MP fallback | 0, 5, 18 | None |
| Silenced fallback | 0, 5, 18 | None |
| Heal the critical ally | 0, 5, 18 | None |
| Revive the KO ally | 0, 5, 18 | None |
| Cleanse the silenced allied caster | 0, 5 | Seed 18 chooses Auto-Life on another ally |
| Avoid ordinary HP healing at full health | 0, 5, 18 | None |
| Avoid redundant Protect/Shell | 0, 5, 18 | None |
| Archer finishes outside hostile adjacency | 0, 5, 18 | None; Boost is allowed |
| Avoid an elemental blast covering a fragile ally | 0, 5, 18 | None |

The failing strong-magic decision still discovers all nine elemental spells.
Its diagnostic recipient rows value basic elemental spells at 134 versus
Fight at 74 against the nearby control target. This narrows the next inquiry
to later ranking, willingness and placement; it does not establish which
instruction caused the chosen turn. Recipient rows do not prove global
optimality or actual damage, and the no-cost knockout preference is a policy
to evaluate against hit probability as well as damage.

## Contract and reproduction

- [Runner](../scripts/evaluate-ai-tactics.py),
  [declared plan](../scripts/ai-tactics-test-plan.json), and
  [baseline](../scripts/ai-tactics-baseline.json).
- [Evidence validator and rejection tests](../scripts/test-ai-tactics-contract.py).
- [Read-only native forecast diagnostics](../scripts/native_ai_eval_probe.py).

All runtime execution goes through `Test Expansion.ps1`. The fixture prerequisite
is the existing `ai-timing-fixtures` step. Reuse it when its authenticated ROM
matches; otherwise build fresh own-ROM allocations first:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/ai-timing-test-plan.json -Only ai-timing-fixtures
& '.\Test Expansion.ps1' -Plan scripts/ai-tactics-test-plan.json -Only ai-tactics-observe
```

Observation records all desired failures and exits successfully only when the
harness completes without a hard error. Its `accepted` flag means collection
succeeded; inspect `qualityPassed`, the counts and every failed check. It is
not a claim that the tactical suite passed.

For subsequent AI candidates, after their own fixtures and both timing profiles
have been measured, run:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/ai-tactics-test-plan.json -Suite ai-tactics
```

This executes the ratchet, validates its evidence, and runs the existing timing
gate. The ratchet preserves **each passing assertion for each seed**, including
passing parts of otherwise failing cases. It accepts newly passing desires but
rejects any lost green assertion; an improved total cannot hide a regression.
The tactical per-decision allowance is at most 5% above the reference frames.
Missing/duplicate cases, changed inputs, changed assertion coverage or changed
evaluation code require investigation rather than silent baseline refresh.

The contract also pins the latest optimized timing workload: fully learned mean
4.1871 seconds and starting-skills mean 1.5557 seconds, using a separate 5%
per-decision limit around those exact measurements. It does not inherit the
older release's looser frame limits. Existing forecast correctness and original
timing gates remain unchanged. Reuse byte-identical ROM evidence at this
evaluation-only checkpoint; measure both profiles after gameplay changes.

To expose the remaining red tactical tests without replaying the game:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/ai-tactics-test-plan.json -Only ai-tactics-quality-gate
```

That strict gate intentionally exits nonzero on this baseline. The separate
`ai-tactics-strict` runtime step performs fresh collection with the same all-green
requirement. Do not put either strict step in a baseline-preserving suite until
its desired cases have passed. Failures are recorded, not skipped or relabeled.

## Fixture safeguards and limits

Each case loads the exact-ROM native Giza battle and uses a real enemy allocation
as the focus. Original job combat inputs and mastery are declared before planning.
Beneficiaries remain members of the existing native enemy cohort. Positions
exchange existing legal tiles/elevations, without overlapping units or drawing
synthetic maps. Non-focus units Wait before the focus activates. Both native
cohort lists are checked against the declared factions after construction.

Pin the RNG once at the native constructor using `PlannerSeed`; execute every
instruction and measure video frames through phase 8. Never inject scores,
candidate rows, destinations or decisions. A private ARM clone can query
recipient forecasts without advancing or writing the live core; its native
queries must preserve canonical units and RNG. The diagnostic `usable` field
is the raw ability-admission helper result: Fight is a special implicit action
and that helper returns false for action zero. Final action validity is checked
against the actual discovered candidate list, not this diagnostic field.

Retain complete reports, start/end states, end screenshots, final RAM, input
receipts, cohort membership, forecasts, seeds and per-phase traces under ignored
`build/expansion/ai-tactics/`. The source baseline contains only hashes, test
results, decisions and frame limits; original game bytes are never committed.

These are first-decision evaluations for four original jobs on one native map.
They do not prove action playback, resource payment, every class, missions,
enemy scaling, threat-map positioning, multi-turn coordination or campaign
difficulty. Healing/elemental footprint checks cover this corpus's radius-one
geometry; they are not a general effect-recipient simulator. Add dedicated
execution tests when the production change affects execution or resource use.

## Evidence and rejected draft

- Retained baseline run: `20260928T041612.332551Z`.
- Tactical report: `build/expansion/ai-tactics/20260928T041613.201112Z/report.json`.
  This final collection normalizes the scenario JSON to Git's required LF
  bytes. All 36 decisions, timings and final EWRAM exactly match the preceding
  collection `20260928T040711.927060Z`; normalization changes no game inputs.
- Final contract and retained timing gate pass in `20260928T041915.734943Z`;
  the validator's 26 positive/counterexample checks pass, with no regressions.
  Strict quality gate `20260928T041939.608187Z` intentionally fails on the four
  remaining decisions, reporting 32/36 and no baseline regressions. An earlier
  validator run exposed a Python module filename/import mismatch; that harness
  error was fixed before these final checks.
- The diagnostic clone pass matches all 36 decisions, frame counts, canonical
  inputs and final EWRAM from the preceding corrected-cohort collection
  `20260928T040126.241483Z`. Only the archer outcome predicate changed: a safe
  Boost is valid positioning, so requiring an immediate hostile target was
  removed before freezing the contract.
- Draft `20260928T035750.640807Z` is **not** a baseline. It demonstrated that
  changing a canonical control bit does not move a unit between native battle
  cohorts. Its apparent support failures are invalid. Its free-finish case
  also allowed competing multi-target damage; the final case leaves only one
  living opponent. Preserve these drafts as evidence of test design corrections.

## Gradual improvement order

1. Trace the existing red decisions through admission, row ordering,
   willingness and placement. Compare native forecasts and legal alternatives
   before changing a score; do not special-case seeds, unit slots or test IDs.
2. Make one coherent production policy change, retaining the native law,
   affordability, ownership and forecast-purity boundaries. Verify affected
   custom classes with their existing deterministic consumer tests as well.
3. Run the tactical ratchet and targeted correctness tests, then both timing
   profiles and timing gates. The old timing gate also requires vanilla-identical
   decisions: a deliberate improvement there needs a separately reviewed
   tactical assertion, not removal of the comparison or an automatic exception.
4. After reviewing new passes, explicitly promote their assertions into the
   source baseline. Never regenerate it from a failing run just to clear a gate.
5. Extend the corpus with mixed expansion classes, harder terrain, protection,
   disabling/status value, movement-only turns, objectives and turn-to-turn
   coordination. Keep these separate from any later enemy-level adjustment.
