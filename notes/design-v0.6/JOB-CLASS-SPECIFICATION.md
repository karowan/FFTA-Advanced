# FFTA: eight-job expansion specification

Design version 0.6 — expanded Spellblade on the adopted council foundation, September 14, 2026

**Current approved design for our vanilla USA FFTA expansion.** The [council’s reconciled recommendations](BALANCE-COUNCIL.md) form the version 0.5 foundation, retaining its 116 entries; six approved Spellblade additions bring the current total to 122. [Spellblade expansion](SPELLBLADE-EXPANSION.md) records the new concepts, categories, and provisional numerical/teaching targets. Values still require implementation and gameplay testing. [Design principles](JOB-DESIGN-PRINCIPLES.md) preserve job identity and mixing.

## 1. Roster and progression

Every race receives exactly two new job options in this roster. Eight job concepts require ten race/job implementations. The Soldier/Gladiator axe additions extend existing jobs and do not increase that job count. Green Mage remains a separate candidate.

| Race | Job | Availability | Required mastered action abilities |
|---|---|---|---|
| Human | Samurai | Exclusive | Fighter 2 + Ninja 1 |
| Human | Dark Knight | Shared with Bangaa | Paladin 2 + Black Mage 2 |
| Bangaa | Viking | Exclusive | Warrior 3 + White Monk 1 |
| Bangaa | Dark Knight | Shared with Human | Gladiator 2 + Bishop 1 |
| Nu Mou | Chemist | Shared with Moogle; starter | None |
| Nu Mou | Geomancer | Exclusive | Sage 2 + Black Mage 3 |
| Moogle | Chemist | Shared with Nu Mou; starter | None |
| Moogle | Bard | Exclusive | Animist 2 + Juggler 2 |
| Viera | Dancer | Exclusive | Fencer 2 + White Mage 2 |
| Viera | Mystic Knight | Exclusive | Red Mage 2 + Elementalist 2 |

