# Command expansion council: utility jobs

> Historical review of 0.6. The user subsequently approved all seven candidates as 0.7; [the adopted council record](../ABILITY-EXPANSION-COUNCIL.md) and current specification supersede the proposal-status wording below.


September 14, 2026. Independent review against approved design 0.6. These are candidates for user review, not adopted abilities. No canonical tables, AP totals, teaching items, or ROM records change through this report. All new mechanics and numbers below are original design proposals unless explicitly identified as source-game facts.

## Recommendation

| Priority | Job | Addition | Suggested command total if accepted |
|---|---|---|---:|
| 1 | Dancer | Passing Step: strike and reposition | 9 |
| 2 | Chemist, both races | Guarding Draught: inventory-funded protection before damage | 9 |
| 3 | Chemist, both races | Inoculation: prevent a specified class of ailments before they arrive | 10 with both mixtures |
| 4, conditional | Geomancer | Nature's Refuge: stationary magical shelter competing with Rime Field | 9 |
| No addition recommended | Bard | Current song kit already covers its principal role | 8 |

These counts are consequences of distinct functions. No job needs to match Mystic Knight's fourteen. The first two additions offer the clearest ordinary-turn gains; Inoculation is deliberately encounter-dependent, and Refuge needs a field-system prototype before committing to its precise rules.

## Dancer: Passing Step

**Gap:** Existing Dancer is an effective debuffer but its actions do not themselves move the performer. Light Foot helps ordinary movement; it does not provide an active choice between commitment and disengagement. Another status dance adds less identity than a movement technique.

