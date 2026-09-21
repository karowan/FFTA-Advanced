# Physical rider primitives: implementation and native review

## Latest installed regression

The installed rider/law suite now passes **17,712 checks** on seven-action ROM `47f630ded93e0e386e7508c22bda988eaee83977`, engine `3cee79c1e08f54556b4a70daab50a4d2d3678795`. Query inputs also cover426/429/430 and before-hit exclusions include431. Native original-action, full outer law, source isolation, actual hit/miss and restorative/null/absorb checks remain passing. Fresh427/428 UI/cold-save acceptance is separately recorded against214e in `physical-riders-in-game.md`; it should not be mislabeled as a fresh47f UI run.

## Current production integration acceptance

Shatter Guard427 and Armor Splitter428 are now integrated into the composed combat probe. `combat.c` enables both at1/1 with primary-axe eligibility, the common restorative-primary policy and the pure rider reference. `combat-hooks.s` excludes their native3D drain and3E cleanup paths. The combat builder installs all three audited rider hooks and single-target Rush-derived physical records: MP6/8, stage vector3F/01/01/01, preview-message0. Content council extended the explicit-coordinate geometry rule to symmetric height2. Actions426/429 remain inert.

`Build Engine.ps1 -SkipTests` completes successfully. Current ROM `214e6722bbd68e53e9bb583f5074ad84241860e1`, engine `69dcde5cefeefc77d612cee5df2654a7fc466e36`. The main test pipeline includes `test-physical-riders.py --current`, which checks actual installed pointers and tests the composed ROM without overlays. The default invocation preserves the earlier frozen primitive experiment.

Accepted on these hashes:

| Test | Checks |
| --- | ---: |
| Final signed physical arithmetic, original IDs, clamp and native ABI |613,757|
| Full native physical references, primary/offhand,3D/3E and restorative elements |28,026|
| Captured committed execution, Fight controls, single primary hit and proc/critical exclusions |21,212|
| Installed riders, hit/miss, preview, full native law phase and outer law evaluator |17,544|
| Eligibility (content council) |24,059|
| Melee geometry/metadata (content council) |36,651|

The actual outer `1343C8` now runs through native heap allocation, copies, `1342CC`, and frees. All347 original actions have matching outer results/full EWRAM at SP0/4, with nonvacuous native positive status controls. Shatter's prediction removes Protect only from the allocated simulation target before P. The live actor, enemy, roster and AP/storage tail remain unchanged. Its full21-harmful-status law loop also completes and reports no harmful status application.

**Clarification from the outer trace:** the existing native type15 status law and type16 harmful-status law call `1342CC` in mode0. Protect25 is absent from the native21 harmful-status list. Shatter correctly returns false for an *added Protect* query; it does not invent a new law violation for removing Protect. The separately verified mode1 removal contract returns true for present Protect, but this should not be described as an existing law that the outer native selector uses. Both mode contracts and post-removal P are now tested.

The shared battle fixture was left intact while content council ran its frozen combo tests. Fresh UI preview/cancel/MP-payment and complete animation/turn flow for427/428 remain end-to-end acceptance work; native captured recipient execution and full law simulation have passed. Redirect/interception coverage beyond the ordinary recipient case remains a broader integration test.

## Initial isolated review and exact hook contracts

The remainder records the initial primitive review before the production integration above; its pending-builder items are resolved by the current acceptance section.

Scope: Shatter Guard427 (`FFTA_SLD_AX_A4`) and Armor Splitter428 (`FFTA_GLD_AX_A1`) per `AXE-SKILL-EXPANSION.md`. Initially only the two primitive source files and isolated test were changed; production commands remained inert during that review.

Files: `src/engine/physical-riders.c`, `src/engine/physical-riders.s`, `scripts/test-physical-riders.py`. The script compiles these files itself into an asserted unused FF bank at ROM1180000/address09180000 and installs three exact, guarded hooks only in `build/expansion/probes/physical-riders-council/rider-test-only.gba`. It reuses its frozen input while the shared pipeline advances.

