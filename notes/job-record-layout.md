# Native job record map and expansion integration evidence

Read-only council investigation, 2026-09-14. Source ROM: `roms/clean/FFTA_US_clean.gba`, SHA-1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`. Addresses below are **ROM offsets**, unless explicitly prefixed `0x08` or described as RAM. No implementation files changed. Current design source: `JOB-CLASS-SPECIFICATION.md`, especially lines 102–154.

## Record and getter contract

Native job records start at `0x521A14`, stride `0x34`; pointer literal `0xC8598`. `0xC8570` takes `r0=job ID`, `r1=fallback/special job ID`, `r2=selector`, truncating all three to bytes. Selector dispatch table is `0xC85A0`, 48 pointers for selectors `0x00..0x2F`. Invalid selectors loop at `0xC858A` rather than returning an error.

Record `+0x05` is **whole-record inheritance**, not a visual donor: zero uses this record; `0xFF` redirects to the second argument; another value redirects to that job. The getter repeats the dispatch after redirect (`0xC8A02..0xC8A16`). Set this byte to zero for each new job; assigning a visual donor here would replace stats, race, equipment permissions, prerequisites, and other fields too. Cyclic aliases can hang the getter.

`0xC92F0` is the unit-aware wrapper. It passes `unit+5`, `unit+7`, and its selector unchanged to `0xC8570` at `0xC9308..0xC930C`; only name selector zero has a separate override. The job getter and this wrapper therefore use the same selector numbers. The unrelated **unit data** getter `0xC7EA4` has a different selector namespace.

| Record offset | Encoding / purpose | Job selector | Native extraction offset |
|---|---|---|---|
| `00..01` | Little-endian name index | `00` | `C866E..C8674` |
| `04` | Race: Human 1, Bangaa 2, Nu Mou 3, Viera 4, Moogle 5 | `01` | `C8686` |
| `05` | Whole-record alias described above | `02` | `C868A` |
| `06` | Native graphics/animation type byte; ordinary playable donors use 1 | `03` | `C869C` |
| `07..08`, `09..0A` | Two little-endian graphics/animation identifiers | `04`, `05` | `C86AE..C86CC` |
| `0B` | Low/high graphics palette nibbles | `06`, `07` | `C86DE..C86F6` |
| `0C` | Byte, zero on all ordinary playable donor records examined; semantic label not established here | `08` | `C8708` |
| `0D`, `0E`, `0F` | Portrait-related identifiers; generic helpers read these, named characters use separate 14-byte character records | `09`, `0A`, `0B` | `C871A`, `C872C`, `C873E`; consumers `CB79A..CB7B4`, `CB7C0..CB800` |
| `10` | Native primary command identifier; not a visual field | `0C` | `C8750`; copied into command data at `C9FB6..C9FBE` |
| `11` | Byte copied into unit `+0B` on creation; zero on ordinary playable donors; full semantics not established | `0D` | `C8762`; creation `C9768..C9770` |
| `12..15` | Eight packed 3-bit elemental affinities, detailed below | `0E..15` | `C8774..C8820` |
| `16` | Status resistance in low 7 bits; high bit is separately queried by native status code | `16` | `C8832`; `12C960..12C974`, `12C986..12C990` |
| `17` | HP base, unsigned byte | `17` | `C8844` |
| `18` | MP base, unsigned byte | `18` | `C8856` |
| `19` | Speed base, unsigned byte | `19` | `C8868` |
| `1A..1C` | Packed 12-bit WAtk and 12-bit WDef | `1A`, `1B` | `C887A..C8884`, `C8896..C889E` |
| `1D..1F` | Packed 12-bit MPow and 12-bit MRes | `1C`, `1D` | `C88B0..C88BA`, `C88CC..C88D4` |
| `20..26` | HP, MP, Speed, WAtk, WDef, MPow, MRes growth bytes | `29..2F` | `C899C..C8A1C` |
| `27` | Not exposed by this getter; retain ordinary donor value until its direct consumers are traced | none | — |
| `28`, `29`, `2A` | Move, Jump, Evade | `1E`, `1F`, `20` | `C88E6..C8910` |
| `2B` | Two movement/standing behavior nibbles; ordinary playable baseline `0x21` | `22`, `23` | `C891C..C8938` |
| `2C` | Free learned-ability index; zero means none | `21` | `C8946`; `CA230..CA244` writes `0xE4` into `unit+0x40+index` when nonzero |
| `2D` | Index into four-byte equipment-category permission table | `24` | `C8956` |
| `2E`, `2F` | Native first/last ability indices | `25`, `26` | `C8966`, `C8976` |
| `30` | Prerequisite record index | `27` | `C8986`; table pointer literal `C8B18`, four-byte prerequisite records |
| `31` | Behavior flags; zero on ordinary playable donors | `28` | `C8996` |
| `32..33` | Not exposed by this getter; do not call these unused padding | none | — |

### Stat packing and growth

Write the attack/defense pairs as 24-bit little-endian integers:

```text
record[1A..1C] = WAtk | (WDef << 12)
record[1D..1F] = MPow | (MRes << 12)
```

Both fields in each pair are **12 bits**, including attack and power. The vendor randomizer's one-byte attack/power accessors and eight-bit defense/resistance masks do not describe the full native range. A setter that writes `u16(+1B, WDef<<4)` without retaining the low nibble can erase WAtk's high four bits. The proposed bases happen to fit below 256; use the correct packing regardless.

Growth bytes are the desired nominal average multiplied by ten. Level-up routine `0xC9B8C` calls getter `29` at `C9BC4`, adds quotient `/10` at `C9BCA..C9BD4`, then awards one extra point when native random `%10` is below the remainder at `C9BD6..C9BFE`. The equivalent sequence for Speed is `C9C68..C9CA6`, and the remaining stats follow through `C9DF4`. Keep this native algorithm and caps. It does not provide guaranteed fractional gains each level.

The following bytes reproduce the current specification. Base column is the contiguous ten bytes `+16..+1F` (status resistance, HP, MP, Speed, two packed pairs); growth column is seven bytes `+20..+26` in native order.

| Profile | Base bytes | Growth bytes |
|---|---|---|
| Human Samurai | `32 24 1C 6A 56 00 05 44 80 04` | `48 1C 0E 56 50 44 48` |
| Human Dark Knight | `32 28 14 63 5A C0 04 44 60 04` | `50 14 0A 5A 4C 44 46` |
| Bangaa Dark Knight | `32 2C 10 61 5C 20 05 3C 40 04` | `58 10 09 5C 52 3C 44` |
| Bangaa Viking | `32 2C 1C 62 54 20 05 4C 40 04` | `58 1C 0A 54 52 4C 44` |
| Nu Mou Geomancer | `32 21 24 61 3A 60 04 56 60 05` | `42 24 0A 3A 46 56 56` |
| Nu Mou Chemist | `32 22 1C 63 40 C0 04 4C 40 05` | `44 1C 0C 40 4C 4C 54` |
| Moogle Chemist | `32 20 1A 69 44 80 04 48 00 05` | `40 1A 0F 44 48 48 50` |
| Moogle Bard | `32 1E 22 69 3C 40 04 4E 80 05` | `3C 22 0E 3C 44 4E 58` |
| Viera Dancer | `32 1D 18 70 48 00 04 48 C0 04` | `3A 18 12 48 40 48 4C` |
| Viera Mystic Knight | `32 22 1E 6A 52 C0 04 48 20 05` | `44 1E 0E 52 4C 48 52` |

Verification: an inline Unicorn check installed these ten synthetic records into an in-memory copy of the clean ROM and executed the real `0x080C8570` getter. **238 assertions passed**: base fields, all growth fields, neutral affinities, and two additional full-width 12-bit stat tuples. This validates encoding, not recruitment, visual rendering, or full gameplay integration.

## Neutral innate settings

For all ten jobs explicitly use `+05=0`, `+11=0`, `+12..15=48 92 24 01`, `+16=32`, `+2B=21`, `+2C=0`, `+31=0`. These match the ordinary playable baseline for the non-stat fields and prevent accidental inherited aliases, innate elemental changes, free learned abilities, or donor behavior flags.

The element dword is `0x01249248`: three-bit values at shifts 3, 6, 9, 12, 15, 18, 21, 24 correspond to Fire, Wind, Earth, Water, Ice, Thunder, Holy, Dark. Each is `1` (normal). The randomizer names 0 weak, 1 normal, 2 nullify, 3 absorb, 4 half; the native extraction of each three-bit field is independently verified. Bits 0–2 and 27–31 are not these eight affinity fields; the ordinary baseline sets them zero.

Do not label `+31` as purely graphical: bit 2 changes the native weapon type/range results at `12EEA2..12EEB2` and `12EEDA..12EEEA`; bit 1 affects the battle object setup at `97650..9766E`. Full names for every bit are outside this bounded audit. The correct conservative value is zero.

Likewise, selectors `22/23` are not proven animation-only. `CA2E8` caches them in unit `+FC/+FD` (`CA382/CA384`), alongside Jump in `+FE` and its complement in `+FF`. Unit getter `C7EA4` selector `44` returns this block at `C8170`. Native numeric routine `13034C` tests `+FC==2` or `+FD==4` at `13037A..130384` before returning zero or computing a value at `13039E..1303A4`. This proves an effect beyond animation selection; it does **not** by itself prove an unwanted Morpher regression. The vendor files `morphingMorphersMorph/newGetMoving.s` and `newGetStanding.s` intentionally replace those nibbles when morphed. Leave the existing foundation decision separate; retain `0x21` for these new ordinary jobs.

No complete status-immunity/permanent-status bitfield taxonomy was established here. Avoid monster/special job records, keep the neutral bytes above, and do not give free support/reaction indices during unit construction. The specification's no-innate-passive rule cannot be certified from the stat table alone: command setup and job-specific engine branches also matter (notably Alchemist's fixed Item exception).

## Equipment permissions and native exceptions

Native table `0x51D0F4` contains little-endian u32 masks, indexed by `record[2D]`. All three pointer literals found are `0xCAC40`, `0xCB488`, `0xCB5F4`. `CB450..CB47E` demonstrates the whole lookup and `mask & (1 << (itemCategory-1))` test; `CAC02..CAC4C` uses the same scheme in complete equipment validation. Repoint all consumers if allocating new permission masks beyond the original table; the original table ends immediately before the item table at `0x51D1A0` (43 four-byte entries).

Category numbers: Sword 1, Blade 2, Saber 3, Knight Sword 4, Greatsword 5, Broadsword 6, Knife 7, Rapier 8, Katana 9, Staff 10, Rod 11, Mace 12, Bow 13, Greatbow 14, Spear 15, Instrument 16, Knuckle 17, Soul 18, Gun 19, Shield 20, Helmet 21, Ribbon 22, Hat 23, Heavy Armor 24, Clothing 25, Robe 26, Shoes 27, Armlet 28, Accessory 29, Consumable 30. New Axe needs an explicitly agreed new category plus its consumers; do not conflate it with an existing category. Preserve ordinary common-accessory permissions when constructing masks from the specification's body/head/weapon lists.

**Table bits are insufficient for complete legality.** Native equipment validation additionally includes:

- Ribbon category 22 is race-gated to Viera at `CAC22..CAC32`; three special hat/clothing items are also race-gated at `CAC5E..CAC7E`.
- Shield coexistence has hardcoded job tests at `CAD54..CAD86` and another path at `CADC6..CADD2`. The two sequences have different existing allowlists. Extend the relevant branches selectively for the approved new jobs, preserving the vanilla lists and support checks. Test both item-slot orders, new one-handed weapons, vanilla one-handed weapons, two-handed weapons, and equipped support combinations. Changing only `CAD5C` or just the permission mask cannot establish correctness.
- Item handedness and slot constraints are independently evaluated at `CAC8A..CADEA`. The permission mask must not create two-handed Axe/shield or greatsword/shield combinations.

Current registry prerequisite names are consistent with the **current** specification lines 23–24: Dancer = Fencer 2 + White Mage 2; Mystic Knight = Red Mage 2 + Elementalist 2. Native Viera IDs are Fencer `1C`, Elementalist `1D`, Red Mage `1E`, White Mage `1F`, Archer `21`. An earlier council message used obsolete prerequisite context; that concern is withdrawn.

## Conservative native visual donors

These are implementation donor recommendations, not a design change or proof of polished visual suitability. All IDs/races below were verified against the native table and decoded native names. Use donor graphics fields, not an alias in `+05` and not the donor job ID as gameplay identity.

| New job | Same-race donor | Rationale |
|---|---|---|
| Human Samurai | Ninja `06` | Native katana-associated Human body/weapon presentation |
| Human Dark Knight | Paladin `03` | Human armored sword presentation |
| Bangaa Viking | Warrior `0D` | Bangaa physical front-line presentation |
| Bangaa Dark Knight | Defender `0F` | Bangaa armored presentation |
| Nu Mou Chemist | Beastmaster `19` | Nu Mou utility presentation without using the Alchemist command exception |
| Nu Mou Geomancer | Sage `1B` | Nu Mou caster with native mace presentation |
| Moogle Chemist | Gadgeteer `29` | Moogle tool-user presentation |
| Moogle Bard | Animist `24` | Native Moogle instrument presentation |
| Viera Dancer | Elementalist `1D` | Ordinary Viera caster presentation; confirm knife/rapier poses visually |
| Viera Mystic Knight | Red Mage `1E` | Native Viera rapier/caster presentation |

A practical record constructor can start from the appropriate ordinary donor, then explicitly overwrite name/race/alias, command, all bases/growth/movement/evade, affinities/status, free ability, permissions, ability bounds, prerequisites, and behavior flags. Donor `+06..0F` are the scoped graphics-related fields; retain unclassified ordinary bytes instead of inventing semantics. Separate party/job icon tables and custom animation mappings may require donor entries as well—the job record alone does not prove every screen uses the donor. Check party list, job wheel, portrait, battle idle/move, attack with each approved weapon, casting, hit/KO, and named-character behavior after integration.
