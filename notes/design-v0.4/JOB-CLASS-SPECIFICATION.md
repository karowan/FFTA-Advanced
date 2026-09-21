# FFTA: eight-job expansion specification

Design version 0.4 — supports for cross-job builds, September 14, 2026

**Our expansion of vanilla USA FFTA.** Preserve each job's spirit and build around FFTA's freedom to mix abilities. [Design principles](JOB-DESIGN-PRINCIPLES.md) guide the kits; [the support redesign](SUPPORT-SKILL-DESIGN.md) explains all 18 transferable supports and example builds. All values remain proposals for playtesting.

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

**Current starter decision:** Chemist has no job prerequisite for either race. It becomes selectable at the first normal opportunity to change jobs, while its skills still use equipment/AP learning. Samurai, Viking, and Dancer remain prerequisite jobs. Additional starter candidates are being considered in [STARTER-JOB-INSPIRATION.md](../../STARTER-JOB-INSPIRATION.md), not automatically added to this roster. Vanilla Moogles do not have White Mage; no such job access is introduced here.

Chemist is a starter; Viking and Dancer are intended to be accessible early after meeting prerequisites. The other jobs are intended for the middle of the campaign. Exact timing depends on equipment and AP access, not just the prerequisite counts. The previous suggestion to make several advanced concepts into starters was not adopted.

## 2. Shared rules and what is an adaptation

**Audit scope:** all 116 ability entries: 64 new-job actions, 32 new-job supports/reactions, 8 combo entries, and 12 Soldier/Gladiator axe additions. Every entry has an inspiration reference and a lineage label; matching a canonical ability is not required. This counts design lessons, not necessarily 116 new engine records: familiar effects and existing abilities should be reused where their behavior is identical. [The audit](JOB-THEME-AUDIT.md) maps every old entry to its replacement.

- **Adaptation** starts from a documented Final Fantasy ability. Its exact effect can change to suit this job and FFTA. **Thematic redesign** develops a new mechanic from the broader identity; a familiar name does not promise a direct port.
- **Original extension** is our invention, justified by that job's established role. Its linked source supports the underlying identity, not the existence of our invented name or exact effect.
- **FFTA integration** means a new job's ordinary combo entry. None of these combo names is claimed as an imported signature ability.

All numerical values, new progression gates, teaching items, racial assignments, and balance limits are ours. Theme and gameplay govern the design. We can change elements, targets, costs, formulas, scaling, and restrictions, or invent a new technique; the table describes our actual effect and the reference only explains inspiration. The reference versions are FFT/War of the Lions, FFV, FFTA2, and specifically identified MMO abilities; these games do not have one universal identical job implementation. Community references document released games, and are not official endorsement of this mod. Fan-made job concepts are not evidence of canon.

### Learning and equipment

The current working lists have 8 A, 2 S, 2 R, and 1 combo lesson per job. This is a provisional size, not a requirement to fill slots or preserve redundant skills. Preserve normal AP/equipment learning, one primary and one secondary action set, one equipped support, one reaction, and one combo. There are no free new passives or extra movement slots. Reactions and supports require equipping even when innate in their source game. Shared jobs have identical skills and separate racial growths. New-job equipment permission is not inherited by mastering the job. Main-job eligibility and existing story-character restrictions remain intact. Job switching does not recalculate accumulated stats. The new actions count for their owning job's mastered-action gates; supports/reactions do not. [Nintendo manual][manual].

### Supports belong to builds

A support is taught by a job, but after mastery it can be equipped on any other legal job of that same character. None of our 18 proposed supports requires the teaching job, its secondary command, its signature weapon, or an exclusive mechanic such as Centered. Broad conditions such as low HP, elemental weakness, item use, movement, or a sequence of magic and physical actions are valid because many jobs can use them. Racial job availability and one equipped support still apply. [The full support sheet](SUPPORT-SKILL-DESIGN.md) gives legal build examples.

The support slot is independent of the primary/secondary action slots. A Paladin can learn Composure from Samurai and equip it while using Chivalry and another Human command; Iaido is unnecessary. This does not grant Samurai to other races. Temporary lesson access still follows existing teaching-equipment rules before mastery.

Support damage bonuses apply to direct physical/magical HP damage where stated, including eligible vanilla and new actions; they are not restricted to new IDs. Fixed/percentage damage, instant KO, HP/MP exchange, HP costs, item effects, drain recovery, damage-over-time, reactions, and combos receive no new outgoing bonus unless a support explicitly names that class of effect. Direct restorative healing includes spells and techniques; Pharmacology owns item potency, and Recuperation owns incoming HP recovery. A normal restorative Fight using Healer counts as direct healing, never damage or drain. Defensive supports apply to their stated damage category regardless of which command produced it.

Beneficial/harmful status checks use explicit effect tags, including vanilla effects and our temporary modifiers. Field tiles, passive equipment stats, learned supports, and reaction readiness are not statuses. Poise can use a beneficial status applied by anyone. Opportunist snapshots the target before damage. Encouragement can trigger once per recipient when adding a status that was absent; its bonus healing cannot trigger another Encouragement. The recipient's Recuperation may enhance it.

Spellweave records the preceding qualifying voluntary action on the user, at action completion, even if it misses. It never boosts the action that first establishes the sequence. Evaluate a sequence once per action, including multi-target actions. For an original multi-cast action, any mixed or ambiguous category breaks the sequence and gains no bonus; do not grant multiple bonuses inside one action. Reactions, forced actions, and movement do not establish a category. Normal Wait breaks the sequence. Job change, KO, Petrify, battle end, or removing the support clears it. The UI must show the next eligible category.

Bloodcasting converts the computed MP cost once per action, adding any native HP payment. At 200 max HP, Blood Edge still costs 20 HP; Abyssal Blade costs 40 HP + 24 HP instead of 12 MP; Unholy Sacrifice costs 60 HP + 32 HP instead of 16 MP. No HP discount remains. Validate each action's affordability before execution. Healing financed by Bloodcasting can have a positive HP return; that is allowed and costs a turn. Test the economy against ordinary healing and MP recovery rather than banning the combination by job.

### Formula and targeting notation

**P** is the damage reference for one primary-weapon physical hit, including applicable defenses. 1.30P is a damage multiplier, not +30% Attack. New A-abilities do not call Fight, cannot crit, do not copy weapon status procs, and never use a second weapon. Damage described as weapon-elemental uses the primary weapon's element. Explicit virtual-weapon dance formulas replace actual weapon Attack and element. **M24** means a proposed magical-damage routine with power 24, caster Magic Power, and target Magic Resistance; it is not a verified ROM field mapping. **A** is an ordinary attack-style accuracy check; **S** is the normal status check with immunity; **Sure** is a legal willing-target effect. An S multiplier scales the final ordinary success chance. Buff-based percentage-point reductions apply afterward, once, floor 0. Damage formula class does not itself determine Silence or reflection; each command specifies those properties. Exact handlers and previews require mapping against [original mechanics research][mechanics].

**rN** is Manhattan tile distance; r1 excludes diagonals. **Cross** means center plus four orthogonal neighbors. **Self cross** centers it on the caster. **Line N** is a chosen cardinal line of N tiles, excluding caster; it stops at impassable terrain. **Any** includes friendly fire. Single-target range has height limit 3; melee limit 2; cross neighbors must be within 2 height of center and line targets within 2 of caster. Projectiles require line of sight; songs, dances, and terrain effects do not. Show all affected tiles and actual chances before commitment. All new actions resolve immediately and use one ordinary action; none grants movement or another turn.

