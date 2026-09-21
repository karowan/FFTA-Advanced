# Approved behavior review

## Final A05 reconciliation — September 17, 2026

A05 is now accepted within its lesson/design scope. This reconciles the prior
root source review below with the completed V01–V05 evidence; it does not
claim a fresh replay of every historical case. Current candidate is
`1f197f6c8ca0a28445dd6c3fec245bacf5660df2`. Its only change since687ed5d4 is
the bounded field compositor; no lesson formula, item, job or save schema changed.

| Approved contract | Reconciled evidence |
| --- | --- |
| All129 lesson identities,158 racial records,85 teachers,10 job profiles, costs, growths, permissions and prerequisites | `installed-design-review.md`; current static run20260917T074520.692367Z passes2,131 checks |
| Actives, reactions, supports, caps, ordering and costs across all eight job concepts and axe additions | Prior root implementation review and corrected contracts below; named native and actual-player evidence in each subsystem note |
| Native text, choices, visible reactions and saber/rapier delivery | `final-presentation-review.md` (V01); current550-check exact help reuse; `mystic-knight-cold-lifecycle.md` |
| Equipment/AP learning, removal/mastery and job-menu persistence | `final-learning-acquisition.md` (V03), complete racial learning matrix and ten actual menu/cold flows |
| Transferable supports/reactions, ordinary attacks, native Doublecast and Combos | `final-combo-synergy.md` (V04),12,661 native combined checks, ten actual Combo flows and weapon-family playback |
| Copy, revival, original-job preservation and nonstandard form lifetimes | V02/V05 in the checklist; `morpher-native-preservation.md`; named reaction/song and Mystic cold reports |
| Geomancer visible fields, lifetime and animation consumers | `geomancer-outline-readability.md`; current four suspend/cold/expiry paths634 checks and160 native animated steps |

Root finds no remaining identified lesson placeholder, unsupported numerical
promise, job-locked transferable support, missing teaching association or
unreconciled defect from this audit. The known rounding, weapon-family, Absorb,
AI/admission, help and saber-pose findings were fixed and have direct evidence.
This is a bounded implementation review, not proof of all possible action
combinations. A01/V06 still own campaign earning/access/Judge milestones; I07
still owns remaining mixed-job pressure and native-effects display acceptance;
R02 owns frozen final assembly/regression and R03 playable delivery. These
independent obligations are not marked complete by closing A05.

## Earlier source review and corrections

This is the root's source-to-design review against
`JOB-CLASS-SPECIFICATION.md` v0.7. It supplements the installed-table audit in
`installed-design-review.md`; neither is full campaign acceptance. No new
agents or gameplay testing agents were used.

## Corrected contracts

1. **CHM-A5 Healing Mist:** explicitly compute
   `max(50, min(100, floor(maxHP / 5)))` before combining Pharmacology and
   Recuperation. The integrated callback previously carried the fractional
   base through those multipliers. At307 maximum HP the correct base is61:
   one support gives91 and both give137. The older92/138 expectations in
   `soldier-supports.md` were incorrect; historical reports remain unchanged.
   The private Chemist callback already followed the approved base formula.
2. **Spellblade weapon family:** accept native categories8/3 (rapier/saber),
   not7/8 (knife/rapier). The old shared predicate contradicted the job's
   equipment permissions, its Combo, and all six added saber teaching items.
   The corrected predicate serves command admission/payment, enchantment
   ownership, native AI and Spell Parry readiness. Dance retains knives/rapiers.
   No equipment permissions, weapon records or racial lesson access changed.

Candidate `a6626e7e30487ffb77e48aa8ab1ee1ee3bff0168`, base
`b26778520203359c3b129bcc025b92dd0e4c01f1`. Prior candidate
`eabce3b98536510e40a8ec5893ecd9bd2996566c` retains unrelated evidence.

## Focused evidence

Run `20260917T045635.290463Z` rebuilt the combined image and captured one native
battle/executor fixture. It ran only the following two consumers and their
eight preparation steps, not the full integration suite:

- `test-semantic-medicine`:480 assertions passed. Seventy-two formula/AI
  combinations cover base-clamp boundaries, fractional bases, missing HP and
  two separate legally equipped supports. Sixteen native executions verify
  actual HP and exact atomic Potion/Hi-Potion payment.
- `test-semantic-spellblade`:1,099 assertions outside its final Parry section
  passed: all461 item IDs including zero,112 command-admission cases,44
  enchantment lifetime cases and56 native command executions. All14 commands
  use both rapier and saber. Silent users are rejected; later Silence keeps a
  prepared enchantment; primary replacement removes it. The last three Parry
  cases incorrectly assumed seed0 must hit and failed. This report remains
  failed; it is not described as a passing whole test.

