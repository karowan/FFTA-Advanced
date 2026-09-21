# Additional ability council — adopted as version 0.7

September 14, 2026. **All seven candidates approved and adopted as design 0.7.** The current specification contains 129 abilities and 85 teaching items. The review below records why they were proposed; former conditional/reserve labels do not postpone adoption. Numerical/teaching targets remain provisional and technical verification remains necessary. No ROM patch is implied.

## Adoption record

The user approved the entire seven-ability shortlist. Canonical rows, shared timing/cleanup rules, command contexts, lineage, AP totals and teaching gear are updated in [the class specification](JOB-CLASS-SPECIFICATION.md). Version 0.6 is archived in notes/design-v0.6. The original Spell Parry reaction remains unchanged; the separate zero-damage-consumption refinement was not one of these seven abilities.

| Adopted ID | Ability | AP | Teaching weapon |
|---|---|---:|---|
| SAM-A9 | Higanbana | 300 | Red Spider Katana |
| DRK-A9 | The Blackest Night | 300 | Nightward Sword |
| VIK-A9 | Provoke | 250 | Challenger Axe |
| GEO-A9 | Nature's Refuge | 300 | Refuge Rod |
| CHM-A9 | Inoculation | 300 | Preventive Knife |
| CHM-A10 | Guarding Draught | 200 | Fortifying Knife |
| DNC-A9 | Passing Step | 250 | Passing Foil |

## Original council recommendation

Expand when an action creates a worthwhile choice. Mystic Knight's elemental coverage justified fourteen; that does not establish a new minimum. Three reviewers examined martial jobs, utility jobs, and adversarial cross-class combinations, followed by peer review and chair reconciliation.

The chair's strongest next candidates are **Dark Knight's The Blackest Night, Dancer's Passing Step, and Chemist's Inoculation**. Guarding Draught is another useful Chemist option, though its Protect/Shell effects overlap existing magic. Samurai's Higanbana and Viking's Provoke deserve consideration with their encounter-specific limits. Geomancer's Nature's Refuge is a reserve candidate. Bard and the existing Soldier/Gladiator axe additions need no extra action now.

| Job | Candidate | New decision | Priority / possible count |
|---|---|---|---|
| Dark Knight, Human/Bangaa | The Blackest Night | Spend HP/MP to shield someone else rather than spend HP to attack | Strong recommendation; 8 → 9 |
| Dancer, Viera | Passing Step | Divide ordinary movement around a melee strike | Strong recommendation; 8 → 9 |
| Chemist, Nu Mou/Moogle | Inoculation | Spend medicine before an ailment arrives, instead of curing it afterward | Strong recommendation; 8 → 9 alone |
| Chemist, Nu Mou/Moogle | Guarding Draught | Use inventory for proactive Protect/Shell instead of restoration | Useful second option; 10 with both mixtures |
| Samurai, Human | Higanbana | Apply a wound and devote later actions to another target or healing | Conditional recommendation; 8 → 9 |
| Viking, Bangaa | Provoke | Reduce an enemy's damage against allies while leaving full damage against the challenger | Conditional recommendation; 8 → 9 |
| Geomancer, Nu Mou | Nature's Refuge | Choose allied magical shelter instead of a hostile Rime zone | Reserve candidate; 8 → 9 if field prototype supports it |
| Bard, Moogle | None now | Existing song coverage is already broad and secondary-command choices remain valuable | Retain 8 |
| Soldier / Gladiator | None now | Four new axe actions already expand each complete vanilla command | Retain vanilla actions plus four axe actions each |
| Mystic Knight, Viera | No further additions this round | Approved fourteen already cover enchantment, control, sustain, dispel and release | Retain 14 |

## Strongest candidates

### The Blackest Night — Dark Knight

Provisional target: 10 MP plus 10% maximum HP, range 3, self or one ally. A short-lived ward halves direct HP damage from the next successful damaging enemy action. It gives no healing, refund, status immunity, or extra action. It expires at the start of the caster's next turn if unused. The payment must still leave at least 1 HP.

