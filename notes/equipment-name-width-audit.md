# Equipment name width audit

Council content review, 2026-09-14. Tested immutable content-data image SHA-1 `182adc35b07a42a752ca8c0688138822055c1d93`. This review owns no engine changes. Parent supplied compact display labels for fifteen long names; full approved names remain in the registry and equipment help.

## Result

The eleven-tile display-name limit is sufficient for the fixed equipment columns traced here. **3,738 assertions pass** in `scripts/test-equipment-name-widths.py`; detailed results are `build/expansion/probes/equipment-name-width-tests.json`. The test loads the ROM once, verifies its manifest hash, uses mGBA's native boot IWRAM, and executes the original font-width routine `161BC`, padding instructions, and installed help decoder. It does not rebuild or touch user play files.

Every original item0–375 and added item376–460 measures at most eleven tiles. This is a font measurement, not an ASCII character-count assumption. The full approved names can remain unchanged in documentation/help; longer display names must fail this validator.

## Confirmed padding defect avoided by compact labels

The inventory council identified shop row renderer `6E6xx`: name width plus two icon tiles is subtracted from thirteen. A negative result becomes a large unsigned clear count.

There is a second instance in the monster-feeding equipment list, renderer `5C220`. It uses the shared state pointer `0200F428`, menu at context+D20 and selected item records at context+2CA4. It renders the name at row graphics+80, measures it at `5C2C2`, then computes:

```
clear_start = row_graphics + (name_tiles + 2) * 64
clear_count = u16(2 * (14 - (name_tiles + 2)))
```

Native `13A88` clears `clear_count * 32` bytes. A thirteen-tile name produces count65534, requesting a very large write. The negative-control test executes the original instructions `5C2C6` through entry `13A88` and reproduces this exact count. It stops before the dangerous clear. For all461 current item IDs, execution instead yields the correct nonnegative count and the same endpoint `row_graphics+380`. This renderer permits twelve name tiles; the stricter eleven-tile display policy resolves both defects without an additional hook.

## Other consumers

| Consumer | Native contract inspected | Current result |
| --- | --- | --- |
| Shared equipment row used by inventory/battle lists, around `2B1D6`/`2B202` | Clears26 graphics tiles =832 bytes; icon consumes128; eleven name tiles consume704. The clear count is fixed, not a subtraction from name width. | Eleven tiles fit exactly after the icon. |
| Party equipment details `8E3C6`–`8E482` | Centers using signed `(12-name_tiles)>>1`; draws a fixed twelve-tile name span; icon/text x offsets are+8/+10. | All coordinates are nonnegative and name width fits. |
| Party equipment info `8C6E0`–`8C704` | Resolves record name and renders directly with `15110`; no name-dependent unsigned padding operation in this path. | Display width stays within the original equipment-name maximum. |
| Shop details `6AF56` / `6CFD2` | Centers icon/name using `(13-(name_tiles+2))>>1`, then adds9. | No negative coordinate for current labels. Inventory council owns shop integration. |
| Reward/item popup `39ED0` / `39FF0` | Twenty-tile centered message consists of a measured fixed prefix, two icon tiles, and item name plus fixed suffix. | Native prefix measures5; every original/new composed label measures at most19 total. |
| Battle command/list builders `26306`–`271C4` | Width measurements raise a maximum-width field; they do not compute a clear count. Several of these measure commands or abilities, rather than item names. | Added equipment remains within the original name-width domain. Command-name expansion is separate. |
| Message layouts `3DCBA`, `3DEF0`, `4A31A` | Explicit oversized-message branches at24/25 tiles render components in alternate layouts. | No additional name-width clear underflow found in the inspected branch logic. |

The static pass enumerated all24 direct calls to `161BC`,46 direct calls to `13A88`, and74 original name-table literals in native code below ROM150000. Dumps are `name-width-consumers.txt`, `name-layout-details.txt`, `name-help-details.txt`, and `equipment-name-pointer-consumers.txt` under the probes directory. Literal words can disassemble as instructions; conclusions above use actual PC-relative load sites and traced blocks, not arbitrary decoded data. These inventories assist future review; enumeration is not proof of every indirect renderer, animation, trade flow or gameplay state.

## Equipment help storage and layout

Native main help setup at `11B80` passes output=context+30E and scratch=context+50C, a **510-byte output interval**. `13E9C` removes the two-byte entry header and writes the remaining body including its terminator. Therefore the existing builder condition `encoded.length <= 512` already implies `decoded.length <= 510`; a bound expressed directly in decoded bytes may be clearer, but the old expression is not an off-by-two bug.

All85 new entries were decoded through the installed native routine with the actual510-byte output/scratch spacing. Tests verify exact output, a guard before the destination, every unused destination-tail byte, scratch, and an outer guard. Maximum decoded body is **121 bytes**, with no unexpected scratch writes. Thus current bodies are also shorter than the128-byte output interval of short-popup decoder call `186C2`; this does not establish that every new help ID should be routed through that popup.

Generated help has at most **three wrapped lines**, each at most **23 native tiles**. Storage and per-line width pass. This function-level review does **not** establish that the help UI displays or scrolls to the final third line. An actual help-window interaction is still required for readability/paging acceptance.

## Separate integration lead

Reward popup `39EEE` compares the item ID against375 and uses quest records for larger IDs. Its equipment and quest branches also choose different name indices. Compact labels do not repair that namespace distinction. This was sent to the inventory council: check whether this popup can receive newly granted equipment, and if so add a context-preserving item-kind path rather than changing the shared quest namespace globally. This is an identified native branch requiring reachability review, not a demonstrated player-facing reward failure in this audit.

## Scope boundary

No remaining name-width memory-write defect was reproduced for the current labels in the traced fixed columns. That conclusion is narrower than an end-to-end UI certification. Actual third-line help access, reward namespace routing, trade/monster-feed gameplay, battle execution and other context-specific icons remain separate integration checks. The existing icon, quest UI, inventory, acquisition and battle tests should continue to run alongside this validator.