**Inspiration:** FFXIV Dancer's En Avant is an explicit forward dash and cannot be used while bound. The official job description ties performance to martial discipline. Passing Step's attack, costs, paths, and turn behavior are our adaptation, not an existing XIV ability. [Official Dancer guide](https://na.finalfantasyxiv.com/jobguide/dancer/).

**Provisional rules after cross-review:** 250 AP, 6 MP; r1 one enemy, A; weapon-free, 0.95 Pdance non-elemental physical damage. After the strike and its immediate reaction finish, a surviving actor able to move may take an optional path costing at most two of the movement points left from its ordinary turn allowance. Deduct actual voluntary movement already taken this turn: it grants no new movement points. Completing this step ends the ordinary Move opportunity; there is no further Move command or reset. This happens on hit or miss, not only after damage. Use ordinary movement costs, height, occupancy, field, trap, and terrain restrictions. Cannot pass through an enemy or end on an occupied/illegal tile. Immobilize prevents the movement but not the strike; KO/Petrify prevents it. The step itself is capped at two even when Light Foot or Updraft increased the original allowance. It works while Silenced, is not Doublecast, and counts as Physical for Spellweave.

This explicitly proposes a narrow exception to the current shared sentence forbidding immediate movement. It buys a split movement sequence, not extra movement. Adoption must amend that shared rule and implement tracking of spent movement; it is not already permitted by 0.6. If the engine cannot safely track remaining movement, defer this candidate instead of silently giving two bonus tiles.

The movement destination should be previewed before commitment. If an intervening reaction makes that route invalid, cancel movement rather than teleporting or choosing a different route without input. If reaction scheduling cannot support post-strike movement safely, keep the concept pending; do not silently move the actor before an enemy's reaction to evade it.

**Normal turn:** A Move-4 Dancer advances two movement points, lands the modest strike, then spends its remaining two to step behind an ally. Sword Dance is still the damage commitment, and ranged debuff dances remain safer if the enemy is too dangerous to approach. A Dancer that already used all four points gets only the strike. Starting adjacent without moving provides no advantage over an ordinary attack-then-Move sequence; this is a specialized approach-and-retreat action.

**Legal mixing:** Fencer/Dance can choose Passing Step for repositioning or a Lunge technique for its other effects. Assassin/Dance can use this weapon-free action with its normal weapons, but a weak melee hit plus two movement points costs the same action that could have used its stronger control. Red Mage/Dance alternates an original spell with Passing Step under Spellweave, but cannot Doublecast the dance. Sword Dance retains its knife/rapier restriction.

**Risks and counterplay:** Splitting movement on an already fast race warrants checks against objectives and hit-and-run play. Enemy counterattacks occur before retreat, Immobilize stops the retreat, and paid terrain costs shorten it. At level 25 the existing virtual weapon value is 27, so it does not borrow the equipped weapon's superior power. Concentrate and Fury may improve the strike but do not grant more movement. Movement under applicable laws must remain visible and judged; the physical strike is not a free Fight or a hidden spell. The reduced damage/MP targets reflect its smaller benefit after the remaining-budget restriction; do not retain the earlier 0.85/10 MP draft automatically.

**Reject for now:** A generic full-party heal overlaps White Magic already available to Viera; Curing Waltz has authentic XIV precedent but is not the most important missing decision here. A partner system that duplicates actions or buffs risks making one high-output ally mandatory. Pure extra-turn dances collide with the agreed no-turn-reset rule. Do not add these just to reach ten.

## Chemist: Guarding Draught

**Gap:** Every current action repairs damage, resource depletion, death, or an existing ailment. There is no medicine to administer proactively when allies are healthy. This also makes the command especially dependent on the current encounter creating a problem after the Chemist's turn.

**Inspiration:** FFV Mix includes Protect Potion, which provides Protect and Shell, alongside other defensive and resistance mixtures. Its original recipe is not ours; FFTA is not gaining Turtle Shell or Dragon Fang inventory. [FFV Mix reference](https://finalfantasy.fandom.com/wiki/Mix_(Final_Fantasy_V)).

**Provisional rules:** 200 AP; consume one Potion and one Soft, 0 MP; r4 one non-undead ally or self, Sure, ordinary projectile LOS/height. Apply ordinary Protect and Shell together; no extra damage multiplier, healing, Regen, Haste, or Reflect. Use the ordinary vanilla duration/removal rules for those statuses. Recipes validate both ingredients before consuming either. Weapon-free; works during Silence; no Reflect, Return Magic, or Doublecast. Long Throw extends eligible range to five; Pharmacology adds nothing to buffs.

Potion plus Soft is an original preparation using an existing restorative and mineral-affliction treatment. The presentation should describe a fortifying mixture, not assert a chemical explanation or claim Soft canonically grants armor. Confirm actual Soft availability before choosing the teaching tier. If its real availability makes this effectively unrestricted and too cheap, adjust the recipe after inventory testing rather than assume scarcity balances it.

**Normal turn:** A healthy frontliner is about to face physical and magical pressure. One Chemist action protects it now, giving medicine a job before someone is injured. If that frontliner already has Protect and Shell, the mix has no added value beyond ordinary refresh behavior; choose another action.

**Legal mixing:** Moogle Juggler/Items chooses the paid defensive preparation instead of Smile. Nu Mou Sage/Items gains silence-resistant proactive support without changing its own equipment. Alchemist/Items must still justify spending its secondary slot on mixtures over Sagacity: fixed ordinary Item already handles basic items. Moogle users can equip Encouragement for the separate bounded heal on a newly applied beneficial status, but cannot equip Pharmacology simultaneously. Nu Mou cannot learn Bard's Encouragement merely by choosing Chemist.

**Risks and counterplay:** Dispel removes protection, and finite inventory/gil matter across missions even when an individual use is cheap. Original Protect/Shell are not new multiplicative copies, so Bard, Samurai, and White Magic cannot stack a second instance. Damage reduction comparisons must use actual vanilla formulas. Repeated casts on one recipient do not repeatedly qualify Encouragement while either relevant status is merely refreshed. Item-use and other applicable laws must continue to apply; being MP-free does not make the action law-free.

## Chemist: Inoculation

**Gap:** Auto-Cureall provides reactive prevention only on the unit equipping that reaction and spends a Cureall per intercepted enemy action. A learned medicine can instead let the Chemist protect an important ally before a status-focused attack, freeing that ally's reaction slot.

**Inspiration:** FFV's mixing list contains status-immunity preparations, including Resist Poison. The following broad preventive treatment and recipe are our invention. They are not a port of that recipe or a claim that ordinary FFTA Cureall grants immunity. [FFV Mix reference](https://finalfantasy.fandom.com/wiki/Mix_(Final_Fantasy_V)).

**Provisional rules:** 300 AP; one Potion and one Cureall, 0 MP; r4 one non-undead ally/self, Sure, ordinary projectile LOS/height. Apply a dispellable Inoculated status T2. While present, block incoming enemy applications of the same curable ailments recognized by current Cureall/Auto-Cureall, including only the custom harmful effects explicitly integrated there. Existing ailments are not removed. No KO immunity, no protection against an uncurable effect, no prevention of self-paid costs or allied sacrifice, and no stripping a drawback while retaining its paired benefit. Does not alter HP damage, accuracy, theft, displacement, or turn-order effects. No stacking; refresh resets the ordinary T2 timer. Weapon-free and usable while Silenced. Long Throw eligible; Pharmacology does not improve duration or coverage.

**Normal turn:** Before a cluster of enemies can apply disabling conditions, administer the mixture to a key ally. That spends a real turn and scarce Cureall in advance. If enemies attack a different unit or use ordinary damage instead, the preventive investment may do little. Use current Cureall rather than Inoculation when the ally already needs cleansing.

**Legal mixing:** A Moogle Time Mage/Items can maintain prevention or use Time Magic, not both on one turn. A Nu Mou Beastmaster/Items provides medicine without needing a restorative spell set, but still has only two learned commands. A recipient may be any legal allied race; that does not transfer the recipe lesson to that race. Moogle Encouragement can trigger its one bounded heal on first application to another ally, never self or simple refresh. No automatic extra reaction is granted.

**Risks and counterplay:** Cureall supply is explicitly finite and progression-dependent; do not add shop stock as a hidden balancing assumption. Long status immunity can neutralize selected encounters, so T2, dispellability, single-target scope, and actual acquisition timing must be tested. Clarify interception order: Inoculated should prevent the eligible ailment before Auto-Cureall considers spending another item. Its duration must expire using recipient turns exactly like other T2 effects. Verify status pressure under Haste/Slow, multi-ailment attacks, reaction-blocking conditions, and custom debuffs. Inoculation is a prospective prevention buff, not a new cure-all loophole.

**Reject for now:** A routine Potion-to-MP recipe would bypass the existing intentional Ether scarcity and compete with Bard's turn-funded Ballad. Inventory duplication, permanent level/HP enhancement, and FFV-style unrestricted absorption are poor fits. Additional Potion tiers add menu size without decisions. An offensive flask is possible in Chemist's broad tradition, but antidotes becoming universal poison bombs need stronger thematic and role justification than these medical preparations.

### Cross-review: Dark Knight's proposed ally ward

The martial council's Blackest Night spends HP and MP for strong protection against one enemy damage action; Guarding Draught consumes inventory for ordinary persistent Protect/Shell, while Inoculation prevents eligible ailments and does nothing against HP damage. They are different preventive choices rather than three copies. Blackest Night stacks with ordinary Protect/Shell once under the real defense formulas; do not add a second custom protection layer to Guarding Draught to compete with it. Neither mixture restores HP by itself, Poise does not amplify their benefits, and Dark Knight's HP costs cannot be prevented by Inoculation. A Moogle Chemist with Encouragement can supply its existing bounded heal on first application to a Human/Bangaa beneficiary, which might move that beneficiary above Desperation's threshold; that is a tradeoff, not a free low-HP sustain loop. Keep the ally action and consumed items in comparisons. Pharmacology and Encouragement compete for the same support slot.

## Geomancer: Nature's Refuge, conditional

**Gap:** Rime Field creates one persistent hostile zone, but the player cannot choose a contrasting field use. Earthen Ward grants mobile physical protection; it does not create a place allies want to hold. A shelter makes positioning a Geomancy decision rather than another damage element or chance ailment.

**Inspiration:** Square Enix describes FFXI Geomancer as using the world's geomantic energies both to aid companions and harm enemies. That supports the role; it does not establish this particular field or its formula. Nature's Refuge is our original earth-spirit shelter. [Official Seekers of Adoulin manual, page 6](https://support.na.square-enix.com/document/manual/20/FFXI_SeekersOfAdoulin_PC.pdf).

**Provisional rules:** 300 AP, 12 MP; r3 center/cross legal map tiles. Place a Refuge in the same persistent-field slot used by Rime: either cast replaces that caster's prior field. Use Rime's two-subsequent-caster-turn expiry and removal on caster KO/Petrify/job change/battle end. At each incoming action's start, allied grounded occupants receive magical direct HP damage ×0.80 for that action. No status is attached to occupants; leaving loses shelter for future actions. No entry heal, damage, extra move cost, physical defense, status immunity, resource gain, or affinity changes. Multiple Refuges do not stack. Works on ordinary legal dry ground without requiring affinity; unknown terrain does not disable it. As Geomancy it is weapon-free and Silence-independent. Float/flying occupants are not connected to this earth shelter.

**Normal turn:** The Geomancer places a shelter over two allies before an enemy mage acts. They may remain to receive the reduction or leave to gain better range. On the next turn, the caster can keep that location active while using another command, or sacrifice it by laying Rime in the enemy's approach.

**Legal mixing:** Time Mage/Geomancy and Alchemist/Geomancy remain legal. Shelter can protect allies already under ordinary Shell, so its marginal stacking benefit must be tested against the MP/turn/positioning cost. Existing Updraft's Float deliberately conflicts with this grounded shelter: use mobility or earth protection, rather than automatically receive both. No Bard Encouragement proc from occupying or re-entering the field, as current rules already exclude occupancy.

**Risks and counterplay:** This is the highest implementation-risk candidate. We need reliable field occupancy, ground/Float checks, effect previews, overlapping casters, and AI understanding. Shared incoming-action snapshot prevents mixed resolution if an action moves a unit before dealing later damage. Leaving, being pushed out, caster defeat, physical attacks, status attacks, and expiry counter it. An area magic attack may still profitably hit clustered occupants: the 20% reduction is not immunity. Do not add independent affinities, healing pulses, or custom walls simultaneously. If the field system cannot implement cleanly, leave Geomancer at eight; no replacement filler is needed.

**Reject for now:** Another earth/water AoE overlaps Stone Pulse/Torrent/Gaia Surge. New terrain that blocks all paths has large AI and softlock risks. Party healing or MP springs would blur White Magic, Chemist, and Bard roles and could create repeated-entry or waiting recovery exploits. Terrain must remain a bonus, not a permission gate.

## Bard: keep eight for this pass

Bard already has a strong spread: healing/cleansing, physical and magical group enhancement, targeted MP support, regeneration, a combined defensive song, undead offense, and personal concealment. Juggler/Song and Time Mage/Song already have substantial action competition. Filling its lack of universal offensive damage is not obligatory; that is a reason to choose a secondary command.

Warden's Paean is authentic inspiration: XIV's version removes a selected detrimental effect or protects against the next one when no cleanse is needed. [Official Bard guide](https://na.finalfantasyxiv.com/jobguide/bard/). I would defer our own version because Soul Etude already combines useful cleansing with healing, and preventive medicine is a stronger missing identity for Chemist. The two Moogle additions would otherwise chase the same niche immediately.

Likewise, a general Sleep song is thematically plausible but would broaden Bard into control without an urgent gap; group Haste or action replay revives the most dangerous action-economy concern in the previous council. More direct damage would be convenient but not inherently interesting. Retaining eight is an affirmative design recommendation, not a claim that Bard may never expand.

## Adoption and testing conditions

If accepted, each candidate needs an individual stable ID and teaching lesson at an appropriate existing story tier; do not raise the weapon-power ceiling merely to add lessons. Chemist recipes are shared lessons across two racial implementations, not duplicated counts. No additional supports, reactions, growth changes, job gates, or new races are justified by this review.

All candidates inherit shared laws, action payment, legal targets, reaction eligibility, and non-Doublecast handling except the explicit movement/field rules that need new integration. Preview actual inventory expenditure and do not consume partial recipes. Test organic progression and optimized inherited growth. Compare the action with a legal vanilla secondary at the same stage, and count the opportunity cost of not using Smile, Quicken, damage, or existing medicine. No proposed numerical value has been battle-tested.
