# Council review: preserving native jobs while integrating explicit lesson lists

Reviewed 2026-09-14. This is an implementation map from the clean USA ROM, the current generated job/lesson data, the existing AP helpers, and the pinned `tools/ffta-engine-hacks` source. No engine or builder changes were made by this review. Addresses below are ROM offsets; add `0x08000000` for GBA addresses.

**Recommended approach:** retain native command IDs and every original job record. Add new-only command resolution and presentation, and route the twelve affected jobs through an explicit lesson iterator. Build the job wheel in pages of at most twelve entries. Existing donor fields already feed the native generic party sprites and portraits; the direct job-icon functions need separate new-only donor mapping.

This map is based on direct disassembly and data inspection, not a claim that these unimplemented flows passed an emulator test. Supporting disassembly is saved under `build/expansion/probes/job-ui-native-disassembly*.txt`. Some dumps pass over literal pools; conclusions below use actual instructions and verified branches, not decoded data.

## 1. Keep job identity and command identity separate

Native unit fields already distinguish them:

| Field | Meaning |
|---|---|
| `unit+5`, `unit+7` | Effective/special job and current fallback job, consumed by the unit-aware getter |
| `unit+8` | Secondary **job** ID |
| `unit+35`, `unit+36`, `unit+37` | Primary, secondary, fixed extra **command** IDs |
| Job record `+10` | Job's command ID |

Original IDs overlap across races: command2 belongs to Human Soldier and Bangaa Warrior; command10 is Black Magic for three races. Original maximum command ID is73, whereas the new records deliberately use unique command IDs116..125. Keep the latter convention limited to those ten records.

`C9078(unit)` is the missing reverse resolver. It searches native racial job ranges for a job whose `+10` matches `unit+36`, with a separate Human Divine Knight exception. A narrow entry wrapper can return command116..125 directly as a job **only when its generated race matches the unit**. Otherwise execute the original function, including its failure return0 and original special-job exception. A wrong-race extension command should resolve to0.

That wrapper lets the original secondary-command commit keep working: `7DFD2..7DFD6` writes the selected command to `unit+36`; `7DFDE` calls `C9078`; `7DFE8` stores its result in `unit+8`. Selection row `+0E` is read at `8479A`, then retained as a halfword at `847A0`. IDs125 and below already fit. **Do not install the vendor's global `8479A/847A0/7DFD2/7DFE8` job-ID rewrite.**

The original job-change function `C8C24` already obtains primary and secondary commands from the appropriate job records (`C8CBA..C8CDC`) and clears duplicate primary/secondary commands. It also preserves the special fixed Item handling (`C8CEA..C8D06`). Do not replace those rules with a blanket two-job-byte copy or broaden the Alchemist exception to Chemist.

### Command text needs its own allocation

Native command descriptors at `527244` are 74 four-byte records: two-byte **Other text** name and two-byte help ID. Reading command116 here currently enters unrelated data. Relocate the table with original rows0..73 byte-identical, reserved rows74..115 initialized safely, and new rows116..125. Allocate appropriate command names/help in their existing text namespaces; the new job-name IDs838+ belong to the item/job-name namespace and cannot be inserted as Other IDs.

An exact pointer search in the clean ROM found eleven references to `0x08527244`: `25850`, `2632C`, `263CC`, `2647C`, `26660`, `26704`, `267D0`, `2892C`, `74C0C`, `7BE7C`, `7DA78`. Ledger and verify these pointer changes. This is a text-table reference inventory, not proof that every battle command branch accepts116..125; battle availability and effect dispatch still require their own integration.

## 2. Explicit lesson lists: what actually needs replacing

Current `build/expansion/job-lessons.h` has contiguous lists for all ten new jobs. The two expanded original jobs are noncontiguous:

- Soldier2: native1..11, followed by172..177.
- Gladiator16: native33..43, followed by105..110.

