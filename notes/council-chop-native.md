# Installed Chop native-path council acceptance

## Seven-action regression acceptance

ROM `47f630ded93e0e386e7508c22bda988eaee83977`, engine `3cee79c1e08f54556b4a70daab50a4d2d3678795`: **33,750 checks pass** for424..430. The shared native formula and3D/3E matrices now include426/429 and430; all original0..346 callbacks remain unchanged. This caught the area donors retaining Earth at action+02; the accepted build sets00 and passes weapon-element normal/null/absorb/restorative controls. Armor uses an independent native capped-defense oracle; Shatter's private evaluated copy is verified byte-for-byte before normalizing its pointer in argument assertions. Executioner's ordinary11/10 case is covered here; exact low-HP boundaries are independently covered in the final and committed tests.

Earlier sections below are historical acceptances on their named builds.

## Dual-action acceptance

ROM `e967ee06310e0358348298d574c06cc956f8578f`, engine `7d963b9cd35c82820c75728b14e54fb1aa4c4d31` passes the updated Chop424/Tomahawk425 suite: **22,852 checks**, 18,480 entry executions, 1,926 complete calls, and2,652 aligned C entries. All original actions0..346 retain native callback behavior;423/426 are passthrough controls. Both actions use ordered primary axe and one final factor: reference16 becomes17 for Chop and14 for Tomahawk. Both weak/normal/null/absorb/half matrices preserve restorative behavior; native positive16 from absorb+3F becomes-17/-14. Shared3D/3E exclusions pass at all observed callers and both SP residues. This supersedes the historical single-action counts below.

## Latest restorative-policy acceptance

Current ROM `62c848bc42e92fd7652075b235c49347c6b23862`, engine `485c65b5985c7c104ccdfef4d80fc1b61a142fee`: **20,344 assertions**, 16,800 entry executions, 1,658 complete calls, 2,020 measured aligned C entries pass. The earlier migration evidence below remains valid; this rerun adds the approved restorative-primary rule.

Native item124 is the only original item carrying effect3F; native `130620(124)` returns1. The native formula tests set item+9=Fire and target+0D to each of weak0/normal1/null2/absorb3/half4, confirmed by native item/unit getter layouts. Both incoming SP residues exercise no3F, primary3F, and offhand3F. No arithmetic or elemental helper is stubbed. Absorb plus primary3F gives native +16 after two sign reversals, while Chop correctly gives -17. Null remains0; ordinary/offhand absorption remains -17; normal primary3F gives -17. All30 elemental cases preserve evaluated unit records and execute exactly one formula/final phase. The matching physical-final test additionally accepts the changed-sign inline ABI using real native item124 at INT32 extremes.

## Action-domain migration acceptance

`scripts/test-chop-native.py` passes **20,233 assertions**, **16,800 full drain/effect function executions**, **1,596 complete magnitude/formula calls**, and **1,772 measured aligned C entries**. No engine files were edited.

Final frozen ROM SHA-1: `9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc`; engine `58c534a82d297fdebcf2db8c156b0000b167045c`. This rerun uses the corrected 347-original/432-total action domain, with Chop424. Explicit423 cases preserve native drain/effect behavior; the physical-final companion tests all65536 IDs and confirms only424 multiplies. Snapshot ROM, manifest and symbols are under `build/expansion/probes/chop-native-council`; results are `build/expansion/probes/chop-native-tests.json`. Historical pre-migration acceptance used Chop423 on ROM `dc02c7b68c950a503441735b1a0d168c847784cd`.

## Drain and effect entry hooks

The harness independently decodes native direct BL instructions and verifies these complete caller sets within the original executable region:

| Helper | Native call offsets | Return/LR contracts tested |
| --- | --- | --- |
| `130654`, drain3D | `A2B0C`, `A30AA`, `1300BC` | `080A2B11`, `080A30AF`, `081300C1` |
| `130688`, effect3E | `A2706`, `A2DC8`, `133954` | `080A270B`, `080A2DCD`, `08133959` |

Each caller runs at SP residues 0/4, with item IDs 0/1/52/453/460, effect 0/3D/3E/3F in each of the three native item effect bytes, and ten action values including original IDs, Chop424, adjacent expanded IDs423/425/431 and high-word sentinels. An unknown drain caller also executes native behavior.

- Drain suppresses only action424 at the ordinary formula caller (r10) or ordinary application caller (halfword at r9+0x10). Fight-region and unknown callers retain native results. The native halfword caller naturally truncates high action bits; the formula caller compares its already-normalized r10 directly.
- Original paths match r0..r11, NZCV, caller SP/frame and unit contents exactly. Chop suppression preserves all callee-saved registers and caller frame. Caller-saved registers/flags on the intentional early return are not required to equal the suppressed operation.
- Native effect3E clears unit+EA bit0x10 through `CDFE4(target,0)` and unit+D9 through `CE420(target,0)`. The fixture explicitly initializes both, avoiding an empty-state test. There are **360 observed native mutations**, including **144 prevented specifically for Chop**. There are **960 positive native drain detections**, including **72 blocked in Chop's applicable caller contexts**.
- Original nonzero/zero drain paths resume after the installed span at `130664` or `13067E`; effect replay resumes at `130694`. Full helper execution returns to the original caller with its original stack. These hooks require no C call or extra global state.

## Full native physical calculation

The magnitude wrapper executes the actual `12FE38` formula and its native callees; no damage arithmetic, item getter or status helper is intercepted. Code hooks observe arguments and the pre-clamp r5 only.

- Every original action0..346, at both SP residues, produces the same full `13189C` callback result and evaluated unit contents as the input pipeline's native callback.
- All axes453..460 execute exactly one formula call with `(actor,target,424,primaryAxe,0,2,0)` in preview mode. Stronger offhand and misleading context item values cannot replace the first equipped weapon. Five offhand choices give the same result for a fixed primary axe.
- Exactly one observed final reference receives the single signed11/10 factor and native ±999 clamp. With Recruit Axe the native reference16 becomes17. The independent native formula without the new code hooks returns the same reference before multiplication.
- Synthetic primary/offhand effects3D,3E,3F in each effect byte confirm primary3F preserves the native sign reversal (-17), while offhand3F leaves +17. Primary/offhand3D or3E do not alter this fixture's result. The drain-entry matrix separately proves positive3D detection is suppressed, so that conclusion does not rely on an ordinary living target's unchanged sign.
- Evaluated unit records remain unchanged by the formula. Every measured C entry (`ffta_physical_magnitude`, `ffta_primary_weapon`, `ffta_physical_final`) is eight-byte aligned despite incoming SP0/4.

## Limits

This is acceptance of the installed entry hooks, original callback preservation, ordered primary-weapon magnitude and preview formula composition. Synthetic dual-weapon fixtures test selection robustness; they do not authorize illegal axe equipment. The test uses the battle-ready RAM fixture for global context and deterministic preview mode, and does not execute an entire committed action, hit/miss dispatch, reaction/counter, law-copy application, AP learning or RNG/variance distribution. Parent's real battle and eligibility work remains necessary. The latest eligibility source is intentionally outside this test's acceptance.
