# FFTA vanilla+ foundation

Revision 1 — approved September 14, 2026. Implementation has begun in a separate experimental ROM; see [implementation status](IMPLEMENTATION-STATUS.md) for installed features, checks and unfinished work. The approved scope below is unchanged.

The user approved the first recommended package: completion safeguards, rare-equipment recovery, clan sorting, Morpher visuals, and small menu improvements. This accompanies [job design 0.7](JOB-CLASS-SPECIFICATION.md) and [equipment acquisition revision 1](WEAPON-ACQUISITION.md); it does not change their abilities, AP costs, growths, job prerequisites, prices, or teaching-item placements.

Our new jobs provide the main expansion. This foundation preserves the original campaign and makes its content easier to retain, organize, and revisit. Borrow selected ideas and integrate them into our own build; installing an existing overhaul or an entire engine-hack collection is not part of this approval.

## Approved features

| ID | Feature | Adopted behavior |
|---|---|---|
| VP-01 | Mission-item safeguards | Preserve mission requirements and quest chains. Refund or provide a recovery route for an important mission item when its consumption or disposal would otherwise permanently block later content. |
| VP-02 | Monster-ability access | Every vanilla learnable monster ability must retain a repeatable encounter source after its original opportunity. Preserve the normal learning requirements. |
| VP-03 | Secret-recruit retries | Provide another opportunity after a failed or missed secret-recruit chance, once the original eligibility requirements have been met. Do not grant the character automatically or duplicate an existing unique recruit. |
| VP-04 | Rare-equipment recovery | Give otherwise permanently missable vanilla teaching equipment an appropriate late-game recovery mission. Retain the original source, equipment stats, abilities, and AP requirements. |
| VP-05 | Manual clan sorting | Let the player arrange the clan roster in a preferred order without changing units, their progression, or their relationships to missions and story events. |
| VP-06 | Visible Morpher transformation | Show the appropriate monster form when a Morpher transforms. Preserve the existing capture, monster-bank, soul, ability, and combat rules. |
| VP-07 | Small menu improvements | Place Missions first in the pub menu while retaining access to the other options. Ensure the expanded ability and equipment displays accurately show lesson ownership, usability, mastery, and AP. |

The display work in VP-07 supports our expansion; it is not a claim that all those displays are broken in the original game. Further interface features are outside this revision.

## Completion safeguards and recovery rules

### Mission items

Use the Minor Tweak Pack's Wyrmstone refund in **A Dragon's Aid** and Elda's Cup refund in **Caravan Guard** as the first two concrete cases to verify and implement. Audit the remaining vanilla mission-item dependencies for the same failure pattern.

For each affected item, record the consuming mission, later requirement, existing reacquisition routes, and intended refund or recovery route. Items with an adequate repeatable vanilla source do not need a new route merely because they are used in a quest. Keep ordinary quest-item costs meaningful. Verify refund behavior when inventory is full, so a safeguard cannot silently discard the returned item.

### Monster abilities and secret recruits

The starting encounter targets are **Goblin in Tricky Spirits** and **Thundrake in Wild Monsters**, following the Minor Tweak Pack. Verify the relevant abilities and that these encounters remain available at the stage where they are needed; audit other ability sources before claiming complete coverage. Use small formation edits that preserve each encounter's character and difficulty.

For secret recruitment, begin with the pack's additional opportunity through **Mythril Rush** corresponding to **Missing Prof.** Preserve the original character and eligibility conditions. The exact recruit identity, chance, mission flags, and retry behavior must be recorded from the original data before implementation. This approval is for retry access, not a blanket increase in recruitment probability or removal of prerequisites. Recruitment safeguards do not introduce resurrection after permanent death.

### Rare equipment

Audit the pack's examples—**Zeus' Mace, Materia Blade, Dark Gear, and Genji Armor**—along with other permanently missable vanilla teaching equipment. These are audit candidates, not a declaration that every example teaches a unique ability or needs the same recovery treatment. Prioritize access to otherwise lost lessons.

Each approved recovery route must:

1. Preserve the original acquisition opportunity and every relevant story or character prerequisite.
2. Open later than that original opportunity, at an appropriate late-game milestone; do not reuse the new-weapon shop gates automatically.
3. Provide a repeatable way to recover the item if it is lost again, with a suitable mission effort or cost.
4. Work without dismissing a secret character, using a link connection, or depending exclusively on a random drop.
5. Avoid granting duplicate unique characters, resetting the original quest, or changing unrelated mission rewards.

