# Job inspiration and design register

Version 0.4 — September 14, 2026

**Theme guides the job; FFTA gameplay guides its mechanics.** The [design principles](JOB-DESIGN-PRINCIPLES.md) supersede the source-list emphasis of the previous audit. [The full specification](JOB-CLASS-SPECIFICATION.md) and [axe addendum](AXE-SKILL-EXPANSION.md) describe the current proposals.

This register covers all 116 current ability entries. An inspiration reference does not establish that our exact move exists in another game, and a recognizable job does not require copied skills. Our changes can improve reliability, change scaling and cost, broaden access, or create new effects. Values remain untested. Samurai and Geomancer were rebuilt in this revision; Viking's wave now has useful base behavior on land. Other entries remain provisional and are free to change under the same principles.

Samurai now uses sword development and a composure-and-release rhythm. Geomancer has useful baseline nature arts, terrain bonuses, party utility, and a persistent ice field. These are deliberate creative departures. Source-game accuracy remains relevant when describing the source, but copying its restrictions is not a requirement for our design.

All 18 support entries now follow [the cross-job support design](SUPPORT-SKILL-DESIGN.md). The teaching job grants access; the benefit applies across legal current jobs and appropriate original or new commands.

## Current entries and inspiration

The previous-name column refers to the initial v0.1 design, retained for traceability. Adaptation and thematic redesign describe a starting point, not a fidelity ranking. Original extensions are equally valid when they serve the job's identity. Combo entries retain ordinary FFTA integration.

