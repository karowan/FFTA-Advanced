# Mission-item dependency ledger

September 16, 2026. Static ledger and bounded native posting proof; A01 remains open. Candidate
`ea9ed600d38fb8b3a5662fc1f116852be8b97548`. Reproduce with
`node scripts/audit-mission-item-dependencies.mjs`; complete semantic records
and prerequisite triples are written to ignored
`build/reports/mission-item-dependencies.json`. No game bytes are changed.

The original-source audit covers all512 native table slots, including400 records with posting
bits enabled,88 required quest-item IDs and119 consumed requirement slots. Every required item has at least one direct
mission reward source.24 have a repeatable source that does not directly require
itself;64 have finite or self-dependent sources. Neither category establishes
actual campaign availability: prerequisite flags, calendar windows, link-only
access and indirect dependency cycles still need native evaluation.

The first version used the shared helper's0..405 range and incorrectly split
the pub calendar byte. Native CFCD0 actually iterates1..511; slot406 has content,
and disabled test slots497..507 are not ordinary reward sources. The revised
audit includes every slot but excludes disabled records from source claims.
No shared build helper or production image is changed by this correction.

Native posting predicates at CFD00..CFF40 require nonzero record+3 bits4..6,
no matching cached posting among64 slots, incomplete-or-repeatable state,
matching month (record+0x0E low3 bits;0 means unrestricted), placed event location
when present, and all three prerequisite clauses. A clause's16-bit selector
below0x600 reads a flag: value0 requires clear,1 requires set, other values
impose no constraint. Selectors0x600 and above read native byte counters and
require at least the declared value. Record text ID383 additionally requires
flags600..604 clear. Native CFFA0 packs duration from record+0x0E high5 bits
and record+0x0F low3 bits; zero becomes255 in the cached posting. These gates
precede construction, category queue insertion and the separate acceptance UI.

Native CF118 atCF18A..CF1CA reads required slot1 at record+36 and consumes it
only on successful completion when record+41 bit4 is set. CF1CA..CF20C uses
slot2 at+37 and bit5. Both opcode masks are asserted by the audit. A requirement
without its consumption bit is retained. Quest local IDs become global reward
IDs by adding375; keep this namespace distinct from expanded equipment.

The original A Dragon's Aid69 requirement does not consume Wyrmstone22. Its
installed extra reward is a spare. Caravan Guard183 consumes Elda's Cup4 and
now returns a copy. Both added sources require the same item, so neither can
recover a copy discarded before entry. Their full-inventory observations are
in `mission-refund-in-game-review.md`; Caravan Guard now also has actual
20-day native travel/return and full-bag reward evidence there.

Most finite multi-consumer items have matching finite supply counts, so the
graph alone does not justify refunding every consumption. Preserve intentional
crafting/trade costs. A recovery should require the original opportunity to
have been earned and a still-uncompleted dependent mission; it must not supply
future quest items early. Disposal, failed offers and genuinely exhausted
supply require distinct eligibility checks. This is an implementation constraint,
the contract now implemented by the 64 earned-supply recovery routes. Their
posting, text, queue pruning and acceptance/completion boundaries have focused
evidence; native assignment, cancellation and five-day success/failure retirement pass.
Actual recovery pub payment, five-day world return, reward collection/full-bag
rejection, cold saves and post-cooldown pub availability now pass. Remaining
campaign/indirect-source obligations and exact test scope are recorded in
`mission-item-recovery-implementation.md`.

All numbers below are native record indices, not displayed mission numbers.
The generated report retains names and decoded unlock clauses for each edge. This retained table describes the pre-recovery source ledger (candidate 5a01c78e),
not all current sources. The current generated catalog adds one conditional
recovery service for each of the 64 finite candidates. Those services are not
independent renewable supply: they require previously earned, unspent copies.

