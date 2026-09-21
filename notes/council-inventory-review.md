# Inventory council review - 2026-09-14

## Latest follow-up: native battle list capacity and navigation

The guarded descriptor changes at ROM0x3914F8 and0x39150C are sufficient for allocation and the native count/index consumers exercised here. `scripts/test-battle-inventory.py` now passes in ordinary acceptance mode against the installed446-capacity probe (SHA1 `a3a98d4ebaef8fa25d521992ce7c9f6fce959528`). Its repeatable results are saved to `build/expansion/probes/battle-inventory.json`. This supersedes the earlier unpatched-capacity status below. No engine or builder implementation was changed by this reviewer.

The test owns one count for every ID1..460 and assigns a synthetic copy of native item1 to every equipment definition. This intentionally reaches the conservative446-entry equipment maximum; it is not a test of the final85 item definitions. Item460 is equipped so the last usability entry is disabled. The native IWRAM helper code is copied from an isolated clean-ROM boot. Allocation, clearing, graphics preparation, class compatibility, equipment checks and freeing all execute real native code; none of those routines is substituted.

Passed checks:

- Native0x27DA0 chooses the proper Throw/Draw descriptor, allocates1784 ID bytes,446 usability bytes,192 temporary bytes and504 bitmap bytes, then invokes native0x27750/0x27800. Both return u16 count446 and the exact446-ID order. Allocation sizes and pointers are observed at native0x05B28/0x05B36.
- Every list write at0x277AC/0x278AE and0x277C0/0x278D4 stays inside the requested native allocation. All existing heap-block headers survive the builders; external heap and compatibility-view guards survive. Native0x2800C frees the four allocations and restores the original coalesced heap header.
- The252-capacity negative controls stop at the first real out-of-bounds ID store for both builders. In this all-sword fixture the first overflowing item is253 at index252. The earlier337-weapon fixture's first overflow was376; both represent the same capacity defect.
- Native0x17B68 resolves local rows to full indices at tops0,250,254,255,256,300,440. Native0x25758 resolves the correct item name at every resulting index. Native0x287C4 reads the correct usability byte using the signed16 one-based context index. The selected-item store at0x28A9C..0x28ACE retains the correct u16 item ID, including460.
- Native0x17BE8 returns445, and0x17A90 correctly recognizes upper/lower scroll boundaries. Native page movement0x284A0 stores positions254→260,260→254,439→440, and bottom440/local5. The movement test stops immediately before sound/render at0x2853C; the selected-item store test likewise stops before sound at0x28AD0.

No additional byte truncation was found in those consumers. Their byte values represent the six local visible rows; global counts/positions use16 bits. The allocator accepts these requested sizes without internal truncation. Compared with252 entries, the ID/usability request increases by970 bytes (972 after four-byte allocation rounding). The test uses a fresh96-KiB native heap; it does **not** establish sufficient headroom in an already populated battle heap, fully rendered navigation, or action execution.

### P1: a separate inline equipment-classification cutoff rejects expanded weapons

The stress test found a distinct integration defect, reported immediately to the parent and the equipment reviewer. Native `0xCABA8`, shared by `0xCB48C` through `0xCAE2C`, inlines `u16(item-1)<=251` at0xCAD04..0xCAD12 instead of calling the patched0xCB1F4 predicate. New weapon IDs therefore follow the native nonweapon branch at0xCAD3A.

Concrete reproduction: active Human job2, item460 in gear slot0, and all equipment definitions cloned from item1. Native0xCB48C returns0 for item1 into slot1, but1 for the otherwise identical item376. Draw Weapon correctly lists446 IDs, then disables all synthetic weapons above252 through that predicate. This is a legality failure, not list-index truncation. `expandedWeaponLegality` in the battle report records those two return values; the separate equipment-legality test owns the acceptance contract for the parent's classification fix.

Recommendation: replace only the inline weapon-classification block with the expansion-aware predicate while preserving its native continuation and register contract, then require original375-item legality equivalence plus expanded clones across relevant equipment/support combinations. Do not bypass the remainder of native equipment restrictions.

## Current follow-up: inventory menus and transaction hooks

Reviewed the later `src/engine/inventory-menus.c`, `inventory-hooks.s`, ownership-view refresh and equipment-event changes in `inventory.c`, and the current hook manifest in `scripts/build-storage-probe.mjs`. Implementation files were not changed. This section supersedes integration-status statements in the earlier review below.

**One confirmed remaining capacity defect: native Throw/Draw Weapon allocations remain at252 entries.** The new party/shop list implementations and native stock behavior passed the additional bounded checks described below. This is not approval of completed battle integration.

### P1: expand native battle weapon list allocation before allowing more than252 owned weapon types

