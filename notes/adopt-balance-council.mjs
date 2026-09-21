import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const read = f => fs.readFileSync(path.join(root, f), 'utf8').replace(/\r\n/g, '\n');
const write = (f, text) => fs.writeFileSync(path.join(root, f), text.trimEnd() + '\n');
const data = JSON.parse(read('notes/job-theme-audit.json'));
if (data.version !== '0.4') throw new Error('One-time 0.4 -> 0.5 adoption; refusing to overwrite a later revision.');
const archive = path.join(root, 'notes/design-v0.4');
fs.mkdirSync(archive, {recursive: true});
for (const file of ['JOB-CLASS-SPECIFICATION.md', 'AXE-SKILL-EXPANSION.md', 'SUPPORT-SKILL-DESIGN.md', 'JOB-THEME-AUDIT.md', 'JOB-DESIGN-PRINCIPLES.md', 'JOB-EXPANSION-DESIGN.md', 'notes/job-theme-audit.json', 'notes/balance-council-coverage.json']) {
  fs.copyFileSync(path.join(root, file), path.join(archive, path.basename(file)), fs.constants.COPYFILE_EXCL);
}

const panels = ['martial', 'magic-utility', 'supports-reactions'];
const rows = new Map();
for (const panel of panels) for (const line of read(`notes/balance-council-${panel}.md`).split('\n')) {
  const m = line.match(/^\|\s*((?:SAM|DRK|VIK|GEO|CHM|BRD|DNC|MYK)-[ASRC]\d|(?:SLD|GLD)-AX-[ASR]\d)\b/);
  if (!m) continue;
  if (rows.has(m[1])) throw new Error(`Duplicate council entry ${m[1]}`);
  const cells = line.split('|').slice(1, -1).map(s => s.trim());
  rows.set(m[1], {cells, panel});
}
if (rows.size !== 116 || data.abilities.some(a => !rows.has(a.id))) throw new Error('Incomplete council coverage');

const clean = s => s.replace(/\bmaxHP\b/g, 'max HP').replace(/\bcurrentMP\b/g, 'current MP').replace(/\bmaxMP\b/g, 'max MP').replace(/\bmissingHP\b/g, 'missing HP').replace(/\bmaxHP\b/g, 'max HP').replace(/\b(\d+)(HP|MP|gil|percentage|tiles)\b/g, '$1 $2').replace(/\bwithinr(\d)/g, 'within r$1').replace(/forT2\b/g, 'for T2').replace(/cap(\d)/g, 'cap $1').replace(/at(\d)/g, 'at $1').replace(/for(\d)/g, 'for $1').replace(/heal(\d)/g, 'heal $1').replace(/restore(\d)/g, 'restore $1').replace(/Activation100%/g, 'Activation 100%').replace(/same modes/g, 'self/Sure OR r1 enemy/A');

for (const a of data.abilities) {
  const {cells, panel} = rows.get(a.id);
  const ap = cells[2].match(/^(\d+)\s*(?:AP\b|;)/) || cells[1].match(/;\s*(\d+)\b/);
  if (!ap) throw new Error(`No AP ${a.id}`);
  a.preBalanceRevision = {name: a.name, ap: a.ap};
  a.ap = Number(ap[1]);
  const label = cells[0].slice(a.id.length).trim().split(/\s+(?:->|→)\s+/).at(-1);
  a.name = label;
  a.effect = clean(cells[2].replace(/^\d+\s*(?:AP\b\s*;?|;)\s*/, ''));
  if (a.type === 'Action' && panel === 'martial' && a.id.startsWith('MYK-')) a.effect += '. ' + clean(cells[3]);
  if (a.type === 'Combo') a.effect += '. Vanilla chain participation profile: ' + cells[3] + ' Preserve vanilla initiation/JP behavior; no new riders.';
  a.balanceRationale = clean(cells.at(-1));
  if (a.type === 'Support') a.buildExamples = clean(cells[3]);
  a.balanceSource = `notes/balance-council-${panel}.md`;
  a.balanceVerdict = cells[1].split(';')[0];
  delete a.cost;
  delete a.target;
}
const get = id => data.abilities.find(a => a.id === id);
const append = (id, text) => { get(id).effect += ' ' + text; };
get('DRK-S1').effect = get('DRK-S1').effect.replace('≤40%', '≤35%').replace('Same exclusions as 0.4.', 'No bonus to fixed/percentage damage, instant KO, costs, items, healing, drain recovery, MP damage, damage-over-time, reactions, or combos.');
get('SAM-S2').effect = get('SAM-S2').effect.replace('Same qualifying statuses as 0.4;', 'Qualifying statuses: Protect, Shell, Haste, Regen, Float, Invisible, and tagged temporary positive effects such as Centered, Last Resort, or an enchantment;');
get('VIK-S2').effect = get('VIK-S2').effect.replace('incoming-action start', 'action start').replace('Existing ailment tags,', 'Harmful statuses include Poison, Blind, Silence, Slow, Immobilize, Disable, Confuse, Sleep, and tagged custom debuffs;');
get('CHM-A8').effect = 'One X-Potion AND one Phoenix Down; r4 one KO non-undead ally; Sure. Revive at floor(0.50 × target max HP), minimum 1 HP, with no 200-HP cap. No additional buffs, turn change, Pharmacology, or incoming-healing bonus.';
append('DRK-A5', 'Outgoing bonus excludes fixed/percentage damage, items, reactions, combos, MP damage and a second multiplication of drain recovery. The linked incoming drawback applies to direct physical HP damage, not costs or damage-over-time. Enemy strike mode is unavailable with Healer; self mode remains legal.');
append('BRD-S1', 'Only persistent tagged beneficial statuses qualify; immediate turn/CT effects such as Smile and Quicken do not. No outgoing-healing multiplier applies to this separate heal; only the recipient’s incoming-healing modifier may apply.');
append('MYK-S1', 'Enchantment followed by Red Magic is Magic-to-Magic and gains no alternation bonus; Fight or a qualifying Lunge action can alternate with the enchantment.');
append('DNC-R1', 'Physical damage classification, not Spellweave sequencing category, determines eligibility; an enchanted strike consumes at most one charge.');