| Local item | Name | Required by | Consumed by | Original reward sources | Installed independent repeatable sources | Added source |
|---|---|---|---|---|---|---|
| 4 | Elda's Cup | 183 | 183 | 138 | - | 183 |
| 6 | Gold Vessel | 332, 334 | - | 326, 327 | - | - |
| 7 | Magic Medal | 288 | 288 | 214, 238 | - | - |
| 8 | Ancient Medal | 158, 198 | 158, 198 | 216, 217 | 217 | - |
| 14 | Rainbowite | 301 | 301 | 141 | - | - |
| 15 | Delta Fang | 175 | 175 | 81 | - | - |
| 16 | Cat's Tears | 164 | 164 | 142 | - | - |
| 17 | Dame's Blush | 177 | 177 | 143 | - | - |
| 18 | Thunderstone | 303 | 303 | 144 | - | - |
| 19 | Stormstone | 303 | 303 | 145 | - | - |
| 21 | Ahriman Eye | 53 | - | 128 | - | - |
| 22 | Wyrmstone | 69 | - | 34 | - | 69 |
| 24 | Zodiac Ore | 103, 148, 201 | 103, 148, 201 | 218 | 218 | - |
| 25 | Silvril | 147, 200 | 147, 200 | 111, 219 | 111, 219 | - |
| 26 | Materite | 313 | 313 | 220 | 220 | - |
| 27 | Leestone | 305 | 305 | 221 | 221 | - |
| 28 | Adamantite | 146, 147, 199, 200 | 146, 147, 199, 200 | 222 | 222 | - |
| 29 | Spiritstone | 85, 101 | 101 | 213 | 213 | - |
| 31 | Adaman Alloy | 300, 312 | 300, 312 | 146, 199 | - | - |
| 32 | Mysidia Alloy | 102, 307 | 102, 307 | 147, 200 | - | - |
| 33 | Crusite Alloy | 302, 309 | 302, 309 | 148, 201 | - | - |
| 35 | Black Thread | 181, 308, 310 | 181, 308, 310 | 223, 224, 225 | - | - |
| 36 | White Thread | 214, 311 | 214, 311 | 226, 227, 228 | - | - |
| 37 | Chocobo Skin | 314, 315 | 314, 315 | 113, 229 | 229 | - |
| 38 | Magic Cloth | 310, 311 | 310, 311 | 230, 231 | 231 | - |
| 39 | Magic Cotton | 231, 246, 314, 315 | 231, 246, 314, 315 | 232 | 232 | - |
| 40 | Blood Shawl | 297 | 297 | 149 | - | - |
| 41 | Ahriman Wing | 156 | 156 | 150 | - | - |
| 42 | Fairy Wing | 150 | 150 | 151 | - | - |
| 43 | Bomb Shell | 170, 185 | 170, 185 | 233, 234 | - | - |
| 46 | Jerky | 282, 284 | 282, 284 | 236 | 236 | - |
| 47 | Gysahl Greens | 243 | 243 | 237 | 237 | - |
| 48 | Chocobo Egg | 240, 243 | 240, 243 | 215, 239 | 215 | - |
| 49 | Goldcap | 195 | 195 | 152 | - | - |
| 50 | Life Water | 189 | 189 | 153 | - | - |
| 51 | Eldagusto | 332, 333 | - | 328, 329 | - | - |
| 53 | Choco Bread | 244, 249 | 244, 249 | 241 | 241 | - |
| 54 | Choco Gratin | 283, 298 | 283, 298 | 242, 243 | - | - |
| 55 | Kiddy Bread | 291 | 291 | 249 | - | - |
| 56 | Grownup Bread | 291 | 291 | 244 | - | - |
| 57 | Malboro Wine | 294 | 294 | 245 | - | - |
| 63 | Runba's Tale | 171, 172 | 171, 172 | 247, 248 | - | - |
| 66 | Homework | 225 | 225 | 158 | - | - |
| 68 | Dictionary | 190 | 190 | 159 | - | - |
| 69 | Monster Guide | 234 | 234 | 160 | - | - |
| 70 | Secret Books | 153 | 153 | 161 | - | - |
| 72 | Stuffed Bear | 383 | - | 379 | - | - |
| 73 | Rat Tail | 206, 312 | 206, 312 | 162, 202 | - | - |
| 74 | Rabbit Tail | 71, 285 | 71, 285 | 251 | 251 | - |
| 75 | Danbukwood | 293 | 293 | 252 | 252 | - |
| 76 | Moonwood | 293 | 293 | 253 | 253 | - |
| 77 | Stradivari | 308 | 308 | 163 | - | - |
| 78 | Clock Post | 196 | 196 | 164 | - | - |
| 82 | Old Statue | 178 | 178 | 168 | - | - |
| 83 | Neighbor Pin | 155 | 155 | 169 | - | - |
| 85 | Rusty Sword | 102, 305 | 102, 305 | 170, 203 | - | - |
| 86 | Broken Sword | 300, 304 | 300, 304 | 171, 204 | - | - |
| 87 | Bent Sword | 101, 301 | 101, 301 | 172, 205 | - | - |
| 88 | Rusty Spear | 99, 307 | 99, 307 | 173, 206 | - | - |
| 89 | Fire Sigil | 211 | 211 | 80, 131 | 131 | - |
| 90 | Water Sigil | 212 | 212 | 82, 132 | 132 | - |
| 91 | Wind Sigil | 211 | 211 | 83, 133 | 133 | - |
| 92 | Earth Sigil | 212 | 212 | 84, 134 | 134 | - |
| 93 | Mind Ceffyl | 213 | 213 | 211 | 211 | - |
| 94 | Body Ceffyl | 213 | 213 | 212 | 212 | - |
| 95 | Feather Badge | 175 | 175 | 174 | - | - |
| 96 | Insignia | 299 | 299 | 175, 207 | - | - |
| 97 | Ally Finder | 177 | 177 | 176 | - | - |
| 98 | Ally Finder2 | 299 | 299 | 71, 177 | - | - |
| 99 | Tranquil Box | 157 | 157 | 178 | - | - |
| 102 | Stasis Rope | 247 | 247 | 181 | - | - |
| 103 | Mythril Pick | 160 | 160 | 182 | - | - |
| 104 | Caravan Musk | 188 | 188 | 183 | - | - |
| 106 | Tonberry Lamp | 163 | 163 | 185 | - | - |
| 107 | Stilpool Scroll | 161 | 161 | 186 | - | - |
| 108 | Flower Vase | 54 | 54 | 28 | - | - |
| 109 | Dragon Bone | 138 | 138 | 187 | - | - |
| 110 | Animal Bone | 168 | 168 | 188 | - | - |
| 111 | Skull | 143 | 143 | 189 | - | - |
| 112 | Helje Key | 67 | 67 | 60 | 60 | - |
| 113 | Clock Gear | 196 | 196 | 190 | - | - |
| 114 | Gun Gear | 309 | 309 | 191 | - | - |
| 116 | Silk Bloom | 306 | 306 | 192 | - | - |
| 117 | Moon Bloom | 306 | 306 | 193 | - | - |
| 121 | Blood Apple | 103, 302 | 103, 302 | 194, 208 | - | - |
| 124 | Vermillion | 333, 334 | - | 330, 331 | - | - |
| 125 | Stolen Gil | 151 | 151 | 197 | - | - |
| 126 | Ancient Bills | 152 | 152 | 198 | - | - |

