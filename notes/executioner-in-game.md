# Executioner actual game flow and preview correction

## Current production acceptance

ROM `d658e596e13febd725a0c312c204f844d2b92e62`, engine `a8436b3593c6f9c133ca42918209b771ba28c593`, passes the fresh **300-check** actual game regression, **35,292** installed preview comparisons, and **4,118** installed finisher comparisons. The preview correction is now accepted in the production stage. The fresh initial state and ROM are frozen privately under `build/expansion/probes/executioner-in-game/d658e596e13febd725a0c312c204f844d2b92e62/`; `report.json` contains outcomes and native display-call captures.

The actual native `2B8CC` display argument is **60%** at125/250 HP and **40%** at126/250 HP; an independent ordinary-chance control is40% in both cases. Screenshots visually confirm72damage/60% and44damage/40%, respectively. At commit, independent native P43 becomes77 or47 with the correct execution-time threshold, including both125→126 and126→125 changes after preview. Native seed0 supplies a miss and seed1 a hit in all four cases. Each pays10MP once; cancellation, turn progression, AP/inventory/gear, native Save Now, and SRAM-only cold resume all pass.

`test-executioner-in-game.py` now defaults to the current shared battle fixture, rejects stale default ROM hashes, and copies its initial state privately before running. `--fixture` remains available for explicit frozen historical audits. No shared build or user save is changed by the test. These results cover Executioner430; they do not certify unfinished arc UI or future Exposed lifecycle changes.

`scripts/test-executioner-in-game.py` uses a fresh private Herb Picking fixture, legal Bangaa Gladiator Jona, War Axe459 and mastered native lesson107. It exercises actual Move, ability selection, targeting, cancellation, native accuracy and damage,10MP payment, facing/turn progression, Save Now and a new emulator's SRAM-only cold resume.

## Initial actual execution results

On ROM `47f630ded93e0e386e7508c22bda988eaee83977`, engine `3cee79c1e08f54556b4a70daab50a4d2d3678795`, the288-check gameplay run passed its coefficient/MP/cancel/save assertions. A control ROM restores **only** the final coefficient/clamp hook at1300E2..1300F2; it retains Executioner's identical accuracy hooks, action metadata and all native processing. Native reference43 produced77 damage at125/250 HP and47 damage at126/250 HP. Seeds0/1 supply real miss/hit in each of four cases.

| Preview HP | Execution HP | Expected factor | Native reference / actual damage |
| ---: | ---: | --- | --- |
|125|125|18/10|43 /77|
|126|126|11/10|43 /47|
|125|126|11/10|43 /47|
|126|125|18/10|43 /77|

The crossed-threshold cases prove the committed coefficient reads execution-time HP, not cached preview HP. Maximum HP is+1A; target MP is independently49. Every hit/miss pays exactly10MP. All cases cancel without mutation, keep AP/inventory/gear, advance the native turn, and cold-resume the successful outcome.

**That original build's displayed chance was wrong**, so the288-check report is not full Executioner acceptance. Both its low-HP preview and a fresh control route with chance hooks removed displayed40%, while low-HP P correctly displayed72. This was an actual missing UI consumer, not a failed arithmetic helper.

## Verified correction

Player preview `B55CC` calls ordinary UI accuracy `12E0BC` at `B5804`; it bypasses the existing `131378` execution/AI hook. `B5808..B5810` caps that ordinary result at100. At `B5816`, r4 is the ordinary chance, r8 is the action, r6 is the explicit target wrapper and `[r6]` is the evaluated target. The shared context is not the right source for this local preview.

New `ffta_executioner_preview_chance` in `gladiator-finishers.c` uses those explicit inputs and delegates the430-only positive+20/cap95 rule to the existing helper. Zero remains zero. `ffta_executioner_preview_entry` in `.s` is installed as the standard10-byte r3-preserving veneer at `B5816..B5820`, preserves incoming V and live registers around aligned C, and replays the five original argument-setup instructions before `B5820 ->2B8CC` displays the result. No unit is mutated.

`scripts/test-executioner-preview.py` passes **35,292 exact native differentials** on the isolated correction: all347 original IDs, new-action controls, all430 chance values0..100, below/above threshold and zero maxHP, both SP residues, V0/1, registers, flags, frame and target isolation. Isolated ROM `7151aefdadf9ba80dc51abd676238ac8c34da0b3` now visibly displays **72 damage /60%** in the identical fresh125/250 route. The fresh ordinary control displays40%.

The gameplay script removes all three chance hooks for its control and traps the actual native `2B8CC` display-call argument to assert the displayed percentage automatically. The current production run above completes the previously pending fresh-fixture verification. `test-executioner-preview.py --current` independently verifies the installed UI hook.

## Independent installed chance regression

`scripts/test-gladiator-finishers.py --current` passes4,118 checks on47f630: all original IDs,88 actual native status/prevention cases, preventing-zero and forced100 controls, HP/MP independence, full committed chance and native-roll-input equivalence. It restores only the two original chance hooks in the control while retaining the production coefficient. Production hostile-only eligibility correctly blocks the artificial same-side late-bonus fixture before any roll; the isolated predecessor's same-side result is not claimed for production. Exposed helper coverage in that file does not imply Exposed persistence/lifecycle acceptance.
