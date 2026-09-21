# Movement supports and native AI policy

September 16, 2026 Pacific. Candidate
`eabce3b98536510e40a8ec5893ecd9bd2996566c`; no gameplay bytes changed.

The ordinary AI review is complete within the approved vanilla+ policy.
Composure and Follow Through work after real movement. A new optimizer that
compares their expected damage at every future movement destination is not
part of the approved class behavior, and is not being introduced.

## Why the earlier backlog item changed

The class specification promises the support conditions and accurate previews
before commitment. It does not promise optimal AI movement. A06 explicitly
requires legal/useful AI decisions without an unapproved strategic AI overhaul.
The older turn-support note listed prospective destination scoring as further
acceptance without first establishing the native planner's policy.

The deterministic trace `20260917T030016.483117Z` resolves that uncertainty:
native command scoring uses the unit's current position. The directional
`080BFDB0` and ordinary `080BEF28` search callbacks then choose destinations
using native geometry, facing, target-count and proximity rules. They do not
re-evaluate the command's damage at each origin. Merely changing the movement
support provider to read a guessed AI coordinate would be incorrect: the
observed score inputs still describe the unmoved unit and wrapper.

This is preserved native planning behavior, not a claim that the AI chooses
the mathematically best use of Composure or Follow Through. Their actual
bonuses follow the committed movement. Existing native execution coverage is
recorded in `notes/turn-supports.md`; final assembled acceptance remains R02.

## Current verification

`scripts/test-ai-movement-supports.py` uses the authenticated exact-ROM capture
and actual native node construction/search. Its six planning cases cover Fight,
Fire, Wind Draw, Crushing Blow and Reaping Arc across legal Human/Bangaa support
owners. Declared possible origins are (4,14), (5,14) and (6,14), with a target
at (7,14). The trace records the real score calls and position/ledger inputs.

It requires legal selected origins/targets and unchanged units, custom state,
inventory and RNG after planning. Thirty subsequent movement/preview cases
cover stationary, one-tile, two-tile, loop and undo behavior. They invoke the
authenticated native move/undo boundary, check exact 25/20 Composure or 27/20
Follow Through factors, and call the public preview `080B55CC`. Preview must
reach the support providers, preserve live state and retire temporary snapshots.
A loop counts as movement but not net displacement; undo restores eligibility.

`20260917T030346.216491Z` passes **174 checks**, six native planning scenarios
and thirty completed-movement/public-preview cases in 0.4 seconds of test time.
It reuses the current capture; no build, full suite, new playback or cold save
was needed. Raw traces, scenarios and results are preserved beside the candidate
in `ai-movement-supports.json`, with full runner logs and input fingerprints.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only @(
  'test-ai-movement-supports-cached'
)
```

These checks do not establish a new damage optimizer, new autonomous support
playback, or final campaign acceptance. They close the question about native
planning inputs and verify the boundary where actual movement affects previews.
