# Spellblade expansion — version 0.6

This records the fourteen-action Spellblade adoption. Its class mechanics remain current in version 0.7; current project-wide totals are 129 abilities and 85 teaching items after the seven additions to other jobs.

September 14, 2026. Approved concepts and Spellweave categories; new costs, AP, powers, and teaching placements are provisional first implementation targets. No ROM changes or gameplay-test claims.

## What the user approved

Mystic Knight grows from eight to fourteen actions: retain Fire, Blizzard, Thunder, Poison, Sleep, Silence, Drain, and Flare; add Slow, Osmose, Holy, Spellbreak, Arcane Release, and Break Blade. Existing racial access, progression, growths, supports, reactions, and equipment categories remain. Command size follows meaningful choices rather than a common quota. The exact current rows live in [the class specification](JOB-CLASS-SPECIFICATION.md#11-mystic-knight--viera).

## Spellweave classification

| Action | Sequence category | Damage / rider |
|---|---|---|
| Self enchantment | Magic | No damage; establishes category |
| Enchant and strike | Magic | Physical HP damage; one action and one evaluation |
| Enchanted Fight | Physical | Physical HP damage with primary-weapon enchantment |
| Spellbreak | Physical | Physical HP damage plus selected dispel; no enchantment rider |
| Arcane Release | Magic | Magical HP damage; consumes eligible enchantment |
| Break Blade | Magic | Petrify attempt only; no HP damage or accuracy bonus |

First qualifying action has no bonus. A subsequent opposite-category action gets ×1.35 eligible direct HP damage. Same-category actions receive no bonus; misses still establish their category. Wait/unclassified actions retain the previous category without a bonus. No action establishes both categories or triggers its own bonus.

Example: Fire enchant-and-strike (Magic, no opening bonus) → Fight (Physical, ×1.35) → Slow enchant-and-strike (Magic, ×1.35 HP damage) → Fight (Physical, ×1.35). Fire → Blizzard or Fire → Red Magic is Magic → Magic and receives no alternation bonus. Fight → Arcane Release alternates, but Release → another enchantment does not.

Status accuracy never improves. MP siphon has no direct Spellweave multiplier: like HP Drain, more actual HP damage can indirectly raise its computed recovery, then its unchanged cap applies. No second recovery multiplier. Spellbreak and an enchanted strike still use physical defenses and physical damage bonuses despite different sequence categories; only Release uses magical defenses/bonuses. New actions remain ineligible for Doublecast.

## Breadth and mixing

Slow offers persistent single-target disruption; Dancer retains area control. Osmose trades another enchantment's benefits for bounded enemy-funded endurance. Holy supplies another matchup. Spellbreak removes one selected magical protection without requiring an enchantment. Release spends sustained offense and Spell Parry fuel for a ranged small area; its friendly fire and magical scaling matter. Break is a separate paid single-target Petrify attempt, never reusable Petrify attached to Fight.

Red Mage/Spellblade can use Osmose to support later original spells but cannot Doublecast a new ability. Fencer/Spellblade and Dancer/Spellblade gain dispel and release with a rapier; accumulated magical stats affect Release. Neither Assassin nor Summoner gains qualifying weapons by equipping the secondary command. One support slot means Spellweave, Concentrate, Half MP, and other alternatives compete; Spellweave is not required for a functional kit.

## Acquisition and validation

Six parallel teaching sabers add 1,800 action AP without raising the existing weapon-power ceiling. Mystic Knight totals 3,400 action AP and 4,800 AP overall. Version 0.6 project totals before the subsequent council adoption: 122 abilities (78 actions, 18 supports, 18 reactions, eight combos), 78 teaching items. Original 0.5 files are archived in notes/design-v0.5.

Check enchant-and-hit miss persistence; one category per action; release expenditure on nullification/miss and loss of parry fuel; no status/drain area release; ordinary weapon versus enchantment element on Spellbreak; selected dispel availability; single S roll and immunity for Break; MP siphon at zero target MP/full user MP/undead/overkill; indirect siphon increase under Spellweave capped at 10 MP; Half MP eligibility (Clear Voice is Moogle-only and cannot be equipped by this Viera); Fury versus magic amplification; AP/shop access; actual job-list/save/item capacity for more than eight actions. Shared laws, payment, reflection, reactions and equipment rules remain applicable. These are required tests, not reported gameplay results.

## Inspiration versus invention

Slow Blade comes from [FFTA2 Spellblade](https://finalfantasy.fandom.com/wiki/Spellblade_(Tactics_A2)). Osmose, Holy, and Break have [FFV Spellblade precedent](https://finalfantasy.fandom.com/wiki/Spellblade_(Final_Fantasy_V)). Our persistent Slow implementation, costs, damage, caps, paid Break technique, Spellbreak, and Arcane Release are adaptations or original design. Source-game behavior does not dictate the mechanics here.

## Council integration clarification

Spellbreak resolves its successful hit and applicable defensive interceptions, removes its selected status if still present, then calculates HP damage. A status already consumed by an interception gives no replacement target or refund. Release explicitly uses A per target, with Magic established only for a committed action. Break excludes a Spellweave accuracy bonus, not the ordinary effects of legal accuracy supports. These clarify the new provisional rows without changing their approved concepts or categories.

The reviewer also proposed making Spell Parry consume only against positive pending physical HP damage. That is a separate change to the previously adopted reaction and remains a candidate: current 0.6 still consumes after a successful eligible physical hit check, even if the eventual HP damage is zero. The canonical reaction row takes precedence over the reviewer recommendation.

## Subsequent adoption

Version 0.7 adds seven abilities to other commands, bringing current totals to 129 abilities and 85 teaching items. All fourteen Mystic Knight actions and existing support/reaction rules remain unchanged. [Adopted council record](ABILITY-EXPANSION-COUNCIL.md).
