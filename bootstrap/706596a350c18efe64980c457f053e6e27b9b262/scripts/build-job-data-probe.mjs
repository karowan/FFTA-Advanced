import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
import {ROMBuilder,encodeText} from '../src/rom-builder.mjs';
import {equipmentDisplayName} from '../src/equipment-display-names.mjs';

const registry=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/registry.json')));
const specification=fs.readFileSync(path.join(root,'JOB-CLASS-SPECIFICATION.md'),'utf8');
const base=fs.readFileSync(path.join(root,'build/foundation/FFTA_vanillaplus_dev.gba'));
const clean=cleanROM(),builder=new ROMBuilder(base);
const rows=specification.split(/\r?\n/).filter(l=>l.startsWith('| ')).map(l=>l.split('|').slice(1,-1).map(x=>x.trim()));
const jobs=registry.jobs.filter(j=>!j.existing);
const permissionBase=0x51d0f4;
let maxPermission=0,maxRequirement=0;
for(let j=0;j<116;j++){
  maxPermission=Math.max(maxPermission,clean[0x521a14+j*52+0x2d]);
  maxRequirement=Math.max(maxRequirement,clean[0x521a14+j*52+0x30]);
}
const requirementsBase=clean.readUInt32LE(0xc8b18)&0x1ffffff;
const permissions=Buffer.alloc((maxPermission+1+jobs.length)*4);
clean.copy(permissions,0,permissionBase,permissionBase+(maxPermission+1)*4);
const requirements=Buffer.alloc((maxRequirement+1+jobs.length)*4);
clean.copy(requirements,0,requirementsBase,requirementsBase+(maxRequirement+1)*4);
const records=Buffer.alloc(126*52);
clean.copy(records,0,0x521a14,0x521a14+116*52);
const names=Buffer.alloc((753+85+10)*4);
base.copy(names,0,0x526680,0x526680+753*4);
// Reserve the approved equipment name IDs as real strings too; no equipment
// records or stock are introduced by this bounded job-data probe.
for(const item of registry.items)names.writeUInt32LE(builder.allocate(item.id+' name',encodeText(equipmentDisplayName(item))),item.nameId*4);
const chassis={
  SAM:{donor:6,move:4,jump:3,evade:50,types:[9,21,23,24,25,26]},
  DRK:{donors:{1:3,2:15},move:3,jump:2,evade:40,types:[1,5,6,20,21,23,24,25]},
  VIK:{donor:13,move:3,jump:2,evade:40,types:[31,21,23,24,25]},
  GEO:{donor:27,move:3,jump:2,evade:45,types:[11,12,23,25,26]},
  CHM:{donors:{3:25,5:41},move:4,jumps:{3:2,5:3},evade:45,types:[7,12,23,25,26]},
  BRD:{donor:36,move:4,jump:3,evade:45,types:[7,16,23,25,26]},
  DNC:{donor:29,move:4,jump:3,evade:55,types:[7,8,23,25]},
  MYK:{donor:30,move:4,jump:2,evade:45,types:[3,8,20,21,23,24,25]},
};
const profiles=[];
for(const [i,job] of jobs.entries()){
  const title=`${job.raceName} ${job.name}`;
  const statRows=rows.filter(r=>r[0]===title&&r.length===8&&r.slice(1).every(v=>/^\d+(?:\.\d+)?$/.test(v)));
  if(statRows.length!==2)throw Error(`Ambiguous stat template ${title}`);
  const growth=statRows[0].slice(1).map(Number),stats=statRows[1].slice(1).map(Number);
  const [hp,mp,attack,defense,power,resistance,speed]=stats;
  const c=chassis[job.group],donor=c.donor??c.donors[job.race];
  if(clean[0x521a14+donor*52+4]!==job.race)throw Error('Cross-race graphics donor');
  const record=Buffer.from(clean.subarray(0x521a14+donor*52,0x521a14+(donor+1)*52));
  record.writeUInt16LE(job.nameId,0);record[4]=job.race;record[5]=0;
  // The expansion dispatch represents learned commands with job IDs. This
  // field requires that dispatch and is not enabled in the standalone probe.
  record[0x10]=job.id;record[0x11]=0;
  record.writeUInt32LE(0x01249248,0x12);record[0x16]=50;
  record[0x17]=hp;record[0x18]=mp;record[0x19]=speed;
  if([attack,defense,power,resistance].some(v=>v<0||v>4095))throw Error('12-bit stat overflow');
  record.writeUIntLE(attack|(defense<<12),0x1a,3);
  record.writeUIntLE(power|(resistance<<12),0x1d,3);
  const nativeGrowth=[growth[0],growth[1],growth[6],growth[2],growth[3],growth[4],growth[5]].map(v=>Math.round(v*10));
  if(nativeGrowth.some(v=>v<0||v>255))throw Error('Growth byte overflow');
  Buffer.from(nativeGrowth).copy(record,0x20);
  record[0x28]=c.move;record[0x29]=c.jump??c.jumps[job.race];record[0x2a]=c.evade;
  record[0x2b]=0x21;record[0x2c]=0;record[0x31]=0;
  const permissionIndex=maxPermission+1+i;
  const mask=[...c.types,27,28,29].reduce((value,type)=>value|(1<<(type-1)),0)>>>0;
  permissions.writeUInt32LE(mask,permissionIndex*4);record[0x2d]=permissionIndex;
  const lessons=registry.lessons.flatMap(a=>a.owners.filter(o=>o.jobId===job.id).map(o=>o.abilityIndex));
  record[0x2e]=Math.min(...lessons);record[0x2f]=Math.max(...lessons);
  if(job.prerequisites.length){
    const index=maxRequirement+1+i;
    if(job.prerequisites.length!==2)throw Error('Expected paired native job prerequisites');
    record[0x30]=index;
    Buffer.from(job.prerequisites.flatMap(p=>[p.jobId,p.actions])).copy(requirements,index*4);
  }else record[0x30]=0;
  record.copy(records,job.id*52);
  names.writeUInt32LE(builder.allocate(title+' name',encodeText(job.name)),job.nameId*4);
  profiles.push({...job,donor,stats,growth,nativeGrowth,move:record[0x28],jump:record[0x29],evade:c.evade,
    permissionIndex,permissionMask:mask,requirementIndex:record[0x30],lessonIndices:lessons,
    recordHex:record.toString('hex')});
}
const addresses={names:builder.allocate('item/job name pointers',names),
  jobs:builder.allocate('expanded job records',records),
  permissions:builder.allocate('equipment permission masks',permissions),
  requirements:builder.allocate('job prerequisite records',requirements)};
builder.repoint(0x08526680,addresses.names,74);
builder.repoint(0x08521a14,addresses.jobs);
builder.repoint(0x0851d0f4,addresses.permissions,3);
builder.repoint(requirementsBase+0x08000000,addresses.requirements);
const out=path.join(root,'build/expansion/probes');fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'job-data.gba'),builder.rom);
fs.writeFileSync(path.join(out,'job-data.json'),JSON.stringify({status:'Native job data probe; new job selection/commands/effects not enabled',
  baseSha1:sha1(base),romSha1:sha1(builder.rom),addresses,profiles,allocations:builder.allocations,changes:builder.changes,
  remaining:['Custom noncontiguous lesson lists and AP consumers','Job wheel, command dispatch and portraits/icons',
             'Both native shield coexistence branches','Actions/reactions/supports/combos and acquisition']},null,2));
console.log(JSON.stringify({jobs:profiles.length,addresses,originalPointerChanges:builder.changes.length}));
