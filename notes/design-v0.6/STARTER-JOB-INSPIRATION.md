# Starter-job inspiration from other Final Fantasy games

Research and design shortlist — September 13, 2026

## Current decision

Our project remains an expansion of vanilla USA FFTA. Chemist is a no-prerequisite job for Nu Mou and Moogle. **Squire and Sentinel have been rejected, including the Sentinel-to-Viking progression. No additional Human or Bangaa starter class is being proposed.** The selected direction is axe access and new skills for the existing Human Soldier and Bangaa Gladiator; see [AXE-SKILL-EXPANSION.md](AXE-SKILL-EXPANSION.md). The previously planned advanced jobs remain in the roster. Green Mage is still a candidate, not an approved addition.

The candidates below are new proposals. A job can inspire a starting profession even if the source game unlocks it later. Race assignments, sample adaptations, and possible branches are ours, not source-game facts. No patch is applied and no additional job is approved merely by appearing here.

The approved roster's current ability lists are in the [version 0.6 class specification](JOB-CLASS-SPECIFICATION.md), guided by [job identity and gameplay principles](JOB-DESIGN-PRINCIPLES.md). Those lists supersede earlier example mechanics. Viking now shares the new Axe family; no additional starter job or prerequisite follows from that equipment change. Rejected and unapproved candidates below remain research history, outside the current 122-entry design.

## Earlier candidates and current status

### Squire — Human — rejected

