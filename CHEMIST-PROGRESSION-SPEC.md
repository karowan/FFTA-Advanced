# Chemist progression: Physician and Sapper

Design checkpoint, 2026-09-26. This extends the existing version 0.7 job specification. It is an implementation target, not evidence that either job is installed or tested.

## Shared rules

Both jobs are tier-three progressions from their race's Chemist. Mastered action abilities count for unlocks; supports, reactions and combos do not. Each uses one ordinary action and an MP-funded, Silence-independent command. Neither command interacts with Reflect, Return Magic or Doublecast. They retain normal laws, AP learning, one secondary action set, one support, one reaction and one combo slot. No new ability grants a turn or creates JP.

The [teaching equipment plan](notes/chemist-progression-equipment.json) pairs two lessons per weapon across stages S1–S3. Those weapons are learning sources, not additional command requirements. The stage and shop plan remains provisional until acquisition and economy checks.

Healing targets living, non-undead allies and cannot exceed missing HP. Listed percentages use the recipient's maximum HP and round down before applicable incoming-healing modifiers. Revival uses the existing eligible-KO rule and is not amplified by direct-healing supports. T2 ends after the recipient's second subsequent turn, excluding the application turn. Custom effects clear on KO, Petrify, job change and battle end; beneficial custom effects are dispellable. Reaction or support healing is a separate event and never recursively triggers itself.

## Nu Mou Physician

**Unlock:** 4 mastered Chemist actions and 3 mastered White Mage actions on the same unit. **Equipment:** staffs and maces, appropriate hats and clothing. **Practice:** short-range field medicine using MP, no item cost. It should have better MP and Magic Power than Chemist with lower physical damage. Its mobility is not increased above Nu Mou Chemist.

Provisional level-one base in native HP/MP/physical Attack/Defense/Magic Power/Resistance/Speed order: **32 / 38 / 56 / 68 / 88 / 86 / 96**. Average growth in the same order: **6.4 / 3.8 / 5.8 / 7.0 / 8.8 / 8.6 / 1.1**. Move 4, Jump 2, Evade 45.

| Ability | Cost | Target | Effect |
|---|---:|---|---|
| Suture | 8 MP | r2 one living ally | Heal floor(20% max HP + 25% missing HP). |
| Triage | 10 MP | r3 one living ally | Through the recipient's next two turns, intercept the first enemy action that deals positive direct HP damage. If the recipient survives that action, heal 25% max HP and remove one Cureall-curable ailment newly inflicted by that action. Consume after that one qualifying action. |
| Purge | 12 MP | r3 one living ally | Remove existing Cureall-curable ailments, including the explicit expansion broad-remedy list, then apply Inoculated T2. No cure is credited for merely preventing a later ailment. |
| Aftercare | 12 MP | r3 one living ally | Heal 25% max HP, then apply ordinary native Regen. Regen has its native duration and removal rules rather than a custom short timer. |
| Rescue Team | 24 MP | r2 center/cross | Revive each eligible KO ally in the area at 35% maximum HP. No living-target healing or restoration multiplier. |
| Mass Triage | 18 MP | r2 center/cross | Heal each living ally 25% maximum HP. No flat cap. |
| Trauma Ward | 20 MP | r3 one living ally | Within the recipient's next two turns, reduce the first incoming enemy action's direct HP damage by 40%, then consume. It does not block instant KO, Petrify, statuses or MP loss, and does not guarantee survival. |

**Follow-up Care (support):** After a voluntary action actually removes an existing curable ailment from another ally, heal that recipient 25% maximum HP, once per recipient and action. Prevention, buff refresh, self-cure, revival, reactions and passive cleansing do not qualify. Its healing receives only the recipient's incoming-healing modifier and cannot trigger another Follow-up Care event.

**Emergency Dressing (reaction):** After surviving direct enemy HP damage at or below half maximum HP, if still able to react, heal 20% maximum HP and remove one curable ailment. Once until the start of the unit's next own turn. No item is spent.

**Physician Combo:** staff or mace, normal Judge Point chain and no new rider.

## Moogle Sapper

**Unlock:** 3 mastered Chemist actions and 2 mastered Gadgeteer actions on the same unit. Gadgeteer retains its existing Thief prerequisite. **Equipment:** knives and maces, appropriate hats and clothing; no gun permission. **Movement:** Move 4, Jump 3. More MP and Magic Power than Moogle Chemist, with a small resistance tradeoff. **Munitions:** MP-funded direct and tactical effects, independent of Silence. Direct charges use a magical-power reference and ordinary elemental immunity/absorption rules.

Provisional level-one base in native HP/MP/physical Attack/Defense/Magic Power/Resistance/Speed order: **31 / 32 / 65 / 67 / 80 / 76 / 106**. Average growth in the same order: **6.2 / 3.2 / 6.4 / 6.8 / 8.0 / 7.6 / 1.5**.

| Ability | Cost | Target | Effect |
|---|---:|---|---|
| Breach Charge | 9 MP | r3 one enemy | Strong Fire damage. Before a successful damaging hit, select either Protect or Shell; ignore and remove only that selected status for this hit. Fire immunity can still negate damage. |
| Flash Charge | 12 MP | r3 center/cross | Light Lightning damage to enemies; each recipient taking positive damage gets an ordinary Blind accuracy check. |
| Concussion Charge | 9 MP | r3 one enemy | Stronger neutral damage, followed by a legal one-tile push after positive damage. No push through occupied or impassable tiles. |
| Tripwire | 8 MP | r3 one empty legal tile | Place a visible one-tile trap. First enemy entry, including forced movement, takes Lightning damage and an ordinary Slow check. One active trap per caster; replacement removes the prior trap. Expires after two caster turns. AI can see and avoid it. |
| Smoke Charge | 12 MP | r3 center/cross | Willing allies receive 25% less direct ranged-attack HP damage for T2. It does not reduce melee damage, statuses, costs or damage over time. |
| Springboard | 8 MP | r2 one other willing ally | Move the ally up to two tiles along a legal path. The caster spends an action; the target gains no turn, Move refill, or movement-law exemption. |
| Timed Fuse | 13 MP | r3 one enemy | Light direct Fire damage. After positive damage, attach a visible fuse. At the end of that carrier's next turn, deal stronger Fire damage in a cross, including allies. Movement, curative removal or carrier KO can counter the fuse. |

**Spotter (support):** If another ally is adjacent to the target at action start, single-target ranged direct attacks gain 10 percentage points to their ordinary attack hit chance and 20% direct HP damage. The accuracy bonus never overrides immunity or applies to status accuracy. Area actions, items, reactions and delayed Fuse explosions do not qualify.

**Duck and Cover (reaction):** Reduce the user's incoming direct HP damage from one enemy area action by 40%. Statuses and other effects still apply. Normal reaction eligibility and action-level interception rules apply.

**Sapper Combo:** knife or mace, normal Judge Point chain and no charge or explosion rider.

## Balance acceptance

These figures are provisional until fixed-level, progression-gated battles compare them with Chemist, Bard, White Mage, Alchemist and Gadgeteer. Measure survival, action economy, MP endurance, turn denial, objective progress and cross-class supports. Verify Triage, Trauma Ward, Emergency Dressing and Duck and Cover against multi-hit actions and competing reactions. Verify no free sustain loops, no unlimited trap/fuse ownership after copy/save transitions, and no AI-targeting advantage from hidden information.