This introduces the dark protector side of the profession. A Bangaa Viking/Dark Arts could protect an ally without needing a sword for this weapon-free technique; Human Paladin/Dark Arts retains its native Paladin command, not an additional White Magic command. Bloodcasting pays both the converted MP and native HP cost. A 200-HP user pays 20 HP and 10 MP normally, or 40 HP with Bloodcasting. Ward plus Poise would leave 37.5% of eligible incoming HP damage for one enemy action; it never protects the HP payment itself. Resource-redirection ordering requires explicit implementation tests, not an assumption that Damage > MP works a particular way.

Its inspiration is FFXIV's self/ally barrier; our sacrifice and single-action reduction are adaptations. [Official Dark Knight guide](https://na.finalfantasyxiv.com/jobguide/darkknight/).

### Passing Step — Dancer

Reconciled provisional target: 6 MP, adjacent enemy, 0.95 Pdance physical damage. After the strike and immediate enemy reaction, the surviving performer may spend up to two **remaining normal movement points** on a legal path; taking this step ends ordinary movement for that turn. It does not refresh Move or grant bonus movement. A full-movement approach leaves no retreat allowance, but the strike remains usable.

Example with Move 4: approach two points, strike, retreat two points. Ordinary act-then-move already permits retreat when starting beside an enemy; the new benefit is splitting movement around the attack. This is an explicit proposed exception to the current rule that actions do not move their user. Immobilize, terrain costs, height, traps, occupancy, and reaction timing still matter. It cannot dodge the reaction that the strike has already triggered.

This works as a physical Spellweave partner for Red Mage/Dance and as a maneuver for Fencer/Dance. Assassin/Dance could use the weapon-free performance, but spends its action on modest melee damage instead of an Assassin action. It uses Pdance, not a powerful held weapon's Attack. Movement after damage cannot retroactively qualify a bonus checked before the attack.

The utility reviewer initially proposed two additional paid movement points. Peer review favored the remaining-budget version to preserve the move's distinctive split movement without also extending objective reach. This is a substantive council revision. En Avant supplies authentic Dancer movement inspiration; Passing Step is our own attack-and-movement adaptation. [Official Dancer guide](https://na.finalfantasyxiv.com/jobguide/dancer/).

### Inoculation — Chemist

Provisional target: one Potion plus one Cureall, range 4, one living non-undead ally or self. Give T2 prevention against the existing Cureall/Auto-Cureall curable-ailment set, with an explicit whitelist required before implementation. It does not cure existing ailments, block damage, grant KO immunity, or erase a paid drawback. It is dispellable and does not stack. Long Throw can extend an eligible throw; Pharmacology cannot strengthen immunity or duration.

This provides an active way to protect a teammate's ability to act, rather than requiring that teammate to equip Auto-Cureall. It spends a scarce item and a turn before knowing whether the protection will matter. Moogle Time Mage/Items can choose prevention or Time Magic; a Nu Mou using Items cannot borrow Moogle-only Encouragement. Protecting another race does not transfer the recipe to that race. Original Cureall supply and mastery timing must be checked.

