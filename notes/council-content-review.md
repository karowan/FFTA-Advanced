# Content data implementation council review

Scope: `scripts/build-content-data-probe.mjs`, `src/engine/text-hooks.s`, and generated content probe. This is a review of data and native readers, not a claim that jobs, AP learning, or battle effects are complete.

## Concrete findings and disposition

1. **Fixed: text hook literal outside the GBA address map.** `0x08036d6c4` evaluates to `0x8036d6c4`. The native bank 13 pointer is at `0x0836d6c4`. The original literal would fault for ordinary text as well as new help. Parent corrected it; actual native text decoder tests pass afterward.
2. **Fixed: item graphic IDs were cleared.** Equipment record `+0E/+0F` is a little-endian graphic ID exposed by native item getter `CA7A4` selector 9. The randomizer's label of `+0E` as Nono type is incorrect. Native weapon display obtains this ID at `986CA`, passes it through `SP+0C`, and uses it in graphic creation at `98956..98962`. Parent preserved donor IDs; native getter tests pass.
3. **Fixed: public teaching getter truncated sets above 255.** `CA7A4` selector `0x12` originally reads only byte `+1D` at `CA8F2`. Expanded sets reach 309. Parent added an ARM7-safe byte-combining replacement via the getter's dispatch table. All 376 original items across all 19 getter selectors remain equivalent to clean ROM; every new getter returns its complete set ID.
4. **Fixed and verified: four inlined teaching readers also truncate.** `48FFC`, `6717A`, `6FC5C`, and `8C822` each read byte `+1D`, multiply by 20, and add the teaching table. They bypass the public getter. Native instruction-block tests initially reproduced exactly 216 failures: 54 items with sets 256–309 in each of four paths. Parent added safe byte-combining shims; all four blocks now pass every item ID 0–460 without stack damage.
5. **Fixed and verified: retain donor graphics parameter at `+0D`.** Selector 8 reads this byte. Weapon display calls it at `986D4`, retains it in r9, then passes it to `21E64` at `9898E`; that routine writes graphic object byte `+1D`. Native rapier/rod donors use 2 and instrument donor uses 1. Parent preserved donor values; tests pass. Exact visual meaning is not established, so it is documented as a graphic parameter rather than guessing a palette name.
6. **Fixed at reviewed callers; native tests pass: menu icon IDs collide with quest icons.** The menu icon API is separate from equipment `+0E`: `CB980(destination, index)` decodes native icon bank `0x083C83FC`; `CB99C(index)` reads palette metadata at `0x083C7FE4`. The index is the original raw item ID, including native quest icons above 375. New equipment IDs 376–460 therefore showed quest icons. Parent added caller-aware entry wrappers which map only equipment pixel/palette arguments to donors. Names, selection IDs, and transactions retain actual new equipment IDs. Generic calls and shop quest/mystery modes retain their original namespace.

## Verified equipment field meanings

| Field | Native evidence / treatment |
|---|---|
| `+0B` | Native handedness; donors retain ordinary family behavior; axes explicitly two-handed. |
| `+0C` bits 0–2 | Double Sword, Doublehand, Monkey Grip compatibility. Axes disallow all three; ordinary families retain donor values. |
| `+0C` bit 3 | Discount eligibility, used by native price function `CBC14`. |
| `+0C` bits 4–7 | Native shop/random tier flags; new shop-only weapons clear these. |
| `+0D` | Graphic parameter routed through `986D4` to `9898E/21E64`; retain donor. |
| `+0E/+0F` | Graphic ID, native selector 9 returns u16. `+0F` is zero in all 375 original items, but the getter genuinely supports 16 bits. |
| `+18` | Actual Nono mystery category. Native `CC788` chooses an original item and rejects category zero at `CC7AE`; `6DA5E` uses the value to select mystery-item help. Clear on the new weapons to keep them shop-only. |
| `+19` | Zero in all 375 original records. No meaning established; preserve donor zero. |
| `+1D/+1E` | Expanded teaching set index. Native original index reads are byte-wide and require the explicit reader changes above. |

The original Nono selector still samples only original IDs: its modulo is 376. Clearing `+18` is a second safeguard if stock-selection limits later expand. Do not expand native mystery/random/reward pools as a shortcut to make new shops work.

## Repeatable tests

`scripts/test-content-data.py` writes `build/expansion/probes/content-data-tests.json` and returns nonzero for any failed check. It covers:

- All original 376 equipment records, including biased index zero; all 225 original teaching sets; all original race ability records and Other-name pointers.
- All 85 new profiles against the approved acquisition ledger, their names/prices/stats/handedness/graphics, every teaching owner and all 129 lessons.
- Actual native `CA7A4` for all 19 selectors and all 376 original item IDs, plus complete new teaching and graphic getters.
- Actual instruction blocks at all four inlined teaching consumers for every item ID 0–460.
- Actual native `19A50` bank routing for all 1,616 original help IDs and 85 new equipment help IDs.
- Actual native `13E9C` decoding for all those entries, checked against the foundation's output for original text and generated uncompressed body for new help. The approved foundation's Pub help swap at IDs 0028/0029 is preserved. Stack and r4–r11 are checked around full function calls; output guards catch buffer corruption.

