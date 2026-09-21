import fs from 'node:fs';
import path from 'node:path';

// Historical v0.2 generator. Never overwrite a later design on an ordinary run.
if (!process.argv.includes('--restore-v0.2')) throw new Error('Archived v0.2 generator. Current design is v0.3; explicit restoration flag required.');

const root = process.cwd();
const oldSpec = fs.readFileSync('JOB-CLASS-SPECIFICATION.md', 'utf8');
const oldAxe = fs.readFileSync('AXE-SKILL-EXPANSION.md', 'utf8');
const originalNames = {};
for (const m of (oldSpec + '\n' + oldAxe).matchAll(/(?:\| |\*\*)([A-Z]+(?:-AX)?-[ASRC]\d) ([^|\n]*?)(?: \|| —)/g)) originalNames[m[1]] = m[2];
if (fs.existsSync('notes/job-theme-audit.json')) for (const r of JSON.parse(fs.readFileSync('notes/job-theme-audit.json','utf8')).abilities) originalNames[r.id] = r.previous;

const refs = {
  sam: ['FFT Samurai / Iaido', 'https://finalfantasy.fandom.com/wiki/Samurai_(Tactics)'],
  drk: ['FFT: War of the Lions Dark Knight', 'https://finalfantasy.fandom.com/wiki/Dark_Knight_(Tactics)'],
  drk14: ['Square Enix: FFXIV Dark Knight job guide', 'https://na.finalfantasyxiv.com/jobguide/darkknight/'],
  drk11: ['FFXI Dark Knight abilities', 'https://finalfantasy.fandom.com/wiki/Dark_Knight_(Final_Fantasy_XI)/Abilities'],
  vik: ['FFTA2 Viking (originally Seeq)', 'https://finalfantasy.fandom.com/wiki/Viking_(Tactics_A2)'],
  geo: ['FFT Geomancer / Geomancy', 'https://finalfantasy.fandom.com/wiki/Geomancer_(Tactics)'],
  chm: ['FFT Chemist / Items', 'https://finalfantasy.fandom.com/wiki/Chemist_(Tactics)'],
  chm5: ['FFV Chemist / Pharmacology', 'https://finalfantasy.fandom.com/wiki/Chemist_(Final_Fantasy_V)'],
  brd: ['Bard comparison: Hurdy in FFTA2 and FFT Bard', 'https://ffcompendium.com/h/jobs/bard.shtml'],
  dnc: ['Dancer comparison: FFT, FFV, and FFTA2', 'https://ffcompendium.com/h/jobs/dancer.shtml'],
  myk: ['FFV Mystic Knight', 'https://finalfantasy.fandom.com/wiki/Mystic_Knight_(Final_Fantasy_V)'],
  spell: ['FFV Spellblade spell effects', 'https://strategywiki.org/wiki/Final_Fantasy_V/Magic_and_skills'],
  axe14: ['Square Enix: FFXIV Warrior / Marauder job guide', 'https://na.finalfantasyxiv.com/jobguide/warrior/'],
  ffta: ['NeoBlitz: original FFTA ability research', 'https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26226'],
  items: ['FFTA item names and effects', 'https://finalfantasy.fandom.com/wiki/Final_Fantasy_Tactics_Advance_items'],
  mechanics: ['Terence Fergusson: original FFTA mechanics research', 'https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262'],
  manual: ['Nintendo: FFTA manual', 'https://www.nintendo.com/eu/media/downloads/games_8/emanuals/game_boy_advance_8/Manual_GameBoyAdvance_FinalFantasyTacticsAdvance_EN_DE_FR_ES_IT.pdf']
};
const A = (name,cost,target,effect,ref,anchor,kind='Adaptation') => ({name,cost,target,effect,ref,anchor,kind});
const P = (name,type,effect,ref,anchor,kind='Original extension') => ({name,type,effect,ref,anchor,kind});
const jobs = [
{
id:'SAM',name:'Samurai',race:'Human',command:'Iaido',ref:'sam',
identity:'A katana warrior who releases the spirits of named blades to harm enemies and shelter allies. This uses FFT Samurai as its main model, rather than treating Iaido as a collection of ordinary physical slashes.',
rules:'Every action requires a primary katana. Offensive Iaido uses Magic Power and Magic Resistance, but remains a sword-spirit technique: Silence, Reflect, Return Magic, and Doublecast do not apply. Each technique is learned from a corresponding new katana; after mastery any equipped katana can channel that learned spirit. This replaces FFT\'s matching-inventory-katana and break-chance rules with FFTA equipment/AP learning and MP costs. No katana breaks. This is an explicit adaptation, not the original FFT implementation.',
actions:[
A('Ashura','4 MP','Self cross, enemies; A','M20 non-elemental.','sam','Katana-spirit damage'),
A('Kotetsu','6 MP','Self cross, enemies; A','M28 non-elemental; no Dark-element assignment merely because the animation is sinister.','sam','Stronger spirit attack'),
A('Osafune','6 MP','Self cross, enemies; A','Remove MP equal to floor(0.25 × the M24 damage reference), capped at current MP. Does not restore the Samurai\'s MP.','sam','MP damage'),
A('Murasame','8 MP','Self cross, allies including self; Sure','Restore floor(0.75 × caster Magic Power) HP to each eligible ally, capped at 120 and missing HP.','sam','Healing sword spirit'),
A('Kiyomori','12 MP','Self cross, allies including self; Sure','Apply Protect and Shell.','sam','Paired defensive blessings'),
A('Muramasa','14 MP','Self cross, enemies; A then S ×0.5','M32 non-elemental; after positive damage attempt Confuse. The source\'s Doom component is deliberately omitted.','sam','Cursed spirit damage and confusion'),
A('Kiku-ichimonji','14 MP','Line 4, enemies; A','M32 non-elemental per target; no friendly fire.','sam','Long-reaching linear spirit attack'),
A('Masamune','20 MP','r2, one ally or self; Sure','Apply Haste and Regen. Single-target here to constrain the source\'s group enhancement.','sam','Haste and regeneration')],
passives:[
P('Single Blade','Support','Physical HP damage dealt ×1.15 with exactly one katana and no shield. Does not boost Iaido, which uses magical damage.','sam','Disciplined single-weapon fighting; related to FFT Doublehand, but not that ability'),
P('Poise','Support','Physical HP damage received ×0.85 while at full HP at the start of the incoming action.','sam','Original defensive discipline for the armored swordsperson'),
P('Shirahadori','Reaction','Requires katana. 25% pre-hit activation: evade the incoming ordinary Fight action. Does not stop spells or A-ability techniques.','sam','Blade-catching defense; narrower than FFT and uses no Brave stat','Adaptation'),
P('Last Reprisal','Reaction','After surviving an adjacent enemy physical action at 30% HP or less, 35% activation: counter once for 1.10P, A accuracy. Requires katana.','sam','FFT Bonecrusher critical-health retaliation, renamed to distinguish unchanged FFTA Bonecrusher; source formula omitted','Adaptation')],
combo:'Crescent Combo',weapons:'katana',items:['Ashura Echo','Kotetsu Echo','Osafune Echo','Murasame Echo','Kiyomori Echo','Muramasa Echo','Kiku Echo','Masamune Echo'],category:'Katana',
build:'Iaido supplies nearby healing and protection as well as damage; Fight Tech supplies physical options. Split attack/magic development and MP expenditure limit specialization. Single Blade supports ordinary katana offense, not spirit damage.'
},
{
id:'DRK',name:'Dark Knight',race:'Human and Bangaa',command:'Dark Arts',ref:'drk',
identity:'A cursed swordsman who exchanges life and safety for force, then drains enemies to recover. FFT: War of the Lions supplies the core sword arts; two explicitly identified MMO abilities reinforce the same identity.',
rules:'Damaging and draining actions require a primary sword, greatsword, or broadsword. Their formulas are physical, including MP drain. Dark Mind and Last Resort need no weapon. Silence, Reflect, Return Magic, and Doublecast do not apply to this adapted command. No summoned undead, necromancy, free revival, or arbitrary binding curse is added.',
actions:[
A('Blood Edge','10% max HP','r1, one enemy; A','1.30P Dark.','drk','Original introductory sword technique built around the job\'s health sacrifice','Original extension'),
A('Sanguine Sword','6 MP','r2, one enemy; A','0.85P non-elemental; heal 25% of actual HP removed, capped at 10% user max HP. Undead reverse drain.','drk','HP-draining sword art'),
A('Infernal Strike','4 MP','r2, one enemy; A','Remove floor(0.20 × the 1.00P non-elemental damage reference) MP, capped at target current MP and 12. Restore exactly the MP removed to user, capped at missing MP. No HP damage.','drk','MP-draining sword art'),
A('Dark Mind','8 MP','Self; Sure','Apply Shell. FFXIV\'s defensive ability is represented by a familiar FFTA magic ward; this is not its full current mitigation profile.','drk14','Personal protection against magic'),
A('Last Resort','6 MP','Self; Sure','T2: physical HP damage dealt ×1.20 and physical HP damage received ×1.20. Both parts form one effect and expire or are dispelled together.','drk11','Attack at the expense of defense'),
A('Crushing Blow','12 MP','r2, one enemy; A then S ×0.5','1.00P weapon-elemental; after positive damage attempt Stop.','drk','Sword damage with Stop'),
A('Abyssal Blade','12 MP + 20% max HP','Line 3, any units; A','Weapon-elemental: 1.40P at tile 1, 1.10P at tile 2, 0.80P at tile 3. Pay HP once. A straight line replaces the source\'s cone.','drk','Health sacrifice, distance-falloff wave'),
A('Unholy Sacrifice','16 MP + 30% max HP','Self cross, any units except self; A then S ×0.5','1.50P Dark to each target; after positive damage attempt Slow. Never drains.','drk','Health sacrifice, dark area damage and Slow')],
passives:[
P('Desperation','Support','Physical HP damage dealt ×1.15 at 35% max HP or less, checked after paying HP costs.','drk','Original incentive to risk low health within the sacrifice identity'),
P('Sacrificial Will','Support','Dark Arts HP costs ×0.75 before rounding. Does not affect incoming damage, MP costs, or drain recovery.','drk','Original mastery of the job\'s existing sacrifice mechanic'),
P('Dark Ward','Reaction','After surviving enemy magical HP damage, 35% activation: apply Shell to self. Does not reduce the triggering damage.','drk14','Original reactive variant of the Dark Mind ward'),
P('Vengeful Pulse','Reaction','After surviving adjacent enemy physical damage, 30% activation: retaliate for Dark damage equal to 20% of HP actually lost, capped at 10% user max HP. No hit roll; elemental immunity/absorption applies. No healing.','drk','Original dark retaliation fueled by injury')],
combo:'Abyss Combo',weapons:'sword, greatsword, or broadsword',category:'Sword',items:['Gloom Sword','Sanguine Edge','Infernal Edge','Veil Sword','Oathbreaker','Crushing Edge','Abyssal Edge','Sacrifice Edge'],
build:'Human Chivalry or Bangaa Prayer can support the HP economy. Slow growth in Speed and substantial self-costs remain weaknesses. Only some arts are Dark-elemental: darkness in a name does not automatically override the documented element.'
},
{
id:'VIK',name:'Viking',race:'Bangaa',command:'Reaving',ref:'vik',
identity:'An axe-bearing plunderer who calls lightning and fights through hostile conditions. The main model is FFTA2\'s Seeq Viking, reassigned to Bangaa for our roster; that racial reassignment is ours.',
rules:'This revision gives Viking access to the new two-handed Axe family, replacing its broadsword placeholder. It shares equipment access, not Soldier/Gladiator lessons. Strong-Arm and Pillage require an axe. Thunder tiers and Tsunami are magic, blocked by Silence; eligible Thunder spells follow vanilla Reflect/Return Magic behavior. Tsunami is an environmental wave and is neither Reflected nor Returned. War Cry and theft work while Silenced. No Doublecast. War Cry improves ailment resilience, not offense.',
actions:[
A('Thunder','8 MP','r3, one target; A','M24 Lightning. Use the original Thunder damage/effect routine where possible, preserving the new command\'s targeting.','vik','Lightning spell'),
A('Pickpocket','0 MP','r1, one enemy; S','Use the original Steal Gil payout and per-target success restrictions. No invented unlimited gil source.','vik','Gil theft'),
A('Strong-Arm','4 MP','r1, one enemy; A then S','0.75P weapon-elemental; after positive damage attempt original Steal: Access. against an eligible accessory. A failed or unavailable theft does not cancel damage. This narrows A2 item theft to an existing FFTA theft category; no generic Steal Item command is assumed.','vik','Damage plus item theft, adapted to accessories'),
A('War Cry','6 MP','Self cross, allies including self; Sure','T2: reduce incoming hostile S-check success chances by 15 percentage points, minimum 0. Does not affect attacks, damage, or effects that do not make a status check; immunity still wins.','vik','Ailment resilience, not Attack'),
A('Thundara','14 MP','r3 center, cross, any units; A','M32 Lightning to each target.','vik','Mid-tier lightning magic'),
A('Pillage','8 MP','r1, one enemy; A then S','0.85P weapon-elemental; after positive damage attempt the original Steal Armor transaction against body equipment only. Preserve protection and theft immunity.','vik','Damage plus armor theft'),
A('Thundaga','20 MP','r3 center, cross, any units; A','M40 Lightning to each target.','vik','High-tier lightning magic'),
A('Tsunami','18 MP','r4 center, cross, any units; A','Requires caster standing in mapped traversable water. M36 Water; after positive damage remove up to 8 MP from each target. No MP recovery.','vik','Water-only wave with MP depletion')],
passives:[
P('Sea Legs','Support','Ignore forced tile displacement. Does not stop Immobilize, Slow, terrain harm, or grant water traversal.','vik','Original stability trait for a seafaring raider'),
P('Heavy Grip','Support','Physical HP damage dealt ×1.15 with an axe. Does not strengthen Thunder or Tsunami.','vik','Original axe mastery; not a copy of one-handed Doublehand'),
P('Absorb Damage','Reaction','After surviving positive enemy HP damage, 35% activation: recover 10% of actual HP lost. Does not reverse lethal hits or trigger from HP costs.','vik','Damage recovery; a chance and lockout are added here','Adaptation'),
P('Gil Snapper','Reaction','After surviving an enemy critical physical hit, 35% activation: gain floor(0.5 × actual HP lost) gil, capped at 50 per battle per unit. No cost to the attacker\'s inventory.','vik','Gil after a critical hit; payout and battle cap are ours','Adaptation')],
combo:'Tempest Combo',weapons:'axe',category:'Axe',items:['Storm Axe','Raider Axe','Plunder Axe','Warcaller Axe','Squall Axe','Pillage Axe','Thunderhead Axe','Tidal Axe'],
build:'Axes provide ordinary offense, thunder provides magical coverage, and theft supplies utility. Water access constrains Tsunami. Moderate magic growth supports the actual spells without making Viking a superior Black Mage. No new forced-targeting AI system is implied.'
},
{
id:'GEO',name:'Geomancer',race:'Nu Mou',command:'Geomancy',ref:'geo',
identity:'A reader of the living landscape. FFT Geomancy supplies elemental damage and associated ailments, with the caster\'s terrain determining access. Rods and stronger magic growth are our Nu Mou adaptation of FFT\'s more martial Geomancer.',
rules:'No weapon required. Nature techniques use Magic Power and Magic Resistance but are not incanted spells: Silence, Reflect, Return Magic, and Doublecast do not apply. Except Wind Slash, each action requires its listed caster terrain. Every damage action targets an r3 center with a cross area, any units except the caster, using A then S ×0.35 for its optional ailment after positive damage. Terrain names are design groups to map to real tile IDs, not artwork detection.',
actions:[
A('Wind Slash','0 MP','Any caster terrain; standard Geomancy area','M16 Wind. On constructed/book/metal/tree/moss terrain, also attempt Disable; elsewhere no ailment. Always available after learning as an explicit fallback adaptation of FFT\'s terrain-limited ability.','geo','Wind and Disable; fallback access is our change'),
A('Sinkhole','0 MP','Soil, road, wasteland, sand; standard area','M20 non-elemental plus Immobilize attempt. Sand is added to its terrain family for this map set.','geo','Ground gives way; immobilization'),
A('Tanglevine','0 MP','Grass or undergrowth; standard area','M20 non-elemental plus Stop attempt.','geo','Vegetation arrests movement'),
A('Torrent','0 MP','Traversable water or wetland; standard area','M24 Water plus Toad attempt. Wetlands are added to the source\'s water family.','geo','Water and transformation'),
A('Tremor','0 MP','Rock, gravel, or stone flooring; standard area','M24 Earth plus Confuse attempt. Our rock group also covers built stone surfaces.','geo','Earth disturbance and confusion'),
A('Will-o\'-the-Wisp','0 MP','Wooden floor, deck, stairs, or carpet; standard area','M24 Fire plus Sleep attempt.','geo','Indoor spirit flame and sleep'),
A('Snowstorm','0 MP','Snow or ice; standard area','M28 Ice plus Silence attempt.','geo','Cold and silence'),
A('Magma Surge','0 MP','Volcanic/hot ground; standard area','M36 Fire. The source\'s instant-KO rider is omitted, not reassigned to another status.','geo','Volcanic eruption')],
passives:[
P('Terrain Lore','Support','Geomancy HP damage ×1.15 on the action\'s native terrain only; Wind Slash receives the bonus only on its listed native group. No accuracy or ailment bonus.','geo','Original strengthening of environmental attunement'),
P('Surefoot','Support','Jump +1. Does not grant flight or permission to occupy an impassable tile.','geo','Original modest traversal trait inspired by Geomancer terrain movement'),
P('Stone Skin','Reaction','After surviving enemy physical HP damage while on mapped rock/stone terrain, 35% activation: apply Protect.','geo','Original terrain-bound earthen defense'),
P('Nature\'s Wrath','Reaction','After surviving an enemy HP-damage action, 30% activation: use the highest-AP learned Geomancy action valid on the caster\'s current tile against that attacker alone at r3. Use M12 with that action\'s element, A accuracy, no ailment or Terrain Lore bonus. No valid learned action means no counter.','geo','Counter with the current terrain\'s power','Adaptation')],
combo:'Gaia Combo',weapons:'rod or mace',category:'Rod',items:['Zephyr Rod','Soil Rod','Root Rod','River Rod','Cairn Rod','Wisp Rod','Rime Rod','Magma Rod'],
build:'Low-power, MP-free nature effects reward position and leave MP for a secondary magic set. Terrain limits most of the repertoire; Wind Slash is only a modest safety net. Float or flight disables terrain-specific powers and bonuses, while fallback Wind Slash remains possible. Unknown terrain permits only fallback Wind Slash until explicitly mapped.'
},
{
id:'CHM',name:'Chemist',race:'Nu Mou and Moogle',command:'Items',ref:'chm',
identity:'An expert in medicines, thrown restoratives, and emergency treatment. FFT item handling is the primary model; FFV Pharmacology informs the optional potency support. This replaces the unsourced eye-drop flash bomb and multi-target Phoenix mixture.',
rules:'All eight actions need no weapon, cost 0 MP, work while Silenced, and consume exactly one named item. Range is r4, one ally or self, Sure; Phoenix Down targets a KO ally. Use the verified vanilla USA item\'s healing amount, revival fraction, cure list, and immunity rules rather than inventing new potion contents. These are separate AP-learned ranged applications; ordinary Item access remains unchanged. For this draft the new restorative actions accept non-undead allies only. No Reflect, Return Magic, or Doublecast.',
actions:[
A('Potion','1 Potion','r4, one ally or self; Sure','Apply the vanilla Potion effect.','chm','Basic restorative'),
A('Antidote','1 Antidote','r4, one ally or self; Sure','Apply the vanilla Antidote cure.','chm','Poison treatment'),
A('Phoenix Down','1 Phoenix Down','r4, one KO ally; Sure','Apply the vanilla Phoenix Down revival, minimum 1 HP.','chm','Item-based revival'),
A('Hi-Potion','1 Hi-Potion','r4, one ally or self; Sure','Apply the vanilla Hi-Potion effect.','chm','Stronger restorative'),
A('Eye Drops','1 Eye Drops','r4, one ally or self; Sure','Apply the vanilla Eye Drops cure. It treats blindness rather than causing it.','chm','Blindness treatment'),
A('Ether','1 Ether','r4, one ally or self; Sure','Apply the vanilla Ether MP recovery.','chm','MP restorative'),
A('Cureall','1 Cureall','r4, one ally or self; Sure','Apply the vanilla Cureall cure list; additionally clear our new harmful Polka, Heathen Frolic, and Exposed modifiers. Does not remove Last Resort\'s drawback separately from its benefit.','chm','FFT Remedy role using the actual FFTA consumable Cureall'),
A('X-Potion','1 X-Potion','r4, one ally or self; Sure','Apply the vanilla X-Potion effect.','chm','High-grade restorative')],
passives:[
P('Pharmacology','Support','HP recovery from the three Chemist potion actions ×1.25, rounded down and capped at missing HP. Does not change ordinary Item, revival, Ether, reactions, or cure lists.','chm5','Enhanced medicine potency; narrower and weaker than FFV','Adaptation'),
P('Long Throw','Support','Range of these eight Chemist actions +1, to r5. Does not affect ordinary Item, attacks, or other jobs.','chm','Original improvement to the adapted ranged-item command'),
P('Auto-Potion','Reaction','After surviving enemy HP damage at 30% HP or below, 50% activation: consume one Potion and apply its vanilla recovery to self. Never substitute Hi-Potion or X-Potion. Requires stock; Pharmacology does not apply.','chm','Automatic inventory-funded treatment; selection and threshold adapted','Adaptation'),
P('Auto-Cureall','Reaction','After surviving an enemy action that inflicted a Cureall-curable ailment, 35% activation: consume one Cureall and apply its cure to self. Requires stock and ability to react; cannot rescue KO or bypass reaction-blocking statuses.','chm','Original extension of emergency item use; no free magical regeneration')],
combo:'Flask Combo',weapons:'knife or mace',category:'Knife',items:['Tonic Knife','Antidote Knife','Phoenix Knife','High Tonic Knife','Clear Eye Knife','Ether Knife','Remedy Knife','Restorer Knife'],
build:'Available without prerequisites for both races. Ranged reliable recovery is purchased with inventory and gil, while Pharmacology competes with additional throw range. Neither race needs White Mage access to use it. Mixtures could be a future FFV-inspired extension, but no invented recipe is presented as established lore.'
},
{
id:'BRD',name:'Bard',race:'Moogle',command:'Song',ref:'brd',
identity:'A traveling musician following Hurdy\'s FFTA2 model: bolster companions, restore them, and repel undead. The shared names Battle Chant and Magickal Refrain use their A2 defensive roles, not their different FFT offensive roles.',
rules:'Songs require a primary instrument and are blocked by Silence; no Reflect, Return Magic, or Doublecast. Hide is a nonmagical self action and is the exception: it needs neither instrument nor voice. Songs resolve once using an action, not as perpetual auras. An actual MP song is included; the misnamed healing Finale is removed.',
actions:[
A('Soul Etude','8 MP','r3, one ally or self; Sure','Heal 20% target max HP, capped at 100; remove Poison, Blind, Silence, and Confuse. Cannot sing it while already Silenced.','brd','Healing plus cleansing'),
A('Battle Chant','8 MP','Self cross, allies including self; Sure','Apply Protect, our representation of A2 defense enhancement.','brd','Defense song'),
A('Magickal Refrain','8 MP','Self cross, allies including self; Sure','Apply Shell, our representation of A2 resistance enhancement.','brd','Magical defense song'),
A('Requiem','8 MP','r3, one undead enemy; A','M32 Holy; invalid against living targets. No instant KO or resurrection suppression.','brd','Anti-undead song'),
A('Angelsong','10 MP','Self cross, allies including self; Sure','Apply Regen.','brd','Regeneration song'),
A('Hide','0 MP','Self; Sure','Apply the original Invisible status with its ordinary break/removal rules. Does not give movement or an extra action.','brd','Self-concealment'),
A('Magick Ballad','6 MP','r3, one ally other than caster; Sure','Restore 8 MP, capped at missing MP. Self-targeting excluded; any remaining two-Bard economy must be evaluated in balance testing.','brd','MP-restoring song'),
A('Nameless Song','16 MP','Self cross, allies including self; Sure','For each ally choose uniformly from Protect, Shell, Regen, and Haste, then apply that status. No reroll for existing status or immunity. Preview shows the four possibilities.','brd','Random beneficial song')],
passives:[
P('Resonance','Support','Single-target Song range +1. No extra area radius; no effect on Hide or self-centered songs.','brd','Original instrumental projection'),
P('Clear Voice','Support','Reduce incoming Silence S-check success by 15 percentage points, minimum 0. Shares the resistance family with War Cry; use the stronger applicable reduction, not both. No protection from non-S effects.','brd','Original resistance to interruption; no immunity or self-cleansing song'),
P('Magick Boost','Reaction','After surviving enemy magical HP damage, 35% activation: magical HP damage dealt ×1.15, T2. Does not strengthen fixed or percent healing.','brd','FFT Bard\'s reactive magical growth made temporary','Adaptation'),
P('Encore','Reaction','After surviving enemy physical HP damage, 35% activation: with an instrument and while not Silenced, recover 5% max HP through a brief reprise. No cleanse or revival.','brd','Original reduced self-reprise of Soul Etude')],
combo:'Chorus Combo',weapons:'instrument',category:'Instrument',items:['Etude Pipe','Battle Pipe','Refrain Pipe','Requiem Pipe','Angel Pipe','Traveler Pipe','Ballad Pipe','Nameless Pipe'],
build:'Support is mostly dependable, with Nameless Song as an explicitly random option. Item support through secondary Chemist works while Silenced. Moogle White Magic is not available. Low physical offense, nearby group positioning, and voice dependence constrain the job.'
},
{
id:'DNC',name:'Dancer',race:'Viera',command:'Dance',ref:'dnc',
identity:'A nimble performer who weakens enemies through rhythm and steals vitality. The repertoire follows FFT/FFTA2 disruption, with FFV\'s recognizable Sword Dance as its weapon finisher. Healing dances do exist elsewhere in FF; this particular job deliberately specializes in enemy disruption.',
rules:'Dance is performance, not incantation: usable while Silenced; no Reflect, Return Magic, or Doublecast. Sword Dance requires a primary knife or rapier; other actions do not. Dances resolve once within tactical range, rather than repeatedly affecting the whole map. They do not advance, reset, or refund turns.',
actions:[
A('Mincing Minuet','4 MP','r3 center, cross, enemies; A','Physical damage using a virtual non-elemental weapon of Attack 12 in the normal P reference. Actual weapon Attack, element, and procs do not enter this formula.','dnc','Area HP-damaging dance'),
A('Witch Hunt','6 MP','r3 center, cross, enemies; A','Remove 6 MP from each successful target, capped at current MP. No recovery to dancer.','dnc','MP-damaging dance'),
A('Slow Dance','8 MP','r3, one enemy; S','Apply Slow. A timed FFTA status replaces the source\'s direct Speed reduction.','dnc','Disrupt enemy tempo'),
A('Polka','8 MP','r3, one enemy; S','T2: physical HP damage dealt ×0.85.','dnc','Weaken physical offense'),
A('Heathen Frolic','8 MP','r3, one enemy; S','T2: magical HP damage dealt ×0.85. Does not weaken item effects, fixed damage, or healing.','dnc','Weaken magical offense'),
A('Forbidden Dance','12 MP','r3 center, cross, enemies; S','For each target choose uniformly from Blind, Silence, Poison, and Confuse; then make its S check. Do not reroll immunities. No Petrify, KO, or turn reset in the pool.','dnc','Random ailments with a restricted pool'),
A('Jitterbug','10 MP','r2, one enemy; A','0.75P using a virtual non-elemental weapon of Attack 18. Drain 50% of actual HP removed, capped at 15% user max HP. Undead reverse drain.','dnc','HP-draining dance'),
A('Sword Dance','16 MP','r1, one enemy; A','1.60P weapon-elemental, one hit. Unlike FFV\'s random Dance result, select it directly after learning and pay MP.','dnc','FFV physical dance finisher')],
passives:[
P('Grace','Support','Base Evade +5 before normal facing, equipment, and caps. Not a universal five-percentage-point dodge bonus.','dnc','Original evasive footwork for this Viera adaptation'),
P('Light Foot','Support','Move +1. No second move, flight, terrain immunity, or free ability slot.','dnc','Original modest mobility instead of importing FFT Fly'),
P('Fury','Reaction','After surviving enemy physical HP damage, 35% activation: physical HP damage dealt ×1.15, T2. No permanent stat growth.','dnc','FFT Dancer\'s reactive offense made temporary','Adaptation'),
P('Counter Rhythm','Reaction','After surviving adjacent enemy physical HP damage, 30% activation: attempt Slow on that attacker with S.','dnc','Original reactive echo of Slow Dance')],
combo:'Waltz Combo',weapons:'knife or rapier',category:'Rapier',items:['Minuet Foil','Witch Foil','Tempo Foil','Polka Foil','Frolic Foil','Forbidden Foil','Jitterbug Foil','Danceblade'],
build:'Physical growth supports its damaging dances while status actions create openings. Spirit Magic adds other debuffs; White Magic remains an optional separate healing set. Fragility, enemy immunity, and MP costs constrain repeated disruption.'
},
{
id:'MYK',name:'Mystic Knight',race:'Viera',command:'Spellblade',ref:'myk',
identity:'An FFV-style enchanted-weapon specialist: choose an elemental or status enchantment, then exploit it through sustained sword attacks. This replaces disposable sigils and invented finishers. Runic belongs to a different FF tradition and no spell-absorption kit is implied here.',
rules:'All eight actions target self, Sure, require a primary rapier or saber, and are blocked by Silence. One enchantment lasts until replaced, Dispel, KO, Petrify, loss/change of the primary weapon, job change, or battle end. Ordinary attacks do not consume it. Silence after preparation prevents re-enchanting but does not erase the existing effect or stop Fight. Only the primary strike of ordinary Fight benefits; other weapon strikes, secondary techniques, reactions, and combos do not. Enchantments replace the primary weapon\'s element and status proc, rather than stacking an item proc with them. No Reflect, Return Magic, or Doublecast.',
actions:[
A('Fire Spellblade','6 MP','Self; Sure','Primary Fight strike becomes Fire-elemental. No separate spell hit or damage bonus beyond elemental interaction.','spell','Fire enchantment'),
A('Blizzard Spellblade','6 MP','Self; Sure','Primary Fight strike becomes Ice-elemental.','spell','Ice enchantment'),
A('Thunder Spellblade','6 MP','Self; Sure','Primary Fight strike becomes Lightning-elemental.','spell','Lightning enchantment'),
A('Poison Spellblade','6 MP','Self; Sure','Primary Fight strike becomes non-elemental; after positive damage attempt Poison with S ×0.5.','spell','Poison enchantment'),
A('Sleep Spellblade','8 MP','Self; Sure','Primary Fight strike becomes non-elemental; after positive damage attempt Sleep with S ×0.5. Resolve the sleep after damage, so the same hit does not immediately wake the target.','spell','Sleep enchantment'),
A('Silence Spellblade','8 MP','Self; Sure','Primary Fight strike becomes non-elemental; after positive damage attempt Silence with S ×0.5.','spell','Silence enchantment'),
A('Drain Spellblade','12 MP','Self; Sure','Primary Fight strike becomes non-elemental; heal 20% of actual HP removed, capped at 8% user max HP per action. Undead reverse drain.','spell','Draining enchantment'),
A('Flare Spellblade','24 MP','Self; Sure','Primary Fight strike becomes non-elemental and uses 75% of the target\'s effective Weapon Defense in its damage calculation. No extra damage multiplier. This is a much smaller defense bypass than FFV.','spell','Non-elemental defense-piercing enchantment')],
passives:[
P('Spellblade Focus','Support','Enchanted primary Fight strikes deal physical HP damage ×1.10. No benefit to secondary attacks, healing, counters, or combos.','myk','Original weapon-enchantment proficiency'),
P('Warding Steel','Support','Magical HP damage received ×0.85 while a rapier or saber is primary. Does not absorb, intercept, or convert a spell.','myk','Original passive expression of the job\'s magical defenses'),
P('Magic Shell','Reaction','After surviving enemy HP damage at 30% max HP or less, 50% activation: apply Shell. Does not reduce the triggering hit; not blocked merely by Silence.','myk','FFV low-health Shell placed in FFTA\'s reaction slot','Adaptation'),
P('Spell Parry','Reaction','Requires a qualifying equipped weapon and active enchantment. 25% pre-hit activation: incoming enemy physical HP damage ×0.5 for that action. Does not consume the enchantment.','myk','Original magically reinforced sword guard')],
combo:'Spellblade Combo',weapons:'rapier or saber',category:'Saber',items:['Ember Saber','Rime Saber','Spark Saber','Venom Saber','Dream Saber','Hush Saber','Siphon Saber','Flare Saber'],
build:'A preparation turn pays off across later Fight actions. Existing Gladiator elemental attacks remain immediate; this job cannot automatically imbue them. Balanced physical development matters more than Magic Power because the enchantments modify weapon attacks. Break/Petrify and an unrestricted status-on-hit guarantee are deliberately absent.'
}
];