### Duration, recovery, and resources

Use vanilla durations, immunity, removal, and stacking for named existing statuses unless an action explicitly specifies another duration. **T2** is a custom effect expiring after the target finishes its second subsequent turn, excluding the application turn. Reapplication refreshes, never stacks. KO, Petrify, battle end, and job change clear custom effects; Dispel removes beneficial effects and ordinary broad remedies also clear our harmful modifiers. Last Resort is indivisible: remove both its benefit and drawback together. Exposed uses its expressly shorter timer. Spellblade instead persists for the expressly listed duration in its section.

Distinct modifiers multiply once; round down only after combining them. Clear Voice grants Silence immunity, which wins over status success modifiers; War Cry continues to reduce other applicable status chances. Same-name modifiers from multiple units do not stack. Existing statuses and supports retain ordinary behavior.

New restorative actions target non-undead allies, with recovery capped by missing HP/MP. Original commands keep their undead interactions. Revives target eligible KO allies only, never removed or permanently lost units. HP costs are percentages of maximum HP, rounded up, minimum 1, paid once per action and never allowed to reduce user below 1 HP. Costs are paid after validation and before hit checks, even if the action misses. HP costs are not damage and trigger no reactions.

HP drain uses actual positive HP removed, limited by target pre-hit HP and each skill's cap. No healing from allies, overkill, absorption, or immunity. Undead reverse the recovery into user damage, which can KO but cannot trigger reactions. MP drain uses actual MP removed, no overdraw; against undead its attempted user recovery becomes MP loss, capped at user current MP. No ability generates JP. Original MP supports retain their behavior. Bloodcasting is our explicit exception that converts an MP cost into HP; no support changes consumable counts.

Consumables must exist in inventory and be deducted once atomically after validation. Never substitute mission items or silently use rarer medicine. New theft reuses original eligibility, target inventory depletion, immunity, and payout restrictions; already-stolen items cannot be stolen again. Damage and theft are separate checks, not one guaranteed steal.

### Reactions and command interactions

All new reactions have their listed activation chance and one activation opportunity per incoming enemy action, locked until the defender's next turn. No self/ally damage, costs, poison ticks, reaction, or combo triggers; no counter chains. Defensive reactions act before damage; recovery/counters require survival and ordinary ability to react. Stated weapons, range, terrain, and voice requirements also apply. A reaction that cannot find a legal target fails without retargeting.

Original Double Sword/Fight remains intact; new attacks use one primary weapon. Spellblade modifies only the primary Fight strike, replaces that strike's ordinary proc, and cannot convert Healer into damaging/draining attacks. No new A-ability is added to Doublecast eligibility. Original eligible magic still works as before. Combo entries use the vanilla Judge Point system and have no custom combat riders. New effects receive applicable existing laws, including elemental, item, theft, healing, and equipment restrictions; a new command name cannot create an exemption.

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

Growth alignment: Samurai's offense now develops through Weapon Attack, avoiding a second mandatory damage stat; Geomancer has MP growth for its stronger, resource-using toolkit. The other new-job growths remain provisional. These are our design targets. Soldier and Gladiator retain their original growths and armor permissions.

All categories are vanilla except the explicitly added Axe family. Racial armor animations and permission fields need validation. Samurai teaching weapons are new spirit-channeling variants, not edits to existing named katanas.

## 4. Samurai — Human

**Command: Iaido.** A disciplined katana fighter who turns composure into decisive techniques and protective blade spirits. All actions require a primary katana. Its identity draws on the [Samurai tradition][sam], while the kit below is designed around FFTA's action economy.

All damaging Iaido uses **P and physical damage**, including spiritual attacks; sword training and equipment drive its offense. Murasame uses the target's maximum HP. Magic Power is not a second offensive requirement. Silence, Reflect, Return Magic, and Doublecast do not apply. After mastery, any equipped katana can use a learned technique; no sword breakage or matching spare blade is required.

**Centered:** a visible, non-stacking T2 buff granted by a successful Ashura or Counter Draw. It is an action/reaction effect, not a free innate passive. The next damaging Iaido other than Ashura, or Murasame, consumes it at execution and gains ×1.25 HP damage or healing for that whole action. A miss still spends it. It does not enhance MP damage, status chance, Fight, counters, combos, Kiyomori, or secondary sets. Kiyomori can be used while holding it. Lose Centered on expiry, Dispel, KO, Petrify, battle end, job change, or a change/loss of primary weapon.

| ID / action | AP | Cost | Target / hit | Proposed effect | Inspiration |
|---|---:|---|---|---|---|
| SAM-A1 Ashura | 100 | 4 MP | r1, one enemy; A | 1.10P non-elemental; after positive damage gain Centered. This action cannot consume or benefit from Centered. | Thematic redesign: Decisive draw that builds composure; original attack-and-prepare mechanic. [Inspiration][sam] |
| SAM-A2 Wind Draw | 150 | 6 MP | Line 3, enemies; A | 0.95P Wind per target. Can spend Centered for its damage bonus. | Thematic redesign: Original cutting wind released through katana technique. [Inspiration][sam] |
| SAM-A3 Osafune | 200 | 6 MP | r2, one enemy; A | 0.85P non-elemental; after positive damage remove up to 10 MP from the target. No MP recovery. Centered boosts HP damage only. | Thematic redesign: MP-cutting blade spirit redesigned to also contribute HP damage. [Inspiration][sam] |
| SAM-A4 Murasame | 200 | 8 MP | r2 center, cross, allies including self; Sure | Restore 25% target maximum HP, capped at 100 HP per target before Centered. Centered multiplies that capped amount by 1.25; final recovery is capped by missing HP. | Thematic redesign: Healing blade spirit, with reach and scaling chosen for frontline support. [Inspiration][sam] |
| SAM-A5 Kiyomori | 250 | 10 MP | Self cross, allies including self; Sure | Apply Protect and Shell. Does not consume Centered. | Thematic redesign: Protective blade spirits; group defense earns its action through multiple allies. [Inspiration][sam] |
| SAM-A6 Guarding Draw | 300 | 6 MP | r1, one enemy; A | 0.90P non-elemental; after positive damage apply Protect to self. Can spend Centered for its damage bonus. | Thematic redesign: Original guarded sword strike that combines pressure with self-protection. [Inspiration][sam] |
| SAM-A7 Kiku-ichimonji | 300 | 12 MP | r3, one enemy; A | 1.30P non-elemental. Can spend Centered for its damage bonus. | Thematic redesign: Far-reaching blade spirit redesigned as a precise ranged finisher. [Inspiration][sam] |
| SAM-A8 Moon Blossom | 400 | 16 MP | Self cross, enemies; A | 1.35P non-elemental per target; after damaging at least one enemy, apply Regen to self. Centered boosts the whole action once. | Thematic redesign: Original culminating spirit release, with offensive and sustaining roles. [Inspiration][sam] |

