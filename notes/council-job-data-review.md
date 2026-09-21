# Council review: native job-data probe

Reviewed 2026-09-14: `scripts/build-job-data-probe.mjs`, generated `build/expansion/probes/job-data.gba` / `.json`, and current `JOB-CLASS-SPECIFICATION.md`. No builder or engine implementation edits were made. Added independently executable audit `scripts/test-job-data.py` and its report `build/reports/job-data.json`.

**Result: no demonstrated defect in this bounded data probe.** The ten new job records reproduce the approved stat/growth/equipment/progression templates. Original native job/getter/category-permission behavior remains unchanged in the coverage below. This is not approval to enable the new jobs before their pending consumers are integrated.

Immutable artifacts tested:

- Probe SHA-1: `6e9a5a8f5c6ca8d9275cb30ece48cb4c82cd5157`.
- Foundation SHA-1: `2c1552fc7f63b5694ec66fe52610a221800a3f24`.
- Clean USA SHA-1: `4ac05441f4de70a4ec3dd932116346c61b8783d9`.

## Repeatable native verification

Run `python scripts/test-job-data.py` after generating the registry and job-data probe. Expected numerical values, body/head/weapon permission sets, movement/evade, and prerequisite job names are parsed from the approved Markdown independently of the builder's generated profile values. Native prerequisite IDs are resolved from original same-race job names. The registry is used for allocated name/lesson identity rather than as the source of approved numerical targets.

The test executed **183,542 native Thumb calls** in Unicorn. Every call checked normal return, balanced stack, and preservation of registers `r4..r11`.

| Coverage | Passed checks |
|---|---:|
| Original `0xC8570` results against clean and foundation | 53,760 |
| Original unit-aware `0xC92F0` results against foundation | 5,568 |
| Original category-eligibility `0xCB450`, every native item for every original job | 43,500 |
| New jobs through both bare and unit-aware getters | 960 |
| New jobs as fallback records of the four native special-job aliases | 1,880 |
| New job category predicate, categories 1–32 | 320 |
| Existing foundation Morpher behavior, nine species × 48 selectors | 432 |
| Binary preservation, allocations, pointer ledger, specification and metadata checks | 1,053 |

All **116 original records**, all 48 job selectors, and all **112 terminating fallback jobs** for each native alias `0x50/0x51/0x52/0x55` were exercised. Cyclic alias fallbacks were intentionally excluded because the original getter itself does not terminate for them. The 375-item equipment comparisons cover the category predicate, not the separate full equipment-layout validator.

The full original job record region and all 753 original item/job name pointers are byte-identical after relocation. Every allocation was checked against untouched `0xFF` bytes in the foundation, within `0x1020000..0x1100000`, with alignment, digest and overlap checks. Reconstructing the entire probe from the foundation plus listed pointer changes and allocated payloads yields the exact probe bytes; no unlisted mutation was found.

## Encoding and pointer findings

- Bases use proper paired 12-bit packing at `+1A..1C` and `+1D..1F`; the actual native getter returns the intended HP, MP, Speed, WAtk, WDef, MPow and MRes for every new profile. Growth bytes are the intended decimal targets ×10 in HP/MP/Speed/WAtk/WDef/MPow/MRes order.
- All ten jobs have status resistance `0x32`, affinity bytes `48 92 24 01`, whole-record alias zero, free learned-ability index zero, behavior flags zero, and ordinary movement nibbles `0x21`. Every graphics donor is the correct race. Retained donor fields were compared through the getter rather than inferred from profile JSON.
- Native record getter pointer `0xC8598` points to the relocated job records. All three permission literals (`0xCAC40`, `0xCB488`, `0xCB5F4`) point to the relocated masks. The native prerequisite pointer `0xC8B18` points to the relocated prerequisite records. Their original referenced data and native lookups match the clean ROM.
- New category masks match the specification, including common shoes/armlet/accessory access and Axe category 31 for Viking. New prerequisite records match the current approved pairs; both Chemists use the original zero-requirement entry. The generated new names decode correctly.
- Foundation Morpher getters retain their existing values after the table relocation. This test establishes preservation of the current foundation; it does not resolve the separate question of whether every original Morpher movement-nibble effect is desirable.

## Integration gates, not newly discovered probe defects

1. `scripts/build-job-data-probe.mjs:53` stores a new job ID as its command byte. The standalone native command path does not yet understand this contract. The manifest correctly says new selection/commands/effects are not enabled. Keep that boundary until dispatch is installed.
2. `scripts/build-job-data-probe.mjs:68` supplies first/last lesson bounds. The current allocated lists match the registry, but native AP capacity, per-race action-list lookup, and custom job lesson consumers still need integration; getter success cannot validate those consumers.
3. The masks permit the designed Dark Knight/Mystic Knight shields, but full legality still reaches hardcoded branches `0xCAD54..0xCAD86` and `0xCADC6..0xCADD2`. Preserve the existing vanilla behavior and test both slot orders when selectively extending these branches. Category-only tests must not be presented as shield/handedness validation.
4. The donor graphics fields preserve valid native identifiers; party icons, job wheel, portraits, battle animation selection, and named-character behavior need their own integrated tests. This probe did not execute those screens or a battle.

Within these boundaries, the records and their relocation are suitable to carry forward into the next integration step. The builder's `remaining` list at lines 93–95 accurately describes the principal unfinished work.