const axeJobs = [
{id:'SLD-AX',name:'Soldier',race:'Human',command:'Battle Tech',
actions:[
A('Chop','0 MP','r1, one enemy; A','1.05P. Basic weapon-elemental strike.','ffta','Original straightforward addition to Soldier\'s martial toolkit','Original extension'),
A('Tomahawk','4 MP','r3, one enemy; A','0.70P weapon-elemental thrown-axe strike. Requires clear line of sight. Does not consume or unequip the axe and does not pull the target.','axe14','Marauder ranged axe attack; no MMO enmity','Adaptation'),
A('Overpower','6 MP','Frontal arc, any units; A','0.75P weapon-elemental per target. Our directional area and friendly fire adapt the axe area-attack concept. No enmity system.','axe14','Marauder area axe attack','Adaptation'),
A('Shatter Guard','8 MP','r1, one enemy; A','0.85P weapon-elemental; after positive damage remove Protect only. No item destruction or permanent Defense loss.','ffta','Original guard-breaking extension of Soldier\'s weakening techniques','Original extension')],
passives:[P('Axe Grip','Support','Physical HP damage dealt ×1.10 while an axe is primary.','ffta','Original weapon training added to Soldier'),P('Haft Guard','Reaction','Requires axe. 25% pre-hit activation: enemy physical HP damage ×0.75 for that action.','ffta','Original mundane defense using the axe haft')],
aps:[100,150,200,300],paps:[200,250],items:['Recruit Axe','Throwing Axe','Field Axe','Breaching Axe']},
{id:'GLD-AX',name:'Gladiator',race:'Bangaa',command:'Spellblade Tech',
actions:[
A('Armor Splitter','8 MP','r1, one enemy; A','1.00P weapon-elemental using 75% of target effective Weapon Defense for this hit. No lasting debuff or destroyed armor.','ffta','Original heavy-weapon penetration added to Gladiator\'s offensive kit','Original extension'),
A('Reaping Arc','12 MP','Frontal arc, any units; A','0.95P weapon-elemental per target. A directional alternative to existing Wild Swing, not a claim that Gladiator lacked area attacks.','ffta','Original positional variant alongside Wild Swing','Original extension'),
A('Executioner','12 MP','r1, one enemy; A','1.20P weapon-elemental; 1.60P if target is at or below 35% max HP at execution. No instant KO.','ffta','Original arena finisher; no claim of a canonical FFTA move','Original extension'),
A('Fell Cleave','16 MP','r1, one enemy; A','1.80P weapon-elemental. Apply Exposed before the hit, even on a miss: physical HP damage received ×1.20 until start of next user turn.','axe14','Warrior heavy axe strike; MP and Exposed replace MMO resources','Adaptation')],
passives:[P('Follow Through','Support','Physical HP damage dealt ×1.15 with an axe if user voluntarily moved at least one tile earlier this turn. Forced movement does not count.','ffta','Original momentum-based axe offense'),P('Axe Reprisal','Reaction','Requires axe. After surviving adjacent enemy physical HP damage, 30% activation: counter once for 0.70P, A accuracy. No proc or critical.','ffta','Original axe counter; compare with existing Strikeback rather than claiming a new role')],
aps:[200,250,300,400],paps:[350,350],items:['Bearded Axe','Arena Axe',"Headsman's Axe",'Titan Axe']}
];