| ID / passive | Type | AP | Effect while equipped | Inspiration |
|---|---|---:|---|---|
| SAM-S1 Composure | Support | 200 | During your own turn, direct HP damage dealt and direct restorative HP healing applied ×1.15 if you have not voluntarily moved before that action starts. Moving afterward is allowed. No weapon, command, or Centered requirement. Does not boost item healing, drain recovery, MP effects, or reaction damage. | Cross-job support design: Calm, deliberate action; useful with attacks, techniques, and magic. [Inspiration][sam] |
| SAM-S2 Poise | Support | 350 | Direct physical and magical HP damage received ×0.85 while at least one beneficial status is active at the start of the incoming action. Qualifying effects are Protect, Shell, Haste, Regen, Float, Invisible, or a tagged temporary beneficial effect such as Centered, Last Resort, or a Spellblade enchantment. Additional statuses do not increase the bonus. No katana or source-job requirement; costs and damage-over-time are excluded. | Cross-job support design: Maintaining composure under protection; benefits can come from allies or another command. [Inspiration][sam] |
| SAM-R1 Blade Ward | Reaction | 250 | Requires katana. 40% pre-hit activation: incoming enemy physical HP damage ×0.70 for that action, including physical A-abilities. No counter. | Thematic redesign: Original blade defense with a broader trigger than a Fight-only evasion move. [Inspiration][sam] |
| SAM-R2 Counter Draw | Reaction | 350 | After surviving adjacent enemy physical HP damage, 35% activation: counter once for 0.70P non-elemental, A accuracy. Requires katana. Positive counter damage grants Centered; the counter cannot consume or benefit from Centered. | Thematic redesign: Original reactive draw that prepares the next deliberate technique. [Inspiration][sam] |

**SAM-C1 Crescent Combo — 100 AP:** Requires katana; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider.

**How it plays:** Ashura contributes damage while preparing a stronger follow-up. Spend Centered on a line attack, ranged strike, close-area finisher, or allied healing; Poise also recognizes other beneficial statuses, so it remains useful after changing jobs or spending Centered. Guarding Draw provides a useful defensive turn without giving up all pressure. Range, target count, and resource needs distinguish the eight actions. These are prototype values, not proof that the kit outperforms or matches any vanilla build.

## 5. Dark Knight — Human and Bangaa

**Command: Dark Arts.** A cursed swordsman who exchanges life and safety for force, then drains enemies to recover. FFT: War of the Lions supplies the core sword arts; two explicitly identified MMO abilities reinforce the same identity. Main reference: [FFT: War of the Lions Dark Knight][drk].

Damaging and draining actions require a primary sword, greatsword, or broadsword. Their formulas are physical, including MP drain. Dark Mind and Last Resort need no weapon. Silence, Reflect, Return Magic, and Doublecast do not apply to this adapted command. No summoned undead, necromancy, free revival, or arbitrary binding curse is added.

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| DRK-A1 Blood Edge | 100 | 10% max HP | r1, one enemy; A | 1.30P Dark. | Original extension: Original introductory sword technique built around the job's health sacrifice. [Source][drk] |
| DRK-A2 Sanguine Sword | 150 | 6 MP | r2, one enemy; A | 0.85P non-elemental; heal 25% of actual HP removed, capped at 10% user max HP. Undead reverse drain. | Adaptation: HP-draining sword art. [Source][drk] |
| DRK-A3 Infernal Strike | 200 | 4 MP | r2, one enemy; A | Remove floor(0.20 × the 1.00P non-elemental damage reference) MP, capped at target current MP and 12. Restore exactly the MP removed to user, capped at missing MP. No HP damage. | Adaptation: MP-draining sword art. [Source][drk] |
| DRK-A4 Dark Mind | 200 | 8 MP | Self; Sure | Apply Shell. FFXIV's defensive ability is represented by a familiar FFTA magic ward; this is not its full current mitigation profile. | Adaptation: Personal protection against magic. [Source][drk14] |
| DRK-A5 Last Resort | 250 | 6 MP | Self; Sure | T2: physical HP damage dealt ×1.20 and physical HP damage received ×1.20. Both parts form one effect and expire or are dispelled together. | Adaptation: Attack at the expense of defense. [Source][drk11] |
| DRK-A6 Crushing Blow | 300 | 12 MP | r2, one enemy; A then S ×0.5 | 1.00P weapon-elemental; after positive damage attempt Stop. | Adaptation: Sword damage with Stop. [Source][drk] |
| DRK-A7 Abyssal Blade | 300 | 12 MP + 20% max HP | Line 3, any units; A | Weapon-elemental: 1.40P at tile 1, 1.10P at tile 2, 0.80P at tile 3. Pay HP once. A straight line replaces the source's cone. | Adaptation: Health sacrifice, distance-falloff wave. [Source][drk] |
| DRK-A8 Unholy Sacrifice | 400 | 16 MP + 30% max HP | Self cross, any units except self; A then S ×0.5 | 1.50P Dark to each target; after positive damage attempt Slow. Never drains. | Adaptation: Health sacrifice, dark area damage and Slow. [Source][drk] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| DRK-S1 Desperation | Support | 200 | Direct physical and magical HP damage dealt ×1.30 while at 35% maximum HP or less, checked after paying costs. Works with any weapon and command. Does not increase HP costs, healing, MP damage, item effects, or damage-over-time. | Cross-job support design: Dangerous offense at low health, usable by martial and magical builds. [Inspiration][drk] |
| DRK-S2 Bloodcasting | Support | 350 | For a voluntarily selected action with an MP cost, pay 2 HP per MP that would otherwise be spent, and spend no MP. Add any native HP cost separately; the combined payment must leave at least 1 HP. Pay after target validation and before accuracy, once per action. Costs trigger no reactions and cannot be reduced by damage protection. Items, JP, and non-MP costs are unchanged. Applies to every command; does not grant access to a command or change its Silence rules. | Cross-job support design: Trade life for action resources across spell and technique sets. [Inspiration][drk] |
| DRK-R1 Dark Ward | Reaction | 250 | After surviving enemy magical HP damage, 35% activation: apply Shell to self. Does not reduce the triggering damage. | Original extension: Original reactive variant of the Dark Mind ward. [Source][drk14] |
| DRK-R2 Vengeful Pulse | Reaction | 350 | After surviving adjacent enemy physical damage, 30% activation: retaliate for Dark damage equal to 20% of HP actually lost, capped at 10% user max HP. No hit roll; elemental immunity/absorption applies. No healing. | Original extension: Original dark retaliation fueled by injury. [Source][drk] |

**DRK-C1 Abyss Combo — 100 AP:** Requires sword, greatsword, or broadsword; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider. FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Source][manual]

**Playstyle and limits:** Human Chivalry or Bangaa Prayer can support the HP economy. Slow growth in Speed and substantial self-costs remain weaknesses. Only some arts are Dark-elemental: darkness in a name does not automatically override the documented element.

## 6. Viking — Bangaa

**Command: Reaving.** An axe-bearing plunderer who calls lightning and fights through hostile conditions. The main model is FFTA2's Seeq Viking, reassigned to Bangaa for our roster; that racial reassignment is ours. Main reference: [FFTA2 Viking (originally Seeq)][vik].

