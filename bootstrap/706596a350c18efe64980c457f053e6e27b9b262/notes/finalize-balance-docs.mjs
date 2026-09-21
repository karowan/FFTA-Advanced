import fs from 'node:fs';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '..');
const read = f => fs.readFileSync(path.join(root,f),'utf8').replace(/\r\n/g,'\n');
const write = (f,s) => fs.writeFileSync(path.join(root,f),s.trimEnd()+'\n');
const data = JSON.parse(read('notes/job-theme-audit.json'));
if (data.version !== '0.5') throw new Error('Requires adopted v0.5');

// Use current rules in canonical tables; retain the review's criticism only in historical evidence/data.
const tidy = s => s.replace(/currentHP/g,'current HP').replace(/forecastdamage/g,'forecast damage').replace(/be≤/g,'be ≤').replace(/maxHP/g,'max HP').replace(/maxMP/g,'max MP').replace(/\bbase range <4 becomes4/g,'base range <4 becomes 4').replace(/\bup to5\b/g,'up to 5').replace(/\bby incoming-action start/g,'at action start').replace(/\bcurrent Exposed\b/g,'Exposed').replace(/\bcurrent bonus\b/g,'the bonus').replace(/\bat≤/g,'at ≤').replace(/\bcap60\b/g,'cap 60').replace(/\bthrough end\b/g,'through the end').replace(/\bonce action\b/g,'once per action');
for (const a of data.abilities) {
  const old = a.effect;
  a.effect = tidy(old);
  if (a.id === 'VIK-A8') a.effect = a.effect.replace('Water next to caster retains the bonus of removing up to 8 MP per positively damaged target.', 'If mapped water is on the caster tile or an orthogonally adjacent tile within 2 height, positive damage also removes up to 8 MP per target, with no recovery.');
  for (const file of ['JOB-CLASS-SPECIFICATION.md','AXE-SKILL-EXPANSION.md','SUPPORT-SKILL-DESIGN.md']) {
    let text = read(file);
    if (text.includes(old)) write(file, text.replaceAll(old,a.effect));
  }
}
// Preserve the existing command name while distinguishing the learned Chemist set from ordinary Item.
data.commandRules.CHM = data.commandRules.CHM.replace('**Medicine — Nu Mou and Moogle.**', '**Items — Nu Mou and Moogle.**').replaceAll('Juggler/Medicine','Juggler/Chemist').replaceAll('Bard/Medicine','Bard/Chemist');
write('JOB-CLASS-SPECIFICATION.md',read('JOB-CLASS-SPECIFICATION.md').replace('**Medicine — Nu Mou and Moogle.**', '**Items — Nu Mou and Moogle.**').replaceAll('Juggler/Medicine','Juggler/Chemist').replaceAll('Bard/Medicine','Bard/Chemist'));
for (const f of ['JOB-CLASS-SPECIFICATION.md','AXE-SKILL-EXPANSION.md']) {
  const lines = read(f).split('\n').map(line => {
    if (line === '| ID / ability | AP | Current rules | Role and build considerations | Inspiration |') return '| ID / ability | AP | Current rules | Inspiration |';
    if (line === '|---|---:|---|---|---|') return '|---|---:|---|---|';
    if (/^\| (?:SAM|DRK|VIK|GEO|CHM|BRD|DNC|MYK|SLD|GLD)-/.test(line)) {
      const c = line.split('|').slice(1,-1).map(s=>s.trim());
      if (c.length===5) return `| ${c[0]} | ${c[1]} | ${c[2]} | ${c[4]} |`;
    }
    return line;
  });
  write(f,lines.join('\n'));
}
write('notes/job-theme-audit.json',JSON.stringify(data,null,2));

let principles = read('JOB-DESIGN-PRINCIPLES.md').replace('Design direction 0.4','Design direction 0.5 — adopted council balance pass');
principles = principles.replace('neither endless self-sustain nor permanent dependence on a rescue turn is the goal.', 'sustainable HP-positive actions are allowed when paid for in turns and resources; automatic or unpaid recovery loops are not.');
const start = principles.indexOf('## Changes made in this revision');
const end = principles.indexOf('## What remains fixed',start);
principles = principles.slice(0,start) + `## Adopted council balance pass

The user approved the reconciled [council proposal](BALANCE-COUNCIL.md). Version 0.5 makes its 116 reviewed entries, shared rules, AP values, and teaching changes the current design. The reports remain evidence; the class/axe specifications and structured ability data now own the current rules.

Mystic Knight can enchant and strike in one action, retaining the enchantment for later primary Fight attacks. Dark Knight gains useful recovery and commitment attacks; its sacrifice costs and thresholds remain meaningful. Samurai retains Centered, and Geomancer retains terrain-independent arts with optional affinity and group Updraft. Viking's middle thunder tier becomes a focused storm-control action, and its theft uses original transactions.

Chemist consolidates ordinary medicine and gains two priced preparations. Bard's active songs work by voice on other legal Moogle jobs and offer dependable party benefits. Dancer gains scaling performance damage and deliberate control. Most reactions become reliable when their conditions are met, with explicit per-entry limits rather than a blanket turn lock. Supports remain useful beyond their teaching jobs.

Keep the council's combined-effect decisions: Desperation is 50% extra eligible damage at 35% HP or below; Spell Parry consumes an enchantment for 50% physical reduction, not immunity; Encouragement excludes immediate turn grants and receives no outgoing-healing multiplier; advanced revival restores 50% max HP without the rejected 200-HP cap. Spellweave's Magic category does not turn an enchanted strike's physical damage into magic.

The ten growth/chassis profiles stay the comparison baseline. Test ordinary progression and optimized inherited growth separately; do not compensate for weak action design by inflating every stat. AP totals vary by job, while all 116 lesson IDs and 72 teaching-item positions remain. Values are adopted design targets, not gameplay-tested guarantees.

` + principles.slice(end);
write('JOB-DESIGN-PRINCIPLES.md',principles);