const ap = [100,150,200,200,250,300,300,400];
const rows = [];
for (const j of [...jobs,...axeJobs]) {
  j.actions.forEach((a,i)=>{a.id=`${j.id}-A${i+1}`;a.ap=(j.aps??ap)[i];a.type='Action';rows.push({...a,job:j.name,previous:originalNames[a.id]??null});});
  const counts={Support:0,Reaction:0};
  j.passives.forEach((p,i)=>{const n=++counts[p.type];p.id=`${j.id}-${p.type[0]}${n}`;p.ap=j.paps?.[i]??(p.type==='Support'?[200,350]:[250,350])[n-1];rows.push({...p,job:j.name,previous:originalNames[p.id]??null});});
  if(j.combo){const c={id:`${j.id}-C1`,name:j.combo,job:j.name,type:'Combo',ap:100,kind:'FFTA integration',ref:'manual',anchor:'Original job-specific label for vanilla Judge Point combo participation',effect:`Requires ${j.weapons}; range 1. Standard vanilla combo. No extra element, status, healing, drain, critical, enchantment, terrain, or support rider.`,previous:originalNames[`${j.id}-C1`]??null};j.c=c;rows.push(c);}
}
const link = key=>`[${refs[key][0]}][${key}]`;
const origin = a => `${a.kind}: ${a.anchor}. [Source][${a.ref}]`;
const table = j => `| ID / action | AP | Cost | Target / hit | Proposed effect | Lineage |\n|---|---:|---|---|---|---|\n`+j.actions.map(a=>`| ${a.id} ${a.name} | ${a.ap} | ${a.cost} | ${a.target} | ${a.effect} | ${origin(a)} |`).join('\n')+'\n\n'+`| ID / passive | Type | AP | Effect while equipped | Lineage |\n|---|---|---:|---|---|\n`+j.passives.map(p=>`| ${p.id} ${p.name} | ${p.type} | ${p.ap} | ${p.effect} | ${origin(p)} |`).join('\n');
const sourceBlock = '\n'+Object.entries(refs).map(([k,[,url]])=>`[${k}]: ${url}`).join('\n')+'\n';

