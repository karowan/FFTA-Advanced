# Council review: native battle and AI command iteration

2026-09-14. Scope: ordinary battle builder `26D44`, restricted builder `26F9C`, special/second-action list `27918`, and AI action builder `133F70`. Reviewer owns `scripts/test-command-iteration.py`; no engine edits were made.

## Result and reproduced fix

The first compiled implementation (`a5144ff7a117eb8660c92c164c19a56a1d6f3293`) reproduced a real regression: Soldier with only original lessons learned yielded IDs1–11 in `27918`, while native yielded only action lessons1–8. Reaction/support records had leaked into the list. The second-list backedge resumed at `27A04`, inside the bytes replaced by its initialization hook (`279FA` through `27A09`). The parent corrected both continuation branches to reconstruct the record pointer and resume at `27A0A`. The regression is covered by original/native differential tests, every appended lesson's record type, and a compiled continuation-literal check against every installed hook span.

The corrected implementation passes **11,918 checks** on command-core SHA-1 `37243bba6f38ba298e436d516d7b266fd837c3b9`, baseline `69479affaf3fc04f3b3dc40780557297dd266ccc`, engine `3745b4400cc71e1c871b6cbf048a241e895819a0`. The exact current hash and check count are recorded in `build/expansion/probes/command-iteration-tests.json`, with the tested ROM, baseline ROM, manifest, symbols and result frozen beneath `command-iteration-council/<ROM SHA-1>/`. The script validates matching ROM/base/engine hashes before freezing; a stale engine fails immediately.

## What executes in the tests

The four native builder bodies execute, including CCE60 bank/range resolution, installed AP accessors, original record-type filters, actual lesson/action output writes, MP/status branches, native action name/font measurement, native AI legality `133E18`, and duplicate filter `133F48`. Ordinary `26D44` really calls installed `26AB8` for action21; the inner scan cannot disturb the outer explicit iterator. Both native stack residues are exercised, with SP and r4–r11 preservation and eight-byte alignment at the replacement C boundaries asserted.

Production definitions for the added action IDs are not yet installed. Each test machine therefore relocates the original action table into a disposable ROM-mapped region and appends copies of original action76 with controlled MP/category fields. It redirects table literals in that emulator instance only. This is important: appending in place at the original table would overwrite the adjacent native names/data. Nothing is written to the ROM files or user play saves.

External status, restriction, MP adjustment and selected CCD50 properties are controlled callbacks shared by original and patched machines. These fixtures test how the native builders consume those properties; they do not certify final action effects, full battle rendering, or those providers' independent gameplay behavior.

## Required semantics

- Output IDs remain actual racial lesson indices for all three battle lists. AI emits actual action IDs, not lesson indices or iterator positions.
- Soldier membership is1–11 plus172–177; Gladiator membership is33–43 plus105–110. Only type1/4 records enter action lists. Current design has12 action records in each17-lesson list.
- Every added lesson is independently tested in either slot with types0–4 and AP0,37,80hex,E4hex. Unlearned/partial AP without equipment availability stays absent; learned/equipment availability follows the installed accessor.
- Ordinary lists retain unusable actions but clear flags for MP/silence. Restricted lists additionally omit selector15-denied actions. Special lists omit selector13-denied actions. Silence-exempt selector14 actions remain usable when MP permits.
- AI retains its status rejection, signed category filter, MP legality and action-ID deduplication. Its output order remains primary, secondary, Item; special lists intentionally do not deduplicate two identical command slots.
- Descriptor matching requires the current unit's command byte, native bank pointer, first and last range endpoints. Deliberate mismatches in each field return to native iteration. A shared command number alone cannot substitute another job's list.
- Primary special alias80 uses a valid fallback Soldier job; Item and empty command slots receive separate native differential cases.

## Native output capacities

| Consumer | Original allocation | Current requirement / evidence |
| --- | --- | --- |
| Ordinary/restricted menus | `27DA0` copies descriptor `08391454`; command6/7/8 maps index3, capacity22. It allocates capacity times4 bytes for lesson IDs and capacity bytes for flags. | Current12 actions fit. A disposable fixture converting all17 lessons into actions also fits. Guard checks include untouched output tails. |
| Special second-action list | Command15 maps descriptor index10, capacity85. | Two synthetic17-action slots produce34 rows without deduplication and fit. Current two12-action slots plus at most15 native Item lessons remain below85. |
| AI manager list | Caller `C2170` passes manager+8 to `134094`; count is manager+58, giving80 bytes/40 halfwords. | Do not treat this as an unbounded output buffer. |
| AI temporary list | `C3866` requests80 bytes through `22840`; `C3870`, `C387C`, `C3888` append category3/2/1 outputs. | Also40 actions total. Both callers use disjoint action categories, so grouped filtering does not triple the count. |

The current native Item bank has15 entries, but only two have nonzero AI action categories. Native Blue Mage is the largest relevant original command with20 actions. Thus an intentionally exaggerated all17-action Soldier plus all20 Blue Magic actions plus both AI Items reaches39, fitting both40-entry buffers. With the approved Soldier action/support types, the same permissive fixture emits33. The test executes both `133F70` and grouped `134094` against the40-entry guard. No allocation expansion is required for the current Soldier/Gladiator addition. Future jobs or changes to Item AI category eligibility must be rechecked against40; the allocator will not protect these writes automatically.

## Remaining scope

These tests close explicit membership, native filtering, nested scans, ABI and bounded output for the four specified builders. They do not establish final new action effects, usable new jobs, final AI utility/scoring, in-game battle UI screenshots, or complete end-to-end playability. Party command loops are reviewed separately by the parent. A nonmonotonic future lesson list would violate the current successor's increasing-ID contract and needs a generator rejection or a different iterator.
