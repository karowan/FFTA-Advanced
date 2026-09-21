# Council: native AP consumers and ownership

2026-09-14. Bounded read-only implementation audit against `roms/clean/FFTA_US_clean.gba` (SHA-1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`). Addresses below are ROM offsets, not CPU addresses; add `0x08000000` for execution. Native disassembly was inspected directly with Capstone. Vendor `jobAndRaceCustomization` source supplied search leads only; its one-bit/AP-removal model is unsuitable here. No engine files were edited. This is a required-path map, not an exhaustive proof that every possible indirect AP access was found.

## Required design contracts

- Native lesson byte is `unit + 0x40 + raceLessonIndex`. Low seven bits are accumulated AP; bit 7 means usable through mastery or current equipment. It is not an independent permanent-mastery bit. Native `CD560(unit,index)` tests only bit 7; permanent mastery checks compare low seven bits against the race ability record's byte +7.
- `CD480(race,index)` returns `raceAbilityTable[(uint8_t)race] + 8*(uint8_t)index` (`CD480..CD490`). It does not validate bounds. Table relocation alone cannot redirect AP storage.
- `unit+0x34` is the exclusive lesson-count limit used by many loops. `C9ED8(race)` returns original counts: Human142, Bangaa77, Nu Mou95, Viera85, Moogle88. Current expansion counts are178/111/124/118/116. Existing saved units need count normalization as well as new constructors.
- Human new lessons144..177 cannot use the native address formula: lesson144 aliases `unit+0xD0`, where native stat/status data begin. Keep142/143 reserved. Other racial extensions fit native byte capacity but still need updated counts, records, and list/range consumers.
- Native Viera Cure coupling is intentional existing behavior: `CD620(unit,index)` copies the full byte between indices0x1A and0x21 for race4; `CD1FC` also considers both equipment lessons. Preserve this. Vendor installation explicitly removes it at490A2, which is not appropriate for this expansion.

## AP hook map

| Priority/path | Verified native access and live inputs | Required integration |
|---|---|---|
| Shared usability | `CD560..CD580`, r0 unit, r1 truncated lesson, returns bit7 as0/1; null returns0 | Route Human extension reads through owner-aware AP logic; preserve this usability contract rather than substituting a mastery-only predicate |
| Shared usability setter | `CD544..CD55E`, r0 unit, r1 lesson, ORs0x80 into existing byte | Redirect extended lesson writes or derive equipment usability without modifying persistent AP during previews |
| Equipment teaching grant | `CCF44(unit,item)` uses teaching-list job match against unit+7; inline address at`CCF7E..CCF8A` ORs0x80; then callsCD620 | Patch inline path too. Calls atCA2D0,CB0C2,CB1DE do not go throughCD544 |
| Equipment removal/change | `CAF78` reads at`CAFEA..CAFF4`; clears bit7 at`CB036..CB042`. `CB0D8` reads at`CB148..CB152`; clears at`CB192..CB19E`. In both, r7=unit,r5=lesson; clear base r6=unit+34 then+0C | Redirect both reads and writes. Preserve equipped reaction/support/combo cleanup and CD1FC check for another item teaching the lesson |
| Candidate equipment legality | `CAEC4..CAECE`: r8=unit,r5=lesson; low7 read before cost comparison | Expanded mastery must remain visible when replacing teaching gear; preserve candidate-preview isolation |
| Results AP award | `49032..49038`: r8=unit,r6=lesson; produces r7=byte pointer. Store`4909C` usesr3; cost viaCD480 at49040 | A pointer shim here can preserve native earning/clamping/mastery notifications. It must leave r7 pointing to the actual byte for the later store, and preserve other locals |
| Job prerequisites | `C8B6C..C8B76`, unit inr10, byte offsetr5; low7 versus nativecost | Use expanded read and new job lesson lists; do not silently count equipment-only availability as mastery |
| Command discovery | `C8F76..C8F7C`, unitr7,lessonr4, tests nonzero. `7D93C..7D946` scans AP within command interval | Redirect extended reads and review noncontiguous job intervals |
| Typed ability lists | `CCFB8(unit,out,type)` inline bit7 read`CD072..CD080`; `CD0EC(unit,out,type)` nonzero read`CD19E..CD1A8`; both loop1..<unit+34 | Central CD560 hook does not catch these inline reads |
| Job mastered | `CD2C4(unit,job)` reads at`CD322..CD33A`, unitr7,lessonr3, compares low7 tocost | Expanded list membership must replace old contiguous interval assumption where Soldier/Gladiator lessons are appended |
| Party ability UI | Reads at`7B9AA..7B9D4`, `7C362..7C368`, `7C49C..7C4A2`, `7C5D6..7C5E4`, `7C694..7C6A2`, `7C770..7C77E` | Redirect row filtering and row AP-byte population together; raw row AP is stored at output row+0E |
| Blue Mage learning | Read`A7BC8..A7BD2`, storeE4`A7BE4..A7BEE`; unit is the doubly dereferenced r7 pointer, lesson r6; cost comparison viaCD480 | Preserve native Learning/race/target checks. Existing Blue Magic indices remain native; ensure expanded accessor does not alter them |
| Steal:Ability | Read`132E62..132E6E`; receiving storeE4`132FC6..132FD0`; victim clear`132FF8..132FFE`; count/mastery read`133D30..133D3A` | Every modified lesson must respect each unit's ownership. Keep CD1FC/CD544/CD620 postprocessing and target support cleanup |
| Scripted AP loss | `1291A6..1291C4` selects a nonzero low7 lesson; `129224..129254` reads/caps loss; `129264..129266` stores; unitr8,lessonr5 | This path is outside ordinary result awards. Redirect scan and store before allowing extension-bearing units through it |
| Template/free innate lesson | `CA22C`: `CA23C..CA244` writesE4 at jobgetter21 lesson when nonzero | Preserve original jobs. New profiles currently have no free innate lesson; route safely if that ever changes |

The low7 check at`620EC..62106` is another required read in roster replacement/learning reconciliation. A raw search only for `adds #0x40` is insufficient: the same array is addressed through `unit+0x34+0x0C` and through a retained pointer. Conversely, many unrelated battle structures also use offset0x40; those are not AP merely because the immediate matches.

## Results owners and battle pointers

**Results ownership is proven:** `48FC2..48FD4` obtains a participant index from`0x0201F518`, multiplies by264, adds literal`0x02000080`, and retains the resulting permanent roster record inr8. Literal words are49148=`0201F518`,4914C=`02000080`; participant count comes from`0201F4FE` (49144). Ordinary result AP therefore writes live roster sidecars directly without copy inference.

**Battle checks accept broader pointers:** player command callsCD560 at25FC8,2606A,260BE,26B54,26D8E,26FDA,27A1E. The inspected callers load`(*(0x0200F438))->0x18` as unit pointer (for example26D82..26D8E). Enemy/action code also callsCD560 at134036 and134278; at134034 its unit isr6 supplied by the action-list routine. A roster-only assumption atCD560 is unsupported. This audit has not established that every invocation of the player pointer is a permanent roster record.

Native`131BB8(unit)` already checks exact pointer equality against all24 permanent roster addresses and returns0/1. It does not identify copies. Native`C83A4()` allocates a free enemy record from twelve264-byte records starting`02002FC4`; `C83CC(characterId)` searches enemy records first, then party records, for special IDs>1. Generic character ID1 is not a unique owner key. Do not use character/job/name equality or unchecked modulo arithmetic to alias unrelated units into a sidecar.

**Copies and rollback are proven:** battle code9DF2E..9DF54 copies each underlying`*battleUnit` record into successive264-byte backups at`r8+4`, through copy call9DF42. Code9F88C..9F89A performs the reverse copy from the backup into`*battleUnit`. A provenance tag would survive these copies, but AP stored outside the copied record would not roll back with it. Before enabling AP-changing preview/simulation actions, extend that transaction or defer persistent AP writes until the actual action commits. Deriving bit7 from the current copy's gear avoids one preview mutation class; it does not solve temporary low7 gains/losses or rollback.

Another concrete copy is6512E: source pointer comes from a selection pointer array at object+424, destination is object+A4C, length108. C6D6E similarly copies a supplied unit into an allocated temporary record; its null-source branch clears108bytes atC6D58. These should be included in copy-ownership fixtures; an arbitrary registry of every memcpy is not recommended.

## Constructor, load, replacement and sorting hooks

**Constructor `C9644(destination,template,level)` must be handled before extended lesson loops run.** C965A..C9664 clears exactly108bytes. It installs equipment viaCA268 atC9AA6, imports template learned abilities throughC9F88 atC9AAE, then applies native innate lessonCA22C atC9AB4. Verified direct constructor calls: BAC84,CA780,D2912,1243EC,124C20,125716,12BAD6. CA744 builds a formation into successive free records; its constructor call isCA780. Enemy construction is verified at1243E2..1243EC usingC83A4.

**Do not simply extend C9ED8 before the unchanged template importer.** C9F88 writes the returned count atunit+34, then loops lessons1..<count. C9FFE..CA014 reads template+14+(lesson-1)/8. CA024..CA02C writes E4 to(unit+34)+0C+lesson. Extending Human count to178 therefore both overwrites native fields fromlesson144 and makes lesson161 read template+28, which is separately consumed as a support field atC9FEA/CA04C; +29 is another field. Keep the vanilla template import bound and native writes, initialize new lessons separately, then publish the expanded count. Existing-race new lessons must start zero rather than accidentally importing formerly unused bitmap bits.

Load migration already runs on validated staging blocks beforeCpuSet at13AA48/13AAD8; success commits3CA8bytes at13AA50/13AAE0. Normalize unit counts and any approved provenance there for existing saves. Only first conversion should zero new AP; current-format saves must retain it. New-game migration clears the816-byte sidecar within the original inventory allocation, but later recruitment/replacement still needs per-slot initialization.

**Constructor hooks alone miss roster replacement.** Routine61F54 uses a live roster pointer matched against its input. Its mode-zero path unequips then clears the matched roster record at61FA4. Its other path copies temporaryr4 to liver7,108bytes, at61FEC. Clear or transfer the corresponding sidecar on these exact lifecycle events. Do not clear AP on an ordinary job change: C8C24 callsCB4C0 to remove equipment, updates job/header fields, and preserves learning.

Current foundation manual sorting is a custom whole-record swap installed at73C3E (see builder for current symbol placement), implemented from vendor`manualSorting/buttonmanualsorting.s`. It swaps108bytes through enemy scratch02002FC4. The sidecar and Auto-Potion preference must move atomically with the two selected roster slots, before any subsequent refresh observes the new records. If a slot-number tag is adopted, restamp both moved live records after swapping; copying their old tags unchanged would point each unit at the opposite slot. Native list sorting and physical record swaps must be distinguished.

## Proposed index-zero provenance tag: not yet approved

Evidence in favor: native learned-template import starts atlesson1; the inspected full racial AP loops inC8F64,CD04E,CD184,12919C and132DEA start at1. Unit+40 is inside the108-byte copy, so it follows the concrete copy paths above.

A small independent Unicorn check executed thirteen native calls: five C9ED8 race counts, five CD480 index-zero row lookups (all returned eight zero bytes), and three CD560(unit,0) checks. The last returned0 for byte00 and1 for both proposed tag endpointsA0/B7. Thus the index-zero semantic change is measured; the row's empty data is also verified, but does not establish that its per-unit byte is globally unused.

Evidence preventing approval: CD560 has no index-zero guard, and settingA0|slot changesCD560(unit,0) fromfalse totrue. CD544 similarly permits index0. Constructor clearing and replacement overwrite the byte; saved legacy records need controlled stamping; enemy constructors must never inherit a live party tag. The bounded disassembly scan is not proof that all index-zero readers or writers are absent. A stale copied tag also needs protection against dismissal/reuse or physical sorting of the referenced slot, and provides no snapshot of externally stored AP.

If pursuing the tag, first explicitly reject index0 through all expanded accessors, verify native default/empty lesson consumers, trace accesses to a stampedunit+40 during real equipment/job/battle/save flows, and test generic enemy/recruit creation, live-slot replacement, two simultaneous copies, cancelled actions, and sort/dismiss/recruit. Until then, keep the implemented explicit live/staging-state resolver rather than claiming generic-copy ownership support.

## Recommended implementation order and acceptance

1. Add a byte-preserving Human AP accessor plus exact race-count normalization, leaving all original indices/other race bytes on their native paths. Keep the template importer bounded as above.
2. Wire result pointer49032, sharedCD544/CD560, equipment grant/removal/candidate paths and ability-menu reads. Confirm one Human extension lesson can be taught, earn partial AP, master, survive removing gear, and save/reload; repeat another race below native capacity.
3. Extend job/race list semantics, including C94D0's old maxjob0x73 atC952A and CD364's hardcoded racial job ranges atCD3BC..CD3E4. Soldier/Gladiator appended lessons require explicit membership, not a widened contiguous interval that swallows other jobs.
4. Complete lifecycle ownership before action/AI preview writes: constructor and roster-replacement clear/transfer, manual swap, copy reads, battle snapshot rollback, AP theft/loss and learning. Preserve existing Blue Mage and Viera behavior as differential fixtures.

Required tests distinguish low7 progress from bit7 equipment availability, two copies with different gear, live versus staging state, original Human maximum/reserved142/143/new144/last177, all other race bounds, rejected/cancelled actions, slot reuse, sorting and cold save reload. Passing isolated address-helper tests does not establish these lifecycle contracts.