const origins = {
 'VIK-A5': ['Original extension', 'Original focused storm that damages and slows, inspired by Viking storm magic'],
 'CHM-A2': ['Thematic redesign', 'Field medicine combines separately stocked, explicitly selected cures into one learned lesson'],
 'CHM-A4': ['Thematic redesign', 'High-grade medicine lesson groups existing consumables without changing their contents'],
 'CHM-A5': ['Original extension', 'Original two-ingredient healing mist grounded in Final Fantasy Chemist preparation and mixing'],
 'CHM-A8': ['Original extension', 'Original costly revival preparation grounded in Final Fantasy Chemist medicine'],
 'BRD-A8': ['Thematic redesign', 'A dependable ensemble of protective statuses replaces the source-inspired random outcome'],
 'BRD-R2': ['Original extension', 'A reactive return to the musical tempo grants temporary Haste instead of a tiny healing reprise'],
 'DNC-A6': ['Thematic redesign', 'A deliberate choice of debilitating dance replaces a random ailment selection'],
 'MYK-R2': ['Original extension', 'Spend a maintained weapon enchantment to soften one incoming physical action']
};
for (const [id, [kind, anchor]] of Object.entries(origins)) Object.assign(get(id), {kind, anchor});
for (const a of data.abilities.filter(a => /^MYK-A/.test(a.id))) {
  a.kind = 'Thematic redesign';
  a.anchor = 'FFV-style weapon enchantment adapted to immediate commitment and sustained primary-weapon combat';
}
data.version = '0.5';
data.schemaVersion = 2;
data.date = '2026-09-14';
data.scope = 'User-approved council balance pass: all 116 abilities, cross-class interactions, AP and teaching data. Current design, not an implemented or gameplay-tested patch.';
data.schemaNote = 'AP has its own field. effect contains the complete action cost, targeting, accuracy, and effect together; commandRules/sharedRules in JOB-CLASS-SPECIFICATION.md also apply. Former separate cost/target fields were removed to avoid stale parallel values.';
data.balanceCouncil = 'BALANCE-COUNCIL.md';

const references = Object.entries(data.sources).map(([id, [, url]]) => `[${id}]: ${url}`).join('\n');
const rowOrigin = a => `${a.kind}: ${a.anchor}. [Inspiration][${a.ref}]`;
function table(list) {
  return '| ID / ability | AP | Current rules | Role and build considerations | Inspiration |\n|---|---:|---|---|---|\n' + list.map(a => `| ${a.id} ${a.name} | ${a.ap} | ${a.effect} | ${a.balanceRationale} | ${rowOrigin(a)} |`).join('\n');
}
const oldSpec = read('JOB-CLASS-SPECIFICATION.md');
const slice = (text, start, end) => { const a = text.indexOf(start), b = text.indexOf(end, a + start.length); if (a < 0 || b < 0) throw new Error(`Missing section ${start}`); return text.slice(a, b); };
const roster = slice(oldSpec, '## 1. Roster', '## 2. Shared');
const stats = slice(oldSpec, '## 3. Stats', '## 4. Samurai').replace('Growth alignment: Samurai', 'Retained after the council review: Samurai');
let equipment = slice(oldSpec, '## 12. Teaching', '## 13. Implementation');
equipment = equipment.replace(/Teaching the revised supports[^\n]+/, 'Eight teaching weapons per new job make 64, plus eight Soldier/Gladiator axes: **72 teaching items**. W1–W8 teach A1–A8. W2 also teaches S1; W3 combo; W4 R1; W5 S2; W6 R2. Each table entry gives its current AP; simultaneous lessons progress normally. The per-job totals below replace the old uniform 3,150-AP total.');
equipment = equipment.replace('| Chemist / Knife | Tonic Knife | Antidote Knife | Phoenix Knife | High Tonic Knife | Clear Eye Knife | Ether Knife | Remedy Knife | Restorer Knife |', '| Chemist / Knife | Tonic Knife | Field Remedy Knife | Phoenix Knife | High Tonic Knife | Mist Knife | Ether Knife | Cureall Knife | Resuscitation Knife |');
equipment = equipment.replace('| Squall Axe |', '| Stormcall Axe |');
equipment = equipment.replace('Chemist\'s later medicine lessons must coincide with repeatable ingredient access; no early X-Potion availability is assumed.', 'A repeatable teaching weapon does not guarantee repeatable ingredients. Ethers are not assumed purchasable, Cureall access is progression-dependent, and no new consumable shop stock is introduced. High Tonic permits using an owned X-Potion without promising early availability or affordability. Verify actual vanilla supply and shop flags.');
const totals = {};
for (const a of data.abilities) { const key = a.id.replace(/-[ASRC]\d$/, ''); totals[key] ??= {Action:0, Support:0, Reaction:0, Combo:0}; totals[key][a.type] += a.ap; }
const names = {SAM:'Samurai',DRK:'Dark Knight (each race)',VIK:'Viking',GEO:'Geomancer',CHM:'Chemist (each race)',BRD:'Bard',DNC:'Dancer',MYK:'Mystic Knight','SLD-AX':'Soldier axe additions','GLD-AX':'Gladiator axe additions'};
const apTable = '| Lesson group | Action AP | Support AP | Reaction AP | Combo AP | Total AP |\n|---|---:|---:|---:|---:|---:|\n' + Object.entries(names).map(([key,name]) => { const t = totals[key]; return `| ${name} | ${t.Action} | ${t.Support} | ${t.Reaction} | ${t.Combo} | ${Object.values(t).reduce((a,b)=>a+b,0)} |`; }).join('\n');
equipment += '\n' + apTable + '\n\nThe totals count lessons, not sequential grinding. New Soldier/Gladiator actions count toward their existing mastered-action gates. Measure earlier unlock timing without changing the accepted prerequisites. New weapons may improve original jobs that can equip them; compare attack, other stats, effects, price, and acquisition against actual vanilla alternatives before tuning those values.\n\n';

