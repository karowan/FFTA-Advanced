# Supports for mixing jobs

Version 0.4 — September 14, 2026

**A job teaches a support; it does not own the support's usefulness.** These 18 proposals work after switching to another legal job, without keeping the teaching job's action set or special weapon equipped. The one support slot remains a meaningful choice. Racial access still applies: a Human cannot learn a Nu Mou-only job just to obtain its support.

Single Blade has been removed. Its single-weapon damage niche overlapped existing Doublehand/weapon-offense choices; **Composure** instead rewards choosing when to move and works for physical attacks, magic, and restorative techniques. Poise no longer requires Centered or a katana. The axe jobs' supports likewise require neither axes nor axe actions. Existing vanilla supports remain unchanged. [Original FFTA mechanics reference](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262).

## Revised support list

Every effect and number is our proposal. The examples respect the teaching job's race access; they illustrate possible builds, not completed balance tests.

| Taught by | Support | General benefit | Examples outside the teaching job |
|---|---|---|---|
| Samurai | Composure | Act before moving for stronger damage or healing. | Human Archer holding a firing position; Human Black Mage casting before moving |
| Samurai | Poise | Take less damage while benefiting from a positive status. | Human Paladin with Protect; Human Blue Mage supported by an allied buffer |
| Dark Knight | Desperation | Stronger physical and magical damage at low HP. | Human Black Mage risking low HP; Bangaa Gladiator using wounded-state burst |
| Dark Knight | Bloodcasting | Spend HP in place of MP for any eligible action. | Human Illusionist using HP to fuel Phantasm; Bangaa Bishop spending HP for Prayer |
| Viking | Sea Legs | Resist forced movement on any job. | Bangaa Dragoon keeping a useful position; Bangaa Templar resisting knockback |
| Viking | Opportunist | Deal more damage to enemies already suffering an ailment. | Bangaa Warrior attacking a blinded target; Bangaa Bishop exploiting an ally-applied debuff |
| Geomancer | Attunement | Improve elemental damage that strikes a weakness, from any command or weapon. | Nu Mou Black Mage exploiting weaknesses; Nu Mou Sage choosing an appropriate element |
| Geomancer | Surefoot | Improve jumping and ignore added terrain movement costs. | Nu Mou Beastmaster reaching a useful position; Nu Mou Alchemist crossing slowed ground |
| Chemist | Pharmacology | Improve HP/MP restoration from ordinary items, mixtures, and item reactions. | Moogle Gunner with ordinary Item; Nu Mou Alchemist using restorative supplies |
| Chemist | Long Throw | Throw ordinary items and other eligible consumables farther. | Moogle Thief with ranged Item support; Nu Mou White Mage delivering an emergency item |
| Bard | Encouragement | Adding a new beneficial status to another ally also heals them slightly. | Moogle Time Mage granting Haste; Moogle Animist applying a beneficial effect |
| Bard | Clear Voice | Protect any caster or singer from Silence. | Moogle Black Mage preserving casting; Moogle Time Mage preserving support magic |
| Dancer | Grace | Improve evasion with any weapon or job. | Viera Fencer defending in melee; Viera Red Mage taking a frontline role |
| Dancer | Light Foot | Increase movement on any job. | Viera Summoner reaching a casting position; Viera Sniper relocating for a shot |
| Mystic Knight | Spellweave | Alternate magic and physical actions for stronger attacks. | Viera Red Mage alternating magic and Lunge Tech; Viera Elementalist with a physical secondary set |
| Mystic Knight | Arcane Ward | Reduce magical damage while keeping a healthy MP reserve. | Viera White Mage conserving MP; Viera Summoner holding a defensive reserve |
| Soldier | Recuperation | Receive stronger direct HP healing from any restorative source. | Human Fighter supported by a healer; Human Paladin benefiting from restorative actions |
| Gladiator | Follow Through | Move before attacking for stronger physical damage with any weapon. | Bangaa Warrior advancing into combat; Bangaa Dragoon moving before a physical technique |

