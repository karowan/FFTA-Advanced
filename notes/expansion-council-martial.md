# Expansion council: martial jobs

> Historical review of 0.6. The user subsequently approved all seven candidates as 0.7; [the adopted council record](../ABILITY-EXPANSION-COUNCIL.md) and current specification supersede the proposal-status wording below.


September 14, 2026. Independent proposal review against design 0.6; nothing in this report is adopted. Existing roster, racial access, gates, growths, equipment and supports/reactions remain unchanged. Numerical targets below are provisional, not ROM-tested mechanics.

## Recommendation

Recommend three additional actions across this group: **Higanbana for Samurai, The Blackest Night for Dark Knight, and Provoke for Viking.** They respectively introduce sustained damage, spending one's life to protect another, and a deliberate enemy-targeting dilemma. Soldier and Gladiator need no additional axe actions at this stage. Their four new actions already sit on top of complete vanilla commands.

| Rank | Job | Recommended addition | Proposed action count |
|---|---|---|---|
| 1 | Dark Knight, Human and Bangaa | The Blackest Night: spend HP to ward an ally | 8 → 9, same lesson for both races |
| 2 | Samurai, Human | Higanbana: persistent blade wound | 8 → 9 |
| 3 | Viking, Bangaa | Provoke: weaken an enemy's damage to everyone except the challenger | 8 → 9 |
| — | Soldier, Human | None | Retain all vanilla actions plus four axe additions |
| — | Gladiator, Bangaa | None | Retain all vanilla actions plus four axe additions |

The first two have the clearest new decisions. Provoke is a good identity addition but requires validating the custom target relationship and enemy evaluation; do not quietly substitute Berserk if that proves difficult.

## Dark Knight: The Blackest Night

**Proposal:** 10 MP + 10% maximum HP; r3 one living ally, self allowed; Sure; weapon-free. Grant a visible ward that halves direct physical/magical HP damage from the next successful enemy action, then expires. It covers every eligible component of that one action. It otherwise expires at the start of the caster's next turn. Misses, zero-damage actions, items, HP costs, damage over time, and status-only actions do not consume it. No prevention of statuses, instant KO, or Petrify. Only one ward of this name per recipient; recasting replaces rather than stacks. Dispel/KO/Petrify/job-change/battle-end remove it. No healing, resource refund, retaliation, or extra action is attached.

**Lineage:** FFXIV's The Blackest Night creates a barrier on self or another party member and rewards full absorption. Our HP sacrifice, single-action reduction, duration, and omission of the refund are an adaptation, not copied source mechanics. [Official FFXIV Dark Knight guide](https://na.finalfantasyxiv.com/jobguide/darkknight/).

**Ordinary turn:** A Bangaa Dark Knight can deal damage now or pay 20 HP and 10 MP at 200 maximum HP to help a nearby wounded caster survive the next enemy hit. If the enemy attacks somebody else, the ward may expire unused. Unlike Dark Mind, this protects another unit and handles physical attacks; unlike healing, it cannot repair existing damage.

**Mixing and limits:** Human Paladin/Dark Arts can use the ward while retaining its native Paladin command; it does not also equip White Magic or gain a third learned command. Bangaa Viking/Dark Arts can use it with an axe because it is weapon-free, but still cannot use sword-gated drains. Dark Knight/Blue Magic and Dark Knight/Prayer gain a protective choice without changing their existing weapon permissions. Bloodcasting changes the example cost to 40 HP total, not 20; Desperation supplies no multiplier to a ward. A self-ward can help sustain a low-HP build, but the ward itself has no attack attached, spends another 10% maximum HP, and cannot make sacrifice costs safe for free.

**Stacking:** Other legitimate reductions may multiply once: ward plus Poise gives 0.50 × 0.75 = 0.375 incoming damage for one enemy action. That is strong, but uses another unit's action or the beneficiary's own previous action and is not immunity. Damage > MP needs explicit ordering at implementation: ward reduces only damage that remains payable to HP after an applicable resource-redirection reaction; an entirely MP-paid action does not consume it. Do not let it reduce MP loss. Consumption readiness must be evaluated once after redirection; other defensive modifiers then apply together without double counting.

**Counterplay/overlap:** Attack another ally, bait with a smaller hit, Dispel, apply statuses, or outlast the short window. Permanent emergency survival, Auto-Life, and broad healing remain separate roles. If implementation cannot clearly preview the ward alongside vanilla redirection, defer the candidate rather than claiming this rule already works in the engine.

**Rejected additions:** Another area drain duplicates Sanguine Sword plus the existing area-sacrifice decision; an immortal Living Dead-style action adds a much larger survival system and can erase Desperation's intended risk. Another self-heal/defense button would overlap Dark Mind. Salted Earth would overlap the new Geomancer field specialty without filling as clear a Dark Knight gap.