**Source identity:** Final Fantasy Tactics uses Squire as a foundational job with basic combat and utility skills. Generic Squire and Ramza's special version are not identical; do not assume every Squire gets Ramza's special speed-boosting abilities. [Job reference](https://finalfantasy.fandom.com/wiki/Squire_(Tactics)).

**Our adaptation:** an apprentice soldier focused on helping the squad: prepare an ally, steady a formation, make a modest ranged distraction, or recover from a small setback. The key difference from FFTA Soldier would be supporting allies rather than centering the same enemy-stat-breaking toolkit.

Example original skill seeds, not a finalized list:

- Rally: modest, temporary offense support for one ally.
- Brace: help an adjacent ally weather the next physical attack.
- Stone Toss: weak ranged harassment, with no guaranteed action interruption.
- Field Drill: a limited positional/support benefit, not permanent stat farming.

**Why it can start:** no magical initiation or mastery theme is necessary; it describes someone learning battlefield fundamentals. It can remain useful as a secondary support set.

**Rejected progression:** Squire is not being added and does not become a Samurai prerequisite.

**Design issue:** if its final list is just Soldier's First Aid and a few weaker attacks, omit it. The ally-support identity must earn the extra class slot. Do not add a mandatory AP multiplier that makes every character train Squire first.

### Sentinel — Bangaa — rejected

**Source identity:** Final Fantasy XIII's Sentinel is a combat role built around reducing damage, guarding, counterattacking, and drawing enemy attention. It is a Paradigm role rather than a tactics-game job tree. [Original manual](https://images-na.ssl-images-amazon.com/images/G/15/electronics/FFXIII-Manual-English._V373561155_.pdf), [role research](https://gamefaqs.gamespot.com/ps3/928790-final-fantasy-xiii/faqs/79486/roles).

**Our adaptation:** a basic shield-bearing guard whose useful actions protect other units. Use vanilla swords and shields rather than assuming a new axe category. Keep Warrior's offensive niche, White Monk's martial/recovery niche, and Defender's later advanced defenses meaningful.

Example original skill seeds:

- Guard Ally: protect a selected nearby ally from a limited amount of incoming damage.
- Shield Bash: a modest close-range attack with a positional effect.
- Brace: improve the guard's own immediate survival.
- Hold Formation: short-range support that rewards staying near the party.

**Why it can start:** guarding a companion is a basic battlefield profession. Its starting kit can be narrow and practical without magical powers or an advanced warrior's finishing moves.

**Rejected progression:** Sentinel is not being added. The proposed Sentinel-to-Viking connection was rejected and must not appear in the current job tree.

**Design issue:** a selfish defense-only class would duplicate Defender and give enemies little reason to engage. Ally protection must be the center. True damage interception, shield-specific attacks, and forced targeting are implementation questions; do not promise the original FFXIII Provoke AI behavior transfers automatically.

### Green Mage — Viera

**Source identity:** FFTA2's Green Mage is a Viera job focused on buffs and ailments. Its repertoire includes protective magic, Blind/Silence/Sleep, accuracy support, and movement/jump support. In that game it has a quest and White Mage prerequisite; making our version a starter is our change. [Job and ability reference](https://finalfantasy.fandom.com/wiki/Green_Mage_(Tactics_A2)).

**Our adaptation:** basic support magic with little direct damage and no full healing/revival toolkit. Teach defenses and simple ailments first; stronger utility belongs later in equipment progression. Use maces from vanilla FFTA rather than adding FFTA2 hammers automatically.

Example adapted skill seeds:

- Protect and Shell: familiar defensive support; existing White Mage keeps these abilities too.
- Blind: a simple offensive support action.
- Leap: temporary movement/jump assistance with strict stacking rules.

**Why it can start:** this is a distinct third branch of basic magic alongside healing and elemental damage. It does not require the fantasy of a master spellsword or accomplished performer.

**Possible progression:** Green Mage can supply a single-job magical foundation for Mystic Knight. Dancer could follow a separate physical/support route rather than forcing both new Viera jobs through the same starter.

**Design issue:** protect its distinction from our Dancer and Bard. Green Mage should emphasize individual wards and magical preparation; Dancer emphasizes mobile disruption; Bard emphasizes musical group support. Avoid importing an unrestricted accuracy buff without checking its interaction with vanilla Assassin abilities.

## Other worthwhile candidates

| Candidate | Source inspiration | Best race fit for our project | Why consider it | Why it is not the default recommendation |
|---|---|---|---|---|
| Lancer | FFXIV's spear/polearm combat class | Human; potentially shared with Bangaa | Reach, thrusts, and formation fighting feel like fundamentals; gives Humans a different weapon identity | Bangaa already have Dragoon. Keep this grounded; no free Jump or dragon magic. Human spear animations/equipment would need work |
| Ranger | FFTA2's Seeq survival/trap job | Human or Viera | Scouting and preparing traps offer a different kind of basic utility | FFTA already has Archer and Hunter; a bow-damage reskin adds little. Actual persistent traps need implementation research |
| Scholar | FFIII's analytical, book-using job; details vary by edition | Nu Mou, possibly shared with Human | Study enemies and help allies exploit information; a believable beginning academic profession | Nu Mou already receive Chemist. Some FFIII versions emphasize enhanced item use, which overlaps it. A mere Scan is weak when the player can already inspect much of a unit's information |
| Marauder | FFXIV's axe-wielding martial class | Bangaa | Direct, physical, understandable raider theme | FFTA has no axe category and Warrior already occupies much of this space; less distinct than a guard focused on allies |

Sources: [official FFXIV Lancer description](https://na.finalfantasyxiv.com/a_realm_reborn/sp/game/classes/war/lancer/), [official Marauder description](https://na.finalfantasyxiv.com/a_realm_reborn/sp/game/classes/war/marauder/), [FFTA2 Ranger](https://finalfantasy.fandom.com/wiki/Ranger_(Tactics_A2)), [FFIII Scholar](https://finalfantasy.fandom.com/wiki/Scholar_(Final_Fantasy_III)). Their listed racial fits are our proposals; FFTA2 Ranger is originally a Seeq job, not a Human/Viera job.

Freelancer/Onion Knight were also considered. They are recognizable foundations in some Final Fantasy versions, but a universal generalist adds less of a new party role here. Importing mastery inheritance or exceptional late-game growth would turn that apparently simple starter into another major system. [FFIII version-dependent job availability](https://finalfantasy.fandom.com/wiki/Final_Fantasy_III_jobs).

## Current foundation direction

| Race | Proposed new no-prerequisite option | Status |
|---|---|---|
| Human | No additional starter job | Expand Soldier with axe skills |
| Bangaa | No additional starter job | Expand Gladiator with axe skills; it retains its existing Warrior prerequisite |
| Nu Mou | Chemist | Accepted starter direction |
| Moogle | Chemist | Accepted starter direction |
| Viera | Green Mage | Candidate |

The current roster remains eight new job concepts, plus the selected skill/equipment expansion for two existing jobs. Choosing Green Mage later would make nine new job concepts. Squire and Sentinel are not counted. Earlier Human/Bangaa alternatives above are research notes, not active proposals.

Other advanced-job requirements remain as documented in the class specification. There is no new starter prerequisite or replacement of the existing Soldier/Warrior unlock branches.