// Preserve the agreed roster and ten stat profiles, with thematic corrections below.
let roster=oldSpec.slice(oldSpec.indexOf('## 1.'),oldSpec.indexOf('## 2.'));
let stats=oldSpec.slice(oldSpec.indexOf('## 3.'),oldSpec.indexOf('## 4.'));
stats=stats.replace('| Human Samurai | 7.0 | 1.8 | 8.8 | 8.0 | 6.2 | 7.2 | 1.5 |','| Human Samurai | 7.0 | 3.0 | 8.0 | 8.0 | 8.2 | 7.2 | 1.4 |')
.replace('| Human Samurai | 36 | 18 | 88 | 80 | 62 | 72 | 108 |','| Human Samurai | 36 | 30 | 80 | 80 | 82 | 72 | 106 |')
.replace('| Bangaa Viking | 9.2 | 1.2 | 8.8 | 8.8 | 5.8 | 6.4 | 1.0 |','| Bangaa Viking | 8.8 | 2.8 | 8.4 | 8.2 | 7.6 | 6.8 | 1.0 |')
.replace('| Bangaa Viking | 46 | 12 | 88 | 88 | 58 | 64 | 98 |','| Bangaa Viking | 44 | 28 | 84 | 82 | 76 | 68 | 98 |')
.replace('| Nu Mou Geomancer | 6.6 | 4.0 | 5.8 | 7.0 | 9.0 | 8.6 | 1.0 |','| Nu Mou Geomancer | 6.6 | 3.0 | 5.8 | 7.0 | 8.6 | 8.6 | 1.0 |')
.replace('| Nu Mou Geomancer | 33 | 40 | 58 | 70 | 90 | 86 | 97 |','| Nu Mou Geomancer | 33 | 30 | 58 | 70 | 86 | 86 | 97 |')
.replace('| Viera Mystic Knight | 6.6 | 3.2 | 8.0 | 7.4 | 8.0 | 8.2 | 1.4 |','| Viera Mystic Knight | 6.8 | 3.0 | 8.2 | 7.6 | 7.2 | 8.2 | 1.4 |')
.replace('| Viera Mystic Knight | 33 | 32 | 80 | 74 | 80 | 82 | 106 |','| Viera Mystic Knight | 34 | 30 | 82 | 76 | 72 | 82 | 106 |')
.replace('| Samurai | 4 | 3 | 50 | Katanas | Clothing/light armor; hats or helmets | No |','| Samurai | 4 | 3 | 50 | Katanas | Clothing, heavy armor, or robes; hats or helmets | No |')
.replace('| Viking | 3 | 2 | 40 | Broadswords | Clothing or heavy armor; hats or helmets | No |','| Viking | 3 | 2 | 40 | New two-handed axes | Clothing or heavy armor; hats or helmets | No |')
.replace('| Mystic Knight | 4 | 2 | 45 | Rapiers, sabers | Clothing or robes; hats | Yes |','| Mystic Knight | 4 | 2 | 45 | Rapiers, sabers | Clothing or heavy armor; hats or helmets | Yes |');
stats=stats.slice(0,stats.includes('Use existing item categories')?stats.indexOf('Use existing item categories'):stats.indexOf('Thematic growth revisions'))+`Thematic growth revisions: Samurai now supports spirit magic as well as swordplay; Viking has MP and magic development for real storm spells; Geomancer no longer needs high MP growth for its own actions; Mystic Knight emphasizes weapon combat over spell damage. These figures and racial adaptations are balance proposals, not canonical stats. Soldier and Gladiator retain every original growth and armor permission.\n\nAll categories are vanilla except the explicitly added Axe family. Racial armor animations and permission fields need validation. Samurai teaching weapons are new spirit-channeling variants, not edits to existing named katanas.\n\n`;

