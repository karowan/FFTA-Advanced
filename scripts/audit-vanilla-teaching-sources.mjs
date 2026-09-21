/* Exhaustive vanilla equipment/lesson ledger with conservative source labels.
 * Formation possession is not proof of stealability; a random pool is not a
 * deterministic recovery route. No ROM changes or runtime tests are performed.
 */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root, cleanROM, itemName, nameAt, sha1} from '../src/rom-data.mjs';

const clean=cleanROM();
const meta=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/probes/integrated-jobs/current.json'),'utf8'));
const current=fs.readFileSync(meta.path);assert.equal(sha1(current),meta.romSha1);
const installedItems=current.readUInt32LE(0xca7c4)&0x1ffffff;
assert(current.subarray(installedItems+32,installedItems+376*32)
  .equals(clean.subarray(0x51d1a0,0x51d1a0+375*32)), 'Original equipment records changed');
assert.equal(clean.readUInt32LE(0xd2154),0x1f6c);
assert.equal(clean.readUInt32LE(0xd2158),0x0851d180);
assert.equal(clean.readUInt32LE(0xd21a0),0x0851d180);
const missions=JSON.parse(fs.readFileSync(path.join(root,'build/reports/mission-item-dependencies.json'),'utf8'));
assert.equal(missions.candidateSha1,meta.romSha1);
// The original records use FFF1..FFF7 for the first seven20-item pools.
// Native also special-cases FFFF for the eighth pool; that pool has no original
// mission-record consumer. Its presence alone is not an acquisition witness.
assert.equal(clean.readUInt32LE(0xd006c),0xffff000f);
assert.equal(clean.readUInt32LE(0xd0070),0x08529494);
assert.equal(clean.readUInt32LE(0xd0024),0xffff);
assert.equal(clean.readUInt32LE(0xd0028),0x085295ac);
const pools=Array.from({length:8},(_,i)=>({index:i,selector:i===7?0xffff:0xfff1+i,
  items:Array.from({length:20},(_,j)=>clean.readUInt16LE(0x529494+i*40+j*2))}));
assert(pools.every(p=>p.items.every(id=>id>=1&&id<=375)));
// D2F78 chooses a weapon from floor(level/5), capped at9. The real caller
// C2778/C2784 selects this for original Throw148 and Hurl211. Whether an enemy
// can use these and Catch can acquire it is a separate encounter obligation.
assert.equal(clean.readUInt32LE(0xd2fb4),0x085295d4);
const throwPools=Array.from({length:10},(_,index)=>({index,levelMinimum:index*5,
  levelMaximum:index===9?99:index*5+4,
  items:Array.from({length:20},(_,j)=>clean.readUInt16LE(0x5295d4+index*40+j*2))}));
assert(throwPools.every(p=>p.items.every(id=>id>=1&&id<=375)));
const towns=[{id:2,name:'Cyril',at:0x528a44},{id:3,name:'Sprohm',at:0x528aa4},
 {id:4,name:'Muscadet',at:0x528b04},{id:5,name:'Cadoan',at:0x528b64},{id:6,name:'Baguba Port',at:0x528bc4}];
// CECF4 counts at most30 liberated territories; CC9F0 indexes one-based
// entries at townRecord+4+2*(position-1). The remaining record tail is not stock.
const townStock=towns.flatMap(town=>Array.from({length:30},(_,i)=>({town:town.id,name:town.name,
  liberatedTerritories:i+1,item:clean.readUInt16LE(town.at+4+i*2)}))).filter(row=>row.item);
assert(townStock.every(row=>row.item<=375));
const original=missions.originalRecords.filter(m=>m.pubEnabled);
const installed=missions.installedRecords.filter(m=>m.pubEnabled);
function sourceRows(records,item){return records.filter(m=>m.rewards.includes(item)).map(m=>({
  mission:m.record,name:m.name,repeatable:m.repeatable,unlock:m.unlock,requirements:m.requirements,
  month:m.pubMonth,location:m.eventLocation}));}