| ID | Initial draft | Current entry | Classification | Inspiration / purpose |
|---|---|---|---|---|
| SAM-A1 | Measured Cut | Ashura | Thematic redesign | Decisive draw that builds composure; original attack-and-prepare mechanic. [Inspiration][sam] |
| SAM-A2 | Hilt Bash | Wind Draw | Thematic redesign | Original cutting wind released through katana technique. [Inspiration][sam] |
| SAM-A3 | Wind Draw | Osafune | Thematic redesign | MP-cutting blade spirit redesigned to also contribute HP damage. [Inspiration][sam] |
| SAM-A4 | Meditate | Murasame | Thematic redesign | Healing blade spirit, with reach and scaling chosen for frontline support. [Inspiration][sam] |
| SAM-A5 | Sunder Guard | Kiyomori | Thematic redesign | Protective blade spirits; group defense earns its action through multiple allies. [Inspiration][sam] |
| SAM-A6 | Guard Stance | Guarding Draw | Thematic redesign | Original guarded sword strike that combines pressure with self-protection. [Inspiration][sam] |
| SAM-A7 | Moon Draw | Kiku-ichimonji | Thematic redesign | Far-reaching blade spirit redesigned as a precise ranged finisher. [Inspiration][sam] |
| SAM-A8 | Heaven Cut | Moon Blossom | Thematic redesign | Original culminating spirit release, with offensive and sustaining roles. [Inspiration][sam] |
| SAM-S1 | Single Blade | Composure | Cross-job support design | Calm, deliberate action; useful with attacks, techniques, and magic. [Inspiration][sam] |
| SAM-S2 | Poise | Poise | Cross-job support design | Maintaining composure under protection; benefits can come from allies or another command. [Inspiration][sam] |
| SAM-R1 | Sheath Guard | Blade Ward | Thematic redesign | Original blade defense with a broader trigger than a Fight-only evasion move. [Inspiration][sam] |
| SAM-R2 | Riposte | Counter Draw | Thematic redesign | Original reactive draw that prepares the next deliberate technique. [Inspiration][sam] |
| SAM-C1 | Crescent Combo | Crescent Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| DRK-A1 | Blood Edge | Blood Edge | Original extension | Original introductory sword technique built around the job's health sacrifice. [Inspiration][drk] |
| DRK-A2 | Siphon Blade | Sanguine Sword | Adaptation | HP-draining sword art. [Inspiration][drk] |
| DRK-A3 | Dread Wave | Infernal Strike | Adaptation | MP-draining sword art. [Inspiration][drk] |
| DRK-A4 | Night Veil | Dark Mind | Adaptation | Personal protection against magic. [Inspiration][drk14] |
| DRK-A5 | Crippling Oath | Last Resort | Adaptation | Attack at the expense of defense. [Inspiration][drk11] |
| DRK-A6 | Blood Price | Crushing Blow | Adaptation | Sword damage with Stop. [Inspiration][drk] |
| DRK-A7 | Gravebind | Abyssal Blade | Adaptation | Health sacrifice, distance-falloff wave. [Inspiration][drk] |
| DRK-A8 | Abyss Blade | Unholy Sacrifice | Adaptation | Health sacrifice, dark area damage and Slow. [Inspiration][drk] |
| DRK-S1 | Desperation | Desperation | Cross-job support design | Dangerous offense at low health, usable by martial and magical builds. [Inspiration][drk] |
| DRK-S2 | Sacrificial Will | Bloodcasting | Cross-job support design | Trade life for action resources across spell and technique sets. [Inspiration][drk] |
| DRK-R1 | Dark Ward | Dark Ward | Original extension | Original reactive variant of the Dark Mind ward. [Inspiration][drk14] |
| DRK-R2 | Vengeful Pulse | Vengeful Pulse | Original extension | Original dark retaliation fueled by injury. [Inspiration][drk] |
| DRK-C1 | Abyss Combo | Abyss Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| VIK-A1 | Cleave | Thunder | Adaptation | Lightning spell. [Inspiration][vik] |
| VIK-A2 | Shoulder Check | Pickpocket | Adaptation | Gil theft. [Inspiration][vik] |
| VIK-A3 | Thunderbrand | Strong-Arm | Adaptation | Damage plus item theft, adapted to accessories. [Inspiration][vik] |
| VIK-A4 | War Cry | War Cry | Adaptation | Ailment resilience, not Attack. [Inspiration][vik] |
| VIK-A5 | Anchor Stance | Thundara | Adaptation | Mid-tier lightning magic. [Inspiration][vik] |
| VIK-A6 | Stormbreaker | Pillage | Adaptation | Damage plus armor theft. [Inspiration][vik] |
| VIK-A7 | Oath of Iron | Thundaga | Adaptation | High-tier lightning magic. [Inspiration][vik] |
| VIK-A8 | Tempest | Tsunami | Thematic redesign | Sea power redesigned to function on land, with water proximity enhancing its effect. [Inspiration][vik] |
| VIK-S1 | Sea Legs | Sea Legs | Cross-job support design | A raider keeps their footing; transferable positional protection. [Inspiration][vik] |
| VIK-S2 | Heavy Grip | Opportunist | Cross-job support design | A raider exploits openings created by any ally or command. [Inspiration][vik] |
| VIK-R1 | Hardy | Absorb Damage | Adaptation | Damage recovery; a chance and lockout are added here. [Inspiration][vik] |
| VIK-R2 | Thunder Rebuke | Gil Snapper | Adaptation | Gil after a critical hit; payout and battle cap are ours. [Inspiration][vik] |
| VIK-C1 | Tempest Combo | Tempest Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| GEO-A1 | Stone Shard | Stone Pulse | Thematic redesign | Original reliable earth pressure; terrain rewards damage rather than unlocking the spell. [Inspiration][geo] |
| GEO-A2 | Vine Snare | Tanglevine | Thematic redesign | Binding vegetation with a useful damage baseline and a stronger native control effect. [Inspiration][geo] |
| GEO-A3 | Rill | Torrent | Thematic redesign | Original wave control that breaks formations rather than copying a transformation rider. [Inspiration][geo] |
| GEO-A4 | Updraft | Updraft | Thematic redesign | Original wind assistance; positioning and traversal utility. [Inspiration][geo] |
| GEO-A5 | Frost Bloom | Earthen Ward | Thematic redesign | Original earth protection that steadies an allied formation. [Inspiration][geo] |
| GEO-A6 | Magma Vent | Wisp Flame | Thematic redesign | Original spirit flame that creates an opening for allied magic. [Inspiration][geo] |
| GEO-A7 | Earthen Ward | Rime Field | Thematic redesign | Original persistent ice terrain for area denial; native ice adds further control. [Inspiration][geo] |
| GEO-A8 | Gaia Pulse | Gaia Surge | Thematic redesign | Original major nature release whose elemental options respond to surroundings. [Inspiration][geo] |
| GEO-S1 | Terrain Lore | Attunement | Cross-job support design | Understand elemental vulnerability and apply that knowledge to any technique. [Inspiration][geo] |
| GEO-S2 | Surefoot | Surefoot | Cross-job support design | Read and traverse difficult ground, regardless of current profession. [Inspiration][geo] |
| GEO-R1 | Stone Skin | Stone Skin | Thematic redesign | Original earthen defense with a dependable opportunity to contribute across maps. [Inspiration][geo] |
| GEO-R2 | Grounding | Nature's Wrath | Thematic redesign | Reactive nature power; neither terrain permission nor a tiny status chance is required for its contribution. [Inspiration][geo] |
| GEO-C1 | Gaia Combo | Gaia Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| CHM-A1 | Field Tonic | Potion | Adaptation | Basic restorative. [Inspiration][chm] |
| CHM-A2 | Purifying Mist | Antidote | Adaptation | Poison treatment. [Inspiration][chm] |
| CHM-A3 | Smelling Salts | Phoenix Down | Adaptation | Item-based revival. [Inspiration][chm] |
| CHM-A4 | High Tonic | Hi-Potion | Adaptation | Stronger restorative. [Inspiration][chm] |
| CHM-A5 | Flash Flask | Eye Drops | Adaptation | Blindness treatment. [Inspiration][chm] |
| CHM-A6 | Ether Draught | Ether | Adaptation | MP restorative. [Inspiration][chm] |
| CHM-A7 | Remedy Compound | Cureall | Adaptation | FFT Remedy role using the actual FFTA consumable Cureall. [Inspiration][chm] |
| CHM-A8 | Phoenix Mist | X-Potion | Adaptation | High-grade restorative. [Inspiration][chm] |
| CHM-S1 | Medicine Lore | Pharmacology | Cross-job support design | Expert medicine preparation transfers to any use of supplies. [Inspiration][chm5] |
| CHM-S2 | Long Throw | Long Throw | Cross-job support design | Throw supplies accurately across the battlefield from any job. [Inspiration][chm] |
| CHM-R1 | Emergency Dose | Auto-Potion | Adaptation | Automatic inventory-funded treatment; selection and threshold adapted. [Inspiration][chm] |
| CHM-R2 | Sterile Wrap | Auto-Cureall | Original extension | Original extension of emergency item use; no free magical regeneration. [Inspiration][chm] |
| CHM-C1 | Flask Combo | Flask Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| BRD-A1 | Mending Song | Soul Etude | Adaptation | Healing plus cleansing. [Inspiration][brd] |
| BRD-A2 | Battle Hymn | Battle Chant | Adaptation | Defense song. [Inspiration][brd] |
| BRD-A3 | Mind Song | Magickal Refrain | Adaptation | Magical defense song. [Inspiration][brd] |
| BRD-A4 | March | Requiem | Adaptation | Anti-undead song. [Inspiration][brd] |
| BRD-A5 | Warding Chorus | Angelsong | Adaptation | Regeneration song. [Inspiration][brd] |
| BRD-A6 | Quiet Refrain | Hide | Adaptation | Self-concealment. [Inspiration][brd] |
| BRD-A7 | Soothing Verse | Magick Ballad | Adaptation | MP-restoring song. [Inspiration][brd] |
| BRD-A8 | Finale | Nameless Song | Adaptation | Random beneficial song. [Inspiration][brd] |
| BRD-S1 | Resonance | Encouragement | Cross-job support design | Inspiring aid makes protective and enhancing actions more useful. [Inspiration][brd] |
| BRD-S2 | Steady Breath | Clear Voice | Cross-job support design | Vocal discipline protects both songs and spellcasting. [Inspiration][brd] |
| BRD-R1 | Refrain | Magick Boost | Adaptation | FFT Bard's reactive magical growth made temporary. [Inspiration][brd] |
| BRD-R2 | Unbroken Tune | Encore | Original extension | Original reduced self-reprise of Soul Etude. [Inspiration][brd] |
| BRD-C1 | Chorus Combo | Chorus Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| DNC-A1 | Feint | Mincing Minuet | Adaptation | Area HP-damaging dance. [Inspiration][dnc] |
| DNC-A2 | Veil Dance | Witch Hunt | Adaptation | MP-damaging dance. [Inspiration][dnc] |
| DNC-A3 | Binding Step | Slow Dance | Adaptation | Disrupt enemy tempo. [Inspiration][dnc] |
| DNC-A4 | Dizzy Waltz | Polka | Adaptation | Weaken physical offense. [Inspiration][dnc] |
| DNC-A5 | Faltering Beat | Heathen Frolic | Adaptation | Weaken magical offense. [Inspiration][dnc] |
| DNC-A6 | Softshoe | Forbidden Dance | Adaptation | Random ailments with a restricted pool. [Inspiration][dnc] |
| DNC-A7 | Mending Step | Jitterbug | Adaptation | HP-draining dance. [Inspiration][dnc] |
| DNC-A8 | Curtain Fall | Sword Dance | Adaptation | FFV physical dance finisher. [Inspiration][dnc] |
| DNC-S1 | Grace | Grace | Cross-job support design | Evasive footwork transferable to any combat style. [Inspiration][dnc] |
| DNC-S2 | Light Foot | Light Foot | Cross-job support design | A performer's mobility becomes a general positioning tool. [Inspiration][dnc] |
| DNC-R1 | Slip Away | Fury | Adaptation | FFT Dancer's reactive offense made temporary. [Inspiration][dnc] |
| DNC-R2 | Counter Rhythm | Counter Rhythm | Original extension | Original reactive echo of Slow Dance. [Inspiration][dnc] |
| DNC-C1 | Waltz Combo | Waltz Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| MYK-A1 | Flame Sigil | Fire Spellblade | Adaptation | Fire enchantment. [Inspiration][spell] |
| MYK-A2 | Frost Sigil | Blizzard Spellblade | Adaptation | Ice enchantment. [Inspiration][spell] |
| MYK-A3 | Storm Sigil | Thunder Spellblade | Adaptation | Lightning enchantment. [Inspiration][spell] |
| MYK-A4 | Siphon Sigil | Poison Spellblade | Adaptation | Poison enchantment. [Inspiration][spell] |
| MYK-A5 | Spellstrike | Sleep Spellblade | Adaptation | Sleep enchantment. [Inspiration][spell] |
| MYK-A6 | Runic Guard | Silence Spellblade | Adaptation | Silence enchantment. [Inspiration][spell] |
| MYK-A7 | Break Seal | Drain Spellblade | Adaptation | Draining enchantment. [Inspiration][spell] |
| MYK-A8 | Trinity Edge | Flare Spellblade | Adaptation | Non-elemental defense-piercing enchantment. [Inspiration][spell] |
| MYK-S1 | Runeblade | Spellweave | Cross-job support design | Combine martial and magical actions across different command sets. [Inspiration][myk] |
| MYK-S2 | Warding Steel | Arcane Ward | Cross-job support design | Maintained magical reserves protect their bearer. [Inspiration][myk] |
| MYK-R1 | Runic Echo | Magic Shell | Adaptation | FFV low-health Shell placed in FFTA's reaction slot. [Inspiration][myk] |
| MYK-R2 | Spell Parry | Spell Parry | Original extension | Original magically reinforced sword guard. [Inspiration][myk] |
| MYK-C1 | Rune Combo | Spellblade Combo | FFTA integration | Original job-specific label for vanilla Judge Point combo participation. [Inspiration][manual] |
| SLD-AX-A1 | Chop | Chop | Original extension | Original straightforward addition to Soldier's martial toolkit. [Inspiration][ffta] |
| SLD-AX-A2 | Hooking Blow | Tomahawk | Adaptation | Marauder ranged axe attack; no MMO enmity. [Inspiration][axe14] |
| SLD-AX-A3 | Wide Swing | Overpower | Adaptation | Marauder area axe attack. [Inspiration][axe14] |
| SLD-AX-A4 | Shatter Guard | Shatter Guard | Original extension | Original guard-breaking extension of Soldier's weakening techniques. [Inspiration][ffta] |
| SLD-AX-S1 | Axe Grip | Recuperation | Cross-job support design | Frontline recovery training, useful to any unit taking sustained damage. [Inspiration][ffta] |
| SLD-AX-R1 | Haft Guard | Haft Guard | Original extension | Original mundane defense using the axe haft. [Inspiration][ffta] |
| GLD-AX-A1 | Armor Splitter | Armor Splitter | Original extension | Original heavy-weapon penetration added to Gladiator's offensive kit. [Inspiration][ffta] |
| GLD-AX-A2 | Reaping Arc | Reaping Arc | Original extension | Original positional variant alongside Wild Swing. [Inspiration][ffta] |
| GLD-AX-A3 | Executioner | Executioner | Original extension | Original arena finisher; no claim of a canonical FFTA move. [Inspiration][ffta] |
| GLD-AX-A4 | Overhead Crash | Fell Cleave | Adaptation | Warrior heavy axe strike; MP and Exposed replace MMO resources. [Inspiration][axe14] |
| GLD-AX-S1 | Follow Through | Follow Through | Cross-job support design | Carry movement into an attack; transferable offensive momentum. [Inspiration][ffta] |
| GLD-AX-R1 | Axe Reprisal | Axe Reprisal | Original extension | Original axe counter; compare with existing Strikeback rather than claiming a new role. [Inspiration][ffta] |

All 116 entries have an effect, identity rationale, and reference. This is document coverage, not a claim of completed numerical balance, canonical equivalence, or a working ROM patch. The roster and progression decisions remain intact.

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
