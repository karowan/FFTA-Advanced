# FFTA job expansion: roster and progression

Status: adopted design 0.7, not installed or implemented. **Confirmed scope: our additions on top of the original US FFTA, with no existing overhaul or mod pack.** The complete job specification is now in [JOB-CLASS-SPECIFICATION.md](JOB-CLASS-SPECIFICATION.md); that document takes precedence where it refines this progression overview.

The [version 0.7 design principles](JOB-DESIGN-PRINCIPLES.md) prioritize each job's spirit and useful FFTA gameplay. The [inspiration register](JOB-THEME-AUDIT.md) covers all 129 entries without requiring copied abilities. Source-game mechanics and balance are not binding.

## Coverage

Every original playable race receives exactly two additional job options in the current eight-job roster: six exclusive jobs and two shared jobs. In addition, the existing Human Soldier and Bangaa Gladiator receive an axe skill/equipment expansion, specified in [AXE-SKILL-EXPANSION.md](AXE-SKILL-EXPANSION.md). No additional Human/Bangaa starter jobs are being added. Existing jobs remain available; technical capacity for the expansion has not yet been established.

| Race | Addition 1 | Addition 2 |
|---|---|---|
| Human | Samurai — exclusive | Dark Knight — shared with Bangaa |
| Bangaa | Viking — exclusive | Dark Knight — shared with Human |
| Nu Mou | Geomancer — exclusive | Chemist — shared with Moogle |
| Moogle | Bard — exclusive | Chemist — shared with Nu Mou |
| Viera | Dancer — exclusive | Mystic Knight — exclusive |

All 18 adopted supports now work beyond their teaching jobs; see [support skills and example builds](SUPPORT-SKILL-DESIGN.md). This preserves racial access and one support slot while removing job-set and signature-weapon dependencies.

## Current unlock requirements

All numbers below count permanently learned action abilities, or A-abilities, in the named job. They are not character levels, job levels, or support/reaction abilities. A character must personally meet every prerequisite joined by a plus sign; the requirements cannot be divided between clan members. Merely equipping an item that grants access to an unmastered ability does not count.

The requirements for the eight new jobs are our proposed balance values. Existing-job prerequisites in the next section follow the original game.

| Race | New job | Proposed requirement | Intended availability |
|---|---|---|---|
| Human | Samurai | Fighter 2 + Ninja 1 | Midgame |
| Human | Dark Knight | Paladin 2 + Black Mage 2 | Midgame |
| Bangaa | Viking | Warrior 3 + White Monk 1 | Early |
| Bangaa | Dark Knight | Gladiator 2 + Bishop 1 | Midgame |
| Nu Mou | Chemist | None | Starter |
| Nu Mou | Geomancer | Sage 2 + Black Mage 3 | Midgame |
| Moogle | Chemist | None | Starter |
| Moogle | Bard | Animist 2 + Juggler 2 | Midgame |
| Viera | Dancer | Fencer 2 + White Mage 2 | Early |
| Viera | Mystic Knight | Red Mage 2 + Elementalist 2 | Midgame |

Availability is a design target, not a guarantee: AP costs and the timing of ability-bearing equipment determine the actual pace. Each unlock route needs sufficient obtainable equipment before the intended point in the story.

## Full progression paths

Each arrow names what unlocks the destination. Separate branches must be completed by the same character before meeting the final requirement above.

- **Human / Samurai:** Soldier --learn 2 Soldier actions--> Fighter; Thief --learn 2 Thief actions--> Ninja. Then learn 2 Fighter actions and 1 Ninja action to unlock Samurai.
- **Human / Dark Knight:** Soldier --learn 2 Soldier actions--> Paladin. Then learn 2 Paladin actions and 2 Black Mage actions to unlock Dark Knight. Black Mage is available from the start.
- **Bangaa / Viking:** Warrior and White Monk are both starting jobs. Learn 3 Warrior actions and 1 White Monk action to unlock Viking.
- **Bangaa / Dark Knight:** Warrior --learn 2 Warrior actions--> Gladiator; White Monk --learn 2 White Monk actions--> Bishop. Then learn 2 Gladiator actions and 1 Bishop action to unlock Dark Knight.
- **Nu Mou / Chemist:** No job prerequisite; available at the first normal opportunity to change jobs. Abilities still require teaching equipment and AP.
- **Nu Mou / Geomancer:** Learn 2 Beastmaster actions and 3 White Mage actions to unlock Sage. Then learn 2 Sage actions and 3 Black Mage actions to unlock Geomancer.
- **Moogle / Chemist:** No job prerequisite; available at the first normal opportunity to change jobs. Abilities still require teaching equipment and AP. White Mage is not a Moogle job in vanilla FFTA.
- **Moogle / Bard:** Thief --learn 2 Thief actions--> Juggler. Then learn 2 Juggler actions and 2 Animist actions to unlock Bard. Animist is a starting job.
- **Viera / Dancer:** Fencer and White Mage are starting jobs. Learn 2 Fencer actions and 2 White Mage actions to unlock Dancer.
- **Viera / Mystic Knight:** Learn 1 Fencer action to unlock Red Mage; learn 1 Fencer action and 1 White Mage action to unlock Elementalist. Then learn 2 Red Mage actions and 2 Elementalist actions to unlock Mystic Knight. The same learned Fencer action satisfies both earlier unlocks.

