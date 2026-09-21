# Combo battle integration review

Current assembled-candidate acceptance is in
[`final-combo-synergy.md`](final-combo-synergy.md): all ten owners, participant
controls, cold saves, all permitted weapon families and focused mixing checks
on687ed5d4. The frozen run below is historical supporting evidence; it is not
the current release status and does not require a rerun after every change.

## Scope and accepted frozen run

`scripts/test-combos-in-game.py` passed410 checks on combat `b6866d6e9fc5dab8b0cf97e7ada8cc42ebda635d`: eight profiles across ten racial owners, ten initiation/cancel/Save Now/cold-resume paths, ten exact new-participant/native-donor comparisons, and30 confirmed returns to the native battle menu. The repaired Nu Mou Chemist retained knife74 throughout its full test. Later combat builds require the normal sequential rerun.

Private RAM fixtures preserve each original character's identity, race, level and accumulated stats, assigning a valid same-race new job, legal primary weapon, mastered racial Combo index, and3 JP. Adjacent allied targets receive999 current/maxHP to prevent KO awards. These are mechanics fixtures, not progression or a natural playthrough. No user ROM/save files are written. Assigned Combo is unit+3C; JP is the native halfword+D6. Human expanded mastery uses the sidecar. Cancellation and execution preserve equipment/AP; execution spends3JP once with no KO award. Native Save Now is followed by a fresh emulator receiving SRAM alone, without a savestate, before Resume Battle. All ten owners retain their job, assignment, JP, equipment and full AP bank.

Completion must return the native menu, not merely change HP/JP. The test compares a mask of the native Wait label's white glyph pixels, excluding the translucent animated background. An initial exact-background comparison incorrectly rejected a completed Dark Knight chain and was corrected after screenshot inspection.

## Actual chain evidence

The new lesson is tested as initiator and as a participant joining an original native initiator. A disposable test-ROM breakpoint atB32E8 stops afterB32E6 publishes the successful count. NativeB3150 allocates a transient15C4-byte context via22840; r7 supplies its actual address. Context+141C/+1420 contain attacker/target wrapper pointers, +1458 the successful participant-wrapper array, and +1539 its count. Each wrapper's first word is the actual unit pointer. The test asserts the exact initiator, target and new participant.

The donor control changes only the new racial lesson's global profile ID to its exact approved native donor: Ninja15, Knight2, Sword7, Wise17, Thief23, Juggle32, Lunge6 or Red11. Name, mastery, equipment and unit remain identical. Native RNG is deterministically seeded through its actual IWRAM state. Participant lists and real JP/HP outcomes must match. Initiators spend3JP; participants retain their JP, matching native behavior. A diagnostic breakpoint atB32E2 initially read zero before the count store; that harness ordering error was corrected before acceptance.

## Nu Mou Chemist knife defect and fix

A legal knife committed damage and JP but left Nu Mou Chemist in the zoomed animation after more than10000 extra frames. The same job with staff149 finished. Separate native White Mage controls reproduced knife failure and staff success. Chemist's actual production sprite donor is Alchemist25; White Mage20 was only an independent control.

A native986DA breakpoint confirmed r6 as evaluated actor wrapper, its first word as the unit, r5 as actual category7, r7 as item74 and r10 as the animation code. Native blade categories select pose family1; rods/staves select family3, which the Nu Mou donor supports. The actor-only branch in `src/engine/axe-visual-hooks.s` maps derived input7 to12 only for rawrace3/job120. It leaves the actual item/category, damage, JP, hit count, effect callback, sound selection and identity unchanged. Original jobs, other races/categories and the other three visual switches retain their behavior. There is no global owner lookup.

`test-axe-visuals.py` checks all24 races times126 jobs at both SP offsets, plus every category0..31 and native animation mode6..17. The first fix passed90240 checks with no failures on axe-visual8e8724314fb6cfe961ce9884c2aafdebcc0b0bef, enginefe7135952ebeb1474b70391a37814103dd113ea5. The full frozen410-check battle run also passed with the actual knife.

## Complete weapon-family matrix and Dancer follow-up

`scripts/test-combo-weapon-visuals-in-game.py` exercises actual Fight and legal Combo animations for all permitted weapon families on all ten jobs, validating its family list against built equipment permissions. There are39 cases:20 Fight and19 Combo, because Bard's knife intentionally cannot perform its instrument-only Combo. Each requires animation completion, preserved equipment/identity, correct JP and a surviving target. This prevents silently replacing the original failing knife with a staff.

The matrix found another missing pose: Viera Dancer124 with knife7 completed Fight (targetHP999 to986), but its Combo stayed zoomed. Elementalist29 is its sprite donor and supports rapier poses. The same actor-only branch now selects derived category8 for rawrace4/job124 knives. Other Viera jobs/categories remain unchanged. A fresh-build battle matrix must pass before this second fix is accepted. Separate old-ROM controls confirmed Mystic Knight's type3 and8 Fight/Combo paths complete.

The evaluated-wrapper contract is native:98378 stores argumentr0 inr6 for9836C;984C0 in that same function reads[r6] as a unit and then unit+4.97520/97594 separately use the wrapper's unit pointer for F6/F7/FD. This supports the contract without an inferred roster association. Transformed status animation behavior is not separately accepted by these fixtures.

## Artifacts and remaining acceptance

Reports: `build/expansion/probes/combos-in-game-tests.json` and `combo-weapon-visuals-tests.json`; adjacent per-hash folders retain private ROMs, states, screenshots, SRAM, participant captures and native donor outcomes. Default tests reject stale hashes; the weapon matrix's explicit `--frozen` option is for isolated historical verification. Production progression, remaining job abilities and a full natural playthrough are outside this audit.

## Combined knife-fix diagnostic acceptance

The two fixes together passed on private ROM `25081e141d5606497b32ba2695d00779c9781090`, using b686 battle states with only the rebuilt actor hook appended and redirected. The assembler object has no relocations. All 39 Fight/Combo executions completed with 156 equipment/identity/JP/survival assertions. All 20 distinct job/weapon-family pairs include at least one successful hit; some Human Fight trials miss under the fixed native seed, while their corresponding Combos hit. Both previously stuck knife Combos finish and return control.

The same private ROM passed 91,776 native visual differential checks, including both scoped job/race exceptions. Reports are `build/expansion/probes/knife-pose-visual-diagnostic.json` and `knife-pose-diagnostic-weapon-visuals/25081e141d5606497b32ba2695d00779c9781090/results.json`. This is explicit diagnostic acceptance, not a claim that the held shared main build already contains the Dancer fix. The next main build must run the normal component, full Combo, and 39-case weapon tests against its fresh fixture.

## Main build acceptance with both knife fixes

Main combat **d658e596e13febd725a0c312c204f844d2b92e62** passed the complete **410-check Combo test**, with all10 owners,30 actual animation returns, exact native participant-list/donor comparisons, cancellation, JP accounting and10 SRAM-only coldloads. Its fresh native battle states then passed the **39-case /156-check weapon matrix**, including both NuMou Chemist and Viera Dancer knife Combos. Every one of20 job/weapon-family pairs has at least one actual hit, and every execution returns control. This accepts the two missing-pose fixes on a normal main build with matching states.

The parent advanced the main ROM while the frozen run finished, so the weapon matrix used the explicit `--frozen` option against d658. It did not mix later-ROM states. Both canonical reports record d658, and their per-hash folders retain the artifacts. The newer axe-visual component **a144a5e5a9afdb534b4867a6973b2803639c84b5** also passed **91,776 native checks**. Later main builds still require their ordinary regression pipeline; the exact evidence above should not be relabeled as a later hash.
