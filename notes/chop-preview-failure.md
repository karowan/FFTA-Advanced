# Real Chop target-preview failure

Frozen failing ROM `dc02c7b68c950a503441735b1a0d168c847784cd`. Reproduction: first battle, Marche moves to (4,14), selects Chop targeting Ocyth at (5,14), then confirms the target. The unit's stored old position remains (2,13), as expected before committing Move. Stable input is `build/expansion/probes/chop-game-lab/prepreview.{state,ram,iwram}`.

## Root cause

Parent identified the relocated racial ability pointer table as truncated: the original table at raw `51BA84` contains **24 pointers**, while the content builder emitted only seven. The monster's raw race18 is a legitimate consumer of this larger pointer table. Preserve original rows6..23 when expanding the playable race banks. No change to Chop's combat calculation is indicated by this failure.

Independent live mGBA evidence confirms the exact failing path. A disposable ROM breakpoint (`E7FE`) at native `2C09A` captured:

| Register | Value |
| --- | --- |
| r2, actual text source passed onward | `FFFFFFFF` |
| r4, racial table working base | `0902D094` |
| r5, name display object | `02031640` |
| r6, allocated text buffer | `02022FBC` |
| LR | `0802C069` |
| PC | `0802C09C` (spin-loop architectural PC) |

The saved state/RAM/IWRAM are `build/expansion/probes/chop-preview-council/break-name.*`; only a disposable ROM was patched. This is the **reaction-name branch** at `2C05E..2C082`, selected by display flags bit2. It is not the ordinary `C7EA4(unit,0)` name getter branch at `2C090`:

1. `2C060` loads the displayed unit and `2C064` calls `C7EA4(unit,3)` for raw race. Ocyth has race18.
2. `2C05E/2C088` obtain the relocated racial pointer table. Index18 falls beyond the seven emitted pointers and reads the following data (`084D1FFA`).
3. The branch uses unit+3A's reaction lesson index, reads its name ID and indexes the native name-pointer table. It ultimately produces `FFFFFFFF` as the text source.
4. `2C0AC ->15110` receives that invalid source, causing the visible failure and subsequent memory damage.

The earlier observation `r4=0902D094` in the font call stack was the caller's retained table base, **not** the actual text source. Likewise, flags `00E3` are not by themselves proof of corruption: bit2 legitimately selects reaction naming. Inventory council independently traced the object/unit and out-of-range row; parent established the original 24-row allocation.

## Excluded paths and scope

`scripts/probe-chop-preview.py` executes the actual frozen prepreview RAM through native `B4C90(actor,target,action,item)` and complete native `130200(actor,target,action,item,0,2)`. Chop423 returns eligibility1 and preview19; Rush112 returns1 and18. Both finish, preserve the calling ABI, and write only the native shared action context in these paths. Full call/write traces are `chop-preview-council/native-preview.json`.

These results narrowed the search but did not themselves certify the surrounding rendered UI. The final root cause is a data-table capacity regression exposed by reaction naming, rather than a defect in the signed11/10 arithmetic.

## Corrected table: actual UI replay

ROM `5a11553bf75ca2cddea3c39366b3396713ec84cf` restores the 24 pointer rows. Replaying the identical failing snapshot (SHA-1 `815795d42f027c67cfc83941fae5b49673a46b4c`) with one A press for eight frames followed by 180 frames now renders the preview correctly, with **19 damage / 40% hit**, intact actor/target panels and unchanged reserved guard. Screenshot was visually inspected. Reproduce with `scripts/probe-chop-preview.py --ui --rom build/expansion/probes/combat.gba`; evidence is in `chop-preview-council/5a11553bf75ca2cddea3c39366b3396713ec84cf-ui/`.

Parent additionally reproduced from an entirely fresh battle on that ROM (`chop-in-game/target-selected.state -> preview.state`), removing possible old-state/ROM-pointer ambiguity. The table corruption is resolved.

## Separate banner and facing-confirmation investigation

The now-visible top banner says “Knock back!”; this is separate from the repaired reaction-name path. Inventory council's controlled marker replacement of Other-name0 changes the lower target name only. Both Marche and Ocyth have reaction index0, and original/expanded native `CD4D4` and `12E6A4` return0. Their empty row0 and name0 pointer `085541B4` are preserved. Do not claim an equipped monster reaction explains the banner.

Rush112 and WildSwing113 have identical `00147220` flags. Many original `3F/01/01` actions share them. Therefore the flags alone have not been established as the banner cause. Native action+14 selects animation109 for Rush; table `3947D8`, entry108 selects callback `080F8C39` with 64-byte private state. Its state machine is `F8C38..F8E30`. A disposable entry breakpoint at `F8C42` loaded from the executed snapshot did not trigger in five frames; neither did a breakpoint at driver common return `A6F02`.