Use `ffta_job_lesson_count/at` for all twelve affected jobs so a future ledger reorder cannot silently change ownership. **Never widen Soldier to1..177 or Gladiator to33..110.** That would import unrelated jobs, commands, reactions and supports. Maximum explicit list length is19 for Mystic Knight, which includes14 actions plus its support/reaction/combo lessons; battle lists must filter ability type rather than assuming the first8 or first14 records are all actions.

`C94D0(race, lesson)` scans jobs0..115 using first/last bounds and returns the owning job, or0. Install an explicit reverse mapping for **added** race/lesson pairs, including the six Soldier and six Gladiator additions. For original lessons, retain native execution exactly. Simply raising its `C952A` maximum to125 does not cover the axe additions, and widening bounds would assign unrelated lessons to the wrong command. Assert unique `(race, lesson)` ownership when generating the reverse map; the same shared class on different races is not a collision.

### Discovery has two different native paths

`C8EBC(unit, byte_output)` builds the known command list and deduplicates command IDs. Its special/guest path scans nonzero AP bytes (`C8F76`), calls `C94D0` (`C8F8C`), then reads the returned job's command field (`C8F9A`). The current AP hook repairs that byte read.

**Ordinary recruits use a different path at `C8FDE`:** hardcoded racial clan-unlock flag ranges, followed by job `+10` lookups. Therefore the `C94D0` fix alone will not add new commands for normal recruits. Prefer preserving the original list first and appending new, same-race commands under an explicit per-unit predicate, deduplicated and capacity-checked. Preserve all existing Item, special-character, and original visibility behavior. Do not grant a new job to every clan member because one member fulfilled its prerequisites.

Keep three predicates distinct: a job can be visible in the wheel, a unit can qualify to change to it, and a command can have an action the unit can actually use. `ffta_new_job_eligible` provides only the second; `ffta_job_action_count(...,1)` supplies mastered/equipped actions. Original `7D8EC` accepts nonzero AP anywhere in the selected range, even partial knowledge, so an expanded predicate must deliberately distinguish browse visibility from selectable/usable actions. Do not alter original command behavior incidentally while choosing the new-job rule.

### `CCE60` is a slot resolver, not a command-ID lookup

Actual signature is approximately `ability_bank CCE60(unit, slot, uint8_t *first, uint8_t *last)`:

- Slot1 gets the primary unit-aware job bounds.
- Slot2 gets bounds from `unit+8`, the secondary job.
- Slot3 uses Item job1 and race0.
- A primary/secondary command byte of1 also invokes the Item/race0 override.
- It returns the race ability-table pointer and optionally writes byte bounds.

Preserve this ABI and Item override. A first/last pair cannot describe the expanded original lists. The safest initial implementation leaves this function native and changes each affected iterator to use `(resolved job, count, position -> lesson)` when a custom list exists. Avoid an undocumented fake `FF/FF` interval as a universal API: unaudited consumers can interpret it as a real ability index. Do not create a process-global iterator whose state can be overwritten by nested menu, AI, or preview calls.

Direct Thumb BL references to `CCE60` in the clean code region are `26000`, `26022`, `26B24`, `27316`, `279F4`, `7B980`, `7C316`, `7C466`, `7D926`, `133DA0`, `133FB0`, `134220`. These are the finite starting checklist for consumer review, not a completeness claim for indirect calls.

## 3. Party ability lists and equip menus

`7C28C` contains several branches. Hooking only the vendor's `7C470` location repairs the secondary-command branch, **not** the primary list built from `7C316/7C338`.

For a custom job, build native 20-byte rows and the native parallel halfword lesson-ID list from explicit membership. Preserve the original row contract:

| Row field | Meaning |
|---|---|
| `+0` | Display row index |
| `+2` | Originally zero in this ability-view branch; do not globally repurpose without auditing readers |
| `+8` | Other name ID, written as a full word by the native code |
| `+0C` | Help ID |
| `+0E` | AP/availability display byte |
| `+0F` | Required AP value |
| `+10` | Ability type |

