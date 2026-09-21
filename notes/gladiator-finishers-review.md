# Gladiator finishers: implementation and integration review

## Installed Executioner follow-up

Production ROM `d658e596e13febd725a0c312c204f844d2b92e62`, engine `a8436b3593c6f9c133ca42918209b771ba28c593`, passes `test-gladiator-finishers.py --current` (**4,118 checks**) and `test-executioner-preview.py --current` (**35,292 checks**). The latter independently verifies the installed player-preview consumer at `B5816..B5820`, including all347 original action IDs, all430 chances0..100, the explicit target, both stack residues, incoming overflow, live registers, output flags, and frame/unit isolation. Player preview uses ordinary accuracy `12E0BC` at `B5804`, bypassing the original execution/AI entry; this additional hook is required. It supplies the adjusted chance to native `2B8CC` after replaying the displaced argument setup. Actual UI/lifecycle evidence is tracked separately in `notes/executioner-in-game.md`.

The sections below describe the earlier isolated prototype and its historical integration limits. They do not supersede the current installed results above. Exposed state lifecycle acceptance remains separate from these helper and Executioner tests.

Reviewed against the current `AXE-SKILL-EXPANSION.md` and `JOB-CLASS-SPECIFICATION.md`. New files are `src/engine/gladiator-finishers.c`, `src/engine/gladiator-finishers.s`, and `scripts/test-gladiator-finishers.py`. They do not enable a production action or alter the shared build.

## Corrected threshold and independent evidence

The initial prototype incorrectly used unit+1C as maximum HP, and its synthetic fixtures repeated that error. Its earlier 4,087-check report is superseded. The corrected implementation uses current HP+18 and maximum HP+1A. Native C7EA4 selectors 19/20/21/22 dispatch to C8022/C8026/C802A/C802E, respectively, reading +18/+1A/+1C/+1E. In the captured native executor, the actor is 59/59 HP and 12/16 MP; the enemy is 27/27 HP and 49/49 MP. The test now asserts the native dispatch entries, calls those untouched native getters, and varies MP independently of HP in 40 coefficient/chance cases.

Executioner's factor is the exact numerator 11 or 18 over 10, selected from execution-time target HP at or below half maximum HP. The threshold uses doubled HP, avoiding fractional rounding. Fell Cleave returns 18/10. The common physical finalizer must combine this factor with the other applicable factors before its final rounding. The primitive does not inflict damage or override native target eligibility. Zero maximum HP is defensive invalid input; zero current HP otherwise satisfies the mathematical threshold, with native eligibility still responsible for rejecting an invalid dead target.

## Executioner hook contracts

At ROM131378, replace exactly 12 bytes `30b5104d286869682a6b5278` with the aligned push-r3 long jump to `ffta_executioner_chance_entry`. Its native trampoline replays push r4/r5/LR; loads global context0200F3F0, actor at+0, target at+4, descriptor pointer at+30 and descriptor byte1; continues at08131384. The wrapper aligns the C stack and preserves the ordinary function ABI. Native chance is computed in full first, including prevention and forced outcomes.

The direct BL callers are A2FDC, C2486, C4942, 134EDC, 1350EE, 1355C0, and135838. The A2FDC committed executor adds a further native ten points at A2FE4..A3002 under its original conditions. Therefore the general chance wrapper identifies saved LR080A2FE1 and leaves this one caller unadjusted. Other callers receive the wounded Executioner adjustment immediately.

At ROM A3004, replace exactly 12 bytes `201c8cf0e9f80006002824d1` with the push-r3 long jump to `ffta_executioner_roll_entry`. R4 is the completed ordinary chance, after the native late adjustment. The entry preserves the register frame around aligned C, writes the adjusted R4, calls native12F1DC once with that final chance, and replays the shifted boolean comparison. It continues at080A3010 on miss or080A305A on hit. It does not overlap the Shatter Guard hook at A3072.