**The apparent animation stall was an incorrect interpretation of the automatic facing prompt after Move+Action.** The gray shapes around Marche are facing controls. Replaying one additional A press advances to Montblanc's ordinary Move/Action/Wait menu; this image was independently inspected (`chop-preview-council/executed-extra-A.png`). The inactive animation breakpoints are consistent with the action having already finished.

Independent native hit-roll evidence establishes why HP was unchanged in the original case. A disposable breakpoint at `A300A`, immediately after `12F1DC`, replayed `confirmation.state` plus A. Captured r0=0 is the native miss result, r4=`0x32` is the actual50% roll threshold (the native player path adds10 to the displayed40 at `A2FFC`), and context stage0/action423 remains intact. `A300E` therefore does not enter the successful-hit branch at `A305A`; it eventually skips the magnitude/application through `A3700`. Target-result pointer `02015A04` has flags+0C=`8000` (eligible) and zero HP delta. Action-object pointer is `020159E4`. Snapshots are `break-hit.state/ram`; reproduce with `probe-chop-preview.py --ui --break-hit --rom build/expansion/probes/chop-in-game/frozen.gba --state build/expansion/probes/chop-in-game/confirmation.state`.

Parent's independent controlled native-RNG runs further show seed0 hitting for18 damage (27→9 HP),8EXP, unchanged target tile(5,14), and seed1 missing with unchangedHP/0EXP. These are parent-provided results in `chop-in-game/seeds`, not substitutes for the independent breakpoint above. **No animation donor change is justified by the facing prompt.** The remaining “Knock back!” preview banner is a UI-description issue requiring its own trace; it does not establish that Chop moved the target.

## Committed result lifetime and fresh action424 capture

After action-domain migration, the current matching ROM `9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc` and confirmation snapshot `a9c94e9d12fb88d477406bfa8158c8401b987027` were independently replayed with native RNG seed0 and a disposable breakpoint at `A3762`, just before the executor returns. Reproduce with `probe-chop-preview.py --ui --break-result --seed 0 --rom build/expansion/probes/chop-in-game/frozen.gba --state build/expansion/probes/chop-in-game/confirmation.state` while that matching pair remains current. Evidence is under `chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-result-seed0`.

Captured action object `020159E4` has action424/item453 and count byte+2C0=1. Its first row at+20 is `02015A04`; row+0 points `02022634`, whose unit pointer is target `020033E4`. Row flags+0C=`8081`, state flags+10=`00000400`, signed HP delta+1E=18, and actual targetHP=9. Native `A2EFA` derives row `object+20+2C*index`; `A3150..56` sets HP-result bit1, `A3158` writes delta, and `A3162` applies it through `A2210`. `A3700..08` iterates descriptor stages0..2.

The late 1200-frame seed snapshots have already freed/reused this object address: their bytes must not be interpreted as retained action results. Capture before executor return or instrument `A3072` (magnitude dispatch), `A3162` (HP application), and the native formula entry to prove exactly one primary application. A one-row late result alone cannot prove strike count.

Critical bookkeeping uses target-row+0C bit20 in the Fight path: `A299E` records successful critical recalculation, then `A29DE..E8` sets20 unless specialmode2. The captured Chop row has20 clear. Its +10 bit400 is not this critical bit: `A341E..2E` sets400 following positive `133988`. Detailed offhand/proc call-count coverage remains separate work; no unverified flag meanings are asserted here.

### Actual committed-frame execution counts

`probe-chop-preview.py --ui --break-exec --seed 0` (or seed1), using the same matching ROM/state arguments, now captures the real mGBA frame at `A2E70`, transfers its complete EWRAM/IWRAM and CPU registers into Unicorn, and resumes the unpatched native executor through `A3762`. This is a real commit frame, not an invented action object. Both executions finish without intercepted arithmetic/gameplay callees.

Seed0 calls magnitude dispatch `A3072` once, native formula `12FE38(actor02000080,target020033E4,action424,item453)` once, HP application `A3162(target,18)` once, and native application dispatcher `13388C` once, all at stage0. The only native `A2298` HP write is targetHP9. Seed1 executes no magnitude/formula/HP application and no native HP write. Both have one target result and critical bit20 clear. These are repeatable assertions in the probe; evidence is `9f773...-break-exec-seed0/report.json` and `seed1/report.json` under the council directory. This proves one primary application and no extra native HP targets for these actual hit/miss fixtures; it does not claim exhaustive synthetic Fight-proc exclusion.
