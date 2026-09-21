# FFTA expansion: council balance pass

September 14, 2026 · Review of design 0.4 · Adopted as design 0.5

**The council recommends structural fixes first, stronger conditional choices second, and targeted testing of a few powerful combinations.** Mystic Knight, Chemist, Bard, and Dancer need more than percentage adjustments. Samurai and Geomancer already have coherent foundations. Dark Knight's risk/reward needs a better recovery cycle, while Viking needs distinct storm and plunder tools. Most reactions need dependable activation rather than several layers of failure.

Three independent agents reviewed the martial kits, magic/utility kits, and supports/reactions. The chair reviewed growths, equipment, progression, and legal builds, then ran a second cross-review round and reconciled disagreements. **All 116 existing entries have an individual verdict and concrete parameters:** 72 actions, 18 supports, 18 reactions, and eight combos. Both versions of shared jobs are included in the build and growth analysis.

**The user approved this proposal; it is now adopted in the [current class specification](JOB-CLASS-SPECIFICATION.md), [support sheet](SUPPORT-SKILL-DESIGN.md), [axe addendum](AXE-SKILL-EXPANSION.md), and structured ability data as version 0.5.** This is a completed design balance pass, not a claim of gameplay-tested balance. The ROM is unchanged. Original 0.4 documents are preserved in notes/design-v0.4; individual council reports remain historical review evidence. Current specifications take precedence over historical examples.

**Subsequent approved expansion:** [Version 0.6 Spellblade](SPELLBLADE-EXPANSION.md) adds six actions and clarifies sequence categories. This report preserves the original 116-entry review; the current specification has 122 entries.

## Read the detailed proposals

| Report | Coverage |
|---|---|
| [Martial abilities](../balance-council-martial.md) | Every Samurai, Dark Knight, Viking, Mystic Knight, and axe action; four combo profiles; legal builds and burst calculations. |
| [Magic and utility abilities](../balance-council-magic-utility.md) | Every Geomancer, Chemist, Bard, and Dancer action; four combo profiles; medicine, music, control, and party synergies. |
| [Supports and reactions](../balance-council-supports-reactions.md) | All 36 lessons, exact effects/AP, two legal external-job examples per support, vanilla competition, and adversarial combinations. |
| [Growths, equipment, progression, and test cases](../balance-council-global.md) | All ten growth profiles; weapon restrictions; item availability; action-cost arithmetic; required scenario comparisons. |
| [Coverage and AP ledger](../balance-council-coverage.json) | Machine-checked inventory of all 116 reviewed IDs, report locations, old/new AP, and integrity checks against the preserved 0.4 review baseline. Current-design consistency is checked separately in notes/design-validation.json. This checks coverage, not gameplay balance. |