FFV Mix contains preventive status mixtures; our recipe, broader whitelist, and duration are original. [FFV Mix reference](https://finalfantasy.fandom.com/wiki/Mix_(Final_Fantasy_V)).

### Guarding Draught — Chemist

Provisional target: one Potion plus one Soft, range 4, one living non-undead ally or self. Apply ordinary Protect and Shell with no new defensive multiplier or healing. The recipe and its fiction are original; FFV Protect Potion is the thematic precedent. It gives medicine a useful healthy-target action while retaining inventory and law costs. [FFV Mix reference](https://finalfantasy.fandom.com/wiki/Mix_(Final_Fantasy_V)).

This overlaps Bard/Samurai/White Magic's protection effects but makes them available through a medical secondary, including for Nu Mou. It does not stack another copy of Protect or Shell. Inoculation remains the more distinctive addition. A Moogle's Encouragement may heal once for a newly applied qualifying status, under current rules; this does not make refreshes into repeated free heals.

## More situational candidates

**Higanbana:** an 8-MP katana strike dealing 0.80P now plus two removable wound pulses of 0.50P each. Its unboosted full total is 1.80P if both pulses occur, versus Kiku-ichimonji's immediate 1.45P at range. The initial hit can receive applicable outgoing bonuses; the wound snapshots its separate reference and does not multiply those bonuses again. One wound per target, no reactions or drain from pulses, no immunity bypass. Its role is sustained pressure during later healing or target changes. If typical enemies die before it earns the second pulse, leave it out rather than add a weak lesson. [Official Samurai guide](https://na.finalfantasyxiv.com/jobguide/samurai/).

**Provoke:** 6 MP, one enemy within range 3, ordinary status check. Until the end of that target's next turn, its eligible HP damage against recipients other than the challenger is multiplied by 0.70. Full damage to the challenger remains. This is an original soft challenge inspired by FFIII Viking's command, not forced targeting or Berserk. Only one challenger applies; ordinary immunity and cleansing remain. Viking/Gladiator can invite axe retaliation, but the enemy retains its actions and target choices. Vanilla AI is not promised to understand the new penalty. Its custom relation and preview are a greater integration cost than another ordinary debuff. [Square Enix FFIII Provoke reference](https://support.na.square-enix.com/faqarticle.php?c=0&id=5141&kid=63557&la=1&page=3&pv=10&ret=faq&sc=0&so=0).

**Nature's Refuge:** 12 MP for a stationary cross-shaped field that reduces magical HP damage by 20% for grounded allied occupants. Shares the caster's single field slot with Rime; neither action is deleted. It adds no healing, status immunity, physical reduction, or occupancy-triggered Encouragement. Earthen Ward remains mobile physical protection. Refuge's occupants must choose between holding shelter and positioning elsewhere; Float/Updraft conflicts with grounded shelter. Defer exact adoption until field occupancy, overlapping casters, and previews work. FFXI's Geomancer provides the aid-allies/harm-enemies identity, not this exact mechanic. [Official Seekers of Adoulin manual](https://support.na.square-enix.com/document/manual/20/FFXI_SeekersOfAdoulin_PC.pdf).

## Review evidence and boundaries

The skeptical audit found no blocking contradiction in the six approved Spellblade concepts. Its new-action clarifications have been integrated: Spellbreak dispels its selected status after hit/interception resolution and before damage calculation; Arcane Release explicitly uses A per target; Break's Spellweave exclusion does not suppress ordinary legal accuracy supports. The axe addendum's global counts now match 122/78. Its proposed change to Spell Parry's zero-damage consumption is **not adopted**: the existing reaction still consumes after a successful eligible physical hit check. See the current [Spellblade record](SPELLBLADE-EXPANSION.md) rather than treating all reviewer suggestions as current rules.

- [Martial review](notes/expansion-council-martial.md): Samurai, both Dark Knights, Viking, and existing axe additions; official lineage, numbers, legal builds and rejected alternatives.
- [Utility review](notes/expansion-council-utility.md): Geomancer, both Chemists, Bard and Dancer; recipes, movement reconciliation, fields and legal secondary commands.
- [Adversarial review](notes/expansion-council-skeptic.md): independent priorities, cross-class interactions, and approved Spellblade integration checks.
- [Approved Spellblade record](SPELLBLADE-EXPANSION.md): what has actually been adopted, including provisional numerical targets.

Exact figures above are review targets, not tested balance or implemented features. No candidate creates another support slot, reaction slot, learned command, immediate turn, new race, growth advantage, prerequisite change, consumable shop stock, or higher weapon-power ceiling. Teaching/AP records for all seven adopted abilities now appear in the current specification. Original 0.5 council evidence remains historical; the current 0.7 specification owns all totals.

## Final integration choices

Passing Step uses the revised 6 MP / 0.95 Pdance remaining-budget split, never the discarded extra-movement draft. Higanbana snapshots before temporary final-damage and interception modifiers. The ward resolves consumption against positive HP-payable damage after prior redirection; entirely MP-paid actions preserve it. Inoculation uses exactly native Cureall eligibility plus the explicitly listed custom broad-remedy tags, resolving before Auto-Cureall stock spending; native status IDs must be verified before implementation. Refuge and Rime occupy one field slot, and only grounded allies receive Refuge protection. All seven remain adopted even though those engine behaviors still require proof.