const common = `## 2. Shared rules

The current design contains **116 entries: 72 actions, 18 supports, 18 reactions, and eight combos**. Eight job concepts require ten racial job implementations. The twelve axe entries are added inside the two existing command sets. These counts describe lessons, not proven available ROM records.

### Learning, equipment, and source lineage

Keep vanilla equipment/AP learning, one freely selected secondary action set, one support, one reaction, and one combo. Original Alchemist retains its fixed ordinary Item command in addition to its two learned command sets; no other job gains a third learned set. A mastered lesson does not grant another race's jobs, new equipment permissions, or a second equipped support. Only action mastery counts toward job gates. Job switching does not recalculate accumulated stats; level-one templates below are generation/test templates, not job-change bonuses.

Sources identify inspiration. Adaptation and thematic redesign may freely change mechanics; original extensions are intentional inventions grounded in a job's identity. None of the new numbers, teaching items, racial assignments, or recipes is claimed to be a direct canonical port. The [lineage register](JOB-THEME-AUDIT.md) covers every lesson.

### Formula, targeting, and action categories

**P** is one primary-weapon physical hit's damage reference, including relevant defenses. 1.30P means a final-damage multiplier, not +30% Attack. New A-abilities do not call Fight, crit, copy weapon status procs, or use a second weapon. Weapon-elemental attacks use the primary weapon's element. Healer remains restorative and cannot be converted into damaging/draining attacks. **M24** is a proposed magical-power reference using Magic Power/Magic Resistance, not a verified ROM field. Original attack/defense supports and Protect/Shell modify their vanilla formula inputs; do not equate them with our final-damage multipliers. [Mechanics][mechanics].

**A** is ordinary attack-style accuracy; **S** is ordinary status accuracy, including immunity; **Sure** is a legal willing-target effect. S multipliers act on final ordinary success chance. Listed percentage-point changes apply after the ordinary calculation, with their stated cap; they never override immunity or a preventing reaction. Theft uses the original transaction's own accuracy and eligibility rather than an invented S check.

**rN** is Manhattan tile distance; r1 excludes diagonals. **Cross** is center plus four orthogonal neighbors. **Self cross** centers on the user. **Line N** is a selected cardinal line excluding the user and stopping at impassable terrain. **Any** permits friendly fire. Single-target range has height limit 3, melee limit 2; cross neighbors are within 2 height of center and line targets within 2 of caster. Projectiles require line of sight; songs, dances, and terrain effects do not. Preview all targets and actual accuracy before commitment. Each new action resolves immediately using one ordinary action; none grants an extra action or immediate movement.

Damage type and Spellweave sequencing are separate. Both Spellblade modes establish **Magic** once but their strike deals **physical** damage. Battle Chant/Fury can boost that strike; Wisp Exposure/Magickal Refrain cannot. Enchantment then Red Magic is Magic-to-Magic, not alternation. New actions never gain Doublecast; original eligible magic remains unchanged. Original Double Sword/Fight still works, but new attacks use only one primary weapon.

### Support and buff interactions

Mastered supports work on every legal current job of their character without the teaching job's command or weapon. Full rules and two external-job examples appear in [the support sheet](SUPPORT-SKILL-DESIGN.md). They integrate with applicable original commands, not only the new IDs.

Unless explicitly included, new outgoing damage bonuses exclude fixed/percentage damage, instant KO, HP/MP exchange, costs, item effects, drain recovery, damage-over-time, reactions, and combos. Direct restorative healing includes spells/techniques; Pharmacology applies to item restoration; Recuperation applies to incoming direct restoration. An increase to actual drain damage may indirectly raise recovery, then the drain cap applies; never multiply recovered HP a second time. Defensive modifiers act on their stated direct damage category, not HP costs or damage-over-time.

Beneficial/harmful statuses use explicit tags, including new temporary effects. Equipment stats, fields, passive lessons, and reaction readiness are not statuses. Poise snapshots the presence of a beneficial status at incoming-action start. Opportunist snapshots the target before outgoing damage; its own rider cannot qualify the same hit. Wisp Exposure begins after Wisp damage and never boosts that hit.

Encouragement recognizes a newly applied **persistent** beneficial status on another ally, once per recipient/action. Immediate turn/CT effects such as Smile and Quicken, refreshing a status, self-targeting, mere cures/healing, and reactions do not qualify. Its separate HP recovery receives only the recipient's incoming-healing modifier, never an outgoing modifier such as Composure or Magick Boost. Resolve base healing and this additional healing as separate events, rounding after each event's combined multipliers and respecting missing HP.

Spellweave records one qualifying voluntary action category at completion even on a miss. Its first action gets no bonus. Wait and unclassified actions retain the previous category without a bonus; repeating a category does not earn the bonus. Same-category Doublecast establishes Magic once; mixed/ambiguous multi-cast clears the sequence. Reactions, movement, and forced actions do not create a category. Job change, KO, Petrify, battle end, or removing the support clears the sequence. Show the next eligible category. Fury uses physical damage classification even when that action's sequencing category is Magic, and is consumed only once.

### Duration, recovery, and payment

Named vanilla statuses use original duration, removal, immunity, and stacking except an expressly listed duration such as Encore's T2 Haste. **T2** expires after the target finishes its second subsequent turn, excluding application turn. Reapplication refreshes rather than stacks. KO, Petrify, battle end, and job change clear custom effects; Dispel removes beneficial effects. Appropriate broad remedies clear custom harmful tags. Last Resort is indivisible: remove its benefit and drawback together. Exposed and reaction charges have their explicitly shorter timers. Spellblade follows its persistent-enchantment rules.

Distinct applicable modifiers multiply once; round down after combining modifiers for that effect. Same-name effects do not stack. Grace changes A-type facing treatment, not SRes or positional damage riders. Attunement refunds only actually paid MP after an eligible success, never per area target or in advance. Clear Voice discounts explicitly tagged incanted magic and songs; it does not discount every MP-using martial technique.

New restoration targets non-undead allies, capped by missing HP/MP. Original commands retain undead behavior. Revival targets eligible KO units only, not removed or permanently lost units, and is not improved by Pharmacology, Recuperation, or other direct-healing modifiers.

HP costs are fractions of maximum HP rounded up, minimum 1. Pay after target validation but before hit checks, once for the committed action, and leave at least 1 HP. Costs are not damage and trigger no reactions or injury effects. Bloodcasting pays 2 HP per computed MP plus native HP costs, with no damage-mitigation discount. Validate the sum of independently priced components before commitment; never make a second component free. This rule does not grant a currently illegal cross-race Doublecast build. Healing may provide positive net HP while spending an action.

At 200 maximum HP: Blood Edge costs 20 HP; Abyssal Blade costs 30 HP + 10 MP, or **50 HP** with Bloodcasting; Unholy Sacrifice costs 40 HP + 14 MP, or **68 HP** with Bloodcasting. Sanguine Sword dealing 40 actual HP damage recovers 20 HP; dealing 200 recovers only its 40-HP cap. With Bloodcasting it also pays 12 HP instead of its 6 MP.

Drain uses actual positive resources removed: no allies, overkill, immunity, absorption, or overdraw. HP recovery respects the individual action cap. Undead reverse attempted HP recovery into user damage that can KO but triggers no reaction; MP drain reverses attempted recovery into MP loss capped at current MP. No new effect generates JP.

Validate all recipe ingredients together and deduct once atomically, never per recipient. No mission-item substitutions or automatic spending of rarer medicine. Long Throw does not turn an area mixture into a ranged single-target action. Auto-Potion requires an explicit pre-battle Potion/Hi-Potion choice, defaults to Potion, and uses no automatic replacement when stock is empty. Auto-Cureall follows the ordinary Cureall cure list plus custom harmful tags included in shared broad-remedy integration; it never prevents KO or an uncurable effect. One Cureall covers eligible ailments of that enemy action; zero stock means no interception.

### Reactions, counters, and combos

All new reactions activate **100% when eligible** unless expressly stated. There is no blanket until-next-turn lock. Apply only an entry's specific lock (Auto-Potion locks after actual consumption until the next own turn). Eligibility or a miss alone consumes no resource or lock. Existing vanilla reactions retain their own behavior.

One multi-hit/multi-cast enemy action is one opportunity for a new reaction. A defensive interception begins after a successful relevant hit check and before application; its reduction covers all eligible components of that action. Retaliation/recovery resolves at most once after the complete action, requires survival and ordinary reaction capability, and targets the original attacker if still legal. Existing incapacitation may prevent interception, but an ailment intercepted before application cannot prevent its own interception. No triggers from allies, self-costs, poison, combos, other reactions, or reaction/reflection chains. No counter recursively triggers another counter.

Spell Parry consumes an active qualifying enchantment for **50% physical HP damage reduction** across one enemy action; it does not negate that action, statuses, or magical components. Misses do not spend the enchantment. Fury/Magick Boost store at most one charge, not permanent stat gains. Encore grants temporary Haste, not an immediate turn, and cannot trigger Encouragement.

Each combo below specifies its original chain participation profile (power/range/hit) separately from the primary weapon's initiation range. Preserve original JP behavior and ordinary weapon-element handling; no new damage/status/support/enchantment/drain rider. Soldier/Gladiator retain existing combo profiles with only axe acceptance/animation added.

New effects follow the relevant original laws: element, item, theft, healing, equipment, and any mapped command restrictions. A new command name creates no law exemption.

`;

