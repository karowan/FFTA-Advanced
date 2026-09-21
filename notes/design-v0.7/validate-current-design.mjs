import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root = path.resolve(import.meta.dirname,'..');
const read = f => fs.readFileSync(path.join(root,f),'utf8').replace(/\r\n/g,'\n');
const data = JSON.parse(read('notes/job-theme-audit.json'));
const baseline = JSON.parse(read('notes/design-v0.4/job-theme-audit.json'));
const previousApproved = JSON.parse(read('notes/design-v0.6/job-theme-audit.json'));
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
requireCheck(data.version==='0.7','Wrong data version');
requireCheck(data.abilities.length===129 && canonical.size===129,'Expected 129 entries');
requireCheck(new Set(data.abilities.map(a=>a.id)).size===129,'Duplicate data IDs');
requireCheck(spec.includes('129 entries: 85 actions, 18 supports, 18 reactions, and eight combos'),'Stale specification count summary');
const themeRows=read('JOB-THEME-AUDIT.md').split('\n').filter(l=>/^\| (?:SAM|DRK|VIK|GEO|CHM|BRD|DNC|MYK|SLD|GLD)-/.test(l));
requireCheck(themeRows.length===129 && data.abilities.every(a=>themeRows.filter(l=>l.startsWith('| '+a.id+' |')).length===1),'Theme register coverage mismatch');
const approvedNewOwners={'SAM-A9':'Samurai','DRK-A9':'Dark Knight','VIK-A9':'Viking','GEO-A9':'Geomancer','CHM-A9':'Chemist','CHM-A10':'Chemist','DNC-A9':'Dancer'};
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
  else requireCheck(a.type==='Action' && ((/^MYK-A(?:9|1[0-4])$/.test(a.id) && a.job==='Mystic Knight' && a.introducedVersion==='0.6') || (approvedNewOwners[a.id]===a.job && a.introducedVersion==='0.7')),'Unexpected new entry '+a.id);
  counts[a.type]=(counts[a.type]??0)+1;
  const job = a.id.replace(/-[ASRC]\d+$/,'');
  totals[job]=(totals[job]??0)+a.ap;
  if(a.type==='Support') {
    const line=supports.split('\n').find(l=>l.startsWith('| '+a.id+' '));
    requireCheck(!!line?.includes(a.effect),'Support sheet rule mismatch '+a.id);
    requireCheck(!!line?.includes(a.buildExamples),'Support build mismatch '+a.id);
  }
}
requireCheck(JSON.stringify(counts)===JSON.stringify({Action:85,Support:18,Reaction:18,Combo:8}), 'Wrong action/support/reaction/combo counts');
const expectedTotals={SAM:3500,DRK:3650,VIK:3050,GEO:3450,CHM:3350,BRD:3050,DNC:3550,MYK:4800,'SLD-AX':1050,'GLD-AX':1850};
requireCheck(Object.entries(expectedTotals).every(([job,ap])=>totals[job]===ap),'AP totals differ from adoption');
const totalLabels={SAM:'Samurai',DRK:'Dark Knight (each race)',VIK:'Viking',GEO:'Geomancer',CHM:'Chemist (each race)',BRD:'Bard',DNC:'Dancer',MYK:'Mystic Knight','SLD-AX':'Soldier axe additions','GLD-AX':'Gladiator axe additions'};
for(const [job,label] of Object.entries(totalLabels)){
  const cells=spec.split('\n').filter(l=>l.startsWith('| '+label+' |')).map(l=>l.split('|').slice(1,-1).map(x=>x.trim())).find(c=>c.length===6 && c.slice(1).every(x=>/^\d+$/.test(x)));
  const typeTotals=['Action','Support','Reaction','Combo'].map(type=>data.abilities.filter(a=>a.id.replace(/-[ASRC]\d+$/,'')===job && a.type===type).reduce((n,a)=>n+a.ap,0));
  requireCheck(!!cells && typeTotals.every((n,i)=>Number(cells[i+1])===n) && Number(cells[5])===totals[job],'Specification AP summary mismatch '+job);
}
const previousSpec = read('notes/design-v0.4/JOB-CLASS-SPECIFICATION.md');
const section=(t,a,b)=>t.slice(t.indexOf(a),t.indexOf(b,t.indexOf(a)+a.length));
requireCheck(section(spec,'## 1. Roster','## 2.')===section(previousSpec,'## 1. Roster','## 2.'),'Roster/progression changed');
const statRows = text=>section(text,'## 3. Stats','## 4.').split('\n').filter(l=>l.startsWith('|')).join('\n');
requireCheck(statRows(spec)===statRows(previousSpec),'Growth/chassis tables changed');
const gearRows=section(spec,'## 12. Teaching','## 13.').split('\n').filter(l=>/^\| (?:Samurai|Dark Knight|Viking|Geomancer|Chemist|Bard|Dancer|Mystic Knight) \/ /.test(l));
const gearCount=gearRows.reduce((sum,line)=>sum+line.split('|').slice(2,-1).length,0);
const axeGearCount=section(axe,'## Teaching axes','## Learning').split('\n').filter(l=>/^\| (?:Recruit|Throwing|Field|Breaching|Bearded|Arena|Headsman|Titan)/.test(l)).length;
const extraGearRows=section(spec,'### Additional Mystic Knight teaching sabers','## 13.').split('\n').filter(l=>/^\| (?:Hourglass|Aether|Dawn|Severance|Prism|Stone) Saber \|/.test(l));
const councilGearRows=section(spec,'### Additional council teaching weapons (0.7)','## 13.').split('\n').filter(l=>/^\| [^|]+ \| (?:SAM|DRK|VIK|GEO|CHM|DNC)-A\d+ /.test(l));
requireCheck(gearCount===64 && axeGearCount===8 && extraGearRows.length===6 && councilGearRows.length===7,'Wrong teaching equipment count');
for(const a of data.abilities.filter(a=>['0.6','0.7'].includes(a.introducedVersion))) {
  const lessons=[...extraGearRows,...councilGearRows].filter(l=>l.includes(a.id+' '+a.name));
  requireCheck(lessons.length===1 && Number(lessons[0]?.split('|')[3].trim())===a.ap,'New teaching lesson mismatch '+a.id);
}
requireCheck(baseline.abilities.every(a=>data.abilities.some(b=>b.id===a.id)),'Missing prior stable ID');
for(const a of previousApproved.abilities) {
  const current=data.abilities.find(b=>b.id===a.id);
  requireCheck(current?.name===a.name && current?.ap===a.ap,'Unintended prior lesson/name change '+a.id);
  requireCheck(current?.effect===a.effect,'Unintended prior rule change '+a.id);
}
const mykContext=section(spec,'**Spellblade — Viera.**','### Actions').trim();
requireCheck(mykContext===data.commandRules.MYK,'Spellblade command rules mismatch');
for(const [job,context] of Object.entries(data.commandRules)) requireCheck(spec.includes(context),'Command context mismatch '+job);
const row=id=>data.abilities.find(a=>a.id===id);
requireCheck(row('DRK-S1').effect.includes('≤35%')&&!row('DRK-S1').effect.includes('≤40%'),'Desperation threshold');
requireCheck(row('MYK-R2').effect.includes('×0.50')&&!row('MYK-R2').effect.includes('negate physical'),'Spell Parry reduction');
requireCheck(row('CHM-A8').effect.includes('no 200-HP cap'),'Revival cap correction');
requireCheck(row('BRD-S1').effect.includes('Smile')&&row('BRD-S1').effect.includes('Quicken'),'Turn-grant exclusions');
requireCheck(row('DNC-R1').effect.includes('Physical damage classification'),'Fury classification');
requireCheck(row('MYK-A13').effect.includes('consume') && row('MYK-A13').effect.includes('Magic sequencing and magical HP damage'),'Release classification/consumption');
requireCheck(row('MYK-A14').effect.includes('no preliminary A roll and no HP damage'),'Break single status resolution');
requireCheck(row('MYK-A12').effect.includes('Physical sequencing and physical HP damage'),'Spellbreak classification');
requireCheck(row('DNC-A9').effect.includes('remaining normal movement points') && row('DNC-A9').effect.includes('no new points') && row('DNC-A9').effect.includes('immediate enemy reactions'),'Passing Step movement/reaction rules');
requireCheck(row('CHM-A9').effect.includes('before Auto-Cureall') && row('CHM-A9').effect.includes('One Potion AND one Cureall'),'Inoculation eligibility/payment');
requireCheck(row('CHM-A10').effect.includes('One Potion AND one Soft'),'Guarding Draught payment');
requireCheck(row('GEO-A9').effect.includes('same single per-caster field slot as Rime'),'Mutually exclusive fields');
requireCheck(row('DRK-A9').effect.includes('entirely MP-redirected damage neither consumes') && row('DRK-A9').effect.includes('10% user max HP'),'Ward payment/redirection');
requireCheck(row('SAM-A9').effect.includes('exactly two pulses') && row('SAM-A9').effect.includes('before outgoing bonuses'),'Wound snapshot/schedule');
requireCheck(row('VIK-A9').effect.includes('One challenger per target') && row('VIK-A9').effect.includes('Does not force'),'Challenge target rules');
requireCheck(spec.includes('Passing Step alone permits immediate post-strike movement'),'Shared movement exception missing');
const perJobActions=Object.fromEntries(Object.keys(data.commandRules).map(job=>[job,data.abilities.filter(a=>a.id.startsWith(job+'-A')).length]));
requireCheck(JSON.stringify(perJobActions)===JSON.stringify({SAM:9,DRK:9,VIK:9,GEO:9,CHM:10,BRD:8,DNC:9,MYK:14}),'Action counts per command');
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
const result={version:data.version,scope:'Document/data consistency only; no gameplay test.',entries:data.abilities.length,counts,perJobActions,apTotals:totals,teachingItems:gearCount+axeGearCount+extraGearRows.length+councilGearRows.length,rosterAndGrowthsPreserved:true,prior122AbilityRowsPreserved:true,romSha1:roms,errors,passed:errors.length===0};
fs.writeFileSync(path.join(root,'notes/design-validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
if(errors.length)process.exitCode=1;
