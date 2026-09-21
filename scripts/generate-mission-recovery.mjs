/* Derive original earned-supply rules. Does not patch or publish a ROM. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root,cleanROM,itemName,sha1} from '../src/rom-data.mjs';
import {encodeText} from '../src/rom-builder.mjs';
const image=cleanROM(),first=407,count=64;
const gear=JSON.parse(fs.readFileSync(path.join(root,'notes/vanilla-equipment-recovery.json'),'utf8'));
assert.equal(gear.routes.length,6);assert.equal(gear.requiredFlag,54);
assert.equal(gear.baseFee%200,0);assert(gear.baseFee/200<=255);
for(const [index,rule] of gear.routes.entries()) {
 assert.equal(rule.mission,first+count+index);
 assert.equal(itemName(image,rule.item),rule.name);
 assert(rule.item>0&&rule.item<=361);
 const mission=Number.isInteger(rule.originalMission),gift=Number.isInteger(rule.originalGift);
 assert(mission!==gift,'Exactly one original opportunity is required');
 if(mission)assert(rule.originalMission>0&&rule.originalMission<407);
 else {
  assert(rule.originalGift>=0&&rule.originalGift<63);
  const at=0x528256+rule.originalGift*12;
  assert.equal(image[at],rule.originalGift,'Gift receipt identity');
  assert.equal(image.readUInt16LE(at+1),rule.item,'Recovery matches original gift reward');
  rule.originalGiftRequirements=Array.from(image.subarray(at+4,at+12));
 }
 const at=0x55ae4c+rule.mission*70;
 assert.equal(image.readUInt16LE(at),rule.mission);
 assert(image.subarray(at+2,at+70).every(v=>v===0),'Equipment recovery slot occupied');
 rule.description=['Recover rare teaching gear',mission?'after its original mission.':'after claiming its clan gift.','Send a member for twenty','days to find a lost copy.',rule.name,'Clan Recovery Office'].join('\n');
}
for(const [offset,expected] of [[0xcfd00,'e97870200840741c0194291c'],[0xd0590,'f0b557464e464546e0b484b0'],[0x5ee20,'b4f7a0fa2868044a80180e21']])
 assert.equal(image.subarray(offset,offset+12).toString('hex'),expected,'Recovery hook preimage');
assert.equal(image.readUInt32LE(0x5ee38),0x119a,'Native acceptance state offset');
const out=process.argv[2]?path.resolve(process.argv[2]):path.join(root,'build/expansion/probes/recovery-draft');
const relative=path.relative(path.join(root,'build'),out);
assert(relative&&!relative.startsWith('..')&&!path.isAbsolute(relative),'Output must be inside ignored build/');
const rows=Array.from({length:512},(_,record)=>{
 const at=0x55ae4c+record*70;
 return {record,enabled:record>0&&!!(image[at+3]&0x70),repeatable:!!(image[at+0x41]&8),
  rewards:[image.readUInt16LE(at+0x22),image.readUInt16LE(at+0x24)],
  requirements:[0,1].map(slot=>({id:image[at+0x36+slot],consumed:!!(image[at+0x41]&(16<<slot))})).filter(r=>r.id)};
}).filter(row=>row.enabled);
const ids=[...new Set(rows.flatMap(row=>row.requirements.map(r=>r.id)))].sort((a,b)=>a-b);
const candidates=ids.filter(id=>!rows.some(row=>row.repeatable&&row.rewards.includes(id+375)&&!row.requirements.some(r=>r.id===id)));
assert.equal(candidates.length,count);
const rules=candidates.map((item,index)=>{
 const mission=first+index,at=0x55ae4c+mission*70;
 assert.equal(image.readUInt16LE(at),mission);
 assert(image.subarray(at+2,at+70).every(v=>v===0),'Reserved mission body occupied');
 const sources=rows.filter(r=>r.rewards.includes(item+375));
 const uses=rows.filter(r=>r.requirements.some(q=>q.id===item));
 assert(sources.length>0&&sources.length<=3&&uses.length>0&&uses.length<=3);
 assert(sources.every(r=>!r.repeatable)&&uses.every(r=>!r.repeatable||!r.requirements.some(q=>q.id===item&&q.consumed)),
  'Completion bits cannot count repeatable earned/consumed edges');
 return {mission,item,name:itemName(image,item+375),
  sources:sources.map(r=>({mission:r.record,copies:r.rewards.filter(id=>id===item+375).length})),
  uses:uses.map(r=>({mission:r.record,required:r.requirements.filter(q=>q.id===item).length,consumed:r.requirements.filter(q=>q.id===item&&q.consumed).length,repeatable:r.repeatable}))};
});
// Native CE8A8 uses this explicit300-record list, not a count of every flag.
const completion=[];
for(let at=0x529ee4;image.readUInt16LE(at)!==0xffff;at+=2) {
 assert(at<0x529ee4+602,'Unexpected completion-list terminator');
 completion.push(image.readUInt16LE(at));
}
assert.equal(completion.length,300);
assert(completion.every(id=>id<first||id>=first+count));
let header='/* Generated from hash-verified original USA mission data. */\n';
header+='static const FFTA_RecoveryRule ffta_recovery_rules[FFTA_RECOVERY_COUNT]={\n';
for(const rule of rules) {
 const sources=rule.sources.map(s=>`{${s.mission},${s.copies}}`).join(',');
 const uses=rule.uses.map(s=>`{${s.mission},${s.required},${s.consumed},${Number(s.repeatable)}}`).join(',');
 header+=` {${rule.item},${rule.sources.length},${rule.uses.length},{${sources}},{${uses}}}, /* ${rule.mission}: ${rule.name} */\n`;
}
header+='};\n';
header+=`static const unsigned ffta_gear_recovery_required_flag=${gear.requiredFlag};\n`;
header+='static const FFTA_GearRecoveryRule ffta_gear_recovery_rules[FFTA_GEAR_RECOVERY_COUNT]={\n';
for(const rule of gear.routes)header+=` {${rule.item},${rule.originalMission??65535},${rule.originalGift??65535}}, /* ${rule.mission}: ${rule.name} */\n`;
header+='};\n';
fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'mission-recovery-data.h'),header);
// The native second description bank covers records201..511; its final table
// entry is a sentinel, not another description. Retain every original byte and
// append uncompressed recovery entries with native six-line dialog geometry.
const oldBank=0x4aadfc,oldEnd=0x4b5374;
assert.equal(image.readUInt16LE(oldBank),312*2);
assert.equal(image.readUInt16LE(oldBank+311*2),0xffff);
let descriptions=Buffer.from(image.subarray(oldBank,oldEnd));
const names=[],records=[];
for(const rule of [...rules,...gear.routes]) {
 const isGear=rule.mission>=first+count;
 if(!isGear){
  rule.title=`Found: ${rule.name}`;
  rule.description=['Lost a mission item your','clan earned before its use.','Send a member to recover','one missing copy.',rule.name,'Clan Recovery Office'].join('\n');
 }
 const body=encodeText(rule.description);
 const text=Buffer.concat([Buffer.from([0x68,0x18]),body.subarray(0,-1),Buffer.from([0x40,0x77,0x40,0x63,0])]);
 assert(descriptions.length+text.length<65535,'Description bank exceeds native16-bit offsets');
 descriptions.writeUInt16LE(descriptions.length,(rule.mission-201)*2);
 descriptions=Buffer.concat([descriptions,text]);
 names.push({mission:rule.mission,title:rule.title,bytes:encodeText(rule.title).toString('hex')});
 const record=Buffer.alloc(70);
 record.writeUInt16LE(rule.mission);
 record[3]=0x10; // Rank1; ordinary dispatch type0, available in every pub.
 for(const at of [7,10,13])record[at]=2; // Native ignored flag predicate.
 record[14]=10<<3; // Ten days posted; accepted dispatch has no expiry.
 const days=isGear?gear.dispatchDays:5;
 record[16]=8|((days&3)<<6);record[17]=days>>2; // Native day mode1.
 record.writeUInt16LE(rule.item+(isGear?0:375),0x22); // One ordinary or quest item.
 record[0x3e]=isGear?gear.baseFee/200:1; // Base fee before town/clan adjustments.
 record[0x3f]=record[0x40]=isGear?gear.cooldownDays:1;
 record[0x41]=8; // Repeatable, cancel allowed, both rewards visible.
 record[0x43]=1; // Easy native dispatch threshold; ordinary quality still used.
 records.push({mission:rule.mission,bytes:record.toString('hex')});
}
fs.writeFileSync(path.join(out,'mission-recovery-descriptions.bin'),descriptions);
const report={cleanSha1:sha1(image),first,count,rules,gear,serviceCount:count+gear.routes.length,names,records,descriptionBank:{original:oldBank,originalEnd:oldEnd,bytes:descriptions.length,literal:0x13cc0},
 baseFee:200,dispatchDays:5,postingDays:10,cooldownDays:1,
 scope:'Source-derived recovery catalog and native mission content; installed only by the integrated builder.'};
fs.writeFileSync(path.join(out,'catalog.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({cleanSha1:report.cleanSha1,first,count,out,scope:report.scope},null,2));