## Next implementation evidence

- Native posting predicates and duration now pass6,943 fixed cases in run
  `20260916T164254.225660Z`; all three selected steps passed with unchanged
  inputs. The installed candidate remains5a01c78e. The test includes511 real
  records, five calendar months, individual clause failures, completion, the
  last cached slot, missing locations, five special exclusions and120 boundary
  clause cases. Scope: pre-construction decisions, not a whole pub/campaign.
- Check queue insertion, acceptance and post-opportunity availability for all24
  repeatable-source candidates; preserve the above native gate evidence.
- Reconcile finite supplies against remaining dependent missions, disposal and
  reward rejection. Audit indirect source cycles before choosing recovery cases.
- Reuse original eligibility/completion flags to gate recovery without duplicate
  quest shortcuts; retain original mission rewards and costs.
- Recovery predicates/boundaries are implemented; test full native acceptance, dispatch completion,
  full inventory, repeated claims and save/reload in one coherent content batch.

The earlier run164222 failed its fixture baseline assertion before native
cases because it compared the unused C9574 flag writer as well as readers.
C9574 already has the intentional movement-lifecycle hook. Restricting the
comparison to actual posting readers corrected the test; no game edit occurred.

The current generated audit explicitly separates 24 independent repeatable
source candidates from 64 conditional recovery services. Their original
finite/self-dependent classification remains visible; recovering an earned
copy does not create a new unrestricted supply chain. Current native recovery
and ordinary controls are recorded in `mission-item-recovery-implementation.md`.

## Renewable ingredient closure

