import fs from 'node:fs';

// Historical v0.3 transformation; later support design must not be overwritten.
if (!process.argv.includes('--restore-v0.3')) throw new Error('Archived v0.3 transformation. Current design is v0.4; explicit restoration flag required.');

const data = JSON.parse(fs.readFileSync('notes/job-theme-audit.json','utf8'));
const changes = new Map();
function change(id,name,effect,extra={}) {
  const old=data.abilities.find(a=>a.id===id);
  if(!old) throw new Error('Missing ability '+id);
  changes.set(id,{...old,priorRevision:old.name,name,effect,kind:'Thematic redesign',...extra});
}
change('SAM-A1','Ashura','1.10P non-elemental; after positive damage gain Centered. This action cannot consume or benefit from Centered.',{cost:'4 MP',target:'r1, one enemy; A',anchor:'Decisive draw that builds composure; original attack-and-prepare mechanic'});
change('SAM-A2','Wind Draw','0.95P Wind per target. Can spend Centered for its damage bonus.',{cost:'6 MP',target:'Line 3, enemies; A',anchor:'Original cutting wind released through katana technique'});
change('SAM-A3','Osafune','0.85P non-elemental; after positive damage remove up to 10 MP from the target. No MP recovery. Centered boosts HP damage only.',{cost:'6 MP',target:'r2, one enemy; A',anchor:'MP-cutting blade spirit redesigned to also contribute HP damage'});
change('SAM-A4','Murasame','Restore 25% target maximum HP, capped at 100 HP per target before Centered. Centered multiplies that capped amount by 1.25; final recovery is capped by missing HP.',{cost:'8 MP',target:'r2 center, cross, allies including self; Sure',anchor:'Healing blade spirit, with reach and scaling chosen for frontline support'});
change('SAM-A5','Kiyomori','Apply Protect and Shell. Does not consume Centered.',{cost:'10 MP',target:'Self cross, allies including self; Sure',anchor:'Protective blade spirits; group defense earns its action through multiple allies'});
change('SAM-A6','Guarding Draw','0.90P non-elemental; after positive damage apply Protect to self. Can spend Centered for its damage bonus.',{cost:'6 MP',target:'r1, one enemy; A',anchor:'Original guarded sword strike that combines pressure with self-protection'});
change('SAM-A7','Kiku-ichimonji','1.30P non-elemental. Can spend Centered for its damage bonus.',{cost:'12 MP',target:'r3, one enemy; A',anchor:'Far-reaching blade spirit redesigned as a precise ranged finisher'});
change('SAM-A8','Moon Blossom','1.35P non-elemental per target; after damaging at least one enemy, apply Regen to self. Centered boosts the whole action once.',{cost:'16 MP',target:'Self cross, enemies; A',anchor:'Original culminating spirit release, with offensive and sustaining roles'});
change('SAM-S1','Single Blade','Physical HP damage dealt ×1.15 with exactly one katana and no shield, including damaging Iaido. Does not boost healing.',{anchor:'Single-weapon discipline supporting both ordinary attacks and job techniques'});
change('SAM-S2','Poise','While Centered and holding a katana, physical HP damage received ×0.85. Check at the start of the incoming action. Spending Centered ends this protection.',{anchor:'Original defensive use of maintained composure'});
change('SAM-R1','Blade Ward','Requires katana. 40% pre-hit activation: incoming enemy physical HP damage ×0.70 for that action, including physical A-abilities. No counter.',{anchor:'Original blade defense with a broader trigger than a Fight-only evasion move'});
change('SAM-R2','Counter Draw','After surviving adjacent enemy physical HP damage, 35% activation: counter once for 0.70P non-elemental, A accuracy. Requires katana. Positive counter damage grants Centered; the counter cannot consume or benefit from Centered.',{anchor:'Original reactive draw that prepares the next deliberate technique'});