const rules=`## 2. Shared rules and what is an adaptation

**Audit scope:** all 116 ability entries: 64 new-job actions, 32 new-job supports/reactions, 8 combo entries, and 12 Soldier/Gladiator axe additions. Every entry has a source and a lineage label. This counts design lessons, not necessarily 116 new engine records: familiar effects and existing abilities should be reused where their behavior is identical. [The audit](JOB-THEME-AUDIT.md) maps every old entry to its replacement.

- **Adaptation** uses a documented Final Fantasy ability and preserves its defining role, while changing costs, range, success rate, or other specified details for FFTA.
- **Original extension** is our invention, justified by that job's established role. Its linked source supports the underlying identity, not the existence of our invented name or exact effect.
- **FFTA integration** means a new job's ordinary combo entry. None of these combo names is claimed as an imported signature ability.

All numerical values, new progression gates, teaching items, racial assignments, and balance limits are ours. A familiar name is not enough: element, target, resource, and effect must match its cited interpretation or the change must be explicit. The reference versions are FFT/War of the Lions, FFV, FFTA2, and specifically identified MMO abilities; these games do not have one universal identical job implementation. Community references document released games, and are not official endorsement of this mod. Fan-made job concepts are not evidence of canon.

### Learning and equipment

Each new job has 8 A, 2 S, 2 R, and 1 combo lesson. Preserve normal AP/equipment learning, one primary and one secondary action set, one equipped support, one reaction, and one combo. There are no free new passives or extra movement slots. Reactions and supports require equipping even when innate in their source game. Shared jobs have identical skills and separate racial growths. New-job equipment permission is not inherited by mastering the job. Main-job eligibility and existing story-character restrictions remain intact. Job switching does not recalculate accumulated stats. The new actions count for their owning job's mastered-action gates; supports/reactions do not. [Nintendo manual][manual].

### Formula and targeting notation

**P** is the damage reference for one primary-weapon physical hit, including applicable defenses. 1.30P is a damage multiplier, not +30% Attack. New A-abilities do not call Fight, cannot crit, do not copy weapon status procs, and never use a second weapon. Damage described as weapon-elemental uses the primary weapon's element. Explicit virtual-weapon dance formulas replace actual weapon Attack and element. **M24** means a proposed magical-damage routine with power 24, caster Magic Power, and target Magic Resistance; it is not a verified ROM field mapping. **A** is an ordinary attack-style accuracy check; **S** is the normal status check with immunity; **Sure** is a legal willing-target effect. An S multiplier scales the final ordinary success chance. Buff-based percentage-point reductions apply afterward, once, floor 0. Damage formula class does not itself determine Silence or reflection; each command specifies those properties. Exact handlers and previews require mapping against [original mechanics research][mechanics].

**rN** is Manhattan tile distance; r1 excludes diagonals. **Cross** means center plus four orthogonal neighbors. **Self cross** centers it on the caster. **Line N** is a chosen cardinal line of N tiles, excluding caster; it stops at impassable terrain. **Any** includes friendly fire. Single-target range has height limit 3; melee limit 2; cross neighbors must be within 2 height of center and line targets within 2 of caster. Projectiles require line of sight; songs, dances, and terrain effects do not. Show all affected tiles and actual chances before commitment. All new actions resolve immediately and use one ordinary action; none grants movement or another turn.

### Duration, recovery, and resources

Use vanilla durations, immunity, removal, and stacking for named existing statuses. **T2** is a custom effect expiring after the target finishes its second subsequent turn, excluding the application turn. Reapplication refreshes, never stacks. KO, Petrify, battle end, and job change clear custom effects; Dispel removes beneficial effects and ordinary broad remedies also clear our harmful modifiers. Last Resort is indivisible: remove both its benefit and drawback together. Exposed uses its expressly shorter timer. Spellblade instead persists for the expressly listed duration in its section.

Distinct modifiers multiply once; round down only after combining them. War Cry and Clear Voice use only the stronger applicable status-resistance reduction. Same-name modifiers from multiple units do not stack. Existing statuses and supports retain ordinary behavior.

New restorative actions target non-undead allies, with recovery capped by missing HP/MP. Original commands keep their undead interactions. Revives target eligible KO allies only, never removed or permanently lost units. HP costs are percentages of maximum HP, rounded up, minimum 1, paid once per action and never allowed to reduce user below 1 HP. Costs are paid after validation and before hit checks, even if the action misses. HP costs are not damage and trigger no reactions.

HP drain uses actual positive HP removed, limited by target pre-hit HP and each skill's cap. No healing from allies, overkill, absorption, or immunity. Undead reverse the recovery into user damage, which can KO but cannot trigger reactions. MP drain uses actual MP removed, no overdraw; against undead its attempted user recovery becomes MP loss, capped at user current MP. No ability generates JP. MP supports affect MP costs through the original system, not item counts or HP costs.

Consumables must exist in inventory and be deducted once atomically after validation. Never substitute mission items or silently use rarer medicine. New theft reuses original eligibility, target inventory depletion, immunity, and payout restrictions; already-stolen items cannot be stolen again. Damage and theft are separate checks, not one guaranteed steal.

### Reactions and command interactions

All new reactions have their listed activation chance and one activation opportunity per incoming enemy action, locked until the defender's next turn. No self/ally damage, costs, poison ticks, reaction, or combo triggers; no counter chains. Defensive reactions act before damage; recovery/counters require survival and ordinary ability to react. Stated weapons, range, terrain, and voice requirements also apply. A reaction that cannot find a legal target fails without retargeting.

Original Double Sword/Fight remains intact; new attacks use one primary weapon. Spellblade modifies only the primary Fight strike, replaces that strike's ordinary proc, and cannot convert Healer into damaging/draining attacks. No new A-ability is added to Doublecast eligibility. Original eligible magic still works as before. Combo entries use the vanilla Judge Point system and have no custom combat riders. New effects receive applicable existing laws, including elemental, item, theft, healing, and equipment restrictions; a new command name cannot create an exemption.

`;

