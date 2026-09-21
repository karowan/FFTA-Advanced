# Exposed storage foundation

This change establishes ownership, copying and persistence only. It does not enable Fell Cleave431, apply Exposed, modify damage, or install turn/status/remedy events.

## Verified saved layout

The existing native saved block is3CA8 bytes. The compressed inventory allocation occupies offsets1940..1F1C. Counts consume1940..1B40, Human AP1B40..1E70, format header starts1E70, and24 Auto-Potion preferences consume1E80..1E98. `persistent.c` migration clears the full1500-byte original inventory span before writing counts/header; existing valid format1 saves therefore have a zeroed unused tail. Format1 migration remains idempotent and does not wipe newly assigned state.

The new allocation is exactly36 bytes at state+1E98..1EBC, leaving96 bytes through1F1C. It stores one Exposed byte per24 party and12 enemy records. The API uses a supplied saved-state base, including the native normal-save staging base02003CB0; it never aliases staging to live state. Invalid format/version and inexact unit addresses return no owner.

The native party ownership predicate131BB8 compares exact addresses against24 records starting02000080 with stride108. Enemy allocator C83A4 reads base02002FC4 from literal C83B8, advances108, and checks12 records. Native C83CC independently searches12 enemy records followed by24 party records. The test drives the actual C83A4 allocator through all12 available records and then verifies exhaustion. No name, character ID, race, or job determines ownership. Enemy12 ends at02003C24, inside the saved block.

Source searches found no competing tail allocation. Aligned ROM literal search found02001EE4 at61E38 and680CC: these are old original inventory-consumable loops bypassed by the installed61DFE reward-cap and6807C transferable-item hooks. The apparent02001F00 word at58D808 is within encoded asset data, not an identified executable pointer consumer. This is supporting evidence, not proof from zeros alone; native normal and suspend persistence plus existing inventory ports are also exercised below.

## Copy and reset integration

`battle-state.c/.h` own saved-domain lookup, clear and roster swapping. `unit-copies.c` renames the unused byte of each36-byte owned `Extra` tail from padding to exposed. No allocation grows. The same registered snapshot, manager, selection and party-preview owners are used. `ffta_owned_exposed` first checks exact canonical domains, then explicitly registered copy containers.

`ffta_on_unit_copy` transfers Exposed before the Human-AP lookup. This separation is necessary: canonical enemies have no Human AP sidecar. Known destinations copied from unknown sources receive zero; self-copy is stable. The generic native copy dispatcher and library-copy entry already call this function, so no new native hook site is needed. Snapshot capture/restoration therefore carries the new byte with the actual unit record rather than a guessed identity.

`ffta_clear_copy_extra` clears the new byte. Constructors already zero their whole36-byte tails. Native whole-record clear resets the matching saved byte; canonical enemy bulk resets clear every complete record contained in the cleared span. Partial unit-field clears preserve it. Tiny clears and spans outside both canonical domains skip the format lookup and36-record scan entirely. Roster manual sorting calls the existing `ffta_swap_extra`, which now swaps the two saved Exposed bytes along with AP/preferences. Existing format/header, inventory, save slots, AP roots and reserved0203FF44..02040000 guard remain unchanged.

## Validation and artifact isolation

`test-exposed-storage.py` compiles the changed C files plus runtime into a private ROM. It redirects only the five affected existing C entry points; production ROMs, compiler outputs and user saves remain untouched. The starting combat ROM is47f630ded93e0e386e7508c22bda988eaee83977, with verified engine3cee79c1e08f54556b4a70daab50a4d2d3678795. Private ROM ise85a580a74a2ccb7fcb51647032e8c5f4ced0b41; isolated binary3b52ff07a14cc83b2b02568dc09063831e98d0c7.

The isolated suite passes212,567 assertions, including5,724 native whole-copy cases at both stack residues, registered-copy/canonical/enemy isolation, invalid owner rejection, native allocator bounds, native3CB0 staging-relative lookups, format1 retention, sorting, partial clear preservation, whole-copy reset and bulk enemy reset. The source/target cross-product includes all36 canonical records,13 snapshot records, both manager copies, selection, party preview, and an unknown buffer.

`test-exposed-storage-in-game.py` additionally performs native party sorting, normal SRAM saving, emulator destruction, and cold loading; all36 bytes and AP survive. It creates a fresh Herb Picking battle from original early-town SRAM on this exact private ROM, exercises native Fight preview/cancel, saves with native Save Now, destroys the emulator, and cold-resumes the battle. All36 bytes, AP and preferences survive, and a resumed ordinary command opens/cancels. The reserved guard is checked after cold resume. The original early-town seed is hashed/compared unchanged.

## Integration and remaining work

Add `src/engine/battle-state.c` to the main compiler inputs; no assembly or production builder offset changes are required. Existing full-memory expected-value tests were updated: `test-unit-sidecars.py` covers exact/bulk canonical clears; `test-unit-copies.py` populates/captures Exposed, includes all12 enemy sources/destinations independently of AP, and checks36-byte temporary clears; `test-persistent-engine.py` now explicitly marks sort/reset fixtures format1 and verifies the corresponding saved byte. These existing scripts require the parent’s next shared compile to run; their syntax is checked, while the isolated suites above execute the changed native code now.

Before enabling431, the separate lifecycle work must apply once after valid commitment and before hit/miss/retaliation; reject an immunity-cancelled drawback before costs; clear at own-turn start, KO, Petrify, battle end, job change and broad remedy; and integrate the incoming6/5 physical factor. Native enemy reinitialization is covered by the storage clear hooks, but battle-end semantics are not substituted with that reset. Inoculation must never preempt this self-inflicted drawback.

The remaining96 bytes are not a promise that the full expansion state will fit. Even seventeen status bytes for36 units would need612 bytes before timers, source identities and charges. Future effects need an explicit broader saved layout and corresponding owned-copy representation. This Exposed-only foundation neither takes the view/heap guard nor invents that future allocation.

### Unsupported ephemeral evaluators

This is registered-owner coverage, not a claim that every native unit copy has state. `physical-riders.c` uses a private264-byte stack target for Shatter Guard preview; `ffta_owned_exposed(predicted)` correctly returnsNULL. Native law1343C8 likewise uses unregistered264-byte copies. The isolated test explicitly copies a canonical exposed source into an IWRAM stack buffer and a real native heap264-byte allocation, verifies neither gains a state owner, and verifies the source stays unchanged.

Before incoming Exposed multiplication reaches these evaluators, the caller must carry the evaluated unit's explicit state through its scoped calculation or provide an actual registered copy owner. For Shatter, a nonmutating Protect formula override can also avoid the private unit copy. Looking up a matching name/character/job or falling back to the live roster would violate preview isolation. The complete damage and law integration remains outside this storage foundation.
