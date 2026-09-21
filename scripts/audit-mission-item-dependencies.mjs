/* Read-only mission-item graph. Static sources do not prove pub availability. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root,cleanROM,nameAt,itemName,sha1} from '../src/rom-data.mjs';
const clean=cleanROM();
const meta=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/probes/integrated-jobs/current.json'),'utf8'));
const current=fs.readFileSync(meta.path);assert.equal(sha1(current),meta.romSha1);
// Native CF118: record+41 bits4/5 consume required slots1/2 only on success.
assert.equal(clean.subarray(0xcf1a4,0xcf1a8).toString('hex'),'10200140');
assert.equal(clean.subarray(0xcf1e6,0xcf1ea).toString('hex'),'20200140');
// CFCD0 loops indices1..511, not the older helper's truncated0..405.
assert.equal(clean.readUInt32LE(0xd058c),511);
function records(image){return Array.from({length:512},(_,record)=>{
 const offset=0x55ae4c+record*70,textId=image.readUInt16LE(offset),event=image[offset+69];
 return {record,name:nameAt(image,0x55a64c,textId),textId,type:image[offset+2],
 pubEnabled:record>0&&!!(image[offset+3]&0x70),repeatable:!!(image[offset+0x41]&8),
 requirements:[0x36,0x37].map((at,slot)=>({localId:image[offset+at],consumed:!!(image[offset+0x41]&(16<<slot))})).filter(r=>r.localId),
 rewards:[0x22,0x24].map(at=>image.readUInt16LE(offset+at)),
 unlock:[5,8,11].map(at=>{const selector=image.readUInt16LE(offset+at);return {
  selector,kind:selector<=0x5ff?'flag':'counter',index:selector<=0x5ff?selector:selector-0x600,value:image[offset+at+2]};}),
 pubDurationDays:(image[offset+14]>>3)|((image[offset+15]&7)<<5),
 pubMonth:image[offset+14]&7,event,eventLocation:event?image[0x563a70+event*12]:null,
 specialAbsentFlags:textId===383?[600,601,602,603,604]:[],
 };});}
const originalRecords=records(clean),installedRecords=records(current);
const original=originalRecords.filter(m=>m.pubEnabled),installed=installedRecords.filter(m=>m.pubEnabled);
const ids=[...new Set(original.flatMap(m=>m.requirements.map(r=>r.localId)))].sort((a,b)=>a-b);
const compact=m=>({record:m.record,name:m.name,repeatable:m.repeatable,requirements:m.requirements,unlock:m.unlock,pubMonth:m.pubMonth,
 pubDurationDays:m.pubDurationDays,eventLocation:m.eventLocation,specialAbsentFlags:m.specialAbsentFlags});
const items=ids.map(id=>{
 const requiredBy=original.filter(m=>m.requirements.some(r=>r.localId===id));
 const consumers=requiredBy.filter(m=>m.requirements.some(r=>r.localId===id&&r.consumed));
 const sources=original.filter(m=>m.rewards.includes(id+375));
 const patched=installed.filter(m=>m.rewards.includes(id+375));
 const recoveryIds=new Set((meta.missionRecovery?.rules??[]).map(r=>r.mission));
 const recoverySources=patched.filter(m=>recoveryIds.has(m.record));
 // Earned-supply services are conditional replacements, not independent new
 // supply. Do not turn the original64 finite chains into88 renewable claims.
 const renewable=patched.filter(m=>m.repeatable&&!recoveryIds.has(m.record));
 const independent=renewable.filter(m=>!m.requirements.some(r=>r.localId===id));
 return {localId:id,globalId:id+375,name:itemName(clean,id+375),
  requiredBy:requiredBy.map(compact),consumers:consumers.map(compact),
  originalRewardSources:sources.map(compact),installedRewardSources:patched.map(compact),
  conditionalRecoverySourceRecords:recoverySources.map(m=>m.record),
  independentRepeatableSourceRecords:independent.map(m=>m.record),
  staticRisk:independent.length?'repeatable-source-needs-gate-proof':sources.length?'finite-or-self-dependent-source':'no-direct-mission-reward-source',
  limits:['Event/script rewards, item disposal, progression gates and mutual dependency cycles require separate native analysis.']};
});
const report={cleanSha1:sha1(clean),candidateSha1:meta.romSha1,missionRecords:originalRecords.length,pubEnabledRecords:original.length,
 originalRecords,installedRecords,
 requiredItemCount:items.length,consumptionSlots:original.reduce((n,m)=>n+m.requirements.filter(r=>r.consumed).length,0),
 items,scope:'Read-only original/installed direct mission-reward dependency graph; candidates, not proven campaign lockouts or recovery acceptance.'};
const out=path.join(root,'build/reports/mission-item-dependencies.json');fs.mkdirSync(path.dirname(out),{recursive:true});
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({candidateSha1:meta.romSha1,missionRecords:report.missionRecords,
 pubEnabledRecords:report.pubEnabledRecords,requiredItemCount:items.length,consumptionSlots:report.consumptionSlots,
 independentRepeatableCandidates:items.filter(i=>i.independentRepeatableSourceRecords.length).length,
 finiteOrSelfDependentCandidates:items.filter(i=>i.staticRisk==='finite-or-self-dependent-source').length,
 conditionalRecoveryCandidates:items.filter(i=>i.conditionalRecoverySourceRecords.length).length,
 noDirectSource:items.filter(i=>i.staticRisk==='no-direct-mission-reward-source').length,
 report:path.relative(root,out)},null,2));
