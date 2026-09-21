import fs from 'node:fs';

const data=JSON.parse(fs.readFileSync('notes/job-theme-audit.json','utf8'));
if(data.version!=='0.3') throw new Error('One-time v0.3 to v0.4 design migration; refusing to overwrite the current revision.');
const supports=[
['SAM-S1','Composure','During your own turn, direct HP damage dealt and direct restorative HP healing applied ×1.15 if you have not voluntarily moved before that action starts. Moving afterward is allowed. No weapon, command, or Centered requirement. Does not boost item healing, drain recovery, MP effects, or reaction damage.','Calm, deliberate action; useful with attacks, techniques, and magic','Human Archer holding a firing position; Human Black Mage casting before moving'],
['SAM-S2','Poise','Direct physical and magical HP damage received ×0.85 while at least one beneficial status is active at the start of the incoming action. Qualifying effects are Protect, Shell, Haste, Regen, Float, Invisible, or a tagged temporary beneficial effect such as Centered, Last Resort, or a Spellblade enchantment. Additional statuses do not increase the bonus. No katana or source-job requirement; costs and damage-over-time are excluded.','Maintaining composure under protection; benefits can come from allies or another command','Human Paladin with Protect; Human Blue Mage supported by an allied buffer'],
['DRK-S1','Desperation','Direct physical and magical HP damage dealt ×1.30 while at 35% maximum HP or less, checked after paying costs. Works with any weapon and command. Does not increase HP costs, healing, MP damage, item effects, or damage-over-time.','Dangerous offense at low health, usable by martial and magical builds','Human Black Mage risking low HP; Bangaa Gladiator using wounded-state burst'],
['DRK-S2','Bloodcasting','For a voluntarily selected action with an MP cost, pay 2 HP per MP that would otherwise be spent, and spend no MP. Add any native HP cost separately; the combined payment must leave at least 1 HP. Pay after target validation and before accuracy, once per action. Costs trigger no reactions and cannot be reduced by damage protection. Items, JP, and non-MP costs are unchanged. Applies to every command; does not grant access to a command or change its Silence rules.','Trade life for action resources across spell and technique sets','Human Illusionist using HP to fuel Phantasm; Bangaa Bishop spending HP for Prayer'],
['VIK-S1','Sea Legs','Ignore forced tile displacement. Works with every job and weapon. Does not stop Immobilize, Slow, voluntary movement, or terrain harm, and does not grant water traversal.','A raider keeps their footing; transferable positional protection','Bangaa Dragoon keeping a useful position; Bangaa Templar resisting knockback'],
['VIK-S2','Opportunist','Direct physical and magical HP damage dealt ×1.20 against a target with at least one harmful status at the start of the action. Qualifying examples include Poison, Blind, Silence, Slow, Immobilize, Disable, Confuse, Sleep, and tagged custom debuffs. Multiple ailments do not multiply the bonus. The action cannot qualify itself by applying a status after its own damage. No weapon or theft requirement.','A raider exploits openings created by any ally or command','Bangaa Warrior attacking a blinded target; Bangaa Bishop exploiting an ally-applied debuff'],
['GEO-S1','Attunement','Elemental direct HP damage dealt ×1.20 when the resolved element is a weakness of the target after ordinary affinity rules. Applies to any physical or magical attack, including elemental weapons and secondary commands. Requires neither Geomancy nor nearby terrain. Neutral, resisted, immune, absorbed, non-elemental, healing, and damage-over-time outcomes gain nothing.','Understand elemental vulnerability and apply that knowledge to any technique','Nu Mou Black Mage exploiting weaknesses; Nu Mou Sage choosing an appropriate element'],
['GEO-S2','Surefoot','Jump +1. Entering an otherwise legally traversable tile pays its normal one-tile movement cost without added terrain movement surcharges, including Rime Field. Does not remove height restrictions, environmental damage or ailments, blocking units, or impassability; no flight or extra movement action.','Read and traverse difficult ground, regardless of current profession','Nu Mou Beastmaster reaching a useful position; Nu Mou Alchemist crossing slowed ground'],
['CHM-S1','Pharmacology','Direct HP and MP restoration from consumed restorative items ×1.50, then round down and cap at the recipient\'s missing resource. Applies to ordinary Item, Chemist actions, other consumable-based commands, and item-consuming reactions such as Auto-Potion. Does not improve revival HP, cure lists, drain, or magic; full restoration remains full restoration. Only the item user\'s support supplies this modifier.','Expert medicine preparation transfers to any use of supplies','Moogle Gunner with ordinary Item; Nu Mou Alchemist using restorative supplies'],
['CHM-S2','Long Throw','For a consumable-based single-target action that can normally target another unit, a base range below 4 becomes 4; a base range of 4 or more gains +1, capped at 5 and never reduced below its original range. Applies to ordinary Item, Chemist applications, and eligible future mixtures. Retain target, height, and line-of-sight restrictions. Does not turn self-only or area effects into ranged single-target effects, and does not extend weapon attacks.','Throw supplies accurately across the battlefield from any job','Moogle Thief with ranged Item support; Nu Mou White Mage delivering an emergency item'],
['BRD-S1','Encouragement','When a voluntary action successfully adds a new beneficial status to another ally, also restore 10% of that ally\'s maximum HP, capped at 30 HP before incoming-healing modifiers. Once per ally per action, even if several statuses are applied. Applies to all commands. Refreshing an existing status or its duration does not qualify; merely healing or curing does not qualify. No self-target bonus or reaction trigger.','Inspiring aid makes protective and enhancing actions more useful','Moogle Time Mage granting Haste; Moogle Animist applying a beneficial effect'],
['BRD-S2','Clear Voice','Immune to Silence while equipped, regardless of job, weapon, or command. No protection against other ailments. Does not grant magic, an instrument, or access to a voice-based command. Ordinary status-immunity handling applies.','Vocal discipline protects both songs and spellcasting','Moogle Black Mage preserving casting; Moogle Time Mage preserving support magic'],
['DNC-S1','Grace','Base Evade +10 before ordinary facing, equipment calculations, and caps. Applies with any job and weapon; it is not a universal ten-percentage-point dodge bonus against every effect.','Evasive footwork transferable to any combat style','Viera Fencer defending in melee; Viera Red Mage taking a frontline role'],
['DNC-S2','Light Foot','Move +1 on any current job. No second movement action, flight, terrain immunity, or free ability slot.','A performer\'s mobility becomes a general positioning tool','Viera Summoner reaching a casting position; Viera Sniper relocating for a shot'],
['MYK-S1','Spellweave','Alternate a voluntary incanted magic action and a physical-damage action. If the current action is the opposite category to the preceding qualifying action, its direct HP damage ×1.20; any physical weapon or command qualifies. Spellblade preparation counts as magic even though it causes no damage, so it can prepare a boosted physical attack. An action with no qualifying category breaks the sequence; repeating a category sets that as the last category without a bonus. No healing, drain-recovery, item, or reaction bonus. Magic acts resolve using an explicit command/effect classification, not simply a nonzero MP cost.','Combine martial and magical actions across different command sets','Viera Red Mage alternating magic and Lunge Tech; Viera Elementalist with a physical secondary set'],
['MYK-S2','Arcane Ward','Magical HP damage received ×0.75 while current MP is at least 50% of maximum MP at the start of the incoming action, with at least 1 MP remaining. Does not spend MP, absorb a spell, or reduce HP costs. Works with every job and weapon.','Maintained magical reserves protect their bearer','Viera White Mage conserving MP; Viera Summoner holding a defensive reserve'],
['SLD-AX-S1','Recuperation','Direct HP healing received ×1.25 from any eligible restorative source, including medicine and allied or self healing. Round down after combining modifiers and cap at missing HP. Does not improve revival HP, drain, regeneration ticks, or MP recovery. No axe, weapon, or command requirement.','Frontline recovery training, useful to any unit taking sustained damage','Human Fighter supported by a healer; Human Paladin benefiting from restorative actions'],
['GLD-AX-S1','Follow Through','During your own turn, direct physical HP damage dealt ×1.15 if you voluntarily moved at least one tile before the action begins. Applies to every weapon and physical command. Extra distance gives no additional bonus; forced displacement and later movement do not qualify. No magic, item, reaction, or damage-over-time bonus.','Carry movement into an attack; transferable offensive momentum','Bangaa Warrior advancing into combat; Bangaa Dragoon moving before a physical technique']
];
const oldNames=new Map();
for(const [id,name,effect,anchor,examples] of supports){
 const row=data.abilities.find(a=>a.id===id);if(!row||row.type!=='Support')throw Error('Missing support '+id);
 oldNames.set(id,row.name);row.preSupportRevision=row.name;row.name=name;row.effect=effect;row.anchor=anchor;row.kind='Cross-job support design';row.buildExamples=examples;
}
// Reconcile existing cross-references to the deliberately broadened supports.
const auto=data.abilities.find(a=>a.id==='CHM-R1');
auto.effect=auto.effect.replace('Pharmacology does not apply.','Pharmacology applies if equipped.');
const wrath=data.abilities.find(a=>a.id==='GEO-R2');
wrath.effect=wrath.effect.replace('or Terrain Lore bonus','or Attunement bonus');
data.version='0.4';data.date='2026-09-14';
data.supportPolicy='The teaching job grants the lesson; mastered supports work on any legal current job without its action set or signature weapon. See SUPPORT-SKILL-DESIGN.md.';
data.scope='Theme-led FFTA design, with all 18 supports reviewed for cross-job mixing. Values and engine compatibility remain provisional.';
const origin=a=>`${a.kind}: ${a.anchor}. [Inspiration][${a.ref}]`;
let spec=fs.readFileSync('JOB-CLASS-SPECIFICATION.md','utf8');
let axe=fs.readFileSync('AXE-SKILL-EXPANSION.md','utf8');
for(const a of data.abilities.filter(a=>a.type==='Support')){
 const row=`| ${a.id} ${a.name} | Support | ${a.ap} | ${a.effect} | ${origin(a)} |`;
 const re=new RegExp('^\\| '+a.id+' .*$', 'm');
 if(a.id.includes('-AX-'))axe=axe.replace(re,row);else spec=spec.replace(re,row);
}
for(const a of [auto,wrath]){
 spec=spec.replace(new RegExp('^\\| '+a.id+' .*$', 'm'),`| ${a.id} ${a.name} | ${a.type} | ${a.ap} | ${a.effect} | ${origin(a)} |`);
}
spec=spec.replace(/^Design version[^\n]*/m,'Design version 0.4 — supports for cross-job builds, September 14, 2026');
spec=spec.replace(/\*\*Our expansion of vanilla USA FFTA\.\*\*[^\n]*/,"**Our expansion of vanilla USA FFTA.** Preserve each job's spirit and build around FFTA's freedom to mix abilities. [Design principles](JOB-DESIGN-PRINCIPLES.md) guide the kits; [the support redesign](SUPPORT-SKILL-DESIGN.md) explains all 18 transferable supports and example builds. All values remain proposals for playtesting.");
const policy=`### Supports belong to builds

A support is taught by a job, but after mastery it can be equipped on any other legal job of that same character. None of our 18 proposed supports requires the teaching job, its secondary command, its signature weapon, or an exclusive mechanic such as Centered. Broad conditions such as low HP, elemental weakness, item use, movement, or a sequence of magic and physical actions are valid because many jobs can use them. Racial job availability and one equipped support still apply. [The full support sheet](SUPPORT-SKILL-DESIGN.md) gives legal build examples.

The support slot is independent of the primary/secondary action slots. A Paladin can learn Composure from Samurai and equip it while using Chivalry and another Human command; Iaido is unnecessary. This does not grant Samurai to other races. Temporary lesson access still follows existing teaching-equipment rules before mastery.

Support damage bonuses apply to direct physical/magical HP damage where stated, including eligible vanilla and new actions; they are not restricted to new IDs. Fixed/percentage damage, instant KO, HP/MP exchange, HP costs, item effects, drain recovery, damage-over-time, reactions, and combos receive no new outgoing bonus unless a support explicitly names that class of effect. Direct restorative healing includes spells and techniques; Pharmacology owns item potency, and Recuperation owns incoming HP recovery. A normal restorative Fight using Healer counts as direct healing, never damage or drain. Defensive supports apply to their stated damage category regardless of which command produced it.

Beneficial/harmful status checks use explicit effect tags, including vanilla effects and our temporary modifiers. Field tiles, passive equipment stats, learned supports, and reaction readiness are not statuses. Poise can use a beneficial status applied by anyone. Opportunist snapshots the target before damage. Encouragement can trigger once per recipient when adding a status that was absent; its bonus healing cannot trigger another Encouragement. The recipient's Recuperation may enhance it.

Spellweave records the preceding qualifying voluntary action on the user, at action completion, even if it misses. It never boosts the action that first establishes the sequence. Evaluate a sequence once per action, including multi-target actions. For an original multi-cast action, any mixed or ambiguous category breaks the sequence and gains no bonus; do not grant multiple bonuses inside one action. Reactions, forced actions, and movement do not establish a category. Normal Wait breaks the sequence. Job change, KO, Petrify, battle end, or removing the support clears it. The UI must show the next eligible category.

Bloodcasting converts the computed MP cost once per action, adding any native HP payment. At 200 max HP, Blood Edge still costs 20 HP; Abyssal Blade costs 40 HP + 24 HP instead of 12 MP; Unholy Sacrifice costs 60 HP + 32 HP instead of 16 MP. No HP discount remains. Validate each action's affordability before execution. Healing financed by Bloodcasting can have a positive HP return; that is allowed and costs a turn. Test the economy against ordinary healing and MP recovery rather than banning the combination by job.

`;
spec=spec.replace('### Formula and targeting notation',policy+'### Formula and targeting notation');
spec=spec.replace('War Cry and Clear Voice use only the stronger applicable status-resistance reduction.','Clear Voice grants Silence immunity, which wins over status success modifiers; War Cry continues to reduce other applicable status chances.');
spec=spec.replace('MP supports affect MP costs through the original system, not item counts or HP costs.','Original MP supports retain their behavior. Bloodcasting is our explicit exception that converts an MP cost into HP; no support changes consumable counts.');
spec=spec.replace('with Poise, holding it has defensive value.','Poise also recognizes other beneficial statuses, so it remains useful after changing jobs or spending Centered.');
spec=spec.replace('Eight new teaching weapons per job make 64,','Teaching the revised supports uses the existing proposed S1/S2 item positions and AP costs. Eight new teaching weapons per job make 64,');
spec=spec.replace('Sacrificial Will changes these to 15/30/45.','Bloodcasting keeps the native HP costs and additionally converts MP costs as described above.');
spec=spec.replace('Surefoot ignore that extra cost.','Surefoot ignore that extra cost. Surefoot also works on other mapped movement surcharges.');
spec=spec.replace('immunity to the new effect prevents the rider, not damage.','immunity to the new effect prevents the rider, not damage.');
spec=spec.replace('7. Full release requires',`7. **Support combinations:** verify all 18 on at least two legal non-teaching jobs, with no teaching-job action set equipped. Check ordinary Item with Pharmacology/Long Throw, original elemental actions with Attunement, movement before/after Composure and Follow Through, ally-applied status with Poise, and native HP-plus-MP costs with Bloodcasting. Compare each support against available vanilla alternatives in that race. Test healing across two units carrying Pharmacology and Recuperation, and spells/physical techniques alternating through Spellweave. New item modifiers must apply exactly once, including Auto-Potion.
8. Full release requires`);
axe=axe.replace(/^Design version[^\n]*/m,'Design version 0.4 — transferable support lessons, September 14, 2026. Expands vanilla USA FFTA; not implemented.');
axe=axe.replace('All twelve entries require a primary axe where their effect specifies it; all eight actions always require one.','All eight actions require a primary axe, and the two reactions retain their stated axe requirement. Recuperation and Follow Through are transferable supports with no weapon requirement.');
axe=axe.replace('Tomahawk + Axe Grip','Tomahawk + Recuperation');
axe=axe.replace('The twelve axe entries below remain provisional.','The twelve entries below remain provisional. [The support redesign](SUPPORT-SKILL-DESIGN.md) makes their two support lessons useful after switching weapons and jobs.');

