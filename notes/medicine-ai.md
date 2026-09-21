# Medicine AI and shared combat stack audit

September 16, 2026 Pacific. Candidate
`12f790448f2fc95e259b78a403895ce0320468d2`.

## Implemented behavior

All ten Medicine commands enter native AI discovery. Six previously inherited
an Item donor's no-AI byte. Admission now requires a living, unconfused,
non-Petrified actor with an exact party ownership token and a stocked complete
recipe. Enemy ownership cannot spend player inventory. Silence remains allowed.

Recipient rows and placement scores use actual capped HP/MP recovery, the
Pharmacology/Recuperation formula, ordinary half-HP revival, absent protection,
and the actual cure domain. Cureall includes the five custom ailments and
excludes beneficial Conceal and Last Resort. Already satisfied benefits score
zero. Native consideration and status heuristics remain; AI may decline a
useful action on a particular turn.

Field Remedy chooses one stocked cure that removes an existing ailment. High
Tonic compares Hi-Potion and X-Potion, keeping Hi-Potion on equal benefit. Each
command still occupies one native 20-byte row. The selected item reaches
forecast, native decision publication, execution and the existing atomic
recipe payment. C48A4's three-argument recipient gate normally substitutes a
weapon; the new guarded entry admits Field Remedy using its exact cure donor
and ownership policy. Unrelated actions enter the original routine without
an additional C stack frame.

Inoculation's AI category uses the existing custom-benefit filter and checks
its own state. Single-target Medicine placement retains its native chosen
origin and beneficiary. Long Throw could leave the published destination on
an adjacent empty tile; completion now publishes the actual beneficiary only
after the public range/height/line-of-sight gate accepts it. Mist retains its
area center. This correction has native placement evidence; this group does
not claim a new rendered five-tile Long Throw scenario.

## Shared stack fixes

The compiled Geomancer choice search reserved 764 bytes even on its ordinary
action fallback. Dispatch now excludes ordinary commands before entering that
matrix. No Geomancer choice algorithm or saved data changed.

Playback also exposed an independent 820-byte snapshot in real Fight
resolution. A native audio interrupt could cross into resident IWRAM renderer
code. A paired diagnostic with identical saved inputs, frame-exact Wait keys
and executor seeds reproduced the first overwrite at frame 4495 both with
the full result recorder and with a minimal RNG-only entry. The latter had
no recorder frame during execution. Stack evidence led through field/peer
lookup under the real Fight preview, rather than medicine execution.

That snapshot now uses the existing eight 824-byte owned storage slots, as
other forecasts already do. The stack lifetime token and snapshot retirement
remain explicit; real Fight's deferred barrier value is published to the
enclosing result after the query retires. Existing storage exhaustion remains
bounded. No RAM reservation, save schema or game balance formula changed.

## Current verification

Report timestamps below use the `20260917T` UTC prefix.

| Report | Verified scope |
|---|---|
| `022422.591339Z` | Assembly, captures, 925 native combat checks, Dark Knight payment/lifecycle checks, 415 storage checks, 3,622 Fight assertions across 1,328 native casts, and 15,202 Fight-preview assertions passed. Medicine rows passed 2,406 checks and 100 native placement scenarios passed 629 checks, including Long Throw and Mist exclusion. |
| `022422.591339Z` | The playback step retained seven successful medicine casts and intact renderer/handoff checks across all ten cases, but the whole step failed because three chosen seeds did not cast. This report remains failed. |
| `022919.721512Z` | A bounded remaining-case sweep retained successful Field Remedy at seed 18 and High Tonic at `0x87654321`; Guarding still lacked a positive cast. This whole report remains failed. |
| `023047.869485Z` | Guarding sweep passed 32 checks: a no-cast control at `0x80000000`, then an actual Protect/Shell cast at `0x01010101`. |
| `023311.113752Z` | Evidence aggregation passed 152 checks for all ten commands against their raw saved inputs/results, exact recipe debits, expected effects, renderer code, retired choice roots and current-ROM/instrumentation hashes. It reuses verified positive cases without relabeling failed sweeps. |

The ten fixed positive seeds are 5 except Field Remedy (18), High Tonic
(`0x87654321`) and Guarding (`0x01010101`). The default playback script now
declares those inputs. This group has ten individually verified positive cases
across retained reports, not a newly repeated all-positive playback run.

Reproduce the grouped build/medicine gate with:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only @('test-medicine-turns')
```

For an unchanged, verified image and capture, use `test-medicine-ai-cached`,
`test-medicine-search-cached`, `test-medicine-choice-turns-cached`,
`test-medicine-turns-cached`, or `test-medicine-evidence-cached` as appropriate.
The evidence aggregator requires actual current-ROM playback artifacts. It
cannot promote an old ROM's evidence to a changed image.

The shared stack change justified the additional localized IDs
`test-mystic-knight-fight`, `test-mystic-knight-fight-preview`,
`test-integrated-dark-knight-batch` and `test-battle-workspace`. No full
integration suite, cold-save sweep or campaign run was needed for this group.

## Diagnostic history and remaining scope

The initial `015133.732928Z` audit exposed missing discovery, stock/ownership
checks and redundant healing. `015813.471317Z` hit the guarded central code
limit; the choice helper moved to the existing reserved code bank.
`015900.919033Z` passed the first 612 checks. Expanded checks in
`020417.008119Z` and `020622.465444Z` exposed the separate C48A4 recipe path.
`020937.639434Z` passed rows/placement but caught the renderer overwrite.
`021253.969153Z` exposed the Long Throw destination issue;
`021609.625907Z` confirmed that fixing placement/AI frames alone did not resolve
the real Fight spill. `021903.054690Z` was an inconclusive diagnostic with
unforced execution RNG; the matched-input `022100.038984Z` comparison isolated
the real spill. Keep these distinctions and the raw reports.

Pinned `test-medicine-stack-trace` and `test-medicine-trace-384/386/392` are
historical diagnostic tools, not release gates. The latter are pinned to the
recorded 12f790 source capture; subsequent additional playback directories
must not be guessed as replacements. `022702.469771Z` and
`022828.174590Z` distinguish discovery, native willingness, later status
heuristics, placement and execution. Those traces support retaining native
randomness rather than changing balance to force a test cast.

A06 remains open for other ordinary attack/status decisions and further shared
support combinations. Final mixed-job/campaign/acquisition/release acceptance
remains on `IMPLEMENTATION-CHECKLIST.md`. This medicine audit does not establish
the entire expansion or every possible Chemist build as complete.
