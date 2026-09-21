# Global balance and cross-class review

> Historical council review of v0.4, adopted through the reconciled v0.5 specification. Statements about unchanged canonical files describe the review stage. For current rules, use [the class specification](../JOB-CLASS-SPECIFICATION.md), [axe addendum](../AXE-SKILL-EXPANSION.md), and [adoption record](../BALANCE-COUNCIL.md).

September 14, 2026. Chair's review of design 0.4, accompanying three independent council reports. Recommendations are design proposals; no ROM or canonical class sheet is changed.

## Balance target

The expansion should offer attractive choices alongside vanilla builds without requiring every new job to reproduce the most extreme vanilla strategy. Preserve ordinary play, equipment/AP learning, racial access, two command sets, one support, and one reaction. Evaluate a standalone new job, a legal mixed build, and an optimized party separately. A good item medic does not have to outperform an entire party built to win before enemies act.

Judge early usefulness, midgame flexibility, and endgame scaling separately. A starter's inexpensive attack can remain useful without becoming an endgame finisher. A 400-AP capstone must justify its action, equipment, MP, and positioning costs. All new jobs should have a useful first combat action and at least one contribution against enemies immune to their main status trick.

Community optimization emphasizes combinations such as Paladin/Hunter, Red Mage/Summoner, and fast Moogle turn support. These are upper benchmarks, not a requirement to homogenize the new roster. [Vanilla optimized-build discussion](https://gamefaqs.gamespot.com/boards/560436-final-fantasy-tactics-advance/57520610).

## Numerical sanity checks

These are transparent calculations from our draft and deliberately simplified comparisons, not emulator battle results.

| Current design case | Calculation | Implication |
|---|---|---|
| Last Resort, then two ordinary attacks | 0 + 1.20P + 1.20P = 2.40P, versus three attacks = 3P | Loses 20% output over this window while increasing incoming damage. A setup before contact has a different opportunity cost, but cannot be the only useful case. |
| Ashura followed by Kiku-ichimonji, both hit | 1.10P + 1.30P × 1.25 = 2.725P, versus two Kiku = 2.60P | Modest two-turn gain and lower MP use; Centered should improve an already useful attack rather than require an idle setup. Misses, facing, range, and expiry can reverse the comparison. |
| A group damage buff of 15% | With three allies each making two equal attacks, added output = 3 × 2 × .15 = .90 ordinary attacks | Still below the casting action's opportunity cost if the caster could otherwise contribute a full equivalent attack. Healing or other utility, more recipients, or a pre-contact cast can change the result. |
| Original Blade Ward | .40 activation × .30 reduction = .12 | 12% expected reduction for an eligible opportunity before its additional lockout. |
| Original Absorb Damage | .35 activation × .10 recovery = .035 | Only 3.5% recovery of damage, with no protection against a lethal hit. |
| Revised Spellweave candidate: 35% alternating bonus | If best repeatable action is worth 1 and alternate action is worth x, an established two-action cycle yields 1.35 × (1 + x); this exceeds 2 only if x > .4815 | Alternation still requires a meaningful second action. First-cycle setup and lost accuracy must also be counted. This is not a promise that every hybrid beats Doublecast. |
| Extra movement or item range | A previously unreachable legal target becomes reachable | Value can be an entire successful rescue or attack, rather than a small percentage increase. Compare at actual map positions. |

For damage comparisons, compute the original attack/defense calculation first, then the proposed post-damage multiplier. Vanilla Weapon Atk+ and Turbo MP modify attack inputs; they are not equivalent to flat final-damage bonuses. Growth is accumulated on level-up; a job switch does not replace the character's growth history. These rules come from [Terence's mechanics research](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262). Numerical examples above are our calculations.

## Growth and chassis decisions

Keep the ten current growth profiles, generation templates, Move/Jump, and equipment permissions as the initial comparison baseline. Do not change growths merely to conceal dead actions. Reconsider only after testing the revised kits with the same history and equipment. No new job has to be the best job to level in; equally, playing the job normally must not render its core kit ineffective.