const descriptions=[
['SAM-S1','Act before moving for stronger damage or healing.'],['SAM-S2','Take less damage while benefiting from a positive status.'],
['DRK-S1','Stronger physical and magical damage at low HP.'],['DRK-S2','Spend HP in place of MP for any eligible action.'],
['VIK-S1','Resist forced movement on any job.'],['VIK-S2','Deal more damage to enemies already suffering an ailment.'],
['GEO-S1','Improve elemental damage that strikes a weakness, from any command or weapon.'],['GEO-S2','Improve jumping and ignore added terrain movement costs.'],
['CHM-S1','Improve HP/MP restoration from ordinary items, mixtures, and item reactions.'],['CHM-S2','Throw ordinary items and other eligible consumables farther.'],
['BRD-S1','Adding a new beneficial status to another ally also heals them slightly.'],['BRD-S2','Protect any caster or singer from Silence.'],
['DNC-S1','Improve evasion with any weapon or job.'],['DNC-S2','Increase movement on any job.'],
['MYK-S1','Alternate magic and physical actions for stronger attacks.'],['MYK-S2','Reduce magical damage while keeping a healthy MP reserve.'],
['SLD-AX-S1','Receive stronger direct HP healing from any restorative source.'],['GLD-AX-S1','Move before attacking for stronger physical damage with any weapon.']
];
const overview=`# Supports for mixing jobs

Version 0.4 — September 14, 2026

**A job teaches a support; it does not own the support's usefulness.** These 18 proposals work after switching to another legal job, without keeping the teaching job's action set or special weapon equipped. The one support slot remains a meaningful choice. Racial access still applies: a Human cannot learn a Nu Mou-only job just to obtain its support.

Single Blade has been removed. Its single-weapon damage niche overlapped existing Doublehand/weapon-offense choices; **Composure** instead rewards choosing when to move and works for physical attacks, magic, and restorative techniques. Poise no longer requires Centered or a katana. The axe jobs' supports likewise require neither axes nor axe actions. Existing vanilla supports remain unchanged. [Original FFTA mechanics reference](https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262).

## Revised support list

Every effect and number is our proposal. The examples respect the teaching job's race access; they illustrate possible builds, not completed balance tests.

| Taught by | Support | General benefit | Examples outside the teaching job |
|---|---|---|---|
${descriptions.map(([id,desc])=>{const a=data.abilities.find(r=>r.id===id);return `| ${a.job} | ${a.name} | ${desc} | ${a.buildExamples} |`;}).join('\n')}

## What mixing means in practice

- A Human Archer can use **Composure** with Aim and another command, with no Iaido equipped. A Human mage can use the same support to cast before relocating. It rewards a tactical decision, not a particular weapon.
- A Moogle Gunner can take **Pharmacology** and ordinary Item for stronger emergency supplies. It does not need the Chemist command. A Nu Mou Alchemist can use the same item support through that race's Chemist access.
- A Nu Mou Black Mage can take **Attunement** without Geomancy; the trigger is exploiting an elemental weakness.
- A Viera Red Mage can take **Spellweave** and alternate spellcasting with physical Lunge Tech. A Mystic Knight can start that rhythm with an enchantment. Neither needs to hold a specified weapon for the support itself; each action still has its own equipment rules.
- A Bangaa Dragoon can take **Follow Through** and use its usual equipment. An allied debuffer can instead make **Opportunist** attractive. Those supports compete for one slot.

## Exact proposed effects

${data.abilities.filter(a=>a.type==='Support').map(a=>`### ${a.name} — ${a.job}, ${a.ap} AP\n\n${a.effect}\n`).join('\n')}

