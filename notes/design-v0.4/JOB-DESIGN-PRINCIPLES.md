# FFTA expansion: job identity and gameplay

Design direction 0.4 — September 14, 2026

**Preserve the spirit of each Final Fantasy job and design its mechanics for FFTA.** The user's clarification supersedes the earlier emphasis on reproducing another game's ability list. Sources provide inspiration and help explain a job's identity; they do not dictate its formula, restrictions, progression, or power level.

The current ability tables are in [the class specification](JOB-CLASS-SPECIFICATION.md) and [the axe addendum](AXE-SKILL-EXPANSION.md). The [lineage register](JOB-THEME-AUDIT.md) distinguishes references from our inventions. A new ability does not need a matching entry in a released game to belong here.

## What makes an ability belong

1. **Express the profession.** Its action, presentation, weapon, and effect should make sense together. A Samurai can focus a blade's spirit into a new technique; a Geomancer can shape the battlefield through natural forces.
2. **Earn the action spent.** Recovery, control, positioning, damage, and preparation all count as useful outcomes. A preparation action must produce enough later value to justify delaying another action. Avoid stacking a setup turn, a rare condition, and a weak payoff on the same move.
3. **Work under ordinary conditions.** A learned job needs useful choices on a normal map and with reasonably available equipment. Favor terrain bonuses over terrain permission checks; a rare affinity should improve an action that is already worth using.
4. **Offer a decision.** Different range, area, resource use, timing, or party interaction should separate moves. Replacing a weak fire attack with a stronger fire attack is less interesting than choosing between breaking a formation and helping an ally cross it.
5. **Support a coherent build.** A job's growths, weapons, actives, and passives should reinforce its intended play. A physical Samurai should not need extensive mage leveling just to make its defining abilities effective.
6. **Make costs buy something.** HP sacrifice should buy meaningful pressure. Inventory consumption should buy reliable support. A reaction or support must compete for its actual FFTA equipment slot. Source-game percentages are not a balance target.
7. **Keep counterplay without making the job helpless.** Immunity can defeat a specific status; it should not erase the entire repertoire. A missed bonus effect should not make an otherwise successful action worthless.
8. **Balance the party, not just the job in isolation.** Consider secondary sets, equipment learning, laws, positioning, and existing powerful options. Strong combinations can be enjoyable; dominance that removes meaningful choices needs adjustment.

**Cross-job supports are a design requirement.** The teaching job supplies the lesson, not a permanent dependency. Most supports should work on multiple other jobs with different commands; our current 18 all meet that scope on paper. Avoid requirements for a specific action set, signature weapon, or exclusive job state. Give each support at least two plausible non-teaching-job uses within legal racial access. [Revised supports and examples](SUPPORT-SKILL-DESIGN.md).

The current eight-action/two-support/two-reaction template is a working size, not a creative requirement. We can merge redundant entries or add a genuinely useful option. Counts and teaching equipment must be updated with any such change. No quota of canonical names is required.

## Identity to retain, mechanics free to change

| Job | Core fantasy | Design freedom and intended contribution |
|---|---|---|
| Samurai | Disciplined katana mastery, composure, decisive draws, blade spirits | Build composure through useful attacks; spend it on a stronger technique or healing spirit. Sword development supports the whole kit. |
| Dark Knight | Dangerous power fueled by sacrifice and recovery through draining | Tune HP costs and recovery together. Give its risk a visible offensive payoff; neither endless self-sustain nor permanent dependence on a rescue turn is the goal. |
| Viking | Sturdy axe raider, plunder, storm and sea power | Combine martial pressure with storm utility. A wave can work on dry ground and improve near water. Three lightning tiers are not mandatory. |
| Geomancer | Attunement to the landscape and control through natural forces | Useful nature arts everywhere; nearby terrain changes their payoff. Include mobility, protection, and a persistent field rather than only elemental damage with a small status chance. |
| Chemist | Practical medicine, mixtures, thrown supplies, emergency treatment | Invent coherent preparations and recipes when they add choices. Sources need not contain the exact recipe. Stock consumption and clear effects matter more than copying the ordinary Item list. |
| Bard | Inspiring, sustaining, and coordinating allies through music | Invent songs, combine effects, or change targeting to reward party coordination. Source-game randomness and weak resource recovery are optional. |
| Dancer | Expressive movement, rhythm, disruption, and draining vitality | Movement-sensitive techniques and useful debuffs can create openings. Dances can be redesigned around FFTA turns without copying map-wide pulses or random selection. |
| Mystic Knight | Deliberate weapon enchantment and martial magic | Enchantments, attacks, or thematic finishers may be combined if setup is worthwhile. Persistent Spellblade is a current choice, not the only faithful implementation. |
| Soldier / Gladiator | Practical frontline technique / forceful arena offense | Axes should add useful choices to their existing kits. Original moves are welcome; neither class needs to inherit a different game's full Warrior kit. |

## Changes made in this revision

Samurai's eight actions now have distinct roles and use sword development for offense. Ashura builds **Centered** while attacking; the next eligible spirit technique can spend it for additional damage or healing. Guarding Draw offers defense while still contributing damage. Its reactions interact with this rhythm. Its supports now benefit broader builds: Composure rewards acting before moving, and Poise recognizes beneficial statuses from any source.

Geomancer's eight actions are available regardless of terrain. Nearby stone, vegetation, water, wood/heat, or ice can improve a relevant action. Its new toolkit includes **Updraft** mobility, **Earthen Ward** protection, **Wisp Flame** to open a target to magic, and **Rime Field** to impede movement. Gaia Surge is usable anywhere, with nearby terrain determining the elements available.

Viking's Tsunami now works on ordinary ground and gains MP depletion near water. This is a deliberate thematic redesign; the original source's restriction is not binding.

The other kits remain provisional designs under these same principles. Their source-inspired entries are not locked; this revision does not claim that every remaining number, reaction, or setup action has already passed balance testing. In particular, review Viking's lightning tiers, Chemist's distinction from ordinary Item, and Bard/Dancer's actual turn value during the next numerical pass.

## What remains fixed

Our vanilla-USA base, eight-job roster, racial distribution, current progression decisions, Chemist starter access, and Soldier/Gladiator axe expansion remain the scope. Squire and Sentinel are rejected; Green Mage remains unapproved. The new techniques and balance targets are design work, not an applied ROM patch.