change('GEO-A1','Stone Pulse','M26 Earth. Rock affinity increases damage ×1.20.',{cost:'4 MP',target:'r3 center, cross, any units except caster; A',anchor:'Original reliable earth pressure; terrain rewards damage rather than unlocking the spell'});
change('GEO-A2','Tanglevine','M24 non-elemental; after positive damage attempt Immobilize with S. Vegetation affinity adds 15 percentage points to the final S chance, capped at 95% before defensive reductions; immunity still wins.',{cost:'6 MP',target:'r3, one enemy; A then S',anchor:'Binding vegetation with a useful damage baseline and a stronger native control effect'});
change('GEO-A3','Torrent','M28 Water. With water affinity, after positive damage push each target one tile in the chosen cardinal direction if legal. Blocked displacement leaves damage intact.',{cost:'8 MP',target:'r3 center, cross, any units except caster; A',anchor:'Original wave control that breaks formations rather than copying a transformation rider'});
change('GEO-A4','Updraft','Apply Float and Move +1 for T2. If caster stands at least two height units above target, also grant Jump +1 for T2. No immediate movement, flight, or new permission to occupy impassable tiles. Float uses its normal status removal rules.',{cost:'6 MP',target:'r3, one ally or self; Sure',anchor:'Original wind assistance; positioning and traversal utility'});
change('GEO-A5','Earthen Ward','Apply Protect. With rock affinity, also prevent forced displacement for T2. Does not prevent voluntary movement or Immobilize.',{cost:'10 MP',target:'r3 center, cross, allies including self; Sure',anchor:'Original earth protection that steadies an allied formation'});
change('GEO-A6','Wisp Flame','M28 Fire; after positive damage inflict Wisp Exposure for T2: magical HP damage received ×1.15. Wood/heat affinity instead applies ×1.25. This new debuff has no second success roll; immunity to the new effect prevents the rider, not damage.',{cost:'10 MP',target:'r3, one enemy; A',anchor:'Original spirit flame that creates an opening for allied magic'});
change('GEO-A7','Rime Field','M28 Ice, then place a frost field on the targeted cross even if damage misses. Entering a field tile costs one additional Move point for any grounded unit, including allies. Ice affinity also attempts Slow with S after positive damage.',{cost:'12 MP',target:'r3 center, cross, any units except caster; A',anchor:'Original persistent ice terrain for area denial; native ice adds further control'});
change('GEO-A8','Gaia Surge','M40 with an element selected from available nearby affinities: Earth for rock, Water for water, Fire for wood/heat, Ice for ice. Wind is always available. No affinity is consumed; this action has no additional native damage bonus.',{cost:'18 MP',target:'r4 center, cross, any units except caster; A',anchor:'Original major nature release whose elemental options respond to surroundings'});
change('GEO-S1','Terrain Lore','Geomancy HP damage ×1.15 when using an action with its relevant affinity. Gaia Surge qualifies only when using an affinity-derived element, never its default Wind. Does not further boost status chance, Wisp Exposure magnitude, healing, or fields.',{anchor:'Environmental mastery amplifies the toolkit without making its baseline dependent on a support slot'});
change('GEO-S2','Surefoot','Jump +1 and ignore Rime Field\'s added movement cost. Does not ignore every terrain penalty or grant flight.',{anchor:'Original traversal mastery that interacts with the job\'s own created terrain'});
change('GEO-R1','Stone Skin','After surviving enemy physical HP damage, 40% activation: apply Protect to self. Works on any terrain.',{anchor:'Original earthen defense with a dependable opportunity to contribute across maps'});
change('GEO-R2',"Nature's Wrath",'After surviving enemy HP damage, 35% activation: counter that attacker alone within r3 for M20, A accuracy. Choose the element of the highest-AP learned damaging Geomancy action; Gaia Surge uses the selected current affinity if available, otherwise Wind. No ailment, field, displacement, or Terrain Lore bonus. No learned damaging action means no counter.',{anchor:'Reactive nature power; neither terrain permission nor a tiny status chance is required for its contribution'});
change('VIK-A8','Tsunami','M36 Water on any terrain. If mapped water occupies the caster tile or an orthogonally adjacent tile within 2 height, successful positive damage also removes up to 8 MP per target. No MP recovery and no water-movement permission.',{cost:'18 MP',target:'r4 center, cross, any units; A',anchor:'Sea power redesigned to function on land, with water proximity enhancing its effect'});

