# Remaining reactions, songs and Updraft player flows

September 16, 2026 Pacific. Candidate
`eabce3b98536510e40a8ec5893ecd9bd2996566c`; no gameplay change in this
checkpoint. Tests authenticate the exact `fixture-two-geomancers` capture
against its preparation manifest and retain native racial sprites.

## Automatic reactions

`test-remaining-reaction-playback-cached` passes **1,073 checks**, 48 paired
playback cases and six actual suspend/cold-boot cases in
`20260917T031552.465129Z` (99.7 seconds). Private artifacts are beside the
candidate in `remaining-reactions-20260917T031553.120686Z`.

| Reaction | Actual positive result | Cold-save scope |
| --- | --- | --- |
| Gil Snapper | Native critical loses29 HP, awards14 gil; miss/ordinary hits award nothing | Gil and owned battle cap |
| Dark Ward | Paired Fire loses16 HP without reaction,12 with reaction, then grants Shell | HP and ordinary Shell |
| Nu Mou Auto-Potion | Selected Potion restores25 HP and consumes one Potion | HP, preference, owned state, inventory |
| Moogle Auto-Potion | Selected Hi-Potion restores50 HP and consumes one Hi-Potion | Same, with Hi-Potion preference |
| Nu Mou Auto-Cureall | Higanbana still loses30 HP; wound prevented for one Cureall | HP, wound absence, inventory |
| Moogle Auto-Cureall | Same result on the other native racial implementation | Same |

Paired controls equip/remove the mastered reaction before input. Actual
Move/Act/target/confirmation buttons drive the original executor and renderer.
The recorder supplies the declared RNG seed at execution entry and copies
completed results; it does not force hits, reactions, inventory, or saves.
Checks cover result ownership, exact payment, AP preservation, renderer code,
changing frames, no duplicate application during playback, and next-turn return.
Cold boots use the original candidate and its actual cartridge save, comparing
HP/MP, statuses, inventory, gil and owned records.

The exploratory Gil run tried seeds0 through18 and found the first critical at18.
The committed script retains only the observed miss/critical seeds0/18 for future
reproduction. Omitted ordinary-hit cases remain valid evidence; this input
selection refinement did not warrant replaying already-passed outcomes.
Chemist cooldown is checked immediately after consumption. Its turn lifecycle
may legitimately clear it before suspension; cold comparison uses the actual
state at suspension, not an assumed still-active lock.

## Bard commands and Updraft

Ten player cases complete: all eight Bard commands, Hide while silenced, and
Updraft. They select the actual command, preview/cancel without payment or
owned-state changes, commit, render, return to the menu and Wait normally.
Checks verify healing/cures, native statuses, timed song tags, positive Requiem
damage, other-ally-only Ballad recovery, and exact MP costs.

Updraft uses natural Giza terrain: caster `(7,4)` at height5, recipient `(7,5)`
at height3. It applies Move+1 to both, Jump+1 only to the lower recipient, and
no immediate movement. Native movement/Jump values are read on disposable
clones. No terrain height, buff result, save payload or timer is injected.

Battle Chant, Magickal Refrain, Nameless Song and Updraft each survive actual
suspend/cold boots. Both timed songs and Updraft then expire through exactly
two actual recipient turns; other actors' turns do not tick their timers.
Updraft's cached Jump and native Move return to their original values.

Evidence is a retained chain, not three newly complete suites:

| Runner report | Scope/result |
| --- | --- |
| `20260917T032215.064663Z` | Five songs pass; whole report fails at Hide's test input sequence |
| `20260917T032402.312653Z` | Remaining four Bard cases pass; whole report fails at the selected Updraft tile |
| `20260917T032624.684270Z` | Passes123 new checks: Updraft, four cold saves and three recipient-turn lifetime cases; reuses the nine retained Bard cases |

The first two reports remain failed. `song-traversal-20260917T032625.351333Z`
contains the final passing report, all ten case references and its preceding
report's hash/path. That report references the first five cases. The failures
were setup differences: Hide reaches confirmation with one fewer input, and
the initial height8-to5 target is rejected by the native range-height gate.
The corrected height5-to3 case is legal. No native gate or combat behavior
was changed to make a test pass.

## Reproduction and remaining scope

With exact assembled prerequisites and the authenticated retained fixture:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-remaining-reaction-playback-cached
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-song-traversal-playback-cached
```

If the second script stops after completed cases, use the declared continuation
`test-song-traversal-playback-resume`. It verifies candidate/instrumented hashes,
retains the source report identity, and selects unfinished player/cold cases.
It does not regenerate the ordinary fixture or replay completed commands just
to obtain a single green log.

Setup gives mastery, gear, resources, allegiance and Requiem's undead condition.
This is not acquisition/campaign evidence. Native frame progression and intact
renderer code do not certify every pixel, banner or animation theme. Informative
presentation review and assembled acceptance remain V01/A05/R02. Dedicated
Updraft cold/lifetime evidence closes that V02 subtask; other roster, slot and
lifecycle obligations remain open. No full integration, new campaign replay
or unrelated persistence matrix was run.