| Profile | Decision and required comparison |
|---|---|
| Human Samurai | Retain 8.6 WAtk / 1.4 Speed growth and Move 4. Compare a normally trained Samurai with the same unit trained partly as Ninja. Centered uses physical development; magic growth must not become a hidden damage requirement. |
| Human Dark Knight | Retain 8.0 HP / 9.0 WAtk / 1.0 Speed. Judge sacrifice against slow turns and rescue actions, then separately test a fast externally trained carrier. |
| Bangaa Dark Knight | Retain 8.8 HP / 9.2 WAtk / .9 Speed. Higher HP raises percentage costs as well as durability; it is not automatically a better Bloodcasting chassis. |
| Bangaa Viking | Retain 8.4 WAtk / 7.6 MPow / 1.0 Speed. Test both its native hybrid progression and a magically trained carrier of Reaving. A physical-only upbringing must still have useful axe actions. |
| Nu Mou Geomancer | Retain 8.6 MPow / 3.6 MP / 1.0 Speed. Its breadth, unreflectable nature arts, and fields are part of the budget; avoid giving it superior raw magic and every utility advantage together. |
| Nu Mou Chemist | Retain Move 4 / 1.2 Speed. Item output deliberately does not need magical growth. Compare Chemist/Time Magic with a more magically trained unit using Chemist secondarily. |
| Moogle Chemist | Retain Move 4 / Jump 3 / 1.5 Speed. Compare native leveling and Thief-trained support; stronger item effects must not depend on raising Magic Power. |
| Moogle Bard | Retain 1.4 Speed / 3.4 MP and modest physical growth. Removing the song instrument gate is preferable to compensating for it with inflated speed. Evaluate primary Bard and fast Juggler/Song. |
| Viera Dancer | Retain 1.8 Speed / 7.2 WAtk / Move 4. Scale damaging dances with a meaningful equipment or level reference; do not use weak fixed weapon power and expect speed to compensate. |
| Viera Mystic Knight | Retain 8.2 WAtk / 1.4 Speed / Move 4 and shield access. An immediate enchantment strike addresses setup cost; adding top physical, magical, and speed growth on top is unnecessary. |

For reproducible comparisons, start from a saved character's actual stats and project 9, 24, or 39 subsequent level gains under the chosen history; do not pretend that a new job could have been unlocked at level one. Show both natural campaign histories and controlled equal-stat comparisons at levels 10, 25, and 40. Record damage, success rate, useful actions before enemies act, total MP/HP/items used, and rescues required. A capstone is unavailable in the early tier unless its teaching item actually exists then.

## Equipment and command legality

| Combination | Legal scope and constraint |
|---|---|
| Human Samurai / Fighter | Katana Iaido plus weapon-compatible Fighter actions. Compare with Ninja/Iaido using a katana. Double Sword consumes the support slot and supplies no second strike to new A-abilities. |
| Human Paladin / Dark Arts | Sword-compatible Dark Arts; a separate support and reaction can be equipped. No automatic Samurai access just because the same character learned it. |
| Human Soldier / Hunter with an axe | Legal under the proposed Soldier axe permission; verify each original Hunt action's own rules. Paladin with Battle Tech cannot use axe-gated additions. |
| Bangaa Viking / Gladiator with an axe | Access to both sets' axe moves, ordinary compatible Gladiator moves, and Viking spells. Consider elemental coverage and immediate burst together. |
| Bangaa Viking / Dark Arts | Dark Mind and Last Resort are weaponless in the draft; sword-gated damaging Dark Arts are unavailable with an axe. Do not advertise this as the full two kits. |
| Bangaa Dark Knight / Bishop | Sword attacks plus Prayer support; compare self-recovery turns with an external healer. Bloodcasting occupies the support slot, so cannot coexist with Half MP or Weapon Atk+. |
| Nu Mou Time Mage / Geomancy | Full weaponless Geomancy plus Time Magic. One support means a choice among Turbo MP, terrain mobility, or another option. |
| Nu Mou Alchemist / Chemist | A legal command pair, but compare Alchemist / Sagacity with Long Throw: Alchemist already has innate ordinary Item regardless of its secondary, as documented in the [Job FAQ](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26178). This exception does not provide a third freely chosen skill set. |
| Moogle Juggler / Song | Legal after the proposed voice-based song change; can sing or use Smile, not both within one action. |
| Moogle Juggler / Chemist | Smile plus advanced medicine; compare ordinary Item plus Long Throw as a different build. The Chemist command frees the support slot but uses the secondary command slot. |
| Moogle Gunner / Chemist | Gun and medicine; does not also gain Juggler or Smile. No Moogle White Magic or Bloodcasting access. |
| Viera Red Mage / Spellblade with rapier | Legal martial/magic hybrid; original eligible spells retain Doublecast, new enchanted attacks do not gain it. |
| Viera Fencer / Spellblade | Legal enchantment plus Lunge Tech; future persistent enchantment effects apply only to explicitly allowed attacks, not every Lunge action by implication. |
| Viera Assassin / Dance | Most dances can work; Sword Dance is unavailable with katana/greatbow. Assassin / Spellblade is not a legal full-kit combination with its ordinary weapons. |
| Viera Red Mage / Summoner with Light Foot | Legal transferable support build; adding Light Foot does not also equip Dancer's command or any other support. |

