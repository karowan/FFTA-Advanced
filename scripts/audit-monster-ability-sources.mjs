/* Native event/formation/racial-lesson audit. Encounter lifecycle is separate. */
import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,nameAt,missions,sha1} from '../src/rom-data.mjs';
const clean=cleanROM(),meta=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/probes/integrated-jobs/current.json')));
const rom=fs.readFileSync(meta.path);
if(sha1(rom)!==meta.romSha1)throw Error('Current candidate hash mismatch');
const learnable=[266,267,269,271,274,275,276,277,278,282,288,293,294,297,300,301,304,305,308,309];
const rows=learnable.map(id=>({id,name:nameAt(clean,0x5567f0,clean.readUInt16LE(0x55187c+28*id)),sources:[]}));
const entries=[];
for(let clan=1;clan<=30;clan++) {
 const event=225+clan,p=0x563a70+12*event;
 if(rom[p+6]!==clan || rom[p+1]!==0xa8)throw Error('Native roaming event domain changed');
 entries.push({kind:'roaming-clan',clan,event,name:nameAt(clean,0x565f14,clan)});
}
for(const mission of missions(clean))if(mission.repeatable&&clean[mission.offset+69])
 entries.push({kind:'repeatable-mission',mission:mission.index,event:clean[mission.offset+69],name:mission.name});
for(const entry of entries) {
 const eventOffset=0x563a70+12*entry.event;
 // 9C18 publishes the primary map and optional secondary enemy formation;
 // A024 selects the latter when nonzero. Native IDs1..442 use CD54+40*id,
 // count+0 and unit pointer+4. Do not mix randomizer offsets with native IDs.
 const formation=rom.readUInt16LE(eventOffset+4)||rom.readUInt16LE(eventOffset+2);
 if(formation<1||formation>442)continue;
 const fp=0x54cd54+40*formation;
 const count=rom[fp],units=rom.readUInt32LE(fp+4)&0x1ffffff;
 if(!count)continue;
 if(count>13 || units<0x52a4d0 || units+48*count>0x54bb30)throw Error(`Formation bounds: ${formation}`);
 for(let slot=0;slot<count;slot++) {
  const unitOffset=units+48*slot,job=rom[unitOffset+1],jp=0x521a14+52*job,race=rom[jp+4];
  if(race<1||race>18)continue;
  const banks=rom.readUInt32LE(0x257e8)&0x1ffffff;
  const bank=rom.readUInt32LE(banks+race*4)&0x1ffffff;
  for(let index=1;index<160;index++) {
   if(!(rom[unitOffset+20+((index-1)>>3)]&(1<<((index-1)&7))))continue;
   const ap=bank+8*index,action=rom.readUInt16LE(ap+4),row=rows.find(r=>r.id===action);
   if(row&&rom[ap+6]===1)row.sources.push({...entry,formation,formationOffset:fp,slot,unitOffset,job,species:nameAt(clean,0x526680,rom.readUInt16LE(jp)),race,racialIndex:index});
  }
 }
}
if(rows.some(row=>!row.sources.length))throw Error('Learnable action lacks a mapped repeatable source');
const out=path.join(root,'build/expansion/probes/monster-access');fs.mkdirSync(out,{recursive:true});
const report={romSha1:sha1(rom),learnableActions:20,rows,formationCount:442,scope:'Current native enemy formation/mastery data, IDs1..442. Native9C18/A024 select event+4 when nonzero, otherwise event+2; the map formation may vary independently. Actual native CCD50 Learning flag and constructors/learning handlers are tested separately. A mapped repeatable-mission formation alone does not prove every dynamic event branch.'};
fs.writeFileSync(path.join(out,'sources.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({romSha1:report.romSha1,actions:rows.length,sources:rows.reduce((n,r)=>n+r.sources.length,0)}));
