/* Independent reads of the current installed tables, compared with the
 * approved Markdown/data. This is content reconciliation, not combat proof. */
import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1,nameAt} from '../src/rom-data.mjs';
import {equipmentDisplayName} from '../src/equipment-display-names.mjs';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const design=read('notes/job-theme-audit.json'),equipment=read('notes/equipment-acquisition.json');
const registry=read('build/expansion/registry.json');
const meta=read('build/expansion/probes/integrated-jobs/current.json');
const rom=fs.readFileSync(meta.path),clean=cleanROM();
const spec=fs.readFileSync(path.join(root,'JOB-CLASS-SPECIFICATION.md'),'utf8');
const rows=spec.split(/\r?\n/).filter(l=>l.startsWith('|')).map(l=>l.split('|').slice(1,-1).map(s=>s.trim()));
let checks=0;const failures=[],lessons=[],items=[],jobs=[];
function check(ok,label){checks++;if(!ok)failures.push(label);}
function pointer(offset){const value=rom.readUInt32LE(offset);if(value<0x08000000||value>=0x0a000000)throw Error('Invalid ROM pointer '+offset.toString(16));return value-0x08000000;}
check(sha1(rom)===meta.romSha1,'Current ROM identity');
check(design.version==='0.7'&&registry.designVersion==='0.7','Approved design version');
check(registry.designSha1===sha1(fs.readFileSync(path.join(root,'notes/job-theme-audit.json'))),'Registry design fingerprint');
check(registry.equipmentSha1===sha1(fs.readFileSync(path.join(root,'notes/equipment-acquisition.json'))),'Registry equipment fingerprint');
const tables={jobs:pointer(0xc8598),permissions:pointer(0xcac40),requirements:pointer(0xc8b18),
 names:pointer(0x18da4),items:pointer(0x2b2a0),teaching:pointer(0x49154),races:pointer(0x257e8),
 others:pointer(0x2c08c),actions:pointer(0x23320),help:pointer(0x36d6c4)};
check(tables.actions===meta.tables.actions,'Installed action pointer agrees with manifest');
check(design.abilities.length===129&&registry.lessons.length===129,'129 lessons');
check(equipment.items.length===85&&registry.items.length===85,'85 items');
// The shared native-text reader leaves expansion hyphens as explicit tokens.
const decodedName=(image,table,id)=>nameAt(image,table,id).replaceAll('[81][B]','-');
const aliases={'GEO-R2':'Nature Wrath','DNC-R2':'Counter Rhy.'};
for(const approved of design.abilities){
 const lesson=registry.lessons.find(x=>x.id===approved.id);check(!!lesson,approved.id+' allocated');if(!lesson)continue;
 for(const field of ['name','effect','ap','type'])check(lesson[field]===approved[field],approved.id+' approved '+field);
 const name=decodedName(rom,tables.others,lesson.nameId);
 check(name===(aliases[lesson.id]??approved.name),lesson.id+' installed name');
 const owners=[];
 for(const owner of lesson.owners){
  const bank=pointer(tables.races+owner.race*4),offset=bank+owner.abilityIndex*8;
  const b=rom.subarray(offset,offset+8),helpId=b.readUInt16LE(2);
  check(b.readUInt16LE(0)===lesson.nameId&&b.readUInt16LE(4)===lesson.globalAbilityId&&b[6]===lesson.nativeType&&b[7]*10===approved.ap,
   lesson.id+' racial lesson/AP '+owner.race);
  check(helpId>=0x650,lesson.id+' has expansion help '+owner.race);
  let helpAddress=null;
  if(helpId>=0x650){helpAddress=pointer(tables.help+(helpId-0x1de)*4);check(rom[helpAddress]===0x28&&rom[helpAddress+1]===0x18,lesson.id+' ordinary help encoding');}
  owners.push({...owner,helpId,helpAddress,record:b.toString('hex')});
 }
 let action=null;
 if(lesson.type==='Action'){
  const b=rom.subarray(tables.actions+lesson.globalAbilityId*28,tables.actions+(lesson.globalAbilityId+1)*28);
  const match=approved.effect.match(/(\d+) MP/),mp=match?Number(match[1]):0;
  check(b.readUInt16LE(0)===lesson.nameId,lesson.id+' action name');
  check(b[4]===mp,lesson.id+' base MP cost');
  const power=approved.effect.match(/\bM(\d+)\b/);
  if(power)check(b[11]===Number(power[1]),lesson.id+' magic power reference');
  check(b.subarray(12,16).some(x=>x>1),lesson.id+' populated effect descriptors');
  action={id:lesson.globalAbilityId,mp:b[4],power:b[11],range:b[6],heightMode:b[7],descriptors:[...b.subarray(12,16)],record:b.toString('hex')};
 }
 lessons.push({id:lesson.id,name,approvedEffect:approved.effect,ap:approved.ap,type:approved.type,owners,action});
}
const types={Sword:1,Saber:3,Knife:7,Rapier:8,Katana:9,Rod:11,Instrument:16,Axe:31};
const taught=new Set();
for(const approved of equipment.items){
 const item=registry.items.find(x=>x.id===approved.id);check(!!item,approved.id+' allocated');if(!item)continue;
 const b=rom.subarray(tables.items+item.romItemId*32,tables.items+(item.romItemId+1)*32);
 const teaching=rom.subarray(tables.teaching+b.readUInt16LE(29)*20,tables.teaching+(b.readUInt16LE(29)+1)*20);
 check(decodedName(rom,tables.names,b.readUInt16LE(0))===equipmentDisplayName({...approved,romItemId:item.romItemId}),approved.id+' visible name');
 check(b[8]===types[approved.category]&&b[16]===approved.weaponAttack&&b[18]===approved.magicPowerBonus,approved.id+' category/power');
 check(b.readUInt16LE(4)===approved.basePriceGil&&b.readUInt16LE(6)===Math.floor(approved.basePriceGil/2),approved.id+' prices');
 check([9,17,19,20,21,22,23,26,27,28].every(n=>b[n]===0),approved.id+' no unapproved bonus/proc');
 if(approved.category==='Axe')check(b[11]===2&&(b[12]&7)===0,approved.id+' two-handed axe restrictions');
 const expected=approved.lessons.flatMap(a=>registry.lessons.find(l=>l.id===a.id).owners.map(o=>[o.jobId,o.abilityIndex,a.id]));
 const installed=Array.from({length:teaching[0]},(_,i)=>[teaching[2+i*2],teaching[3+i*2]]);
 check(JSON.stringify(installed)===JSON.stringify(expected.map(x=>x.slice(0,2))),approved.id+' teaching and racial owners');
 expected.forEach(x=>taught.add(x[2]));
 items.push({id:approved.id,romItemId:item.romItemId,teaching:expected,stage:approved.stageId,
  shops:[approved.primaryShop,...approved.additionalShops],record:b.toString('hex')});
}
check(taught.size===129&&design.abilities.every(a=>taught.has(a.id)),'All129 lessons taught');
const weaponTypes={'Katanas':[9],'Swords, greatswords, broadswords':[1,5,6],'New two-handed axes':[31],
 'Rods, maces':[11,12],'Knives, maces':[7,12],'Instruments, knives':[16,7],'Knives, rapiers':[7,8],'Rapiers, sabers':[8,3]};