The separate lesson-ID list receives the real race lesson index (`7C4C2`). Keep it synchronized with filtering and cursor restoration. The native branch skips zero-knowledge entries in some views, while another mode shows all; preserve the caller's mode rather than making enemies or in-battle inspection reveal everything. Obtain AP through the owner-aware helper; `7C4D8..7C4E0` is another inline AP display read, separate from the filter at `7C49C..7C4A6`. Current source contains a filter hook but that does not by itself prove correct display for Human sidecar lessons.

`7D96C` constructs Action/Reaction/Support selection rows. Action commands come from `C8EBC`, are greyed through `7D8EC`, and use command descriptors from `527244`. A narrow custom-command branch in `7D8EC` should resolve the job and test its explicit list against the actual roster owner; its temporary unit copy at menu base`+1BE4` is not a valid sidecar owner. Normal selection can remain native after `C9078` and the descriptor table are extended.

Reaction and Support branches use the race ability table plus `CCFB8(unit,out,type)`; `CD0EC` constructs the related known-ability lists. Their upper bound is `unit+34`, not a fixed8. Existing high-AP hooks/count normalization are the right direction: retain generic same-race selection so a Samurai support can be equipped on another Human job. Validate real row IDs and persistence, not only text. A type2/3 list should never be gated on the teaching job or current weapon. Combo type5 likewise needs the existing slot behavior preserved.

Capacity evidence: `7D96C` reserves a `0x100`-byte local ID list and writes20-byte rows at output`+0x230`; `7C28C` has a `0x200`-byte parallel halfword area before its local bound bytes. Those temporary arrays accommodate current lesson counts. This does **not** establish capacity of the outer row allocation, count fields, scroll callback, or current-job navigation buffer. Assert those actual ranges with guarded native calls and mGBA before enabling the UI. Test the19-row Mystic Knight list and17-row Soldier/Gladiator lists specifically.

## 4. Job wheel and changing jobs

The native job-list helper `C8A24(unit,out)` explicitly clears **12 bytes** at entry. Its results are signed bytes: low7 bits are the job ID, high bit participates in native selectability rendering. Wheel state begins at menu base`+1270`, its ID array is at`+1278`, and per-entry records begin12 bytes later with stride`0x1C`. The original caller at`85C90` writes directly into that ID array.

Human has11 regular native jobs plus2 new ones, so simply raising a loop maximum or appending both jobs there overwrites the first wheel entry. Other regular races reach9 or10 jobs. All new IDs116..125 still fit the native seven-bit job representation; **retain the `0x7F` mask at87D06**. Vendor's `0xFF` replacement is associated with its replacement wheel format and cannot be transplanted independently.

Recommended implementation:

1. Let the native builder produce its original list into a bounded temporary buffer, retaining ordering, original unlock side effects, story restrictions, and disabled encoding.
2. Append at most the same-race new jobs, with visibility and per-unit eligibility applied separately. The two Chemists can be offered immediately without altering any original prerequisites.
3. Copy a page of at most12 entries into the actual wheel and construct only that page's native records/sprites. Keep a small, explicitly allocated menu-owned page state and clamp/reset it when the selected unit or available-job count changes.
4. Add L/R page handling with visible page indication; select the page containing the current job initially. Never let an invisible thirteenth entry be selected by cursor arithmetic.
5. Recheck eligibility on confirmation. Preserve the original `C8C24` change operation, equipment cleanup, fixed Item behavior, and named-character rules.

Vendor hook locations `85CAC` and `8616E` are useful leads for replacing the populated page and reading page buttons. Its implementation also clears roughly256 bytes after the wheel header, writes page state to hardcoded`0203FFF0`, changes palette ownership and changes the irreversible-change message. Do not copy those choices without a local ownership/behavior audit. New page state belongs in a documented allocation, not assumed free RAM.

The separate enable/confirm checks for Change Jobs (`750E2`, `76A68` vendor leads) need new-job awareness too. Preserve native special-character/story restrictions before considering extension eligibility. A broader generic job availability scan must not expose NPC, monster or event-only jobs44..115. Returning a 13-entry list from a global `C8A24` wrapper would break other callers with original buffers, so keep expanded paging local to the wheel path unless all callers are changed.