## Progression, prices, and teaching items

Retain the agreed job prerequisites and Chemist starter access. Audit every new action counted toward existing job gates: cheap Soldier axe lessons may accelerate Fighter/Paladin access and Gladiator axe lessons may accelerate Bangaa Dark Knight access. This is an additive consequence to measure, not grounds to silently change the user's accepted gates.

Do not infer learning time from the sum of all AP values: simultaneous lessons can progress together. A W2 teaching an action and support is different from two separate compulsory equipment periods. Recalculate totals if panel recommendations change AP; preserve every reviewed ID's teaching position unless an explicit replacement row says otherwise.

Keep 72 proposed teaching items for the first prototype; do not treat the generic attack/price ladder as verified campaign balance. For each actual shop release, compare the item with obtainable vanilla alternatives in that category, including stat bonuses, special effects, shields, and handedness. New swords, katanas, sabers, rods, and knives can improve original jobs even without teaching them a lesson. Test those spillovers before increasing any weapon power. New axes sacrifice shield/dual-wield access but must not become universally superior at their first shop tier.

Ethers cannot simply be assumed buyable in vanilla, and Cureall access is progression-dependent. A Chemist lesson's repeatable teaching weapon does not establish repeatable ingredient supply. Retain the existing inventory economy; any added recipe must specify its existing ingredients and count. [Original item economy documentation](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262).

## Required interaction tests and acceptance evidence

1. **Bloodcasting + Damage > MP + healing:** use an actual Human with two legal commands. Price every selected spell's cost; separate self-cost from damage. Positive HP return that costs an action is allowed. Fail if costs are omitted, duplicated incorrectly, reduced by defense, or trigger retaliation. Compare with the same party using normal MP and external healing.
2. **Wisp Exposure + allied Doublecast:** the triggering Wisp hit receives no bonus from the exposure it just applies. Subsequent eligible damage can benefit. No same-name stacking, no multiplication per target, no permanent exposure after expiry. Measure the entire party action sequence against attacking immediately.
3. **Bard buffs + Encouragement + healing modifiers:** once per newly buffed ally per action. Refreshes do not farm healing. A recipient's incoming-healing support may apply once. A buff action does not create free turns or recursive songs.
4. **Mystic Knight + Spellweave + Red Magic:** define one category for the whole enchanted strike, not one magic event and one physical event. Test first activation, repeated enchantments, Fight, ordinary doublecast, misses, and weapon loss. No new move acquires Doublecast just because it uses MP.
5. **Haste/Smile/Quicken with temporary buffs and reactions:** separate actual turn events from enemy-action events. Repeated quick turns must not refresh infinite shields without the documented expense/opportunity; counters never recursively trigger counters.
6. **Witch Hunt and MP denial:** test enemy with 0, 6, 12, 24, and 48 MP, including one whose defining move costs more than its remaining MP. Denial is valuable even when it does no HP damage. Do not invent negative MP or recover more than removed.
7. **Viking theft:** evaluate damage and the original theft routine separately, with equipment eligibility and already-stolen handling. Armor/accessory effects are updated after the correct transaction. No farming an inventory that has already been emptied.
8. **Dark Knight drain and area sacrifice:** test low enemy HP, undead, immunity, absorption, misses, and several targets. Heal only actual eligible loss; total action recovery respects the stated cap. Pay native HP costs once even if every hit misses.
9. **Fields and movement:** Updraft, Light Foot, Surefoot, Float, immunity to forced displacement, stacking, heights, impassable tiles, and caster death. No terrain affinity manufactured by Rime Field itself.
10. **Defensive reactions against actual enemy actions:** ordinary Fight, physical A-ability, magic, multihit, area attack, lethal damage, incapacitation, costs, ally damage, and damage-over-time. A reaction's preview and trigger must agree.
11. **Statuses and bosses:** a fully immune enemy should remove the status payoff, not erase unrelated damage/support options. No proposal silently strips a boss's immunity. Cure actions must specify whether they remove custom debuffs or only the original item's cure list.
12. **Equipment/laws/AP/save:** legal main weapon, mastered versus temporary lessons, command and effect laws, new item shop timing, AP gate acceleration, job changes, save/load, and old vanilla command behavior.

This is a complete design review framework and prioritized test plan, not a claim that those emulator tests have run. The council's row-level recommendations supply the concrete changes to evaluate.