Run `20260917T045841.358675Z` reran only
`test-semantic-parry-cached` plus unchanged assembly verification. Its124
assertions passed. Native hit observations distinguish misses from successful
hits;48 paired executions across eight seeds prove actual halved damage and
fuel expenditure for rapier/saber, no Parry from a knife, and fuel retention
on misses. No command matrix or medicine checks were repeated.

Accepted coverage is1,703 assertions from these independent sections. Local
consumer reports are under the candidate directory in:

```
semantic-contracts-20260917T045720.310859Z/report.json
semantic-contracts-20260917T045720.602819Z/report.json
semantic-contracts-20260917T045842.151194Z/report.json
```

Each records exact candidate/capture hashes and fixed inputs. Raw reports and
binaries remain ignored. The runner's top-level legacy foundation hash differs
from this assembled candidate; the builder and consumer hashes above identify
the tested executable. These are controlled native consumers, not a complete
player-interface or campaign playthrough. No save-layout change was made.

## Absorb Damage follow-up

Candidate `9fef4cbe557b69ec9fc9d63ed0f39ed38e8782a6` removes the unrelated
scaling-category gate from Absorb's direct-HP-loss trigger. Native-primary
origin, actual loss, hostile ownership, reaction readiness, survival and the
per-action recovery cap remain required. Gil Snapper retains its independent
physical/critical gate. No storage, queue transport or damage formula changed.

`test-absorb-direct-loss` passes245 assertions across80 native executions in
`20260917T050338.272292Z`. Fight, Fire, Demi, Twister and Limit Glove each have
four fixed seeds and ordinary/ally/KO/blocked controls. On seed3 the two native
percentage attacks each remove400 HP and recover120, despite their unclassified
scaling category0. Limit Glove removes the remaining800 HP and cannot revive
the recipient. Normal physical/magical positive recovery remains verified.
The native result list contains exactly one queued recovery where eligible.

The report is `absorb-direct-loss-20260917T050423.600687Z/report.json` beneath
the current candidate; it records exact ROM/capture hashes, complete cases and
limits. Retain earlier dual-hit and reaction-scope evidence: this correction
changes trigger classification, not those mechanisms. No full regression ran.

## Review coverage and remaining work

| Area | Reviewed contracts / implementation paths |
|---|---|
| Samurai | Primary katana, Centered consumption, rational Murasame, Protect/Regeneration, Higanbana's owned pulses and integrated prevention, Composure/Poise and physical reactions. |
| Dark Knight | Additive HP costs, Bloodcasting boundary, actual-loss drain caps/undead, post-payment Desperation, Last Resort/TBN ownership and aftermath, direct-damage classification and reactions. |
| Viking | Native theft before independent damage, water/terrain displacement, War Cry and challenge lifetime, Sea Legs, action-start Opportunist, critical-gil provenance. Absorb's direct-loss trigger is corrected and verified above. |
| Geomancer | Affinity queries, capped/positive-damage riders, stronger Wisp preservation, shared field slot/timers, grounded Refuge, Updraft/Steady, Attunement refund and Surefoot. Rendering acceptance remains separate. |
| Chemist | Recipe/stock ownership, atomic payment, HP/MP/restoration versus revival, projectile and range rules, Inoculation and actual equipped reaction preferences. Healing Mist corrected above. |
| Bard | Weapon-free/Silence rules, marginal AI values, song percentage caps, tagged Encouragement and incoming-only bonus, charged incantations, Clear Voice, Encore and native Haste replacement. |
| Dancer | Virtual weapon versus Sword Dance, percentage/capped Witch Hunt, custom debuffs, chosen ailments, Fury's physical category distinct from sequencing, Grace/Light Foot and Passing Step ledger. |
| Mystic Knight | Shared weapon predicate corrected above; self/strike modes, actual-loss resource caps, primary-only Fight, Spellbreak selection, Release fuel, Break's S check, sequence and defensive ownership. Retained detailed notes cover Doublecast, predictions and laws. |
| Axe additions / Combos | Primary-only physical riders, Shatter ordering, Executioner threshold, Fell drawback, Recuperation/Haft Guard and Follow Through. Combo weapon families compared with approved equipment categories. Final Combo/campaign gate remainsV04. |

This review is not an A05 completion claim. Remaining presentation and lifecycle
evidence must be reconciled with the complete approved lesson contracts.
The subsequent actual saber playback exposed a missing Viera pose; its fix and
three Mystic cold-state cases are in
[`mystic-knight-cold-lifecycle.md`](mystic-knight-cold-lifecycle.md).
Presentation, save lifetimes and final assembled acceptance remain in the main
checklist rather than being inferred from this source review. These three
corrections add no new balance package or job scope.

## Reproduction

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-semantic-medicine,test-semantic-spellblade
```

After an unchanged build, select `test-semantic-medicine-cached`,
`test-semantic-spellblade-cached`, or the narrower `test-semantic-parry-cached`
only when that behavior has changed or remains unresolved. Completed evidence
does not need to be recreated because a document or test comment changed.