One approved integration detail extends beyond new jobs: mastered Soldier/Gladiator axe **actions** must count toward existing owning-job unlock gates. Native prerequisite counting at`C8B26..C8B92` loops first/last bounds. Selectively use the explicit action-count helper for requirements on job2 or16 while preserving every other original rule and clan-flag side effect. Support/reaction mastery must not count toward those gates.

## 5. Visual donors: fewer new hooks are needed

The ten records already clone same-race donor graphics fields:

| New job | Donor |
|---|---|
|116 Samurai |6 Ninja|
|117 Human Dark Knight |3 Paladin|
|118 Viking |13 Warrior|
|119 Bangaa Dark Knight |15 Defender|
|120 Nu Mou Chemist |25 Beastmaster|
|121 Geomancer |27 Sage|
|122 Moogle Chemist |41 Gadgeteer|
|123 Bard |36 Animist|
|124 Dancer |29 Elementalist|
|125 Mystic Knight |30 Red Mage|

Contrary to the broad vendor installation, the native generic party sprite path is already record-driven. Both party`87B70` and wheel`87D40` call`22238(unit,palette_out)`. That calls`CB65C` for palette selectors6/7 and`CB714` for animation selector4. The companion`CB750` uses selector5. Thus valid copied fields already feed the native sprite animation lookup; IDs116..125 are not themselves used as raw sprite table indexes on that path. Generic portrait consumers`CB79A`, `CB7F0` use selectors9/A/B. Named-character branches instead use the native character table and should be preserved. No blanket portrait-table expansion, custom compressed sprite loader, or global job alias is needed just to reuse donor artwork.

Direct **job icons** are different. `CB9E0(dest,job)` clamps116+ to45 before lookup; `CBA14(job)` also clamps them to45 for palette selection. Wrap these two entries so only116..125 maps to the appropriate donor. Tail-call unchanged original logic for all other jobs. Preserve the existing subtle difference for original job77: the graphic routine explicitly special-cases77, while the palette routine uses its ordinary range branch. Do not "clean up" that original difference during this task.

These are temporary donor visuals, not unique finished job art. Real-game review must show each job's portrait, party sprite, wheel sprite, command label, action list and equipment preview, including Marche/Montblanc and relevant named-character aliases. Getter equivalence alone does not establish a complete visual result.

## 6. Battle and regression gates before enabling the jobs

The existing vendor's player action hooks`26D70/26F6C` and enemy hooks`133FEC/13406E` identify the two halves of range iteration. Adapt the explicit-list selection at these consumers rather than assuming a menu fix changes battle behavior. Native command usability`25FDC` invokes`CCE60` with slot1 or2 and iterates bounds too. Preserve its original battle restrictions while replacing only custom-job membership/availability. The Morpher, Beastmaster and stealing paths among the other`CCE60` callers must continue native execution unless their resolved job is specifically in the twelve-entry custom registry; never interpret an original command ID as a job.

Required regression evidence for this integration:

- Original `C9078` and `C94D0` inputs produce original results; ten new commands round-trip for the correct race and reject the wrong race. All added lessons map to the intended owner; Human reserved142/143 remain unowned.
- Normal generic recruits discover new commands, not just special-unit fixtures. Partial, equipped, mastered and revoked AP states produce the intended browse/selection/usable distinctions.
- Soldier/Gladiator list exact native lessons plus six additions, and zero unrelated lessons. All19 Mystic Knight lessons scroll with correct names, AP, type, help and cursor identity.
- Each new mastered Support/Reaction can be selected from a different legal job of that race, saved, cold-loaded and removed. Human sidecar AP is read through the roster owner even when UI previews use copies.
- All13 regular Human jobs are reachable through pages; page changes, unit changes, current-job selection, cancel and repeated reopening preserve native data. Guard the12-byte array and wheel sprite records against writes beyond the selected page.
- Actual job changes for all ten additions retain accumulated stats, equipment rules, AP and secondary commands; the original Alchemist retains its fixed Item command and original named/story restrictions remain intact.
- Primary and secondary new commands produce identical intended action membership in the party screen, battle command window and targeting preview. Original Blue Mage/Beastmaster/Morpher/Item/steal behaviors retain their native paths.
- Original command text descriptors are byte-identical after relocation and all11 pointers resolve correctly. Original party/wheel/menu screenshots match before and after, while each new job uses its intended temporary donor.