const commandRules = {
SAM: `**Iaido — Human.** Requires a primary katana for every action. All damage uses physical P; Murasame uses target maximum HP. Silence, Reflect, Return Magic, and Doublecast do not apply. Mastered techniques need no spare or matching named sword; no breakage.\n\n**Centered:** a visible non-stacking T2 buff from successful Ashura or Counter Draw. The next damaging Iaido other than Ashura, or Murasame, consumes it at execution for ×1.25 damage/healing for the whole action, including a miss. No bonus to MP damage, status, Fight, counters, combos, or secondary sets. Kiyomori neither consumes nor benefits. Clear on expiry, Dispel, KO, Petrify, battle end, job change, or primary weapon change/loss.\n\nUse a katana on Ninja/Iaido, or mix Samurai with Hunt or White Magic. Concentrate improves reliability; Double Sword takes the same support slot and only doubles ordinary Fight.`,
DRK: `**Dark Arts — Human and Bangaa.** Sword/greatsword/broadsword required for damaging/draining sword arts. Dark Mind and self-mode Last Resort are weapon-free; Last Resort's optional commitment strike accepts any damaging primary weapon at r1, not Healer. All strikes/drains are physical; Silence, Reflect, Return Magic, and Doublecast do not apply.\n\nLast Resort's initial strike precedes the new buff; an already active buff follows ordinary rules. Its outgoing multiplier applies only to eligible direct physical damage, not fixed/percentage effects, items, reactions, combos, MP damage, or a second drain-recovery multiplier. Its incoming physical drawback remains linked to the benefit. At low HP, Desperation can activate after paying a sacrifice; the threshold is 35%, not 40%.\n\nHuman Dark Knight/Blue Magic and Bangaa Dark Knight/Prayer are legal. Axe Gladiator/Dark Arts or Viking/Dark Arts can use Dark Mind and Last Resort but cannot use sword-gated drain/sacrifice moves while holding an axe. Bloodcasting and Desperation cannot be equipped together.`,
VIK: `**Reaving — Bangaa.** Uses the new two-handed Axe family. Strong-Arm/Pillage require an axe. Thunder, Stormcall, Thundaga, and Tsunami are incanted magic blocked by Silence; lightning actions follow ordinary applicable Reflect/Return Magic behavior. Tsunami is environmental and neither Reflected nor Returned. Theft and War Cry work while Silenced. No Doublecast.\n\nResolve each eligible original theft transaction independently before HP damage, using its original accuracy, protection, loot ownership, and depletion rules. A damage miss/zero damage does not remove the theft attempt. Stolen defenses change the following damage calculation and preview. Never steal the same depleted item again. No generic S roll replaces the original handler.\n\nViking/Gladiator offers two compatible axe sets; Viking/Bishop adds support magic. Bishop/Reaving can cast storms but cannot perform axe theft. Tsunami's dry-ground displacement is distinct from its optional water-adjacent MP removal; neither grants water traversal.`,
GEO: `**Geomancy — Nu Mou.** Weapon-free nature arts; damage uses Magic Power/Magic Resistance. No Silence, Reflect, Return Magic, or Doublecast. Every action works without terrain affinity.\n\n**Nearby affinity:** inspect caster tile and four orthogonal neighbors within 2 height; rock/stone, vegetation, water/wetland, wood/heat, and snow/ice groups supply at most one relevant bonus. Unknown tiles give no affinity but disable no action. Nearby inaccessible water can be sensed but not entered. Gaia Surge always offers Wind, plus mapped local elements; Nature's Wrath now always uses Wind independently of learned actions. Float does not prevent affinity.\n\n**Frost field:** one cross per caster, replacing the previous field. Expires after the caster's second subsequent turn, or on caster KO/Petrify/job change/battle end. Each entered field tile adds one movement cost for grounded allies/enemies; overlapping fields never add more. Float/flying/Surefoot ignore the surcharge, not other tile legality. No entry damage, impassability, reaction triggers, or changed affinity; a field does not qualify its own cast for an ice bonus.\n\nWisp Exposure starts after damage, refreshes without stacking, and a weaker application cannot refresh a stronger one. Immunity to its custom effect blocks the rider; elemental immunity/absorption prevents positive-damage riders. Updraft can combine with an ally's Light Foot for +2 Move but never stack with itself. Time Mage/Geomancy and Alchemist/Geomancy are legal weapon-free mixes.`,
CHM: `**Medicine — Nu Mou and Moogle.** This command is distinct from vanilla ordinary Item. All eight lessons need no weapon, cost 0 MP, work while Silenced, and consume the exact named ingredients. No Reflect, Return Magic, or Doublecast. Single-target medicine is r4 with ordinary projectile LOS/height unless specified; Healing Mist is an r3 center/cross area, not Long Throw eligible. New medicine targets non-undead allies; revivals require eligible KO allies.\n\nField Remedy selects exactly one stocked cure with only that item's cure list. High Tonic selects one stocked Hi-Potion or X-Potion. Healing Mist and Resuscitating Draught are original two-ingredient preparations, not claims about vanilla potion contents. Validate the entire recipe before spending any ingredient. Pharmacology improves explicit item HP/MP restoration once, never revival fractions. Resuscitating Draught restores half maximum HP without a 200-HP cap or any healing-support increase.\n\nItems remain actual inventory resources: no shop-buyable Ether assumption or new consumable stock. Moogle Juggler/Medicine retains Smile; Bard/Medicine lacks Stunt. Alchemist already has fixed ordinary Item: Alchemist/Sagacity with Long Throw is a serious alternative, so Chemist's mixtures must earn the secondary slot.`,
BRD: `**Song — Moogle.** Voice is sufficient: no active song requires an instrument or grants instrument equipment permission. Silence blocks songs; Hide requires neither voice nor weapon and works while Silenced. No Reflect, Return Magic, or Doublecast. Instruments remain Bard equipment and Chorus Combo's requirement.\n\nMarching Strength/Inspired Magic use T2 final physical/magical damage multipliers, not attack-stat boosts. Exclude fixed/percentage damage, items, reactions, combos, and a second drain-recovery bonus. No healing bonus from Inspired Magic. Nameless Song applies Protect, Shell, and Regen deterministically; no random pool or Haste. Magick Ballad may restore MP over ordinary turns, but never grants an extra action or restores the caster directly.\n\nA new persistent song buff may trigger Encouragement once per other ally. Magick Boost can improve the song's own HP restoration, not the separate Encouragement heal or Ballad's MP recovery. Juggler/Song can choose a song or Smile, not both in one action. Time Mage/Song is legal; Moogle White Magic and Bloodcasting are not.`,
DNC: `**Dance — Viera.** Performance works while Silenced; no Reflect, Return Magic, or Doublecast. Only Sword Dance needs a primary knife/rapier. Dances do not directly grant or reset turns.\n\n**Pdance:** use virtual weapon V = min(35, 12 + floor(0.60 × level)), replacing the primary weapon's Attack contribution and weapon-power term in the physical P formula. Keep the character's accumulated physical Attack, nonweapon gear bonuses, applicable supports, and target defense. Ignore held weapon Attack/element/procs and second weapons. V is 18/27/35 at levels 10/25/40. This is a defined custom formula, not a verified ROM field. Sword Dance instead uses the actual primary weapon's P.\n\nPolka/Heathen Frolic use physical damage followed by their custom weakening rider; custom immunity blocks the rider, not unrelated damage. Forbidden Dance selects one ailment for the entire cast, not separately per enemy and not at random. Assassin/Dance works for weapon-free dances but not Sword Dance with a bow/katana. Red Mage/Dance cannot Doublecast dances; Dancer/White Magic can trade offense for restoration.`,
MYK: `**Spellblade — Viera.** Every action requires a primary rapier/saber and is blocked by Silence. Select self preparation (Sure) or one r1 enemy for an immediate enchanted A-type strike. Pay once; apply/replace the enchantment even if the strike misses; this is one action, not a free second action or movement. The strike is physical and not Fight: no crit, weapon proc, second weapon, Doublecast, or automatic bypass of applicable defensive reactions.\n\nOne enchantment persists until replaced, Dispel, KO, Petrify, primary weapon change/loss, job change, battle end, or Spell Parry consumption. Silence after preparation prevents re-enchanting but does not erase it or stop Fight. Future benefits apply only to primary Fight, replacing its ordinary element/proc; no secondary technique, counter, combo, or second weapon inherits a rider. Healer cannot become damaging/draining.\n\nBoth modes establish Magic once for Spellweave; their damage remains physical. Follow with Fight/Lunge to alternate, not Red Magic. Battle Chant/Fury can improve the strike; Wisp/Inspired Magic cannot. Spell Parry spends the enchantment for 50% physical damage reduction against one enemy action, then it must be reapplied deliberately. Red Mage/Spellblade, Fencer/Spellblade, and Dancer/Spellblade work with rapiers; Assassin/Summoner lack qualifying normal weapons.`
};
data.commandRules = commandRules;
const jobTitles = {SAM:'Samurai — Human',DRK:'Dark Knight — Human and Bangaa',VIK:'Viking — Bangaa',GEO:'Geomancer — Nu Mou',CHM:'Chemist — Nu Mou and Moogle',BRD:'Bard — Moogle',DNC:'Dancer — Viera',MYK:'Mystic Knight — Viera'};
let jobs = '', section = 4;
for (const [key, title] of Object.entries(jobTitles)) {
  const abilities = data.abilities.filter(a => a.id.startsWith(key + '-'));
  jobs += `## ${section++}. ${title}\n\n${commandRules[key]}\n\n### Actions\n\n${table(abilities.filter(a=>a.type==='Action'))}\n\n### Supports and reactions\n\n${table(abilities.filter(a=>['Support','Reaction'].includes(a.type)))}\n\n### Combo\n\n${table(abilities.filter(a=>a.type==='Combo'))}\n\n`;
}
const acceptance = `## 13. Implementation and balance validation

Version 0.5 is the user's adopted council design, not an applied or gameplay-tested ROM patch. Preserve the vanilla-USA base, original jobs/abilities/stories/laws/missions/recruitment and saves, except the approved additive axe permission/lessons and explicit integration of new effects. Squire/Sentinel remain rejected and Green Mage remains a candidate.

Prove storage for ten racial job implementations, mastery, teaching items, lists, saves, and animations before assuming new records can be added. Verify original handlers for formulas, theft, item effects, reaction scheduling, enchantment modes, cost/preview behavior, and laws. No data-only implementation is assumed. Validate pre-battle Auto-Potion selection and the next-category Spellweave display rather than silently replacing those user-facing choices.

The [council report](BALANCE-COUNCIL.md) documents adopted decisions, burst examples, and research. The [global review](notes/balance-council-global.md) supplies the comparison matrix. Test early/mid/late equipment around levels 10/25/40, organic and optimized inherited growth, actual AP/shop availability, short and long encounters, two-enemy focus fire, and real boss immunities.

Priority cases: Bloodcasting + Damage > MP at tiny/full MP reserves; capped drain and undead; Desperation/Dragonheart with sacrifice and party buffs; attack-and-enchant with Spellweave/Fury/Spell Parry; Song/Encouragement/charged healing and donated turns; Chemist inventory recipes and revival at high HP; Dancer virtual-weapon scaling; Geomancer fields, affinities and movement; new axes with every original Soldier/Gladiator action. Count setup, allied healing, and extra-turn actions rather than comparing only a successful hit.

At 300 target max HP, Healing Mist restores 60, or 135 when the item user has Pharmacology and a Human recipient has Recuperation. Charged Angelsong plus a new Regen/Encouragement on that Human restores 117 + 67 = 184 HP, capped by missing HP. Encore/self/refresh/Smile never generate that extra Encouragement heal. These are arithmetic expectations, not results from playtesting.

Keep original unlock gates and verify any acceleration from additional mastered axe actions. Match all 72 teaching items to actual shop flags, retain repeatable teaching access without inventing consumable supply, and compare new equipment's effect on original jobs. Combo profiles require both correct initiation and chain participation. Full release needs real battle, AI, law, AP, job change, ordinary save/load, and clean-ROM patch tests; old-save migration is not assumed.

The [modding guide](FFTA-MODDING-GUIDE.md) covers tooling and research. No ROM has been changed by adopting these documents.
`;
write('JOB-CLASS-SPECIFICATION.md', '# FFTA: eight-job expansion specification\n\nDesign version 0.5 — adopted council balance pass, September 14, 2026\n\n**Current approved design for our vanilla USA FFTA expansion.** The [council’s reconciled recommendations](BALANCE-COUNCIL.md) are adopted here, including all 116 entries, cross-class rules, AP, and teaching data. Values still require implementation and gameplay testing. [Design principles](JOB-DESIGN-PRINCIPLES.md) preserve job identity and mixing.\n\n' + roster + common + stats + jobs + equipment + acceptance + '\n' + references);

