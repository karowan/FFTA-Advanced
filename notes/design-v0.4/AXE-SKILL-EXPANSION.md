# Axe skills for Soldier and Gladiator

Design version 0.4 — transferable support lessons, September 14, 2026. Expands vanilla USA FFTA; not implemented.

The [version 0.4 design principles](JOB-DESIGN-PRINCIPLES.md) now govern this draft: retain the jobs' identity while freely adapting mechanics for useful FFTA gameplay. Existing references are inspiration, not required moves or balance targets. The twelve entries below remain provisional. [The support redesign](SUPPORT-SKILL-DESIGN.md) makes their two support lessons useful after switching weapons and jobs.

No Squire or Sentinel, and no Sentinel → Viking branch. Human Soldier remains a starter; Bangaa Gladiator retains its original two-Warrior-action gate. Original job skills, growths, movement, armor, and prerequisites remain. This adds four actions, one support, and one reaction to each existing command set. [The main specification](JOB-CLASS-SPECIFICATION.md) owns shared combat rules and the eight-job roster.

**Theme:** Soldier gains practical axe handling alongside its existing weakening techniques. Gladiator gains arena-style heavy offense alongside its existing elemental attacks. These roles refer to FFTA Soldier/Gladiator, not FFVII SOLDIER or FFXIV's shield-bearing Gladiator. [Original FFTA ability reference][ffta]. Tomahawk, Overpower, and Fell Cleave borrow actual FFXIV axe techniques, with their tactical adaptations explicitly listed; they do not import MMO threat or gauge systems. [Official Warrior guide][axe14].

## Weapon and command rules

Define a real, separate **two-handed Axe family**: ordinary range 1, no shield or second weapon, no inherent armor bypass or random damage. Soldier and Gladiator gain equip permission; the revised Viking also uses this family. Warrior and other jobs do not automatically gain access. Teaching permission remains job-specific even when equipment can be shared.

All eight actions require a primary axe, and the two reactions retain their stated axe requirement. Recuperation and Follow Through are transferable supports with no weapon requirement. Keep them inside Soldier **Battle Tech** and Gladiator **Spellblade Tech**, not a third equipped command. Physical effects use P/A from the main specification, work while Silenced, and cannot be Reflected, Returned, or Doublecast. One primary-weapon hit per target, no critical, proc, or second weapon. No action consumes the axe. Mastered actions count toward existing owning-job unlock gates; supports and reactions do not.

**Frontal arc:** choose a cardinal facing; hit the tile directly ahead plus its two diagonal neighbors, within 2 height. Allies can be hit; caster cannot. Preview all tiles. Tomahawk uses the shared ranged projectile rules. The earlier unexplained two-tile Hooking Blow pull is removed.

## Soldier — Human

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| SLD-AX-A1 Chop | 100 | 0 MP | r1, one enemy; A | 1.05P. Basic weapon-elemental strike. | Original extension: Original straightforward addition to Soldier's martial toolkit. [Source][ffta] |
| SLD-AX-A2 Tomahawk | 150 | 4 MP | r3, one enemy; A | 0.70P weapon-elemental thrown-axe strike. Requires clear line of sight. Does not consume or unequip the axe and does not pull the target. | Adaptation: Marauder ranged axe attack; no MMO enmity. [Source][axe14] |
| SLD-AX-A3 Overpower | 200 | 6 MP | Frontal arc, any units; A | 0.75P weapon-elemental per target. Our directional area and friendly fire adapt the axe area-attack concept. No enmity system. | Adaptation: Marauder area axe attack. [Source][axe14] |
| SLD-AX-A4 Shatter Guard | 300 | 8 MP | r1, one enemy; A | 0.85P weapon-elemental; after positive damage remove Protect only. No item destruction or permanent Defense loss. | Original extension: Original guard-breaking extension of Soldier's weakening techniques. [Source][ffta] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| SLD-AX-S1 Recuperation | Support | 200 | Direct HP healing received ×1.25 from any eligible restorative source, including medicine and allied or self healing. Round down after combining modifiers and cap at missing HP. Does not improve revival HP, drain, regeneration ticks, or MP recovery. No axe, weapon, or command requirement. | Cross-job support design: Frontline recovery training, useful to any unit taking sustained damage. [Inspiration][ffta] |
| SLD-AX-R1 Haft Guard | Reaction | 250 | Requires axe. 25% pre-hit activation: enemy physical HP damage ×0.75 for that action. | Original extension: Original mundane defense using the axe haft. [Source][ffta] |