data.version='0.3';
data.date='2026-09-14';
data.scope='Theme-led FFTA design. Sources document inspiration, not mandatory abilities or balance. Samurai/Geomancer redesigned; other values remain provisional.';
data.designPrinciples='JOB-DESIGN-PRINCIPLES.md';
data.abilities=data.abilities.map(a=>changes.get(a.id)??a);
const cureall=data.abilities.find(a=>a.id==='CHM-A7');
cureall.effect=cureall.effect.replace('Polka, Heathen Frolic, and Exposed modifiers','Polka, Heathen Frolic, Exposed, and Wisp Exposure modifiers');
const origin=a=>`${a.kind}: ${a.anchor}. [Inspiration][${a.ref}]`;
const format = id => {
  const rows=data.abilities.filter(a=>a.id.startsWith(id+'-'));
  const acts=rows.filter(a=>a.type==='Action'), ps=rows.filter(a=>a.type==='Support'||a.type==='Reaction');
  const c=rows.find(a=>a.type==='Combo');
  return `| ID / action | AP | Cost | Target / hit | Proposed effect | Inspiration |\n|---|---:|---|---|---|---|\n`+acts.map(a=>`| ${a.id} ${a.name} | ${a.ap} | ${a.cost} | ${a.target} | ${a.effect} | ${origin(a)} |`).join('\n')+'\n\n'+`| ID / passive | Type | AP | Effect while equipped | Inspiration |\n|---|---|---:|---|---|\n`+ps.map(a=>`| ${a.id} ${a.name} | ${a.type} | ${a.ap} | ${a.effect} | ${origin(a)} |`).join('\n')+`\n\n**${c.id} ${c.name} — ${c.ap} AP:** ${c.effect}\n\n`;
};
let spec=fs.readFileSync('JOB-CLASS-SPECIFICATION.md','utf8');
function section(start,end,value){const a=spec.indexOf(start),b=spec.indexOf(end,a);if(a<0||b<0)throw Error('Missing section '+start);spec=spec.slice(0,a)+value+spec.slice(b);}
section('## 4.','## 5.',`## 4. Samurai — Human

**Command: Iaido.** A disciplined katana fighter who turns composure into decisive techniques and protective blade spirits. All actions require a primary katana. Its identity draws on the [Samurai tradition][sam], while the kit below is designed around FFTA's action economy.

All damaging Iaido uses **P and physical damage**, including spiritual attacks; sword training and equipment drive its offense. Murasame uses the target's maximum HP. Magic Power is not a second offensive requirement. Silence, Reflect, Return Magic, and Doublecast do not apply. After mastery, any equipped katana can use a learned technique; no sword breakage or matching spare blade is required.

**Centered:** a visible, non-stacking T2 buff granted by a successful Ashura or Counter Draw. It is an action/reaction effect, not a free innate passive. The next damaging Iaido other than Ashura, or Murasame, consumes it at execution and gains ×1.25 HP damage or healing for that whole action. A miss still spends it. It does not enhance MP damage, status chance, Fight, counters, combos, Kiyomori, or secondary sets. Kiyomori can be used while holding it. Lose Centered on expiry, Dispel, KO, Petrify, battle end, job change, or a change/loss of primary weapon.

${format('SAM')}**How it plays:** Ashura contributes damage while preparing a stronger follow-up. Spend Centered on a line attack, ranged strike, close-area finisher, or allied healing; with Poise, holding it has defensive value. Guarding Draw provides a useful defensive turn without giving up all pressure. Range, target count, and resource needs distinguish the eight actions. These are prototype values, not proof that the kit outperforms or matches any vanilla build.

`);
section('## 7.','## 8.',`## 7. Geomancer — Nu Mou

**Command: Geomancy.** A battlefield controller who shapes natural forces to damage enemies, protect allies, and influence movement. The [landscape-magic tradition][geo] supplies its identity. Every learned action works on ordinary terrain; local affinity provides an additional advantage instead of permission to use the skill.

No weapon required. Damaging actions use Magic Power and Magic Resistance. Silence, Reflect, Return Magic, and Doublecast do not apply. Stronger baseline actions now spend MP. Standard damage/target rules apply; only Tanglevine and native Rime Field make their listed additional status checks.

**Nearby affinity:** check the caster's tile and four orthogonal neighboring tiles within 2 height. Relevant mapped groups are rock/stone, vegetation, water/wetland, wood/heat, and snow/ice. An action gets at most one instance of its bonus. Neighbors can be inaccessible to the caster; sensing water does not let a unit enter it. Unknown tiles supply no affinity but disable no action. For Gaia Surge, choose one eligible element in the preview; Wind is always eligible. An element-aware effect such as Nature's Wrath reuses the last chosen eligible Gaia element, otherwise Wind. Float does not stop nearby attunement.

**Frost field:** Rime Field creates one cross of affected ground per caster; replacing it removes that caster's previous field. Expire it at the end of the caster's second subsequent turn, excluding placement turn; caster KO, Petrify, job change, or battle end clears it. Overlapping fields charge only one extra movement point per entered tile. Float/flying units and equipped Surefoot ignore that extra cost. It causes no falling damage, new impassability, entry damage, or reaction triggers. It does not change a tile's affinity or enable a bonus to the cast that created it. Show affected tiles and adjusted movement paths. This is a new mechanic requiring implementation work.

Wisp Exposure refreshes rather than stacks; the stronger magnitude wins and a weaker cast cannot refresh a stronger one. It is removable by our broad-remedy handling for custom harmful effects. Elemental immunity or absorption prevents damage-triggered riders; stated status/custom-effect immunity still applies. Earthen Ward's displacement protection uses the strongest existing equivalent, not a second stack.

${format('GEO')}**How it plays:** use Stone Pulse for dependable area pressure, Tanglevine to threaten a key mover, Torrent to break a formation, or Rime Field to make an approach costly. Updraft and Earthen Ward help the party exploit that control; Wisp Flame creates a magic-damage opening. Gaia Surge supplies a substantial finish with environmentally influenced coverage. MP, friendly fire, enemy defenses, and a single active field constrain the kit. Damage power and field duration must be compared with actual FFTA encounters.

`);
spec=spec.replace(/^Design version 0\.[23][^\n]*/m,'Design version 0.3 — identity and gameplay, September 14, 2026');
spec=spec.replace(/^\| CHM-A7 .*$/m,`| ${cureall.id} ${cureall.name} | ${cureall.ap} | ${cureall.cost} | ${cureall.target} | ${cureall.effect} | ${origin(cureall)} |`);
spec=spec.replace(/\*\*Our expansion of vanilla USA FFTA\.\*\*[^\n]*/,"**Our expansion of vanilla USA FFTA.** Preserve each job's spirit and make its abilities useful in FFTA. [The design principles](JOB-DESIGN-PRINCIPLES.md) supersede the previous emphasis on copying source-game skill lists. Samurai and Geomancer have redesigned kits; the remaining kits are provisional under the same standard. All numbers still need playtesting.");
spec=spec.replace('Every entry has a source and a lineage label.','Every entry has an inspiration reference and a lineage label; matching a canonical ability is not required.');
spec=spec.replace('- **Adaptation** uses a documented Final Fantasy ability and preserves its defining role, while changing costs, range, success rate, or other specified details for FFTA.','- **Adaptation** starts from a documented Final Fantasy ability. Its exact effect can change to suit this job and FFTA. **Thematic redesign** develops a new mechanic from the broader identity; a familiar name does not promise a direct port.');
spec=spec.replace("A familiar name is not enough: element, target, resource, and effect must match its cited interpretation or the change must be explicit.","Theme and gameplay govern the design. We can change elements, targets, costs, formulas, scaling, and restrictions, or invent a new technique; the table describes our actual effect and the reference only explains inspiration.");
spec=spec.replace('Each new job has 8 A, 2 S, 2 R, and 1 combo lesson.','The current working lists have 8 A, 2 S, 2 R, and 1 combo lesson per job. This is a provisional size, not a requirement to fill slots or preserve redundant skills.');
spec=spec.replace('| Human Samurai | 7.0 | 3.0 | 8.0 | 8.0 | 8.2 | 7.2 | 1.4 |','| Human Samurai | 7.2 | 2.8 | 8.6 | 8.0 | 6.8 | 7.2 | 1.4 |');
spec=spec.replace('| Human Samurai | 36 | 30 | 80 | 80 | 82 | 72 | 106 |','| Human Samurai | 36 | 28 | 86 | 80 | 68 | 72 | 106 |');
spec=spec.replace('| Nu Mou Geomancer | 6.6 | 3.0 | 5.8 | 7.0 | 8.6 | 8.6 | 1.0 |','| Nu Mou Geomancer | 6.6 | 3.6 | 5.8 | 7.0 | 8.6 | 8.6 | 1.0 |');
spec=spec.replace('| Nu Mou Geomancer | 33 | 30 | 58 | 70 | 86 | 86 | 97 |','| Nu Mou Geomancer | 33 | 36 | 58 | 70 | 86 | 86 | 97 |');
spec=spec.replace(/Thematic growth revisions:[^\n]*/,"Growth alignment: Samurai's offense now develops through Weapon Attack, avoiding a second mandatory damage stat; Geomancer has MP growth for its stronger, resource-using toolkit. The other new-job growths remain provisional. These are our design targets. Soldier and Gladiator retain their original growths and armor permissions.");
spec=spec.replace('| Samurai / Katana | Ashura Echo | Kotetsu Echo | Osafune Echo | Murasame Echo | Kiyomori Echo | Muramasa Echo | Kiku Echo | Masamune Echo |','| Samurai / Katana | Ashura Echo | Wind Reed | Osafune Echo | Murasame Echo | Kiyomori Echo | Guarding Blade | Kiku Echo | Moonblossom |');
spec=spec.replace('| Geomancer / Rod | Zephyr Rod | Soil Rod | Root Rod | River Rod | Cairn Rod | Wisp Rod | Rime Rod | Magma Rod |','| Geomancer / Rod | Stone Rod | Root Rod | River Rod | Zephyr Rod | Wardstone Rod | Wisp Rod | Rime Rod | Gaia Rod |');
const ts=data.abilities.find(a=>a.id==='VIK-A8');
spec=spec.replace(/^\| VIK-A8 .*$/m,`| ${ts.id} ${ts.name} | ${ts.ap} | ${ts.cost} | ${ts.target} | ${ts.effect} | ${origin(ts)} |`);
spec=spec.replace('Water access constrains Tsunami.','Water proximity enhances Tsunami; the wave is useful on land too.');
spec=spec.replace(/Terrain requires an audited tile-ID map across campaign battles\.[^\n]*/,"Terrain requires a tile-ID affinity map and a new field implementation. Unknown tiles provide no affinity; the complete base toolkit remains available. Verify field expiry, overlapping fields, path costs, Float/Surefoot, chosen elemental previews, and terrain heights. Tsunami does not grant water movement. Item effects, stealing, Invisible, status cures, and drain behavior require clean-ROM confirmation. No data-only implementation is assumed.");
spec=spec.replace('Persistent Flare Spellblade, zero-MP Geomancy, Haste/Regen Masamune, MP songs, drain loops, theft, and Gil Snapper','Persistent Flare Spellblade, MP-funded Geomancy, Centered technique chains, magic vulnerability, persistent fields, MP songs, drain loops, theft, and Gil Snapper');
if(!spec.includes('Verify Centered spending/expiry')) spec=spec.replace('no permanent stat gains from Fury or Magick Boost.','no permanent stat gains from Fury or Magick Boost. Verify Centered spending/expiry and weapon changes; Updraft buffs do not stack on repeated casts.');
spec=spec.replace('Source references support the lineage column, not the invented balance numbers.',"Source references document inspiration. They do not dictate the kit, and no source game is treated as a balance standard.");
// Updraft is expressly timed, unlike the default duration for existing statuses.
spec=spec.replace('Use vanilla durations, immunity, removal, and stacking for named existing statuses.','Use vanilla durations, immunity, removal, and stacking for named existing statuses unless an action explicitly specifies another duration.');