const oldAxe = read('AXE-SKILL-EXPANSION.md');
const axeGear = slice(oldAxe, '## Teaching axes', '## Implementation boundary');
write('AXE-SKILL-EXPANSION.md', `# Axe skills for Soldier and Gladiator

Design version 0.5 — adopted council balance pass, September 14, 2026. Design only; no ROM patch applied.

Add four actions, one support and one reaction to each existing command. Preserve original Soldier/Gladiator moves, growths, armor, movement and prerequisites. No Squire, Sentinel, or Sentinel-to-Viking branch. The [class specification](JOB-CLASS-SPECIFICATION.md) owns shared combat, support, reaction, law, and learning rules. [Council rationale](BALANCE-COUNCIL.md).

## Weapon, geometry, and interaction rules

The new two-handed Axe family has ordinary range 1, no shield/second weapon, and no inherent armor bypass/random damage. Soldier, Gladiator, and Viking can equip it; Warrior and other jobs do not automatically gain permission. Equipment access does not grant another job's teaching lessons.

All eight actions require a primary axe. Recuperation and Follow Through are transferable, weapon-free supports; both reactions require an axe. Actions remain inside Battle Tech or Spellblade Tech, not a third command. They use physical P/A, work while Silenced, and cannot Reflect, Return Magic, Doublecast, crit, copy procs, or gain a second weapon strike. No axe is consumed. Mastered actions count toward existing owning-job unlock gates.

Frontal arc selects the tile directly ahead plus the two diagonals beside it, within 2 height, with friendly fire and no caster hit. Tomahawk needs projectile LOS. Shatter Guard removes Protect on a successful hit before damage; Armor Splitter reduces effective defense for that hit only. Exposed multiplies incoming direct physical damage by 1.20 until the next own turn starts, including immediate retaliation, even if Fell Cleave misses. It does not stack; KO/Petrify/battle end/broad remedy clears it. The action is unavailable if immunity would cancel its drawback at application. Protect may mitigate normally. Last Resort's linked drawback can multiply with Exposed to 1.44.

New reactions use dependable eligible activation and one opportunity per enemy action, without the former blanket turn lock. They retain range/weapon/survival requirements and no reaction chains. Follow Through requires ending voluntary movement at least two Manhattan tiles from turn-start position, not merely walking two tiles or circling back.

## Soldier — Human

${table(data.abilities.filter(a=>a.id.startsWith('SLD-AX-')))}

Soldier/Hunter is legal with an axe. Paladin/Battle Tech cannot use axe additions without axe permission. These techniques add practical reach/area/guard breaking; they do not replace original Soldier weakening moves.

## Gladiator — Bangaa

${table(data.abilities.filter(a=>a.id.startsWith('GLD-AX-')))}

Viking/Gladiator can use both axe sets. Axe Gladiator/Dark Arts can use Dark Mind and Last Resort's any-primary-weapon commitment strike, but not sword-gated Sanguine Sword or sacrifice attacks. Original Rush, Wild Swing, Beatdown, elemental techniques, and Strikeback stay intact. Existing Soldier/Gladiator combo numbers and JP behavior are unchanged, with axe acceptance/animation added.

${axeGear}
## Learning and implementation

Soldier's additions total **1,050 AP**; Gladiator's total **1,850 AP**. Simultaneous lessons progress normally. The full project retains 116 entries and 72 teaching items; record capacity, animations, UI, law dispatch, shops, and mastery storage still need proof. Generic attack/price targets must be compared with actually available vanilla equipment. No original item, story, or save is changed by these documents.

${references}`);