The native battle-menu descriptors at ROM0x3914F4 and0x391508 have a u16 capacity252 at offset+4, respectively ROM0x3914F8 and0x39150C. The current probe builder does not change them.

At0x27DA0, native code selects/copies the descriptor into the current menu geometry. It then allocates:

- `capacity*4` bytes for IDs at0x27DD4-0x27DE0, storing the pointer at menu+0x94;
- `capacity` bytes for usability at0x27DEE-0x27DF8, storing the pointer at menu+0x98.

The surviving Throw builder0x27750 and Draw Weapon builder0x27800 subsequently enumerate the expanded inventory. They do not cap their output to that allocation. Thus owning more than252 qualifying weapons can write beyond the native allocation even though the party and shop buffers are now larger.

Reproduction in isolated ARM execution: provided the native Throw routine with all252 original weapons plus85 synthetic appended weapon records, the actual patched CB210 reader and weapon predicate, and descriptor-sized output buffers. Substituted only its unrelated temporary graphics allocation/copy helpers. It produced337 entries and wrote item376 at `IDs+252*4`, the first word outside the1008-byte native ID allocation. This establishes the output overrun; it is not a full battle UI run.

Recommendation: raise the two descriptor capacities to a supported conservative bound (446 equipment slots, or a proven weapon maximum). This retains the native allocation/free path instead of adopting fixed vendor buffers. Then exercise Throw/Draw selection, scrolling and cancellation beyond entry255, with buffer guards. Do not replace the native Item restrictions merely to fix this capacity.

### Native shop stock fidelity: passed

Executed the compiled `ffta_shop_buy_list` against native0x080CBDC0 in separate ARM instances with equivalent full original inventories. Compared count, order, IDs, owned bytes and equipped bytes, and checked stack plus r4-r11 preservation.

- All6 tabs;
- tier keys0,10,20 (all three native tiers);
- special shop keys2..6;
- owned-territory counts0,7,30, set through native territory flags.

All270 combinations matched byte-for-byte. This includes native appended special stock. The current inclusive `i<=limit` loop agrees with native0xCBF14-0xCBF1E, and CC9F0 intentionally returns no item for index0.

Also compared compiled sell-list output against native0xCC7F8 with every original item owned. All6 tabs matched exactly, with counts23 helmets,51 armor,252 weapons,12 shields,23 others and14 consumables. This checks the C item-type tab mapping for every original item, not just ordinary merchandise.

These tests used the original item table. Repointing all required item-table consumers and integrating the85 gated items remain separate work.

### Transaction hooks and unaligned hook skips: passed bounded execution

The manifest uses a two-byte NOP followed by an aligned eight-byte jump for the unaligned sites0x6C942,0x5B872 and0x61DFE. Each twelve-byte patch fully covers the original instructions intended to be replaced; it does not leave execution entering the embedded destination word.

- Sell continues at0x6C94E after the complete original subtraction block.
- Feeding continues at0x5B87E after the complete original subtraction block.
- Equipment reward capacity continues at0x61E68, the enclosing native function epilogue, leaving quest/unit arms intact.

Executed the installed sell and feed entry patches, not only their standalone C functions, with quantities0,1,3,99 and an owned count7. Both correctly saturate persistent ownership, restore original SP/LR, and leave r4 pointing at the selected record. Unrelated persistent bytes were unchanged. These executions stopped at the intended native continuation; they do not replace an actual monster-feeding UI test.

No further direct writer beyond the already intercepted sell, feeding and CAB24 paths was found in the previously enumerated20 CB210 callsites. The ordinary purchase still commits through CA900. `refresh_owned` now updates matching materialized view entries after native grant/remove, addressing the prior owned-byte cache concern. `ffta_native_equipment_event` mirrors native increment/decrement behavior; native CAF78 calls those events before the final equipment-slot store at0xCB0BC, so incrementally updating the existing mirror is appropriate for that path.

### Party/shop output capacity: passed function-level guard checks

Used a synthetic valid table assigning all460 records to the weapon tab, and owned one of every ID. The compiled party-list function returned460, wrote through0x0203261F, and left its following guard and the entire compatibility view at0x02033000 unchanged. The sell-list function likewise returned460, wrote through0x0203072F, and preserved its guards. These are conservative maxima; actual categories have fewer entries.

The party header plus460 twenty-byte records requires0x2620 bytes at0x02030000, below the separate view at0x02033000. This verifies the C list builders' bounds in those fixtures; generic UI navigation/count handling and other runtime allocation overlap still need their appropriate high-count game tests.

### Remaining acceptance boundaries

