# Party command iteration review

Verified against command-core `37243bba6f38ba298e436d516d7b266fd837c3b9`, command-data native-loop baseline `69479affaf3fc04f3b3dc40780557297dd266ccc`, engine `3745b4400cc71e1c871b6cbf048a241e895819a0`.

Run `scripts/test-party-command-lists.py` with the bundled Python runtime used by the other emulator tests. It freezes the ROM, baseline, engine and symbols under `build/expansion/probes/party-command-lists/`, checks their manifest/embedded-engine coherence and verifies the six installed iterator jump destinations against the symbol snapshot. `report.json` and eight first/last-page screenshots are written there. No user ROM/save is modified and no visible emulator is launched.

## Results and scope

- 784 comparisons across 58 original noncustom job records pass against the same content with native loops. Both slots of playable jobs and primary slots of named records run both complete list builders with AP bytes 0, 1, 128 and 228. Native row bytes, real lesson IDs, count, return value and cursor agree. Header text-table pointer is excluded because relocation is intentional. This is a **loop regression comparison**, not a claim that all current content equals vanilla.
- Eight additional native Item-command bypass comparisons pass, including zero AP. Selected command 1 bypasses both the known-AP and record-type checks in the secondary edit branch. It is not an independent display-mode flag that can be combined with Soldier/Gladiator command selection.
- Forty explicit membership cases pass: Soldier and Gladiator, primary and secondary slots, learned and edit builders, each with no AP, partial AP, available-bit-only AP, all lessons and added-only lessons. Soldier ordering is `1..11,172..177`; Gladiator is `33..43,105..110`. The stack lesson-ID write sites are observed directly, avoiding an assumption that row ordinal equals lesson ID.
- Live AP used for filtering and independent preview AP used for display match their respective fixtures. The Human canonical sidecar and registered party preview tail remain unchanged. Secondary selection may change only the native preview job/command bytes. Callee-saved r4-r11 and SP return intact; 9,480 measured successor-helper entries are aligned to eight bytes.
- Actual mGBA command browsing shows all 17 lessons for both jobs via R from Pick Abilities and via explicit selection of the secondary command followed by R. All row name IDs and AP bytes match the generated records. Sixteen Down presses reach absolute row 16, scroll 12, relative row 4; the screenshots select **Haft Guard** and **Axe Reprisal**. The original source unit, AP sidecar and reserved guard `0203FF44..0203FFFF` remain intact while browsing.

**Rendered-scope limit:** both actual browse routes retain context `+1131=1`. They establish the normal command-browser UI, including the secondary edit branch, not a separately reached mode-0 primary edit UI. The complete mode-0 primary function and dynamic-slot learned function are directly executed and checked in ARM; their independent normal-menu entry has not been demonstrated here. The report uses `current-command` and `secondary-command` labels rather than claiming two different native branches from similar screenshots. Natural job prerequisite progression, gameplay AP earning and new battle effects are outside this test.

The live fixture uses the existing Marche and Bangaa Jona, preserving their identities, equipment and stats. It sets job/selected-command fields and 17 AP bytes to `0x81` before opening the native party UI. Jona's test job is Gladiator. Native party entry refreshes the unit checksum at `+FE/+FF` after those fixture edits; source preservation is checked against the valid post-entry unit.

## Exact dynamic slot and hook ABI

`7B928(r0=mode,r1=slot,r2=destination)` has two direct call sites:

| Call | Mode source | Slot source | Destination |
| --- | --- | --- | --- |
| `7C8B0` | byte at context `+1131`, literal `7C964` | byte at context `+BF9`, literal `7C968` | pointer at context `+2E1C`, literal `7C96C` |
| `7D302` | same, literal `7D37C` | same, literal `7D380` | same, literal `7D384` |

Context is `*(uint32_t *)03002818`. Its field `+1D0C` is a **pointer** to the selected live unit; it is not an inline unit. Native CCE60 at `7B980` receives that pointer and the unsigned input slot. A dynamic hook must dereference the field. The first hook revision omitted this dereference; parent corrected it before the passing runs.