`scripts/audit-mission-renewable-chains.mjs` consumes the hash-matched ledger
and builds a fixed-point witness for every original repeatable supply. A recipe
can enter the next layer only after all its ingredients already have proven
repeatable witnesses. This prevents a mutually dependent recipe cycle from
being mislabeled renewable. Conditional recovery services are excluded.

All 24 candidates have an acyclic witness: 20 ingredient-free supplies and
these four recipes, with at most two ingredient layers:

| Output | Repeatable mission | Inputs and renewable source |
|---|---|---|
| Magic Cloth | 231, Magic Cloth | Magic Cotton from 232, Cotton Guard |
| Mind Ceffyl | 211, Mind Ceffyl | Fire Sigil from 131 and Wind Sigil from 133 |
| Body Ceffyl | 212, Body Ceffyl | Earth Sigil from 134 and Water Sigil from 132 |
| Spiritstone | 213, The Spiritstone | Mind Ceffyl and Body Ceffyl above |

The selected witnesses have positive prerequisites and recurring month windows,
with no negative flag clauses or special exclusions. Silvril uses Seeking
Silver219, which does not depend on Mythril Rush's placed location. Helje Key
still requires Sprohm to be placed. The Spiritstone/Ceffyl recipes also require
flag1323, now traced to original pub rumor43 as documented below. Positive
flag tests alone do not prove those flags become reachable naturally.
The existing native posting matrix covers the predicates; this source audit
adds recipe dependency closure, not another runtime or campaign test.

Preserve the original costs and sources: no extra recovery missions are
justified by these four ingredient chains. The report also isolates original
sources with non-mission or negative gates for remaining review. Flags1445/1446
select Shining Lake, Sauce Recipe and Hero Of Yore variants; native ROM0xCEA80
includes RNG-driven writes to those flags. The ordinary name-confirmation
caller is now traced and executed for all four outcomes; these are not
exclusively link-owned flags. Original variant conditions remain intact. See
[original source gates](original-source-gates.md) for86 native naming/offer
checks and575 retained checks covering all24 renewable source lifecycles.
This does not claim all later link consumers were audited.

Reproduce after the main dependency audit with
`node scripts/audit-mission-renewable-chains.mjs`. Full witnesses and unusual
gates are saved in ignored `build/reports/mission-renewable-chains.json`.

## Pub-rumor prerequisites and retirement

The14 rumor-history flags used by original mission prerequisites correspond
to topics31,32,33,34,35,36,38,39,41,42,43,46,47,49. Native D1B80 enumerates
127 eight-byte topic records beginning at ROM5573F4, respecting town, required
and excluded flags/counters. Pub controller5D800 calls it with capacity64;
5D8F8 calls6130C after reading a topic. That acknowledgment sets `0x500 | topicID`
and does not consume a quest item. Topic IDs are not quest-item IDs.

Rumor43 requires flag848 (Free Baguba!, mission81 completed) and disappears
after flag980 (The Spiritstone, mission213 completed). Reading it sets1323.
Its disappearance does not clear history, so the three Ceffyl/Spiritstone
recipes remain repeatable after the first Spiritstone. No extra recovery route
or removal of that original rumor requirement is needed.

`test-mission-rumor-gates-cached` passes130 assertions in
`20260916T181510.811890Z` on ea9ed600. All14 topics use actual enumeration and
acknowledgment, preserve inventory, retain their history on rereading and topic
exclusion, and respect list capacity. The specific Free Baguba→rumor43→recipe
chain runs the complete native mission generator before/after reading and
after Spiritstone completion. No recipe posts before the required rumor;
all three post afterward and retain repeat access. This is controlled native
progression evidence; rendered Rumors-menu playback remains a separate VP-07
interface check. These source/runtime results close1323's provenance question.

## Connected earned history and ingredients

The current1b070824 candidate now passes1,344 targeted checks from authenticated
opening history through34 original story/battle receipts, all four teaching
stages,149 original source/side completions and13 earned rumor acknowledgments.
All24 renewable witnesses now consume actually collected native ingredients;
their later flags and ingredients are not inserted. See
[connected progression](campaign-progression.md) for the exact scope, report
hashes, source/queue handling and remaining scene/placement limitations. This
extends the earlier independent gate/recipe proof without claiming a full
campaign or erasing the remaining V06 milestone work.
