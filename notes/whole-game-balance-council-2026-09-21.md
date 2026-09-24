# Whole-game balance council: vanilla plus the expansion

September 21, 2026. **Recommendation for a prototype, not an adopted specification or applied patch.**

## Decision

Make combat less explosive by giving opponents opportunities to respond: bound extra turns and mass control, require preparation for instant removal, and reduce exceptional burst. Preserve reliable ordinary attacks, distinctive jobs, and strong tactical combinations. Do not globally increase HP or reduce all damage.

The user requested online research and a council. Three independent reviewers covered vanilla optimized builds, actual expansion implementation, and pacing/progression/verification. The chair supplied a common proposal for a second cross-review and reconciled the objections below. This document is the resulting recommendation. No gameplay code, ROM, save, release channel, or public repository was changed for this review.

Current baseline was checked against [the handoff](../HANDOFF.md), [release recipe](../scripts/mod-release.json), and [player overview](../MOD-README.md): 0.7-art1-job-visibility, eight new jobs across ten race/job options, 129 added ability entries, and 85 teaching weapons. The earlier [balance council](../BALANCE-COUNCIL.md) remains historical expansion-design evidence; it is not a whole-game balance result. Existing saves have accumulated growth and equipment histories, so new-game and existing-save results must be distinguished.

## Research: what actually makes strong builds strong

These are recurring strong-build patterns, not a measured ranking of the assembled expansion. Original player reports identify candidates; original mechanics research and local implementation explain what to test. Research concerns FFTA on GBA, not FFT or FFTA2.