`7B928` saves r4-r7/lr and r8-r10, then reserves `0x20C` local bytes. At init:

- Native `7B990..7B996`, bytes `26782d78ae4239dc`, loads first lesson into r6, last into r5, compares and exits to `7BA0C` if empty.
- r1 is the racial lesson bank; r3 is row count 0; r4 points to stack first bound `sp+200`; r5 points to last bound `sp+201`; r7 is output; r8 is output `+230`; r9 is offset `1D0C`; r10 is `03002818`.
- Native `7B998..7B99A` computes r5 = bank + lesson*8; `7B99C` moves output-row base r8 into r4; `7B99E` initializes the parallel ID cursor r2 to SP.
- The body **replaces r8 with the menu owner at `7B9A4`**. It must not later be treated as a permanent output pointer. r9/r10 retain the offset/global-pointer roles.
- `7B9BE` stores the actual lesson r6 into the stack halfword list; `7B9C0` stores the row ordinal r3 into the 20-byte row. They are different identities.
- Backedge `7B9FE..7BA08`, bytes `083501360d48684400788642`, advances record eight bytes, lesson one, loads native last bound `sp+201`, compares; `7BA0A` branches to `7B9A0`. Preserve r2 ID cursor, r3 count, r4 next row, r7 output, r8 owner, r9 offset and r10 global. A discontinuous step must update both r6 and r5; its delta can be computed from old/new lesson IDs.

The installed paired spans are `7B990..7B99C`, `7B9FE..7BA0C`, `7C338..7C344`, `7C410..7C41E`, `7C476..7C482`, and `7C53A..7C548`. All six contain the preserving jump stubs and run through the full function tests.

## Primary and secondary edit branches

`7C28C(destination,cursorOut)` saves the same eight registers and reserves `0x52C` local bytes. It uses `context+1BE4` as the inline preview unit. Known-AP filtering uses the live pointer at `context+1D0C`; display uses the preview, whose Human extension is owned by the party container tail `+7240`.

- Primary CCE60 is `7C316`, slot 1. Init `7C338..34C` loads bounds, restores global pointer into r3, computes the record and row pointer. Native `7C350..356` publishes the stack ID cursor at `sp+520`; `7C358..35A` **changes r9 from global pointer to zero row flag**. Do not carry the original r9 interpretation into its body/backedge. ID store is `7C37C`; next span is `7C410..41C`; exit is `7C6C2`.
- Secondary CCE60 is `7C466`, slot 2. Before that, `7C432` copies the selected command into preview `+36`, and C9078 at `7C43C` resolves its job, stored in preview `+8` at `7C448`. Init `7C476..48C` initializes r6, r5 record, r9 zero, r4 row cursor and r2 stack ID cursor. ID store is `7C4C2`; cursor matching compares real lesson r6 to byte `context+1C19` at `7C4B6`. Next span is `7C53A..546`, exit `7C548`.
- r10 is loaded at `7C2F8` from byte `context+1134[context+1133]`. This is the **selected command**, not an arbitrary Boolean mode. In particular, r10=1 is Item and bypasses both AP and type filtering at `7C490..4A8`.
- Native job command lookup is C8570 selector **0x0C**, explicitly called by C9078 at `C90F0..F2`. Selector0x24 / record+2D is not the command ID. Soldier command is2; Gladiator command is8.

## Native command-discovery fixture requirement

For normal units, native C8EBC follows clan job-unlock flags, not simply nonzero or mastered lesson AP: `C8FDE..C9020` selects the racial flag interval; `C903C` calls C9540 for each flag; `C9046..C9052` resolves job `flag-3` through C8570 selector0x0C and appends its command.

Consequently, merely changing Jona to Gladiator and giving its AP does not make command8 available in the native menu. The test sets only flag **19 = Gladiator16+3** in disposable RAM using the bit layout read from C9540 (`C9546` literal `C9568`). It does not change production command discovery or claim an iterator fault when the seed lacks that unlock.
