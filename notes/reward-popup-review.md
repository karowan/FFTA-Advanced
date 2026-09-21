# Reward popup namespace review

No production hook is warranted for the approved shops-only equipment expansion. Raising the cutoff at `39EF0` would break real native quest rewards. Keep this popup's mixed namespace unchanged.

## Caller and source namespace

Native popup `39DF4(r0=u16 rewardID)` has one direct native callsite, `3A500`, and no ROM function-pointer references. Its caller takes the u16 value from `0201F46C + 2*[0201F474]`. It obtains that value by decoding four native reward bytes at context-selected record offsets `B8..BB`; each byte chooses a weighted table or the shared direct table. This is an encoded reward namespace, not an equipment-only inventory ID.

The four weighted tables start at `391BBC`, `391BD0`, `391BE8`, and `391C08`, with5,6,8,28 four-byte entries respectively. The shared21-entry u16 table is `391C78..391CA2`. Native source codes `81..95` select its rows. That table includes421 and422, which already mean native quest items. All these table bytes are unchanged in the reviewed expansion.

At `39EEE..39EF2`, IDs at most375 select equipment; larger IDs select quest records. Quest record address is `0851FAA4 + rewardID*16`. This is equivalent to a128-row table at `08521214`, local IDs0..127, ending exactly at the native job table `08521A14`. The127 valid nonzero quest entries encode global IDs376..502; their first halfwords independently confirm these IDs. The quest name branch at `39FB4..39FBE` reads the native item-name table at index `rewardID+123`.

The equipment branch uses the installed equipment record pointer at `39F60`, equipment nameID, and icon/palette calls `39F08`/`39F20`. The quest branch uses native quest-icon encoding and separate calls `39F8E`/`39FA4`. Existing generic icon wrappers retain those calls' namespace. A global icon-donor mapping here would also be wrong.

The shop buy commit `6A8C2..6A8FE` grants its u16 item through `CA900` and subtracts gil; it does not call this popup. The approved85 new items enter through the shop route. There is no supported equipment-only callsite to distinguish an overlapping rewardID such as421 inside `39DF4`.

## Repeatable native tests

`scripts/test-reward-popup.py` freezes the current combat ROM/manifest, verifies its embedded engine, and compares against the clean native ROM. It passed combat `62c848bc42e92fd7652075b235c49347c6b23862`, engine `485c65b5985c7c104ccdfef4d80fc1b61a142fee`.

- 502 native popup branch cases: equipment IDs1..375 and every quest ID376..502. Executes the real namespace decision, native icon decompression, palette lookup, name lookup, and copy arguments. Text pointers, decoded icon pixels, palettes, and VRAM results match vanilla exactly. Equipment storage, quest inventory, scratch guards, and preserved fragment registers remain intact.
- 68 native source-decoder cases: every weighted-table row and every shared direct-table row. Both ROMs execute the actual native decoder instructions and produce identical reward IDs;421 and422 remain present.
- All127 quest records and all native reward lookup bytes are unchanged. Native callsite discovery still finds only `3A500`.

Unicorn models BIOS CpuSet (`SWI0B`) for the native copy; the popup, icon decoder, palette, and source decoder code execute unchanged. These are real native rendering-branch tests, not a claim to have completed a mission or replayed the entire popup-window event through mGBA. Reports and the frozen ROM are in `build/expansion/probes/reward-popup`.

## Integration

Only add `scripts/test-reward-popup.py` to the sequential test list if desired. No assembly, compiler source, stage builder, reward cutoff, or icon allowlist change is required.

If a later design grants new gear through mission rewards, it needs an explicit equipment-kind encoding and a matching grant path, name/icon route, and quest-preservation test. Merely raising375 to460 cannot distinguish the overlapping namespaces.