Numbers count actions permanently learned by the same character, not character levels or job levels. Reaction, support, and combo abilities do not count. Meeting one branch does not satisfy a requirement on another character. The existing prerequisite branches are recorded in [the progression outline](JOB-EXPANSION-DESIGN.md#full-progression-paths).

**Current starter decision:** Chemist has no job prerequisite for either race. It becomes selectable at the first normal opportunity to change jobs, while its skills still use equipment/AP learning. Samurai, Viking, and Dancer remain prerequisite jobs. Additional starter candidates are being considered in [STARTER-JOB-INSPIRATION.md](STARTER-JOB-INSPIRATION.md), not automatically added to this roster. Vanilla Moogles do not have White Mage; no such job access is introduced here.

Chemist is a starter; Viking and Dancer are intended to be accessible early after meeting prerequisites. The other jobs are intended for the middle of the campaign. Exact timing depends on equipment and AP access, not just the prerequisite counts. The previous suggestion to make several advanced concepts into starters was not adopted.

## 2. Shared rules

The current design contains **122 entries: 78 actions, 18 supports, 18 reactions, and eight combos**. Eight job concepts require ten racial job implementations. Mystic Knight has 14 actions; each other new job currently has eight. The twelve axe entries are added inside the two existing command sets. These counts describe lessons, not proven available ROM records.

### Learning, equipment, and source lineage

Keep vanilla equipment/AP learning, one freely selected secondary action set, one support, one reaction, and one combo. Original Alchemist retains its fixed ordinary Item command in addition to its two learned command sets; no other job gains a third learned set. A mastered lesson does not grant another race's jobs, new equipment permissions, or a second equipped support. Only action mastery counts toward job gates. Job switching does not recalculate accumulated stats; level-one templates below are generation/test templates, not job-change bonuses.

Sources identify inspiration. Adaptation and thematic redesign may freely change mechanics; original extensions are intentional inventions grounded in a job's identity. None of the new numbers, teaching items, racial assignments, or recipes is claimed to be a direct canonical port. The [lineage register](JOB-THEME-AUDIT.md) covers every lesson.

### Formula, targeting, and action categories

**P** is one primary-weapon physical hit's damage reference, including relevant defenses. 1.30P means a final-damage multiplier, not +30% Attack. New A-abilities do not call Fight, crit, copy weapon status procs, or use a second weapon. Weapon-elemental attacks use the primary weapon's element. Healer remains restorative and cannot be converted into damaging/draining attacks. **M24** is a proposed magical-power reference using Magic Power/Magic Resistance, not a verified ROM field. Original attack/defense supports and Protect/Shell modify their vanilla formula inputs; do not equate them with our final-damage multipliers. [Mechanics][mechanics].

**A** is ordinary attack-style accuracy; **S** is ordinary status accuracy, including immunity; **Sure** is a legal willing-target effect. S multipliers act on final ordinary success chance. Listed percentage-point changes apply after the ordinary calculation, with their stated cap; they never override immunity or a preventing reaction. Theft uses the original transaction's own accuracy and eligibility rather than an invented S check.

**rN** is Manhattan tile distance; r1 excludes diagonals. **Cross** is center plus four orthogonal neighbors. **Self cross** centers on the user. **Line N** is a selected cardinal line excluding the user and stopping at impassable terrain. **Any** permits friendly fire. Single-target range has height limit 3, melee limit 2; cross neighbors are within 2 height of center and line targets within 2 of caster. Projectiles require line of sight; songs, dances, and terrain effects do not. Preview all targets and actual accuracy before commitment. Each new action resolves immediately using one ordinary action; none grants an extra action or immediate movement.

Damage type and Spellweave sequencing are separate. Both Spellblade modes establish **Magic** once but their strike deals **physical** damage. Battle Chant/Fury can boost that strike; Wisp Exposure/Magickal Refrain cannot. Enchantment then Red Magic is Magic-to-Magic, not alternation. New actions never gain Doublecast; original eligible magic remains unchanged. Original Double Sword/Fight still works, but new attacks use only one primary weapon.

### Support and buff interactions

Mastered supports work on every legal current job of their character without the teaching job's command or weapon. Full rules and two external-job examples appear in [the support sheet](SUPPORT-SKILL-DESIGN.md). They integrate with applicable original commands, not only the new IDs.

Unless explicitly included, new outgoing damage bonuses exclude fixed/percentage damage, instant KO, HP/MP exchange, costs, item effects, drain recovery, damage-over-time, reactions, and combos. Direct restorative healing includes spells/techniques; Pharmacology applies to item restoration; Recuperation applies to incoming direct restoration. An increase to actual drain damage may indirectly raise recovery, then the drain cap applies; never multiply recovered HP a second time. Defensive modifiers act on their stated direct damage category, not HP costs or damage-over-time.

Beneficial/harmful statuses use explicit tags, including new temporary effects. Equipment stats, fields, passive lessons, and reaction readiness are not statuses. Poise snapshots the presence of a beneficial status at incoming-action start. Opportunist snapshots the target before outgoing damage; its own rider cannot qualify the same hit. Wisp Exposure begins after Wisp damage and never boosts that hit.

Encouragement recognizes a newly applied **persistent** beneficial status on another ally, once per recipient/action. Immediate turn/CT effects such as Smile and Quicken, refreshing a status, self-targeting, mere cures/healing, and reactions do not qualify. Its separate HP recovery receives only the recipient's incoming-healing modifier, never an outgoing modifier such as Composure or Magick Boost. Resolve base healing and this additional healing as separate events, rounding after each event's combined multipliers and respecting missing HP.

Spellweave records one qualifying voluntary action category at completion even on a miss. Its first action gets no bonus. Wait and unclassified actions retain the previous category without a bonus; repeating a category does not earn the bonus. Same-category Doublecast establishes Magic once; mixed/ambiguous multi-cast clears the sequence. Reactions, movement, and forced actions do not create a category. Job change, KO, Petrify, battle end, or removing the support clears the sequence. Show the next eligible category. Fury uses physical damage classification even when that action's sequencing category is Magic, and is consumed only once.

### Duration, recovery, and payment

Named vanilla statuses use original duration, removal, immunity, and stacking except an expressly listed duration such as Encore's T2 Haste. **T2** expires after the target finishes its second subsequent turn, excluding application turn. Reapplication refreshes rather than stacks. KO, Petrify, battle end, and job change clear custom effects; Dispel removes beneficial effects. Appropriate broad remedies clear custom harmful tags. Last Resort is indivisible: remove its benefit and drawback together. Exposed and reaction charges have their explicitly shorter timers. Spellblade follows its persistent-enchantment rules.

Distinct applicable modifiers multiply once; round down after combining modifiers for that effect. Same-name effects do not stack. Grace changes A-type facing treatment, not SRes or positional damage riders. Attunement refunds only actually paid MP after an eligible success, never per area target or in advance. Clear Voice discounts explicitly tagged incanted magic and songs; it does not discount every MP-using martial technique.

New restoration targets non-undead allies, capped by missing HP/MP. Original commands retain undead behavior. Revival targets eligible KO units only, not removed or permanently lost units, and is not improved by Pharmacology, Recuperation, or other direct-healing modifiers.

HP costs are fractions of maximum HP rounded up, minimum 1. Pay after target validation but before hit checks, once for the committed action, and leave at least 1 HP. Costs are not damage and trigger no reactions or injury effects. Bloodcasting pays 2 HP per computed MP plus native HP costs, with no damage-mitigation discount. Validate the sum of independently priced components before commitment; never make a second component free. This rule does not grant a currently illegal cross-race Doublecast build. Healing may provide positive net HP while spending an action.

At 200 maximum HP: Blood Edge costs 20 HP; Abyssal Blade costs 30 HP + 10 MP, or **50 HP** with Bloodcasting; Unholy Sacrifice costs 40 HP + 14 MP, or **68 HP** with Bloodcasting. Sanguine Sword dealing 40 actual HP damage recovers 20 HP; dealing 200 recovers only its 40-HP cap. With Bloodcasting it also pays 12 HP instead of its 6 MP.

Drain uses actual positive resources removed: no allies, overkill, immunity, absorption, or overdraw. HP recovery respects the individual action cap. Undead reverse attempted HP recovery into user damage that can KO but triggers no reaction; MP drain reverses attempted recovery into MP loss capped at current MP. No new effect generates JP.

Validate all recipe ingredients together and deduct once atomically, never per recipient. No mission-item substitutions or automatic spending of rarer medicine. Long Throw does not turn an area mixture into a ranged single-target action. Auto-Potion requires an explicit pre-battle Potion/Hi-Potion choice, defaults to Potion, and uses no automatic replacement when stock is empty. Auto-Cureall follows the ordinary Cureall cure list plus custom harmful tags included in shared broad-remedy integration; it never prevents KO or an uncurable effect. One Cureall covers eligible ailments of that enemy action; zero stock means no interception.

### Reactions, counters, and combos

All new reactions activate **100% when eligible** unless expressly stated. There is no blanket until-next-turn lock. Apply only an entry's specific lock (Auto-Potion locks after actual consumption until the next own turn). Eligibility or a miss alone consumes no resource or lock. Existing vanilla reactions retain their own behavior.

One multi-hit/multi-cast enemy action is one opportunity for a new reaction. A defensive interception begins after a successful relevant hit check and before application; its reduction covers all eligible components of that action. Retaliation/recovery resolves at most once after the complete action, requires survival and ordinary reaction capability, and targets the original attacker if still legal. Existing incapacitation may prevent interception, but an ailment intercepted before application cannot prevent its own interception. No triggers from allies, self-costs, poison, combos, other reactions, or reaction/reflection chains. No counter recursively triggers another counter.

Spell Parry consumes an active qualifying enchantment for **50% physical HP damage reduction** across one enemy action; it does not negate that action, statuses, or magical components. Misses do not spend the enchantment. Fury/Magick Boost store at most one charge, not permanent stat gains. Encore grants temporary Haste, not an immediate turn, and cannot trigger Encouragement.

Each combo below specifies its original chain participation profile (power/range/hit) separately from the primary weapon's initiation range. Preserve original JP behavior and ordinary weapon-element handling; no new damage/status/support/enchantment/drain rider. Soldier/Gladiator retain existing combo profiles with only axe acceptance/animation added.

New effects follow the relevant original laws: element, item, theft, healing, equipment, and any mapped command restrictions. A new command name creates no law exemption.

## 3. Stats, movement, and equipment

These are **proposed average gains per level**, before the existing stat caps. A decimal is a growth expectation, not a promise of a fractional displayed stat. For example, 1.5 Speed means a target average of one and a half points per level, using the original growth system. Values deliberately avoid making one new job best at physical damage, magic, durability, and speed together.

| Race/job | HP | MP | Weapon Atk | Weapon Def | Magic Power | Magic Res | Speed |
|---|---:|---:|---:|---:|---:|---:|---:|
| Human Samurai | 7.2 | 2.8 | 8.6 | 8.0 | 6.8 | 7.2 | 1.4 |
| Human Dark Knight | 8.0 | 2.0 | 9.0 | 7.6 | 6.8 | 7.0 | 1.0 |
| Bangaa Dark Knight | 8.8 | 1.6 | 9.2 | 8.2 | 6.0 | 6.8 | 0.9 |
| Bangaa Viking | 8.8 | 2.8 | 8.4 | 8.2 | 7.6 | 6.8 | 1.0 |
| Nu Mou Geomancer | 6.6 | 3.6 | 5.8 | 7.0 | 8.6 | 8.6 | 1.0 |
| Nu Mou Chemist | 6.8 | 2.8 | 6.4 | 7.6 | 7.6 | 8.4 | 1.2 |
| Moogle Chemist | 6.4 | 2.6 | 6.8 | 7.2 | 7.2 | 8.0 | 1.5 |
| Moogle Bard | 6.0 | 3.4 | 6.0 | 6.8 | 7.8 | 8.8 | 1.4 |
| Viera Dancer | 5.8 | 2.4 | 7.2 | 6.4 | 7.2 | 7.6 | 1.8 |
| Viera Mystic Knight | 6.8 | 3.0 | 8.2 | 7.6 | 7.2 | 8.2 | 1.4 |

The intended shared-job distinction is modest: Bangaa Dark Knight is sturdier and slower; Moogle Chemist is quicker while Nu Mou Chemist has stronger magical development. Consumable healing itself does not scale with Magic Power.

### Initial stat templates

These are proposed **level-one generation templates**, used only if a character is generated directly in that job during testing or a future supported recruitment extension. They are not bonuses applied on job change. Retain the original generation variation and level-up algorithm. Normal recruitment tables are unchanged in this version.

| Race/job | HP | MP | WAtk | WDef | MPow | MRes | Speed |
|---|---:|---:|---:|---:|---:|---:|---:|
| Human Samurai | 36 | 28 | 86 | 80 | 68 | 72 | 106 |
| Human Dark Knight | 40 | 20 | 90 | 76 | 68 | 70 | 99 |
| Bangaa Dark Knight | 44 | 16 | 92 | 82 | 60 | 68 | 97 |
| Bangaa Viking | 44 | 28 | 84 | 82 | 76 | 68 | 98 |
| Nu Mou Geomancer | 33 | 36 | 58 | 70 | 86 | 86 | 97 |
| Nu Mou Chemist | 34 | 28 | 64 | 76 | 76 | 84 | 99 |
| Moogle Chemist | 32 | 26 | 68 | 72 | 72 | 80 | 105 |
| Moogle Bard | 30 | 34 | 60 | 68 | 78 | 88 | 105 |
| Viera Dancer | 29 | 24 | 72 | 64 | 72 | 76 | 112 |
| Viera Mystic Knight | 34 | 30 | 82 | 76 | 72 | 82 | 106 |

All ten profiles have Status Resistance 50 and neutral innate elemental affinities. No innate status immunity, flight, regeneration, permanent Haste, or free equip-ability is granted. Evade below is the job's base value, not a universal percentage chance to dodge.

| Job/profile | Move | Jump | Evade | Allowed weapons | Body/head | Shield |
|---|---:|---:|---:|---|---|---|
| Samurai | 4 | 3 | 50 | Katanas | Clothing, heavy armor, or robes; hats or helmets | No |
| Dark Knight, both races | 3 | 2 | 40 | Swords, greatswords, broadswords | Clothing or heavy armor; hats or helmets | Yes with a one-handed sword |
| Viking | 3 | 2 | 40 | New two-handed axes | Clothing or heavy armor; hats or helmets | No |
| Geomancer | 3 | 2 | 45 | Rods, maces | Clothing or robes; hats | No |
| Chemist, Nu Mou | 4 | 2 | 45 | Knives, maces | Clothing or robes; hats | No |
| Chemist, Moogle | 4 | 3 | 45 | Knives, maces | Clothing or robes; hats | No |
| Bard | 4 | 3 | 45 | Instruments, knives | Clothing or robes; hats | No |
| Dancer | 4 | 3 | 55 | Knives, rapiers | Clothing; hats | No |
| Mystic Knight | 4 | 2 | 45 | Rapiers, sabers | Clothing or heavy armor; hats or helmets | Yes |

Retained after the council review: Samurai's offense now develops through Weapon Attack, avoiding a second mandatory damage stat; Geomancer has MP growth for its stronger, resource-using toolkit. The other new-job growths remain provisional. These are our design targets. Soldier and Gladiator retain their original growths and armor permissions.

All categories are vanilla except the explicitly added Axe family. Racial armor animations and permission fields need validation. Samurai teaching weapons are new spirit-channeling variants, not edits to existing named katanas.

## 4. Samurai — Human

**Iaido — Human.** Requires a primary katana for every action. All damage uses physical P; Murasame uses target maximum HP. Silence, Reflect, Return Magic, and Doublecast do not apply. Mastered techniques need no spare or matching named sword; no breakage.

**Centered:** a visible non-stacking T2 buff from successful Ashura or Counter Draw. The next damaging Iaido other than Ashura, or Murasame, consumes it at execution for ×1.25 damage/healing for the whole action, including a miss. No bonus to MP damage, status, Fight, counters, combos, or secondary sets. Kiyomori neither consumes nor benefits. Clear on expiry, Dispel, KO, Petrify, battle end, job change, or primary weapon change/loss.

Use a katana on Ninja/Iaido, or mix Samurai with Hunt or White Magic. Concentrate improves reliability; Double Sword takes the same support slot and only doubles ordinary Fight.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| SAM-A1 Ashura | 100 | 4 MP; r1 enemy; A; 1.10P non-elemental, positive damage grants Centered. | Thematic redesign: Decisive draw that builds composure; original attack-and-prepare mechanic. [Inspiration][sam] |
| SAM-A2 Wind Draw | 150 | 4 MP; cardinal line 3, enemies; A per target; 1.00P Wind. Centered eligible. | Thematic redesign: Original cutting wind released through katana technique. [Inspiration][sam] |
| SAM-A3 Osafune | 200 | 6 MP; r2 enemy; A; 0.85P non-elemental and remove up to 10 MP after positive damage; no MP recovery. | Thematic redesign: MP-cutting blade spirit redesigned to also contribute HP damage. [Inspiration][sam] |
| SAM-A4 Murasame | 200 | 8 MP; r2 center, ally cross including user; Sure; restore 35% each target's max HP, cap 140 before Centered; cap final recovery by missing HP. | Thematic redesign: Healing blade spirit, with reach and scaling chosen for frontline support. [Inspiration][sam] |
| SAM-A5 Kiyomori | 250 | 10 MP; self cross, allies; Sure; Protect + Shell using ordinary status rules; no Centered consumption. | Thematic redesign: Protective blade spirits; group defense earns its action through multiple allies. [Inspiration][sam] |
| SAM-A6 Guarding Draw | 250 | 6 MP; r1 enemy; A; 1.00P non-elemental; gain Protect after a valid attack attempt, including a miss. Centered eligible. | Thematic redesign: Original guarded sword strike that combines pressure with self-protection. [Inspiration][sam] |
| SAM-A7 Kiku-ichimonji | 300 | 10 MP; r4 enemy; A; 1.45P non-elemental. Centered eligible. | Thematic redesign: Far-reaching blade spirit redesigned as a precise ranged finisher. [Inspiration][sam] |
| SAM-A8 Moon Blossom | 400 | 16 MP; self cross, enemies; A per target; 1.35P non-elemental; positive damage to any enemy grants Regen once. Centered eligible for the entire action. | Thematic redesign: Original culminating spirit release, with offensive and sustaining roles. [Inspiration][sam] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| SAM-S1 Composure | 250 | During own turn, direct physical/magical HP damage and direct restorative HP healing ×1.25 if no voluntary movement occurred before action. Moving afterward is allowed. Item and drain recovery excluded. | Cross-job support design: Calm, deliberate action; useful with attacks, techniques, and magic. [Inspiration][sam] |
| SAM-S2 Poise | 350 | Incoming direct physical/magical HP damage ×0.75 while at least one tagged beneficial status is active at incoming-action start. Qualifying statuses: Protect, Shell, Haste, Regen, Float, Invisible, and tagged temporary positive effects such as Centered, Last Resort, or an enchantment; additional statuses add nothing. Costs/DoT excluded. | Cross-job support design: Maintaining composure under protection; benefits can come from allies or another command. [Inspiration][sam] |
| SAM-R1 Blade Ward | 300 | Primary katana required. Incoming enemy physical direct HP damage ×0.65 for the whole action, including physical abilities. No counter; no cross-action lock. | Thematic redesign: Original blade defense with a broader trigger than a Fight-only evasion move. [Inspiration][sam] |
| SAM-R2 Counter Draw | 350 | After surviving adjacent enemy physical HP damage, primary katana counters once for 1.00P non-elemental with A accuracy. Positive counter damage grants Centered; counter never consumes/uses it. No cross-action lock. | Thematic redesign: Original reactive draw that prepares the next deliberate technique. [Inspiration][sam] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| SAM-C1 Crescent Combo | 100 | katana. Vanilla chain participation profile: Ninja Combo: power 5%, participation range 2, hit 100% Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 5. Dark Knight — Human and Bangaa

**Dark Arts — Human and Bangaa.** Sword/greatsword/broadsword required for damaging/draining sword arts. Dark Mind and self-mode Last Resort are weapon-free; Last Resort's optional commitment strike accepts any damaging primary weapon at r1, not Healer. All strikes/drains are physical; Silence, Reflect, Return Magic, and Doublecast do not apply.

Last Resort's initial strike precedes the new buff; an already active buff follows ordinary rules. Its outgoing multiplier applies only to eligible direct physical damage, not fixed/percentage effects, items, reactions, combos, MP damage, or a second drain-recovery multiplier. Its incoming physical drawback remains linked to the benefit. At low HP, Desperation can activate after paying a sacrifice; the threshold is 35%, not 40%.

Human Dark Knight/Blue Magic and Bangaa Dark Knight/Prayer are legal. Axe Gladiator/Dark Arts or Viking/Dark Arts can use Dark Mind and Last Resort but cannot use sword-gated drain/sacrifice moves while holding an axe. Bloodcasting and Desperation cannot be equipped together.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| DRK-A1 Blood Edge | 100 | 10% max HP; r1 enemy; A; 1.50P Dark. | Original extension: Original introductory sword technique built around the job's health sacrifice. [Inspiration][drk] |
| DRK-A2 Sanguine Sword | 150 | 6 MP; r2 enemy; A; 0.95P non-elemental; recover 50% actual HP removed, cap 20% user's max HP. | Adaptation: HP-draining sword art. [Inspiration][drk] |
| DRK-A3 Infernal Strike | 200 | 4 MP; r2 enemy; A; 0.75P non-elemental HP damage. After positive HP damage remove MP equal to floor(20% of actual HP removed), capped at 16 and target current MP; restore exactly actual MP removed, capped by missing MP. | Adaptation: MP-draining sword art. [Inspiration][drk] |
| DRK-A4 Dark Mind | 200 | 8 MP; self; Sure; Shell plus restore 20% max HP, cap 100. Weapon-free. | Adaptation: Personal protection against magic. [Inspiration][drk14] |
| DRK-A5 Last Resort | 250 | 8 MP; self OR r1 enemy; self mode Sure, enemy mode A; enemy mode first deals 1.00P weapon-elemental using any primary weapon. Then either mode grants T2 outgoing physical HP damage x1.25 and incoming physical HP damage x1.20 as one indivisible buff. Apply the buff even if the attack misses, but only after the initial strike so it cannot boost itself. Outgoing bonus excludes fixed/percentage damage, items, reactions, combos, MP damage and a second multiplication of drain recovery. The linked incoming drawback applies to direct physical HP damage, not costs or damage-over-time. Enemy strike mode is unavailable with Healer; self mode remains legal. | Adaptation: Attack at the expense of defense. [Inspiration][drk11] |
| DRK-A6 Crushing Blow | 300 | 10 MP; r2 enemy; A then S x0.5 after positive damage; 1.15P weapon-elemental with Stop attempt. | Adaptation: Sword damage with Stop. [Inspiration][drk] |
| DRK-A7 Abyssal Blade | 300 | 10 MP + 15% max HP; line 3, any units; A per target; weapon-elemental 1.40P / 1.25P / 1.10P by tile distance. | Adaptation: Health sacrifice, distance-falloff wave. [Inspiration][drk] |
| DRK-A8 Unholy Sacrifice | 400 | 14 MP + 20% max HP; self cross, any units except self; A then S x0.5 per damaged target; 1.75P Dark plus Slow attempt. | Adaptation: Health sacrifice, dark area damage and Slow. [Inspiration][drk] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| DRK-S1 Desperation | 300 | Direct physical/magical HP damage ×1.50 while HP ≤35% maximum, checked after paying action costs. No bonus to fixed/percentage damage, instant KO, costs, items, healing, drain recovery, MP damage, damage-over-time, reactions, or combos. | Cross-job support design: Dangerous offense at low health, usable by martial and magical builds. [Inspiration][drk] |
| DRK-S2 Bloodcasting | 400 | Eligible voluntary actions pay 2 HP per computed MP and zero MP; native HP costs are additional; total payment leaves ≥1 HP. For multiple subcasts, pay the **sum of all subcast MP costs**, once before the committed action; if dynamic costs can change, reserve the full validated payment and reconcile without overdrawing. Costs never trigger R, damage protection, Encouragement, or HP-loss mechanics. No free or discounted second subcast. | Cross-job support design: Trade life for action resources across spell and technique sets. [Inspiration][drk] |
| DRK-R1 Dark Ward | 300 | Incoming magical direct HP damage ×0.75 for triggering action; after survival grant ordinary Shell. Already-Shelled users still receive the .75 reduction, but Shell does not stack. No cross-action lock. | Original extension: Original reactive variant of the Dark Mind ward. [Inspiration][drk14] |
| DRK-R2 Vengeful Pulse | 350 | After surviving enemy direct HP damage, retaliate against attacker within r3 for Dark damage equal to50% of HP actually lost, capped at 25% user max HP. No hit roll; apply elemental immunity/absorption. One return after the entire action; no cross-action lock. | Original extension: Original dark retaliation fueled by injury. [Inspiration][drk] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| DRK-C1 Abyss Combo | 100 | sword/greatsword/broadsword. Vanilla chain participation profile: Knight Combo: power 10%, participation range 1, hit 100% Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 6. Viking — Bangaa

**Reaving — Bangaa.** Uses the new two-handed Axe family. Strong-Arm/Pillage require an axe. Thunder, Stormcall, Thundaga, and Tsunami are incanted magic blocked by Silence; lightning actions follow ordinary applicable Reflect/Return Magic behavior. Tsunami is environmental and neither Reflected nor Returned. Theft and War Cry work while Silenced. No Doublecast.

Resolve each eligible original theft transaction independently before HP damage, using its original accuracy, protection, loot ownership, and depletion rules. A damage miss/zero damage does not remove the theft attempt. Stolen defenses change the following damage calculation and preview. Never steal the same depleted item again. No generic S roll replaces the original handler.

Viking/Gladiator offers two compatible axe sets; Viking/Bishop adds support magic. Bishop/Reaving can cast storms but cannot perform axe theft. Tsunami's dry-ground displacement is distinct from its optional water-adjacent MP removal; neither grants water traversal.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| VIK-A1 Thunder | 100 | 6 MP; r4 one target; A; M24 Lightning. | Adaptation: Lightning spell. [Inspiration][vik] |
| VIK-A2 Pickpocket | 100 | 0 MP; r1 enemy; use the original Steal Gil action's hit handling, payout and per-target restrictions rather than assuming S. | Adaptation: Gil theft. [Inspiration][vik] |
| VIK-A3 Strong-Arm | 200 | 6 MP; r1 enemy; 0.85P weapon-elemental with one A check for damage. Attempt original Steal Accessory independently using that original transaction's own accuracy and restrictions. Resolve eligible theft before HP damage; a damage miss or zero damage does not prevent the theft roll. | Adaptation: Damage plus item theft, adapted to accessories. [Inspiration][vik] |
| VIK-A4 War Cry | 200 | 8 MP; self cross allies; Sure; remove Blind, Silence and Confuse, then T2 reduce incoming hostile S-check chances by 25 percentage points, floor zero. | Adaptation: Ailment resilience, not Attack. [Inspiration][vik] |
| VIK-A5 Stormcall | 250 | 12 MP; r4 one enemy; A for M28 Lightning, followed after positive damage by ordinary S chance to apply Slow. | Original extension: Original focused storm that damages and slows, inspired by Viking storm magic. [Inspiration][vik] |
| VIK-A6 Pillage | 300 | 10 MP; r1 enemy; 1.00P weapon-elemental with A damage check. Independently execute original Steal Armor against body armor using its original A-type check and restrictions, before HP damage. | Adaptation: Damage plus armor theft. [Inspiration][vik] |
| VIK-A7 Thundaga | 300 | 20 MP; r3 center, cross, any units; A per target; M40 Lightning. | Adaptation: High-tier lightning magic. [Inspiration][vik] |
| VIK-A8 Tsunami | 400 | 18 MP; r4 center, cross, any units; A per target; M36 Water. Positive damage pushes surviving targets one tile directly away from center when legal. On center tile, use direction away from caster; if center equals caster or direction ties, no push. If mapped water is on the caster tile or an orthogonally adjacent tile within 2 height, positive damage also removes up to 8 MP per target, with no recovery. No collision damage, illegal landing or push from immune targets. | Thematic redesign: Sea power redesigned to function on land, with water proximity enhancing its effect. [Inspiration][vik] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| VIK-S1 Sea Legs | 150 | Immune to forced displacement and Immobilize. No Slow immunity, added movement, water traversal, or terrain-damage immunity. | Cross-job support design: A raider keeps their footing; transferable positional protection. [Inspiration][vik] |
| VIK-S2 Opportunist | 350 | Direct physical/magical HP damage ×1.30 against an enemy carrying a qualifying harmful status at action start. Harmful statuses include Poison, Blind, Silence, Slow, Immobilize, Disable, Confuse, Sleep, and tagged custom debuffs; no self-qualification by the same hit, no stacking for multiple statuses. | Cross-job support design: A raider exploits openings created by any ally or command. [Inspiration][vik] |
| VIK-R1 Absorb Damage | 300 | After surviving enemy direct HP damage, heal 30% of HP actually lost, capped at 15% user max HP per incoming action. Round down; no cross-action lock. | Adaptation: Damage recovery; a chance and lockout are added here. [Inspiration][vik] |
| VIK-R2 Gil Snapper | 50 | After surviving a critical physical enemy hit, gain floor(0.5 × HP actually lost) gil, capped at 50gil per battle per unit. Activation 100%; no cross-action lock, no inventory loss to enemy, no reaction from allies/costs. | Adaptation: Gil after a critical hit; payout and battle cap are ours. [Inspiration][vik] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| VIK-C1 Tempest Combo | 100 | axe. Vanilla chain participation profile: Sword Combo: power 10%, participation range 1, hit 100% Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 7. Geomancer — Nu Mou

**Geomancy — Nu Mou.** Weapon-free nature arts; damage uses Magic Power/Magic Resistance. No Silence, Reflect, Return Magic, or Doublecast. Every action works without terrain affinity.

**Nearby affinity:** inspect caster tile and four orthogonal neighbors within 2 height; rock/stone, vegetation, water/wetland, wood/heat, and snow/ice groups supply at most one relevant bonus. Unknown tiles give no affinity but disable no action. Nearby inaccessible water can be sensed but not entered. Gaia Surge always offers Wind, plus mapped local elements; Nature's Wrath now always uses Wind independently of learned actions. Float does not prevent affinity.

**Frost field:** one cross per caster, replacing the previous field. Expires after the caster's second subsequent turn, or on caster KO/Petrify/job change/battle end. Each entered field tile adds one movement cost for grounded allies/enemies; overlapping fields never add more. Float/flying/Surefoot ignore the surcharge, not other tile legality. No entry damage, impassability, reaction triggers, or changed affinity; a field does not qualify its own cast for an ice bonus.

Wisp Exposure starts after damage, refreshes without stacking, and a weaker application cannot refresh a stronger one. Immunity to its custom effect blocks the rider; elemental immunity/absorption prevents positive-damage riders. Updraft can combine with an ally's Light Foot for +2 Move but never stack with itself. Time Mage/Geomancy and Alchemist/Geomancy are legal weapon-free mixes.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| GEO-A1 Stone Pulse | 100 | 4 MP; r3 center/cross, any except caster; A. M26 Earth; rock affinity multiplies damage by 1.20. | Thematic redesign: Original reliable earth pressure; terrain rewards damage rather than unlocking the spell. [Inspiration][geo] |
| GEO-A2 Tanglevine | 150 | 6 MP; r3 one enemy; A, then S after positive damage. M24 non-elemental and Immobilize; vegetation adds 15 percentage points to final S, capped at 95% before defensive reductions. | Thematic redesign: Binding vegetation with a useful damage baseline and a stronger native control effect. [Inspiration][geo] |
| GEO-A3 Torrent | 200 | 8 MP; r3 center/cross, any except caster; A. M28 Water; water affinity pushes each positively damaged target one tile in one cardinal direction selected for the whole cast. Illegal pushes fail individually; damage remains. | Thematic redesign: Original wave control that breaks formations rather than copying a transformation rider. [Inspiration][geo] |
| GEO-A4 Updraft | 200 | 8 MP; r3 center/cross, allies including self; Sure. Apply Float and Move +1 T2. Also Jump +1 T2 to each recipient at least two height below the caster. No immediate movement. | Thematic redesign: Original wind assistance; positioning and traversal utility. [Inspiration][geo] |
| GEO-A5 Earthen Ward | 250 | 10 MP; r3 center/cross, allies including self; Sure. Protect; rock affinity also grants displacement immunity T2. | Thematic redesign: Original earth protection that steadies an allied formation. [Inspiration][geo] |
| GEO-A6 Wisp Flame | 300 | 10 MP; r3 one enemy; A. M28 Fire, then magical damage received x1.15 T2 after positive damage; wood/heat instead x1.25. No second status roll; custom immunity applies. No same-name stacking; weaker applications cannot refresh a stronger exposure. | Thematic redesign: Original spirit flame that creates an opening for allied magic. [Inspiration][geo] |
| GEO-A7 Rime Field | 300 | 12 MP; r3 center/cross, any except caster; A. M28 Ice plus the existing cross-shaped field even on a miss. Ice affinity attempts Slow with S after damage. One field/caster, existing two-subsequent-caster-turn timer and nonstacking movement surcharge. | Thematic redesign: Original persistent ice terrain for area denial; native ice adds further control. [Inspiration][geo] |
| GEO-A8 Gaia Surge | 400 | 18 MP; r4 center/cross, any except caster; A. M40; Wind always available, other eligible local elements chosen before commitment. No additional affinity multiplier. | Thematic redesign: Original major nature release whose elemental options respond to surroundings. [Inspiration][geo] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| GEO-S1 Attunement | 300 | Weakness-hitting elemental direct HP damage ×1.25. After an MP-funded voluntary action deals positive weakness damage to at least one enemy, refund floor(25% of that action's MP actually paid), once for the action, not per target/hit; cap at missing MP. For independently costed subcasts, each can refund only its own paid MP. Costs must first be affordable in full. | Cross-job support design: Understand elemental vulnerability and apply that knowledge to any technique. [Inspiration][geo] |
| GEO-S2 Surefoot | 200 | Jump +1; ignore extra movement surcharges on legally traversable tiles, including Rime Field. Retain height, occupancy, impassability and environmental harm. | Cross-job support design: Read and traverse difficult ground, regardless of current profession. [Inspiration][geo] |
| GEO-R1 Stone Skin | 300 | Incoming physical direct HP damage ×0.75; after survival grant ordinary Protect. No terrain restriction, no cross-action lock. | Thematic redesign: Original earthen defense with a dependable opportunity to contribute across maps. [Inspiration][geo] |
| GEO-R2 Nature's Wrath | 350 | After surviving enemy direct HP damage, counter original attacker within r4 forM24 Wind with A accuracy. No learned-action lookup, no terrain requirement, no ailment/field/displacement, no outgoing S damage bonus. No cross-action lock. | Thematic redesign: Reactive nature power; neither terrain permission nor a tiny status chance is required for its contribution. [Inspiration][geo] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| GEO-C1 Gaia Combo | 100 | rod or mace. Vanilla chain participation profile: Wise Combo: 10% / 2 / 60%. Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 8. Chemist — Nu Mou and Moogle

**Items — Nu Mou and Moogle.** This command is distinct from vanilla ordinary Item. All eight lessons need no weapon, cost 0 MP, work while Silenced, and consume the exact named ingredients. No Reflect, Return Magic, or Doublecast. Single-target medicine is r4 with ordinary projectile LOS/height unless specified; Healing Mist is an r3 center/cross area, not Long Throw eligible. New medicine targets non-undead allies; revivals require eligible KO allies.

Field Remedy selects exactly one stocked cure with only that item's cure list. High Tonic selects one stocked Hi-Potion or X-Potion. Healing Mist and Resuscitating Draught are original two-ingredient preparations, not claims about vanilla potion contents. Validate the entire recipe before spending any ingredient. Pharmacology improves explicit item HP/MP restoration once, never revival fractions. Resuscitating Draught restores half maximum HP without a 200-HP cap or any healing-support increase.

Items remain actual inventory resources: no shop-buyable Ether assumption or new consumable stock. Moogle Juggler/Chemist retains Smile; Bard/Chemist lacks Stunt. Alchemist already has fixed ordinary Item: Alchemist/Sagacity with Long Throw is a serious alternative, so Chemist's mixtures must earn the secondary slot.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| CHM-A1 Potion | 50 | one Potion; r4 single ally/self; Sure; vanilla Potion healing. | Adaptation: Basic restorative. [Inspiration][chm] |
| CHM-A2 Field Remedy | 100 | choose exactly one stocked Antidote, Eye Drops, Echo Screen, or Soft; r4 single ally/self; Sure; apply only that chosen item's vanilla cure. A valid cure must be present before use. | Thematic redesign: Field medicine combines separately stocked, explicitly selected cures into one learned lesson. [Inspiration][chm] |
| CHM-A3 Phoenix Down | 150 | one Phoenix Down; r4 one KO ally; Sure; unchanged vanilla revival amount/fraction, minimum 1 HP. | Adaptation: Item-based revival. [Inspiration][chm] |
| CHM-A4 High Tonic | 150 | choose one stocked Hi-Potion or X-Potion; r4 single ally/self; Sure; apply exactly the chosen item's vanilla healing. | Thematic redesign: High-grade medicine lesson groups existing consumables without changing their contents. [Inspiration][chm] |
| CHM-A5 Healing Mist | 250 | one Potion AND one Hi-Potion; r3 center/cross, non-undead allies including self; Sure. Each recipient heals max(50, min(100, floor(0.20 x recipient max HP))). | Original extension: Original two-ingredient healing mist grounded in Final Fantasy Chemist preparation and mixing. [Inspiration][chm] |
| CHM-A6 Ether | 200 | one Ether; r4 single ally/self; Sure; vanilla MP recovery. | Adaptation: MP restorative. [Inspiration][chm] |
| CHM-A7 Cureall | 250 | one Cureall; r4 single ally/self; Sure. Vanilla cure list plus the expansion's broad-remedy custom ailments; do not separate Last Resort's drawback from its benefit. | Adaptation: FFT Remedy role using the actual FFTA consumable Cureall. [Inspiration][chm] |
| CHM-A8 Resuscitating Draught | 400 | One X-Potion AND one Phoenix Down; r4 one KO non-undead ally; Sure. Revive at floor(0.50 × target max HP), minimum 1 HP, with no 200-HP cap. No additional buffs, turn change, Pharmacology, or incoming-healing bonus. | Original extension: Original costly revival preparation grounded in Final Fantasy Chemist medicine. [Inspiration][chm] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| CHM-S1 Pharmacology | 200 | Consumed restorative items restore ×1.50 HP/MP; round down once and cap at missing resource. Ordinary Item, Chemist, and eligible item reactions. No improved revival fraction, full-restoration amount, cure list, drain or spells. Only item's user's support applies. | Cross-job support design: Expert medicine preparation transfers to any use of supplies. [Inspiration][chm5] |
| CHM-S2 Long Throw | 350 | For eligible consumable single-target actions able to target others: base range <4 becomes 4; otherwise +1 up to 5 without reducing an already larger base range. Existing target/height/line-of-sight restrictions remain. Self-only/area actions and weapon attacks excluded. | Cross-job support design: Throw supplies accurately across the battlefield from any job. [Inspiration][chm] |
| CHM-R1 Auto-Potion | 300 | After surviving enemy direct HP damage at ≤50% max HP, consume one player-selected Potion or Hi-Potion and apply its normal item recovery. Selection is explicit before battle, default Potion; no automatic substitution, no X-Potion. Pharmacology applies. Maximum one use until start of next own turn, lock only after an item is actually consumed. | Adaptation: Automatic inventory-funded treatment; selection and threshold adapted. [Inspiration][chm] |
| CHM-R2 Auto-Cureall | 350 | After an enemy action passes accuracy and is about to apply one or more Cureall-curable ailments, consume one Cureall and prevent those curable ailments for that whole action. Use the same cure eligibility as ordinary Cureall, including custom harmful tags added by the shared broad-remedy integration. Never prevent KO or an uncurable status. Damage remains. Existing reaction-blocking status prevents use, but the newly intercepted ailment cannot block it before it is applied. One Cureall per action; no cross-action lock; zero stock means no interception. | Original extension: Original extension of emergency item use; no free magical regeneration. [Inspiration][chm] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| CHM-C1 Flask Combo | 100 | knife or mace. Vanilla chain participation profile: Thief Combo: 5% / 2 / 100%. Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 9. Bard — Moogle

**Song — Moogle.** Voice is sufficient: no active song requires an instrument or grants instrument equipment permission. Silence blocks songs; Hide requires neither voice nor weapon and works while Silenced. No Reflect, Return Magic, or Doublecast. Instruments remain Bard equipment and Chorus Combo's requirement.

Marching Strength/Inspired Magic use T2 final physical/magical damage multipliers, not attack-stat boosts. Exclude fixed/percentage damage, items, reactions, combos, and a second drain-recovery bonus. No healing bonus from Inspired Magic. Nameless Song applies Protect, Shell, and Regen deterministically; no random pool or Haste. Magick Ballad may restore MP over ordinary turns, but never grants an extra action or restores the caster directly.

A new persistent song buff may trigger Encouragement once per other ally. Magick Boost can improve the song's own HP restoration, not the separate Encouragement heal or Ballad's MP recovery. Juggler/Song can choose a song or Smile, not both in one action. Time Mage/Song is legal; Moogle White Magic and Bloodcasting are not.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| BRD-A1 Soul Etude | 100 | 8 MP; r4 one ally/self; Sure. Heal 40% target max HP, cap 160, and remove Poison, Blind, Silence, Confuse. | Adaptation: Healing plus cleansing. [Inspiration][brd] |
| BRD-A2 Battle Chant | 150 | 12 MP; r3 center/cross, allies including self; Sure. Protect plus Marching Strength T2: direct physical damage dealt x1.20. No fixed/percentage damage, items, reactions, combos, or drain-recovery bonus. | Adaptation: Defense song. [Inspiration][brd] |
| BRD-A3 Magickal Refrain | 200 | 12 MP; r3 center/cross, allies including self; Sure. Shell plus Inspired Magic T2: direct magical damage dealt x1.20. Same exclusions as Battle Chant; no restorative-healing bonus. | Adaptation: Magical defense song. [Inspiration][brd] |
| BRD-A4 Requiem | 200 | 8 MP; r3 center/cross, undead enemies only; A per target. M60 Holy. No resurrection suppression or instant KO. | Adaptation: Anti-undead song. [Inspiration][brd] |
| BRD-A5 Angelsong | 250 | 12 MP; r3 center/cross, allies including self; Sure. Apply Regen and immediately heal 20% target max HP, cap 80. | Adaptation: Regeneration song. [Inspiration][brd] |
| BRD-A6 Hide | 150 | 0 MP; self; Sure. Apply vanilla Invisible with ordinary break/removal rules. Requires neither voice nor weapon. | Adaptation: Self-concealment. [Inspiration][brd] |
| BRD-A7 Magick Ballad | 300 | 0 MP; r4 one ally other than caster; Sure. Restore 20 MP, capped by missing MP. Not a spell-healing effect or item; no Pharmacology. | Adaptation: MP-restoring song. [Inspiration][brd] |
| BRD-A8 Nameless Song | 400 | 24 MP; r3 center/cross, allies including self; Sure. Apply Protect, Shell, and Regen together. No Haste, random selection, or rerolls. | Thematic redesign: A dependable ensemble of protective statuses replaces the source-inspired random outcome. [Inspiration][brd] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| BRD-S1 Encouragement | 250 | Applying at least one previously absent **persistent tagged beneficial status** through a voluntary action to another ally restores 15% of target max HP, capped at 60 before incoming-healing modifiers. Once per recipient/action. Immediate turn/CT effects such as Smile/Quicken are excluded. This bonus receives no outgoing-healing modifiers such as Composure/Magick Boost, only the recipient's incoming modifiers. Refresh, extension, self-target, mere healing/cure, reaction application and field occupancy do not qualify. Only persistent tagged beneficial statuses qualify; immediate turn/CT effects such as Smile and Quicken do not. No outgoing-healing multiplier applies to this separate heal; only the recipient’s incoming-healing modifier may apply. | Cross-job support design: Inspiring aid makes protective and enhancing actions more useful. [Inspiration][brd] |
| BRD-S2 Clear Voice | 300 | Silence immunity. MP costs of explicitly tagged incanted magic and songs ×0.75, rounded up with minimum1 for a nonzero original cost. Does not discount martial techniques merely because they use MP. No other immunity. | Cross-job support design: Vocal discipline protects both songs and spellcasting. [Inspiration][brd] |
| BRD-R1 Magick Boost | 300 | After surviving enemy direct HP damage, gain one charge through the end of next own turn: next voluntary incanted magic/song action has magical direct HP damage and direct restorative HP healing ×1.30. Explicitly includes percentage-based song HP restoration, not MP restoration, revival or items. A qualifying action consumes charge even if it misses/heals zero. No accumulated charges. | Adaptation: FFT Bard's reactive magical growth made temporary. [Inspiration][brd] |
| BRD-R2 Encore | 350 | After surviving enemy physical HP damage while able to react and not Silenced, grant self Haste for T2. No instrument requirement. Refreshes duration, never stacks speed; no cross-action lock. | Original extension: A reactive return to the musical tempo grants temporary Haste instead of a tiny healing reprise. [Inspiration][brd] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| BRD-C1 Chorus Combo | 100 | instrument. Vanilla chain participation profile: Juggle Combo: 10% / 3 / 70%. Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 10. Dancer — Viera

**Dance — Viera.** Performance works while Silenced; no Reflect, Return Magic, or Doublecast. Only Sword Dance needs a primary knife/rapier. Dances do not directly grant or reset turns.

**Pdance:** use virtual weapon V = min(35, 12 + floor(0.60 × level)), replacing the primary weapon's Attack contribution and weapon-power term in the physical P formula. Keep the character's accumulated physical Attack, nonweapon gear bonuses, applicable supports, and target defense. Ignore held weapon Attack/element/procs and second weapons. V is 18/27/35 at levels 10/25/40. This is a defined custom formula, not a verified ROM field. Sword Dance instead uses the actual primary weapon's P.

Polka/Heathen Frolic use physical damage followed by their custom weakening rider; custom immunity blocks the rider, not unrelated damage. Forbidden Dance selects one ailment for the entire cast, not separately per enemy and not at random. Assassin/Dance works for weapon-free dances but not Sword Dance with a bow/katana. Red Mage/Dance cannot Doublecast dances; Dancer/White Magic can trade offense for restoration.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| DNC-A1 Mincing Minuet | 100 | 6 MP; r3 center/cross, enemies only; A. 0.85 Pdance, non-elemental. | Adaptation: Area HP-damaging dance. [Inspiration][dnc] |
| DNC-A2 Witch Hunt | 150 | 8 MP; r3 center/cross, enemies only; A. Remove min(24, max(8, floor(0.20 x target max MP))) MP, capped at target current MP; no recovery. | Adaptation: MP-damaging dance. [Inspiration][dnc] |
| DNC-A3 Slow Dance | 200 | 12 MP; r3 center/cross, enemies only; S per target. Apply vanilla Slow. | Adaptation: Disrupt enemy tempo. [Inspiration][dnc] |
| DNC-A4 Polka | 200 | 12 MP; r3 one enemy; A. 0.80 Pdance; after positive damage inflict T2 physical damage dealt x0.65. No second S roll; custom immunity blocks only the rider. No effect on HP costs, fixed damage, items, healing, or reactions. | Adaptation: Weaken physical offense. [Inspiration][dnc] |
| DNC-A5 Heathen Frolic | 250 | 12 MP; r3 one enemy; A. 0.80 Pdance; after positive damage inflict T2 magical damage dealt x0.65. Same exclusions/rider-immunity handling as Polka. | Adaptation: Weaken magical offense. [Inspiration][dnc] |
| DNC-A6 Forbidden Dance | 300 | 14 MP; r3 center/cross, enemies only; S per target. Select Blind, Silence, Poison, or Confuse once for the cast; attempt that chosen ailment on every target. No immunity reroll. | Thematic redesign: A deliberate choice of debilitating dance replaces a random ailment selection. [Inspiration][dnc] |
| DNC-A7 Jitterbug | 300 | 10 MP; r2 one enemy; A. 1.00 Pdance; drain 50% of actual positive HP removed, capped at 25% user max HP. Existing no-allies/no-overkill/undead reversal rules apply. | Adaptation: HP-draining dance. [Inspiration][dnc] |
| DNC-A8 Sword Dance | 400 | 16 MP; r1 one enemy; A. Requires primary knife/rapier; 1.60 P from that actual primary weapon, weapon-elemental, one hit, no critical/proc/second strike. | Adaptation: FFV physical dance finisher. [Inspiration][dnc] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| DNC-S1 Grace | 300 | Facing never reduces the user's Evade for ordinary A-type evasion calculations: use the frontal Evade value even for side/rear attacks. No flat Evade addition. Attacker accuracy supports, caps, automatic-hit statuses and reaction prevention still apply. Does not change SRes or an ability's separate positional damage rider. | Cross-job support design: Evasive footwork transferable to any combat style. [Inspiration][dnc] |
| DNC-S2 Light Foot | 350 | Move +1, with no extra movement action, flight, or terrain immunity. | Cross-job support design: A performer's mobility becomes a general positioning tool. [Inspiration][dnc] |
| DNC-R1 Fury | 300 | After surviving enemy direct HP damage, gain one charge through the end of next own turn: next voluntary physical-damage action deals×1.35 direct HP damage. Consume on execution even on miss; no stacking charges, no reaction/DoT/MP damage bonus. Eligibility uses actual physical damage category even if Spellblade's separate Spellweave sequencing tag is magic; consume once for the whole action. Physical damage classification, not Spellweave sequencing category, determines eligibility; an enchanted strike consumes at most one charge. | Adaptation: FFT Dancer's reactive offense made temporary. [Inspiration][dnc] |
| DNC-R2 Counter Rhythm | 350 | After surviving enemy physical HP damage, if attacker within r3, attempt Slow using S plus20percentage points, maximum95%, after normal accuracy/support/facing modifiers; immunity remains absolute. One check; no separate proc chance. No cross-action lock. | Original extension: Original reactive echo of Slow Dance. [Inspiration][dnc] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| DNC-C1 Waltz Combo | 100 | knife or rapier. Vanilla chain participation profile: Lunge Combo: 10% / 1 / 100%. Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 11. Mystic Knight — Viera

**Spellblade — Viera.** All 14 actions require a primary rapier/saber and are blocked by Silence. Only the eleven enchantments (MYK-A1–A11) offer self preparation (Sure) or one r1 enemy for an immediate enchanted A-type strike. Pay once; apply/replace the enchantment even if the strike misses; this is one action, not a free second action or movement. Their strike is physical and not Fight: no crit, weapon proc, second weapon, Doublecast, or automatic bypass of applicable defensive reactions. Spellbreak, Arcane Release, and Break Blade follow their own targeting and resolution below; they never automatically enchant the weapon.

One enchantment persists until replaced, Dispel, KO, Petrify, primary weapon change/loss, job change, battle end, Spell Parry consumption, or Arcane Release consumption. Silence after preparation prevents command actions but does not erase it or stop Fight. Future benefits apply only to primary Fight, replacing its ordinary element/proc; no secondary technique, counter, combo, or second weapon inherits a rider. Arcane Release explicitly consumes a permitted enchantment for its own magical formula, not an inherited Fight rider. Healer cannot become damaging/draining.

Each action establishes at most one Spellweave category. Both modes of every enchantment establish Magic; the strike still deals physical HP damage. Enchanted Fight and Spellbreak establish Physical. Arcane Release and Break Blade establish Magic. The burst deals magical HP damage; Break Blade has no HP damage and cannot receive a Petrify-chance bonus. Follow an enchantment with Fight/Lunge/Spellbreak to alternate, not Red Magic or Arcane Release. Battle Chant/Fury can improve an enchantment strike; Wisp/Inspired Magic cannot. Those magical bonuses can instead improve Arcane Release. Spell Parry spends the enchantment for 50% physical reduction against one enemy action. Red Mage/Spellblade, Fencer/Spellblade, and Dancer/Spellblade work with rapiers; Assassin/Summoner lack qualifying normal weapons.

The six additions' concepts and sequence categories are approved. Their costs, AP, exact powers, and teaching placements below are provisional first implementation targets. The original eight entries, supports, reactions, growths, and unlocks retain their adopted tuning. See [the expansion record](SPELLBLADE-EXPANSION.md) for sequence examples and resource tests.

### Actions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| MYK-A1 Fire Spellblade | 100 | 6 MP; self/Sure OR r1 enemy/A. Strike 1.00P Fire; persistent primary Fight becomes Fire. No extra damage bonus. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A2 Blizzard Spellblade | 100 | 6 MP; self/Sure OR r1 enemy/A. Strike 1.00P Ice; persistent primary Fight becomes Ice. Equal AP avoids artificially delaying basic elemental coverage. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A3 Thunder Spellblade | 100 | 6 MP; self/Sure OR r1 enemy/A. Strike 1.00P Lightning; persistent primary Fight becomes Lightning. Keeping distinct elemental lessons is acceptable where three-tier damage inflation is not. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A4 Poison Spellblade | 150 | 6 MP; self/Sure OR r1 enemy/A. Strike and future primary Fight are non-elemental; after positive damage attempt Poison using normal S, not S x0.5. Immediate strike 1.00P. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A5 Sleep Spellblade | 250 | 10 MP; self/Sure OR r1 enemy/A. Immediate 0.80P non-elemental; future Fight stays ordinary power/non-elemental. After positive damage from either carrier attempt Sleep at S x0.5; apply after damage. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A6 Silence Spellblade | 200 | 8 MP; self/Sure OR r1 enemy/A. Immediate 1.00P non-elemental; future Fight non-elemental. Each carrier attempts Silence at normal S after positive damage. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A7 Drain Spellblade | 300 | 12 MP; self/Sure OR r1 enemy/A. Immediate 1.00P non-elemental; future Fight non-elemental. Each carrier heals 35% of actual HP removed, cap 15% user max HP per action. Existing undead reversal and no-overkill rules. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A8 Flare Spellblade | 400 | 20 MP; self/Sure OR r1 enemy/A. Immediate 1.00P non-elemental and future primary Fight each use 75% effective target WDef. No independent damage multiplier, no second attack. | Thematic redesign: FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat. [Inspiration][spell] |
| MYK-A9 Slow Spellblade | 250 | 12 MP; self/Sure OR r1 enemy/A. Immediate 0.80P non-elemental; future primary Fight remains ordinary power/non-elemental. After positive HP damage from either carrier attempt vanilla Slow at normal S. Magic sequencing; physical HP damage. | Thematic redesign: FFTA2 Slow Blade adapted to a maintained enchantment; sustained single-target control. [Inspiration][spellA2] |
| MYK-A10 Osmose Spellblade | 300 | 8 MP; self/Sure OR r1 enemy/A. Immediate 0.80P non-elemental; future primary Fight remains ordinary power/non-elemental. After positive HP damage siphon floor(25% of actual HP removed) MP, capped at 10 MP per action and target current MP; restore only MP actually removed, capped by user missing MP. No ally, overkill, absorbed-hit, or second-weapon siphon. Apply shared undead reversal. Spellweave never directly multiplies MP loss/recovery; increased actual HP damage may indirectly raise siphon only up to the same cap. Magic sequencing; physical HP damage. | Thematic redesign: FFV Osmose enchantment; limited enemy-funded endurance with a lower immediate strike. [Inspiration][spellV] |
| MYK-A11 Holy Spellblade | 250 | 12 MP; self/Sure OR r1 enemy/A. Immediate 1.00P Holy; persistent primary Fight becomes Holy. Normal elemental resistance, immunity, and absorption; no automatic undead kill or independent damage bonus. Magic sequencing; physical HP damage. | Thematic redesign: FFV Holy enchantment adapted as a distinct elemental matchup. [Inspiration][spellV] |
| MYK-A12 Spellbreak | 250 | 10 MP; r1 one enemy/A. 0.85P using ordinary primary weapon element. Resolve A and applicable defensive interceptions first; on a successful hit remove one selected dispellable beneficial status if still present, then calculate HP damage using remaining defenses and resolved interception modifiers. Removal does not require positive HP damage. If an interception already consumed the selected status, do not select another or refund the action. Select from eligible statuses before commitment; no eligible status means the action cannot be selected. Never removes equipment, passive lessons, fields, or undispellable boss effects. Preserve the user enchantment without applying its element, proc, drain, or Flare penetration. Physical sequencing and physical HP damage. | Original extension: Original sword-delivered dispel: trade damage for removal of a selected magical protection. [Inspiration][myk] |
| MYK-A13 Arcane Release | 350 | 14 MP plus consume an active Fire, Blizzard, Thunder, Holy, or Flare enchantment at commitment; r3 center/cross, Any, line of sight. M40 magical HP damage for elemental enchantments using their element; Flare instead gives M44 non-elemental magical damage with normal MRes and no WDef penetration. A per target under the shared accuracy rules; preview each target. Immunity and defensive effects remain applicable. A committed miss still establishes Magic; invalid actions spend neither MP nor enchantment and establish no category. No Sleep, Poison, Silence, Slow, Drain, or Osmose release. No weapon proc, status rider, recovery, Reflect, Return Magic, or Doublecast. Enchantment is spent even if every target avoids or nullifies the burst; no Spell Parry fuel remains. Magic sequencing and magical HP damage. | Original extension: Original discharge of maintained blade magic for range and area at the expense of sustain and parry fuel. [Inspiration][myk] |
| MYK-A14 Break Blade | 400 | 24 MP; r1 one enemy/S. Attempt Petrify at normal S, respecting immunity and applicable defenses; no preliminary A roll and no HP damage. A sword-delivered magical technique, not an enchantment: does not create, consume, replace, or carry the existing enchantment. Magic sequencing; Spellweave cannot improve Petrify chance. Ordinary legal accuracy supports retain their native eligibility and occupy the same single support slot; this is not a ban on accuracy support. No Reflect, Return Magic, or Doublecast. | Thematic redesign: FFV Break Spellblade inspiration adapted to a separately paid Petrify technique, not persistent Petrify on Fight. [Inspiration][spellV] |

### Supports and reactions

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| MYK-S1 Spellweave | 300 | Alternate one tagged magical voluntary action and one physical-damage voluntary action; opposite category direct HP damage ×1.35. First qualifying action has no bonus. A nonqualifying action/Wait **retains** the previous category but never grants a bonus; repeated category updates it without bonus. Magic healing establishes magic but receives no healing bonus. One category and evaluation per action; same-category Doublecast establishes magic once, mixed/ambiguous multi-cast clears the sequence. Spellblade enchant-and-strike is tagged **magic** for sequencing only: its damage stays physical, and it cannot establish both categories. Enchantment followed by Red Magic is Magic-to-Magic and gains no alternation bonus; Fight or a qualifying Lunge action can alternate with the enchantment. Enchanted Fight and Spellbreak establish Physical; Arcane Release and Break Blade establish Magic. Arcane Release deals magical HP damage; Break Blade has no HP damage. No bonus to status accuracy or directly to MP damage/recovery; increased actual HP damage can indirectly raise capped drain/siphon recovery once. An enchanted hit never establishes both categories or triggers its own bonus. | Cross-job support design: Combine martial and magical actions across different command sets. [Inspiration][myk] |
| MYK-S2 Arcane Ward | 350 | Incoming magical direct HP damage ×0.75 while current MP ≥50% max MP and ≥1, checked at incoming-action start. No MP expenditure or absorption. | Cross-job support design: Maintained magical reserves protect their bearer. [Inspiration][myk] |
| MYK-R1 Magic Shell | 300 | Before a successful enemy magical HP-damage action, forecast damage without this reaction. If current HP minus forecast damage would be ≤50% max HP, apply ordinary Shell before that action's damage is calculated. Already-Shelled units gain no additional defense. Forecast once; no recursive reevaluation. No cross-action lock. | Adaptation: FFV low-health Shell placed in FFTA's reaction slot. [Inspiration][myk] |
| MYK-R2 Spell Parry | 350 | While wielding a qualifying rapier/saber with active Spellblade, after an enemy physical hit check succeeds, consume the enchantment to reduce physical HP damage ×0.50 from that one enemy action. The spent enchantment is unavailable for other effects immediately. Status riders and magical components are unaffected. Misses do not consume it. | Original extension: Spend a maintained weapon enchantment to soften one incoming physical action. [Inspiration][myk] |

### Combo

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| MYK-C1 Spellblade Combo | 100 | rapier/saber. Vanilla chain participation profile: Red Combo: power 10%, participation range 2, hit 70% Preserve vanilla initiation/JP behavior; no new riders. | FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |

## 12. Teaching equipment and availability

The original W1–W8 tables supply 64 job weapons; six additional Mystic Knight teaching sabers and eight Soldier/Gladiator axes bring the total to **78 teaching items**. W1–W8 teach A1–A8. W2 also teaches S1; W3 combo; W4 R1; W5 S2; W6 R2. Each table entry gives its current AP; simultaneous lessons progress normally. The per-job totals below replace the old uniform 3,150-AP total.

| Job / category | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 |
|---|---|---|---|---|---|---|---|---|
| Samurai / Katana | Ashura Echo | Wind Reed | Osafune Echo | Murasame Echo | Kiyomori Echo | Guarding Blade | Kiku Echo | Moonblossom |
| Dark Knight / Sword | Gloom Sword | Sanguine Edge | Infernal Edge | Veil Sword | Oathbreaker | Crushing Edge | Abyssal Edge | Sacrifice Edge |
| Viking / Axe | Storm Axe | Raider Axe | Plunder Axe | Warcaller Axe | Stormcall Axe | Pillage Axe | Thunderhead Axe | Tidal Axe |
| Geomancer / Rod | Stone Rod | Root Rod | River Rod | Zephyr Rod | Wardstone Rod | Wisp Rod | Rime Rod | Gaia Rod |
| Chemist / Knife | Tonic Knife | Field Remedy Knife | Phoenix Knife | High Tonic Knife | Mist Knife | Ether Knife | Cureall Knife | Resuscitation Knife |
| Bard / Instrument | Etude Pipe | Battle Pipe | Refrain Pipe | Requiem Pipe | Angel Pipe | Traveler Pipe | Ballad Pipe | Nameless Pipe |
| Dancer / Rapier | Minuet Foil | Witch Foil | Tempo Foil | Polka Foil | Frolic Foil | Forbidden Foil | Jitterbug Foil | Danceblade |
| Mystic Knight / Saber | Ember Saber | Rime Saber | Spark Saber | Venom Saber | Dream Saber | Hush Saber | Siphon Saber | Flare Saber |

These are new proposed item names. An Echo katana teaches the named sword spirit without changing the vanilla weapon bearing a similar name. A teaching weapon's name never grants an unlisted proc or power. Chemist uses the actual FFTA consumable **Cureall**, not an assumed inventory item named Remedy. [FFTA item reference][items].

Weapon Attack targets, W1–W8: Samurai/Dark Knight/Viking/Mystic Knight 18/22/26/30/34/38/42/46; Dancer/Chemist 14/17/20/23/26/29/32/35; Bard 12/15/18/21/24/27/30/33; Geomancer 10/12/14/16/18/20/22/24 with Magic Power bonuses 0/2/4/6/8/10/12/14. Other bonuses are zero; no innate element, proc, or automatic status. Categories use original handedness except new axes, which are two-handed and exclude shields/second weapons.

Prices: 300/600/1,000/1,600/2,400/3,400/4,800/6,500 gil. W1–2 are initial shop-tier stock; W3–4 first expansion; W5–6 second; W7–8 last pre-final-story expansion. These anchors require real story-flag mapping. Gear may be purchased before a job unlocks, but only an eligible active job learns its lessons. All gear must remain repeatably obtainable. A repeatable teaching weapon does not guarantee repeatable ingredients. Ethers are not assumed purchasable, Cureall access is progression-dependent, and no new consumable shop stock is introduced. High Tonic permits using an owned X-Potion without promising early availability or affordability. Verify actual vanilla supply and shop flags.

Viking can equip all new axes, but only learns its Reaving lessons on Viking teaching axes. Soldier and Gladiator likewise learn only their own documented lessons. See [the axe addendum](AXE-SKILL-EXPANSION.md) for their eight weapons and twelve entries. Viking axe access is now part of this revised design; Warrior does not automatically gain axe access.


| Lesson group | Action AP | Support AP | Reaction AP | Combo AP | Total AP |
|---|---:|---:|---:|---:|---:|
| Samurai | 1850 | 600 | 650 | 100 | 3200 |
| Dark Knight (each race) | 1900 | 700 | 650 | 100 | 3350 |
| Viking | 1850 | 500 | 350 | 100 | 2800 |
| Geomancer | 1900 | 500 | 650 | 100 | 3150 |
| Chemist (each race) | 1550 | 550 | 650 | 100 | 2850 |
| Bard | 1750 | 550 | 650 | 100 | 3050 |
| Dancer | 1900 | 650 | 650 | 100 | 3300 |
| Mystic Knight | 3400 | 650 | 650 | 100 | 4800 |
| Soldier axe additions | 750 | 150 | 150 | 0 | 1050 |
| Gladiator axe additions | 1150 | 350 | 350 | 0 | 1850 |

The totals count lessons, not sequential grinding. New Soldier/Gladiator actions count toward their existing mastered-action gates. Measure earlier unlock timing without changing the accepted prerequisites. New weapons may improve original jobs that can equip them; compare attack, other stats, effects, price, and acquisition against actual vanilla alternatives before tuning those values.

### Additional Mystic Knight teaching sabers

These are parallel lessons within existing shop tiers, not six stronger endgame tiers. Only Mystic Knight learns these lessons; learned actions transfer normally with a legal weapon. No extra support/reaction lessons or changes to W1–W8. All six use ordinary saber handedness, with zero other bonuses and no innate element/proc/status. Story-flag mapping and item-record capacity remain unverified.

| New saber | Lesson | AP | Weapon Attack | Gil | Shop tier |
|---|---|---:|---:|---:|---|
| Hourglass Saber | MYK-A9 Slow Spellblade | 250 | 30 | 1600 | First expansion |
| Aether Saber | MYK-A10 Osmose Spellblade | 300 | 34 | 2400 | Second expansion |
| Dawn Saber | MYK-A11 Holy Spellblade | 250 | 38 | 3400 | Second expansion |
| Severance Saber | MYK-A12 Spellbreak | 250 | 26 | 1000 | First expansion |
| Prism Saber | MYK-A13 Arcane Release | 350 | 34 | 2400 | Second expansion |
| Stone Saber | MYK-A14 Break Blade | 400 | 46 | 6500 | Last pre-final-story expansion |

The additional 1,800 action AP represents optional breadth; it is not required before Mystic Knight becomes useful. Existing prerequisite counts stay unchanged. Check whether broader mastery opportunities accelerate any downstream access before proposing gate changes.

## 13. Implementation and balance validation

Version 0.6 contains the user's adopted council design and approved Spellblade expansion, not an applied or gameplay-tested ROM patch. Preserve the vanilla-USA base, original jobs/abilities/stories/laws/missions/recruitment and saves, except the approved additive axe permission/lessons and explicit integration of new effects. Squire/Sentinel remain rejected and Green Mage remains a candidate.

Prove storage for ten racial job implementations, mastery, teaching items, lists, saves, and animations before assuming new records can be added. Verify original handlers for formulas, theft, item effects, reaction scheduling, enchantment modes, cost/preview behavior, and laws. No data-only implementation is assumed. Validate pre-battle Auto-Potion selection and the next-category Spellweave display rather than silently replacing those user-facing choices.

The [council report](BALANCE-COUNCIL.md) documents adopted decisions, burst examples, and research. The [global review](../balance-council-global.md) supplies the comparison matrix. Test early/mid/late equipment around levels 10/25/40, organic and optimized inherited growth, actual AP/shop availability, short and long encounters, two-enemy focus fire, and real boss immunities.

Priority cases: Bloodcasting + Damage > MP at tiny/full MP reserves; capped drain and undead; Desperation/Dragonheart with sacrifice and party buffs; attack-and-enchant with Spellweave/Fury/Spell Parry; Song/Encouragement/charged healing and donated turns; Chemist inventory recipes and revival at high HP; Dancer virtual-weapon scaling; Geomancer fields, affinities and movement; new axes with every original Soldier/Gladiator action. Count setup, allied healing, and extra-turn actions rather than comparing only a successful hit.

At 300 target max HP, Healing Mist restores 60, or 135 when the item user has Pharmacology and a Human recipient has Recuperation. Charged Angelsong plus a new Regen/Encouragement on that Human restores 117 + 67 = 184 HP, capped by missing HP. Encore/self/refresh/Smile never generate that extra Encouragement heal. These are arithmetic expectations, not results from playtesting.

Keep original unlock gates and verify any acceleration from additional mastered axe actions. Match all 78 teaching items to actual shop flags, retain repeatable teaching access without inventing consumable supply, and compare new equipment's effect on original jobs. Combo profiles require both correct initiation and chain participation. Full release needs real battle, AI, law, AP, job change, ordinary save/load, and clean-ROM patch tests; old-save migration is not assumed.

The [modding guide](../../FFTA-MODDING-GUIDE.md) covers tooling and research. No ROM has been changed by adopting these documents.

[sam]: https://finalfantasy.fandom.com/wiki/Samurai_(Tactics)
[drk]: https://finalfantasy.fandom.com/wiki/Dark_Knight_(Tactics)
[drk14]: https://na.finalfantasyxiv.com/jobguide/darkknight/
[drk11]: https://finalfantasy.fandom.com/wiki/Dark_Knight_(Final_Fantasy_XI)/Abilities
[vik]: https://finalfantasy.fandom.com/wiki/Viking_(Tactics_A2)
[geo]: https://finalfantasy.fandom.com/wiki/Geomancer_(Tactics)
[chm]: https://finalfantasy.fandom.com/wiki/Chemist_(Tactics)
[chm5]: https://finalfantasy.fandom.com/wiki/Chemist_(Final_Fantasy_V)
[brd]: https://ffcompendium.com/h/jobs/bard.shtml
[dnc]: https://ffcompendium.com/h/jobs/dancer.shtml
[myk]: https://finalfantasy.fandom.com/wiki/Mystic_Knight_(Final_Fantasy_V)
[spell]: https://strategywiki.org/wiki/Final_Fantasy_V/Magic_and_skills
[axe14]: https://na.finalfantasyxiv.com/jobguide/warrior/
[ffta]: https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26226
[items]: https://finalfantasy.fandom.com/wiki/Final_Fantasy_Tactics_Advance_items
[mechanics]: https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262
[manual]: https://www.nintendo.com/eu/media/downloads/games_8/emanuals/game_boy_advance_8/Manual_GameBoyAdvance_FinalFantasyTacticsAdvance_EN_DE_FR_ES_IT.pdf

[spellV]: https://finalfantasy.fandom.com/wiki/Spellblade_(Final_Fantasy_V)
[spellA2]: https://finalfantasy.fandom.com/wiki/Spellblade_(Tactics_A2)
