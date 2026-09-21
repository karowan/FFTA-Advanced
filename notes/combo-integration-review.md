# Combo integration council review

The eight combo profiles and four scoped weapon gates pass the native regression on combo ROM `fa23daa43767ba45588c2413f49ab7bb16ac9b90`, engine `7d963b9cd35c82820c75728b14e54fb1aa4c4d31`. The review found and corrected three named-donor mismatches before acceptance. Native committed battle, JP spending, and chain execution remain separate gameplay acceptance work.

## Native domains and exact donors

Scanning all24 native racial banks finds42 type5 combo lesson records. They occur only in player races1..5 and cover every nonzero global comboID1..33. Global0 is the absent/default profile. The native profile table at `0852736C` therefore needs all34 original rows preserved. Its only three literal consumers are `12E19C`, `12E3E4`, and `130514`; the current builder repoints exactly those three.

The expanded table has136 four-byte entries: original0..33 unchanged, reserved34..127 zero, new128..135 copied from the exact named profiles below. Assignment byte `unit+3C` remains a racial lesson index, not the global profileID. Native `CD480(race,index)` reads the racial record, whose halfword+4 is the global comboID.

| New lesson | Exact native donor | Native globalID | Other-text nameID | Native four bytes |
| --- | --- | --- | --- | --- |
| SAM-C1 | Ninja Combo | 15 | 568 | `00402064` |
| DRK-C1 | Knight Combo | 2 | 546 | `00221C64` |
| VIK-C1 | Sword Combo | 7 | 571 | `00220064` |
| GEO-C1 | Wise Combo | 17 | 549 | `00421C3C` |
| CHM-C1 | Thief Combo | 23 | 551 | `00400064` |
| BRD-C1 | Juggle Combo | 32 | 553 | `00620046` |
| DNC-C1 | Lunge Combo | 6 | 566 | `00220064` |
| MYK-C1 | Red Combo | 11 | 544 | `00420046` |

Initial proposed donor23 for Ninja was actually Thief; donor1 for Sword was Combat; donor18 for Wise was Gold. Sword7/Combat1 have identical bytes, but Ninja15 differs from Thief23 in byte2 bit5, and Wise17 differs from Gold18 in byte2 bits2..4. The currently traced readers mask those bits out, so the visible power/range/hit happened to agree. Copying the exact named records still preserves the full native profiles. Parent corrected the builder to15/2/7/17/23/32/6/11.

Native participation power reads byte1 low5 at `1304FE..130502` and maps0..4 to5/8/10/12/15. Range at `12E3D2..12E3DE` combines byte1 high3 with byte2 low2. Chance reads byte3 at `12E16E`, optionally adds native RNG modulo15 in mode bit4, and clamps0..100.

## Gate and trampoline contracts

`combos.c` identifies only type5 lessons whose globalIDs are128..135, using the evaluated unit's raw race and assigned racial index. Original combos bypass the new weapon gate. The native range/chance/power paths still determine original return semantics.

The primary weapon is the first qualifying weapon in the native five-slot equipment order, excluding shield category20 and empty/nonweapon entries. It is not the strongest weapon. Samurai requires katana9; Dark Knight1/5/6; Viking axe31; Geomancer11/12; Chemist7/12; Bard instrument16; Dancer7/8; Mystic Knight8/3. The actual evaluated copy is used; there is no canonical-owner/name/characterID alias.

The installed entry points are `CD4C0`, `12E130`, `12E3B0`, and `1304E0`. Entry wrappers restore the long-jump's savedr3, save the caller's frame, alignSP to8 bytes for C, then restore the original incomingSP. The three native trampolines reproduce the displaced prologue and native getter call before continuing at `12E13C`, `12E3BE`, and `1304EE`.

These trampolines use an ARM7TDMI standalone Thumb BL suffix after settingLR. Unicorn's newer CPU model rejects that legacy instruction; the test models that single instruction's target and link semantics. No native chance/range/power/getter body is stubbed.

## Remaining initiation and participation paths

- Native menu construction calls `CD4C0` only at `264E2`, after native flag2 and `C8240` checks. It retains its generic status check through `25F8C` at `26516`. Returning0 from the scoped assigned-combo hook removes an unavailable new combo while preserving native original menu behavior.
- Native participation evaluator `A966C` calls geometry `12E1A8` with flag8. Its combo branch calls chance at `12E210` with mode4 and immediately rejects0, then calls range at `12E232`. Therefore a failed weapon gate cannot acquire range simply by returning0 from the range helper.
- After geometry, `A9682` calls chance again with mode0 for the native participation probability path. Both native chance callers reach the installed boundary.
- Power readers at `B330C` and `B42AC` sum the returned participant power. Their post-call instructions do not rely on native volatile-register residue.
- Native chance first checks `C8298` (unit flags+28 bit1000), then assigned globalID, then all44 status bits through `133B3C`. `133B24` uses the shared native status-permission table `08527E1C`; it does not index a status table by the new global comboID. There is no additional comboID-indexed status-table expansion needed in this path.

The audit found no additional profile-table reference or uncovered direct caller of these four boundaries. This callsite finding is narrower than full JP/animation/chain gameplay acceptance.

## Repeatable verification

`scripts/test-combos-native.py` freezes the combo ROM, exact input, manifest, engine, and symbols and checks their hashes before running. It independently asserts named donors from the original racial records and nameIDs rather than trusting the builder's profile labels.

- 528 original comparisons: all42 native racial combo lessons and no-assigned across24 races, all four entry points, both incoming stack offsets0/4 modulo8.
- 2560 weapon cases: all32 actual equipment categories, all eight new lessons across their ten racial owners, all four installed entry points, both stack offsets.
- 160 ordered-hand cases: a stronger allowed offhand cannot rescue a disallowed primary weapon; a legal primary keeps its native profile despite another offhand.
- 3620 native chance comparisons: none/all44 individual status bits, both deterministic/RNG modes, two seeds, both stack offsets, plus native unit flag1000. Both chance return and resulting RNG state match a unit assigned the exact native donor profile.
- Null menu behavior preserved. All functions leave unit data, equipment/AP storage, and surrounding guards unchanged. All13210 observed C entries have8-byte alignedSP; native callee-saved registers and incomingSP are preserved.

Reports are under `build/expansion/probes/combos-native`. The test is ready for the sequential build test list; this council did not modify shared build scripts or production code.