The research baseline includes [Terence's mechanics guide](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262), the [R/S ability reference](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/39140), and [published optimized-build discussion](https://gamefaqs.gamespot.com/boards/560436-final-fantasy-tactics-advance/57520610). The reports distinguish documented vanilla behavior, our arithmetic, and proposed custom mechanics.

## What changes for each job

| Job | Consolidated direction | Examples of legal mixing |
|---|---|---|
| **Samurai** | Keep attack-and-Centered rhythm. Strengthen Murasame to 35% max HP, cap 140 before Centered; make Guarding Draw's Protect reliable even on a miss; improve the paid ranged finisher. | Ninja/Iaido with katana; Samurai/Hunt; Samurai/White Magic. New techniques still use only one weapon. |
| **Dark Knight** | Stronger sacrifice attacks and useful capped drain; Infernal Strike contributes HP damage while stealing MP; Dark Mind adds healing. Last Resort can make an ordinary-strength commitment strike before applying its linked benefit/drawback. | Human Dark Knight/Blue Magic; Bangaa Dark Knight/Prayer; axe Gladiator/Dark Arts can use weaponless utility and the new Last Resort strike, but not sword-gated drain attacks. |
| **Viking** | Keep cheap precise Thunder and a large Thundaga; replace the redundant middle tier with Stormcall's damage plus Slow. Correct theft handling and give Tsunami displacement on ordinary ground. | Viking/Gladiator for axes and storms; Viking/Bishop for support; Bishop/Reaving uses storms and weaponless utilities but lacks axe theft. |
| **Geomancer** | Retain most of the kit. Make Updraft a group mobility action. Preserve Wisp Exposure's payoff for an allied caster and the optional terrain bonuses. | Time Mage/Geomancy; Alchemist/Geomancy; Geomancer/Chemist. |
| **Chemist** | Consolidate narrow cures and high-grade potions. Add a two-ingredient Healing Mist and a stronger single-target revival mixture. Keep stock consumption and early access meaningful. | Moogle Juggler/Chemist; Bard/Chemist; Nu Mou Geomancer/Chemist. Compare with Alchemist's innate ordinary Item plus Long Throw. |
| **Bard** | Songs work by voice on other Moogle jobs. Meaningful area damage buffs with Protect/Shell, immediate group healing, useful MP recovery, and a dependable final defensive song. | Juggler/Song; Time Mage/Song; Bard/Chemist. Each still chooses two learned commands. |
| **Dancer** | Scale performance damage through the campaign. Polka and Heathen Frolic deal damage and substantially weaken one enemy. Slow Dance becomes area control; Forbidden Dance lets the player select its ailment. | Assassin/Dance for most dances; Red Mage/Dance; Dancer/White Magic. Sword Dance still needs knife/rapier. |
| **Mystic Knight** | Every enchantment can be applied while delivering one immediate adjacent enchanted strike. Self-only preparation remains available. Later primary Fight attacks retain the enchantment. | Red Mage/Spellblade; Fencer/Spellblade; Dancer/Spellblade with rapier. Neither Assassin nor Summoner gains suitable weapon access by learning the command. |
| **Soldier axes** | Practical low-cost reach/area attacks, plus Shatter Guard removing Protect before its successful damage. | Soldier/Hunter with an axe. Other Human jobs cannot execute axe lessons without axe permission. |
| **Gladiator axes** | Stronger narrow area attack; Executioner gains a meaningful wounded-target accuracy niche. Retain Fell Cleave's substantial damage and exposed-state risk. | Viking/Gladiator; axe Gladiator/Dark Arts for Last Resort. Full sword drain and axe finishers cannot coexist in that fixed loadout. |

## Supports: the revised competitive roles

Keep **Long Throw, Pharmacology, Light Foot, and Arcane Ward** substantially intact. They already change reach, resources, or survivability in recognizable builds. Surefoot keeps its effect with lower AP, reflecting its map-specific value.

The larger proposed revisions are:

- **Composure:** 25% damage/direct-healing bonus when acting before moving. It remains an alternative for a build that already has adequate accuracy.
- **Poise:** 25% direct damage reduction while benefiting from a positive status. Multiple buffs do not increase its magnitude.
- **Desperation:** 50% eligible damage bonus at **35% HP or below**, checked after costs. This deliberately differs from the panel's original 40% suggestion.
- **Bloodcasting:** retain 2 HP per MP and preserve all native HP costs. Explicitly charge the full eligible action cost, never a free additional component. It cannot coexist with another support such as Desperation or Half MP.
- **Opportunist:** 30% damage against an already afflicted enemy. Its magical use is particularly relevant to Bangaa.
- **Attunement:** 25% weakness damage plus a 25% refund of MP actually spent on an eligible successful weakness-hitting action. No refund per area target and no pre-financing an unaffordable spell.
- **Sea Legs:** forced-displacement and Immobilize immunity; a specialist, affordable choice.
- **Encouragement:** 15% target-max-HP healing, cap 60, when applying a new qualifying persistent buff to another ally. Immediate turn grants do not qualify.
- **Clear Voice:** Silence immunity plus a 25% MP discount on tagged incanted magic/songs. This gives Moogles a distinctive casting-support choice.
- **Grace:** preserve frontal Evade against side/rear accuracy calculations, rather than adding a small generic Evade bonus. Accuracy supports and automatic-hit conditions still matter.
- **Spellweave:** 35% damage for alternating action categories; ordinary waiting or an unclassified action preserves, rather than erases, the previous category. One category is evaluated per action.
- **Recuperation:** 50% stronger incoming direct HP restoration. It does not improve revival, drain, or Regen ticks.
- **Follow Through:** 35% physical damage after ending voluntary movement at least two Manhattan tiles from the turn's starting position. A loop ending near the starting tile does not qualify.

These are candidate numbers with different opportunities and costs. They are not eighteen unconditional upgrades over Concentrate. The complete support table specifies exclusions and legal external-job examples.

## Reactions: reliability with clear tradeoffs

Remove the blanket lock until the user's next turn. Most reactions activate reliably when eligible, with their own targeting, survival, and weapon conditions. Offensive counters still have an ordinary hit check. An enemy multi-hit/multi-cast action supplies one opportunity for a new reaction; counters/recovery happen after the full action, and a defensive reduction consistently covers its eligible damage components. Vanilla reactions retain their original behavior.

Representative results:

| Reaction | Consolidated proposal |
|---|---|
| Blade Ward | Katana required; reduce physical direct damage by 35%, including physical abilities. |
| Dark Ward / Stone Skin | Reduce the relevant incoming damage by 25%, then grant Shell / Protect after survival. Their status component uses the original defense-stat behavior. |
| Counter Draw / Axe Reprisal | Reliable eligible counter opportunity at 1.00P / 1.20P, with ordinary accuracy and survival/range/weapon restrictions. Counter Draw can establish Centered. |
| Absorb Damage | Recover 30% of actual HP lost, capped at 15% maximum HP per incoming action; cannot save a lethal hit. |
| Auto-Potion | Use an explicitly selected Potion or Hi-Potion at half HP or below; at most one consumed item until the next own turn. No silent upgrade to rarer stock. |
| Auto-Cureall | Spend one Cureall to intercept eligible ailments from the enemy action, not its damage. Existing incapacitation can prevent reacting; newly intercepted incapacitation cannot prevent its own interception. |
| Encore | Reactive, temporary self-Haste after surviving physical damage while able to react and unsilenced; no instrument gate or immediate extra turn. |
| Fury / Magick Boost | Store one temporary charge for a stronger appropriate subsequent action; no permanent growth or accumulating charges. |
| Spell Parry | **Consume the enchantment for 50% physical damage reduction against one enemy action.** Re-enchantment is a deliberate action; it does not provide complete immunity. |
| Gil Snapper | Retain an explicitly economic niche at 50 AP, reliable on the qualifying critical hit but capped at 50 gil per battle. No promise that it is an endgame combat pick. |

The full report covers all 18 reactions, including Nature's Wrath, Vengeful Pulse, Counter Rhythm, Magic Shell, and Haft Guard. No new response triggers from self-costs, allied attacks, damage-over-time, combos, or another reaction.

## Decisions reached during cross-review

1. **Reject a renewable full physical shield.** The first Spell Parry candidate completely negated one enemy action. Because enchantment now also attacks, the combined package made shield renewal too inexpensive. Adopt 50% reduction while consuming the enchantment.
2. **Retain the 35% Desperation threshold.** Raising it to 40% creates an exact shortcut from Dragonheart's half-HP revival through Blood Edge's 10%-max-HP cost. The 35% threshold avoids that shortcut; a larger sacrifice can still deliberately activate the support. The 50% damage bonus remains a test candidate.
3. **Do not add free healing to every Smile.** Encouragement recognizes new persistent tagged buffs, excluding immediate turn/CT effects such as Smile and Quicken. Reactive self-Haste, refreshes, and self-buffs also produce no Encouragement heal.
4. **Separate sequencing from damage type.** Both Spellblade modes establish Magic for Spellweave, but the strike deals physical damage. Battle Chant and Fury may enhance the strike; Wisp Exposure and Magickal Refrain do not. Spellblade followed by Red Magic is Magic-to-Magic, so earns no alternating bonus. The action never counts as both categories.
5. **Make the advanced revival always an upgrade.** Resuscitating Draught revives at 50% target maximum HP, rounded down, minimum 1, with no 200-HP cap. It consumes one X-Potion and one Phoenix Down; no Pharmacology or incoming-healing amplification. The rejected cap could make it worse than ordinary revival at very high HP.
6. **Keep positive-resource actions when they cost turns.** Bloodcasting-funded healing, MP songs, and drain can sustain a party. Do not ban them merely because resources can increase. Reject omitted costs, duplicated recovery, recursive reactions, or a newly introduced cycle producing free productive actions.
7. **Resolve healing and buff math once.** Drain recovers from actual damage removed, then applies its cap; no second outgoing-healing multiplier. Encouragement's separate heal receives only the recipient's incoming-healing modifier, not Magick Boost or Composure. Resolve each healing event's combined multipliers before rounding and the missing-HP cap.
8. **Constrain Last Resort's bonus explicitly.** Its outgoing modifier covers eligible direct physical HP damage, not fixed/percentage effects, items, reactions, combos, MP damage, or a second multiplication of drain recovery. Its linked incoming drawback uses its stated physical direct-damage category. Self mode works with Healer; enemy strike mode cannot turn a restorative weapon into damage.
9. **Use one cure-eligibility contract.** Auto-Cureall follows the ordinary Cureall cure list plus any custom harmful tags included by the expansion's shared broad-remedy integration. It does not prevent KO, effects the item cannot cure, or HP costs. One consumed item covers only the eligible ailments of that enemy action. Manual Chemist recipes do not silently grant every remedy that cure list.
10. **Keep Gil Snapper thematic and inexpensive.** Reject the alternative of spending gil for generic mitigation. An economy lesson can remain a niche rather than competing numerically with every defensive reaction.

## Strong combinations to preserve and measure

These arithmetic examples assume successful eligible actions and ignore defense/affinity changes already inside P. They do not predict average battle damage or prove dominance.

| Legal combination | Maximum illustrated payoff | Real cost / counterplay |
|---|---|---|
| Bangaa Dark Knight/Gladiator, Desperation, Dragonheart; allied Battle Chant; own Last Resort | Unholy Sacrifice: 1.75P × 1.50 × 1.25 × 1.20 = **3.9375P per target**, before Dark affinity. | Low HP, 20% max-HP sacrifice plus 14 MP, prior own buff action and allied song, adjacency/friendly fire, ordinary accuracy, elemental resistance. Dragonheart reduces the defensive risk; this is a priority test, not presumed fair. |
| Axe Gladiator/Dark Arts with Follow Through; own Last Resort and allied Battle Chant | Fell Cleave: 1.80P × 1.35 × 1.25 × 1.20 = **3.645P**. | Real relocation, support/secondary commitment, 16 MP, setup, and Exposed. Last Resort plus Exposed makes eligible incoming physical damage ×1.44 before mitigation. No sword drain in this loadout. |
| Axe Gladiator/Dark Arts with Desperation instead | Fell Cleave reaches **4.05P** with Last Resort and Battle Chant. | Low-HP threshold replaces the movement support; no simultaneous Follow Through. No native HP cost on Fell Cleave to create that threshold for free. |
| Dancer/Spellblade with Spellweave and Fury; allied Battle Chant | Sword Dance: 1.60P × 1.35 × 1.35 × 1.20 = **3.4992P**. | Prior Magic-category action, surviving an enemy hit, rapier, 16 MP, no Concentrate, no defensive reaction. |
| Geomancer Wisp Exposure plus Bard Inspired Magic benefiting an allied caster | **1.50×** eligible magical damage at strongest affinity: 1.25 × 1.20. | Two allied setup actions, target survival/position, MP and expiry. The setup hits/buffs cannot multiply themselves retroactively. |
| Chemist Healing Mist with Pharmacology, on a Human with Recuperation | At 300 maximum HP: 60 × 1.50 × 1.50 = **135 HP**. | Two existing consumables, an action, area positioning, two units' support slots. No revival increase. |
| Bard with Magick Boost and Encouragement using Angelsong on a 300-HP Human with Recuperation | Base song heal 60 × 1.30 × 1.50 = 117; new-buff heal floor(45 × 1.50) = 67; **184 total HP**, plus Regen. | Bard's S/R slots, prior enemy damage and survival, song MP/action, and newly absent Regen. Refreshing Regen loses the 67-HP bonus. |
| Human Dark Knight/Blue Magic with Bloodcasting and Damage > MP | HP pays actions while existing MP can protect against qualifying damage; Infernal Strike can replenish some enemy-derived MP. | No Desperation/Weapon Atk+ at the same time; finite enemy MP; HP costs, hit checks, recovery actions, and actual redirection rules. Test starting with just 1 MP as well as a full reserve. |

The council accepted these as useful candidates for measurement. It did not establish that they are balanced against every boss, stat history, or equipment combination. In particular, sustained Dark Knight resource defense and highly buffed sacrifice damage deserve the first scenario tests.

## Growths, learning, and equipment

Retain the ten current growth/chassis profiles for the first prototype. Fixing actions first avoids masking weak mechanics with inflated stats. Test natural campaign leveling and optimized inherited growth separately. Keep the roster, Chemist starter status, racial distribution, and accepted job prerequisites.

Keep 72 teaching-item positions; renamed/repurposed lessons need matching item text. Generic prices and weapon powers remain provisional until matched with actual vanilla shop tiers. Review spillover onto original jobs that can equip the new swords, knives, katanas, sabers, and rods. Do not make Ethers purchasable or add recruitment changes implicitly.

| Lesson group | Existing total AP | Proposed total AP |
|---|---:|---:|
| Samurai | 3,150 | 3,200 |
| Dark Knight | 3,150 | 3,350 |
| Viking | 3,150 | 2,800 |
| Geomancer | 3,150 | 3,150 |
| Chemist | 3,150 | 2,850 |
| Bard | 3,150 | 3,050 |
| Dancer | 3,150 | 3,300 |
| Mystic Knight | 3,150 | 3,000 |
| Soldier axe additions | 1,200 | 1,050 |
| Gladiator axe additions | 1,850 | 1,850 |

These are sums of lessons, not required sequential grinding: simultaneous learning matters. Both races of a shared job use the same lesson totals. Cheap new actions may accelerate existing unlock gates; measure that without silently changing the agreed prerequisites.

## First prototype priorities

1. Prove action-cost, classification, damage-preview, and inventory handling for one representative action from each new mechanic.
2. Test Dark Knight damage/HP/MP cycles, buffed sacrifice, and Damage > MP at tiny reserves.
3. Test enchant-and-strike with Spellweave, Fury, and consumable Spell Parry across two enemy attacks.
4. Test Bard/Chemist rescue output, Encouragement exclusions, and MP/extra-turn party schedules.
5. Test Dancer control/scaling and Geomancer fields on ordinary, cramped, high-ground, and immunity-heavy encounters.
6. Run matched early/mid/late comparisons around levels 10, 25, and 40 with actual available gear and organic versus optimized stat histories.

Review coverage and AP arithmetic are complete; the 0.4 baseline is preserved and the adopted 0.5 documents/data are checked for consistency. Gameplay, clean-ROM handler mapping, and campaign playtesting remain future implementation work; the numerical proposal should be revised from that evidence.
