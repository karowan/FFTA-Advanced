# Council: expanded equipment legality and Axe category

Read-only native integration investigation, 2026-09-14. Owned test: `scripts/test-equipment-legality.py`; output: `build/reports/equipment-legality.json`. Parent owns all engine changes. All addresses below are clean USA **ROM offsets**. Tests use the original game's boot-installed IWRAM routines in Unicorn; no game window, user save, or ROM file is changed.

## Current council acceptance

**Accepted for equipment legality and native validator integration.** The implemented hooks in `src/engine/equipment-hooks.s`, guard in `src/engine/equipment.c`, and installation in `scripts/build-content-data-probe.mjs` were reviewed and independently tested on current `content-inventory.gba`, SHA-1 **`a66bafe40a4a551140f31a647f962d40623a9432`**. The repeatable test executes **46,151 native calls with zero failures**, including all original comparisons, new owner permissions, Axe exclusion with every tested support, and new shield jobs. The defects described below are historical findings resolved by these hooks.

The aligned **CADC4** installation is correct. Its literal-load/BX trampoline does not change condition flags; the first `bhi` in `ffta_equipment_twohand_jobs` therefore retains the original hand-count rejection to CADFE. New jobs continue at CADD4, preserving the native Monkey Grip check. Original jobs replay `subs/lsls/lsrs` and resume CADCC, where the original comparison executes. This supersedes the earlier suggested unaligned CADC6 insertion below.

The CABA8 wrapper saves all four native arguments, maps only candidate gear and invalid-slot selector to its C guard, and restores the original arguments before reconstructing the six displaced native instructions. Its rejecting branch restores SP, LR and preserved registers while returning the guard's exact byte. The classifier preserves native scratch locals r2/r3 as well as callee-saved registers; CAD12 establishes fresh flags from its returned boolean. The ordinary shield fallback reproduces the displaced comparison and preserves its flags through the continuation trampoline.

An additional ABI review found that native callers can supply either SP modulo 8 = 0 or 4. The initial fixed-size helper frames did not normalize both cases. The current source fixes both C boundaries by saving the frame pointer in preserved r4, rounding SP down to eight-byte alignment for BL, and restoring the saved frame afterward. **All eight measured helper entries are now aligned**, covering both input residues through direct CABA8 and CB48C. Every native call also checks stack balance and r4..r11 preservation.

Native error-byte cleanup was executed, not inferred solely from the guard's return value: six actual CB54C query/cleanup cases preserve the first hand item and unrelated armor, remove conflicting entries, and subsequently validate successfully. Query mode leaves the unit unchanged. Eighteen Axe selected-slot checks verify exact 1 versus 0x81 results; 3,000 original selected-slot/ability-loss-flag comparisons retain native behavior. No remaining equipment-legality defect was demonstrated in this bounded review. Category31 battle presentation, AP mastery and full action execution are outside this acceptance.

## Historical defects and fixture correction

The initial content-inventory ROM `d29d79765786cffd1945a06be16a9388fe4e2a2c` preserved all 15,162 original single-item and 1,890 original multi-item comparisons. New equipment testing identified three separate defects:

1. **New one-handed weapons are misclassified as shields.** `CABA8` contains an inline old-ID weapon test at `CAD04..CAD14`. It recognizes IDs 1–252, independently of the patched `CB1F4` helper. For example, Samurai's new katana 376 is rejected even by an otherwise empty unit. There were 174 failed new owner/slot checks in the initial test.
2. **Axe flags alone do not prevent Monkey Grip plus shield.** Native two-handed processing checks equipped support ID 6 without consulting item compatibility flags at `CADDC..CADE6` and `CADD4..CADD8`. Soldier with Monkey Grip can equip Axe 453 with shield 253 in either order. This violates the explicit Axe no-shield/no-second-weapon rule. The initial matrix had 68 incorrectly accepted Axe/other-hand layouts, plus 17 incorrectly accepted cases in each direction of the equipment-menu wrapper.
3. **New Dark Knights and Mystic Knight are absent from native shield allowlists.** Correct category masks do not bypass `CAD54..CAD86`; the approved new jobs need selective insertion.