const equipment=`## 12. Teaching equipment and availability

Eight new teaching weapons per job make 64, plus eight Soldier/Gladiator teaching axes make **72 proposed items**. Existing item stats and lessons stay intact. W1–W8 teach A1–A8 respectively. Additional lessons: W2 teaches S1, W3 combo, W4 R1, W5 S2, W6 R2. Each job has 1,900 action AP, 550 support AP, 600 reaction AP, and 100 combo AP: 3,150 total lesson AP, with simultaneous lessons progressing normally.

| Job / category | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 |
|---|---|---|---|---|---|---|---|---|
${jobs.map(j=>`| ${j.name} / ${j.category} | ${j.items.join(' | ')} |`).join('\n')}

These are new proposed item names. An Echo katana teaches the named sword spirit without changing the vanilla weapon bearing a similar name. A teaching weapon's name never grants an unlisted proc or power. Chemist uses the actual FFTA consumable **Cureall**, not an assumed inventory item named Remedy. [FFTA item reference][items].

Weapon Attack targets, W1–W8: Samurai/Dark Knight/Viking/Mystic Knight 18/22/26/30/34/38/42/46; Dancer/Chemist 14/17/20/23/26/29/32/35; Bard 12/15/18/21/24/27/30/33; Geomancer 10/12/14/16/18/20/22/24 with Magic Power bonuses 0/2/4/6/8/10/12/14. Other bonuses are zero; no innate element, proc, or automatic status. Categories use original handedness except new axes, which are two-handed and exclude shields/second weapons.

Prices: 300/600/1,000/1,600/2,400/3,400/4,800/6,500 gil. W1–2 are initial shop-tier stock; W3–4 first expansion; W5–6 second; W7–8 last pre-final-story expansion. These anchors require real story-flag mapping. Gear may be purchased before a job unlocks, but only an eligible active job learns its lessons. All gear must remain repeatably obtainable. Chemist's later medicine lessons must coincide with repeatable ingredient access; no early X-Potion availability is assumed.

Viking can equip all new axes, but only learns its Reaving lessons on Viking teaching axes. Soldier and Gladiator likewise learn only their own documented lessons. See [the axe addendum](AXE-SKILL-EXPANSION.md) for their eight weapons and twelve entries. Viking axe access is now part of this revised design; Warrior does not automatically gain axe access.

## 13. Implementation, balance, and acceptance

This is a source-audited design, **not an implemented or balance-tested patch**. The roster, progression, job identity, ability behavior, provisional growths, equipment, and learning scheme are specified; storage capacity and effect support remain unproven. FFTA is the clean base, with no third-party overhaul. Existing abilities, growths, stories, laws, missions, and recruitment rules stay intact except the selected additive Soldier/Gladiator changes. Squire and Sentinel remain rejected; Green Mage is only a candidate.

Before full implementation, prove a new job record, one ability, teaching equipment, AP mastery, and ordinary save/load without occupying existing records. Count actual new records only after identifying safely reusable effects. Validate ten race/job implementations, ability-list lengths, mastery storage, icons, sprites, animation states, equipment categories, shops, and law dispatch. New Axe permission must be represented across all three intended jobs and all relevant interfaces, not just assigned a spare numeric type.

Terrain requires an audited tile-ID map across campaign battles. Unknown tiles allow only Wind Slash's weak fallback; they cannot fabricate lava or water access. Check whether rare terrain makes certain Geomancy lessons too situational. Tsunami must not grant water movement. Custom defense bypass must operate at the stated formula stage, without accidentally removing Protect or ignoring all defense. Item effects, stealing, Invisible, status cures, and drain reversal require clean-ROM confirmation. Do not claim a direct data-only implementation until proven.

Law integration must check effect as well as command: Viking now contains magic and theft, Chemist uses real items, and Spellblade changes effective attack elements. Any command aliases to existing law categories must be mapped and documented per action after investigation. A single blanket Reaving-to-Battle-Tech alias is insufficient. No new law cards or hidden exemptions are proposed.

Meaningful balance cases:

1. Compare matched equipment tiers around levels 10, 25, and 40. Samurai against Fighter/Ninja plus nearby support; Viking against Warrior/Defender and Black Mage damage; Geomancer against Black Mage/Sage; Chemist against ordinary Item/White Mage; Bard and Dancer against other support options; Mystic Knight against Fencer/Red Mage and Gladiator-style immediate attacks.
2. Include setup turns and whole-battle resources. Persistent Flare Spellblade, zero-MP Geomancy, Haste/Regen Masamune, MP songs, drain loops, theft, and Gil Snapper need explicit testing. Thematic correctness does not establish fair numbers.
3. At 200 max HP, Blood Edge costs 20, Abyssal Blade 40, and Unholy Sacrifice 60. Sacrificial Will changes these to 15/30/45. Sanguine Sword removing 40 HP restores 10; removing 200 restores only its 20-HP cap. Check misses, immunity, overkill, undead, and unaffordable costs.
4. Exercise secondary sets, original Double Sword and Doublecast, Healer, damage/status supports, Reflect, Return Magic, all protections, reaction lockouts, direct and area attacks, forced movement, save/reload, and temporarily AI-controlled units. Valid-action generation must respect terrain, weapon, voice, inventory, and HP affordability.
5. Validate T2 at each turn phase; Last Resort's linked drawback; short Exposed; persistent Spellblade replacement/removal; status resistance without stacking; no permanent stat gains from Fury or Magick Boost.
6. Preserve original Soldier/Gladiator moves, including Rush, Wild Swing, Beatdown, elemental attacks, and Strikeback where applicable. New axes are alternatives; Reaping Arc and Axe Reprisal must compete with existing choices, not merely rename them. Test old techniques and combos with new weapons.
7. Full release requires a fresh save, real battles, learning, job changes, ordinary save/load, campaign shop checks, and a reproducible patch from the verified clean ROM. Keep the original play/save files separate. Old-save migration is not promised until proven.

Source references support the lineage column, not the invented balance numbers. [The modding guide](FFTA-MODDING-GUIDE.md) covers tooling and limitations. No ROM has been changed by this revision.
`;