This revision gives Viking access to the new two-handed Axe family, replacing its broadsword placeholder. It shares equipment access, not Soldier/Gladiator lessons. Strong-Arm and Pillage require an axe. Thunder tiers and Tsunami are magic, blocked by Silence; eligible Thunder spells follow vanilla Reflect/Return Magic behavior. Tsunami is an environmental wave and is neither Reflected nor Returned. War Cry and theft work while Silenced. No Doublecast. War Cry improves ailment resilience, not offense.

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| VIK-A1 Thunder | 100 | 8 MP | r3, one target; A | M24 Lightning. Use the original Thunder damage/effect routine where possible, preserving the new command's targeting. | Adaptation: Lightning spell. [Source][vik] |
| VIK-A2 Pickpocket | 150 | 0 MP | r1, one enemy; S | Use the original Steal Gil payout and per-target success restrictions. No invented unlimited gil source. | Adaptation: Gil theft. [Source][vik] |
| VIK-A3 Strong-Arm | 200 | 4 MP | r1, one enemy; A then S | 0.75P weapon-elemental; after positive damage attempt original Steal: Access. against an eligible accessory. A failed or unavailable theft does not cancel damage. This narrows A2 item theft to an existing FFTA theft category; no generic Steal Item command is assumed. | Adaptation: Damage plus item theft, adapted to accessories. [Source][vik] |
| VIK-A4 War Cry | 200 | 6 MP | Self cross, allies including self; Sure | T2: reduce incoming hostile S-check success chances by 15 percentage points, minimum 0. Does not affect attacks, damage, or effects that do not make a status check; immunity still wins. | Adaptation: Ailment resilience, not Attack. [Source][vik] |
| VIK-A5 Thundara | 250 | 14 MP | r3 center, cross, any units; A | M32 Lightning to each target. | Adaptation: Mid-tier lightning magic. [Source][vik] |
| VIK-A6 Pillage | 300 | 8 MP | r1, one enemy; A then S | 0.85P weapon-elemental; after positive damage attempt the original Steal Armor transaction against body equipment only. Preserve protection and theft immunity. | Adaptation: Damage plus armor theft. [Source][vik] |
| VIK-A7 Thundaga | 300 | 20 MP | r3 center, cross, any units; A | M40 Lightning to each target. | Adaptation: High-tier lightning magic. [Source][vik] |
| VIK-A8 Tsunami | 400 | 18 MP | r4 center, cross, any units; A | M36 Water on any terrain. If mapped water occupies the caster tile or an orthogonally adjacent tile within 2 height, successful positive damage also removes up to 8 MP per target. No MP recovery and no water-movement permission. | Thematic redesign: Sea power redesigned to function on land, with water proximity enhancing its effect. [Inspiration][vik] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| VIK-S1 Sea Legs | Support | 200 | Ignore forced tile displacement. Works with every job and weapon. Does not stop Immobilize, Slow, voluntary movement, or terrain harm, and does not grant water traversal. | Cross-job support design: A raider keeps their footing; transferable positional protection. [Inspiration][vik] |
| VIK-S2 Opportunist | Support | 350 | Direct physical and magical HP damage dealt ×1.20 against a target with at least one harmful status at the start of the action. Qualifying examples include Poison, Blind, Silence, Slow, Immobilize, Disable, Confuse, Sleep, and tagged custom debuffs. Multiple ailments do not multiply the bonus. The action cannot qualify itself by applying a status after its own damage. No weapon or theft requirement. | Cross-job support design: A raider exploits openings created by any ally or command. [Inspiration][vik] |
| VIK-R1 Absorb Damage | Reaction | 250 | After surviving positive enemy HP damage, 35% activation: recover 10% of actual HP lost. Does not reverse lethal hits or trigger from HP costs. | Adaptation: Damage recovery; a chance and lockout are added here. [Source][vik] |
| VIK-R2 Gil Snapper | Reaction | 350 | After surviving an enemy critical physical hit, 35% activation: gain floor(0.5 × actual HP lost) gil, capped at 50 per battle per unit. No cost to the attacker's inventory. | Adaptation: Gil after a critical hit; payout and battle cap are ours. [Source][vik] |

**VIK-C1 Tempest Combo — 100 AP:** Requires axe; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider. FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Source][manual]

**Playstyle and limits:** Axes provide ordinary offense, thunder provides magical coverage, and theft supplies utility. Water proximity enhances Tsunami; the wave is useful on land too. Moderate magic growth supports the actual spells without making Viking a superior Black Mage. No new forced-targeting AI system is implied.

## 7. Geomancer — Nu Mou

**Command: Geomancy.** A battlefield controller who shapes natural forces to damage enemies, protect allies, and influence movement. The [landscape-magic tradition][geo] supplies its identity. Every learned action works on ordinary terrain; local affinity provides an additional advantage instead of permission to use the skill.

No weapon required. Damaging actions use Magic Power and Magic Resistance. Silence, Reflect, Return Magic, and Doublecast do not apply. Stronger baseline actions now spend MP. Standard damage/target rules apply; only Tanglevine and native Rime Field make their listed additional status checks.

**Nearby affinity:** check the caster's tile and four orthogonal neighboring tiles within 2 height. Relevant mapped groups are rock/stone, vegetation, water/wetland, wood/heat, and snow/ice. An action gets at most one instance of its bonus. Neighbors can be inaccessible to the caster; sensing water does not let a unit enter it. Unknown tiles supply no affinity but disable no action. For Gaia Surge, choose one eligible element in the preview; Wind is always eligible. An element-aware effect such as Nature's Wrath reuses the last chosen eligible Gaia element, otherwise Wind. Float does not stop nearby attunement.

**Frost field:** Rime Field creates one cross of affected ground per caster; replacing it removes that caster's previous field. Expire it at the end of the caster's second subsequent turn, excluding placement turn; caster KO, Petrify, job change, or battle end clears it. Overlapping fields charge only one extra movement point per entered tile. Float/flying units and equipped Surefoot ignore that extra cost. Surefoot also works on other mapped movement surcharges. It causes no falling damage, new impassability, entry damage, or reaction triggers. It does not change a tile's affinity or enable a bonus to the cast that created it. Show affected tiles and adjusted movement paths. This is a new mechanic requiring implementation work.

Wisp Exposure refreshes rather than stacks; the stronger magnitude wins and a weaker cast cannot refresh a stronger one. It is removable by our broad-remedy handling for custom harmful effects. Elemental immunity or absorption prevents damage-triggered riders; stated status/custom-effect immunity still applies. Earthen Ward's displacement protection uses the strongest existing equivalent, not a second stack.

| ID / action | AP | Cost | Target / hit | Proposed effect | Inspiration |
|---|---:|---|---|---|---|
| GEO-A1 Stone Pulse | 100 | 4 MP | r3 center, cross, any units except caster; A | M26 Earth. Rock affinity increases damage ×1.20. | Thematic redesign: Original reliable earth pressure; terrain rewards damage rather than unlocking the spell. [Inspiration][geo] |
| GEO-A2 Tanglevine | 150 | 6 MP | r3, one enemy; A then S | M24 non-elemental; after positive damage attempt Immobilize with S. Vegetation affinity adds 15 percentage points to the final S chance, capped at 95% before defensive reductions; immunity still wins. | Thematic redesign: Binding vegetation with a useful damage baseline and a stronger native control effect. [Inspiration][geo] |
| GEO-A3 Torrent | 200 | 8 MP | r3 center, cross, any units except caster; A | M28 Water. With water affinity, after positive damage push each target one tile in the chosen cardinal direction if legal. Blocked displacement leaves damage intact. | Thematic redesign: Original wave control that breaks formations rather than copying a transformation rider. [Inspiration][geo] |
| GEO-A4 Updraft | 200 | 6 MP | r3, one ally or self; Sure | Apply Float and Move +1 for T2. If caster stands at least two height units above target, also grant Jump +1 for T2. No immediate movement, flight, or new permission to occupy impassable tiles. Float uses its normal status removal rules. | Thematic redesign: Original wind assistance; positioning and traversal utility. [Inspiration][geo] |
| GEO-A5 Earthen Ward | 250 | 10 MP | r3 center, cross, allies including self; Sure | Apply Protect. With rock affinity, also prevent forced displacement for T2. Does not prevent voluntary movement or Immobilize. | Thematic redesign: Original earth protection that steadies an allied formation. [Inspiration][geo] |
| GEO-A6 Wisp Flame | 300 | 10 MP | r3, one enemy; A | M28 Fire; after positive damage inflict Wisp Exposure for T2: magical HP damage received ×1.15. Wood/heat affinity instead applies ×1.25. This new debuff has no second success roll; immunity to the new effect prevents the rider, not damage. | Thematic redesign: Original spirit flame that creates an opening for allied magic. [Inspiration][geo] |
| GEO-A7 Rime Field | 300 | 12 MP | r3 center, cross, any units except caster; A | M28 Ice, then place a frost field on the targeted cross even if damage misses. Entering a field tile costs one additional Move point for any grounded unit, including allies. Ice affinity also attempts Slow with S after positive damage. | Thematic redesign: Original persistent ice terrain for area denial; native ice adds further control. [Inspiration][geo] |
| GEO-A8 Gaia Surge | 400 | 18 MP | r4 center, cross, any units except caster; A | M40 with an element selected from available nearby affinities: Earth for rock, Water for water, Fire for wood/heat, Ice for ice. Wind is always available. No affinity is consumed; this action has no additional native damage bonus. | Thematic redesign: Original major nature release whose elemental options respond to surroundings. [Inspiration][geo] |