- The recorded native buy/sell/equip/save test covers an original Bronze Helm and preserves816 extra AP bytes. It is useful integration evidence, but not an expanded-item or battle test.
- Monster feeding now has the required transaction hook, but actual feeding remains untested in the reported game flow.
- The battle capacity defect above must be corrected and tested before expanded weapon ownership is safe in those commands.
- The old sorting input is disabled; its on-screen hint still needs adjustment, and manual inventory ordering is still a deliberate behavior difference.
- Ordinary Item restrictions are retained. Their battle behavior, Throw, Draw Weapon, and later AP/roster lifecycle integration must still receive native tests.
- The load shims were moved before native live-state commit: normal hook0x13AA48 migrates staging then continues at0x13AA50, and suspend hook0x13AAD8 continues at0x13AAE0. This supersedes the older hook-position discussion below and avoids committing rejected legacy input to live state.

## Earlier review snapshot

Scope: read-only review of `src/engine/persistent.c`, `inventory.c`, `load-hooks.s`, and their native inventory callers. This report is the only file written by this reviewer. The inventory UI port is not installed yet; findings below are integration requirements, not claims about a released build.

## Result

The compiled compatibility view has correct indexing and slice semantics in the bounded checks performed. The weapon predicate exactly matches native behavior for every original item ID 0 through 375. One additional direct inventory writer beyond the known sell/CAB24 paths is confirmed: monster feeding at ROM 0x5B872-0x5B87C. Redirecting CB210 alone would cause feeding to reduce a temporary view while persistent inventory remains unchanged.

The previously identified non-CB210 readers, menu capacities, and lifecycle hooks still need the planned integration. This review does not approve the whole inventory port as complete.

## Executed checks

Used the existing compiled `build/expansion/engine.bin` and symbols in isolated Unicorn ARM7 instances, with the clean ROM for native functions. No emulator save or implementation file was modified.

- Executed native 0x080CB1F4 and `ffta_native_is_weapon` for all IDs 0..375. Zero differing results. The C type check includes the original Souls and weapons and excludes original equipment/consumables that native excludes.
- Constructed counts for all IDs 1..460, three equipped slots, and an active roster record. Executed `ffta_native_inventory`.
- Verified the exact equipment order: IDs 1..361 followed by 376..460, then consumables 362..375.
- Verified all 460 records have unique IDs, correct owned bytes, and correct equipped bytes.
- Equipment return is 0x02033000 with count 446. Consumable return is 0x020336F8 with count 14.
- Verified the 60-byte guard immediately following the 1840-byte view was unchanged. The used range is 0x02033000..0x0203372F.

These are function-level checks. They do not establish that other runtime allocations never overlap that view or that every native menu rebuilds its cached data after mutations.

## Confirmed writer requiring interception

### Monster feeding

The caller obtains the inventory slice at 0x5B84A and keeps its pointer in r6. It resolves the owned item's native slot with CC86C at 0x5B860, puts that index in r4, and obtains selected quantity through 0x802AB5C at 0x5B86E. It then executes:

```text
0x5B872: index = u16(r4) * 4
0x5B876: r4 = r6 + index
0x5B878: r1 = byte[r4 + 2]
0x5B87A: r1 -= r0
0x5B87C: byte[r4 + 2] = r1
0x5B87E: continuation
```

This must reduce the persistent owned count through the scalar inventory API. A hook can use the selected record's ID and the requested quantity rather than changing only the mirror. Preserve r5/r10 and continuation behavior. A native UI feeding test must prove both the gameplay action and a count reduction that survives save/cold-load.

The vendor hook at 0x5B860 is an alternative insertion point, but its unchecked subtract should not be copied unchanged. Starting at the actual write block can retain the now-compatible native index lookup.

### Known writers reviewed

- Sell: 0x6C926 obtains CB210 view, 0x6C932 finds index, 0x6C942-0x6C94C subtracts quantity into record +2. Continue at 0x6C94E after committing the persistent count.
- Equipped-count update: CAB24 writes legacy +3 bytes using its own hardcoded old inventory scans. It must remain disabled/replaced when counts are derived from roster.
- Buy: 0x6A8CC's CB210 return is discarded. The actual inventory grant goes through CA900 at 0x6A8E6; the later direct store at 0x6A8FE updates gil, not the inventory view. No additional inventory writer hook is required there.

## Surviving CB210 readers

The direct-call scan over the clean native code region found 20 BL callsites. The following grouping distinguishes inventory writes from output-list writes:

| Callsites | Treatment |
|---|---|
| 25A5C | Draw Weapon quantity display: reads returned inventory records. Native item-ID list semantics must remain consistent. |
| 26A3A, 26A84 | Weapon/Throw availability scans: inventory readers. |
| 2777E, 2786E | Throw/Draw Weapon list builders: read inventory, write separate UI lists. Those UI buffers still require expanded-capacity review. |
| 58C16 | Monster-food existence check: read-only and compatible with the 14-item consumable slice. |
| 5B84A | Leads to the monster-feeding direct write above. |
| 67F42 | Builds a list of pointers to inventory records, not copies. Treat downstream UI as retaining references to the compatibility view. |
| 6A8CC | Return discarded; purchase subsequently calls CA900. |
| 6B554 | Purchase cap lookup: read-only through CC86C and record +2. |
| 6C926 | Leads to direct sale write above. |
| 6D5FC, 6D62C | Shop sell availability: read-only. Native returns true for owned equipped items too, preserving vanilla display behavior. |
| 6EC84, 6ECE6 | Shop tab builders: inventory reads; their stores populate stack/UI tab data. |
| C27B6 | Reads owned minus equipped to evaluate a candidate; no inventory record write in the inspected block. |
| CBE66, CBEE8 | Shop stock builders: inventory reads and writes to their output list. Preserve native appended-stock second pass. |
| CC818 | Shop sell list: copies qualifying four-byte records to its destination. |
| CC878 | Item-to-record-index helper: read-only. |

No additional direct write through these inspected CB210 callsite blocks was found beyond sell and monster feeding. This is a bounded direct-call/source review, not proof against all indirect calls or code outside the scanned region.

Because 67F42 persists pointers to view entries, reserve 0x02033000..0x0203372F against other scratch allocation for that UI's entire lifetime. The stable deterministic mapping is helpful: rebuilding the same view does not change an item's address. However, changing counts does not immediately update previously returned mirror bytes until another view rebuild. Native callbacks that retain these references should rebuild after count/equipment mutations, or the scalar write layer should explicitly invalidate/refresh them. This is an integration condition; a reproduced stale-menu failure was not established in this review.

## Remaining readers outside CB210

These were identified in the prior council pass and are not fixed by the compatibility view alone:

- CB2B4 free-count getter and CB320 has-item getter have their own legacy scans. The new scalar wrappers are suitable planned replacements.
- 388C8 is a separate owned-count getter using computed base 0x02000000 + 0x1940/0x1942. It supports special duplicate mission rewards.
- 61DFE-61E42 directly scans the legacy inventory for count 99 inside the typed reward capacity dispatcher at 61DD0. Preserve the quest/unit branches.
- 6807C independently scans equipment/consumables for transferable inventory, excluding equipment IDs 0x33, 0x94, 0x11E, and 0x12E.
- Party/equipment list builders have their own hardcoded legacy bases; the planned UI port remains required.

Do not replace quest namespace decisions such as the 375 threshold in script removal at 3EB0C. Equipment IDs 376..460 are valid in shop/equipment contexts, while existing mission/script encodings above375 continue to mean quest items.

## C and load-hook observations

- The compatibility-view mapping has no index gap or collision: item376 maps to index361, item460 to445, item362 to446, and item375 to459.
- The active-unit check avoids counting stale equipment on empty roster slots. Counts include all five equipment fields of each of 24 active records.
- Migration validates all old entries before clearing the overlapping region and builds counts in scratch, so its in-place conversion does not overwrite records before reading them.
- The metadata magic cannot occur in a valid old inventory at its aligned location: its first old-record ID would exceed375. The tested current-format/version behavior is therefore appropriate for valid native input.
- The reviewed hooks preserve r4-r11 through the C ABI, save/restore the temporary caller registers, and reproduce the displaced load bytes. Normal success continues at 13AA5C and suspend success at13AAEC. Failure branches go to the native error paths at13AA30/13AACA. The surrounding native bytes agree with these addresses.
- Only normal in-game load/migration has been established by the reported native test. The suspend hook still requires an actual suspend-load exercise; function structure alone does not establish its runtime path.
- The explicit state parameter supports save-preview/staging blocks without assuming live RAM. The current hooks intentionally migrate gameplay loads, not previews.
- The C sidecar helpers are not themselves lifecycle integration. Roster swaps, removal, recruitment, and loaded race/AP paths must invoke them at the correct points before the expansion is playable.

## Recommended next acceptance checks

1. Keep the compatibility view and global getter hooks; intercept monster-feed and sell writes; disable legacy equipped-count writes.
2. Exercise native Item restrictions unchanged, monster feeding, buys/sells with quantities greater than1, and retained-pointer UI refresh.
3. Preserve original special shop stock and compare all original weapon classifications (the latter already passes the isolated differential).
4. Fill expanded list categories to their maximum possible size and check buffer guards, not only sparse early-game inventory.
5. Perform native ordinary and suspend save/cold-load with expanded items and nonzero Human AP sidecars.
