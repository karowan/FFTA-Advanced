# Council: native shop allocation and wide indices

2026-09-14. Bounded native disassembly against clean US ROM SHA-1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`. Initial read-only mapping was subsequently implemented under the parent council task; acceptance evidence is at the end. Native offsets below omit CPU base08000000.

## Confirmed runtime failure

On frozen integrated ROM `a19ef933d927a33682af25059cfc32c535bafbd8`, an actual mGBA Sell weapon tab with all460 item counts set to1 builds all337 weapon entries (IDs457..460 are present at indices333..336), but stores count81 at context+446D. Native shop context in this fixture is02022F5C. Report `build/expansion/probes/ap-heap/shop-sell-wide.json`; screenshot `conditional-sell-all-weapon.png`. The C builder's full-width return and a larger array alone do not expose the full list.

## Owner and capacity

Shop context is dynamically allocated by68B06 from native22840. Size literal68B5C is9C08;68B0A publishes it to0200F428;68B12 clears the requested size. Free68BEC is followed by nulling global68BF2. Original buffer is context+4504, not a universal absolute02027460. With the observed context base it happens to equal02027460. The next separately accessed field found is4AE4 (6ABE2..6ABEC), giving a376-record geometric span4504..4AE3; this is enough for the current337-weapon Sell tab, but not a proof that every byte of that span is dedicated to the list. Do not infer a256-record allocation from the byte counter. The chosen explicit1840-byte appended tail removes that layout uncertainty.

Append1840 bytes atcontext+9C08 and grow allocation toA338. A wide metadata tail can then use aligned countA338, selected absolute indexA33A, six u16 saved scroll valuesA33C..A347, and optional six byte cursor valuesA348..A34D; rounded allocationA360 is sufficient. Native cursor can remain at44F7 because it is a visible row0..3. Keep original selected ITEM ID44EC separate from absolute list index44EE. Offset44EF is used by another shop mode (for example6D99E..6DA54), so widening44EE in place would corrupt that mode.

The actual shop uses battle heap020159D0..0203F800. In the measured normal buy menu the last free block begins0202D564 and spans76944 bytes. A scratch list at0203C000 lies inside it. The owned tail corrects that lifetime problem without reducing the opening-name heap by16KiB.

## Shared native list contract

- 16210 truncates its fourth argument to u16 at16218..1621A and passes it to15C90; native list count is a halfword atlist+18. No generic u8 count change is needed there.
- Shop scroll/top index is already halfword atcontext+14DA (list+1A). Saved per-tab scroll44F1 is the narrowing boundary.
- 17B68 takes a signed8 relative row/delta and adds it to native halfword scroll, clamps to halfword count, returnsu16. Preserve signed relative -1 semantics. The rowcursor nativeobject+11 is0..3; it does not need to grow because the list grows.
- 6E298 buy-list setup: r0 tab remainsu8; r1 saved scroll is incorrectly narrowed at6E2AA/6E2AC; r2 visible row remainsu8. Sell setup6E384 has corresponding r1 narrowing6E396/6E398. Widen only the scroll argument pairs to16.
- 6E170 already accepts scroll r0 asu16 at6E17A/17C, row r1 asu8 at6E17E/180, and mode r2 asu8 at6E184/186. It stores scroll tolist+1A at6E1B4; change absolute selected-index store/load6E19C/6E1A2, not the relative row argument.
- Sell setup6E42A/6E42C narrows count-4 into scrollr6; widen to16. The later6E458/6E45A is the visible row clamp on the <=4-entry branch; it can remainu8.

## Additional absolute result truncations

The following pairs narrow the u16 return of17B68 before indexing or navigation; change both shifts24 to16, preserving source/destination registers:6A30A/6A30C,6B37E/6B380,6B402/6B404,6C3E2/6C3E4,6D346/6D348,6D3CA/6D3CC. Calls69FB6,6A146,6B4E6,6C0AE,6C232,6D446 instead narrow at subsequent selected-index byte stores listed below. Calls6E4F0,6E6AE,6E876 preserve16-bit results already.

## List relocation must preserve derived non-list fields

Original6E1A8 loads list offset4504 into r4; after reading the item,6E1AE subtracts18 and6E1B2 stores selected item ID at44EC. Original6D45C loads4504 into r3;6D462 subtracts18 and6D466 stores at44EC. Relocating their shared literal to9C08 silently redirects these selected-ID stores to9BF0. Replace those derives with the original explicit44EC offset. The analogous6B502 already loads an independent44EC literal and does not have this problem. Correct initial selection and post-sale refresh must be tested without moving the cursor first, because other movement paths separately write44EC and can mask it.

## Scalar access map

The lists below were located by literal-reference tracking and inspected as native byte accesses. They are concrete direct paths, not a proof against every possible indirect alias. Map field literals to aligned appended offsets and change these strb/ldrb operations to strh/ldrh, preserving registers. Do not change the byte fields next to the originals.

### 0x446d

Literal words: `69F08`, `6A02C`, `6A084`, `6A0D0`, `6A1BC`, `6A2CC`, `6B2E8`, `6B334`, `6C008`, `6C124`, `6C178`, `6C1C4`, `6C2A8`, `6C3A4`, `6E280`, `6E36C`, `6E438`.

| Instruction | Native access |
|---|---|
| `69EE2` | `ldrb r0, [r0]` |
| `69F54` | `ldrb r0, [r0]` |
| `6A066` | `ldrb r0, [r3]` |
| `6A074` | `ldrb r0, [r3]` |
| `6A096` | `ldrb r0, [r0]` |
| `6A0DC` | `ldrb r0, [r4]` |
| `6A0F0` | `ldrb r1, [r4]` |
| `6A2A4` | `ldrb r0, [r0]` |
| `6B29E` | `ldrb r0, [r0]` |
| `6B324` | `ldrb r0, [r0]` |
| `6BFE4` | `ldrb r0, [r0]` |
| `6C054` | `ldrb r0, [r0]` |
| `6C15A` | `ldrb r0, [r3]` |
| `6C168` | `ldrb r0, [r3]` |
| `6C18A` | `ldrb r0, [r0]` |
| `6C1D0` | `ldrb r0, [r4]` |
| `6C1E4` | `ldrb r1, [r4]` |
| `6C380` | `ldrb r0, [r0]` |
| `6E1BA` | `ldrb r3, [r3]` |
| `6E2D8` | `strb r0, [r1]` |
| `6E2FA` | `ldrb r3, [r0]` |
| `6E3B6` | `strb r0, [r1]` |
| `6E3DA` | `ldrb r3, [r0]` |
| `6E41A` | `ldrb r1, [r0]` |
### 0x44ee

Literal words: `6A038`, `6A1C8`, `6A3DC`, `6A4C8`, `6B57C`, `6C12C`, `6C2B0`, `6C498`, `6C544`, `6D524`, `6E278`.

| Instruction | Native access |
|---|---|
| `69FC0` | `strb r0, [r1]` |
| `69FC6` | `ldrb r1, [r2]` |
| `6A150` | `strb r0, [r1]` |
| `6A156` | `ldrb r1, [r2]` |
| `6A328` | `ldrb r0, [r0]` |
| `6A332` | `strb r3, [r1]` |
| `6A338` | `ldrb r0, [r0]` |
| `6A474` | `ldrb r0, [r0]` |
| `6B4F0` | `strb r0, [r1]` |
| `6B4F6` | `ldrb r1, [r2]` |
| `6C0B8` | `strb r0, [r1]` |
| `6C0BE` | `ldrb r1, [r2]` |
| `6C23C` | `strb r0, [r1]` |
| `6C242` | `ldrb r1, [r2]` |
| `6C400` | `ldrb r0, [r0]` |
| `6C40E` | `strb r3, [r1]` |
| `6C414` | `ldrb r0, [r0]` |
| `6C504` | `ldrb r0, [r0]` |
| `6D450` | `strb r0, [r1]` |
| `6D456` | `ldrb r1, [r1]` |
| `6D4C0` | `ldrb r0, [r5]` |
| `6E19C` | `strb r3, [r1]` |
| `6E1A2` | `ldrb r1, [r2]` |

## Per-tab saved scroll and cursor

For saved scroll44F1, moving to u16 requires both ldrh/strh **and two-byte tab stride**. Merely changing the load/store width would overlap adjacent tab entries. Most call sites obtain a fresh tab from6EFE4, perform lsls24/lsrs24, then add that index to the field base. Where the index has no other live use, changing that index-extraction right shift to23 directly yields2*tab. Check each site's live registers rather than applying that globally. Initialization loops share the tab counter with the cursor array, so use a separate scaled index or a small clear wrapper there.

Saved-scroll44F1 direct access instructions:

`69B04 strb r2, [r0]`, `69C60 ldrb r4, [r4]`, `69DA6 ldrb r6, [r4]`, `69E60 ldrb r6, [r4]`, `6A00C strb r0, [r1]`, `6A19C strb r0, [r1]`, `6A382 strb r0, [r1]`, `6AB08 ldrb r6, [r4]`, `6B522 strb r0, [r1]`, `6BB6E strb r2, [r0]`, `6BD7E ldrb r4, [r4]`, `6BEAC ldrb r6, [r4]`, `6BF60 ldrb r6, [r4]`, `6C104 strb r0, [r1]`, `6C288 strb r0, [r1]`, `6C45E strb r0, [r1]`, `6CBD2 ldrb r4, [r4]`, `6D482 strb r0, [r1]`.

Saved-scroll literal words: `69B50`, `69D00`, `69DF0`, `69EA0`, `6A04C`, `6A1DC`, `6A3EC`, `6AB64`, `6B58C`, `6BBEC`, `6BE0C`, `6BEF8`, `6BFA4`, `6C140`, `6C2C4`, `6C4A8`, `6CC2C`, `6D530`.

The initialization loops are69AFE..69B16 and6BB68..6BB80 (six tabs). Other reads lead into buy/sell list reconstruction after tab changes, help/preview, purchase or sale; writes preserve the current scroll after movement. Keep those transitions in the wide-index test, not only repeatedDown navigation.

Cursor44F7 is populated from visible cursorobject+11 and can remainu8. Several branches share the final store at6A3B0 or6C478; do not mistake those for missing independent stores. Two native sequences6B5F2 and6D4FE briefly write the halfword scroll's lowbyte into this cursor byte, then overwrite the same slot with the visible cursor at6B60E/6D518. Preserve the final behavior; blindly widening one isolated intermediate store is unnecessary and could damage adjacent cursor slots.

## Required acceptance evidence

Run actual all337 Sell weapons through indices254,255,256,336; verify displayed item/name/price and committed item ID/count. Switch tabs and return atscroll>=256. Open and close help/equipment comparison atthat index. Sell the last owned item there and verify rebuiltlist clamps scroll correctly. Repeat native Buy navigation and first-item immediatepurchase. Execute zero/one/four/five-entry tab transitions, keeping cursor0..3 and selected indexu16. Verify neighboring original shop fields44EC/44EF and appended bounds. Native shop allocation/free should return to the same heap accounting after exit.


## Implemented result and native validation (2026-09-14)

The guarded storage builder now allocates `A360` bytes for the shop owner. Its appended list starts at `9C08`, u16 count at `A338`, u16 absolute selection at `A33A`, and six u16 saved scrolls at `A33C`. Visible row cursors remain at native `44F7`; selected item ID stays at `44EC`. The four assembly entries preserve the displaced r3 argument across installed 12-byte long jumps and keep the original stack depth. Initialization scales only the scroll index, retaining byte row cursors.

Additional rendered-row boundaries required widening: the top-index load at `6E1E8`, absolute-loop increment shifts at `6E220/6E222`, absolute index passed to tile mapping at `6E818/6E81A`, and its callee argument extraction at `6F6BE/6F6C0`. Relative row arguments remain signed bytes. Without those changes, numeric selection can pass while names/icons refer to the wrong VRAM ring row above 255.

The rendered stress test also exposed an independent native name-padding underflow: `6E716` measures text in tiles, adds two, and `6E724..6E72E` clears `13 - (nameTiles + 2)` tiles after narrowing that subtraction to u16. Fifteen expansion names exceeded eleven tiles. An isolated ROM changing only item379's name pointer to Shortsword prevented the row255 whole-screen corruption. The integrated fix uses compact labels from `src/equipment-display-names.mjs`, preserving the approved full names in registry/help. There is no runtime shop clipping helper. Shop equipment icon callers `0806E6A4` and `0806E81E` were added to the context-specific equipment icon mapping; quest icon contexts remain separate.

`scripts/test-shop-wide-in-game.py` freezes a private ROM, measures all460 labels with native `161BC`, drives actual mGBA through the337-entry weapon Sell tab and validates image headers as well as numeric state. Accepted frozen SHA1: `c8c3f157a250f9db68dc49c6414ad879710c1ca1`. All460 labels fit at most11 native tiles. Rows254/255/256/336 selected IDs378/379/380/460; native names, icons, price columns and shop panels were visually inspected. Tab switching and Info preserve scroll333/index336. Selling the sole Titan Axe removes only item460, grants3250 gil, and rebuilds to count336/index335/scroll332/item459. Native ordinary save followed by emulator destruction and cold load preserves all512 inventory bytes,816 AP bytes and8250 gil. Appended-owner canaries and global guard `3FF44..40000` survive; `3FF30..3FF44` is AP owner metadata and intentionally excluded.

`scripts/test-shop-native-compatibility.py` compares clean/native and integrated shops with0/1/4/5/252 owned weapon fixtures, other categories populated. The zero-weapon fixture checks native skipping of the disabled empty tab. Initial display, six Down presses, and tab switch/return give15 matching state/image comparisons. Every pixel outside the native animated pointer matches; that narrow pointer area is masked because the native/C list build may differ by one animation frame. Counts, absolute selection, selected item and scroll are compared separately without a mask. Native fixtures retain the fixed361-equipment/14-consumable record partitions; compacting consumable records into the equipment prefix would create a false mismatch.

These tests cover the shop port and its ordinary save path, not every battle or results screen. The earlier offset maps above describe the original byte sites replaced by the implementation.