// Native46910 scans64 twelve-byte rewards, checks eight clan levels at
// 020021B6+2*skill, and permanently marks the claimed row in02002C08's64 bits.
assert.equal(clean.readUInt32LE(0x469b0),0x08528256);
assert.equal(clean.readUInt32LE(0x469ac),0x02002c08);
assert.equal(clean.readUInt32LE(0x469b4),0x020021b6);
const clanSkills=['Combat','Magic','Smithing','Craft','Appraise','Gather','Negotiate','Track'];
const clanGifts=Array.from({length:64},(_,index)=>{
  const at=0x528256+index*12,item=clean.readUInt16LE(at+1);
  if(!item){assert.equal(index,63,'Only the final clan reward is empty');return null;}
  assert.equal(clean[at],index);assert(item<=375);
  return {index,item,quantity:clean[at+3],repeatable:false,claimedBit:index,
    requirements:clanSkills.map((name,skill)=>({skill,name,level:clean[at+4+skill]})).filter(r=>r.level)};
}).filter(Boolean);
const formationEvents=new Map();
const unresolvedEventFormations=[];
for(let event=1;event<256;event++) {
  const at=0x563a70+event*12,formation=clean.readUInt16LE(at+4)||clean.readUInt16LE(at+2);
  if(!formation)continue;
  if(formation>442){unresolvedEventFormations.push({event,selector:formation});continue;}
  if(!formationEvents.has(formation))formationEvents.set(formation,[]);
  const linked=original.filter(m=>m.event===event);
  formationEvents.get(formation).push({event,formation,roamingClan:event>225?event-225:null,
    missions:linked.map(m=>({mission:m.record,name:m.name,repeatable:m.repeatable,unlock:m.unlock}))});
}
const formationItems=new Map();
const dynamicFormationEquipment=[];
for(let formation=1;formation<=442;formation++) {
  const at=0x54cd54+formation*40,count=clean[at],ptr=clean.readUInt32LE(at+4)&0x1ffffff;
  if(!count)continue;
  // Native9C18/A024 select enemy IDs independently from map/deployment IDs.
  // Native records include the first story party and Mortal Snow's last row.
  assert(count<=13&&ptr>=0x52a4d0&&ptr+count*48<=0x54bb30,`Formation domain${formation}`);
  for(let slot=0;slot<count;slot++)for(let gear=0;gear<5;gear++) {
    const unit=ptr+slot*48,item=clean.readUInt16LE(unit+8+gear*2);
    if(!item)continue;
    if(item>375){dynamicFormationEquipment.push({formation,slot,gear,selector:item});continue;}
    if(!formationItems.has(item))formationItems.set(item,[]);
    formationItems.get(item).push({formation,slot,gear,unitOffset:unit,job:clean[unit+1],type:clean[unit],
      support:clean[unit+41],events:formationEvents.get(formation)??[]});
  }
}
const rows=Array.from({length:375},(_,i)=>{
  const id=i+1,at=0x51d180+id*32,set=clean.readUInt16LE(at+29),teachingAt=0x520080+set*20;
  assert(set<225,`Native teaching-set domain${id}`);
  const n=clean[teachingAt];assert(n<=9,`Teaching count${id}`);
  const specialTeaching=[];
  const lessons=Array.from({length:n},(_,j)=>{
    const job=clean[teachingAt+2+j*2],index=clean[teachingAt+3+j*2],jp=0x521a14+job*52;
    // Three boot records use the native FF sentinel. These are not racial
    // job/AP records; retain them separately rather than reading a bogus job.
    if(job===255){specialTeaching.push({job,index});return null;}
    assert(job<72,`Native job${job}`);
    const race=clean[jp+4];assert(race<24);
    const bank=clean.readUInt32LE(0x51ba84+race*4)&0x1ffffff,ap=bank+index*8;
    return {job,jobName:nameAt(clean,0x526680,clean.readUInt16LE(jp)),race,index,
      name:nameAt(clean,0x5567f0,clean.readUInt16LE(ap)),type:clean[ap+6],
      action:clean.readUInt16LE(ap+4),ap:clean[ap+7]*10,key:`${job}:${index}`,racialKey:`${race}:${index}`};
  }).filter(Boolean);
  const ordinaryTiers=[0,1,2].filter(tier=>clean[at+12]&(16<<tier));
  const specialStock=townStock.filter(t=>t.item===id);
  const fixed=sourceRows(original,id),now=sourceRows(installed,id);
  const randomPools=pools.filter(p=>p.items.includes(id)).map(p=>({index:p.index,selector:p.selector,
    slots:p.items.filter(item=>item===id).length,originalMissions:sourceRows(original,p.selector),
    installedMissions:sourceRows(installed,p.selector)}));
  return {id,name:itemName(clean,id),category:clean[at+8],buy:clean.readUInt16LE(at+4),sell:clean.readUInt16LE(at+6),
    teachingSet:set,lessons,specialTeaching,ordinaryTiers,specialStock,
    clanBattleRewardTiers:[0x90,0xa0,0xc0].flatMap((mask,tier)=>clean[at+12]&mask?[tier]:[]),
    originalFixedMissions:fixed,installedFixedMissions:now,
    randomPools,throwPools:throwPools.filter(p=>p.items.includes(id)),clanGifts:clanGifts.filter(g=>g.item===id),
    formationPossession:formationItems.get(id)??[],mysteryCategory:clean[at+24],
    deterministicSourceClass:ordinaryTiers.length||specialStock.length?'shop-data':now.some(m=>m.repeatable)?'repeatable-fixed-mission-data':
      now.length?'finite-fixed-mission-data':'other-source-review-required'};
});
const teachers=new Map();
const racialTeachers=new Map();
for(const item of rows)for(const lesson of item.lessons){
 if(!teachers.has(lesson.key))teachers.set(lesson.key,[]);teachers.get(lesson.key).push(item.id);
 if(!racialTeachers.has(lesson.racialKey))racialTeachers.set(lesson.racialKey,new Set());
 racialTeachers.get(lesson.racialKey).add(item.id);
}
for(const item of rows)for(const lesson of item.lessons){
 lesson.otherTeachingItems=teachers.get(lesson.key).filter(id=>id!==item.id);
 lesson.otherRacialTeachingItems=[...racialTeachers.get(lesson.racialKey)].filter(id=>id!==item.id);
}
const review=rows.filter(item=>item.lessons.length&&!['shop-data','repeatable-fixed-mission-data'].includes(item.deterministicSourceClass));
const report={candidateSha1:meta.romSha1,cleanSha1:sha1(clean),equipmentCount:375,
 teachingItems:rows.filter(r=>r.lessons.length).length,jobLessonPairs:teachers.size,racialLessons:racialTeachers.size,
 originalEquipmentRecordsPreserved:true,installedItems,
 needsSourceReview:review.map(r=>r.id),approvedExamples:rows.filter(r=>[26,158,298,313].includes(r.id)),
 formationCount:442,formationIndexConvention:'Native IDs1..442; CD54+40*id, count+0, units+4; enemy selector A024',dynamicFormationEquipment,unresolvedEventFormations,clanGifts,throwPools,rows,
 limits:['Static shop entries still require native unlock/menu availability.',
 'Fixed repeatable missions retain original prerequisites and may require scarce items.',
 'Random mission pools remain random; formation possession does not prove stealability or repeat access.',
 'Throw/Hurl pools do not prove an eligible repeat enemy, usable Catch or retained inventory reward.',
 'Treasure hunts, recruit loadouts, event gifts, drops and link/mystery behavior require separate provenance.',
 'Review candidates are not automatically approved new recovery rewards; preserve original character/story prerequisites.']};
const out=path.join(root,'build/reports/vanilla-teaching-sources.json');
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({equipment:375,teachingItems:report.teachingItems,jobLessonPairs:report.jobLessonPairs,
 needsSourceReview:review.length,examples:report.approvedExamples.map(r=>({id:r.id,name:r.name,lessons:r.lessons.map(l=>l.name),
 fixed:r.originalFixedMissions.map(m=>m.mission),random:r.randomPools.map(p=>p.index),formations:r.formationPossession.length})),
 report:path.relative(root,out)},null,2));
