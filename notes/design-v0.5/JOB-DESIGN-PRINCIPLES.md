# FFTA expansion: job identity and gameplay

Design direction 0.5 — adopted council balance pass — September 14, 2026

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
| Dark Knight | Dangerous power fueled by sacrifice and recovery through draining | Tune HP costs and recovery together. Give its risk a visible offensive payoff; sustainable HP-positive actions are allowed when paid for in turns and resources; automatic or unpaid recovery loops are not. |
| Viking | Sturdy axe raider, plunder, storm and sea power | Combine martial pressure with storm utility. A wave can work on dry ground and improve near water. Three lightning tiers are not mandatory. |
| Geomancer | Attunement to the landscape and control through natural forces | Useful nature arts everywhere; nearby terrain changes their payoff. Include mobility, protection, and a persistent field rather than only elemental damage with a small status chance. |
| Chemist | Practical medicine, mixtures, thrown supplies, emergency treatment | Invent coherent preparations and recipes when they add choices. Sources need not contain the exact recipe. Stock consumption and clear effects matter more than copying the ordinary Item list. |
| Bard | Inspiring, sustaining, and coordinating allies through music | Invent songs, combine effects, or change targeting to reward party coordination. Source-game randomness and weak resource recovery are optional. |
| Dancer | Expressive movement, rhythm, disruption, and draining vitality | Movement-sensitive techniques and useful debuffs can create openings. Dances can be redesigned around FFTA turns without copying map-wide pulses or random selection. |
| Mystic Knight | Deliberate weapon enchantment and martial magic | Enchantments, attacks, or thematic finishers may be combined if setup is worthwhile. Persistent Spellblade is a current choice, not the only faithful implementation. |
| Soldier / Gladiator | Practical frontline technique / forceful arena offense | Axes should add useful choices to their existing kits. Original moves are welcome; neither class needs to inherit a different game's full Warrior kit. |

## Adopted council balance pass

The user approved the reconciled [council proposal](BALANCE-COUNCIL.md). Version 0.5 makes its 116 reviewed entries, shared rules, AP values, and teaching changes the current design. The reports remain evidence; the class/axe specifications and structured ability data now own the current rules.

Mystic Knight can enchant and strike in one action, retaining the enchantment for later primary Fight attacks. Dark Knight gains useful recovery and commitment attacks; its sacrifice costs and thresholds remain meaningful. Samurai retains Centered, and Geomancer retains terrain-independent arts with optional affinity and group Updraft. Viking's middle thunder tier becomes a focused storm-control action, and its theft uses original transactions.

Chemist consolidates ordinary medicine and gains two priced preparations. Bard's active songs work by voice on other legal Moogle jobs and offer dependable party benefits. Dancer gains scaling performance damage and deliberate control. Most reactions become reliable when their conditions are met, with explicit per-entry limits rather than a blanket turn lock. Supports remain useful beyond their teaching jobs.

Keep the council's combined-effect decisions: Desperation is 50% extra eligible damage at 35% HP or below; Spell Parry consumes an enchantment for 50% physical reduction, not immunity; Encouragement excludes immediate turn grants and receives no outgoing-healing multiplier; advanced revival restores 50% max HP without the rejected 200-HP cap. Spellweave's Magic category does not turn an enchanted strike's physical damage into magic.

The ten growth/chassis profiles stay the comparison baseline. Test ordinary progression and optimized inherited growth separately; do not compensate for weak action design by inflating every stat. AP totals vary by job, while all 116 lesson IDs and 72 teaching-item positions remain. Values are adopted design targets, not gameplay-tested guarantees.

## What remains fixed

Our vanilla-USA base, eight-job roster, racial distribution, current progression decisions, Chemist starter access, and Soldier/Gladiator axe expansion remain the scope. Squire and Sentinel are rejected; Green Mage remains unapproved. The new techniques and balance targets are design work, not an applied ROM patch.## Adopted council balance pass

The user approved the reconciled [council proposal](BALANCE-COUNCIL.md). Version 0.5 makes its 116 reviewed entries, shared rules, AP values, and teaching changes the current design. The reports remain evidence; the class/axe specifications and structured ability data now own the current rules.

Mystic Knight can enchant and strike in one action, retaining the enchantment for later primary Fight attacks. Dark Knight gains useful recovery and commitment attacks; its sacrifice costs and thresholds remain meaningful. Samurai retains Centered, and Geomancer retains terrain-independent arts with optional affinity and group Updraft. Viking's middle thunder tier becomes a focused storm-control action, and its theft uses original transactions.

Chemist consolidates ordinary medicine and gains two priced preparations. Bard's active songs work by voice on other legal Moogle jobs and offer dependable party benefits. Dancer gains scaling performance damage and deliberate control. Most reactions become reliable when their conditions are met, with explicit per-entry limits rather than a blanket turn lock. Supports remain useful beyond their teaching jobs.

Keep the council's combined-effect decisions: Desperation is 50% extra eligible damage at 35% HP or below; Spell Parry consumes an enchantment for 50% physical reduction, not immunity; Encouragement excludes immediate turn grants and receives no outgoing-healing multiplier; advanced revival restores 50% max HP without the rejected 200-HP cap. Spellweave's Magic category does not turn an enchanted strike's physical damage into magic.

The ten growth/chassis profiles stay the comparison baseline. Test ordinary progression and optimized inherited growth separately; do not compensate for weak action design by inflating every stat. AP totals vary by job, while all 116 lesson IDs and 72 teaching-item positions remain. Values are adopted design targets, not gameplay-tested guarantees.

## What remains fixed

Our vanilla-USA base, eight-job roster, racial distribution, current progression decisions, Chemist starter access, and Soldier/Gladiator axe expansion remain the scope. Squire and Sentinel are rejected; Green Mage remains unapproved. The new techniques and balance targets are design work, not an applied ROM patch.
