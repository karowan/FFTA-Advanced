# Relocated table domain council review

The audit found a second omitted native tail: **global action346 is Blank Card**. The original action table has347 records, not the346 exposed by the randomizer's partial data map. Relocating only346 and assigning the first custom action346 loses this original ability.

## Confirmed action defect and migration

Native action base is `0855187C`, stride28. Record346 is at `08553E54` and contains:

```
1e02006400000000024000008f010101400214005501900110022800
```

Its Other-name ID is542, decoded as **Blank Card**. The next address after all347 records is `08553E70`, the native descriptor table. Independently, native action-help bank23 covers help IDs1209..1555 inclusive, exactly347 entries. These structural bounds and the nonzero named record override the vendor's incomplete count `0x15A`.

The systematic correction reserves native0..346 and moves all85 custom action IDs to347..431. Chop moves423→424. Race-specific AP indexes, item IDs, lesson names, job IDs and support/reaction/combo ID spaces do not change. Old complete emulator savestates must remain paired with their frozen ROM; do not resume an old program-counter snapshot against a newly compiled image merely because AP indexes are stable.

Changed by this council, without running a shared build:

- `scripts/generate-expansion-registry.mjs`: derives347 from the native table boundary, verifies the final Blank Card name, starts new Action IDs there, publishes the action domain in the registry.
- `scripts/build-action-data-probe.mjs`: preserves347, allocates432 total, and rejects a stale registry whose85 new actions are not exactly347..431.
- `scripts/test-action-data.py`: tests all347 original records and432 total; explicitly asserts the native Blank Card bytes and boundary. All seventeen native literal users are still covered.
- `scripts/test-command-iteration.py`: disposable synthetic actions now start347 and retain native Blank Card.
- `scripts/test-chop-eligibility.py`: uses the combat manifest's Chop ID and compares all347 original callbacks.
- `scripts/test-relocated-table-domains.py`: new domain/prefix/native-consumer regression test.

The parent rebuilt the full migration and uses generated `registry.h` / `ability-ids.inc` identifiers in combat C/assembly. Fresh verification passed:

- Action-data `699778367047883a26d9fc633e4b6e516d7fab10`: **45,127 assertions**, **68,198 native getter executions**; all347 native rows including Blank Card346, all85 inert additions, all432 rows through seventeen literal consumers.
- Relocated-domain test: **14,530 checks**, zero failures. Stage hashes: job-data `ffacb3df886d7776190b47d10d8b2ecb93c74f25`; content-data `276c6b36ef3226d1310665f47cb3de9b0e55b338`; command-data `2435b6ec441d77f268378b8463046fb0eca2976f`; action-data as above.
- Chop424 eligibility: **21,883 checks** on combat `9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc`, engine `58c534a82d297fdebcf2db8c156b0000b167045c`. Includes all347 original callback IDs and explicit native moved-origin geometry.

The initial failing action346 domain test is closed by these rebuilt artifacts. This acceptance remains bounded to data/getters/eligibility/geometry; committed combat and rendered gameplay are separately tested by the parent and engine council.

Hardcoded references were identified in `src/engine/combat.c`, `combat-hooks.s`, `scripts/build-combat-probe.mjs`, `test-chop-native.py`, `test-physical-final.py`, `probe-chop-preview.py`, `probe-chop-preview-variants.py`, and `probe-chop-animation-variants.py`. The parent migrated live engine/build/test sources to generated/dynamic Chop424 identifiers; historical frozen423 debug probes stay paired with their old ROMs and are not migration acceptance tests. Prior reports claiming the346-row relocation preserved every original action are superseded by this finding. Generated registry/header/content/action/combat artifacts were rebuilt together.

## Other relocated domains

| Table | Original domain | Evidence and result |
| --- | --- | --- |
| Job records | 0..115;116×52 bytes | Includes monster/story/alias jobs. Native job icons clamp116+; subsequent bytes are another structure. Every original record and all48 native getter selectors were compared, with a valid fallback job2 for special aliases. |
| Item/job-name pointers | 0..752;753×4 | Ends exactly at command descriptor base527244. All pointers retained. |
| Command descriptors | 0..73;74×4 | Ends exactly at support metadata52736C. All native job+10 command values fit. Original rows preserved; expansion reserves holes74..115 and uses116..125. |
| Equipment | 0..375;376×32 | Includes biased index0 and every375 ordinary items. Ends at teaching base520080. All records preserved. |
| Teaching sets | 0..224;225×20 | All376 item records reference this range, with maximum224. Original rows are unchanged. Rows214..221 use native job255 wildcard; these are not invalid references to job255. |
| Equipment permission masks | 0..34;35×4 | Ends exactly at equipment base51D180; all116 original jobs have maximum mask34. Full mask prefix preserved before new masks. |
| Job prerequisites | 0..19;20×4 referenced domain | Maximum across all116 original job records is19. Getter uses the job's prerequisite index. Full referenced prefix preserved before appended requirements. This is a referenced-domain result, not a claim about unreferenced padding. |
| Other-name pointers | 0..766;767×4 | Tail pointers remain valid ROM text pointers; the following two words are zero before unrelated data. All original action/command name IDs fit. Prefix preserved against the approved foundation, including its intentional four pub-name pointer changes at IDs41..44. |
| Racial ability pointer table | 0..23;24×4 | First bank begins immediately after24 pointers at51BAE4. Parent fixed the truncated table. This test checks allocation capacity; the inventory council owns all24 native getter/preview tests. |
| Help range table | Eleven scanned slots | Native19A50 scans indices0..10. First ten actual ranges remain identical; original slot10 is zero padding. The extension occupies this spare slot. It does not remove an original help range. |
| Help bank13 | Original33 entries | Existing range478..510 remains earlier in the scan. Every original text entry is decoded natively before/after conversion from relative-u16 entries to pointers; every valid original help ID retains its native bank/index. |
| Global actions | **0..346;347×28** | **Defect found; migration source prepared.** Exact next-table boundary553E70 and native Blank Card346 establish the full domain. |

The initial domain test verified all original table prefixes except the lost Blank Card row, all original job/equipment/command/action name and index references, and expanded indexes against allocation capacities. Native checks include5,568 job-selector comparisons, all1,616 distinct original help mappings, and33 original bank13 decodes. The new test records the exact hash of every stage it reads and refuses stale ROM/manifest pairs.

## Scope and remaining risks

This audit covers tables actually relocated by job-data, content-data, command-data and action-data. It does not claim all possible arbitrary invalid byte/halfword indexes are safe; native getters often have no general bounds check. Special actor/job/race namespaces must be tested with actual original records and caller contracts rather than inferred from playable menus.

Original support/reaction/combo dispatch metadata has not been relocated or extended in this slice. Allocated custom IDs128+ are not evidence that their effect tables or masks are implemented. Those features still need their own native dispatch work and full-domain audit before enabling them.

The failed preview demonstrates why prefix counts must come from native bounds/records, including enemies and story content. A vendor tool's exposed subset and a passing playable-race fixture are insufficient substitutes.