| Pattern | Why it belongs in the comparison | Evidence |
|---|---|---|
| Assassin-grown Red Mage/Summoner | Combines early initiative with two spells and broad coverage; a damage-only adjustment leaves initiative intact. | [Players' build comparison](https://gamefaqs.gamespot.com/boards/560436-final-fantasy-tactics-advance/47894705), [growth discussion](https://gamefaqs.gamespot.com/boards/560436-final-fantasy-tactics-advance/48024347) |
| Assassin with Concentrate and ranged finishers | Removal and ranged offense cover different defenses; assess the complete command/equipment loadout. | [Assassin discussion](https://gamefaqs.gamespot.com/boards/560436-final-fantasy-tactics-advance/42801349) |
| Ninja-grown Paladin/Hunter or Blue Mage | A useful strong physical comparison with either ranged offense or disruptive utility. Preserve a viable ordinary attacker. | [Human build comparison](https://gamefaqs.gamespot.com/boards/560436-final-fantasy-tactics-advance/48013954) |
| Smile/Quicken supporters | Turn transfer concentrates output in the strongest unit; reciprocal Smile is a documented enemy-turn denial loop. | [White_Ghost's walkthrough](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/25622) |
| Multiple Turbo MP Illusionists | Test stacked global coverage separately from one caster in a mixed party. | [Original community FAQ](https://gamefaqs.gamespot.com/boards/560436-final-fantasy-tactics-advance/44957549) |
| Blue Mage Night with sleep-resistant allies | Party preparation can make broad control functionally one-sided; include it in the opening-turn comparison. | [First-hand player strategy](https://www.reddit.com/r/finalfantasytactics/comments/1i8t9uz) |

Mechanics checks from [Terence Fergusson's original research, v0.95](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262): Concentrate changes attack evasion and status resistance differently; Turbo MP also affects accuracy. Sleep/Stop can alter hit resolution, so accuracy changes alone do not close removal chains. FFTA Doubleshot has two half-strength effects; Double Sword does not double every ability. Ultima Masher uses weapon range/power with a triple-damage effect. Smile applies Quicken without MP. These distinctions prevent importing sequel advice or treating every accuracy roll alike. The guide explicitly has incomplete cases; verify changed paths in the native game.

## Recommended first prototype

Numbers below are explicit starting values for comparison, not claims of tested balance. Treat the prototype as one coherent package, with independent switches for diagnosis. Retune from measured results before release.

### 1. Preserve turn support, stop recursive feeding

- A unit may receive **one granted turn between its naturally scheduled turns**.
- An actor taking a granted turn cannot issue another immediate turn grant. Apply the rule to all equivalent effects, both teams, and reflected/re-directed results.
- Keep normal movement and one ordinary action during the granted turn. Haste and native speed still matter.
- Reset recipient eligibility only on authenticated natural scheduler readiness, never on an ordinary turn-start callback. A KO/revival, unit copy, or suspend/resume cannot clear exhaustion. Initialize it as available at battle start.
- If native control skips a naturally scheduled turn, that verified natural opportunity may reset eligibility; a generic status tick cannot. A scheduler trace must establish the actual distinction before implementation.
- Granted turns do not refresh once-per-natural-turn recovery readiness or award renewable start-turn resources. Maintain explicit per-effect timer rules; do not freeze every temporary buff to achieve this. Movement still initializes normally.
- Make exhausted targets visibly unavailable and exclude those actions from AI scoring before commitment. Preserve existing costs, law checks, and normal status immunity.

**Payoff:** a Juggler still rescues an ally or accelerates a finisher, but multiple supporters cannot repeatedly feed the same carry, and two supporters cannot monopolize the scheduler.

**Risk:** this is a scheduler change, not a numeric edit. Existing [turn support code](../src/engine/turn-supports.c) tracks movement and support readiness, not proof of natural-turn origin. If origin cannot be represented safely, redesign the grant rule rather than silently substituting a bypassable cooldown.

### 2. Doublecast remains two useful choices

Use **80% direct HP damage and direct HP restoration per subcast**, with full normal MP payment for both. One ordinary cast remains 100%. Equal spells therefore yield 160% output in one action; the player still gains coverage, two targets, or healing plus attack.

Allow at most **one hard-control/removal spell and one revival spell** in a pair. For the control count, a spell carrying Sleep, Stop, Disable, Charm, Confuse, KO, or Petrify counts even when it also damages. Soft effects such as Poison, Blind, Silence, and Slow retain their existing behavior initially. Buffs, cures, and legal revival fractions are not numerically multiplied; revival still obeys the one-component limit. A revival-plus-control pair remains legal and is an explicit test case.

Use 80% once on eligible calculated HP magnitude, consistently for elemental absorption and drain; recovery from drain follows actual damage and its existing cap. Do not multiply fixed costs, MP restoration, status probabilities, or revival fractions by 80%. Audit percent/fixed-damage exceptions individually so they cannot become the replacement burst exploit. New expansion techniques remain ineligible for Doublecast.

**Decision from debate:** rejected 100% first/60% second because it arbitrarily rewards ordering the stronger spell first. One reviewer preferred leaving healing untouched; the chair chose symmetric direct healing because compressed healing can otherwise dominate longer fights. Ordinary single-cast healing and Chemist restoration are untouched.

**Risk:** native forecast, spell selection, subcast cancellation, absorption, laws, and AI must agree. The existing [Doublecast continuation](../src/engine/mystic-knight-doublecast.c) is useful infrastructure, not an already implemented balance hook.

### 3. Removal requires a wounded target; control requires engagement

Prototype deliberate hostile KO/Petrify effects as finishers against living targets at **50% maximum HP or lower**, retaining the native success check and all immunities. Above the threshold, show the removal effect as unavailable; hybrid actions may still deal their otherwise legal damage. Evaluate eligibility before that component's damage, so a full-HP hit cannot qualify its own removal rider. Audit every equivalent vanilla, monster, item, reaction, weapon-proc, and expansion route, including Break Blade. Ordinary lethal damage and special mission scripts are outside this rule.

Remove Concentrate/Turbo MP accuracy bonuses from the **hard-control/removal effect only**, not the preceding damage roll. Preserve ordinary accuracy, soft debuffs, facing, and innate immunities. Conditional guaranteed-hit states do not bypass the HP requirement.

Change **Night to range 4, Manhattan radius 2**, retaining friendly fire, caster exclusion, native resistance/immunity, and Blue Magic learnability. Height and line-of-sight behavior need an explicit targeting contract using an existing supported area template; do not ship an undocumented geometry approximation. Target-area law classification, enemy learning opportunities, forecast, and AI must match the new shape.

**Payoff:** assassination becomes a supported finisher; control enables an advance instead of shutting down the entire map from safety.

**Tradeoff:** a native-chance finisher may be unattractive compared with simply attacking. Compare it with a separate 35%-HP guaranteed-eligible variant if usage collapses; do not silently stack both advantages. Do not give all bosses blanket status immunity. If focused control still denies all usable turns indefinitely, the package fails acceptance: test a clearly displayed one-natural-turn recovery immunity for the same hard-control family as a separate revision, not an assumed feature of this proposal.

### 4. Close the tiny-MP shield without deleting magical defense

For hits already eligible for Damage > MP, spend available MP **one-for-one against the final otherwise payable damage**, and apply any remainder to HP. Preserve native eligibility restrictions. Illustrative proposed result: 100 damage into 12 MP becomes 12 MP lost and 88 HP lost.

This retains a finite shield and makes Bloodcasting's preservation of MP useful without making tiny reserves erase arbitrarily large hits. Resolve ordinary mitigation once before splitting resources. Self-costs remain self-costs. Drain, wounds, retaliation, and damage-triggered recovery use actual qualifying HP loss, not absorbed MP or forecast damage.

**Risk:** the expansion currently intentionally treats native MP interception as a separate path in [Dark Knight supports](../src/engine/dark-knight-support.c), [Bard modifiers](../src/engine/bard.c), and other consumers. Spillover requires a shared damage-resolution contract and audits of Poise, wards, multi-hit attacks, forecast and AI; it is not a one-line reaction edit.

### 5. Trim exceptional burst, retain earned combinations

| Mechanic | Current reviewed value | First prototype | Reason and consequence |
|---|---:|---:|---|
| Racial Ultima actions | Audit each native record; the documented Masher baseline is 3.00x | 2.25x; keep each existing MP cost and weapon reach | Costly ranged finishers remain strong; do not compensate by making them cheap. Verify all variants together. |
| Desperation | +50% at <=35% HP | +35%; same threshold | Sacrifice remains rewarding with a smaller burst ceiling. |
| Last Resort | +25% physical output; +20% incoming physical | +15% output; retain linked +20% drawback and initial strike | Setup already contributes an attack; it need not also supply a large multiplier. Check that the increased relative risk still earns a slot. |
| Bard offensive song bonus | +20% | +15% | Party-wide value, Protect/Shell, reach, and duration remain valuable. Do not reduce healing songs here. |
| Sword Dance | 1.60P | 1.40P | Maintains a straightforward paid finisher without dominating alternating builds. |

Retain Spellweave/Follow Through at +35%, Fury's current charge, ordinary Double Sword, Doubleshot, base job damage, and normal defenses initially. Do not add a universal modifier cap: it hides wasted support slots and punishes the very setup choices the patch should encourage.

Source-supported example ceilings, excluding hit chance, defenses, weakness, resources, and the actions spent establishing conditions:

- Fell Cleave with Desperation, Last Resort, and the physical song: `1.80 x 1.50 x 1.25 x 1.20 = 4.05P`; prototype `1.80 x 1.35 x 1.15 x 1.15 = 3.21P`.
- Sword Dance with Spellweave, Fury, and the physical song: `1.60 x 1.35 x 1.35 x 1.20 = 3.50P`; prototype `1.40 x 1.35 x 1.35 x 1.15 = 2.93P`.

These are illustrative legal conditional products, not measured party DPS or promised kill thresholds. Setup is not free, but attack-and-buff actions, multi-ally songs, and reactive charges mean it is not always a completely lost attack either. Update all rational-factor callers together; the current Dark Knight and Bard functions use shared denominators.

## Keep the rest of the game relevant

- **Samurai:** keep Centered's rhythm, useful defense, and healing; test Ninja-trained carriers separately from native growth.
- **Dark Knight:** preserve HP costs and action-paid recovery. Retest Bloodcasting plus the new finite MP shield; do not additionally cut drains without evidence.
- **Viking and axe Soldier/Gladiator:** preserve reach, theft, storms, displacement, and weapon restrictions. Last Resort must not grant sword drains to axe loadouts.
- **Geomancer:** preserve fields, movement control, Refuge, and terrain choices. Include Wisp Exposure plus allied Doublecast in the burst matrix.
- **Chemist:** retain ranged rescue, ingredient costs, and existing revival rules. Slower fights increase inventory consumption, so track spend per battle, not only healing per action.
- **Bard:** keep cures, recovery, and protection; test fast Juggler/Song without conflating two commands with three.
- **Dancer/Mystic Knight:** keep repositioning, weakness setup, enchantments and alternation. Apply the removal rule to Break Blade; do not accidentally grant Doublecast to dances or Spellblade.

Do not globally reduce speed growth in the first patch. It would leave existing trained units different from new ones and can make normal progression feel punitive. Run ordinary, organically trained parties and legal optimized-growth parties side by side. If optimized speed still prevents response after the action-economy changes, speed is a release blocker requiring a separately specified combat-speed adjustment, not a reason to secretly rewrite saved stats.

Likewise include optimized Morphers, Blue Mage stat-building, growth weapons, repeated global Illusionist casts, combos, Totema, and early acquisition shortcuts in adversarial tests. They are unresolved comparison cases, not confirmed balanced by these changes. Do not remove Steal Ability, AP mastery, or recovery features merely to postpone powerful builds. Judge availability using real chapter/shop/AP constraints, not fully mastered endgame units placed in early missions.

Enemy changes should initially concern **using legal changed abilities competently**. Then adjust only identified outlier encounters: a limited support unit, better separation, or an answer to a specific tactic can help. Avoid handing every enemy blanket immunities, inflated stats, or the player's strongest infinite combo. Verify scripted objectives, solo battles, recruitment/learning opportunities, and fixed bosses separately.

## What would count as success

All targets below are proposed acceptance criteria; no baseline measurements were collected in this review.

1. On representative neutral equal-tier matchups, an ordinary damage action usually removes roughly **25–45%** of an ordinary foe's HP; a paid/prepared burst roughly **55–75%**. These are diagnostic bands, not hard runtime caps. Weakness exploitation, fragile targets, and coordinated focus fire may still kill. Multi-target totals, bosses, fixed damage and reactions need separate comparisons.
2. On a fixed representative six-enemy map, at least **three enemies obtain a usable natural action before being removed or continuously disabled** under the selected optimized opening. Measure the actual first natural opportunity, not arbitrary player rounds. Bounded control paid for with comparable party actions is an explicitly reviewed exception, not an automatic failure.
3. No renewable deterministic action sequence prevents all enemy opportunities indefinitely. Measure denial as well as damage; replacing damage blitz with Sleep/Stop lock is failure.
4. Mixed ordinary parties finish routine fixtures with at most **25% more total unit activations** than their baseline. For optimized parties, initially target **25–60% more activations** only on fixtures that currently collapse before meaningful response. Absolute turn counts, animations, and completion time must also be recorded; these relative bands must not bless already tedious fights.
5. No forced heal/revive equilibrium. Flag three consecutive natural cycles of continuing resource exchange without net objective progress; distinguish deliberate optional stalling from a dominant or unavoidable loop. Record healing, MP and consumable expenditure, denied actions, KO/revival counts, and objective progress.
6. At least one representative organic party of each racial mix remains viable; the best new job combination cannot be the sole practical answer. Compare identical progression/equipment histories where possible.

Use fixed seeds/scenarios at levels about **10/25/40**, real shop/mastery tiers, compact/open/chokepoint maps, and both mixed and adversarial squads. Freeze a manageable baseline corpus first: three stage fixtures, three geometry fixtures, targeted exploit scenarios, and selected bosses/solo/objective missions. Do not imply that a small corpus proves every mission balanced.

## Implementation and verification order

1. Record an authenticated baseline ROM, legal builds and deterministic inputs. No game-playing agents or one-off interactive fixtures.
2. Implement turn provenance, targeting/forecast/AI rules, and MP spillover as bounded components; verify each contract before combining them.
3. Apply Doublecast, removal/Night, and numeric changes as the coherent prototype. Update help text, laws, previews and AI alongside mechanics.
4. Run the fixed balance corpus and targeted existing regressions through **Test Expansion.ps1** with a declared plan and `-Only` plus prerequisites. Record exact IDs and justification before runtime execution.
5. Retune the specific failure: distinguish raw damage, initiative, mass control, sustain, geometry and acquisition. Do not reflexively add HP.
6. Only at final assembled acceptance, justify a full integration run and representative longer campaign testing. Current campaign-progression checks do not establish encounter difficulty, and the existing release still lacks a full campaign playthrough.

Relevant existing IDs in [the integration plan](../scripts/integration-test-plan.json) include `test-integrated-dark-knight-desperation`, `test-integrated-dark-knight-blood-edge`, `test-integrated-hp-provenance`, `test-integrated-bard`, `test-integrated-bard-passives`, `test-integrated-dancer`, `test-integrated-turn-supports`, `test-integrated-chemist-reactions`, `test-integrated-geomancer-fields`, `test-mystic-knight-doublecast`, `test-doublecast-reactions`, `test-mystic-knight-doublecast-lifecycle`, `test-ai-choice`, and `test-custom-status-law-prediction`. Choose actual affected consumers; this list is not an instruction to run every test. Existing AI/turn checks have narrow scope and do not prove all vanilla AI or scheduler provenance.

**New tests must be authored and declared**, with proposed names `test-balance-turn-grants`, `test-balance-mp-spillover`, `test-balance-doublecast-budget`, `test-balance-removal-eligibility`, `test-balance-night-targeting`, `test-balance-opening-response`, and `test-balance-campaign-pacing`. These names are planning labels, not runnable or passing tests. Include multiple donors, both sides, reflected grants, interrupted actions, skipped turns, KO/revive, suspend/copy, native immunities, status riders, two-hit attacks, stock exhaustion, prediction/result agreement, and legal AI choices. New battle state needs suspend/copy/lifecycle verification; cold-save tests depend on whether persistent state actually changes.

Preserve ROM hashes, complete logs, fixed inputs and pass/fail results. Document-only validation for this proposal covers links, format, cited source paths and the Git asset guard; it cannot validate the proposed gameplay.

## Council resolutions and remaining uncertainty

| Question | Resolution | Why |
|---|---|---|
| Raise all HP or cut all damage? | Rejected | Leaves instant removal intact and increases healing/control dominance. |
| Universal +50% bonus pool/cap? | Rejected | Creates hidden dead choices and a broad modifier rewrite. Prefer four targeted trims. |
| Doublecast 100%/60% or 80%/80%? | Chair selects 80%/80% | Avoid arbitrary ordering advantage; direct-healing trim remains a monitored tradeoff. |
| Lower Concentrate for everything? | Rejected | Makes routine attacks frustrating and misses Turbo MP's alternative status benefit. |
| Make healthy-target assassination merely less accurate? | Rejected | Encourages retries and leaves guaranteed-hit setup paths. |
| Damage/HP finishers alone solve control? | Rejected | Night geometry, duplicate control and repeated denial must also be measured. |
| Cut healing, growth and every strong vanilla job now? | Rejected | Too many interacting changes to diagnose; preserve anchors and react to measured failures. |
| Can this be called balanced now? | No | It is a source-backed, coherent prototype recommendation. Scheduler, AI and campaign outcomes remain untested. |

The intended feel is an opening that establishes positions and pressure, an exchange where enemies can respond and support matters, and finishers that reward preparation. Strong parties should still win decisively; they should need to engage with the fight.