Prefer a new recovery mission or a carefully selected repeatable reward route. Do not overwrite an existing reward needed for another quest. The exact mission names, unlock flags, rewards, and repeat costs remain implementation-planning work; no new mission records or ROM capacity have been verified yet.

The [85 new teaching weapons](WEAPON-ACQUISITION.md) already have approved repeatable shop routes. VP-04 addresses vanilla equipment and does not move those new weapons into mission rewards or revise their prices.

## Interface and presentation rules

**Clan sorting:** Treat this as a change in ordering, not unit identity. Confirm that equipment, learned abilities, dispatch assignments, unique-character events, deployment selection, and saves still refer to the correct character after sorting. Sorting must not grant new deployment privileges to story characters.

**Morpher visuals:** Map each supported morph to its intended appearance and return the unit to its appropriate appearance when the morph ends. Check movement, facing, attacks, casting, damage, defeat, and battle exit. Establish how incompatible or missing animations will display without changing combat behavior. A visual effect must not silently copy monster growths, resistances, or equipment rules.

**Menus:** Put Missions first at the pub; retain rumors and the ability to leave. Show our expanded lessons correctly when scrolling between equipment and switching jobs. Preserve AP learning and combo access. Menu improvements do not authorize changing combat targeting or movement commitment rules.

## Systems retained and proposals not adopted

Keep laws and judges, equipment-based AP mastery, combos, racial access, the original starting party, the campaign's original progression, and vanilla growth rules. Targeted completion edits above are the exceptions to unchanged mission data.

This revision does **not** adopt a general vanilla-ability rebalance, extra clan challenges, boss rematches, an optional tutorial skip, deterministic growths, JP ability purchasing, movement skills replacing combos, or law removal. The proposed weak-ability pass and optional challenges remain possible later work after playtesting.

Do not enable Leonarth's movement-confirmation option as a convenience change: its documented behavior also restricts undoing movement after confirmation. Leave the existing movement behavior intact.

## Integration and verification

This is the approved scope; the experimental patch implements only part of it. Integration and release requirements remain:

- Create a case-by-case recovery ledger with original mission/item/encounter identifiers, eligibility conditions, exact replacement or added data, and evidence for each lockout.
- Check dependencies and capacity in the chosen engine implementation. Leonarth's collection requires its job/race customization infrastructure; individual feature switches do not mean every feature is independent.
- Keep JP purchase, one-bit ability storage that removes AP, combo replacement, quick start, and law removal disabled. Validate preservation of AP and combos in the actual build rather than assuming the collection's defaults match our design.
- Validate recovery both at the original opportunity and after missing it, including full inventories, unavailable recruits, repeated claims, and save/reload behavior.
- Validate roster identity after sorting and all supported Morpher visuals in battle. Confirm accurate menu data for both vanilla and new jobs.
- Recheck all 129 approved lessons and 85 teaching-item placements. Keep the clean and vanilla playing ROMs untouched; the eventual expansion receives a separate output and save.

## Sources and adaptations

Sources were inspected during the preceding recommendation pass on September 14, 2026. Feature availability in source is not evidence of successful integration into this project.

- [Chronosplit: FFTA Minor Tweak Pack](https://romhackplaza.org/romhacks/ffta-minor-tweak-pack-game-boy-advance/) documents the two mission-item refunds, extra recruit opportunity, Goblin/Thundrake additions, and alternate equipment rewards. Its equipment rewards use missions associated with dismissing secret characters; our approved recovery design deliberately uses routes that do not require dismissal. The complete dependency audit and recovery ledger are our additional design work.
- [Leonarth: FFTA Engine Hacks](https://github.com/LeonarthCG/FFTA_Engine_Hacks) documents manual sorting, Morpher appearance changes, expanded ability-list fixes, and the required job/race infrastructure.
- [Leonarth: build configuration](https://github.com/LeonarthCG/FFTA_Engine_Hacks/blob/master/ROM%20Buildfile.event) documents pub-option ordering, feature switches, tutorial skipping, and the movement-undo restriction. Our package selects only the approved features above.