## What each job contributes

These are the adopted roles, including Spellblade and all seven further council additions. The class specification supplies exact rules; no ROM implementation is claimed.

| Job | Intended contribution | Distinction from existing jobs |
|---|---|---|
| Samurai | Katana mastery, composure, and blade spirits | Useful attacks build Centered for stronger follow-ups; sword development supports its offense |
| Dark Knight | Spend HP for pressure; recover through capped drain and paid healing | Useful attack-and-buff commitment; sustainable actions are allowed, but automatic/unpaid recovery is not |
| Viking | Axe plunder, differentiated storms, and ailment resilience | Independent original theft transactions; precise Thunder, focused Stormcall, area Thundaga, and dry-ground Tsunami displacement |
| Geomancer | Nature damage, battlefield control, allied mobility and protection | Every skill works on ordinary terrain; nearby affinity improves its effect; Rime Field influences movement |
| Chemist | Ranged medicine, grouped remedies/tonics, two-ingredient healing and revival | Mixtures justify the command beside ordinary Item plus Long Throw; actual ingredient supply and no MP cost |
| Bard | Voice-based party offense/protection, healing, MP recovery, and Requiem | Songs transfer as a secondary; Nameless Song deterministically applies Protect, Shell, and Regen |
| Dancer | Scaling performance damage, deliberate debuffs, vitality drain, Sword Dance | Weapon-free dances remain useful on other Viera jobs; Sword Dance retains a knife/rapier gate |
| Mystic Knight | Fourteen actions: sustained enchantments, dispel, ranged release, and a paid Petrify technique | Magic sequencing stays separate from physical damage; Spell Parry and Arcane Release compete for the maintained enchantment |

Shared jobs should have the same core action list where possible. Chemist is a starter for both races. Dark Knight has different prerequisite routes because the two races have different existing jobs; its final gate totals three learned advanced actions for Bangaa versus two advanced plus two basic actions for Human. These are not assumed equally costly until AP and equipment access are evaluated. Any racial growth differences must be tuned and documented rather than assumed to happen automatically.

The user rejected making Samurai, Viking, and Dancer starters, and rejected Squire, Sentinel, and the Sentinel-to-Viking branch. Chemist is the accepted new starter for both eligible races; Green Mage remains a candidate. The Human/Bangaa direction is new axe skills for Soldier and Gladiator. See [the starter research](STARTER-JOB-INSPIRATION.md) and [the axe specification](AXE-SKILL-EXPANSION.md). Other job prerequisites remain the current draft.

## Implementation boundaries and acceptance criteria

- Confirm how to add the required race/job records, menus, sprites, animations, ability lists, and equipment without removing existing jobs. Eight job concepts across ten race/job combinations do not imply only eight internal records or eight sprite sets.
- Check that prerequisite evaluation supports these counts and job identifiers. Test immediately below and exactly at every unlock threshold, including the shared jobs on both races.
- Preserve the selected AP/equipment learning and the current per-job AP totals. No JP-purchasing system is introduced.
- Give every new job obtainable early equipment and at least one useful initial action. Unlocking a job must not leave it unusable until a rare late reward.
- Test each new job with existing secondary command sets and strong supports/reactions. In particular, check Mystic Knight with Red Mage abilities and Dark Knight with healing or multi-hit options.
- Validate terrain checks, HP costs, consumable behavior, and temporary enchantments before promising their exact form. Simplified effects may be appropriate for the first playable prototype.
- Test ordinary saving and loading, job switching, equipment, shops, recruitment, dispatches, and battle animations with the final data layout.

## References

- Original FFTA unlock routes: [Thonky job reference](https://www.thonky.com/tactics-advance/jobs), consulted September 13, 2026. Its Moogle list incorrectly includes White Mage and omits Gunner. Cross-check racial availability against [Terence's mechanics research](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262) and [EraDktor's weapon/job reference](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/29777). The incorrect Moogle White Mage prerequisite in our initial draft has been corrected to Animist.
- Background research and tool limitations: [FFTA modding guide](../../FFTA-MODDING-GUIDE.md).
- The roster, race assignments, numerical gates for new jobs, and adaptations in this document are original proposals for this project.

## Adopted command breadth (0.7)

Samurai: 9 actions with Higanbana; Dark Knight: 9 with The Blackest Night; Viking: 9 with Provoke; Geomancer: 9 with Nature's Refuge; Chemist: 10 with Inoculation and Guarding Draught; Dancer: 9 with Passing Step; Bard: 8; Mystic Knight: 14. Shared jobs use the same lesson list on both eligible races. Soldier and Gladiator retain four added axe actions each. See [the adopted council record](ABILITY-EXPANSION-COUNCIL.md) for integration and teaching details.