## Verified native boundaries

All addresses below are ROM offsets unless prefixed with08/09 for CPU addresses.

- `CDB0C(unit)` reads Protect at unit+EB bit02. `CE094(unit,0)` clears it; `CE448(unit,0)` clears its timer at+DE. Native cleanup at `131CB6..131CE2` tests the Protect getter and invokes the timer setter. The primitive uses these setters on the explicit recipient; it never resolves an AP owner or accesses a live roster through a copied unit.
- `12FDDC` composes effective WDef through `12F704`, `12F770`, `12F798`, `12F874`. Protect contributes at `12F7B8..12F7CE` (358/256 in physical mode). Armor Splitter therefore must change the resulting defense scalar, rather than the unit's base stat or final damage.
- `12FE38` caps attack at999 (`12FE86..12FE8E`), calls effective defense at `12FE9C`, and caps defense at999 (`12FEA0..12FEA6`). `12FEA8..12FEAE` sign-normalizes attack and defense with four shifts. `12FEB0` calls `12FE28`, which subtracts half defense. The Armor hook scales this capped effective defense to trunc(3*WDef/4), then replays those four shifts. Stored unit stats remain untouched. All other action IDs pass through unchanged.
- Battle execution calls accuracy randomization at `A3006 ->12F1DC`. Failure bypasses the success branch. On success, `A306E ->12F34C` selects the actual recipient at shared context+08, followed by `A3072 ->131B20` for magnitude. This is the verified Shatter removal boundary: after the successful roll and recipient selection, before P. Only stage0 of427 removes Protect.
- Prediction is different: `130200` mode2 asks for magnitude without a committed successful roll. The new `ffta_physical_rider_reference(context,primary,mode)` copies the explicit target into a private264-byte stack buffer for427, removes Protect there, then calls native `12FE38`. Querying a live target cannot change it. The helper returns the native signed physical reference; the common caller must still select a legal primary and enforce custom final-sign/effect policies.

## Installer contracts

| Span | Installer veneer | Entry/continuation |
| --- | --- | --- |
| `12FEA8..12FEB0` (8 bytes) | `ldr r0,[pc,#0]; bx r0; .word entry+1` | `ffta_physical_defense_entry`; r1=capped WDef, r4=attack, r10=action; replay four shifts, continue `0812FEB1` |
| `A3072..A307C` (10 bytes) | `push {r3}; ldr r3,[pc,#0]; bx r3; .word entry+1` | `ffta_physical_success_entry`; consumes savedr3, calls before-hit helper, replays native magnitude and stage branch; continue `080A307D` or `080A3087` |
| `13434C..134354` (8 bytes) | `ldr r0,[pc,#0]; bx r0; .word entry+1` | `ffta_physical_law_entry`; r6=status-output byte pointer, r7=bit, r8=removal mode; native magnitude/compare branches continue `08134355` or `081343B7`; confirmed Shatter Protect-removal query continues native true-return `08134383` |

Both shims dynamically align the C boundary to8 bytes for native SP residues0/4. The defense shim preserves incoming V because the displaced shifts preserve V while C arithmetic does not; replay computes native N/Z/C. The success shim recreates native magnitude's exposed r1=`080A3077` (the dispatcher returns using `pop {r1}; bx r1`). It uses `adds r5,r0,#0`, not a flag-incompatible register MOV alias. These details were verified by live-register, flags, SP and caller-frame comparisons, not merely C return values.

## Verification

Latest frozen input ROM: `5b90d5fb623457405d96948e33df623b342da14c`.
Isolated test ROM: `f50adfac6afa8beaee12865cef99bfc55ceecb20`.
Standalone rider code: `36a97b5a039a7ceee8cacbfede631b053b0aa5b4`.

**16,795 checks passed**, including20,218 native entry segments and11,192 complete calls:

- Every capped WDef0..999, four action identities, both SP residues and both incoming V states; all original action IDs0..346 have exact defense and success-branch register/NZCV/frame differentials. The success matrix deliberately uses the ordinary physical descriptor to isolate the installed dispatch boundary; it is not a matrix of every original nonphysical callback.
- All original IDs plus427/428 across three stages and both residues verify recipient-copy-only mutation. Only427 stage0 may clear EB bit02/DE; the separate live target stays byte-identical.
-120 full native P comparisons cover Protect off/on, native elemental normal/null/absorb, primary effect00/3F and both residues. The independent Armor oracle changes only the native capped scalar at12FEA8; the Shatter oracle changes only its separate target copy. Every query preserves the complete EWRAM image.
-48 executions resumed the real captured native committed frame at `A24A8` through `A3762`, including native dispatch and hit roll. Seeds0/1 provide nonvacuous hit/miss. Original Fight/Rush/Chop/Tomahawk controls are unchanged. Shatter hit clears Protect/timer before actual12FE38; miss preserves both. Armor preserves Protect/timer and stored stats.
-2,776 complete native `1342CC` original-action comparisons cover IDs0..346, add/removal query mode, Protect present/absent and SP0/4. Return values, live registers/flags and complete EWRAM match the unhooked control exactly.
-512 full Shatter law evaluations cover all64 status indices, both modes, Protect present/absent and SP0/4. Only removal of present Protect (index25) returns true. The simulated recipient is cleared before P; live roster, source enemy, copied actor, AP/storage tail and copy guards remain intact. Twelve normal/null/absorb/primary3F combinations prove the removal result remains true even when damage is zero or restorative, and law P equals the private-copy preview reference.

The native frame comes from the existing `chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-exec-seed0` capture. Test results and all isolated binary inputs are in the probe directory. This is native CPU execution from a captured frame, not a newly launched full game route or UI cancellation test.

## Required integration before enabling either command

1. Parent-owned common physical definitions must include427/428 at1/1, with the same primary-axe requirement, primary-only selection, no Fight critical/offhand/proc route,3D drain suppression,3E exclusion and restorative-primary sign policy as424/425. The isolated records are copied only to drive tests. In particular, native primary3F plus elemental absorb yields positive P before the common restorative sign guard; this probe does **not** claim that unintegrated427/428 already satisfy that final policy.
2. Route enabled Shatter magnitude through the private-copy reference helper for previews and other repeated evaluations. The before-hit hook alone cannot produce correct preview damage against Protect. Do not install an unconditional live-target removal in the magnitude callback.
3. Install the now-verified law phase hook as well as the battle hook. Native `1343C8` creates actor/target copies at `1347D6..1347FA`, then calls `1342CC` at `134812`; it never passes battle `A3072`. The new `13434C` hook runs only after native stage eligibility (`134336`) and recipient selection (`134342`). It clears Protect on the explicit simulation recipient before magnitude. Native `134350/134352` skips status application whenever magnitude is nonzero, so this combined damage/status action also needs the hook's explicit true return for a present Protect removal query. The native initial status-presence precheck and all other query branches remain intact. The full `1342CC` phase passes; an outer `1343C8` heap-allocation/law-selection and fresh UI route remains part of production integration testing.
4. Target+04 and actual recipient+08 are distinct contracts. Prediction uses the explicit evaluated target; committed removal uses the post-`12F34C` recipient. The recorded ordinary enemy case has identical pointers. The full native law phase now has separate simulated actor/target pointers and source isolation tests. Redirect/interception still requires an outer integration case; local recipient tests do not certify all outer routing semantics.
5. Add approved action metadata, MP costs, eligibility/geometry and actual fresh UI preview/cancel/hit/miss/law controls in the parent-owned pipeline. Armor's scalar hook is complete as a primitive; Shatter's battle successful-hit and pure prediction primitives are complete within the contracts above. No broader lifecycle completion is implied.