const supportRows = data.abilities.filter(a => a.type === 'Support');
write('SUPPORT-SKILL-DESIGN.md', `# Supports for mixing jobs

Version 0.5 — adopted council balance pass, September 14, 2026

**A job teaches a support; it does not own the support's usefulness.** All 18 lessons transfer to any legal current job of the same character without requiring the teaching command or its signature weapon. One support slot still applies. [Current class rules](JOB-CLASS-SPECIFICATION.md) govern timing, exclusions, action categories, original-command integration, and payment; [the council](BALANCE-COUNCIL.md) explains the balance choices.

## All supports and legal uses

| ID / support | Taught by | AP | Current effect | External builds and tradeoff |
|---|---|---:|---|---|
${supportRows.map(a=>`| ${a.id} ${a.name} | ${a.job} | ${a.ap} | ${a.effect} | ${a.buildExamples} |`).join('\n')}

## Shared interpretation

Do not combine two supports in one build: Bloodcasting excludes Half MP/Desperation, Pharmacology excludes Long Throw, and Spellweave excludes Concentrate. Different party members may combine their effects through legitimate actions. Alchemist retains fixed ordinary Item alongside its two learned commands; other jobs do not gain a third learned set.

Modifiers integrate with eligible vanilla and new actions. Costs, fixed/percentage damage, instant KO, items, direct drain recovery, damage-over-time, reactions, and combos receive no new outgoing damage bonus unless explicitly included. Higher actual drain damage can increase recovery once up to the action cap; no second multiplier. Direct healing, item potency, revival, and MP recovery are distinct categories. Full restoration cannot exceed missing resources.

Bloodcasting sums payable MP and native HP costs before commitment, leaves at least 1 HP, and cannot trigger injury reactions. Attunement refunds only actually paid eligible MP after resolution, never once per area target or before affordability. Clear Voice discounts only tagged incanted magic/song costs; it does not grant Moogles Half MP or another race's command.

Spellblade establishes Magic for Spellweave while its damage remains physical. Repeating enchantment then Red Magic is not alternation. Wait/nonqualifying actions retain the prior category without a bonus. Immediate turn/CT effects such as Smile/Quicken never qualify for Encouragement. Its separate healing takes only the recipient's incoming modifier, never Composure/Magick Boost. Reactive/self/refresh effects provide no bonus.

At 300 max HP, Healing Mist with the giver's Pharmacology and the Human receiver's Recuperation restores 135 HP, capped by missing HP. Each character uses one support slot. A Juggler/Item with Long Throw retains Smile; Gunner/Item does not also gain Stunt. Useful map-specific supports need not beat Concentrate everywhere. These are adopted design values, not measured gameplay balance.
`);