| ID / passive | Type | AP | Effect while equipped | Inspiration |
|---|---|---:|---|---|
| GEO-S1 Attunement | Support | 200 | Elemental direct HP damage dealt ×1.20 when the resolved element is a weakness of the target after ordinary affinity rules. Applies to any physical or magical attack, including elemental weapons and secondary commands. Requires neither Geomancy nor nearby terrain. Neutral, resisted, immune, absorbed, non-elemental, healing, and damage-over-time outcomes gain nothing. | Cross-job support design: Understand elemental vulnerability and apply that knowledge to any technique. [Inspiration][geo] |
| GEO-S2 Surefoot | Support | 350 | Jump +1. Entering an otherwise legally traversable tile pays its normal one-tile movement cost without added terrain movement surcharges, including Rime Field. Does not remove height restrictions, environmental damage or ailments, blocking units, or impassability; no flight or extra movement action. | Cross-job support design: Read and traverse difficult ground, regardless of current profession. [Inspiration][geo] |
| GEO-R1 Stone Skin | Reaction | 250 | After surviving enemy physical HP damage, 40% activation: apply Protect to self. Works on any terrain. | Thematic redesign: Original earthen defense with a dependable opportunity to contribute across maps. [Inspiration][geo] |
| GEO-R2 Nature's Wrath | Reaction | 350 | After surviving enemy HP damage, 35% activation: counter that attacker alone within r3 for M20, A accuracy. Choose the element of the highest-AP learned damaging Geomancy action; Gaia Surge uses the selected current affinity if available, otherwise Wind. No ailment, field, displacement, or Attunement bonus. No learned damaging action means no counter. | Thematic redesign: Reactive nature power; neither terrain permission nor a tiny status chance is required for its contribution. [Inspiration][geo] |

**GEO-C1 Gaia Combo — 100 AP:** Requires rod or mace; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider.

**How it plays:** use Stone Pulse for dependable area pressure, Tanglevine to threaten a key mover, Torrent to break a formation, or Rime Field to make an approach costly. Updraft and Earthen Ward help the party exploit that control; Wisp Flame creates a magic-damage opening. Gaia Surge supplies a substantial finish with environmentally influenced coverage. MP, friendly fire, enemy defenses, and a single active field constrain the kit. Damage power and field duration must be compared with actual FFTA encounters.

## 8. Chemist — Nu Mou and Moogle

**Command: Items.** An expert in medicines, thrown restoratives, and emergency treatment. FFT item handling is the primary model; FFV Pharmacology informs the optional potency support. This replaces the unsourced eye-drop flash bomb and multi-target Phoenix mixture. Main reference: [FFT Chemist / Items][chm].

All eight actions need no weapon, cost 0 MP, work while Silenced, and consume exactly one named item. Range is r4, one ally or self, Sure; Phoenix Down targets a KO ally. Use the verified vanilla USA item's healing amount, revival fraction, cure list, and immunity rules rather than inventing new potion contents. These are separate AP-learned ranged applications; ordinary Item access remains unchanged. For this draft the new restorative actions accept non-undead allies only. No Reflect, Return Magic, or Doublecast.

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| CHM-A1 Potion | 100 | 1 Potion | r4, one ally or self; Sure | Apply the vanilla Potion effect. | Adaptation: Basic restorative. [Source][chm] |
| CHM-A2 Antidote | 150 | 1 Antidote | r4, one ally or self; Sure | Apply the vanilla Antidote cure. | Adaptation: Poison treatment. [Source][chm] |
| CHM-A3 Phoenix Down | 200 | 1 Phoenix Down | r4, one KO ally; Sure | Apply the vanilla Phoenix Down revival, minimum 1 HP. | Adaptation: Item-based revival. [Source][chm] |
| CHM-A4 Hi-Potion | 200 | 1 Hi-Potion | r4, one ally or self; Sure | Apply the vanilla Hi-Potion effect. | Adaptation: Stronger restorative. [Source][chm] |
| CHM-A5 Eye Drops | 250 | 1 Eye Drops | r4, one ally or self; Sure | Apply the vanilla Eye Drops cure. It treats blindness rather than causing it. | Adaptation: Blindness treatment. [Source][chm] |
| CHM-A6 Ether | 300 | 1 Ether | r4, one ally or self; Sure | Apply the vanilla Ether MP recovery. | Adaptation: MP restorative. [Source][chm] |
| CHM-A7 Cureall | 300 | 1 Cureall | r4, one ally or self; Sure | Apply the vanilla Cureall cure list; additionally clear our new harmful Polka, Heathen Frolic, Exposed, and Wisp Exposure modifiers. Does not remove Last Resort's drawback separately from its benefit. | Adaptation: FFT Remedy role using the actual FFTA consumable Cureall. [Inspiration][chm] |
| CHM-A8 X-Potion | 400 | 1 X-Potion | r4, one ally or self; Sure | Apply the vanilla X-Potion effect. | Adaptation: High-grade restorative. [Source][chm] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| CHM-S1 Pharmacology | Support | 200 | Direct HP and MP restoration from consumed restorative items ×1.50, then round down and cap at the recipient's missing resource. Applies to ordinary Item, Chemist actions, other consumable-based commands, and item-consuming reactions such as Auto-Potion. Does not improve revival HP, cure lists, drain, or magic; full restoration remains full restoration. Only the item user's support supplies this modifier. | Cross-job support design: Expert medicine preparation transfers to any use of supplies. [Inspiration][chm5] |
| CHM-S2 Long Throw | Support | 350 | For a consumable-based single-target action that can normally target another unit, a base range below 4 becomes 4; a base range of 4 or more gains +1, capped at 5 and never reduced below its original range. Applies to ordinary Item, Chemist applications, and eligible future mixtures. Retain target, height, and line-of-sight restrictions. Does not turn self-only or area effects into ranged single-target effects, and does not extend weapon attacks. | Cross-job support design: Throw supplies accurately across the battlefield from any job. [Inspiration][chm] |
| CHM-R1 Auto-Potion | Reaction | 250 | After surviving enemy HP damage at 30% HP or below, 50% activation: consume one Potion and apply its vanilla recovery to self. Never substitute Hi-Potion or X-Potion. Requires stock; Pharmacology applies if equipped. | Adaptation: Automatic inventory-funded treatment; selection and threshold adapted. [Inspiration][chm] |
| CHM-R2 Auto-Cureall | Reaction | 350 | After surviving an enemy action that inflicted a Cureall-curable ailment, 35% activation: consume one Cureall and apply its cure to self. Requires stock and ability to react; cannot rescue KO or bypass reaction-blocking statuses. | Original extension: Original extension of emergency item use; no free magical regeneration. [Source][chm] |