The adjustment applies only to action430 and a wounded target: positive chance plus20, capped95. Native prevention zero stays zero; a forced100 becomes95 as required by the explicit cap. The native ordinary A callback is13112C, via12EF94/12C7F4; ordinary evasion is clamped5..95 at12C670, so a zero returned by the full131378 path is a preventing result rather than ordinary evasion. No RNG is added by either hook.

## Current validation

Run the script with the bundled Python runtime used by the other mGBA tests. It compiles only these new sources into a private ROM at091E0000. Frozen source ROM SHA1 is `5b90d5fb623457405d96948e33df623b342da14c`; final isolated binary SHA1 is `bfbe9733d6ee4c6a4d64fa6d73ccc43295f610dc`. Original fixture files are hashed before and after.

The corrected run passes **4,130 checks**, including all347 original native chance actions at both stack residues (694 comparisons), 88 real native status cases, and 78 executions of the captured native A2E70..A3762 frame. Comparisons cover complete EWRAM and the native RNG state. The executor oracle changes only the native roll input to the specified expected chance, then executes the unchanged native magnitude/HP path. No formula or status handler is mocked. The wounded 13/27 target changes final50 to70; 14/27 remains50. Flipping native allegiance exercises the path without the ten-point bonus:40 becomes60 only when wounded. Native zero prevention remains zero; forced100 is capped95. The reserved guard0203FF44..02040000 remains intact.

The private430 action descriptor is deliberately copied from425 solely to exercise accuracy. Its actual 10 MP cost, r1 enemy geometry, primary-axe restriction, coefficient integration, visual/help metadata and no-crit/proc/drain behavior still need production integration and fresh gameplay tests. Central preview/AI callers are covered, but no claim is made yet about the exact number drawn by the complete430 preview UI.

## Fell Cleave: safe primitives, not enabled state

`ffta_exposed_transition` receives an explicitly owned byte; it does not invent an identity or borrow a native status bit. Apply refreshes to1 without stacking. Own-turn start, KO, Petrify, battle end, job change and broad remedy clear it. An application-cancelling immunity returns failure without mutation. The caller must distinguish genuine cancellation from Inoculation: the specification expressly says Inoculation never prevents self-inflicted Exposed or Last Resort's drawback.

`ffta_exposed_numerator` returns6/5 only for positive direct physical HP damage to an exposed recipient, including immediate retaliation. Costs, MP loss, healing/absorption and ticks return5/5. It produces a factor, not a separately rounded value; combined with Last Resort's6/5 it must become36/25. Protect remains part of the ordinary calculation.

The actual captured A2E70 frame is already after Tomahawk's MP cost: actor MP12, maximum16. Its accuracy roll is at A3006. Native item consumption branches at A2EAE..A2EE6 precede that roll. Therefore adding an availability rejection at the roll hook would be too late to guarantee no paid cost. Exposed must be applied once on a validated committed action before all hit/miss outcomes and retaliation; repeated preview/AI queries must not mutate it. A2E70 lies in a recipient-processing flow, not a proven once-per-action entry. It is not claimed as an adequate final application hook.

Existing `unit-copies.c` provides useful allocation ownership but not this state contract. Its `Extra` is36 bytes:34 AP bytes, one potion preference and one padding byte. Snapshot units, manager copies, selection and party previews have these owned tails. The padding is initialized for snapshots but is not copied by `ffta_on_unit_copy` or cleared by `ffta_clear_copy_extra`; using it without extending those paths loses or leaks Exposed. Canonical24 roster ownership does not cover the captured enemy at020033E4. No name or generic character ID may substitute for that missing owner.

Fell Cleave remains unenabled pending explicit canonical/enemy state ownership, copy/snapshot restoration, native suspend serialization, once-per-action application after pre-cost validation, actual own-turn-start expiry, and verified KO/Petrify/job-change/battle-end/broad-remedy hooks. The current repository does not yet provide verified native addresses for that complete lifecycle. The existing top-RAM owner root0203FF30..0203FF44 and view reservation must remain intact. This is a bounded primitive deliverable, not acceptance of the full persistent effect.