write('JOB-THEME-AUDIT.md', `# Job inspiration and design register

Version 0.5 — adopted council balance pass, September 14, 2026

**Theme guides the job; FFTA gameplay guides its mechanics.** The [class specification](JOB-CLASS-SPECIFICATION.md), [axe addendum](AXE-SKILL-EXPANSION.md), and [support sheet](SUPPORT-SKILL-DESIGN.md) are the current design. The [council](BALANCE-COUNCIL.md) records its adopted balance rationale. Numerical tuning remains subject to gameplay testing.

All 116 stable IDs are retained. Chemist's consolidated cures/tonics and two mixtures, Viking Stormcall, intentional dance control, and immediate Spellblade strikes are adaptations or original extensions. Source links explain the profession or inspiration, not the existence of our exact name, recipe, timing, or formula. Eight-action templates remain a design choice, not a fidelity requirement.

The initial-name column preserves v0.1 lineage; the preceding-name column records v0.4. Old exact mechanics are archived in notes/design-v0.4 and are not current requirements. Roster, racial distribution, growth/chassis baseline, accepted prerequisites, and Chemist starter access remain unchanged.

| ID | Initial draft | Preceding name (0.4) | Current entry | Classification | Inspiration / purpose |
|---|---|---|---|---|---|
${data.abilities.map(a=>`| ${a.id} | ${a.previous ?? a.preBalanceRevision.name} | ${a.preBalanceRevision.name} | ${a.name} | ${a.kind} | ${a.anchor}. [Inspiration][${a.ref}] |`).join('\n')}

${references}`);
write('notes/job-theme-audit.json', JSON.stringify(data, null, 2));
console.log(JSON.stringify({version: data.version, entries: data.abilities.length, totals}, null, 2));