**CHM-C1 Flask Combo — 100 AP:** Requires knife or mace; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider. FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Source][manual]

**Playstyle and limits:** Available without prerequisites for both races. Ranged reliable recovery is purchased with inventory and gil, while Pharmacology competes with additional throw range. Neither race needs White Mage access to use it. Mixtures could be a future FFV-inspired extension, but no invented recipe is presented as established lore.

## 9. Bard — Moogle

**Command: Song.** A traveling musician following Hurdy's FFTA2 model: bolster companions, restore them, and repel undead. The shared names Battle Chant and Magickal Refrain use their A2 defensive roles, not their different FFT offensive roles. Main reference: [Bard comparison: Hurdy in FFTA2 and FFT Bard][brd].

Songs require a primary instrument and are blocked by Silence; no Reflect, Return Magic, or Doublecast. Hide is a nonmagical self action and is the exception: it needs neither instrument nor voice. Songs resolve once using an action, not as perpetual auras. An actual MP song is included; the misnamed healing Finale is removed.

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| BRD-A1 Soul Etude | 100 | 8 MP | r3, one ally or self; Sure | Heal 20% target max HP, capped at 100; remove Poison, Blind, Silence, and Confuse. Cannot sing it while already Silenced. | Adaptation: Healing plus cleansing. [Source][brd] |
| BRD-A2 Battle Chant | 150 | 8 MP | Self cross, allies including self; Sure | Apply Protect, our representation of A2 defense enhancement. | Adaptation: Defense song. [Source][brd] |
| BRD-A3 Magickal Refrain | 200 | 8 MP | Self cross, allies including self; Sure | Apply Shell, our representation of A2 resistance enhancement. | Adaptation: Magical defense song. [Source][brd] |
| BRD-A4 Requiem | 200 | 8 MP | r3, one undead enemy; A | M32 Holy; invalid against living targets. No instant KO or resurrection suppression. | Adaptation: Anti-undead song. [Source][brd] |
| BRD-A5 Angelsong | 250 | 10 MP | Self cross, allies including self; Sure | Apply Regen. | Adaptation: Regeneration song. [Source][brd] |
| BRD-A6 Hide | 300 | 0 MP | Self; Sure | Apply the original Invisible status with its ordinary break/removal rules. Does not give movement or an extra action. | Adaptation: Self-concealment. [Source][brd] |
| BRD-A7 Magick Ballad | 300 | 6 MP | r3, one ally other than caster; Sure | Restore 8 MP, capped at missing MP. Self-targeting excluded; any remaining two-Bard economy must be evaluated in balance testing. | Adaptation: MP-restoring song. [Source][brd] |
| BRD-A8 Nameless Song | 400 | 16 MP | Self cross, allies including self; Sure | For each ally choose uniformly from Protect, Shell, Regen, and Haste, then apply that status. No reroll for existing status or immunity. Preview shows the four possibilities. | Adaptation: Random beneficial song. [Source][brd] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| BRD-S1 Encouragement | Support | 200 | When a voluntary action successfully adds a new beneficial status to another ally, also restore 10% of that ally's maximum HP, capped at 30 HP before incoming-healing modifiers. Once per ally per action, even if several statuses are applied. Applies to all commands. Refreshing an existing status or its duration does not qualify; merely healing or curing does not qualify. No self-target bonus or reaction trigger. | Cross-job support design: Inspiring aid makes protective and enhancing actions more useful. [Inspiration][brd] |
| BRD-S2 Clear Voice | Support | 350 | Immune to Silence while equipped, regardless of job, weapon, or command. No protection against other ailments. Does not grant magic, an instrument, or access to a voice-based command. Ordinary status-immunity handling applies. | Cross-job support design: Vocal discipline protects both songs and spellcasting. [Inspiration][brd] |
| BRD-R1 Magick Boost | Reaction | 250 | After surviving enemy magical HP damage, 35% activation: magical HP damage dealt ×1.15, T2. Does not strengthen fixed or percent healing. | Adaptation: FFT Bard's reactive magical growth made temporary. [Source][brd] |
| BRD-R2 Encore | Reaction | 350 | After surviving enemy physical HP damage, 35% activation: with an instrument and while not Silenced, recover 5% max HP through a brief reprise. No cleanse or revival. | Original extension: Original reduced self-reprise of Soul Etude. [Source][brd] |

**BRD-C1 Chorus Combo — 100 AP:** Requires instrument; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider. FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Source][manual]

**Playstyle and limits:** Support is mostly dependable, with Nameless Song as an explicitly random option. Item support through secondary Chemist works while Silenced. Moogle White Magic is not available. Low physical offense, nearby group positioning, and voice dependence constrain the job.

## 10. Dancer — Viera

**Command: Dance.** A nimble performer who weakens enemies through rhythm and steals vitality. The repertoire follows FFT/FFTA2 disruption, with FFV's recognizable Sword Dance as its weapon finisher. Healing dances do exist elsewhere in FF; this particular job deliberately specializes in enemy disruption. Main reference: [Dancer comparison: FFT, FFV, and FFTA2][dnc].

Dance is performance, not incantation: usable while Silenced; no Reflect, Return Magic, or Doublecast. Sword Dance requires a primary knife or rapier; other actions do not. Dances resolve once within tactical range, rather than repeatedly affecting the whole map. They do not advance, reset, or refund turns.

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| DNC-A1 Mincing Minuet | 100 | 4 MP | r3 center, cross, enemies; A | Physical damage using a virtual non-elemental weapon of Attack 12 in the normal P reference. Actual weapon Attack, element, and procs do not enter this formula. | Adaptation: Area HP-damaging dance. [Source][dnc] |
| DNC-A2 Witch Hunt | 150 | 6 MP | r3 center, cross, enemies; A | Remove 6 MP from each successful target, capped at current MP. No recovery to dancer. | Adaptation: MP-damaging dance. [Source][dnc] |
| DNC-A3 Slow Dance | 200 | 8 MP | r3, one enemy; S | Apply Slow. A timed FFTA status replaces the source's direct Speed reduction. | Adaptation: Disrupt enemy tempo. [Source][dnc] |
| DNC-A4 Polka | 200 | 8 MP | r3, one enemy; S | T2: physical HP damage dealt ×0.85. | Adaptation: Weaken physical offense. [Source][dnc] |
| DNC-A5 Heathen Frolic | 250 | 8 MP | r3, one enemy; S | T2: magical HP damage dealt ×0.85. Does not weaken item effects, fixed damage, or healing. | Adaptation: Weaken magical offense. [Source][dnc] |
| DNC-A6 Forbidden Dance | 300 | 12 MP | r3 center, cross, enemies; S | For each target choose uniformly from Blind, Silence, Poison, and Confuse; then make its S check. Do not reroll immunities. No Petrify, KO, or turn reset in the pool. | Adaptation: Random ailments with a restricted pool. [Source][dnc] |
| DNC-A7 Jitterbug | 300 | 10 MP | r2, one enemy; A | 0.75P using a virtual non-elemental weapon of Attack 18. Drain 50% of actual HP removed, capped at 15% user max HP. Undead reverse drain. | Adaptation: HP-draining dance. [Source][dnc] |
| DNC-A8 Sword Dance | 400 | 16 MP | r1, one enemy; A | 1.60P weapon-elemental, one hit. Unlike FFV's random Dance result, select it directly after learning and pay MP. | Adaptation: FFV physical dance finisher. [Source][dnc] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| DNC-S1 Grace | Support | 200 | Base Evade +10 before ordinary facing, equipment calculations, and caps. Applies with any job and weapon; it is not a universal ten-percentage-point dodge bonus against every effect. | Cross-job support design: Evasive footwork transferable to any combat style. [Inspiration][dnc] |
| DNC-S2 Light Foot | Support | 350 | Move +1 on any current job. No second movement action, flight, terrain immunity, or free ability slot. | Cross-job support design: A performer's mobility becomes a general positioning tool. [Inspiration][dnc] |
| DNC-R1 Fury | Reaction | 250 | After surviving enemy physical HP damage, 35% activation: physical HP damage dealt ×1.15, T2. No permanent stat growth. | Adaptation: FFT Dancer's reactive offense made temporary. [Source][dnc] |
| DNC-R2 Counter Rhythm | Reaction | 350 | After surviving adjacent enemy physical HP damage, 30% activation: attempt Slow on that attacker with S. | Original extension: Original reactive echo of Slow Dance. [Source][dnc] |

