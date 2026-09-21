# Custom physical committed-action review

## Seven-action committed regression acceptance

ROM `47f630ded93e0e386e7508c22bda988eaee83977`, engine `3cee79c1e08f54556b4a70daab50a4d2d3678795`: **37,109 checks pass across11,205 native executor calls**. The matrix covers424..430, all66 synthetic primary/offhand weapon effects, both SP residues and native modes0/2, with paired unchanged Fight controls. Added430 executions atHP124/125/126 of250 prove18/10 at/below half and11/10 above half; primary3F remains restorative. Original critical/proc positive controls remain nonvacuous.

The synthetic target now starts at250/250 HP. This prevents legitimate KO cleanup from masquerading as a forbidden weapon-status proc when effect0F increases damage. On the earlier27HP fixture, Reaping Arc could KO the target and correctly clear Doom; that was a test attribution error, not a production3E regression. These are recipient-executor tests, not the complete three-target area-list/UI acceptance, which parent tests separately.

Earlier sections below are historical acceptances on their named builds.

## Dual-action acceptance

The fresh build enabling both Chop424 and Tomahawk425 passes **10,622 checks**, **3,228 native executor runs**, and12 outer-loop gate executions. ROM `e967ee06310e0358348298d574c06cc956f8578f`; engine `7d963b9cd35c82820c75728b14e54fb1aa4c4d31`. The full effects00..41 primary/offhand/mode/SP matrix now runs for both actions. Each committed HP delta equals the independently captured native pre-final r5 scaled once by11/10 or9/10, with restorative-primary sign preservation. Both exclude drain,3E cleanup, critical mode/flags, extra target HP writes and outer second-weapon iteration. Native Fight remains byte-for-byte equivalent in1,056 differential cases; the real critical seed control remains positive. The earlier prospective425 gap below is resolved in this accepted build and that diagnostic has been removed from the harness.

This executor test does not debit or validate Tomahawk's MP cost: payment occurs in the enclosing action flow. It also does not substitute for fresh full-game geometry/line-of-sight/animation validation. The historical single-action investigation follows for native evidence and the defect's provenance.

`scripts/test-custom-physical-commit.py` passes **4,801 checks**, including **1,638 native executor runs** and12 outer-loop gate executions. Final frozen ROM SHA-1 is `7a1f35c5d5c3c7912dafe1f85d7bfcb71b597069`; engine `f15ddb64ed23adb9124c6b01f506f4f0624acb6e`. No production source or pipeline build was changed by this review.

Inputs, a native control image and results are saved under `build/expansion/probes/custom-physical-commit/`. The pipeline advanced between test iterations; each run reads immutable bytes once, validates the manifest hash, and saves that exact input. Earlier iterations accepted `62c848bc.../485c65b5...` and `20819c5e.../f15ddb64...`; the final complete run is the hash above.

## Fixture and coverage

The starting frame comes from real mGBA commit execution at native `A2E70`, source stateSHA-1 `5c448bdc10d6a35f55b1ea472650f4d858d96455`. It retains the real actor, target handles, evaluated position and caller stack. The standalone test verifies the consumed relocated item/action/ability pointer anchors and descriptor bytes against the captured ROM, restores EWRAM/IWRAM/registers for every case, and resumes at `A24A8` so native action routing is included. This adapts an earlier native commit frame to the frozen current code; it is not a new full-screen mGBA route on the latest ROM.

528 cases combine item effects00..41, primary/offhand placement, native modes0/2, and incoming SP residues0/4. The actor carries primary Recruit Axe453 and synthetic offhand52; this illegal dual fixture intentionally challenges isolation, without changing equipment legality. Target Doom state is initialized nonzero, avoiding a vacuous cleanup assertion. Every case compares original Fight against the same image with the three combat entry patches reverted. Both versions preserve actor/target records, result object, live registers, NZCV and observed calls exactly.

