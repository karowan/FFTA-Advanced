# Soldier Recuperation and Haft Guard

The root integrated image now implements both Soldier support/reaction
additions. No further agents were used. The runtime batch adds no saved state,
hidden actions, reaction claims, equipment records or acquisition changes.

## Runtime contract

Recuperation checks the explicit recipient's equipped support. Direct healing
from self or an ally receives a 3/2 multiplier; enemy healing, undead targets,
revival, drain recovery, Regen and MP restoration do not. It has no axe or
Soldier-current-job requirement. Native Charm-aware allegiance is preserved.

Ordinary Potion/Hi-Potion/X-Potion and the new direct HP medicines combine the
giver's Pharmacology with the recipient's Recuperation before division. These
are separate support slots on separate units. New medicine previews cap at
missing HP; ordinary Item retains its native uncapped magnitude and caps at
the actual HP writer. Murasame combines Centered and Recuperation once; Dark
Mind applies Recuperation to its self-heal. Remaining original healing uses
native application kind/sign metadata at the signed magnitude stage, excluding
drain and revival selectors. Elemental absorption is not restorative magic.

Healing Mist explicitly floors its 20% base before the 50/100 bounds, as
specified by CHM-A5. Pharmacology and Recuperation then multiply that integer
base together before one final division. At 307 maximum HP the base is61,
Pharmacology alone restores91, and both supports restore137. The September17
semantic review corrected root integration to match this recipe and the
private Chemist callback. The older evidence below tested the previous
fractional-base behavior (92/138); those historical passes do not validate
the corrected values. Current verification is recorded in
[`semantic-contract-review.md`](semantic-contract-review.md).

Haft Guard reuses the shared Blade Ward weapon-defense path. It requires an
equipped primary axe, passes native reaction availability/incapacity checks,
and multiplies hostile direct physical damage by 3/4. It gives no counter or
magical reduction. It combines with Poise and other direct physical factors
before rounding. Snapshot bit30 distinguishes the axe guard from Blade Ward;
copied recipients inherit the original decision and reaction suppression still
applies. The allocation ledger records this bit. No new reaction slot exists.

The source-generated help includes both descriptions within the existing
three-line native limits. Shared builds include Haft Guard and the help;
Recuperation's healing composition is installed by the root integrated build.

## Deterministic evidence and limits

`scripts/test-integrated-soldier-supports.py` is declared in the combined test
plan. It passes 2,898 assertions on candidate
`ff7369a8700614ec4f0e456d142662439c59cfb0`, shared base
`9ec81ca9d0c51eb8692e53f1ea763eaa06fa400b`.

All 39 steps of the consolidated combined suite passed in
`20260915T084056.050238Z`, with `inputsUnchanged: true`, including the existing
24 reaction playback scenarios and three native cold resumes. The report is
local under `build/expansion/test-runs/`; generated captures remain ignored.

- 576 medicine combinations cover fractional bases, support combinations,
  tiny missing-HP caps and unchanged preview RAM/RNG.
- Murasame and Dark Mind test independent rational healing expectations.
- 192 original/custom native action scenarios cover physical defense, magic
  exclusion, Poise composition and actual Cure recovery across eight seeds.
- 24 native Murasame/Potion Dart/Healing Mist executions verify combined HP
  restoration, exact medicine payment and retired transient state.
- Native equipped-lesson lookup, wrong weapons, Petrify, copied recipients and
  explicit reaction suppression are checked.

These controlled native execution fixtures do not prove every legal command
loadout, menu rendering, teaching/AP, acquisition, campaign AI, forced action,
or save-slot path. Some native action comparisons invoke the command directly
to isolate its consumer. The medicine support combinations themselves use a
Moogle giver and Human recipient with one support each. The expansion remains
incomplete; Composure, the remaining jobs and final campaign/UI acceptance
remain separate work.