## Samurai: Higanbana

**Proposal:** 8 MP; katana; r1 enemy; A; 0.80P non-elemental physical damage. Positive HP damage applies a removable **Blade Wound** with two pulses, one at the end of each of the target's next two turns. Each pulse is 0.50 times the snapshotted P reference, excluding outgoing damage bonuses. No second S roll, but custom ailment immunity blocks the wound. The initial strike still works against immune enemies. Pulses are damage over time, not physical attack events: no reactions, drain, Spellweave, criticals, weapon procs or outgoing support/buff amplification. One wound per target; a new one replaces rather than stacks. Broad remedies cure it; KO/Petrify/battle end clear it. This is a new custom ailment, not renamed vanilla Poison.

The snapshot uses the current target's physical defenses, including applicable Protect, when the sword lands; later defense changes do not recalculate it. Centered, Composure, Desperation and other applicable outgoing bonuses affect the immediate strike only, not the stored P reference or subsequent pulses. Centered is consumed normally at execution, including a miss. The voluntary action sequences Physical; the later pulses establish no action category. No new source-job support is required.

**Lineage:** FFXIV Higanbana is a Samurai Iaijutsu attack with a damage-over-time component. Our katana gating, FFTA turns, wound status, powers and cleansing rules are adaptations. [Official FFXIV Samurai guide](https://na.finalfantasyxiv.com/jobguide/samurai/).

**Ordinary turn:** Against an enemy with a 40-damage P reference, an unboosted Higanbana deals 32 now and 20 at each of its next two turn ends, totaling 72 if uncleansed. Kiku-ichimonji deals 58 immediately from up to four tiles for 10 MP. Higanbana earns its place only when the target will live long enough; Kiku remains the better immediate finishing and ranged action. This is a comparison of proposed formulas, not a measured fight.

**Mixing and limits:** Ninja/Iaido can apply a wound with a katana, then use original Ninja tools on a later turn; Double Sword only improves ordinary Fight and does not double the wound. Samurai/Hunt can keep pressure on a durable opponent while directing later actions elsewhere, subject to individual Hunt equipment gates. Samurai/White Magic can spend later turns on recovery while the wound continues. Concentrate improves landing reliability; Composure improves the initial hit only. No Human can equip Viera-only Spellweave, and none of these combinations gains Dancer's support lessons.

**Counterplay/overlap:** Cure the wound, prevent the initial hit, or use ailment immunity. Short fights favor direct damage. The wound should not stack with copies from other Samurai, and artificial extra-turn effects cannot be used to manufacture indefinite pulses: it owns exactly two. Haste shortens the time available to cure it by bringing target turns earlier, but does not create extra pulses. Test enemy-wait/end-turn semantics and multi-Samurai replacement explicitly.

**Why not more Samurai actions now:** The existing list already has reach, line damage, group healing, group Protect/Shell, guarded damage and a sustaining area finisher. A new Third Eye overlaps Guarding Draw and Blade Ward; another stronger single strike merely competes numerically with Kiku-ichimonji. Tsubame-gaeshi-style repeat actions risk duplicating a finisher or effectively introducing extra actions. Masamune as area Haste would buy a powerful role at the cost of collapsing distinct support niches. A purification spirit is thematically plausible but less necessary while White Magic is a legal secondary option.

## Viking: Provoke

**Proposal:** 6 MP; r3 enemy; S; weapon-free and usable while Silenced. Apply **Challenged** until the end of that target's next turn. Its direct physical/magical HP damage to recipients other than the provoking unit is multiplied by 0.70. Damage to the provoking unit is unchanged. This is a soft taunt: the enemy retains movement, target selection, and its whole legal command list. No Berserk, forced Fight, automatic attack, added turn, self-guard, or defense reduction. Fixed/percentage damage, status chances, items, costs, damage over time, and reactions are unaffected. For area damage, evaluate the recipient condition separately. One challenger per target; newer successful application replaces the old one. Cure through broad remedies; end on either party's KO/Petrify, caster job change, or battle end.

**Lineage:** Provoke is a documented FFIII Viking ability. Square Enix's support page itself addresses that command. Our damage penalty for ignoring the challenger is an original tactical adaptation, not FFIII's targeting mechanism. [Square Enix FFIII Provoke support](https://support.na.square-enix.com/faqarticle.php?c=0&id=5141&kid=63557&la=1&page=3&pv=10&ret=faq&sc=0&so=0).

**Ordinary turn:** Before a threatening enemy's turn, challenge it so that a hit against the Viking retains full damage while a hit against the exposed healer is reduced. The modifier functions regardless of the vanilla AI's choice; there is no guarantee the AI will strategically favor the challenger until its evaluation is tested or adapted. This competes with Stormcall's damage plus Slow: Provoke has only one status check and costs less, but supplies no damage and does not stop the enemy from acting. When immediate killing is possible, an attack remains better.

**Mixing and limits:** Viking/Gladiator with Axe Reprisal can invite adjacent physical attacks; the enemy can instead cast, move away, or accept the penalty. Templar/Reaving can use the weapon-free taunt while retaining legal Templar arms, without gaining axe theft. Viking/Bishop can protect a party without another new class. Bangaa Opportunist recognizes Challenged as a custom harmful status, but Provoke itself deals no damage and cannot self-qualify a hit. Weapon Atk+ and Opportunist still compete for one support slot. The mark survives ordinary movement; it is brief enough that this does not become indefinite long-range suppression.

**Counterplay/overlap:** Status immunity/resistance, cleanse, attacks on the challenger, non-HP control, and the one-target/one-turn duration all remain relevant. Combine Provoke with Protect or a Dancer reduction only through separate units' actions; each independently applicable modifier multiplies once. Avoid stacking marks from multiple Vikings to create contradictory obligations. UI must identify the challenger and show per-recipient reduced damage. The enemy AI should account for the penalty, but the mechanic does not require lying about a forced target if AI evaluation remains vanilla.

**Conditional alternate, not an additional recommended slot:** A mundane grappling-hook attack could pull a target one tile toward the Viking, providing a melee setup opposite Tsunami's push. It is an original raider extension, not a canonical named Viking move. Rank it below Provoke because Tsunami already offers displacement and a hook adds equipment-fiction questions to an axe-and-storm job. Do not add both simply to reach ten actions.

**Rejected additions:** A fourth lightning damage spell, more theft categories by default, automatic theft of every enemy slot, or an axe strike that also delivers full magic damage. Existing two independent theft transactions already broaden this race and require balancing; further inventory extraction should wait for that playtest.

## Soldier and Gladiator: no further additions recommended

Soldier already gets a free dependable axe hit, ranged Tomahawk, frontal area damage and Protect removal, alongside original weakening techniques. Another defensive posture overlaps Haft Guard and the incoming-healing support; another armor break overlaps the original Soldier identity and the approved Shatter Guard. Keep four new axe actions.

Gladiator already gets armor penetration, a controlled arc, a wounded-target finisher and a high-damage exposed strike, alongside original Rush, Wild Swing, Beatdown and elemental skills. Another self-buff overlaps Last Resort through legal axe Gladiator/Dark Arts; another area strike overlaps Reaping Arc/Wild Swing. Keep four new axe actions. Viking/Gladiator already has the largest combined martial breadth in this racial branch without needing more lessons.

The official Warrior guide supplies further axe-related sustain/protection precedents such as Raw Intuition and Nascent Flash, but availability of precedent does not establish need. Importing them here would crowd existing Dark Knight, Chemist, and proposed ward roles. [Official FFXIV Warrior guide](https://na.finalfantasyxiv.com/jobguide/warrior/).

## Implementation and acquisition notes

These three proposals would add three action records, not new supports/reactions or racial jobs. Do not edit canonical totals or AP/shop data until user adoption. Suggested mastery band: 250–350 AP each; place Higanbana around Kiku progression, The Blackest Night around Last Resort/Crushing Blow, and Provoke early-to-middle alongside War Cry. Reuse teaching-item power tiers or add parallel sidegrades rather than raising weapon ceilings. Preserve all original vanilla moves. Verify more-than-eight mastery storage, command UI, AI preview, laws, custom status cleanup and all event timings before gameplay claims.

No candidate is intended to compete with optimized vanilla builds by unlimited extra actions, universal accuracy, or free resource loops. The objective is to add a reason to choose a different ordinary action while preserving useful secondary-command choices.

## Cross-review: Dancer attack with a finishing step

A bounded post-strike step could create a useful Dancer decision, but it needs an explicit exception to the current shared prohibition on immediate action-granted movement. Recommend consuming the user's remaining ordinary movement budget, with a small per-technique cap, rather than granting a fresh movement allowance. The initial attack must work when no movement remains. Preview the optional destination and its actual terrain cost; respect Immobilize, occupancy, elevation, hazards and laws. A miss should not restore spent movement or permit another action.

If the intended mechanic permits movement before and after the attack, document that split explicitly: unused points from a pre-attack Move are retained only for this finishing step, not a new full Move. Do not retroactively qualify movement-sensitive damage on the preceding attack using the finishing step. The movement consumes budget even if an allied buff increased it; no copy/reflection/reaction/Doublecast can spawn a second step. This is a candidate mechanic, not approved engine behavior. It should be compared with ordinary Act-then-Move, which is already available; otherwise the new ability risks spending an action slot on an animation of something the player can already do.