The 85 new equipment descriptions use only one or two lines and fewer than 100 encoded bytes each. A bounded decode test is appropriate here. Future effect-specific help may be longer and requires new layout tests.

After the fixes above, content probe `1963e38351de0611808a2106f2f8d21dc0ef87ff` passed **14,959 checks**, including all four inlined readers and donor graphics parameters. The subsequent `45a9e538d5cb535ec671da51504979296db4e92a` probe also passed. Read the latest generated report for the authoritative disposition for a newer build.

## Menu icon follow-up

Confirmed equipment-only icon callsites:

| Context | Pixel decode call | Palette call(s) |
|---|---|---|
| Party/equip item list | `8168A` | `8160E` |
| Equipment detail/name renderer | `7031C` | `70370`, `70392` |
| Unit's five equipped slots | `749E8` | `749B0` |
| Selected equipment/name renderer | `8E3F2` | `8E3DE` |
| Shop equipment mode | shared `6796E` | `67514` |

The shop draw call is shared: native context at r5 has mode byte `+8`. Mode 4 uses equipment IDs; mode 5 constructs quest icons and mode 6 mystery icons. A conditional wrapper must map only mode 4. The palette callback at `67514` is already equipment-specific.

The list renderer reads actual item ID from entry `+4` at `8160A`, not `+18`. Do not put a donor ID into that field: it is also the item selected for gameplay. Map only the icon call arguments.

`scripts/test-equipment-icons.py` provides **6,915 native pixel/palette checks** across all these callsites and IDs 0–460, including both non-equipment shop modes and the unchanged generic icon APIs. It writes `equipment-icon-tests.json`. Before context mapping, probe `e870b554b467cdc106927c5497cba0b1027e9659` had 671 pixel/palette failures. After the wrappers, probe **`cb5f63fbd84798e38e3f3fb65b2597fed68c92e6` passed all 6,915 icon tests and all 14,959 content tests** (21,874 total checks).

Wrapper audit: ARM entry transfers the original LR and r5 without disturbing saved registers; C reads the correct original bank and masks the index to u16 as native code did. The shop pointer is bounded before reading mode byte `+8`. The generic APIs produce identical pixels/palettes for every tested original/quest index. The axe currently uses Barong donor 52 artwork; this test does not claim custom axe artwork exists.

**Mission Item context concern closed by actual native UI comparison.** `scripts/test-quest-icons-in-game.py` cold-loads the ordinary `early-town.sav` through the game's Continue/Load flow and opens Clan > Mission Item in isolated mGBA. A disposable fixture adds only native completion flag `0x303` (saved byte `0x02001FD0`, bit3, Thesis Hunt/internal mission4 complete) to make the Clan menu available, then native quest local IDs1–85 in two independent64/21-slot batches. The expanded fixture also owns all85 new equipment IDs at the same time, proving coexistence of both namespaces.

The final run on frozen expanded ROM **`28fccf61903920412a3cb4f34d82b62c7c235bc5`** versus foundation **`2c1552fc7f63b5694ec66fe52610a221800a3f24`** passed **170 exact full-frame pixel comparisons**:85 distinct selected list screens and85 selected first help pages, covering global quest/icon IDs376–460. Manual screenshot checks and original ROM names confirmed Magic Trophy/local1, Crusite Alloy/local33, and Rusty Sword/local85. The list includes the native full64-slot case. Names, icons, palettes, counts and help descriptions match the foundation.

The test checks that roster, equipment/AP storage, all256 quest-inventory bytes and emulated SRAM remain unchanged by viewing. It never saves to a user play file or alters the source seed. ROMs are copied into disposable build fixtures before execution so concurrent rebuilds cannot change the tested hash. Quest help can have multiple pages, and B advances pages; each help inspection restores its same-build selected-list checkpoint before scrolling. Assertions enforce85 distinct selected screens and a visibly opened help page for every item, avoiding false coverage caused by swallowed navigation input.

Report and screenshot evidence: `build/expansion/probes/quest-icons/report.json` and `expanded-001-list.png`, `expanded-033-list.png`, `expanded-085-help.png` in the same directory. Quest consumption/rewards and custom axe artwork remain outside this UI test's scope.

## Remaining integration boundaries

- New ability help is still deliberately zero in this data-only probe; final effect-specific descriptions are required with dispatch integration.
- AP reads/writes still need sidecar-safe access and noncontiguous job lesson lists. Correct teaching rows do not prove learning is safe.
- Native weapon-animation type dispatch at `986DA..98758` handles types 1–19. Axe type 31 requires selective graphics mapping and actual battle checks.
- No buffer claim is made for larger battle action lists, job menus, Throw/Draw Weapon, or new job sprites. They remain separate integration tests.
- Equipment and quest item IDs intentionally overlap numerically after 375. Keep their context-specific namespaces and do not replace quest reward/removal thresholds globally.