let overview = read('JOB-EXPANSION-DESIGN.md').replace('# FFTA job expansion: proposed roster and progression','# FFTA job expansion: roster and progression').replace('Status: design draft, not installed or implemented.', 'Status: adopted design 0.5, not installed or implemented.').replace('version 0.4','version 0.5').replace('this initial outline','this progression overview').replace('All 18 proposed supports','All 18 adopted supports').replace('## Proposed unlock requirements','## Current unlock requirements').replace('These are proposed identities and example mechanics, not claims of working implementations.', 'These are the adopted 0.5 roles. The class specification supplies exact rules; no ROM implementation is claimed.');
const changes = {
 'Dark Knight': ['Spend HP for pressure; recover through capped drain and paid healing', 'Useful attack-and-buff commitment; sustainable actions are allowed, but automatic/unpaid recovery is not'],
 'Viking': ['Axe plunder, differentiated storms, and ailment resilience', 'Independent original theft transactions; precise Thunder, focused Stormcall, area Thundaga, and dry-ground Tsunami displacement'],
 'Chemist': ['Ranged medicine, grouped remedies/tonics, two-ingredient healing and revival', 'Mixtures justify the command beside ordinary Item plus Long Throw; actual ingredient supply and no MP cost'],
 'Bard': ['Voice-based party offense/protection, healing, MP recovery, and Requiem', 'Songs transfer as a secondary; Nameless Song deterministically applies Protect, Shell, and Regen'],
 'Dancer': ['Scaling performance damage, deliberate debuffs, vitality drain, Sword Dance', 'Weapon-free dances remain useful on other Viera jobs; Sword Dance retains a knife/rapier gate'],
 'Mystic Knight': ['Immediate enchant-and-strike plus persistent primary-Fight enchantments', 'Preparation can contribute now; Magic sequencing stays separate from physical damage; Spell Parry spends the enchantment']
};
for (const [name, c] of Object.entries(changes)) overview = overview.replace(new RegExp('^\\| '+name+' \\|[^\\n]+','m'), `| ${name} | ${c[0]} | ${c[1]} |`);
overview = overview.replace('- Pick AP/equipment learning for this vanilla-based specification. A switch to JP purchasing requires explicit progression and economy adjustments.', '- Preserve the selected AP/equipment learning and the current per-job AP totals. No JP-purchasing system is introduced.');
write('JOB-EXPANSION-DESIGN.md',overview);
write('STARTER-JOB-INSPIRATION.md',read('STARTER-JOB-INSPIRATION.md').replace('version 0.4 class specification','version 0.5 class specification'));
write('START-HERE.md',read('START-HERE.md').replace('The class and axe specifications are version 0.4;', 'The adopted class and axe specifications are version 0.5;').replace('These are design documents, not an installed patch.', 'The [adopted council balance pass](BALANCE-COUNCIL.md) explains the decisions and strongest combinations. All 116 abilities and their AP/teaching details are updated. These are design documents, not an installed patch.'));

let council = read('BALANCE-COUNCIL.md').replace('September 14, 2026 · Review of design 0.4 · Consolidated proposal for the next prototype', 'September 14, 2026 · Review of design 0.4 · Adopted as design 0.5');
council = council.replace('This is a completed design balance pass, **not a claim of gameplay-tested balance**. The original class specification, support sheet, axe sheet, source data, and ROM are unchanged. These reports contain the reviewable recommendations. Where a historical example or preliminary suggestion differs, the decisions in this document govern the consolidated proposal.', '**The user approved this proposal; it is now adopted in the [current class specification](JOB-CLASS-SPECIFICATION.md), [support sheet](SUPPORT-SKILL-DESIGN.md), [axe addendum](AXE-SKILL-EXPANSION.md), and structured ability data as version 0.5.** This is a completed design balance pass, not a claim of gameplay-tested balance. The ROM is unchanged. Original 0.4 documents are preserved in notes/design-v0.4; individual council reports remain historical review evidence. Current specifications take precedence over historical examples.');
council = council.replace('and confirmation that the four canonical source files are unchanged.', 'and integrity checks against the preserved 0.4 review baseline. Current-design consistency is checked separately in notes/design-validation.json.');
council = council.replace('Coverage, AP arithmetic, and unchanged-source checks are complete.', 'Review coverage and AP arithmetic are complete; the 0.4 baseline is preserved and the adopted 0.5 documents/data are checked for consistency.');
write('BALANCE-COUNCIL.md',council);
for (const name of ['martial','magic-utility','supports-reactions','global']) {
  const f = `notes/balance-council-${name}.md`;
  let t = read(f);
  const notice = '> Historical council review of v0.4, adopted through the reconciled v0.5 specification. Statements about unchanged canonical files describe the review stage. For current rules, use [the class specification](../JOB-CLASS-SPECIFICATION.md), [axe addendum](../AXE-SKILL-EXPANSION.md), and [adoption record](../BALANCE-COUNCIL.md).\n\n';
  if (!t.includes('> Historical council review')) { const i=t.indexOf('\n\n'); t=t.slice(0,i+2)+notice+t.slice(i+2); }
  write(f,t);
}
console.log('Updated current overviews, shared-rule wording, and historical review status.');