fs.writeFileSync('JOB-CLASS-SPECIFICATION.md',spec);
fs.writeFileSync('notes/job-theme-audit.json',JSON.stringify(data,null,2)+'\n');

const sources='\n'+Object.entries(data.sources).map(([key,[,url]])=>`[${key}]: ${url}`).join('\n')+'\n';
const audit=`# Job inspiration and design register

Version 0.3 — September 14, 2026

**Theme guides the job; FFTA gameplay guides its mechanics.** The [design principles](JOB-DESIGN-PRINCIPLES.md) supersede the source-list emphasis of the previous audit. [The full specification](JOB-CLASS-SPECIFICATION.md) and [axe addendum](AXE-SKILL-EXPANSION.md) describe the current proposals.

This register covers all 116 current ability entries. An inspiration reference does not establish that our exact move exists in another game, and a recognizable job does not require copied skills. Our changes can improve reliability, change scaling and cost, broaden access, or create new effects. Values remain untested. Samurai and Geomancer were rebuilt in this revision; Viking's wave now has useful base behavior on land. Other entries remain provisional and are free to change under the same principles.

Samurai now uses sword development and a composure-and-release rhythm. Geomancer has useful baseline nature arts, terrain bonuses, party utility, and a persistent ice field. These are deliberate creative departures. Source-game accuracy remains relevant when describing the source, but copying its restrictions is not a requirement for our design.

## Current entries and inspiration

The previous-name column refers to the initial v0.1 design, retained for traceability. Adaptation and thematic redesign describe a starting point, not a fidelity ranking. Original extensions are equally valid when they serve the job's identity. Combo entries retain ordinary FFTA integration.

| ID | Initial draft | Current entry | Classification | Inspiration / purpose |
|---|---|---|---|---|
${data.abilities.map(a=>`| ${a.id} | ${a.previous??'—'} | ${a.name} | ${a.kind} | ${a.anchor}. [Inspiration][${a.ref}] |`).join('\n')}

All 116 entries have an effect, identity rationale, and reference. This is document coverage, not a claim of completed numerical balance, canonical equivalence, or a working ROM patch. The roster and progression decisions remain intact.
`+sources;
fs.writeFileSync('JOB-THEME-AUDIT.md',audit);
let outline=fs.readFileSync('JOB-EXPANSION-DESIGN.md','utf8');
outline=outline.replace(/The version 0\.2[^\n]*/,"The [version 0.3 design principles](JOB-DESIGN-PRINCIPLES.md) prioritize each job's spirit and useful FFTA gameplay. The [inspiration register](JOB-THEME-AUDIT.md) covers all 116 entries without requiring copied abilities. Source-game mechanics and balance are not binding.");
outline=outline.replace(/^\| Samurai \|.*$/m,'| Samurai | Katana mastery, composure, and blade spirits | Useful attacks build Centered for stronger follow-ups; sword development supports its offense |');
outline=outline.replace(/^\| Geomancer \|.*$/m,'| Geomancer | Nature damage, battlefield control, allied mobility and protection | Every skill works on ordinary terrain; nearby affinity improves its effect; Rime Field influences movement |');
outline=outline.replace('uses Tsunami only from water','uses Tsunami on any ground, enhanced near water');
fs.writeFileSync('JOB-EXPANSION-DESIGN.md',outline);
let starter=fs.readFileSync('STARTER-JOB-INSPIRATION.md','utf8').replace('version 0.2 class specification','version 0.3 class specification').replace('with a [complete thematic audit](JOB-THEME-AUDIT.md)','guided by [job identity and gameplay principles](JOB-DESIGN-PRINCIPLES.md)');
fs.writeFileSync('STARTER-JOB-INSPIRATION.md',starter);
let start=fs.readFileSync('START-HERE.md','utf8');
start=start.replace(/Start with \[the thematic audit\][^\n]*/,"Start with [the design principles](JOB-DESIGN-PRINCIPLES.md): preserve each job's spirit and design its mechanics for FFTA. [The full class specification](JOB-CLASS-SPECIFICATION.md) contains jobs, prerequisites, abilities, passives, growths, and equipment; [the axe addendum](AXE-SKILL-EXPANSION.md) covers Soldier and Gladiator. The class specification is version 0.3; the axe detail remains version 0.2 under the new principles. These are design documents, not an installed patch.");
fs.writeFileSync('START-HERE.md',start);
console.log(JSON.stringify({version:data.version,changedAbilities:changes.size,totalAbilities:data.abilities.length}));
