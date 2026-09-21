import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8').replace(/\r\n/g,'\n');
const write=(f,s)=>fs.writeFileSync(path.join(root,f),s.endsWith('\n')?s:s+'\n');
const data=JSON.parse(read('notes/job-theme-audit.json'));
if(data.version!=='0.5') throw new Error('One-time migration requires version 0.5');
const docs=['JOB-CLASS-SPECIFICATION.md','AXE-SKILL-EXPANSION.md','SUPPORT-SKILL-DESIGN.md','JOB-DESIGN-PRINCIPLES.md','JOB-THEME-AUDIT.md','JOB-EXPANSION-DESIGN.md','START-HERE.md','STARTER-JOB-INSPIRATION.md','BALANCE-COUNCIL.md'];
fs.mkdirSync(path.join(root,'notes/design-v0.5'),{recursive:true});
for(const f of [...docs,'notes/job-theme-audit.json','notes/design-validation.json']) fs.copyFileSync(path.join(root,f),path.join(root,'notes/design-v0.5',path.basename(f)),fs.constants.COPYFILE_EXCL);
const newAbilities=[
 ['MYK-A9','Slow Spellblade',250,'12 MP; self/Sure OR r1 enemy/A. Immediate 0.80P non-elemental; future primary Fight remains ordinary power/non-elemental. After positive HP damage from either carrier attempt vanilla Slow at normal S. Magic sequencing; physical HP damage.','spellA2','Thematic redesign','FFTA2 Slow Blade adapted to a maintained enchantment; sustained single-target control.'],
 ['MYK-A10','Osmose Spellblade',300,'8 MP; self/Sure OR r1 enemy/A. Immediate 0.80P non-elemental; future primary Fight remains ordinary power/non-elemental. After positive HP damage siphon floor(25% of actual HP removed) MP, capped at 10 MP per action and target current MP; restore only MP actually removed, capped by user missing MP. No ally, overkill, absorbed-hit, or second-weapon siphon. Apply shared undead reversal. Spellweave never directly multiplies MP loss/recovery; increased actual HP damage may indirectly raise siphon only up to the same cap. Magic sequencing; physical HP damage.','spellV','Thematic redesign','FFV Osmose enchantment; limited enemy-funded endurance with a lower immediate strike.'],
 ['MYK-A11','Holy Spellblade',250,'12 MP; self/Sure OR r1 enemy/A. Immediate 1.00P Holy; persistent primary Fight becomes Holy. Normal elemental resistance, immunity, and absorption; no automatic undead kill or independent damage bonus. Magic sequencing; physical HP damage.','spellV','Thematic redesign','FFV Holy enchantment adapted as a distinct elemental matchup.'],
 ['MYK-A12','Spellbreak',250,'10 MP; r1 one enemy/A. 0.85P using ordinary primary weapon element; on a successful hit remove one selected dispellable beneficial status even if HP damage is zero. Select from eligible statuses before commitment; no eligible status means the action cannot be selected. Never removes equipment, passive lessons, fields, or undispellable boss effects. Preserve the user enchantment without applying its element, proc, drain, or Flare penetration. Physical sequencing and physical HP damage.','myk','Original extension','Original sword-delivered dispel: trade damage for removal of a selected magical protection.'],
 ['MYK-A13','Arcane Release',350,'14 MP plus consume an active Fire, Blizzard, Thunder, Holy, or Flare enchantment at commitment; r3 center/cross, Any, line of sight. M40 magical HP damage for elemental enchantments using their element; Flare instead gives M44 non-elemental magical damage with normal MRes and no WDef penetration. Use the ordinary damaging-spell hit resolution per target and preview it; immunity and defensive effects remain applicable. No Sleep, Poison, Silence, Slow, Drain, or Osmose release. No weapon proc, status rider, recovery, Reflect, Return Magic, or Doublecast. Enchantment is spent even if every target avoids or nullifies the burst; no Spell Parry fuel remains. Magic sequencing and magical HP damage.','myk','Original extension','Original discharge of maintained blade magic for range and area at the expense of sustain and parry fuel.'],
 ['MYK-A14','Break Blade',400,'24 MP; r1 one enemy/S. Attempt Petrify at normal S, respecting immunity and applicable defenses; no preliminary A roll and no HP damage. A sword-delivered magical technique, not an enchantment: does not create, consume, replace, or carry the existing enchantment. Magic sequencing; Spellweave cannot improve Petrify chance. No Reflect, Return Magic, or Doublecast.','spellV','Thematic redesign','FFV Break Spellblade inspiration adapted to a separately paid Petrify technique, not persistent Petrify on Fight.']
].map(([id,name,ap,effect,ref,kind,anchor])=>({id,name,ap,effect,ref,kind,anchor,type:'Action',job:'Mystic Knight',introducedVersion:'0.6',parameterStatus:'Provisional numerical/teaching targets; concept and Spellweave category approved by user.',balanceRationale:anchor,balanceSource:'SPELLBLADE-EXPANSION.md',balanceVerdict:'Approved concept; new tuning requires playtesting'}));
data.version='0.6';
data.scope='Version 0.5 council foundation plus six user-approved Mystic Knight actions and explicit Spellweave categories: 122 entries. New costs, AP, formulas and teaching targets are provisional; no implemented or gameplay-tested patch.';
data.sources.spellV=['FFV Spellblade repertoire','https://finalfantasy.fandom.com/wiki/Spellblade_(Final_Fantasy_V)'];
data.sources.spellA2=['FFTA2 Spellblade repertoire','https://finalfantasy.fandom.com/wiki/Spellblade_(Tactics_A2)'];
const insertAt=data.abilities.findIndex(a=>a.id==='MYK-S1');
data.abilities.splice(insertAt,0,...newAbilities);
let spec=read('JOB-CLASS-SPECIFICATION.md');
spec=spec.replace('Design version 0.5 — adopted council balance pass','Design version 0.6 — expanded Spellblade on the adopted council foundation');
spec=spec.replace('including all 116 entries, cross-class rules, AP, and teaching data.','The version 0.5 foundation retains its 116 entries; six approved Spellblade additions bring the current total to 122. [Spellblade expansion](SPELLBLADE-EXPANSION.md) records the new concepts, categories, and provisional numerical/teaching targets.');
const context=`**Spellblade — Viera.** All 14 actions require a primary rapier/saber and are blocked by Silence. Only the eleven enchantments (MYK-A1–A11) offer self preparation (Sure) or one r1 enemy for an immediate enchanted A-type strike. Pay once; apply/replace the enchantment even if the strike misses; this is one action, not a free second action or movement. Their strike is physical and not Fight: no crit, weapon proc, second weapon, Doublecast, or automatic bypass of applicable defensive reactions. Spellbreak, Arcane Release, and Break Blade follow their own targeting and resolution below; they never automatically enchant the weapon.

One enchantment persists until replaced, Dispel, KO, Petrify, primary weapon change/loss, job change, battle end, Spell Parry consumption, or Arcane Release consumption. Silence after preparation prevents command actions but does not erase it or stop Fight. Future benefits apply only to primary Fight, replacing its ordinary element/proc; no secondary technique, counter, combo, or second weapon inherits a rider. Arcane Release explicitly consumes a permitted enchantment for its own magical formula, not an inherited Fight rider. Healer cannot become damaging/draining.

Each action establishes at most one Spellweave category. Both modes of every enchantment establish Magic; the strike still deals physical HP damage. Enchanted Fight and Spellbreak establish Physical. Arcane Release and Break Blade establish Magic. The burst deals magical HP damage; Break Blade has no HP damage and cannot receive a Petrify-chance bonus. Follow an enchantment with Fight/Lunge/Spellbreak to alternate, not Red Magic or Arcane Release. Battle Chant/Fury can improve an enchantment strike; Wisp/Inspired Magic cannot. Those magical bonuses can instead improve Arcane Release. Spell Parry spends the enchantment for 50% physical reduction against one enemy action. Red Mage/Spellblade, Fencer/Spellblade, and Dancer/Spellblade work with rapiers; Assassin/Summoner lack qualifying normal weapons.

The six additions' concepts and sequence categories are approved. Their costs, AP, exact powers, and teaching placements below are provisional first implementation targets. The original eight entries, supports, reactions, growths, and unlocks retain their adopted tuning. See [the expansion record](SPELLBLADE-EXPANSION.md) for sequence examples and resource tests.`;
const start=spec.indexOf('**Spellblade — Viera.**');
const end=spec.indexOf('### Actions',start);
spec=spec.slice(0,start)+context+'\n\n'+spec.slice(end);
const oldA8=spec.split('\n').find(l=>l.startsWith('| MYK-A8 '));
spec=spec.replace(oldA8,oldA8+'\n'+newAbilities.map(a=>`| ${a.id} ${a.name} | ${a.ap} | ${a.effect} | ${a.kind}: ${a.anchor} [Inspiration][${a.ref}] |`).join('\n'));
const support=data.abilities.find(a=>a.id==='MYK-S1');
const oldSupport=support.effect;
support.effect+=' Enchanted Fight and Spellbreak establish Physical; Arcane Release and Break Blade establish Magic. Arcane Release deals magical HP damage; Break Blade has no HP damage. No bonus to status accuracy or directly to MP damage/recovery; increased actual HP damage can indirectly raise capped drain/siphon recovery once. An enchanted hit never establishes both categories or triggers its own bonus.';
spec=spec.replace(oldSupport,support.effect);
spec=spec.replace('Eight teaching weapons per new job make 64, plus eight Soldier/Gladiator axes: **72 teaching items**. W1–W8 teach A1–A8.','The original W1–W8 tables supply 64 job weapons; six additional Mystic Knight teaching sabers and eight Soldier/Gladiator axes bring the total to **78 teaching items**. W1–W8 teach A1–A8.');
spec=spec.replace('| Mystic Knight | 1600 | 650 | 650 | 100 | 3000 |','| Mystic Knight | 3400 | 650 | 650 | 100 | 4800 |');
const gear=`### Additional Mystic Knight teaching sabers

These are parallel lessons within existing shop tiers, not six stronger endgame tiers. Only Mystic Knight learns these lessons; learned actions transfer normally with a legal weapon. No extra support/reaction lessons or changes to W1–W8. All six use ordinary saber handedness, with zero other bonuses and no innate element/proc/status. Story-flag mapping and item-record capacity remain unverified.

| New saber | Lesson | AP | Weapon Attack | Gil | Shop tier |
|---|---|---:|---:|---:|---|
| Hourglass Saber | MYK-A9 Slow Spellblade | 250 | 30 | 1600 | First expansion |
| Aether Saber | MYK-A10 Osmose Spellblade | 300 | 34 | 2400 | Second expansion |
| Dawn Saber | MYK-A11 Holy Spellblade | 250 | 38 | 3400 | Second expansion |
| Severance Saber | MYK-A12 Spellbreak | 250 | 26 | 1000 | First expansion |
| Prism Saber | MYK-A13 Arcane Release | 350 | 34 | 2400 | Second expansion |
| Stone Saber | MYK-A14 Break Blade | 400 | 46 | 6500 | Last pre-final-story expansion |

The additional 1,800 action AP represents optional breadth; it is not required before Mystic Knight becomes useful. Existing prerequisite counts stay unchanged. Check whether broader mastery opportunities accelerate any downstream access before proposing gate changes.

`;
spec=spec.replace('## 13. Implementation and balance validation',gear+'## 13. Implementation and balance validation');
spec=spec.replace("Version 0.5 is the user's adopted council design", "Version 0.6 contains the user's adopted council design and approved Spellblade expansion");
spec=spec.replace('Match all 72 teaching items','Match all 78 teaching items');
spec+='\n[spellV]: '+data.sources.spellV[1]+'\n[spellA2]: '+data.sources.spellA2[1]+'\n';
write('JOB-CLASS-SPECIFICATION.md',spec);
data.commandRules.MYK=context;
write('notes/job-theme-audit.json',JSON.stringify(data,null,2));
write('SUPPORT-SKILL-DESIGN.md',read('SUPPORT-SKILL-DESIGN.md').replace('Version 0.5 — adopted council balance pass','Version 0.6 — council foundation and expanded Spellweave clarification').replace(oldSupport,support.effect));
let theme=read('JOB-THEME-AUDIT.md').replace('Version 0.5 — adopted council balance pass','Version 0.6 — council foundation and Spellblade expansion').replace('All 116 stable IDs are retained.','All 116 prior stable IDs are retained; MYK-A9–A14 bring the current register to 122 entries.');
const themeA8=theme.split('\n').find(l=>l.startsWith('| MYK-A8 |'));
theme=theme.replace(themeA8,themeA8+'\n'+newAbilities.map(a=>`| ${a.id} | — (new in 0.6) | — (new in 0.6) | ${a.name} | ${a.kind} | ${a.anchor} [Inspiration][${a.ref}] |`).join('\n'));
theme+='\n[spellV]: '+data.sources.spellV[1]+'\n[spellA2]: '+data.sources.spellA2[1]+'\n';
write('JOB-THEME-AUDIT.md',theme);
let principles=read('JOB-DESIGN-PRINCIPLES.md');
const duplicate=principles.indexOf('## Adopted council balance pass',principles.indexOf('## Adopted council balance pass')+1);
if(duplicate>=0) principles=principles.slice(0,duplicate).trim()+'\n';
principles=principles.replace('Design direction 0.5 — adopted council balance pass','Design direction 0.6 — council foundation and variable command sizes');
principles=principles.replace('The current eight-action/two-support/two-reaction template is a working size, not a creative requirement. We can merge redundant entries or add a genuinely useful option. Counts and teaching equipment must be updated with any such change. No quota of canonical names is required.','**There is no uniform action-count requirement.** Mystic Knight now has 14 actions; other jobs may retain eight or gain more when each addition earns a distinct decision. Neither 8 nor 14 is a target for every job. Audit role overlap, legal secondary builds, acquisition, AP burden, and menu clarity before expanding a kit. More actions do not automatically justify more supports or reactions. Counts, teaching equipment, and data validation must track each adopted change.');
principles+='\n## Approved Spellblade expansion (0.6)\n\nSix additions—Slow, Osmose, Holy, Spellbreak, Arcane Release, and Break Blade—bring Mystic Knight to 14 actions and the project to 122 entries/78 teaching items. Enchantments sequence as Magic while their strikes deal physical damage; enchanted Fight and Spellbreak sequence as Physical; Release and Break sequence as Magic. Release alone deals magical HP damage, while Break has no HP damage. [Expansion record](SPELLBLADE-EXPANSION.md). New numeric and teaching targets are provisional. Further council candidates remain proposals until adopted.\n';
write('JOB-DESIGN-PRINCIPLES.md',principles);
write('JOB-EXPANSION-DESIGN.md',read('JOB-EXPANSION-DESIGN.md').replaceAll('design 0.5','design 0.6').replace('version 0.5 design principles','version 0.6 design principles').replace('all 116 entries','all 122 entries'));
let home=read('START-HERE.md');
home=home.slice(0,home.indexOf('Start with [the design principles]'))+'Start with [the design principles](JOB-DESIGN-PRINCIPLES.md): preserve each job\'s spirit and design its mechanics for FFTA. [The full class specification](JOB-CLASS-SPECIFICATION.md) is version 0.6 and covers jobs, prerequisites, abilities, growths, and equipment. [The axe addendum](AXE-SKILL-EXPANSION.md) retains the adopted version 0.5 rules; [the support sheet](SUPPORT-SKILL-DESIGN.md) includes the expanded Spellweave categories.\n\nThe [original council balance pass](BALANCE-COUNCIL.md) explains the 116-entry foundation. The [approved Spellblade expansion](SPELLBLADE-EXPANSION.md) adds six actions, bringing the design to 122 abilities and 78 teaching items. New numerical and teaching targets are provisional. These are design documents, not an installed patch.\n';
write('START-HERE.md',home);
write('BALANCE-COUNCIL.md',read('BALANCE-COUNCIL.md').replace('## Read the detailed proposals','**Subsequent approved expansion:** [Version 0.6 Spellblade](SPELLBLADE-EXPANSION.md) adds six actions and clarifies sequence categories. This report preserves the original 116-entry review; the current specification has 122 entries.\n\n## Read the detailed proposals'));
write('SPELLBLADE-EXPANSION.md',`# Spellblade expansion — version 0.6

September 14, 2026. Approved concepts and Spellweave categories; new costs, AP, powers, and teaching placements are provisional first implementation targets. No ROM changes or gameplay-test claims.

## What the user approved

Mystic Knight grows from eight to fourteen actions: retain Fire, Blizzard, Thunder, Poison, Sleep, Silence, Drain, and Flare; add Slow, Osmose, Holy, Spellbreak, Arcane Release, and Break Blade. Existing racial access, progression, growths, supports, reactions, and equipment categories remain. Command size follows meaningful choices rather than a common quota. The exact current rows live in [the class specification](JOB-CLASS-SPECIFICATION.md#11-mystic-knight--viera).

## Spellweave classification

| Action | Sequence category | Damage / rider |
|---|---|---|
| Self enchantment | Magic | No damage; establishes category |
| Enchant and strike | Magic | Physical HP damage; one action and one evaluation |
| Enchanted Fight | Physical | Physical HP damage with primary-weapon enchantment |
| Spellbreak | Physical | Physical HP damage plus selected dispel; no enchantment rider |
| Arcane Release | Magic | Magical HP damage; consumes eligible enchantment |
| Break Blade | Magic | Petrify attempt only; no HP damage or accuracy bonus |

First qualifying action has no bonus. A subsequent opposite-category action gets ×1.35 eligible direct HP damage. Same-category actions receive no bonus; misses still establish their category. Wait/unclassified actions retain the previous category without a bonus. No action establishes both categories or triggers its own bonus.

Example: Fire enchant-and-strike (Magic, no opening bonus) → Fight (Physical, ×1.35) → Slow enchant-and-strike (Magic, ×1.35 HP damage) → Fight (Physical, ×1.35). Fire → Blizzard or Fire → Red Magic is Magic → Magic and receives no alternation bonus. Fight → Arcane Release alternates, but Release → another enchantment does not.

Status accuracy never improves. MP siphon has no direct Spellweave multiplier: like HP Drain, more actual HP damage can indirectly raise its computed recovery, then its unchanged cap applies. No second recovery multiplier. Spellbreak and an enchanted strike still use physical defenses and physical damage bonuses despite different sequence categories; only Release uses magical defenses/bonuses. New actions remain ineligible for Doublecast.

## Breadth and mixing

Slow offers persistent single-target disruption; Dancer retains area control. Osmose trades another enchantment's benefits for bounded enemy-funded endurance. Holy supplies another matchup. Spellbreak removes one selected magical protection without requiring an enchantment. Release spends sustained offense and Spell Parry fuel for a ranged small area; its friendly fire and magical scaling matter. Break is a separate paid single-target Petrify attempt, never reusable Petrify attached to Fight.

Red Mage/Spellblade can use Osmose to support later original spells but cannot Doublecast a new ability. Fencer/Spellblade and Dancer/Spellblade gain dispel and release with a rapier; accumulated magical stats affect Release. Neither Assassin nor Summoner gains qualifying weapons by equipping the secondary command. One support slot means Spellweave, Concentrate, Half MP, and other alternatives compete; Spellweave is not required for a functional kit.

## Acquisition and validation

Six parallel teaching sabers add 1,800 action AP without raising the existing weapon-power ceiling. Mystic Knight totals 3,400 action AP and 4,800 AP overall. Current project totals: 122 abilities (78 actions, 18 supports, 18 reactions, eight combos), 78 teaching items. Original 0.5 files are archived in notes/design-v0.5.

Check enchant-and-hit miss persistence; one category per action; release expenditure on nullification/miss and loss of parry fuel; no status/drain area release; ordinary weapon versus enchantment element on Spellbreak; selected dispel availability; single S roll and immunity for Break; MP siphon at zero target MP/full user MP/undead/overkill; indirect siphon increase under Spellweave capped at 10 MP; Half MP and Clear Voice eligibility; Fury versus magic amplification; AP/shop access; actual job-list/save/item capacity for more than eight actions. Shared laws, payment, reflection, reactions and equipment rules remain applicable. These are required tests, not reported gameplay results.

## Inspiration versus invention

Slow Blade comes from [FFTA2 Spellblade](${data.sources.spellA2[1]}). Osmose, Holy, and Break have [FFV Spellblade precedent](${data.sources.spellV[1]}). Our persistent Slow implementation, costs, damage, caps, paid Break technique, Spellbreak, and Arcane Release are adaptations or original design. Source-game behavior does not dictate the mechanics here.
`);
console.log('Updated design to 0.6; six approved actions and related docs written.');
