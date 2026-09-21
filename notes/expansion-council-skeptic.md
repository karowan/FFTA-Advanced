# Expansion council: independent skeptical review

> Historical review of 0.6. The user subsequently approved all seven candidates as 0.7; [the adopted council record](../ABILITY-EXPANSION-COUNCIL.md) and current specification supersede the proposal-status wording below.


September 14, 2026. Read-only review of current design 0.6, the support sheet, axe addendum, principles, approved Spellblade expansion, and both new candidate reports. No canonical changes or ROM tests. Mystic Knight's six additional concepts and their sequence categories are accepted scope; the questions below concern their provisional mechanics and documentation.

## Recommendation: at most five additions, with unequal priority

| Priority | Candidate | Judgment and condition |
|---|---|---|
| 1 | Chemist: Inoculation | Clearest new medical decision: spend an action and finite ingredients before a disabling attack. It protects another character without occupying that recipient's reaction slot. Keep one target, T2, actual Cureall eligibility, no cure of existing ailments, and no KO/CT protection. This is more distinct than another Protect/Shell source. |
| 2 | Dark Knight: The Blackest Night | An ally ward gives a selfish sacrifice/drain kit a genuine team decision. Accept the martial panel's paid, one-enemy-action reduction provisionally; no refund, attack, retaliation, or free resource when it breaks. Clarify redirection and consumption before implementing. |
| 3 | Dancer: Passing Step | Accept the final 6-MP, 0.95-Pdance proposal using up to two **remaining normal movement points**, ending Move. Its new function is approach/strike/retreat within one ordinary movement allowance. It is not merely the already legal act-then-move order. Explicitly amend the shared no-immediate-movement sentence if adopted. |
| 4 | Viking: Provoke | Accept the proposed recipient-dependent damage penalty, not forced AI targeting. One enemy, one next enemy turn, S accuracy, no damage, and no stack of multiple challengers retain useful counterplay. Its implementation must show which unit is the challenger. |
| 5, conditional | Samurai: Higanbana | A defensible long-fight choice, but the least necessary of these five. Accept only as the proposed bounded two-pulse wound with its full snapshot/cleanup rules; no generic Poison rename, repeated procs, or escalating stacks. Short fights should continue to favor Kiku or Moon Blossom. |

This is a maximum shortlist, not a five-slot quota. Inoculation and the ally ward have the clearest distinct roles. Passing Step adds tactical positioning; Provoke adds a targeting dilemma. Higanbana should wait if status-system effort competes with the first four.

**No additional actions now:** Bard already has healing, cleansing, group offense/protection, regeneration, MP support, undead offense, and concealment. More universal control or living-target damage would mostly remove reasons to select a secondary. Soldier and Gladiator already have four new axe choices on top of their vanilla commands. Mystic Knight has fourteen and should be validated before expanding again. Geomancer already has eight differentiated tools; its proposed Nature's Refuge can stay a later field-system experiment. A 20% magic shelter that must be occupied is plausible, but less urgent than proving Rime, Float, occupancy, and target previews first.

**Defer Guarding Draught rather than reject its theme.** Potion+Soft for ordinary Protect/Shell is coherent and legally useful, especially for a Nu Mou with a non-healing secondary. However, the party already obtains these statuses from White Magic, Samurai, and Bard; it adds less distinct decision space than prospective ailment prevention. If adopted later, keep the actual vanilla statuses rather than an additional stacking defense layer. Alchemist's fixed ordinary Item makes unique mixtures especially important when evaluating whether to sacrifice its secondary slot.

## Cross-panel adversarial review

### Prevention stacking

The Blackest Night plus Poise is 0.50 x 0.75 = 0.375 of otherwise resolved eligible damage for the warded action; ordinary Protect/Shell change their original formula inputs, not a separate assumed flat 50%. Adding another defensive reaction can be strong but costs its own slot. Dragonheart occupies the reaction slot and only helps under its actual trigger; it cannot also be Damage > MP. A self-ward pays both HP and MP and gives up an attack. If cast by another unit, count that ally action. These combinations justify tests, not automatic prohibition.

The martial panel correctly proposes that wholly MP-redirected damage neither consumes the ward nor receives a reduction to MP loss. This is a specification requiring validation against the original handler, not established behavior. Resolve redirection/HP-payable damage consistently for the whole multi-component action, then consume at most one ward. Zero-damage/status-only events cannot waste it.

Inoculation must prevent eligible status applications before Auto-Cureall decides whether to spend an item. It must not prevent self-inflicted Exposed or remove Last Resort's drawback separately. Moogle Encouragement can heal another ally on first application, but neither a refresh nor a later interception grants another heal. Such healing can move a Dark Knight above Desperation's threshold; that is a real tradeoff. Pharmacology has no effect on prevention, and cannot be equipped beside Encouragement on the same caster.

