# Axe skills for Soldier and Gladiator

Axe ability rules retain adopted version 0.5; global references updated for project version 0.7, September 14, 2026. Design only; no ROM patch applied.

Add four actions, one support and one reaction to each existing command. Preserve original Soldier/Gladiator moves, growths, armor, movement and prerequisites. No Squire, Sentinel, or Sentinel-to-Viking branch. The [class specification](JOB-CLASS-SPECIFICATION.md) owns shared combat, support, reaction, law, and learning rules. [Council rationale](BALANCE-COUNCIL.md).

## Weapon, geometry, and interaction rules

The new two-handed Axe family has ordinary range 1, no shield/second weapon, and no inherent armor bypass/random damage. Soldier, Gladiator, and Viking can equip it; Warrior and other jobs do not automatically gain permission. Equipment access does not grant another job's teaching lessons.

All eight actions require a primary axe. Recuperation and Follow Through are transferable, weapon-free supports; both reactions require an axe. Actions remain inside Battle Tech or Spellblade Tech, not a third command. They use physical P/A, work while Silenced, and cannot Reflect, Return Magic, Doublecast, crit, copy procs, or gain a second weapon strike. No axe is consumed. Mastered actions count toward existing owning-job unlock gates.

Frontal arc selects the tile directly ahead plus the two diagonals beside it, within 2 height, with friendly fire and no caster hit. Tomahawk needs projectile LOS. Shatter Guard removes Protect on a successful hit before damage; Armor Splitter reduces effective defense for that hit only. Exposed multiplies incoming direct physical damage by 1.20 until the next own turn starts, including immediate retaliation, even if Fell Cleave misses. It does not stack; KO/Petrify/battle end/broad remedy clears it. The action is unavailable if immunity would cancel its drawback at application. Protect may mitigate normally. Last Resort's linked drawback can multiply with Exposed to 1.44.

New reactions use dependable eligible activation and one opportunity per enemy action, without the former blanket turn lock. They retain range/weapon/survival requirements and no reaction chains. Follow Through requires ending voluntary movement at least two Manhattan tiles from turn-start position, not merely walking two tiles or circling back.

## Soldier — Human

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| SLD-AX-A1 Chop | 100 | 0 MP; axe; r1 enemy; A; 1.10P weapon-elemental. | Original extension: Original straightforward addition to Soldier's martial toolkit. [Inspiration][ffta] |
| SLD-AX-A2 Tomahawk | 150 | 4 MP; axe; r4 enemy with projectile line of sight; A; 0.90P weapon-elemental; no consume/unequip. | Adaptation: Marauder ranged axe attack; no MMO enmity. [Inspiration][axe14] |
| SLD-AX-A3 Overpower | 200 | 4 MP; axe; frontal three-tile arc, any units; A each; 0.90P weapon-elemental. | Adaptation: Marauder area axe attack. [Inspiration][axe14] |
| SLD-AX-A4 Shatter Guard | 300 | 6 MP; axe; r1 enemy; A; on hit remove Protect before calculating 1.00P weapon-elemental damage. | Original extension: Original guard-breaking extension of Soldier's weakening techniques. [Inspiration][ffta] |
| SLD-AX-S1 Recuperation | 150 | Direct restorative HP healing received ×1.50 from self/allied medicine and spells/techniques; round after combined modifiers. No revival, drain, Regen tick or MP improvement. | Cross-job support design: Frontline recovery training, useful to any unit taking sustained damage. [Inspiration][ffta] |
| SLD-AX-R1 Haft Guard | 150 | Primary axe required. Incoming physical direct HP damage ×0.75; no counter and no cross-action lock. | Original extension: Original mundane defense using the axe haft. [Inspiration][ffta] |

Soldier/Hunter is legal with an axe. Paladin/Battle Tech cannot use axe additions without axe permission. These techniques add practical reach/area/guard breaking; they do not replace original Soldier weakening moves.

## Gladiator — Bangaa

