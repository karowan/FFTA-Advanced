import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root = path.resolve(import.meta.dirname,'..');
const read = f => fs.readFileSync(path.join(root,f),'utf8').replace(/\r\n/g,'\n');
const data = JSON.parse(read('notes/job-theme-audit.json'));
const baseline = JSON.parse(read('notes/design-v0.4/job-theme-audit.json'));
const previousApproved = JSON.parse(read('notes/design-v0.5/job-theme-audit.json'));
const spec = read('JOB-CLASS-SPECIFICATION.md');
const axe = read('AXE-SKILL-EXPANSION.md');
const supports = read('SUPPORT-SKILL-DESIGN.md');
const errors = [];
const requireCheck = (ok, message) => { if(!ok) errors.push(message); };
const canonical = new Map();
for (const line of (spec+'\n'+axe).split('\n')) {
  const match = line.match(/^\| ((?:SAM|DRK|VIK|GEO|CHM|BRD|DNC|MYK)-[ASRC]\d+|(?:SLD|GLD)-AX-[ASR]\d+)\b/);
  if (!match) continue;
  requireCheck(!canonical.has(match[1]),'Duplicate table ID '+match[1]);
  canonical.set(match[1], line.split('|').slice(1,-1).map(x=>x.trim()));
}
requireCheck(data.version==='0.6','Wrong data version');
requireCheck(data.abilities.length===122 && canonical.size===122,'Expected 122 entries');
requireCheck(new Set(data.abilities.map(a=>a.id)).size===122,'Duplicate data IDs');
requireCheck(spec.includes('122 entries: 78 actions, 18 supports, 18 reactions, and eight combos'),'Stale specification count summary');
const themeRows=read('JOB-THEME-AUDIT.md').split('\n').filter(l=>/^\| (?:SAM|DRK|VIK|GEO|CHM|BRD|DNC|MYK|SLD|GLD)-/.test(l));
requireCheck(themeRows.length===122 && data.abilities.every(a=>themeRows.filter(l=>l.startsWith('| '+a.id+' |')).length===1),'Theme register coverage mismatch');
const counts = {}, totals = {};
for (const a of data.abilities) {
  const row = canonical.get(a.id);
  requireCheck(row?.[0]===a.id+' '+a.name,'Name mismatch '+a.id);
  requireCheck(Number(row?.[1])===a.ap,'AP mismatch '+a.id);
  requireCheck(row?.[2]===a.effect,'Rule mismatch '+a.id);
  requireCheck(!!data.sources[a.ref],'Unknown lineage source '+a.id);
  requireCheck(!('cost' in a) && !('target' in a),'Stale parallel fields '+a.id);
  const before = baseline.abilities.find(b=>b.id===a.id);
  if(before) requireCheck(a.job===before.job && a.type===before.type,'Changed owner/type '+a.id);
  else requireCheck(/^MYK-A(?:9|1[0-4])$/.test(a.id) && a.job==='Mystic Knight' && a.type==='Action' && a.introducedVersion==='0.6','Unexpected new entry '+a.id);
  counts[a.type]=(counts[a.type]??0)+1;
  const job = a.id.replace(/-[ASRC]\d+$/,'');
  totals[job]=(totals[job]??0)+a.ap;
  if(a.type==='Support') {
    const line=supports.split('\n').find(l=>l.startsWith('| '+a.id+' '));
    requireCheck(!!line?.includes(a.effect),'Support sheet rule mismatch '+a.id);
    requireCheck(!!line?.includes(a.buildExamples),'Support build mismatch '+a.id);
  }
}
requireCheck(JSON.stringify(counts)===JSON.stringify({Action:78,Support:18,Reaction:18,Combo:8}), 'Wrong action/support/reaction/combo counts');
const expectedTotals={SAM:3200,DRK:3350,VIK:2800,GEO:3150,CHM:2850,BRD:3050,DNC:3300,MYK:4800,'SLD-AX':1050,'GLD-AX':1850};
requireCheck(Object.entries(expectedTotals).every(([job,ap])=>totals[job]===ap),'AP totals differ from adoption');
const previousSpec = read('notes/design-v0.4/JOB-CLASS-SPECIFICATION.md');
const section=(t,a,b)=>t.slice(t.indexOf(a),t.indexOf(b,t.indexOf(a)+a.length));
requireCheck(section(spec,'## 1. Roster','## 2.')===section(previousSpec,'## 1. Roster','## 2.'),'Roster/progression changed');
const statRows = text=>section(text,'## 3. Stats','## 4.').split('\n').filter(l=>l.startsWith('|')).join('\n');
requireCheck(statRows(spec)===statRows(previousSpec),'Growth/chassis tables changed');
const gearRows=section(spec,'## 12. Teaching','## 13.').split('\n').filter(l=>/^\| (?:Samurai|Dark Knight|Viking|Geomancer|Chemist|Bard|Dancer|Mystic Knight) \/ /.test(l));
const gearCount=gearRows.reduce((sum,line)=>sum+line.split('|').slice(2,-1).length,0);
const axeGearCount=section(axe,'## Teaching axes','## Learning').split('\n').filter(l=>/^\| (?:Recruit|Throwing|Field|Breaching|Bearded|Arena|Headsman|Titan)/.test(l)).length;
const extraGearRows=section(spec,'### Additional Mystic Knight teaching sabers','## 13.').split('\n').filter(l=>/^\| (?:Hourglass|Aether|Dawn|Severance|Prism|Stone) Saber \|/.test(l));
requireCheck(gearCount===64 && axeGearCount===8 && extraGearRows.length===6,'Wrong teaching equipment count');
for(const a of data.abilities.filter(a=>a.introducedVersion==='0.6')) {
  const lessons=extraGearRows.filter(l=>l.includes(a.id+' '+a.name));
  requireCheck(lessons.length===1 && Number(lessons[0]?.split('|')[3].trim())===a.ap,'New teaching lesson mismatch '+a.id);
}
requireCheck(baseline.abilities.every(a=>data.abilities.some(b=>b.id===a.id)),'Missing prior stable ID');
for(const a of previousApproved.abilities) {
  const current=data.abilities.find(b=>b.id===a.id);
  requireCheck(current?.name===a.name && current?.ap===a.ap,'Unintended prior lesson/name change '+a.id);
  if(a.id!=='MYK-S1') requireCheck(current?.effect===a.effect,'Unintended prior rule change '+a.id);
}
const mykContext=section(spec,'**Spellblade — Viera.**','### Actions').trim();
requireCheck(mykContext===data.commandRules.MYK,'Spellblade command rules mismatch');
const row=id=>data.abilities.find(a=>a.id===id);
requireCheck(row('DRK-S1').effect.includes('≤35%')&&!row('DRK-S1').effect.includes('≤40%'),'Desperation threshold');
requireCheck(row('MYK-R2').effect.includes('×0.50')&&!row('MYK-R2').effect.includes('negate physical'),'Spell Parry reduction');
requireCheck(row('CHM-A8').effect.includes('no 200-HP cap'),'Revival cap correction');
requireCheck(row('BRD-S1').effect.includes('Smile')&&row('BRD-S1').effect.includes('Quicken'),'Turn-grant exclusions');
requireCheck(row('DNC-R1').effect.includes('Physical damage classification'),'Fury classification');
requireCheck(row('MYK-A13').effect.includes('consume') && row('MYK-A13').effect.includes('Magic sequencing and magical HP damage'),'Release classification/consumption');
requireCheck(row('MYK-A14').effect.includes('no preliminary A roll and no HP damage'),'Break single status resolution');
requireCheck(row('MYK-A12').effect.includes('Physical sequencing and physical HP damage'),'Spellbreak classification');
const documents=['JOB-CLASS-SPECIFICATION.md','SUPPORT-SKILL-DESIGN.md','AXE-SKILL-EXPANSION.md','JOB-THEME-AUDIT.md','JOB-DESIGN-PRINCIPLES.md','JOB-EXPANSION-DESIGN.md','START-HERE.md','STARTER-JOB-INSPIRATION.md','BALANCE-COUNCIL.md','SPELLBLADE-EXPANSION.md','ABILITY-EXPANSION-COUNCIL.md'];
for(const file of documents) {
  const text=read(file);
  for(const match of text.matchAll(/\]\(([^)]+)\)/g)) {
    const target=match[1].split('#')[0];
    if (!target || /^https?:/i.test(target)) continue;
    requireCheck(fs.existsSync(path.resolve(path.dirname(path.join(root,file)),target)),'Missing local link '+file+': '+target);
  }
  requireCheck(!/version 0\.4 class specification|specifications are version 0\.4|Design version 0\.4|Design direction 0\.4/.test(text),'Stale current version '+file);
}
const expectedRom='4ac05441f4de70a4ec3dd932116346c61b8783d9';
const roms={};
for(const file of ['roms/clean/FFTA_US_clean.gba','roms/play/vanilla/FFTA_US_vanilla.gba']) {
  roms[file]=crypto.createHash('sha1').update(fs.readFileSync(path.join(root,file))).digest('hex');
  requireCheck(roms[file]===expectedRom,'ROM hash changed '+file);
}
const result={version:data.version,scope:'Document/data consistency only; no gameplay test.',entries:data.abilities.length,counts,apTotals:totals,teachingItems:gearCount+axeGearCount+extraGearRows.length,rosterAndGrowthsPreserved:true,romSha1:roms,errors,passed:errors.length===0};
fs.writeFileSync(path.join(root,'notes/design-validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
if(errors.length)process.exitCode=1;
