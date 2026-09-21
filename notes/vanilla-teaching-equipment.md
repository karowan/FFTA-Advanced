# Vanilla teaching-equipment source ledger

Updated September 16, 2026. A04 native source audit and I10 equipment recovery are complete within their documented bounds. Final campaign/release acceptance remains open. Six recovery services are
installed; the other five rare items have renewable native encounter sources.

Current source audit: `eabce3b98536510e40a8ec5893ecd9bd2996566c`. All375 original equipment
records remain byte-identical through the installed native item-table pointer.
The ledger enumerates216 equipment items teaching457 racial AP records, with
job, race, action/type, AP and alternate teachers. Matching an ability's English
name across races does not establish that the same unit can learn it elsewhere.
The three boot rows using job255 are retained separately; they are not parsed
as racial AP records.

## Reproduction and evidence

Run `node scripts/audit-mission-item-dependencies.mjs`, then
`node scripts/audit-vanilla-teaching-sources.mjs`. The latter writes ignored
`build/reports/vanilla-teaching-sources.json`, bound to the verified candidate
and clean USA hashes. No ROM is changed and no game build is required.

For the original clan gift consumer, use the declared plan:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-vanilla-clan-gifts-cached
```

On prior candidateea9ed600, run `20260916T183431.890143Z` passes all four selected steps: assembly
verification, both static ledgers and the native gift test. The latter passes
424 assertions in149 fixed scenarios covering all63 nonempty original gifts.
Every required skill is tested one level below its threshold, at eligibility,
and after claiming. The native function returns the exact item/quantity and
sets only its original receipt bit. A second claim fails without inventory or
other persistent changes. Reward-dialog acceptance, full equipment inventory
and cold saves are separate obligations; this consumer returns a reward and
does not itself add equipment to the bag.

The harness's top-level ROM label refers to its older foundation image; the
consumer report and verified assembly identify the actual candidate above.
Private report/state hashes remain in the run and candidate directories.

## Source classes, not completion claims

| Teaching items | Static evidence | Remaining interpretation |
|---:|---|---|
|109|Ordinary tier or town territory stock|Installed native shop union covers all109 at declared late-tier/territory inputs; campaign acquisition remains V06.|
|70|A random reward pool referenced by repeatable original missions|Seven ingredient-free repeatable missions pass posting/completion/reposting; native seeded selection covers all70.|
|17|Mythril combo weapons in original roaming-clan rewards|NativeD2114 admits all17 at all three tiers; real seeded selector checks pass. No new recovery for an unused mission selector.|
|9|Morpher Souls229–237|Native Capture/disposal/release/recapture passes for all20 species. Native roaming generation and regeneration now establish renewable access.|
|11|Rare items listed below|Six recovery routes are installed; the other five have native theft witnesses and renewable roaming/colored-clan access. Continuous second paid equipment recovery now passes; final campaign acceptance remains open.|

The categories sum to216. Formation possession, a reward-pool entry and a
one-time gift are deliberately separate fields in the machine-readable ledger.
All442 native formation records are inspected, including Mortal Snow's final
formation442. The prior audit used a shifted editor layout and incorrectly
rejected this selector. Native battle setup uses `54CD54 + 40*ID`, count+0 and
unit pointer+4; event+4 supplies enemies when nonzero, otherwise event+2 does.
The corrected audit and native selector proof are documented in
[repeatable encounter access](repeatable-encounter-access.md). Historical
template combat results remain valid; their mission/formation labels are superseded.

## Rare item review

Numbers below are native item and mission records, not walkthrough numbering.
All listed lessons have no other teaching item for the same racial AP record.
Normal AP requirements are preserved.

| Item | Lesson access | Original source evidence and next check |
|---|---|---|
|26 Materia Blade|Bangaa Ultima Sword; moogle Ultima Charge|Recovery471 after original Present Day22 and game completion. Original Throw/Hurl pool8, levels40–44, and treasure/hidden-steal opportunities are preserved.|
|68 Vajra|Bangaa Meltdown|Gift20, Smithing30; native theft from Brass Dragoons, native formation214. Roaming generation and regeneration pass.|
|84 Cinquedea|Human/moogle Steal Ability|Recovery474 after claimed gift23 (Negotiate30) and game completion. Original gift and Throw/Hurl pool7 are preserved.|
|99 Madu|Viera Doublecast|Recovery475 after claimed gift15 (Negotiate40) and game completion. Original gift, encounters and Throw/Hurl pool7 are preserved.|
|116 Zanmato|Viera Ultima Masher|Gift6, Smithing50; fixed mission32; native theft from Clan Belmia, native formation182. Roaming generation and regeneration pass.|
|158 Zeus Mace|Nu mou Ultima Blow|Recovery472 after original Golden Clock16 and game completion. Original Over The Hill25 equipment and hidden-steal/treasure opportunities are preserved.|
|183 Max's Oathbow|Viera Doom Archer|Gift16, Track40; native theft template belongs to Brown Rabbits109, native formation273. Native colored-clan cycles provide another opportunity after success or a missed mission.|
|298 Genji Armor|Human Reflex|Recovery473 after original The Dark Blade101 and game completion. Original finite formations and treasure opportunities are preserved; other races' Mirage Vest does not teach this racial lesson.|
|313 Dark Gear|Nu mou Weapon Def+|Native theft passes for White Kupos110/native274 and four roaming-clan loadouts. Native roaming availability passes; no new recovery needed.|
|314 Wygar|Human/bangaa Strikeback|Gift24, Track30; six native theft witnesses pass. Renewable roaming sources include native222/232/234. Native formation196 is protected by Maintenance and excluded.|
|336 Sage Robe|Human/nu mou/moogle Geomancy|Recovery476 after claimed gift8 (Magic45) and game completion. Original gift and finite encounter templates remain intact.|

## Installed recovery services

`notes/vanilla-equipment-recovery.json` defines services471–476 in the original
512-record mission table. Each requires original cleared-game flag54, its
completed original mission or claimed clan gift listed above and no owned copy. Equipped copies
count as owned. A20-day dispatch costs base10000gil (15000 in Cyril) and has a
30-day cooldown. Success grants exactly one original item, with no bonus AP,
gil or recruit. Original item records, lessons, AP requirements and sources
remain unchanged. No new save bytes or completion flags are allocated.

The shared quest-recovery hooks now admit70 services; original quest rules
407–470 remain unchanged. Full posting caches retain their existing contents.
Acquiring a copy removes stale offers; an acquisition after opening final
confirmation rejects acceptance before payment or member assignment. A gift's
skill threshold alone is not enough: the original gift consumer must have
claimed its reward. The generator authenticates each gift's native item/receipt
identity and retains its original thresholds in the catalog. No new claim bit
is introduced.

Cinquedea and Madu are in Throw/Hurl tier7, limited to levels35–39. That pool
membership alone does not establish repeatable acquisition at every later
progression state. Their recovery preserves the original gift and Catch paths
while providing a late, paid replacement after the original gift was claimed.
Sage Robe's other recorded formation is finite. These services preserve all
original acquisition routes and do not make unclaimed gifts available early.

Recovery implementation evidence on historical candidate1dbb18a2:

- Run `20260916T191813.983597Z`: six assembly prerequisites plus5542 quest
  checks and2217 gear/clan checks pass (834 gear and1383 clan rewards). Native
  original gift claims authorize recovery; high skills or unrelated mission
  completion flags cannot replace the actual receipt.
- Run `20260916T191853.539134Z`: assembly verification and nine targeted player
  consumers pass. Six pub flows provide75 payment/assignment/stale-offer checks;
  three return flows provide105 actual20-day reward/save/Continue checks.
  Sage Robe is collected with every other equipment stack at99; all other
  counts and the original gift receipts are preserved through a cold save.
  All three native description and reward screens were reviewed.
- Static delta against combat5a01c78e accounts for67857 bytes, preserving18
  call destinations and7 equivalent veneers. Existing471–473 player evidence
  below is retained; no unrelated combat or old player-flow rerun.

Earlier services471–473 evidence on9d874955, through declared `Test Expansion.ps1 -Only` entries:

- Run184501 (`20260916T184501.770253Z`): assembly and5542 existing quest checks
  pass; a new gear test stops on an incorrect native field-selector oracle.
- Run184618: all411 gear checks complete, including gate matrices, native
  posting, assignment,20-day countdown, success/failure/cancel and cooldown.
  The run then fails a separate unchanged-clan assertion because it compared
  intentionally relocated item-table literals. Its failed report is retained.
- Run184727: corrected clan-only check passes1383 assertions. Both native
  item-table pointers match installedCA7C4; all375 original item records and
  the selector's executable code remain unchanged. Actual seeded native RNG
  reaches every candidate, including all17 Mythril weapons, at six boundary
  counters spanning the three original reward tiers.
- Run185007:99 assertions pass for all three actual20-day travel, native
  return/reward, normal Save and fresh Continue flows. Original item names and
  icons were visually checked. Inventory, whole roster/AP and gil survive.
- Run185236:75 assertions pass across six actual pub flows, covering each
  successful15000gil payment/assignment and each stale held-copy rejection
  before payment. Native descriptions fit; no charge for browsing.

Pub and return tests use separate deterministic fixtures; this is not one
continuous paid campaign playthrough. The return fixture calls native mission
construction/assignment, then advances all20 days through real travel without
writing timers or outcomes. The new Sage Robe full-stock case closes the
equipment-capacity gap; a second paid recovery remains open. Original
clan-gift424-assertion evidence is retained
because neither that consumer nor its inputs changed.

ROM delta against combat candidate5a01c78e accounts for66825 changed bytes in
recovery content/hooks, preserving18 call destinations and7 equivalent linker
veneers. No unrelated combat suite was rerun for this content change.

## Morpher Souls

Run `20260916T190758.914039Z`, ID `test-vanilla-soul-sources-cached`, passes446
assertions on the unchanged9d874955 candidate. It reuses the hashed cold-world
fixture; native tests take about0.2seconds. All20 capturable species map to the
nine original Soul IDs229–237 and have repeatable-mission or roaming-clan
formation witnesses. That historical audit used the shifted441-row layout;
the current audit covers all442 native IDs and corrects source labels without
changing Capture or its tested species inputs.

Original Capture188 and its consumer code are byte-preserved. Native eligibility,
low-HP accuracy, species-bank selection and application execute without patched
results. Preview grants nothing. Each successful application stores the monster
and grants exactly one correct Soul through the installed inventory API. The
test also disposes an existing Soul through originalCA9E8 and captures another
species in that family, verifying all nine alternate-species recovery paths.

With all20 bank slots occupied, native Capture accuracy correctly becomes zero.
Original bank-confirmation caller5A6D4 invokesCC510 to release one species. For
each of the20 species, the test calls that actual consumer, checks preservation
of every other bank record and owned Soul, disposes its Soul, and recaptures the
same species. Its original bank record and exactly one Soul return. There is
no one-time Soul grant flag requiring a new recovery mission.

CC510 deliberately leaves byte+4 while clearing the name pointer and all other
record bytes; native occupancy reads that pointer. The first release test
run190725 incorrectly expected every byte zero and failed before recapture.
Its failed log is retained. Correcting that oracle produced the446-check pass;
no game change was made. Earlier run190549 passed284 pre-release checks.

These use declared original species metadata on fixture units and native
consumers. They do not claim a rendered Capture battle, release-menu input,
cold save, or a complete campaign. The subsequent native roaming audit closes
repeatable encounter availability for all20 species, including generation,
map selection, expiry and battle-return regeneration. Soul supply needs no
added content. Full campaign and rendered Capture/menu/save acceptance remain
separate from these controlled native consumers.

## Remaining source decisions

Run `20260916T191415.128333Z`, ID `test-vanilla-rare-theft-cached`, passed137
native checks on9d874955 using15 actual repeatable-source loadouts. Fourteen
grant the expected rare equipment through original Steal Weapon/Steal Armor
admission, accuracy, real hit RNG and application. Preview is pure; successful
theft depletes only the correct target slot and awards exactly one correct item.
The fifteenth, Wygar in native formation196 (historically labeled194), has actual Maintenance and correctly
returns zero chance. Every one of the five reviewed items has another admitted
witness. Template job, equipment, mastery and assigned reactions/supports are
retained; ordinary level/stats/position are declared fixture inputs. This is
native consumer evidence, not full encounter construction or battle playback.

The [native encounter audit](repeatable-encounter-access.md) now establishes
renewable availability for all five theft items and all20 Soul species. It
corrects the earlier Oathbow attribution from Blue Geniuses108 to Brown
Rabbits109; the original tested unit template and theft consumer are unchanged.
No additional recovery content is needed for these sources. A04/I10 remain
open for general shop/random-mission eligibility reconciliation and a second
paid recovery acceptance. Preserve original character requirements; never
repurpose dismissal missions384–387.

## Native provenance

- Equipment: biased base51D180, IDs1–375,32 bytes each. Teaching index at+29;
  original teaching sets520080,225x20; pairs at+2; race bank pointers51BA84.
- Ordinary shop tiers use item+12 bits4–6. Town stock starts townRecord+4
  and is indexed by at most30 liberated territories, not the entire96-byte
  town record. Actual inventory-menu implementation retains these consumers.
- Mission pools529494: originalFFF1–FFF7 rewards select seven20-item lists.
  FFFF separately selects5295AC; no original mission record usesFFFF.
- Roaming-clan rewardD2114, reached by native caller47B46, uses counter02001F6C:
  masks90/A0/C0 for counters0–10/11–20/21+. Item+12 bit7 admits all17 Mythril
  weapons at every tier. Seeded native RNG2804 selects the actual candidate;
  this proves selector eligibility, not17 complete battle playbacks.
- Clan rewards528256:64x12, final empty sentinel. Byte0 index, unaligned
  u16+1 item, byte3 quantity, eight level requirements at+4. Function46910
  checks levels020021B6+2*skill and permanently records claimed bits02002C08.
  Its item output does not imply successful inventory acceptance.
- Throw/Hurl pools5295D4:10x20u16. D2F78 indexes floor(level/5), capped at9;
  actual callersC2778/C2784 select actions148/211. A pool member does not
  establish a renewable enemy, usable Catch or completed acquisition.
- Native formations: IDs1..442 at54CD54+40*ID, count+0, unit pointer+4. Templates
  span52A4D0..54BB30,48 bytes each; one formation has13 members. Do not reuse
  the older audit's narrower530000..540000 range as an exhaustive bound.

## External leads

Consulted September16. These guides supply acquisition leads, while native
IDs, claim flags and runtime behavior above come from the local ROM audit.
The [Thieves Guild guide](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/27821)
describes hidden item inventories and repeated stealing opportunities.
[Dev's guide](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/25637)
lists the relevant clan-skill gifts; the independently decoded native table
confirms their exact thresholds.
The [GameSpot walkthrough](https://www.gamespot.com/articles/final-fantasy-tactics-advance-walkthrough/1100-6072833/)
identifies treasure-layout and rare-steal alternatives. Do not translate its
displayed quest numbers directly into native record offsets.

## Original source gates reconciled

The native source audit is documented in [original source gates](original-source-gates.md).
It closes the109 shop and70 random-mission classifications under their declared
original eligibility inputs without new recovery content. Real campaign
progression, collection screens and second paid recovery are separate remaining
acceptance obligations. No full integration suite was rerun.

## Continuous second payment accepted

[Paid recovery cycle](paid-recovery-cycle.md) closes the gap left by the separate
pub/return fixtures above: the same candidate now has one continuous actual
payment/return, sale, cooldown, second payment/return and cold Save/Continue
chain for Materia Blade. All six routes retain their earlier native and player
coverage; the shared repeat transaction was not redundantly repeated six times.
The historical statements about second-payment gaps describe those earlier
checkpoints, not this accepted continuation. Final campaign/release acceptance
and quest-item repeat transactions remain distinct.