For Chop424, every case enters the ordinary A-action route, executes exactly one `12FE38(actor,target,424,453)` formula in mode0, never sets critical bit20, preserves target status bytes and initialized Doom, records no actor-drain delta, and has at most one native HP write to the selected target. Offhand3D/3E/3F leave targetHP equal to the no-effect baseline. Positive native controls include four drain-bookkeeping cases and four target-cleanup cases. Native RNG seed20 produces a real Fight critical; the same seed does not give Chop a critical. Mode2 is a native special-hit mode, not a forced-critical setting.

## Exact native boundaries

| Concern | Native evidence | Required action |
| --- | --- | --- |
| Fight route | `A2592..A259E` admits only action0 andDF223 to `A25A2`; other IDs go `A2DEC`, then ordinary `A2E70` | Preserve this gate.424/425 already avoid it. |
| Critical chance and damage | Fight calls `12E0FC` at `A28F8`, rolls at `A2942`, recalculates `130200` with mode1 at `A2974`, and sets row+0C bit20 at `A29DE..E8` except specialmode2 | No new global critical hook is needed. The ordinary A-action formula remains mode0. |
| Second weapon | Outer `A445C` obtains weapon list/count; `A494E..A4966` repeats the weapon loop only for action0 orDF223. Other IDs leave at `A4968` | Native tests verify0/223 continue and112/424/425/65535 leave, at both SP residues. Preserve the gate. |
| Drain3D | `130654` is called by native formula `1300BC`, Fight bookkeeping `A2B0C`, and ordinary bookkeeping `A30AA` | Exclude applicable custom IDs at both formula/ordinary caller contracts; preserve Fight. |
| Doom removal3E | `130688(item,action,target)` has callers `A2706`, `A2DC8` in the Fight region and `133954` inside generic `13388C` postprocessing | The shared entry guard remains necessary even though custom actions avoid Fight. A formula-only exclusion is insufficient. |
| Restorative3F | `130620` recognizes the native restorative effect; original item124 carries it | Preserve the separately accepted primary-only restorative policy and null/absorb behavior. |
| Weapon enumeration helpers | `12E55C` is called via `12F0DA`/returnLR`0812F0DF` during the native formula, including correct Chop execution | A helper invocation does not prove an offhand strike. Assert actual formula arguments, mode, HP applications and outer-loop gate. |

The committed target-row contract is `object+20+2C*index`, count byte at object+2C0, flags+0C, signed HP delta+1E. Native `A3158` stores the delta; `A3162 -> A2210 -> A2298` applies HP. Results must be captured before free/reuse; late UI RAM is not retained action evidence.

## Poison/status labels and scope

Effects bearing Poison, Slow, Charm and similar names are often **defensive immunities**, as independently decoded in `notes/chop-hostility-procs-review.md`; for example native effect37 is null Poison. They are not evidence of an offensive on-hit rider. The00..41 sweep verifies that these native metadata values do not add target status effects to Chop. It does not invent a poison proc or suppress defensive equipment refresh. No additional general native weapon-status proc executor was established. Effects outside the tested native domain or new future custom riders need their own implementation tests.

The test starts inside the committed executor's existing caller frame and separately tests the outer repeat gate. It does not run the complete outer animation/reaction/law lifecycle for every synthetic item variant. Legal axes already exclude second weapons. Counter/reaction and new persistent enchantment behavior are separate features, not certified by this matrix.

## Verified prerequisite for Tomahawk425

Tomahawk is not implemented in this frozen manifest. A strictly in-memory diagnostic copies Chop's record to425, retaining current production code, then executes the same real commit frame. Primary3D produces actor-drain bookkeeping **-18**, and primary3E clears target Doom **17→0**. The diagnostic restores the original record afterward and is labeled `prospective425` in the report; it is not a playable implementation or a failing claim about currently enabled Tomahawk.

Before enabling425, include it in the appropriate custom physical classification for ordered primary magnitude, restorative policy, and the existing3D/3E exclusions, with its own approved factor/target geometry. Native critical and second-weapon route gates already exclude425. Do not broaden the new behavior to original action IDs or infer that data-only record cloning completes the action.
