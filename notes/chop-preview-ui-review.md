# Chop preview UI council review

The white screen came from an undersized relocated racial ability pointer table. The remaining “Knock back!” banner came from the copied Rush description halfword. These are separate defects; neither needs a unit-name getter or AP-copy workaround.

## Frozen evidence and repeatable regression

Pipeline test: `scripts/test-racial-bank-domain.py` tests the current `combat` stage (or `--stage NAME`) without any historical ROM, battle state, emulator, or user save dependency. It freezes and verifies the manifest, ROM, embedded engine, and symbols; checks all22 native table-reference literals; executes 192 native name/getter cases over24 races; and explicitly checks monster race18/name0. It passed current combat `62c848bc42e92fd7652075b235c49347c6b23862`, engine `485c65b5985c7c104ccdfef4d80fc1b61a142fee`. Its reports are in `build/expansion/probes/racial-bank-domain`.

Run `scripts/probe-chop-preview-ui.py` with the bundled Python runtime (Pillow and the repo's Unicorn package are required). It hashes every file in `build/expansion/probes/chop-game-lab` before and after the run and never modifies that evidence or user saves. Diagnostic ROMs, states, screenshots, and `report.json` live in `build/expansion/probes/chop-preview-ui`.

- Original failing ROM: `dc02c7b68c950a503441735b1a0d168c847784cd`; original `prepreview.state` is one A press before the failure.
- Production table-fix verification: `5a11553bf75ca2cddea3c39366b3396713ec84cf`, engine `7b954b8185755f6794d910c9137d4e2f472dc241`.
- Latest repeat: production `9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc`, engine `58c534a82d297fdebcf2db8c156b0000b167045c`; all 24 bank checks and 192 native name/getter cases passed. Hash-specific copies and reports retain both results.
- The UI causal variants deliberately retain the original failing engine, original action423, and original saved state. Only the pointer-table allocation is repaired, followed by the individually stated diagnostic field changes. They do not replay an old action423 state against the later registry that moved Chop to424.

## Complete native racial table

The original table is `0851BA84..0851BAE4`: 24 pointers, immediately followed by its first ability bank at `0851BAE4`. The previous `build-content-data-probe.mjs` allocation copied only seven pointers. Parent corrected it to 24, preserving native banks0 and6..23 and retaining the intentionally expanded five player-race banks.

The enemy in this fixture is unit `020033E4`. Native `C7EA4(unit,3)` returns raw race18; its byte `unit+3A` is0. Native race18 bank is `0851CEA4`, whose first eight-byte record is zero. The short relocated table instead reads `084D1FFA` at relocated-table+18*4. That points into unrelated data: the resulting nameID6184 resolves to `FFFFFFFF`.

The observed name-render fragment is native `2C05E..2C09A`: get raw race using `C7EA4(...,3)`, index the bank table, index the eight-byte record with `unit+3A`, read nameID, and fetch the other-text pointer. At the failing live breakpoint `2C09A`, `r2=FFFFFFFF`, `r4=0902D094` (the table base), and `r5=02031640` (the UI object). The table base seen in the failing stack was not itself the returned text pointer.

`C7EA4(...,0)` remains native and returns the valid enemy name `08567A1F`; its selector0 body at `C7FD4` simply reads the unit's name pointer. There is no evidence of unit-name corruption or an AP-copy return-register bug in this failure. UI flags `E3` select the alternate racial-record name path; changing those flags would hide the incomplete table rather than fix its bounds.

The diagnostic repair puts the complete 96-byte table at `09F00000` and repoints the same 22 native literals (including `2C088` and `CD538`). All remaining ROM bytes and the failing engine remain identical. Replaying the original state changes a one-color white screen into a live preview with 19 damage and49% hit rate. Automated image and reserved-guard checks pass.

The native regression executes `CD480` and the actual `2C05E..2C09A` fragment for all24 races and indices0..7 (192 cases). It checks valid text pointers and exact original record/text preservation for bank0 and banks6..23. Player-race expansion is checked against its installed bank and other-text pointer table. This is a bounded eight-row regression per race, not a claim to execute every ability record.

## The top banner is action metadata

The original race18 record0 resolves other-text entry0 to `085541B4`; the byte stream begins `01 FF 00`. A zero-filled record does not establish the decoded display text. Replacing only other-text entry0 with the literal marker `NAMEZERO` changes the lower target-name row while leaving the top “Knock back!” banner pixel-identical. Thus that banner is not entry0 or a side effect of the racial name lookup.

Native banner producer, independently confirmed by an actual mGBA spin breakpoint:

1. `B5CD8..B5CE6` reads the current actionID from interpreter context `r8+EC` and skips absent action0.
2. `B5CE8..B5CF0` computes the 28-byte action record using the action-table literal at `B5D18`.
3. `B5CF2` is `ldrh r0,[r1,#0x16]`: the description halfword at decimal record+22. Zero skips the banner. A nonzero value calls `29528` at `B5CFC`.
4. `29528` ORs `0x4000` into that messageID and calls native text-task constructor `25688`. The task renders centered text through `25CA4 -> 1539C -> 15110`; the lower racial name instead calls `15110` at `2C0AC`.
5. After creating the message, `B5D00..B5D12` ORs `0x40` into interpreter context+1112 and zeros context+1114. These are message/interpreter fields, not evidence that knockback occurred.

At the live `B5CF2` breakpoint, `r1=09032328` (original Chop423 record) and `r8=020159E4`. Its description halfword is `A5`, copied with the Rush record.

Controlled variants change only that halfword at ROM offset `0103233E` in the frozen diagnostic base:

| Description ID | Actual native preview |
| --- | --- |
| `A5` | “Knock back!” |
| `0000` | No top banner |
| `A8` | “Aimed attack!” |

All three retain UI flagsE3 and the same lower numerical preview (19 damage,49%, HP/MP/EXP/name-region pixels). Removing a text task shifts animated map sprite poses at the fixed screenshot frame, so the test compares the numerical UI rather than claiming the entire screen is unchanged. `banner-0.png` and `banner-a8.png` show the two variants.

Recommendation: give Chop an appropriate native/custom description ID, or use0 to omit its banner. Do not alter combat result flags to remove this copied description. Parent separately established a committed hit with unchanged target coordinates; that behavior test is outside this UI review.

No production engine or builder files were changed by this review. The committed-animation/facing-input investigation remains with the parent and engine council agent.