## What mixing means in practice

- A Human Archer can use **Composure** with Aim and another command, with no Iaido equipped. A Human mage can use the same support to cast before relocating. It rewards a tactical decision, not a particular weapon.
- A Moogle Gunner can take **Pharmacology** and ordinary Item for stronger emergency supplies. It does not need the Chemist command. A Nu Mou Alchemist can use the same item support through that race's Chemist access.
- A Nu Mou Black Mage can take **Attunement** without Geomancy; the trigger is exploiting an elemental weakness.
- A Viera Red Mage can take **Spellweave** and alternate spellcasting with physical Lunge Tech. A Mystic Knight can start that rhythm with an enchantment. Neither needs to hold a specified weapon for the support itself; each action still has its own equipment rules.
- A Bangaa Dragoon can take **Follow Through** and use its usual equipment. An allied debuffer can instead make **Opportunist** attractive. Those supports compete for one slot.

## Exact proposed effects

### Composure — Samurai, 200 AP

During your own turn, direct HP damage dealt and direct restorative HP healing applied ×1.15 if you have not voluntarily moved before that action starts. Moving afterward is allowed. No weapon, command, or Centered requirement. Does not boost item healing, drain recovery, MP effects, or reaction damage.

### Poise — Samurai, 350 AP

Direct physical and magical HP damage received ×0.85 while at least one beneficial status is active at the start of the incoming action. Qualifying effects are Protect, Shell, Haste, Regen, Float, Invisible, or a tagged temporary beneficial effect such as Centered, Last Resort, or a Spellblade enchantment. Additional statuses do not increase the bonus. No katana or source-job requirement; costs and damage-over-time are excluded.

### Desperation — Dark Knight, 200 AP

Direct physical and magical HP damage dealt ×1.30 while at 35% maximum HP or less, checked after paying costs. Works with any weapon and command. Does not increase HP costs, healing, MP damage, item effects, or damage-over-time.

### Bloodcasting — Dark Knight, 350 AP

For a voluntarily selected action with an MP cost, pay 2 HP per MP that would otherwise be spent, and spend no MP. Add any native HP cost separately; the combined payment must leave at least 1 HP. Pay after target validation and before accuracy, once per action. Costs trigger no reactions and cannot be reduced by damage protection. Items, JP, and non-MP costs are unchanged. Applies to every command; does not grant access to a command or change its Silence rules.

### Sea Legs — Viking, 200 AP

Ignore forced tile displacement. Works with every job and weapon. Does not stop Immobilize, Slow, voluntary movement, or terrain harm, and does not grant water traversal.

### Opportunist — Viking, 350 AP

Direct physical and magical HP damage dealt ×1.20 against a target with at least one harmful status at the start of the action. Qualifying examples include Poison, Blind, Silence, Slow, Immobilize, Disable, Confuse, Sleep, and tagged custom debuffs. Multiple ailments do not multiply the bonus. The action cannot qualify itself by applying a status after its own damage. No weapon or theft requirement.

### Attunement — Geomancer, 200 AP

Elemental direct HP damage dealt ×1.20 when the resolved element is a weakness of the target after ordinary affinity rules. Applies to any physical or magical attack, including elemental weapons and secondary commands. Requires neither Geomancy nor nearby terrain. Neutral, resisted, immune, absorbed, non-elemental, healing, and damage-over-time outcomes gain nothing.

### Surefoot — Geomancer, 350 AP

Jump +1. Entering an otherwise legally traversable tile pays its normal one-tile movement cost without added terrain movement surcharges, including Rime Field. Does not remove height restrictions, environmental damage or ailments, blocking units, or impassability; no flight or extra movement action.

### Pharmacology — Chemist, 200 AP

Direct HP and MP restoration from consumed restorative items ×1.50, then round down and cap at the recipient's missing resource. Applies to ordinary Item, Chemist actions, other consumable-based commands, and item-consuming reactions such as Auto-Potion. Does not improve revival HP, cure lists, drain, or magic; full restoration remains full restoration. Only the item user's support supplies this modifier.