**The opening Recruit Axe fixture was not itself evidence of an Axe-category rejection.** Saved opening equipment evidence `build/expansion/probes/equip-menu.ram` has Marche's underlying job `0x50`, fallback Soldier 2, equipment `(1,288,253,0,0)`. Item 253 is a shield. The real `CB48C` call rejects Recruit Axe while that shield remains and accepts it after the shield is removed. All 255 Axe-alone combinations (17 axes × 3 owning jobs × 5 support cases) pass before the fixes. Axes therefore do not need a broad permission bypass.

## Native function contracts

- `CB48C(unit, newItem, slot)` calls `CAE2C(unit, newItem, slot, 0)`. Its result bit 0 means forbidden; other bits can warn about lost equipped abilities.
- `CAE2C` constructs a candidate five-halfword equipment array, temporarily accounts for ability loss, and calls `CABA8` at `CAF5A`.
- `CABA8(r0=unit*, r1=candidate five-u16 array*, r2=invalid-slot selector, r3=ability-loss flags)` returns a byte. `r2` is truncated to a byte; `0xFF` is normal validation. `r3 & 4` temporarily disables the equipped support in `CABE8..CABF2`.
- Native invalid equipment returns 1, adding `0x80` if the offending slot equals the low byte of `r2` (`CADFE..CAE0A`). This distinction matters: `CB54C` uses `0x81` to decide which slot to clear during validation (`CB574..CB58E`). An early guard must preserve this contract, not always return 1.

## Minimal selective hook contracts sent to implementation

### Inline weapon identity at CAD04

Overwrite eight bytes `00 21 70 1E 00 04 00 0C` (`movs r1,0; subs r0,r6,1; lsls r0,16; lsrs r0,16`). Input `r6=item ID`; produce weapon boolean in `r1` and resume **CAD12**, allowing its original `cmp r1,0; beq CAD3A` to run. Skip the obsolete compare/range branches at `CAD0C..CAD10`.

Preserve `r2`, `r3` and all callee-saved registers: `r3=current gear slot`, `r4=cached hand counter`, `r5=eight-byte validation counters`, `r6=item`, `r7=invalid-slot selector`, `r8=support ID`, `r9=unit`. A classifier helper call must not leak its scratch registers into these native locals.

### New ordinary shield jobs at CAD54

Overwrite eight bytes `90 1E 00 06 00 0E 01 28` (`subs r0,r2,2; lsls r0,24; lsrs r0,24; cmp r0,1`). Here `r2=effective job from unit+7`, `r1=hand counter`, `r3=current slot`. Jobs 117, 119 and 125 go directly to **CAD88**. Other jobs replay the four displaced instructions and resume **CAD5C with their flags intact**. Do not remove the existing allowlist or Shieldbearer support check.

### Second allowlist at CADC6: narrower semantics

This branch is **not simply the reverse order of ordinary one-handed weapon plus shield**. It handles a two-handed weapon when a shield already occupies a hand, followed by the Monkey Grip support check. The ordinary shield byte triggers the first allowlist regardless of which one-handed equipment slot is first.

If extending native Monkey Grip behavior to the new shield jobs, overwrite the same eight bytes at `CADC6`. Matching new jobs go to **CADD4**, which retains the native `support==6` requirement. Others replay the displaced instructions and resume **CADCE**. Preserve `r1/r2/r3` and the native locals. Axe exclusion must still apply before this path.

### Axe guard at CABA8 entry

The most contained rule is a wrapper that checks the whole candidate equipment array before entering the original validator:

```text
if an Axe-category item exists and there are at least two weapon-or-shield entries:
    reject with 1, or 0x81 when r2 identifies the offending second hand entry
otherwise:
    execute the unchanged native validator
```

Weapons here are categories 1–19 and 31; shields are category 20. Armor/accessories do not count. Select the second weapon-or-shield entry in ascending gear-slot order as the offending slot, matching the ordinary sequential conflict model. Preserve the full original arguments and return convention. The guard must not modify the candidate array or unit.

A 12-byte preserved-`r3` entry trampoline overwrites `F0 B5 4F 46 46 46 C0 B4 86 B0 81 46`:

```text
push {r4-r7,lr}
mov r7,r9
mov r6,r8
push {r6,r7}
sub sp,0x18
mov r9,r0
```

After a passing guard, reconstruct these six instructions and resume **CABB4**. On rejection, return through the original LR with the original stack and preserved registers. A literal-load trampoline must save/restore `r3` because it is a real fourth argument. Guard return zero can mean native fallthrough; nonzero means an immediate rejected result. This avoids copying the entire validator and preserves all original shield, support, armor and slot rules.

## Repeatable test and remaining validation

Run with the bundled Python runtime:

```powershell
. ./scripts/resolve-python.ps1
& (Resolve-FftaPython) scripts/test-equipment-legality.py
```

`--allow-incomplete` produces diagnostics without a failing exit status while integration is in progress. Without that option, any mismatch against the approved rules or the original engine fails the test. `--rom` selects another generated probe. The report records the exact tested SHA-1.

The expanded suite adds 3,000 differential checks for the fourth argument's ability-loss flags and the selected-invalid-slot error byte; Axe/armor compatibility; explicit `0x81` conflict-index checks; opening Marche with/without shield; new shield jobs with both old and new legal one-handed weapons. Every native call checks return, stack balance and `r4..r11`. The test also verifies `CB48C` leaves the unit unchanged. Synthetic support records exercise native support IDs 6/7/8/15, not AP mastery or support-learning integration.

The first extended run, before the requested hooks landed, tested ROM `09d2b680c8ace1816b09a7beddb58ea8dd08206e`: 46,103 native calls; all original comparisons passed; 308 new-rule checks failed as expected. Read the latest JSON report for subsequent implementation results rather than treating this baseline count as current.

## Axe category consumer audit beyond equipment legality

A bounded scan of direct calls to item getter `CA7A4` selector 3 found the following **verified general weapon-family range gates**. They accept categories 1–19 and send 31 to a fallback. They are priorities for battle presentation integration after the actual equip blockers above:

| Consumer | Exact gate and fallback | What is established |
|---|---|---|
| `986C0` category read | `986DA..986DE`: `(type-1)>18` → `98758`, sets group 0 | Battle weapon/animation dispatch does not assign a native weapon group to Axe31 |
| `A589C` category read | `A58A0..A58A4` → `A597C` | Selects default sound ID `0x7E` rather than a native family branch |
| `A7ED8` category read | `A7EDC..A7EE0` → `A7FB8` | Same default sound ID `0x7E` |
| `B3C60` category read | `B3C64..B3C6A` → `B3D88` | Bypasses the nineteen-entry dispatch and selects its default function pointer |

These bounded tables have guarded fallbacks; an out-of-bounds access was **not** demonstrated at these sites. Copying a donor item record alone does not change these category gates. Use an explicit visual-family donor only at presentation consumers, retaining category31 for real permissions and Axe-only abilities. A universal item-type getter alias would erase Axe identity throughout gameplay.

Other verified category checks are narrower gameplay filters, not demonstrated bugs: `26818` / `133F10` accept spear15; `A27F0`, `A27FE`, `B7CC8..B7CD0`, `B7D7A..B7D82`, `12C5FC`, `12E82A..12E838`, `12E8E8` distinguish bows13/14 and/or gun19. Axe should remain on melee/default paths there unless the owning ability's intended rule says otherwise. `130972..13097E` recognizes categories1–9; its owning action semantics need identification before extending it. `12D450..12D460`, `132CEE`, `13469C` compare against caller-supplied category lists and require reviewing those lists in their action context.

The actual permission-mask consumers (`CAC44..CAC4C`, `CB470..CB47E`, `CB5F8..CB600`, `CC988..CC992`) use 32-bit category bits and can represent category31. Their masks still need the right content. `CBD5E` delegates weapon classification to patched `CB1F4`, so its native weapon-tab selection benefits from the central helper. The formerly independent inline `CAD04` test is now hooked to the same classification behavior.

This scan is not a claim of exhaustive indirect/direct-ROM-field discovery. Battle execution, animation rendering, shops, Throw/Draw eligibility, and action-specific family restrictions remain separate integration tests. No design changes are recommended merely because a native family-specific test excludes31.