**DNC-C1 Waltz Combo — 100 AP:** Requires knife or rapier; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider. FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Source][manual]

**Playstyle and limits:** Physical growth supports its damaging dances while status actions create openings. Spirit Magic adds other debuffs; White Magic remains an optional separate healing set. Fragility, enemy immunity, and MP costs constrain repeated disruption.

## 11. Mystic Knight — Viera

**Command: Spellblade.** An FFV-style enchanted-weapon specialist: choose an elemental or status enchantment, then exploit it through sustained sword attacks. This replaces disposable sigils and invented finishers. Runic belongs to a different FF tradition and no spell-absorption kit is implied here. Main reference: [FFV Mystic Knight][myk].

All eight actions target self, Sure, require a primary rapier or saber, and are blocked by Silence. One enchantment lasts until replaced, Dispel, KO, Petrify, loss/change of the primary weapon, job change, or battle end. Ordinary attacks do not consume it. Silence after preparation prevents re-enchanting but does not erase the existing effect or stop Fight. Only the primary strike of ordinary Fight benefits; other weapon strikes, secondary techniques, reactions, and combos do not. Enchantments replace the primary weapon's element and status proc, rather than stacking an item proc with them. No Reflect, Return Magic, or Doublecast.

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| MYK-A1 Fire Spellblade | 100 | 6 MP | Self; Sure | Primary Fight strike becomes Fire-elemental. No separate spell hit or damage bonus beyond elemental interaction. | Adaptation: Fire enchantment. [Source][spell] |
| MYK-A2 Blizzard Spellblade | 150 | 6 MP | Self; Sure | Primary Fight strike becomes Ice-elemental. | Adaptation: Ice enchantment. [Source][spell] |
| MYK-A3 Thunder Spellblade | 200 | 6 MP | Self; Sure | Primary Fight strike becomes Lightning-elemental. | Adaptation: Lightning enchantment. [Source][spell] |
| MYK-A4 Poison Spellblade | 200 | 6 MP | Self; Sure | Primary Fight strike becomes non-elemental; after positive damage attempt Poison with S ×0.5. | Adaptation: Poison enchantment. [Source][spell] |
| MYK-A5 Sleep Spellblade | 250 | 8 MP | Self; Sure | Primary Fight strike becomes non-elemental; after positive damage attempt Sleep with S ×0.5. Resolve the sleep after damage, so the same hit does not immediately wake the target. | Adaptation: Sleep enchantment. [Source][spell] |
| MYK-A6 Silence Spellblade | 300 | 8 MP | Self; Sure | Primary Fight strike becomes non-elemental; after positive damage attempt Silence with S ×0.5. | Adaptation: Silence enchantment. [Source][spell] |
| MYK-A7 Drain Spellblade | 300 | 12 MP | Self; Sure | Primary Fight strike becomes non-elemental; heal 20% of actual HP removed, capped at 8% user max HP per action. Undead reverse drain. | Adaptation: Draining enchantment. [Source][spell] |
| MYK-A8 Flare Spellblade | 400 | 24 MP | Self; Sure | Primary Fight strike becomes non-elemental and uses 75% of the target's effective Weapon Defense in its damage calculation. No extra damage multiplier. This is a much smaller defense bypass than FFV. | Adaptation: Non-elemental defense-piercing enchantment. [Source][spell] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| MYK-S1 Spellweave | Support | 200 | Alternate a voluntary incanted magic action and a physical-damage action. If the current action is the opposite category to the preceding qualifying action, its direct HP damage ×1.20; any physical weapon or command qualifies. Spellblade preparation counts as magic even though it causes no damage, so it can prepare a boosted physical attack. An action with no qualifying category breaks the sequence; repeating a category sets that as the last category without a bonus. No healing, drain-recovery, item, or reaction bonus. Magic acts resolve using an explicit command/effect classification, not simply a nonzero MP cost. | Cross-job support design: Combine martial and magical actions across different command sets. [Inspiration][myk] |
| MYK-S2 Arcane Ward | Support | 350 | Magical HP damage received ×0.75 while current MP is at least 50% of maximum MP at the start of the incoming action, with at least 1 MP remaining. Does not spend MP, absorb a spell, or reduce HP costs. Works with every job and weapon. | Cross-job support design: Maintained magical reserves protect their bearer. [Inspiration][myk] |
| MYK-R1 Magic Shell | Reaction | 250 | After surviving enemy HP damage at 30% max HP or less, 50% activation: apply Shell. Does not reduce the triggering hit; not blocked merely by Silence. | Adaptation: FFV low-health Shell placed in FFTA's reaction slot. [Source][myk] |
| MYK-R2 Spell Parry | Reaction | 350 | Requires a qualifying equipped weapon and active enchantment. 25% pre-hit activation: incoming enemy physical HP damage ×0.5 for that action. Does not consume the enchantment. | Original extension: Original magically reinforced sword guard. [Source][myk] |

**MYK-C1 Spellblade Combo — 100 AP:** Requires rapier or saber; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider. FFTA integration: Original job-specific label for vanilla Judge Point combo participation. [Source][manual]

**Playstyle and limits:** A preparation turn pays off across later Fight actions. Existing Gladiator elemental attacks remain immediate; this job cannot automatically imbue them. Balanced physical development matters more than Magic Power because the enchantments modify weapon attacks. Break/Petrify and an unrestricted status-on-hit guarantee are deliberately absent.

## 12. Teaching equipment and availability

Teaching the revised supports uses the existing proposed S1/S2 item positions and AP costs. Eight new teaching weapons per job make 64, plus eight Soldier/Gladiator teaching axes make **72 proposed items**. Existing item stats and lessons stay intact. W1–W8 teach A1–A8 respectively. Additional lessons: W2 teaches S1, W3 combo, W4 R1, W5 S2, W6 R2. Each job has 1,900 action AP, 550 support AP, 600 reaction AP, and 100 combo AP: 3,150 total lesson AP, with simultaneous lessons progressing normally.