The full [class specification](JOB-CLASS-SPECIFICATION.md) defines timing, action categories, stacking, status tags, healing, and costs. Existing action equipment restrictions remain; support flexibility does not grant a character new weapons or cross-race jobs. Pharmacology, Long Throw, Attunement, and Spellweave require explicit integration with relevant original actions, not merely a whitelist of our new skills.

## Balance requirements

Each support must have two plausible uses outside its teaching job and compete with supports actually obtainable by that race. A percentage alone is not evidence of competitiveness. Check turn value, resource loops, damage formulas, item potency, buff availability, and secondary-command combinations at matched levels/equipment. Bloodcasting and Spellweave introduce new systems; confirm implementation and test their payoff before fixing the numbers.

No claim that all vanilla supports are universally usable is needed. Our design goal is broad mixing with meaningful conditions. The previous tendency to write “only this job's eight actions” into support descriptions is explicitly rejected. A future narrow support would need a compelling build reason rather than serving as a required tax on its own job's effectiveness.

The draft still has 116 ability entries and 72 teaching items. Support AP, teaching positions, roster, and unlock requirements are unchanged. No ROM is modified.
`;
fs.writeFileSync('SUPPORT-SKILL-DESIGN.md',overview);
fs.writeFileSync('JOB-CLASS-SPECIFICATION.md',spec);
fs.writeFileSync('AXE-SKILL-EXPANSION.md',axe);
fs.writeFileSync('notes/job-theme-audit.json',JSON.stringify(data,null,2)+'\n');
let register=fs.readFileSync('JOB-THEME-AUDIT.md','utf8');
register=register.replace('Version 0.3','Version 0.4');
register=register.replace('## Current entries and inspiration','All 18 support entries now follow [the cross-job support design](SUPPORT-SKILL-DESIGN.md). The teaching job grants access; the benefit applies across legal current jobs and appropriate original or new commands.\n\n## Current entries and inspiration');
for(const a of data.abilities){register=register.replace(new RegExp('^\\| '+a.id+' \\|.*$', 'm'),`| ${a.id} | ${a.previous??'—'} | ${a.name} | ${a.kind} | ${a.anchor}. [Inspiration][${a.ref}] |`);}
fs.writeFileSync('JOB-THEME-AUDIT.md',register);
let principles=fs.readFileSync('JOB-DESIGN-PRINCIPLES.md','utf8');
principles=principles.replace('Design direction 0.3','Design direction 0.4');
principles=principles.replace('The current eight-action/two-support/two-reaction template',`**Cross-job supports are a design requirement.** The teaching job supplies the lesson, not a permanent dependency. Most supports should work on multiple other jobs with different commands; our current 18 all meet that scope on paper. Avoid requirements for a specific action set, signature weapon, or exclusive job state. Give each support at least two plausible non-teaching-job uses within legal racial access. [Revised supports and examples](SUPPORT-SKILL-DESIGN.md).

