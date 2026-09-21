# Acquisition engine council audit — 2026-09-14

The completion-gated additive shop stock passes the bounded native tests below. This review changes only its test and this audit artifact. It does not claim completed campaign or battle-effect integration.

Repeatable test: `scripts/test-acquisition-gates.py`. Results: `build/expansion/probes/acquisition-gates.json`. The latest run used clean-ROM SHA1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`, integrated content/inventory probe SHA1 `a66bafe40a4a551140f31a647f962d40623a9432`, and compiled engine SHA1 `20aef5112f918826115639a01248330b4908fca0`.

## Completion flags

The public mission numbers in the design ledger are not the native record indices. Native records at ROM `0x55AE4C + index*0x46` and their names from the `0x55A64C` pointer table establish this mapping:

| Approved stage | Public mission | Native record | C9540 flag ID | Saved byte | Mask |
| --- | --- | --- | --- | --- | --- |
| S1 | #005 Twisted Flow | 7 | 0x306 | 0x02001FD0 | 0x40 |
| S2 | #011 Pale Company | 13 | 0x30C | 0x02001FD1 | 0x10 |
| S3 | #017 Desert Patrol | 19 | 0x312 | 0x02001FD2 | 0x04 |

All three records are nonrepeatable: record+0x41 bit3 is clear. Do not feed the ledger's public numbers5/11/17 directly to the native completion getter.

- Native `0xC9540` reads flag `f` from `0x02001F70 + (u16(f)>>3)`, mask `1<<(f&7)`. Native `0xC9574` updates the same bank.
- Battle completion `0xD1E70` reads the packed10-bit active-record index. Only nonzero u16 success enters `0xD1EA2..0xD1EA8` and sets `record+0x2FF`. A zero result leaves it unchanged, including after a previous success.
- Dispatch processing `0xD0F74` requires record+3 bit7 before processing. The completion bit is set at `0xD0FC0` only when `(record[5]&0xFE)==0xC8`. Record ID high bit is packed separately in record[5] bit0.
- Native pub-generation decision `0xCFD44..0xCFD6C` reads the same flag and rejects a completed nonrepeatable mission. It continues when the bit is absent, or when the mission is repeatable.

Executed three battle-result cases per target (0,1,0x100) and12 dispatch cases per target (six outcome codes, processed bit clear/set), using the actual native flag writer/getter. Executed the pub exclusion decision on the resulting state. An active record alone, unsuccessful battle result and unprocessed/failed dispatch never satisfy these completion predicates. This tests the decision blocks, not the entire acceptance or reward UI.

Ordinary native save/cold-load was also exercised in isolated mGBA: the three bits were produced by native success code, copied into the running native flag bank, saved through the game's menu, then loaded after restarting the emulator. Saved bytes `43 10 04` and all three getter results1 survived. The extra low bits in the first byte belong to the original seed and were preserved. The original seed file was unchanged. This persistence check does not simulate playing those three story missions.

## Town identity and native stock inputs

| `special_key` | Town | Native name pointer slot | Native special-stock record |
| --- | --- | --- | --- |
| 2 | Cyril | ROM0x5271BC | ROM0x528A44 |
| 3 | Sprohm | ROM0x5271C0 | ROM0x528AA4 |
| 4 | Muscadet | ROM0x5271C4 | ROM0x528B04 |
| 5 | Cadoan | ROM0x5271C8 | ROM0x528B64 |
| 6 | Baguba Port | ROM0x5271CC | ROM0x528BC4 |

Muscadet and Cadoan must not be assigned by story placement order. The native town-name strings were independently decoded using `src/rom-data.mjs`; the world UI at `0x3D2A2..0x3D2AE` resolves `nameTable[identity+0x2CD]` from the global table at ROM0x526680. The test executes that lookup arithmetic for all five identities.

Shop initialization `0x68CDC..0x68CF4` reads the selected world-map tile from `0x02002E54&31`, calls `0x36350`, and stores the resulting canonical identity at `shopContext+0x4BFB`. The inverse lookup searches the30 world records at `0x02002C10`, using byte `+0xB3+(identity-1)*12`; its return is identity, not tile position. The test assigns arbitrary distinct tile positions and executes this native initialization block for all towns.

The only directly encoded call to native `0xCBDC0` is `0x6E2CE`. Its arguments are:

| Argument | Meaning/source |
| --- | --- |
| r0 | List destination, repointed to0x02030000 in the integrated probe |
| r1 | Shop category tab |
| r2 (`tier_key`) | Native global u16 at0x02001F6C |
| r3 (`special_key`) | Canonical town byte at `*(u32*)0x0200F428 + 0x4BFB` |

`0xCC8B4` maps tier keys0..9 to tier0,10..19 to tier1, and20..65535 to tier2. This is unrelated to the new completion flags. The returned list count is stored as a **byte** at `shopContext+0x446D` by `0x6E2D8`; no high-count acceptance should assume it is a word.

## Installed shop boundary, stock and prices

The final tests call installed `0x080CBDC0` in the integrated probe, not the C symbol alone. This includes the parent's corrected fourth-argument-preserving shop entry shim. Calling the C function directly would not establish that native r3/town survives a long-jump hook.

All2160 cases passed: five towns × six tabs × eight independent gate combinations × three native tiers × territory counts0,7,30. For each case:

- The full original prefix, including native appended special merchandise, equals the clean native builder's count/order/packed row bytes.
- The appended new IDs exactly equal the independent acquisition ledger's town and stage filter.
- No new duplicates or original/new ID collisions occur. No duplicate appeared in these original prefixes either.
- The following output guard stays unchanged, and the full list fits the native count byte.

Maximum list sizes observed are182 Cyril,122 Sprohm,121 Muscadet,116 Cadoan and116 Baguba Port. Each includes every unlocked addition and the maximum territory-prefix length; all are below255. This establishes capacity for the current85-item ledger, not arbitrary future additions.

All1275 native price cases passed:85 new items × five towns × clan ranks0,1,5. Native `0xCBC14` reads the extended32-byte item record and retains its base price, sell-price floor and applicable clan/town reductions. `0xCC958` treats the weapon category as a bit in the town's32-bit mask: type31 uses bit30 and does not index beyond a category array. None of the current town masks favors axes, so axes receive no extra town-category reduction; their applicable clan reduction still follows the native record flags. These are function-level price checks, not1275 UI checkouts.

## Equipment and quest namespaces at purchase

The native purchase commit at `0x6A8C2..0x6A8FE` reads the selected item as u16, obtains the quantity from the native quantity control (`0x2AB5C`), calls `0xCA900` with u16 ID/u8 quantity, then subtracts the approved total from gil. It does not invoke the quest-reward dispatcher or apply its>=376 quest encoding.

Executed this native block through the installed inventory hooks for all85 new equipment IDs with quantities1 and3:170 cases. Every grant changes exactly the intended compressed equipment count; gil falls by the prepared transaction total; all120 bytes of the quest-item region at0x02002B08 remain unchanged. This establishes that this purchase commit treats376..460 as equipment. Original mission/script reward encodings above375 must remain quest items in their separate contexts.

The commit fixtures begin after native UI affordability/quantity confirmation; they do not validate those earlier input guards or render every new item. The parent's actual Recruit Axe checkout/equip/save test is complementary evidence and is reported separately.