| ID / ability | AP | Current rules | Inspiration |
|---|---:|---|---|
| GLD-AX-A1 Armor Splitter | 200 | 8 MP; axe; r1 enemy; A; 1.00P weapon-elemental using 75% effective target WDef for this hit only. | Original extension: Original heavy-weapon penetration added to Gladiator's offensive kit. [Inspiration][ffta] |
| GLD-AX-A2 Reaping Arc | 250 | 8 MP; axe; frontal three-tile arc, any units; A each; 1.10P weapon-elemental. | Original extension: Original positional variant alongside Wild Swing. [Inspiration][ffta] |
| GLD-AX-A3 Executioner | 300 | 10 MP; axe; r1 enemy; A; 1.10P weapon-elemental normally, 1.80P when target at or below 50% max HP; in that condition add 20 percentage points to final ordinary A hit chance, capped 95%, after immunity/reaction checks. | Original extension: Original arena finisher; no claim of a canonical FFTA move. [Inspiration][ffta] |
| GLD-AX-A4 Fell Cleave | 400 | 16 MP; axe; r1 enemy; A; 1.80P weapon-elemental. Before hit apply Exposed x1.20 incoming physical damage until start of next user turn, even on a miss. | Adaptation: Warrior heavy axe strike; MP and Exposed replace MMO resources. [Inspiration][axe14] |
| GLD-AX-S1 Follow Through | 350 | During own turn, direct physical HP damage ×1.35 if voluntary movement placed the user at least two Manhattan tiles from turn-start position before action. Walking a loop to end near the origin does not qualify. Any weapon/physical command; no magical, item, reaction or DoT bonus. | Cross-job support design: Carry movement into an attack; transferable offensive momentum. [Inspiration][ffta] |
| GLD-AX-R1 Axe Reprisal | 350 | After surviving adjacent enemy physical HP damage, primary axe counters once for 1.20P with ordinary A accuracy and weapon element, no crit/proc. No cross-action lock. | Original extension: Original axe counter; compare with existing Strikeback rather than claiming a new role. [Inspiration][ffta] |

Viking/Gladiator can use both axe sets. Axe Gladiator/Dark Arts can use Dark Mind and Last Resort's any-primary-weapon commitment strike, but not sword-gated Sanguine Sword or sacrifice attacks. Original Rush, Wild Swing, Beatdown, elemental techniques, and Strikeback stay intact. Existing Soldier/Gladiator combo numbers and JP behavior are unchanged, with axe acceptance/animation added.

## Teaching axes

Eight additional items; all non-elemental, with no extra stat bonuses, automatic statuses, or procs. Both existing jobs and Viking can equip them, but only the listed owning job learns the lessons.

| Item | Weapon Attack | Price | Lessons |
|---|---:|---:|---|
| Recruit Axe | 20 | 300 gil | Soldier: Chop |
| Throwing Axe | 24 | 600 gil | Soldier: Tomahawk + Recuperation |
| Field Axe | 28 | 1,000 gil | Soldier: Overpower + Haft Guard |
| Breaching Axe | 32 | 1,600 gil | Soldier: Shatter Guard |
| Bearded Axe | 34 | 2,400 gil | Gladiator: Armor Splitter |
| Arena Axe | 38 | 3,400 gil | Gladiator: Reaping Arc + Follow Through |
| Headsman's Axe | 42 | 4,800 gil | Gladiator: Executioner + Axe Reprisal |
| Titan Axe | 46 | 6,500 gil | Gladiator: Fell Cleave |

Acquire every listed axe in Cyril, with matching stock in Sprohm when usable. Recruit/Throwing use S0 (opening stock); Field/Breaching use S1 (clear #005 Twisted Flow); Bearded/Arena use S2 (clear #011 Pale Company); Headsman's/Titan use S3 (clear #017 Desert Patrol). Stock is permanent and repeatably purchasable. These are our added stock gates, not native shop upgrades; ROM flags still require verification. Viking has nine separate teaching axes in the main specification. See [the complete acquisition ledger](WEAPON-ACQUISITION.md) for every weapon and lesson; sharing the family grants no cross-job lesson access.


## Learning and implementation

Soldier's additions total **1,050 AP**; Gladiator's total **1,850 AP**. Simultaneous lessons progress normally. The full project retains 129 entries and 85 teaching items; record capacity, animations, UI, law dispatch, shops, and mastery storage still need proof. Generic attack/price targets must be compared with actually available vanilla equipment. No original item, story, or save is changed by these documents.

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