### Provoke: the mechanical penalty is preferable to AI compulsion

The proposed soft version still works if the enemy AI remains unchanged. Do not guarantee that the enemy will attack the Viking, and do not quietly turn it into Berserk or force a scripted boss to use Fight. AoE damage is calculated per recipient: including the challenger does not remove the penalty for the other victims. Multiple marks replace rather than create contradictory obligations. The one-target/one-turn scope matters: adding damage or group application would turn it into an easier, broader Polka/Heathen Frolic. Its S roll, lack of damage, and vulnerability to immunity are acceptable because another Reaving action remains useful when it fails.

### Passing Step: approve the final bounded split, not a hidden movement reset

An ordinary Move-4 user can advance two paid points, strike, then retreat two paid points. A user who spent all four gets only the attack. Light Foot/Updraft may increase the original allowance, but the finishing segment remains capped at two and pays terrain surcharges. After the step, no second Move menu opens. Preview the route; resolve enemy reactions first, then cancel an invalidated route without teleporting or silently selecting another destination.

I would not call a paid extra-two-points alternative intrinsically impossible to balance, but it is a different, substantially stronger mobility design. It can make objective travel and repeated kiting the primary reason to equip Dance. The final remaining-budget rule is the council recommendation; do not accidentally implement the earlier extra-movement draft. Donated turns still provide their ordinary separate turns; this ability itself grants none. A finishing step never retroactively improves the preceding attack's movement-sensitive bonus.

### Higanbana: sustained pressure, not mandatory opener

The proposed unboosted total is 0.80P + 0.50P + 0.50P = 1.80P if both pulses occur, versus Kiku's immediate 1.45P. The extra total is bought with melee exposure, delayed kills, and two opportunities for the victim to act or be cured. With Centered, only the initial part changes: 1.00P + 1.00P total pulses = 2.00P; Centered Kiku is 1.8125P immediately at range. This keeps the wound a durable-target choice rather than a compulsory setup for all attacks.

The snapshot must exclude outgoing modifiers even if they apply to the initial strike. Define whether existing recipient final-damage reductions are excluded from that stored P as well: the panel specifies physical defenses/Protect, but the broad P definition can otherwise be read to include Poise or reaction mitigation. Recommend store the ordinary attack-versus-defense P before the initial strike's temporary final multipliers/interceptions. Applying the wound still requires actual positive HP damage. Later pulses use the stored amount without another defense/evade/reaction evaluation and own exactly two scheduled events. A weaker replacement should not accidentally bank prior pulses or produce three ticks in one turn.

## Audit of the six approved Mystic Knight additions

| ID | Provisional balance verdict | Required clarification or test |
|---|---|---|
| MYK-A9 Slow Spellblade | Keep 12 MP / 0.80P / normal S as the first test. | Sustained single-target Slow does not replace Dancer's area control. Damage hit and rider are separate chances; immunity leaves the hit. Enchant-and-strike establishes Magic; later Fight establishes Physical. Spellweave never boosts S. |
| MYK-A10 Osmose Spellblade | Keep 8 MP / 0.80P / 25%-of-actual-HP siphon capped at 10. | At the cap, activation can gain 2 net MP; Half MP can raise that to 6. Later Fight can recover up to 10 without an MP payment, but drains an actual enemy pool and retains Fight's counters. This is intended endurance, not an infinite resource source. It competes with other enchantments, and Spell Parry consumes it. Test zero target MP, full user MP, overkill, undead, and positive damage after redirection. |
| MYK-A11 Holy Spellblade | Keep 12 MP / 1.00P Holy. | The higher price than Fire/Ice/Thunder buys a distinct matchup, not universal superiority. Holy Release uses the same M40 as other elemental releases. No undead auto-KO or recovery. |
| MYK-A12 Spellbreak | Concept sound; fix effect order before implementation. | Specify whether selected Protect/Shell is removed before damage calculation. Recommend successful A check, applicable interception resolution, remove selected status if still present, then compute HP damage with the remaining defenses and resolved interception modifiers. A selected status consumed by an interception causes no refund or retargeting. Preserve own enchantment; neither its element, Flare penetration, nor siphon is carried. |
| MYK-A13 Arcane Release | Keep provisional 14 MP / M40, or M44 Flare, pending actual formula comparison. | Replace vague 'ordinary damaging-spell hit resolution' with the explicit shared A check, unless another exact handler is deliberately chosen. Enchantment consumption is a real cost: it removes future Fight benefits and Spell Parry fuel even on miss/immunity. Already engaged enchant-and-strike earned its own action, so do not double-count that action as completely lost setup. Weak natural magical growth can make Release situational; that is acceptable beside physical strikes, but preview actual Magic Power results. |
| MYK-A14 Break Blade | Keep 24 MP / r1 / single normal S as a first test. | 'No accuracy bonus' must mean no intrinsic or Spellweave bonus, not rejection of normal Concentrate or Turbo MP effects when legally equipped instead. It retains existing enchantment but does not use its riders. It has no HP damage, so cannot consume Fury as a physical attack or benefit from outgoing damage boosts. |