The current eight-action/two-support/two-reaction template`);
principles=principles.replace('Its passives and reactions interact with this rhythm.','Its reactions interact with this rhythm. Its supports now benefit broader builds: Composure rewards acting before moving, and Poise recognizes beneficial statuses from any source.');
fs.writeFileSync('JOB-DESIGN-PRINCIPLES.md',principles);
let start=fs.readFileSync('START-HERE.md','utf8');
start=start.replace('The class specification is version 0.3; the axe detail remains version 0.2 under the new principles.','The class and axe specifications are version 0.4; [the support sheet](SUPPORT-SKILL-DESIGN.md) explains transferable skills and example builds.');
fs.writeFileSync('START-HERE.md',start);
let outline=fs.readFileSync('JOB-EXPANSION-DESIGN.md','utf8').replace('version 0.3 design principles','version 0.4 design principles');
outline=outline.replace('## Proposed unlock requirements','All 18 proposed supports now work beyond their teaching jobs; see [support skills and example builds](SUPPORT-SKILL-DESIGN.md). This preserves racial access and one support slot while removing job-set and signature-weapon dependencies.\n\n## Proposed unlock requirements');
fs.writeFileSync('JOB-EXPANSION-DESIGN.md',outline);
console.log(JSON.stringify({version:data.version,supportsReviewed:supports.length,totalAbilities:data.abilities.length}));