## Gladiator — Bangaa

| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |
|---|---:|---|---|---|---|
| GLD-AX-A1 Armor Splitter | 200 | 8 MP | r1, one enemy; A | 1.00P weapon-elemental using 75% of target effective Weapon Defense for this hit. No lasting debuff or destroyed armor. | Original extension: Original heavy-weapon penetration added to Gladiator's offensive kit. [Source][ffta] |
| GLD-AX-A2 Reaping Arc | 250 | 12 MP | Frontal arc, any units; A | 0.95P weapon-elemental per target. A directional alternative to existing Wild Swing, not a claim that Gladiator lacked area attacks. | Original extension: Original positional variant alongside Wild Swing. [Source][ffta] |
| GLD-AX-A3 Executioner | 300 | 12 MP | r1, one enemy; A | 1.20P weapon-elemental; 1.60P if target is at or below 35% max HP at execution. No instant KO. | Original extension: Original arena finisher; no claim of a canonical FFTA move. [Source][ffta] |
| GLD-AX-A4 Fell Cleave | 400 | 16 MP | r1, one enemy; A | 1.80P weapon-elemental. Apply Exposed before the hit, even on a miss: physical HP damage received ×1.20 until start of next user turn. | Adaptation: Warrior heavy axe strike; MP and Exposed replace MMO resources. [Source][axe14] |

| ID / passive | Type | AP | Effect while equipped | Lineage |
|---|---|---:|---|---|
| GLD-AX-S1 Follow Through | Support | 350 | During your own turn, direct physical HP damage dealt ×1.15 if you voluntarily moved at least one tile before the action begins. Applies to every weapon and physical command. Extra distance gives no additional bonus; forced displacement and later movement do not qualify. No magic, item, reaction, or damage-over-time bonus. | Cross-job support design: Carry movement into an attack; transferable offensive momentum. [Inspiration][ffta] |
| GLD-AX-R1 Axe Reprisal | Reaction | 350 | Requires axe. After surviving adjacent enemy physical HP damage, 30% activation: counter once for 0.70P, A accuracy. No proc or critical. | Original extension: Original axe counter; compare with existing Strikeback rather than claiming a new role. [Source][ffta] |


Exposed is a new harmful modifier ending at the start of the user's next turn, including immediate retaliation before then. It does not stack. KO, Petrify, battle end, or a broad remedy clears it; the action cannot be selected if immunity would cancel its drawback at application. Protect can mitigate the risk through the usual rules. This drawback is our balance addition to Fell Cleave, not a claim about FFXIV.

**Existing-kit check:** Gladiator already has Rush, Wild Swing, Beatdown, and elemental techniques. Reaping Arc changes positioning rather than inventing the job's first area attack; Fell Cleave offers a cost/risk profile rather than presenting heavy damage as a missing identity. Axe Reprisal must be compared with existing Strikeback. Shatter Guard fits Soldier's weakening role; it is an original Protect-breaking move, not the equipment-destroying ability Armor Break. [Original FFTA abilities][ffta].

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

Release the first pair in initial shops, then subsequent pairs at ordinary shop expansions, all before the final story stretch and repeatably obtainable. Actual flags need mapping. Viking has eight separate teaching axes in the main specification; sharing the weapon family grants no cross-job lesson access.

## Implementation boundary

Twelve reviewed additions plus the eight-job lesson sets make 116 ability entries and 72 teaching items. Counts are not proof of record capacity. Verify new weapon type, handedness, equip menus, sorting, icons, animations across Human Soldier/Bangaa Gladiator/Bangaa Viking, AP ownership, mastery storage, shops, and law checks. Keep existing weapon categories intact. [Original item layout](https://datacrystal.tcrf.net/wiki/Final_Fantasy_Tactics_Advance/Items).

There is no new combo in this addendum. Adapt existing Soldier/Gladiator combo weapon acceptance and animation without changing JP or damage behavior. Test every old skill with axes and preserve its original weapon-independent or weapon-dependent rules. Compare old and new options at matched equipment tiers before claiming balance. No ROM has been changed.

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
