/* Enumerate original recruitment entry points; runtime consumers prove access. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root,cleanROM,sha1,itemName,nameAt} from '../src/rom-data.mjs';
const clean=cleanROM(),meta=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/probes/integrated-jobs/current.json')));
const rom=fs.readFileSync(meta.path);assert.equal(sha1(rom),meta.romSha1);
const ledger=JSON.parse(fs.readFileSync(path.join(root,'build/reports/mission-item-dependencies.json')));
assert.equal(ledger.candidateSha1,meta.romSha1);
const names={138:93,140:27,142:94,144:95,146:97,148:96};
const special={150:['Ezel',10,600,618,384],152:['Babus',9,601,619,385],
 154:['Ritz',4,602,620,386],156:['Shara',12,603,621,null],158:['Cid',94,604,622,387]};
const items=Array.from({length:128},(_,id)=>({id,rule:rom[0x521214+id*16+14],bonus:rom[0x521214+id*16+13]}));
const rows=[];
for(let rule=138;rule<=158;rule+=2){
 const p=0x529764+12*rule;assert.deepEqual(rom.subarray(p,p+24),clean.subarray(p,p+24));
 const [name,type,acceptedFlag,historyFlag,retryException]=special[rule]??[nameAt(clean,0x5516d0,names[rule]),1,null,null,null];
 const missionRecords=ledger.installedRecords.filter(m=>rom[0x55ae4c+70*m.record+53]===rule);
 const carriedItems=items.filter(i=>i.rule===rule).map(i=>({...i,name:itemName(clean,i.id+375)}));
 assert(missionRecords.length||carriedItems.length,'Recruit has no declared entry point');
 rows.push({rule,name,type,nameIndex:names[rule]??null,chance:rom[p],job:rom[p+3],acceptedFlag,historyFlag,retryException,
  originalMissions:ledger.originalRecords.filter(m=>clean[0x55ae4c+70*m.record+53]===rule).map(m=>m.record),
  missions:missionRecords,carriedItems});
}
assert.equal(rows.length,11);
assert.deepEqual(rom.subarray(0x521214,0x521a14),clean.subarray(0x521214,0x521a14));
const report={candidateSha1:meta.romSha1,cleanSha1:sha1(clean),rows,
 scope:'All six named item/mission recruits and five special story rules. Entries and flags require native access/policy validation; table presence is not campaign proof.'};
const out=path.join(root,'build/reports/secret-recruit-sources.json');fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({candidateSha1:meta.romSha1,recruits:rows.map(r=>({name:r.name,rule:r.rule,missions:r.missions.map(m=>m.record),items:r.carriedItems.map(i=>i.id)}))},null,2));
