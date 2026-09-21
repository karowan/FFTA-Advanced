# Council review: explicit command membership and predicates

2026-09-14. Reviewed `src/engine/command-lists.c` against the native instructions documented in `notes/noncontiguous-command-consumers.md`. Frozen command-core SHA-1 `62ffec1983af32c075a55f5cf80eb429e6cf7c0f`; baseline command-data SHA-1 `98bd2f5cbe731cac9cb7cd325e9fbdb562ebfb2d`; engine SHA-1 `e5a0eff270a642415f51b1da4a91d48a09b87699`.

## Result

**13,306 checks pass** in `scripts/test-command-predicates.py`. No semantic regression was reproduced in the four replacements within the tested contracts. The script verifies matching ROM, baseline and engine hashes and freezes the current command-core/manifest/symbols in `build/expansion/probes/command-predicate-council/<hash>/`. No engine files or user play files were changed by this reviewer.

The native four-predicate bodies, CCE60 range resolution, installed AP accessors and replacement code all execute. Battle-manager restriction, C8298 status rejection and CCD50 selectors13/15 are controlled callbacks with shared behavior in baseline and replacement. This isolates predicate semantics; it does not certify those external providers' gameplay behavior or full battle menus.

## Semantic comparison

| Replacement | Required native behavior | Review outcome |
| --- | --- | --- |
| `ffta_battle_command`, entry25FDC | Only selections6/7 are primary/secondary. Ordinary branch accepts usable type1/4 actions. Restricted branch additionally requires action selector15. Native Item behavior remains in fallback. | Matches. Every added lesson is tested with independently varied type/AP/restriction flags and selector denial. |
| `ffta_special_action`, entry26AB8 | Scan nonzero command slots1..3; retain type1/4, availability and selector13. Item is included through race-zero records. | Matches. No new Item exclusion or mastery-only check was introduced. |
| `ffta_action_command`, entry133D78 | Return the first command byte containing an action with matching actionID and type1/4, without an AP requirement; skip commandbyte0. | Matches. Added-only records are found even with AP0 or partial AP. Original primary-before-secondary-before-Item ordering is retained. |
| `ffta_action21`, entry1341EC | C8298 early rejection; skip zero commands and Item; require type1/4, availability and exact actionID21hex. | Matches. Tests include blocked status, partial AP, equipment availability, other action IDs and Item slots. |

**Commandbyte0 is deliberately handled differently by the first predicate.** Native25FDC does not skip a zero command before scanning its resolved job range. The other three functions do skip it. Consequently `ffta_command_custom_job` must not globally reject commandbyte0: the caller decides whether to scan that slot. The current implementation preserves this distinction. Differential cases explicitly cover `(primary,secondary)` bytes `(0,0)`, `(0,2)`, `(1,2)`, `(2,1)`, `(2,0)`, `(2,2)` for both custom jobs, including all action IDs0..255 for reverse lookup.

Selections other than6/7 and contexts without a custom Soldier/Gladiator slot delegate to the original predicate. This review does not invent a new meaningful result for invalid battle-menu selections where the native routine has no established initialized-range contract.

## Job resolution and aliases

Primary resolution starts with unit+5 and uses unit+7 only as the fallback for record aliasFF. Secondary resolution uses unit+8 as both initial job and fallback, consistent with native C8570 range selectors. A zero record alias selects the current job; a fixed nonzero alias follows that record. Item commandbyte1 forces the native Item job/race-zero bank. Only resolved Human Soldier2 and Bangaa Gladiator16 activate explicit membership; a shared command number alone never identifies Soldier.

The original job table has four nonzero aliases: job80 (Human),81 (Viera),82 (Moogle),85 (Viera), allFF. The original-job differential matrix includes these playable aliases with valid fallback jobs, including job80→Soldier. It covers60 original playable-race job records under four AP patterns. Invalid alias cycles and out-of-table aliases are bounded by the new helper, but are not passed into original native fallback predicates in tests because the native getter can itself loop or read outside its table on malformed data.

`range()` retains native CCE60 for the record bank and original ranges. Only the two recognized custom jobs replace membership with the explicit list. Record pointers remain `bank + actualLessonID*8`; row ordinal is never used as an AP index. Both current custom lists are strictly increasing, which is required by the successor's `lesson > current` rule. A future reordered/nonmonotonic explicit list would need a different successor contract or a generation-time ordering rejection.

## Reentrancy and ABI

Membership helpers are stateless. `Range`, slot and loop positions are local to each invocation; there is no mutable static iterator, fake global range or globally remembered selected command. Interleaved Soldier/Gladiator successor calls still return exactly17 real lessons in each slot, including11→172 and43→105, followed by marked termination1FFFF. Item returns zero, meaning native iteration.

This supports nested26D44→26AB8 structurally: the inner scan cannot replace an outer cursor. The test interleaves actual helper invocations but does not execute the complete nested native action-list constructor. Parent's large-list integration must still run that actual nested path.

All four entry points are differentially tested at both Thumb SP residues using custom and fallback jobs. Native SP and r4–r11 preservation are enforced by the shared harness. Every observed replacement C boundary is aligned to eight bytes.

## Test coverage and limits

- 2,880 original-job predicate comparisons with no added AP.
- 3,120 inactive/Item/secondary command comparisons.
- 2,880 added-only type/AP/status cases, covering each of the twelve appended lessons in either command slot.
- 4,320 selector allow/deny and exact-action21 checks.
- 73 successor membership/interleaving checks.
- 33 ABI/fallback/alignment checks.

No additional engine correction is requested from this bounded review. Continue separately with the large party/battle list initialization and backedge shims, output capacities, MP/law/status handling inside those builders, real nested special scans, and native AI output deduplication. Passing these predicates does not enable all ten new jobs or prove complete battle execution.
