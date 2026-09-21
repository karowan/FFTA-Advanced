# Physical final multiplier council acceptance

## Seven-action regression acceptance

Engine `3cee79c1e08f54556b4a70daab50a4d2d3678795` passes **702,317 checks**. Factors cover42411/10,4259/10,4269/10,4271/1,4281/1,42911/10 and43011/10 or18/10. An additional690 exact-threshold cases verify zero/odd/even/65535 maximum HP, below/equal/above half, INT32 extremes, primary/offhand restorative metadata, SP0/4, live registers/NZCV and unmodified frames/units. Every16-bit action identity remains checked, with431 still passing through. The disposable shim image is `324a7359c04212ff0781b256c3d118ce035af890`; the matching production combat ROM is `47f630ded93e0e386e7508c22bda988eaee83977`.

Earlier sections below are historical acceptances on their named builds.

Latest dual-action build passes **525,887 assertions**, 157,361 complete calls and105,396 inline executions: engine `7d963b9cd35c82820c75728b14e54fb1aa4c4d31`, upstream `1b58777133dd55df284f7b379868018f9587ca1e`, disposable `d27868bfad85599a2f9d0bcfc427b547fb43757d`, helper `09101B08`, entry `09103AD4`, no overlay. The exhaustive ID sweep selects only Chop424 at11/10 and Tomahawk425 at9/10. Signed boundaries, INT32 extremes, ±999 continuation clamp, native registers/NZCV, frame/unit isolation and SP0/4 C alignment all pass. Explicit423/426 remain unchanged. Real native restorative item124 primary/offhand cases cover both actions, including positive native references that must become restorative. Historical acceptance entries follow below.

Latest restorative-policy rerun: **481,952 assertions**, 154,440 complete calls, 93,652 inline executions pass on engine `485c65b5985c7c104ccdfef4d80fc1b61a142fee`, upstream axe-visual `7d9f7a2034ee45ca8cec2dc59fc36df5ccf02d16`, disposable `a19ed998b16d912ff75a80b068a025b4aa06a67f`; helper `09101ADC`, entry `09103728`, no engine overlay. Ninety additional installed-shim cases use real restorative item124 as primary, offhand, and first nonempty slot, with signed INT32 edges, zero, SP0/4, and action423/424/425. All live registers, NZCV, frames, units, original arguments and C alignment pass. For Chop with restorative primary, the expected result is negative absolute scaled magnitude even if the incoming reference is positive; offhand3F has no influence. Main arithmetic fixtures explicitly clear equipment so sentinel bytes are not interpreted as item IDs. The historical migration baseline below predates that intentional sign rule.

The corrected helper and disposable installed clamp shim pass **481,592 assertions**, including 154,440 complete function calls and 93,472 native/expanded inline executions. Reproduce with `scripts/test-physical-final.py`.

Frozen accepted engine SHA-1: `58c534a82d297fdebcf2db8c156b0000b167045c`; input axe-visual ROM: `7ab5444fd7042b80d5b8dffd84040fd35ad74c2b`; disposable test image: `17932f1379c0898cb423db61b31b00bf8dda63e2`. The input already contained this engine; no engine overlay was needed. Helper address `09101ADC`, shim `0910368C`. This is the fresh action-domain migration rerun: Chop is424, original Blank Card346 remains native, and explicit423 signed/inline cases preserve ordinary behavior.

## Verified contract

- Every 16-bit action ID at both incoming SP residues 0/4: only action424 changes magnitude. Additional 32-bit action sentinels preserve the original value.
- Chop computes `floor(abs(reference)*11/10)` once and restores its sign. Negative results therefore truncate toward zero. Intermediate 64-bit arithmetic handles INT32_MIN/MAX safely; helper saturation is ±INT_MAX, followed by the native ±999 clamp.
- A 2,921-value signed matrix includes every integer -1200..1200, overflow boundaries, INT32 extremes, and seeded random 32-bit values. Eight actions and both SP residues exercise the installed raw `1300E2..1300F2` replacement.
- At native continuation `081300F2`, all live r0..r11, NZCV, SP/frame contents, evaluated unit bytes, and clamped result match the independent native-clamp oracle. r0 is 999; r5 is the signed result. LR is a tail-transfer scratch value, subsequently restored by the native epilogue.
- The helper receives the original signed r5, action r10, actor r8, and target from **original SP+0x18**. Distinct adjacent stack sentinels prevent accepting the wrong target slot. Every installed C entry is eight-byte aligned; writes remain in the temporary stack frame.

## Defect found and resolved

The initial shim used `MOVS r5,r0` for the upper clamp. Native raw `1300F0` is `ADDS r5,r0,#0` (`051c`), which clears carry; MOVS preserves carry from the preceding comparison. This produced 7,524 NZCV-only mismatches, including reference 1000/action 0 (native NZCV 0, shim C=1). Parent changed all three assignments to ADDS; the full matrix now passes. The next native instruction at `1300F2` itself overwrites flags, so this was an exact continuation-contract defect without an observed damage-value failure.

## Scope

This accepts the multiplier arithmetic and native clamp boundary only. The generated `physical-final-test-only.gba` is a disposable harness artifact, not a playable pipeline build. Full combat formula, descriptor dispatch, hit/miss, AP, law, counters, primary-weapon choice, and committed action behavior require separate integration evidence. Current later combat additions are outside this acceptance.