The most economical integration is therefore several narrow resolvers plus bounded custom-list builders, not the vendor's global job/race overhaul. Keep the work test-only until these actual menu and battle paths are exercised; record/table tests alone cannot close these gates.

## Follow-up: `C8EBC` output-buffer capacity

All five known direct callers can safely receive the proposed13–15 command IDs without resizing their stack frames. Each has a conservative256-byte output region. This conclusion comes from native frame allocation, live adjacent locals, and the immediate output-consumption loop; it is not inferred from the old number of jobs.

| Call site | Containing function/frame | Output region relative to current SP | Adjacent live local/evidence | Safe byte capacity |
|---|---|---|---|---:|
|`7C9E2`|`7C7E8`, `sub sp,#120` at`7C7F2`|`+00C..+10B`|Cursor word initialized at`+10C` by`7C9D0..7C9D6`, reread at`7CA2C`; output read from`+C` at`7C9F2`|256|
|`7CB74`|Same function, frame`120`|`+008..+107` conservatively|Cursor word at`+110`, initialized`7CB5E..7CB68`; leave the gap`108..10F` unclaimed; output read at`7CB86..7CB8C`|256|
|`7D3F0`|`7D240`, `sub sp,#114` at`7D248`|`+008..+107`|Cursor word at`+108`, initialized`7D3DE..7D3E4`, reread`7D43A`; output read`7D402..7D408`|256|
|`7D53E`|Same function, frame`114`|`+008..+107` conservatively|Cursor word at`+10C`, initialized`7D52E..7D532`; leave`108..10B` unclaimed; output read`7D550..7D556`|256|
|`7D9E2`|`7D96C`, `sub sp,#104` at`7D976`|`+000..+0FF`|Live row pointer stored at`+100` by`7D9A6`, reread`7D9F4`; output passed as SP and read from SP|256|

The first two restore their frame with`add sp,#120` at`7D230`; the next two restore`114` at`7D8DC`; the final caller restores`104` at`7DC00`. No nested call's frame overlaps the caller output: normal stack growth is downward, while these arrays are above the caller's SP. A wrapper must still preserve the original SP and callee-saved registers.

Native `C8EBC` writes **one byte per command and returns the count**, with no trailing terminator. The count is narrowed to8 bits, so the sensible API ceiling is255 entries even though the physical buffers accommodate256. The actual approved expansion is far below that:

- Normal Human:11 original job commands + at most1 Item +2 new = **14**.
- Conservative special Human path: also allow native Divine Magic command73, giving **15**.
- Bangaa:7 + Item +2 = at most**10**.
- Nu Mou, Viera, Moogle:8 + Item +2 = at most**11** each.

The native Alchemist's fixed Item does not require a second duplicate command1 in this list; preserve the existing Item inclusion test and deduplicate any append. Soldier/Gladiator axe lessons extend existing commands and add no command IDs. A same-race append contributes at most two bytes, not all ten new racial implementations.

All five consumers also use the same menu command-ID array at menu base`+1134`: stores at`7CA14`, `7CBA4`, `7D420`, `7D56E`, and`7DA6A`. This follow-up closes **the requested caller stack-buffer concern**. It does not independently prove the outer menu allocation or all subsequent20-byte row renderers for arbitrary255-entry lists. Keep the proposed append bounded to the generated same-race jobs and exercise the maximum15-command fixture in the real UI; no stack-frame patch or caller-specific restriction is necessary for that bounded expansion.

Additional native disassembly for this audit is saved as `build/expansion/probes/command-discovery-capacity-disassembly.txt`. No engine changes or emulator test claims were made by this follow-up.