const nativeJobs=new Map(Array.from({length:42},(_,n)=>{const id=n+2,p=0x521a14+id*52;return [clean[p+4]+':'+nameAt(clean,0x526680,clean.readUInt16LE(p)),id];}));
for(const job of registry.jobs.filter(x=>!x.existing)){
 const title=job.raceName+' '+job.name,b=rom.subarray(tables.jobs+job.id*52,tables.jobs+(job.id+1)*52);
 const statRows=rows.filter(r=>r[0]===title&&r.length===8&&r.slice(1).every(s=>/^\d+(\.\d+)?$/.test(s)));
 check(statRows.length===2,title+' approved stats available');if(statRows.length!==2)continue;
 const growth=statRows[0].slice(1).map(Number),stats=statRows[1].slice(1).map(Number);
 const gains=[0,1,6,2,3,4,5].map(i=>Math.round(growth[i]*10));
 const installed=[b[23],b[24],b.readUIntLE(26,3)&4095,b.readUIntLE(26,3)>>>12,b.readUIntLE(29,3)&4095,b.readUIntLE(29,3)>>>12,b[25]];
 check(JSON.stringify(installed)===JSON.stringify(stats),title+' generation stats');
 check(JSON.stringify([...b.subarray(32,39)])===JSON.stringify(gains),title+' growths');
 check(b[4]===job.race&&b[5]===0&&b[22]===50&&b.readUInt32LE(18)===0x01249248,title+' race/status/affinities');
 const gearName=job.name==='Dark Knight'?'Dark Knight, both races':job.name==='Chemist'?'Chemist, '+job.raceName:job.name;
 const gear=rows.find(r=>r[0]===gearName&&r.length===7);check(!!gear,title+' approved gear available');if(!gear)continue;
 const allowed=new Set([...(weaponTypes[gear[4]]??[]),27,28,29]);
 for(const [word,type] of [['clothing',25],['heavy armor',24],['robes',26],['hats',23],['helmets',21]])if(gear[5].toLowerCase().includes(word))allowed.add(type);
 if(gear[6].startsWith('Yes'))allowed.add(20);
 const mask=[...allowed].reduce((n,t)=>n|1<<(t-1),0)>>>0;
 check(rom.readUInt32LE(tables.permissions+b[45]*4)===mask,title+' equipment mask');
 check([40,41,42].every((p,i)=>b[p]===Number(gear[i+1])),title+' Move/Jump/Evade');
 const progression=rows.find(r=>r.length===4&&r[0]===job.raceName&&r[1]===job.name);
 const prerequisites=progression[3]==='None'?[0,0,0,0]:progression[3].split(' + ').flatMap(s=>{const m=s.match(/^(.+) (\d+)$/);return [nativeJobs.get(job.race+':'+m[1]),Number(m[2])];});
 const actual=[...rom.subarray(tables.requirements+b[48]*4,tables.requirements+(b[48]+1)*4)];
 check(JSON.stringify(actual)===JSON.stringify(prerequisites),title+' mastered-action prerequisites');
 jobs.push({id:job.id,title,stats,growth,move:b[40],jump:b[41],evade:b[42],permissionMask:mask,prerequisites});
}
check(jobs.length===10,'Ten racial jobs');
const report={passed:!failures.length,candidateSha1:meta.romSha1,checks,failures,tables,lessons,items,jobs,
 scope:'Installed costs, AP, racial ownership, teaching, stats, growths, permissions, prerequisites and nonzero help. Effect formulas, runtime stock gates, mixing and presentation require their scoped evidence.'};
fs.writeFileSync(path.join(root,'build/reports/installed-design.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,candidateSha1:meta.romSha1,checks,failures,lessons:lessons.length,items:items.length,jobs:jobs.length},null,2));
if(failures.length)process.exitCode=1;
