# Ordinary martial attack AI

September 16, 2026 Pacific; report timestamps below are UTC.
Current candidate: `eabce3b98536510e40a8ec5893ecd9bd2996566c`, shared base
`b26778520203359c3b129bcc025b92dd0e4c01f1`.

## Implemented corrections

- Last Resort's hostile area score now uses the same primary-weapon gate as
  its recipient row. An unarmed or Healer user cannot contribute an illegal
  strike's actor-buff value to the hostile search. Weapon-free self preparation
  remains available. Existing Last Resort contributes no new preparation bonus.
- Provoke's recipient row and area score reject an existing challenge from
  that exact caster. Another caster may still replace the challenge. This is
  a redundant-action check, not forced targeting or a strategic AI redesign.
- Native candidate filtering previously discarded Provoke because its effect
  94 exceeds the original switch's maximum of 92. The guarded hook at
  `080C3608..080C3614` accepts only action 373/effect 94 after ordinary
  willingness and exact effect compatibility. All other switch cases retain
  their original branches. It allocates no extra stack frame or persistent RAM.

Native command probabilities, damage formulas, costs, effects and save layout
are unchanged. The hook's expected original bytes are checked during assembly.

## Deterministic coverage

`scripts/test-martial-attack-ai.py` covers 30 attacks/status commands across
Samurai, both Dark Knight owners, Viking and the Soldier/Gladiator axe additions.
It uses the existing exact-ROM two-Geomancer capture, native admission
`08133E18`, recipient rows `080C2618`, scores `080BDECC` and recipient admission
`080C48A4`. It verifies both stack alignments, live input/RNG preservation,
row guards and retired choice scopes. Conditions include weapon absence/type,
Healer, Silence, MP, KO, Petrify, allegiance, relevant target statuses,
Last Resort, Bloodcasting, Composure, Opportunist and completed Follow Through
movement, restricted to each support's owning race.

An additional Last Resort control removes only the actor-buff descriptor in
private emulator memory, then compares its native first-stage value against the
real row/score plus exactly one new preparation benefit. The five weapon inputs
include no weapon, sword, Healer, katana and axe. These are formula/gate inputs,
not a claim that every tested current job can equip every family. It also checks
weapon-free self mode and restores every modified byte. Other attacks retain
exact original row/score policy; this differential alone is not independent
proof of every combat formula.

`scripts/test-martial-hostile-search.py` exercises 42 fixed Last Resort/Provoke
scenarios with actual native node construction `080C01D0` and its returned
callback. It checks weapon gates, same/other challenger, existing Last Resort,
Silence, MP, height, distance, blocked movement and reachable destinations.
The search must select the real target and a declared legal origin, without
modifying units, inventory, RNG or guarded scratch storage.

`scripts/test-provoke-ai-filter.py` calls the complete native candidate filter
`080C32C0` with native rows and eight fixed RNG seeds at both stack alignments.
It verifies successful compatible Provoke consideration, including Silence,
and rejection of KO, Petrify, redundant challenges, the native early law-block
flag and the actual equipped vanilla Immunity support. Comparison with the
unpatched switch proves the previous rejection and preserves native willingness
RNG. Nine other commands retain exact native filter outcomes. Forty explicit
switch-boundary controls cover effects 0/1/21/59/82/92/93/94/95/255, both
action identities and alignments, original continuations and live registers.

## Evidence and reproduction

- `20260917T025158.838617Z`: successful six-step assembly and exact capture;
  **13,256 attack assertions / 1,316 cases passed**. Its filter step failed
  in test instrumentation; the whole report remains failed.
- `20260917T025505.351732Z`: **3,986 filter checks / 976 native cases** plus
  the 40 switch controls; **285 placement checks / 42 scenarios**. All selected
  steps pass on the current candidate. Eight Provoke candidate acceptances
  occur across the ordinary/Silenced fixed inputs without forcing a return.
- Earlier `20260917T024827.157607Z` passed the expanded attack audit,
  placement, 2,470 martial-utility and 2,406 medicine checks on candidate
  `2e2b54c56a1b6cdaa4032173257d492b378efcc7`. Retain those neighboring-consumer
  results with their original hash; they are not relabeled as current-ROM runs.

Fresh assembly/capture and the two native audits:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only @(
  'test-provoke-ai-filter'
)
```

Once that preparation report exists, individual current-image checks use
`test-martial-attack-ai-cached`, `test-provoke-ai-filter-cached` and
`test-martial-hostile-search-cached`. The assembly verifier rejects code drift;
each test also authenticates its exact captured inputs. Reports live beside the
candidate as `martial-attack-ai.json`, `provoke-ai-filter.json` and
`martial-hostile-search.json`. The runner preserves full logs and input hashes.

## Diagnostic corrections and remaining scope

The initial `024243.217115Z` audit incorrectly imposed medicine-style Petrify
rejection on ordinary attacks. The complete audit now compares that admission
with native attack policy; a positive early row is not proof of final selection.
`024618.235762Z` additionally selected a cached verifier beside a fresh build,
before its immutable preparation report existed. Later runs reused the completed
preparation correctly; no identical rebuild was needed for diagnosis.

The original-switch comparison initially failed with fetch address `F8B3F000`
(`025158.838617Z`, diagnosed in `025324.547525Z`). Unicorn retained translated
instructions for a block spanning the edited inline hook. The control now
invalidates `080C3200..080C4800` whenever switching those bytes. The subsequent
`025406.680992Z` passes; the final run adds real Immunity coverage and repeats
only the affected filter and placement checks.

No new autonomous command playback, cold save or campaign sweep was run for
this batch. Candidate-filter acceptance is not an executed Provoke turn.
Prospective moved-destination scoring for Composure/Follow Through remains
separate from the completed-movement inputs tested here. Final mixed-job AI,
campaign/acquisition and release acceptance remain in the maintained checklist.