const spec=`# FFTA: eight-job expansion specification

Design version 0.2 — thematic audit, September 13, 2026

**Our expansion of vanilla USA FFTA.** Eight new job concepts across the five original races, plus axe abilities for existing Soldier and Gladiator. This revision replaces the generic v0.1 kits with source-grounded job identities. Start with [the short audit overview](JOB-THEME-AUDIT.md) for what changed, or read the full abilities below. All balance values remain proposals.

`+roster+rules+stats+jobs.map((j,i)=>`## ${i+4}. ${j.name} — ${j.race}

**Command: ${j.command}.** ${j.identity} Main reference: ${link(j.ref)}.

${j.rules}

${table(j)}

**${j.c.id} ${j.c.name} — 100 AP:** ${j.c.effect} ${origin(j.c)}

**Playstyle and limits:** ${j.build}

`).join('')+equipment+sourceBlock;

const axe=`# Axe skills for Soldier and Gladiator

Design version 0.2 — thematic audit, September 13, 2026. Expands vanilla USA FFTA; not implemented.

No Squire or Sentinel, and no Sentinel → Viking branch. Human Soldier remains a starter; Bangaa Gladiator retains its original two-Warrior-action gate. Original job skills, growths, movement, armor, and prerequisites remain. This adds four actions, one support, and one reaction to each existing command set. [The main specification](JOB-CLASS-SPECIFICATION.md) owns shared combat rules and the eight-job roster.

**Theme:** Soldier gains practical axe handling alongside its existing weakening techniques. Gladiator gains arena-style heavy offense alongside its existing elemental attacks. These roles refer to FFTA Soldier/Gladiator, not FFVII SOLDIER or FFXIV's shield-bearing Gladiator. [Original FFTA ability reference][ffta]. Tomahawk, Overpower, and Fell Cleave borrow actual FFXIV axe techniques, with their tactical adaptations explicitly listed; they do not import MMO threat or gauge systems. [Official Warrior guide][axe14].

## Weapon and command rules

Define a real, separate **two-handed Axe family**: ordinary range 1, no shield or second weapon, no inherent armor bypass or random damage. Soldier and Gladiator gain equip permission; the revised Viking also uses this family. Warrior and other jobs do not automatically gain access. Teaching permission remains job-specific even when equipment can be shared.

All twelve entries require a primary axe where their effect specifies it; all eight actions always require one. Keep them inside Soldier **Battle Tech** and Gladiator **Spellblade Tech**, not a third equipped command. Physical effects use P/A from the main specification, work while Silenced, and cannot be Reflected, Returned, or Doublecast. One primary-weapon hit per target, no critical, proc, or second weapon. No action consumes the axe. Mastered actions count toward existing owning-job unlock gates; supports and reactions do not.

**Frontal arc:** choose a cardinal facing; hit the tile directly ahead plus its two diagonal neighbors, within 2 height. Allies can be hit; caster cannot. Preview all tiles. Tomahawk uses the shared ranged projectile rules. The earlier unexplained two-tile Hooking Blow pull is removed.

${axeJobs.map(j=>`## ${j.name} — ${j.race}\n\n${table(j)}\n`).join('\n')}