### Long Throw — Chemist, 350 AP

For a consumable-based single-target action that can normally target another unit, a base range below 4 becomes 4; a base range of 4 or more gains +1, capped at 5 and never reduced below its original range. Applies to ordinary Item, Chemist applications, and eligible future mixtures. Retain target, height, and line-of-sight restrictions. Does not turn self-only or area effects into ranged single-target effects, and does not extend weapon attacks.

### Encouragement — Bard, 200 AP

When a voluntary action successfully adds a new beneficial status to another ally, also restore 10% of that ally's maximum HP, capped at 30 HP before incoming-healing modifiers. Once per ally per action, even if several statuses are applied. Applies to all commands. Refreshing an existing status or its duration does not qualify; merely healing or curing does not qualify. No self-target bonus or reaction trigger.

### Clear Voice — Bard, 350 AP

Immune to Silence while equipped, regardless of job, weapon, or command. No protection against other ailments. Does not grant magic, an instrument, or access to a voice-based command. Ordinary status-immunity handling applies.

### Grace — Dancer, 200 AP

Base Evade +10 before ordinary facing, equipment calculations, and caps. Applies with any job and weapon; it is not a universal ten-percentage-point dodge bonus against every effect.

### Light Foot — Dancer, 350 AP

Move +1 on any current job. No second movement action, flight, terrain immunity, or free ability slot.

### Spellweave — Mystic Knight, 200 AP

Alternate a voluntary incanted magic action and a physical-damage action. If the current action is the opposite category to the preceding qualifying action, its direct HP damage ×1.20; any physical weapon or command qualifies. Spellblade preparation counts as magic even though it causes no damage, so it can prepare a boosted physical attack. An action with no qualifying category breaks the sequence; repeating a category sets that as the last category without a bonus. No healing, drain-recovery, item, or reaction bonus. Magic acts resolve using an explicit command/effect classification, not simply a nonzero MP cost.

### Arcane Ward — Mystic Knight, 350 AP

Magical HP damage received ×0.75 while current MP is at least 50% of maximum MP at the start of the incoming action, with at least 1 MP remaining. Does not spend MP, absorb a spell, or reduce HP costs. Works with every job and weapon.

### Recuperation — Soldier, 200 AP

Direct HP healing received ×1.25 from any eligible restorative source, including medicine and allied or self healing. Round down after combining modifiers and cap at missing HP. Does not improve revival HP, drain, regeneration ticks, or MP recovery. No axe, weapon, or command requirement.

### Follow Through — Gladiator, 350 AP

During your own turn, direct physical HP damage dealt ×1.15 if you voluntarily moved at least one tile before the action begins. Applies to every weapon and physical command. Extra distance gives no additional bonus; forced displacement and later movement do not qualify. No magic, item, reaction, or damage-over-time bonus.


The full [class specification](JOB-CLASS-SPECIFICATION.md) defines timing, action categories, stacking, status tags, healing, and costs. Existing action equipment restrictions remain; support flexibility does not grant a character new weapons or cross-race jobs. Pharmacology, Long Throw, Attunement, and Spellweave require explicit integration with relevant original actions, not merely a whitelist of our new skills.

## Balance requirements

Each support must have two plausible uses outside its teaching job and compete with supports actually obtainable by that race. A percentage alone is not evidence of competitiveness. Check turn value, resource loops, damage formulas, item potency, buff availability, and secondary-command combinations at matched levels/equipment. Bloodcasting and Spellweave introduce new systems; confirm implementation and test their payoff before fixing the numbers.

No claim that all vanilla supports are universally usable is needed. Our design goal is broad mixing with meaningful conditions. The previous tendency to write “only this job's eight actions” into support descriptions is explicitly rejected. A future narrow support would need a compelling build reason rather than serving as a required tax on its own job's effectiveness.

The draft still has 116 ability entries and 72 teaching items. Support AP, teaching positions, roster, and unlock requirements are unchanged. No ROM is modified.
