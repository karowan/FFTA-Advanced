# Spell Parry implementation

This checkpoint implements the physical defensive interception only. Magic
Shell, enchanted primary Fight, whole Doublecast sequencing, native Mystic
presentation and final job acceptance remain separate work.

Spell Parry freezes ordinary reaction capability and the qualifying prepared
blade at incoming-action start. Native successful Fight boundary A28E2 and
successful physical command boundary A3072 claim extension bit19, then clear
the live enchantment. Misses never reach those boundaries. Successful hits
spend fuel even if immunity or redirection makes eventual HP damage zero.
The frozen readiness remains for subsequent physical components of that same
action. The shared exact-ratio finalizer includes its one-half factor before
rounding. Status effects and magical HP components retain their ordinary rules.

Hostility, reaction permission, actor/copy provenance and origin gates exclude
allies, self, combos and reaction chains. Query scopes cannot claim or clear
fuel. Pure reaction lookups return the exact frozen extension when available;
unsnapshotted AI candidates first check the equipped reaction, avoiding costly
enchantment/ownership queries for ordinary units. No new saved bytes, global
RAM reservations or action-frame ABI changes were needed.

Capability deliberately uses the original Reflex status mask, as the other
defensive interceptions do. The first focused run passed all448 native casts
but failed four test expectations that assumed Sleep disabled that mask.
The corrected test compares all44 native status bits with the native mask and
incapacity predicates; no production status rule was relaxed to pass it.

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite
mystic-parry` for the focused suite and `-Suite combined` for assembly
acceptance. The test observes real hit boundaries and HP writes, never injecting
outcomes. It covers native Fight and techniques, magic, status-only Break,
misses, elemental immunity, ally attacks, two weapon objects, prediction
purity, copied recipients, nested previews and disabled/reaction/combo scopes.
The two-weapon input validates component ownership, not equipment-menu access.
Whole Doublecast ownership remains unimplemented and is not claimed here.

## Corrected Fight investigation

The earlier investigation's proposed weapon indices are incorrect. Physical
formula12FE38's fifth argument is a native reaction discriminator: native
Fight loads reaction selection at A2910, passes it through130200 to12FE38,
and value10 has a special formula branch at13009C. Likewise the native result
frame's2F4 value originates in reaction control, not the dual-weapon loop.

The actual A433C weapon iteration is at native frame+34, initialized A44F2;
frame+38 is weapon count, and frame+B0 is next index. A445C populates the
weapon array through12F0D8. Actual result evaluation at A4852 calls A23B8.
These addresses are static investigation leads, not yet a verified carrier
hook. Two identical item IDs cannot establish which hand is being evaluated.
Do not implement enchantment ownership by comparing item IDs alone or by
reinterpreting the reaction discriminator as a weapon index.

## Evidence

Focused run `20260916T052014.919050Z`:14/15, four incorrect Sleep expectations,
candidate6697acfe368b7c4a57746daf401156798325ba14. Follow-up focused run
`20260916T052228.242871Z`:15/15, including native dual-weapon observation.
The final76/76 combined run `20260916T052427.627672Z` passes on
`3aa5cd8334a0c2b99c61b7cadda93aaf627cdbde` with unchanged inputs and an
independent post-run hash. The extended test adds copied/nested permission,
reaction/combo and real ally-attack checks, for496 native casts total.
Existing playback, AI, field persistence, allocation and startup tests pass.