| Job / category | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 |
|---|---|---|---|---|---|---|---|---|
| Samurai / Katana | Ashura Echo | Wind Reed | Osafune Echo | Murasame Echo | Kiyomori Echo | Guarding Blade | Kiku Echo | Moonblossom |
| Dark Knight / Sword | Gloom Sword | Sanguine Edge | Infernal Edge | Veil Sword | Oathbreaker | Crushing Edge | Abyssal Edge | Sacrifice Edge |
| Viking / Axe | Storm Axe | Raider Axe | Plunder Axe | Warcaller Axe | Squall Axe | Pillage Axe | Thunderhead Axe | Tidal Axe |
| Geomancer / Rod | Stone Rod | Root Rod | River Rod | Zephyr Rod | Wardstone Rod | Wisp Rod | Rime Rod | Gaia Rod |
| Chemist / Knife | Tonic Knife | Antidote Knife | Phoenix Knife | High Tonic Knife | Clear Eye Knife | Ether Knife | Remedy Knife | Restorer Knife |
| Bard / Instrument | Etude Pipe | Battle Pipe | Refrain Pipe | Requiem Pipe | Angel Pipe | Traveler Pipe | Ballad Pipe | Nameless Pipe |
| Dancer / Rapier | Minuet Foil | Witch Foil | Tempo Foil | Polka Foil | Frolic Foil | Forbidden Foil | Jitterbug Foil | Danceblade |
| Mystic Knight / Saber | Ember Saber | Rime Saber | Spark Saber | Venom Saber | Dream Saber | Hush Saber | Siphon Saber | Flare Saber |

These are new proposed item names. An Echo katana teaches the named sword spirit without changing the vanilla weapon bearing a similar name. A teaching weapon's name never grants an unlisted proc or power. Chemist uses the actual FFTA consumable **Cureall**, not an assumed inventory item named Remedy. [FFTA item reference][items].

Weapon Attack targets, W1–W8: Samurai/Dark Knight/Viking/Mystic Knight 18/22/26/30/34/38/42/46; Dancer/Chemist 14/17/20/23/26/29/32/35; Bard 12/15/18/21/24/27/30/33; Geomancer 10/12/14/16/18/20/22/24 with Magic Power bonuses 0/2/4/6/8/10/12/14. Other bonuses are zero; no innate element, proc, or automatic status. Categories use original handedness except new axes, which are two-handed and exclude shields/second weapons.

Prices: 300/600/1,000/1,600/2,400/3,400/4,800/6,500 gil. W1–2 are initial shop-tier stock; W3–4 first expansion; W5–6 second; W7–8 last pre-final-story expansion. These anchors require real story-flag mapping. Gear may be purchased before a job unlocks, but only an eligible active job learns its lessons. All gear must remain repeatably obtainable. Chemist's later medicine lessons must coincide with repeatable ingredient access; no early X-Potion availability is assumed.

Viking can equip all new axes, but only learns its Reaving lessons on Viking teaching axes. Soldier and Gladiator likewise learn only their own documented lessons. See [the axe addendum](AXE-SKILL-EXPANSION.md) for their eight weapons and twelve entries. Viking axe access is now part of this revised design; Warrior does not automatically gain axe access.

## 13. Implementation, balance, and acceptance

This is a source-audited design, **not an implemented or balance-tested patch**. The roster, progression, job identity, ability behavior, provisional growths, equipment, and learning scheme are specified; storage capacity and effect support remain unproven. FFTA is the clean base, with no third-party overhaul. Existing abilities, growths, stories, laws, missions, and recruitment rules stay intact except the selected additive Soldier/Gladiator changes. Squire and Sentinel remain rejected; Green Mage is only a candidate.

Before full implementation, prove a new job record, one ability, teaching equipment, AP mastery, and ordinary save/load without occupying existing records. Count actual new records only after identifying safely reusable effects. Validate ten race/job implementations, ability-list lengths, mastery storage, icons, sprites, animation states, equipment categories, shops, and law dispatch. New Axe permission must be represented across all three intended jobs and all relevant interfaces, not just assigned a spare numeric type.

Terrain requires a tile-ID affinity map and a new field implementation. Unknown tiles provide no affinity; the complete base toolkit remains available. Verify field expiry, overlapping fields, path costs, Float/Surefoot, chosen elemental previews, and terrain heights. Tsunami does not grant water movement. Item effects, stealing, Invisible, status cures, and drain behavior require clean-ROM confirmation. No data-only implementation is assumed.

Law integration must check effect as well as command: Viking now contains magic and theft, Chemist uses real items, and Spellblade changes effective attack elements. Any command aliases to existing law categories must be mapped and documented per action after investigation. A single blanket Reaving-to-Battle-Tech alias is insufficient. No new law cards or hidden exemptions are proposed.

Meaningful balance cases:

1. Compare matched equipment tiers around levels 10, 25, and 40. Samurai against Fighter/Ninja plus nearby support; Viking against Warrior/Defender and Black Mage damage; Geomancer against Black Mage/Sage; Chemist against ordinary Item/White Mage; Bard and Dancer against other support options; Mystic Knight against Fencer/Red Mage and Gladiator-style immediate attacks.
2. Include setup turns and whole-battle resources. Persistent Flare Spellblade, MP-funded Geomancy, Centered technique chains, magic vulnerability, persistent fields, MP songs, drain loops, theft, and Gil Snapper need explicit testing. Thematic correctness does not establish fair numbers.
3. At 200 max HP, Blood Edge costs 20, Abyssal Blade 40, and Unholy Sacrifice 60. Bloodcasting keeps the native HP costs and additionally converts MP costs as described above. Sanguine Sword removing 40 HP restores 10; removing 200 restores only its 20-HP cap. Check misses, immunity, overkill, undead, and unaffordable costs.
4. Exercise secondary sets, original Double Sword and Doublecast, Healer, damage/status supports, Reflect, Return Magic, all protections, reaction lockouts, direct and area attacks, forced movement, save/reload, and temporarily AI-controlled units. Valid-action generation must respect terrain, weapon, voice, inventory, and HP affordability.
5. Validate T2 at each turn phase; Last Resort's linked drawback; short Exposed; persistent Spellblade replacement/removal; status resistance without stacking; no permanent stat gains from Fury or Magick Boost. Verify Centered spending/expiry and weapon changes; Updraft buffs do not stack on repeated casts.
6. Preserve original Soldier/Gladiator moves, including Rush, Wild Swing, Beatdown, elemental attacks, and Strikeback where applicable. New axes are alternatives; Reaping Arc and Axe Reprisal must compete with existing choices, not merely rename them. Test old techniques and combos with new weapons.
7. **Support combinations:** verify all 18 on at least two legal non-teaching jobs, with no teaching-job action set equipped. Check ordinary Item with Pharmacology/Long Throw, original elemental actions with Attunement, movement before/after Composure and Follow Through, ally-applied status with Poise, and native HP-plus-MP costs with Bloodcasting. Compare each support against available vanilla alternatives in that race. Test healing across two units carrying Pharmacology and Recuperation, and spells/physical techniques alternating through Spellweave. New item modifiers must apply exactly once, including Auto-Potion.
8. Full release requires a fresh save, real battles, learning, job changes, ordinary save/load, campaign shop checks, and a reproducible patch from the verified clean ROM. Keep the original play/save files separate. Old-save migration is not promised until proven.

Source references document inspiration. They do not dictate the kit, and no source game is treated as a balance standard. [The modding guide](../../FFTA-MODDING-GUIDE.md) covers tooling and limitations. No ROM has been changed by this revision.

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