### Concrete cross-document issues to resolve

1. **Spellbreak order is currently under-specified.** The axe Shatter Guard explicitly dispels Protect before calculating damage; Spellbreak currently only says 'on a successful hit.' Different implementations produce different damage and barrier consumption. Choose and document the order above or an explicit alternative.
2. **Arcane Release accuracy is currently less precise than the common A/S notation.** Its category is approved Magic, but that does not define its hit routine. Use explicit A plus ordinary legal accuracy supports and caps. Clarify that a fully resolved miss still spends the enchantment and establishes Magic; an invalid uncommitted action does neither.
3. **Spell Parry currently consumes an enchantment after a physical hit check succeeds, without explicitly requiring positive pending HP damage.** A zero-damage hit could therefore destroy Release fuel and the maintained enchantment. Recommend consume only when the action has positive physical HP damage to reduce after applicable prior redirection/mitigation. This is a refinement to consumption eligibility, not changing the approved 50% reduction to immunity.
4. **Accuracy wording must remain support-specific.** Break Blade receives no Spellweave accuracy bonus. It can instead equip Concentrate and receive that support's ordinary S benefit; it cannot equip both. Clear Voice is Moogle-only, so its presence in the Spellblade validation checklist must not imply a legal Viera Clear Voice build. An allied Bard's buffs are separate legal interactions.
5. **Axe addendum global totals are stale.** Its final section says the full project retains 116 entries/72 items while current class/Spellblade sheets say 122/78. This does not change any axe ability, but should be corrected when canonical documents are next updated. Do not use old global totals for record-capacity tests.

### Spellweave and resource stress cases

- Fire enchant-and-strike is Magic sequence but physical damage. Fight, then Arcane Release can alternate Physical to Magic; Release then another enchantment is Magic to Magic and gives no bonus. Break then Fight can establish a sequence even when Petrify fails, but the failed Break already cost 24 MP and its action. This is not a free damage setup.
- A Red Mage/Spellblade may use its legal original spells and these weapon actions; it does not also gain Summoning. A Dancer/Spellblade uses a rapier and its actual acquired Magic Power for Release. Assassin/Spellblade and Summoner/Spellblade cannot use the command with their normal weapon permissions. Trained stats survive a switch to an eligible main job.
- Osmose recasting plus Spell Parry can deliver a modest strike, recover enemy MP, and refresh a consumable defense each turn. At full siphon it can be resource-positive, particularly with Half MP, but one enemy action consumes the enchantment and additional attacks remain. Half MP excludes Spellweave and Concentrate. Count enemy MP depletion and actual hit rates before calling this an infinite loop.
- Wisp Exposure and Inspired Magic can amplify Release, not the physical enchant-and-strike or Spellbreak. Fury can amplify those physical strikes even when their sequence tag is Magic, but not Release. The tag should never determine both damage type and sequence type in a shared handler.

## Sources and why they matter

[Terence's original FFTA mechanics research](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262) lists Bishop Break at 20 MP/r3/S and Assassin Rockseal at 32 MP/r1/S. Those frame Break Blade's 24 MP/r1 tradeoff: ranged cheaper Petrify exists on another race, while the same-race non-incanted alternative is more expensive. The same source documents that Protect/Shell and attack supports affect formula inputs and that command effects have explicit hit routines; this is why vague categories are insufficient.

[Square Enix's Dark Knight guide](https://na.finalfantasyxiv.com/jobguide/darkknight/) provides a genuine ally/self barrier precedent for The Blackest Night; the proposed FFTA life cost, action timing, and no-refund rule are our design. [Square Enix's Samurai guide](https://na.finalfantasyxiv.com/jobguide/samurai/) explicitly gives Higanbana damage over time; it does not dictate FFTA pulse count or damage. These live guides were checked September 14, 2026. Their current MMO numbers are not balance targets for this project.

## Bloat and acquisition gate

Mystic Knight now has 3,400 action AP and fourteen actions versus its original 1,600 action AP/eight actions. That is not fourteen mandatory skills, but it doubles much of the mastery commitment and gives one secondary broad physical, magical, sustain, control, and dispel access. Do not add stronger teaching weapons to justify more lessons. Keep optional sidegrade lessons at appropriate existing tiers; do not require learning the whole command to use its first useful build.

For any adopted addition, count one concept/lesson even on shared races, explicitly price its teaching equipment, and verify more-than-eight menu/mastery/save capacity. No extra supports/reactions, growth inflation, or new job prerequisites follow automatically. The final shortlist's smaller scope preserves reasons to mix jobs and leaves space to adjust demonstrated weak actions after actual play.
