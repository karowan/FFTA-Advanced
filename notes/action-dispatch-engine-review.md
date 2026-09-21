# Council: native action dispatch and first combat integration

2026-09-14. Read-only implementation audit of clean USA ROM `roms/clean/FFTA_US_clean.gba`, SHA-1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`. Addresses below are raw ROM offsets; add `08000000` for CPU addresses. Evidence comes from native Thumb disassembly, literal-reference scans, and table bytes. Vendor files were search leads only. No engine source was changed. This is a practical integration map, not acceptance of the currently unimplemented 129 effects or an exhaustive proof of every dynamically constructed reference.

## Immediate integration blockers

1. **Expanded lessons alone do not create executable actions.** `CCD50` accepts a uint16 action ID without checking the original action-table count. New action IDs346..430 currently read past the original table. Relocate and extend the whole action bank, including its direct consumers, before making new actions executable. `scripts/build-content-data-probe.mjs` explicitly labels custom dispatch as unfinished; this finding identifies that missing implementation, rather than contradicting the probe's stated scope.
2. **Reaction128 is unsafe before it reaches reaction dispatch.** `12E6A4 -> 133ADC -> 1339CC` indexes a native reaction/status compatibility mask using the new ID without a bound. Reaction128 reads `0852835C`, outside the native reaction-mask rows. The later reaction switch separately accepts only1..15. A new reaction handler alone does not fix this earlier access.
3. **Native previews/law checks execute effect callbacks on copies.** `1343C8` allocates two264-byte unit copies and invokes `1342CC`, which can call the same application dispatcher used in battle. Resolving such a copy to its live owner and mutating a persistent sidecar from an application callback would corrupt live state during evaluation. This is a verified lifecycle hazard for upcoming implementation, not an observed corruption in existing code.
4. **There is no single native action callback that performs an entire attack.** Eligibility, accuracy, magnitude, HP/MP application, secondary effects, reactions and costs have separate paths. The ordinary physical-damage application callback is literally `bx lr`: the outer executor applies its magnitude. Custom direct HP writes would bypass that executor's bookkeeping.

## Global action records and literal users

The native global action table starts at `55187C`, has346 records (IDs0..345), and uses28-byte records. Its end is `553E54`; the descriptor bank begins at `553E70`. There is no room to append85 records in place. Allocate431 records, copying original346 records byte-for-byte. The highest new ID430 fits all observed uint16 action-ID paths.

`CCD50(r0=actionID, r1=selector)` truncates ID to uint16 and selector to uint8; `CCD5C..CCD64` computes `28*ID`; literal `CCD84` supplies the base. No ID-count comparison precedes the load. Unsupported selectors return0, which must not be confused with bounds checking on the ID.

| Selector | Native return | Evidence / interpretation |
|---|---|---|
|0|u16 record+00|`CCE24`, Other text name ID|
|1|u8 +02|`CCE28`; element also inspected by law code `13450E`|
|2|u8 +04|`CCE2C`; MP cost read by `12ED98`|
|3|u8 +05|`CCE30`; weapon-associated mode, used by weapon power/element/range and weapon requirements; do not model as a simple boolean everywhere|
|4,5,6,7,8|u8 +06,+07,+08,+09,+0A|Range/shape bytes. Native range fields have packed flag bits; copy a verified donor before changing geometry, rather than writing unencoded distances|
|9|pointer to +0C|`CCE48..CCE4A`; four descriptor-index bytes in the record; inspected native execution loops use stages0..2|
|10|u32 +10|Flags|
|0B..1F|boolean bit(selector-0B) of +10|`CCD68..CCD82`; preserve original flag meanings|
|20|u16 +14|`CCE52`; animation selection field used by native animation consumers|
|21|u8 +0B|`CCE56`; action power used at `12FF5E`|

Record+03 is not returned by this getter. Do not use it in place of the racial learned-record AP cost at+07. Record+19 is a native action classification/filter byte: `133E66..133E7A` directly reads it when deciding action usability. The full semantics of +16..1B were not established in this bounded audit; retain donor bytes until individually justified.

An exact whole-ROM word scan found **17 literal references** to `0855187C`:

`23320 236AC 25998 26C9C 26D3C 26E18 27048 27170 279A0 27A94 A784C B5D18 C3080 C3474 CCD84 133E70 13416C`.

Repoint all17 and assert their original words before patching. A getter-only hook leaves battle menus, AI and direct usability reads pointed at the old bank. This list covers literal occurrences, not arithmetic derivations from another address. No action-ID<=345 guard was found in the traced getter/dispatch paths; that is not proof that every consumer is count-independent.

## Effect descriptors and dispatch stages

Action record+0C contains byte indices into the four-byte descriptor bank at `553E70`. The native209 descriptor rows occupy `553E70..5541B3`, and observed fields are:

`[eligibilityKind, applicationKind, accuracyKind, magnitudeKind]`.

These are indices, not pointers or global action IDs. Do not allocate a fresh byte descriptor for each of85 actions by blindly appending to209: that exceeds256. Reuse native descriptors where valid, use action-ID-specific callbacks behind existing stages, or allocate a bounded shared set of custom descriptors and extend only their necessary dispatch tables.

Descriptor-base literal occurrences: `B4CEC C1CA4 C230C 12F2A0 12F348 12F3C8`. The bank is read directly outside the common context initializer.

| Stage | Bank / native dispatcher | Contract and preservation requirement |
|---|---|---|
|Eligibility|u32 callback bank `3A8604`,29 entries; `130FBC()` uses shared context; `131048(ctx)` explicit context|Descriptor byte0. Callback receives r0=context. Dispatch sites `131004..131012`, `13105C..13106A`; preserve native null/incapacity checks and return predicate|
|Accuracy|u32 callback bank `3A8678`,32 entries; `131378()`|Descriptor byte2; dispatch `13143A..131448`, r0=context. Return percentage narrowed to uint8. Native reaction/status overrides run before/after callback; retaining only its raw result would bypass them|
|Magnitude|u32 callback bank `3A86F8`,46 entries; `131B20()`|Descriptor byte3; dispatch `131B38..131B46`, r0=context. Result is signed; native code multiplies by application metadata sign at `131B4C..131B50`, then performs category-specific checks|
|Secondary effect/application|12-byte metadata bank `3A87B0`,93 native rows; `13388C()`|Descriptor byte1. Row+0 is callback(context), +4 is category, +8 signed result multiplier. `1338BA` dispatches after native status compatibility; native postprocessing follows the callback|

Native table-base references, useful if relocating a bank:

- Eligibility: `131020 131078`.
- Accuracy: `13146C`.
- Magnitude: `131B6C`.
- Application metadata: `1323B8 132430 133920 133984 1339A4`.

`133970(kind)` returns metadata category. `133988()` returns the signed multiplier. `12F358()` usually returns that category but has special handling for application kind59; do not replace it with an unconditional metadata read. Category1 feeds ordinary HP subtraction; category2 feeds MP subtraction; other categories have distinct outer branches. Categories alone do not establish approved direct/fixed/percentage/drain/item/combo semantics; use explicit action/effect tags for the new modifier eligibility rules.

Application status compatibility uses `1339A8(kind,status,flag)` and the12-byte bit-mask base `52790C`. Reaction compatibility uses a separate base `527D5C`. These bases overlap a default/end row in the native layout; do not infer a table length merely by subtracting these addresses. Extending applicationKind also requires supplying its compatibility data, not only a callback pointer. Reusing native application kinds avoids that extra extension for ordinary damage/healing.

## Native action context, preview and ownership

The shared context is `0200F3F0`,52 bytes. `12F230(ctx, actionID, itemID, flag)` initializes it, and `12F2A4(actionID,itemID,flag)` calls that initializer on the shared context. Fields directly established here:

| Offset | Meaning / evidence |
|---|---|
|+00,+04|Actor and evaluated defender pointers, stored at `A2F10/A2F12` and `B4D20` vicinity|
|+08|Current effect recipient, set by `12F34C`; may be null during validation|
|+0C,+0E|uint16 actionID and item/weapon ID|
|+20,+22|Signed stage results retained across initialization; initializer deliberately saves/restores them|
|+26|Native flags; bit10 switches deterministic preview magnitude in physical formula; other flags are effect-processing state|
|+28|Current stage0..2|
|+2C|Pointer to action's descriptor-index vector|
|+30|Pointer to selected four-byte descriptor|

`12F328(stage)` selects a descriptor on the shared context; `12F3B0(ctx,stage)` is the explicit-context counterpart. Neither grants reentrancy to routines that still read `0200F3F0` internally.

The real battle executor at `A2E70` initializes from action-result object `sb+10` (action ID) and `sb+12` (item); target result entries start at `sb+20`, stride2C. It sets actor/defender, loops stages, tests `130FBC`, asks `131378` for accuracy, and calls hit randomization `12F1DC`. On success it sets recipient and calls `131B20` at `A3072`. Native observed loops run stages0..2 (`A2EF0` initialization and subsequent iteration; also `9F61A..9F6C4`, `13027C..1302E8`, `13432E..1343BA`). The fourth descriptor-vector byte is structural storage, not evidence of a fourth executed stage.

**Concrete nested/simulation path:** law evaluator `1343C8` allocates two0x108-byte units at `1347D6/1347DE`, copies actor/target at `1347EE/1347FA`, calls `1342CC` at `134812`, and frees at `13481E/134824`. Another copy loop occurs `134892..1348FA`. `1342CC` sets the shared context, calls eligibility/magnitude and can call `13388C` at `134372/1343A6`. Thus even an application callback is not proof of committed combat. Vendor `_MasterHackInstaller.event:178` disables `1343C8` only under its optional noJudges block; that is a lead confirming the law role, not permission to disable native laws.

Required implementation boundary: carry explicit execution mode and an action-owned state frame through custom hooks. Evaluation mutates only the passed simulation units and an isolated temporary effect-state copy; commit mutates the actual battle unit/state. A helper must not follow AP provenance back to live persistent state when called for law/AI/target previews. Preserve/restore the full shared context and any other actually-used native scratch around nested evaluation; saving just actor and action ID is insufficient. Do not reserve undocumented spare bytes in this context or global EWRAM.

## HP, MP, law and reaction continuation paths

**HP:** after magnitude, `A3150..A3162` records the signed delta at target-result+1E, sets its flag, and calls `A2210(unit,s16 delta)`. That function computes currentHP-delta, clamps to0..maxHP, writes unit+18 at `A2298`, and returns a state transition code used by death/critical result bookkeeping. `A341E..A3478` subsequently calls `13388C` with native result/status buffers. The special action5 path `9F642..9F672` also applies HP directly and then calls the application dispatcher. A universal hook only at `A2210` therefore misses other HP writers and cannot safely distinguish damage from cost/DoT by itself.

**MP:** `12ED98(unit,actionID)` obtains selector2 and implements existing support4 doubling and support10 rounded-up halving. `A45B0..A45D2` calls it, subtracts from currentMP, rejects a negative remainder, and writes unit+1C. `A2438..A2472` is a separate MP restoration path, not another identical debit. Menu affordability reads include `C11A8 C3332 C355E 133E40`; new payment logic must agree across validation and commit, and run once per committed action rather than once per target/stage. Chop's0MP avoids new payment mechanics in the first slice, but does not establish Bloodcasting/multicast correctness.

**Law:** preserve `1343C8` and its callers `134C52 134E64 135072 13528A 135668 135712 1357A8`. Its checks inspect action element (`13450E`), flag selector0C (`134550`), area byte selector7 (`13461E/134644`), weapon mode (`134670`), and item category (`134698`), among other branches. Relocated original records must preserve these fields. Custom geometry/status/damage must be visible to its simulation. A custom effect that skips evaluation or writes only a private final damage value after law checks would not preserve this behavior.

**Reaction:** `12E6A4(unit)` gets assigned global reaction via `CD4D4`, tests native incapacity, then `133ADC(unit+E8,reactionID)`. That loops44 status bits and calls `1339CC(reactionID,status,0)`, which reads a12-byte mask at `527D5C+12*ID`. Native learned reaction globals are1..15; new128 must be intercepted or supplied a relocated extended mask. Preserve the native status restrictions for whichever new reaction semantics actually apply; do not make every new reaction always eligible by returning true.

`12E6E0(actor,defender,actionID,reactionID)` excludes self-targets and action0x109, then branches on reaction1..15 at `12E70E..12E714`; new128 otherwise follows the failure continuation `12EA38`. Its direct caller is `12EAAC`. Add explicit new-only logic without widening the old jump-table range into unrelated bytes. Native accuracy also queries reactions (`1313EA..131422`); preserve these existing checks. Blade Ward's approved whole-action mitigation must be a classified incoming modifier with an action snapshot, not a fabricated native counter command or per-stage readiness consumption.

## Learned records and support namespace

Racial learned records are8 bytes, selected by race and lesson index. +04 is global effect/action ID, +06 is native type, +07 is AP cost in tens. Type1 action rows need uint16 global IDs; support/reaction globals use a separate namespace even when both equal128.

- Unit+3A stores assigned reaction **lesson**; `CD498` returns it. `CD4D4` resolves its racial record then loads **byte**+4 at `CD4FA`.
- Unit+3B stores assigned support **lesson**; `CD4AC` returns it. `CD50C` resolves its record then loads **byte**+4 at `CD532`.
- Unit+3C stores assigned combo lesson; `CD4C0` returns it.

Globals128/129 fit those byte loads. Do not put global IDs directly into assigned-lesson slots. Existing loss/unequip cleanup `CD654` clears matching assigned lessons and must stay effective.

Native support behavior is distributed among comparisons on IDs1..15, rather than a generic support128-entry dispatch table. Confirmed CD50C consumers include `258CA 26A10 A7B88 C13DA C1BB2 CABDE 12C612 12D0C0 12D1BA 12D62E 12DA84 12EDB4 12F4BA 12F77A 12FFDE`. New globals128+ are inert in those inspected comparisons. Do not alias a new support to a native support ID to activate it; that would grant unintended native behavior. `12F48C` handles native offense modifiers, but `12F770/12F798` modify intermediate defense/status-derived values; they are not automatically the correct final damage multiplier insertion points.

## Minimal vertical slice, without changing approved effects

**Soldier Chop:** registry ID `SLD-AX-A1`, global action423, Human lesson172, owner job2, AP100; approved0MP, axe, r1 enemy, attack-style accuracy,1.10P weapon element. This is a small complete action slice because it needs no new custom persistent status or payment rule.

1. Relocate all431 action records and the17 base literals. Keep every original row identical. Populate423 using a physical melee donor's native flags/animation/range encoding, with new name,0MP and explicit axe/enemy/r1/height legality. Do not enable the other84 new actions with accidental donors while their effects remain unimplemented.
2. Native Rush112 has stage0 descriptor3F = `[8,21,10,30]`, stage1 descriptor4B (knockback), stage2 noop1. **Use the ordinary physical stage, not Rush's whole unmodified effect vector**: Chop must not acquire knockback. Descriptor3F routes eligibility to130A95, accuracy to13112D, magnitude to13189D, and application to13215D (`bx lr`). Air Render108 also uses3F but has different range/power geometry; do not clone its range unchanged.
3. `13189C(ctx)` calls `13079C -> 12FE38(actor,defender,actionID,itemID,0,mode,0)`. That formula obtains native offense/defense, chooses action power versus weapon power using selector3 at `12FECE`, chooses action+0B power at `12FF5E` or weapon power at `12FF6A`, applies elemental behavior, native Healer/support/law-related behavior, optional variance, weapon special effects, then clamps signed result to±999 at `1300E2..1300F0`. Preserve this pipeline and primary-weapon behavior.
4. A narrow new-ID branch at the magnitude dispatch/callback boundary is sufficient to select Chop computation while leaving old IDs unchanged. P is explicitly the final primary-weapon physical-hit reference, including defenses;1.10P is not an Attack-stat or weapon-power bonus. Do not claim arithmetic correctness by multiplying the already rounded/clamped native result repeatedly: approved distinct multipliers combine before rounding. Establish one documented native baseline and one shared rational modifier phase before final cap, including Chop, outgoing support and incoming support. The precise arithmetic insertion must be tested against the approved P definition; this audit does not approve replacing elemental/defense operations with a new formula. Weapon-associated mode also reaches native weapon special-effect processing: `130688(itemID,actionID,unit)` tests selector3 at `1306A0` before scanning item+1A..1C. Audit/suppress unapproved weapon-proc inheritance for new A-abilities while preserving required weapon element and Healer behavior; a Rush donor alone is not evidence that this exclusion holds.
5. Return the signed result through `131B20` and the outer executor. Let native hit processing, HP application, result flags, animation, law and reactions continue. Learning/equipment availability/results AP remain on the already-integrated racial lesson172/sidecar path; action423 itself must not award AP per attack.

**Samurai support slice:** Poise (`SAM-S2`, global support129, Human lesson154, AP350) can establish a damage-only support hook with native Protect as one positive case. Its approved result is incoming direct physical/magical HP damage×0.75 when at least one qualifying beneficial status existed at incoming-action start. Resolve support with CD50C on the actual evaluated defender; snapshot status eligibility once for the action in owned evaluation/commit state, apply via the common modifier phase, and preserve native Protect's own effect. Initial native-Protect coverage is a test slice, not completion of all Poise statuses/custom wards/multihit semantics. Poise must also work on legal non-Samurai jobs.

Composure is support128/lesson153/AP250. It additionally needs proven voluntary-movement and own-turn lifecycle state. Merely comparing current coordinates, inspecting job ID, or recording that a movement animation ran is insufficient. Its turn-start/movement/commit hook points remain a followup trace; do not silently substitute a stationary snapshot or a katana restriction. The remaining approved effects retain their specification.

## Acceptance checks for the first implementation

- Execute CCD50 for every selector over all346 original IDs and compare clean results, adjusting pointer-valued selector9 only for bank relocation; compare original table bytes and all17 installed base words. Exercise423 through real native command selection and target preview, not just a helper call.
- On a live Human Soldier, equip teaching axe, verify lesson172 available; remove it before mastery and verify unavailable; earn100AP through native results and verify persistent mastery after save/cold-load. No stat/neighbor-sidecar writes.
- Run native preview and committed execution for hit/miss, front/side/back, illegal target/range/weapon, elevation, elemental resistance/null/absorb, Protect, death, counter prevention, and law violation. Match old donor/control behavior where the specification does not intentionally change it. Assert no unintended knockback, offhand second hit, AP-per-use, or MP debit.
- Test Poise with support129 on Samurai and another legal Human job, with/without each qualifying status, status removed during a multistage action, HP cost, DoT, physical/magical/fixed/drain/item categories, and combined modifiers including Chop. Test law/AI copies and repeated previews for live HP/MP/AP/custom-state isolation and deterministic preview RNG behavior.
- At every C boundary measure SP alignment for native SP mod8=0 and4; preserve displaced live registers and condition flags at inline shims. Callback ABI is r0=context, return r0; ordinary caller-saved registers are free only at an actual native function-call boundary, not arbitrary insertion sites.
- Before accepting reaction128, execute its status mask and native reaction paths under all44 status bits and confirm old1..15 behavior. Before accepting custom state, prove initialization, nested evaluation isolation, turn/action cleanup, KO/Petrify/job-change/battle-end cleanup and save ownership. No combat implementation was executed or accepted by this read-only audit.

## Subsequent bounded data-stage implementation

Parent subsequently authorized `scripts/build-action-data-probe.mjs` and `scripts/test-action-data.py`. These are complete; no shared engine source or Build Engine script was edited. The builder composes `command-core -> command-data -> ability-core -> content-inventory -> content-data`, verifies manifest hashes and ancestor allocation hashes, then allocates after the maximum inherited allocation end. The extra command-data allocation is significant: starting immediately after content-data alone would overlap its command names/descriptors. Current allocation is raw `102F4E4..1032407`, CPU `0902F4E4`, below engine raw1100000.

Output `build/expansion/probes/action-data.gba` SHA-1 `c7cffe2535c985b0622882b2d19bf456f4ee3691`, frozen composed input SHA-1 `f14496fd79b8c2ffcf946726acaf1644abdff05d`. The builder saves that input as `action-data-input.gba` so later parent rebuilds do not invalidate the differential test. Only the431-row allocation and the17 verified base literals differ. The new85 rows are all zero and point to native no-op descriptor0; support/reaction masks and handlers remain unchanged and unprotected for their new IDs, so this remains a data-only test artifact.

Validation passed **44,935 assertions** and **67,854 actual native CCD50 executions**. Coverage includes all346 old records, all85 zero rows,17 direct-literal consumers×431 records, all documented selectors and representative default/truncation cases, both native SP residues0/4, callee-saved registers, uint16 action truncation, and exact full-image scope comparison. Results are in `build/expansion/probes/action-data-test.json`. This validates safe table relocation and inert rows, not target execution, new effects, support/reaction behavior, law-copy isolation or a playable expansion.