Exposed is a new harmful modifier ending at the start of the user's next turn, including immediate retaliation before then. It does not stack. KO, Petrify, battle end, or a broad remedy clears it; the action cannot be selected if immunity would cancel its drawback at application. Protect can mitigate the risk through the usual rules. This drawback is our balance addition to Fell Cleave, not a claim about FFXIV.

**Existing-kit check:** Gladiator already has Rush, Wild Swing, Beatdown, and elemental techniques. Reaping Arc changes positioning rather than inventing the job's first area attack; Fell Cleave offers a cost/risk profile rather than presenting heavy damage as a missing identity. Axe Reprisal must be compared with existing Strikeback. Shatter Guard fits Soldier's weakening role; it is an original Protect-breaking move, not the equipment-destroying ability Armor Break. [Original FFTA abilities][ffta].

## Teaching axes

Eight additional items; all non-elemental, with no extra stat bonuses, automatic statuses, or procs. Both existing jobs and Viking can equip them, but only the listed owning job learns the lessons.

| Item | Weapon Attack | Price | Lessons |
|---|---:|---:|---|
| Recruit Axe | 20 | 300 gil | Soldier: Chop |
| Throwing Axe | 24 | 600 gil | Soldier: Tomahawk + Axe Grip |
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
`+sourceBlock;

const overview=`# Job theme audit

September 13, 2026 — completed design review of **all 116 ability entries**, including every active, support, reaction, and combo entry. The current full lists are in [the revised class specification](JOB-CLASS-SPECIFICATION.md) and [the revised axe addendum](AXE-SKILL-EXPANSION.md). These replace v0.1; this is not just a list of suggestions beside an unchanged draft.

## What changed

| Job | Source identity used | Main correction |
|---|---|---|
| Samurai | FFT katana spirits | Named Iaido damage, healing, protection, and blessing techniques; magical growth now supports the kit |
| Dark Knight | FFT: War of the Lions, with named FFXI/XIV additions | HP sacrifice and HP/MP drain; removed the arbitrary binding curse and misleading Blood Price exchange |
| Viking | FFTA2 Seeq Viking, adapted to Bangaa | Real axes, plundering, thunder magic, water-dependent Tsunami; War Cry now resists ailments |
| Geomancer | FFT landscape powers | Terrain now unlocks effects; no generic freely chosen elemental spellbook; explicitly weaker universal Wind Slash fallback |
| Chemist | FFT Items and FFV Pharmacology | Actual consumables, thrown medicine, inventory-funded reactions; removed invented flash/revival recipes and free regeneration |
| Bard | Hurdy in FFTA2 | Recognizable songs, anti-undead Requiem, MP ballad; no unrelated healing ability called Finale |
| Dancer | FFT/FFTA2 disruption, FFV Sword Dance | HP/MP damage, weakened offense, ailments, draining, and a dance finisher |
| Mystic Knight | FFV Spellblade | Sustained elemental/status enchants and low-health Magic Shell; removed Runic absorption implications and disposable-sigil finishers |
| Soldier / Gladiator | Original FFTA roles, with selected FFXIV axe techniques | Practical and heavy martial axe options; accounted for existing Wild Swing/Beatdown/Strikeback rather than claiming their roles were absent |

The full tables explain source-specific distinctions and deliberate changes. For example, the Bard names Battle Chant and Magickal Refrain have different effects in FFT and FFTA2; this design consistently uses the A2 versions. [Bard comparison][brd]. Viking's A2 War Cry is resilience support. [Viking reference][vik]. Spellblade is not Celes-style Runic. [FFV Mystic Knight][myk].

## What this review does and does not establish

Every retained effect now has a thematic rationale tied to a released Final Fantasy job. **Not every ability is an exact canon import.** Original passives and axe extensions are labeled honestly; costs, formulas, caps, AP, durations, and race assignments are our adaptations. The sources establish lineage, not balance or engine feasibility. Community wikis and game guides are identified as such, and MMO techniques use official Square Enix job guides where available. Fan-created tabletop classes and other people's mod moves were not used as canon evidence.

The source-style changes to Samurai, Viking, Geomancer, and Mystic Knight also required updated growths/equipment. Chemist remains the only accepted new starter. No Squire, Sentinel, Green Mage, or new prerequisite has been silently added. There are still eight new job concepts and two new options per race. The user-selected axe direction remains on Soldier and Gladiator; the proposed Viking now shares the real axe family because its prior broadsword placeholder conflicted with its chosen source identity.

## Complete ability crosswalk

“Original extension” means our name/effect is not asserted to exist in a released game. Its source documents the parent job identity. “Adaptation” names a documented source ability but follows the explicit FFTA behavior in the class tables. Combo entries are ordinary FFTA integration. All entries below were individually reviewed, including ones whose names remain unchanged.

| ID | Previous draft | Revised entry | Classification | Source role / thematic rationale |
|---|---|---|---|---|
${rows.map(r=>`| ${r.id} | ${r.previous??'—'} | ${r.name} | ${r.kind} | ${r.anchor}. [Reference][${r.ref}] |`).join('\n')}

Machine-readable coverage: [ability audit data](notes/job-theme-audit.json). No ROM was changed. The next implementation gate is proving data capacity and one working job/ability; the next design gate is gameplay balance, especially persistent enchantments, terrain availability, Haste, MP recovery, and the new axe choices.
`+sourceBlock;

if(rows.length!==116 || new Set(rows.map(r=>r.id)).size!==116) throw Error('Ability coverage mismatch');
for(const r of rows) if(!refs[r.ref] || !r.anchor || !r.effect) throw Error('Missing lineage/effect: '+r.id);
fs.writeFileSync('JOB-CLASS-SPECIFICATION.md',spec);
fs.writeFileSync('AXE-SKILL-EXPANSION.md',axe);
fs.writeFileSync('JOB-THEME-AUDIT.md',overview);
fs.writeFileSync('notes/job-theme-audit.json',JSON.stringify({version:'0.2',date:'2026-09-13',scope:'Design only; no ROM mutation',sources:refs,abilities:rows},null,2)+'\n');
console.log(JSON.stringify({reviewed:rows.length,byKind:rows.reduce((a,r)=>(a[r.kind]=(a[r.kind]??0)+1,a),{}),files:['JOB-CLASS-SPECIFICATION.md','AXE-SKILL-EXPANSION.md','JOB-THEME-AUDIT.md','notes/job-theme-audit.json']}));
