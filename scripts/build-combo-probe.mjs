import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
import {ROMBuilder} from '../src/rom-builder.mjs';
const out=path.join(root,'build/expansion/probes');
const input=fs.readFileSync(path.join(out,'command-label.gba'));
const prior=JSON.parse(fs.readFileSync(path.join(out,'command-label.json')));
const action=JSON.parse(fs.readFileSync(path.join(out,'action-data.json')));
const engine=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(sha1(input)!==prior.romSha1 || sha1(engine)!==prior.engineSha1 ||
 !input.subarray(0x1100000,0x1100000+engine.length).equals(engine))throw Error('Stale combo input');
const clean=cleanROM();
const builder=new ROMBuilder(input,{start:Math.max(...action.allocations.map(a=>a.offset+a.bytes))});
const registry=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/registry.json')));
const profiles=[['SAM-C1',15,'Ninja Combo'],['DRK-C1',2,'Knight Combo'],
 ['VIK-C1',7,'Sword Combo'],['GEO-C1',17,'Wise Combo'],
 ['CHM-C1',23,'Thief Combo'],['BRD-C1',32,'Juggle Combo'],
 ['DNC-C1',6,'Lunge Combo'],['MYK-C1',11,'Red Combo']];
// All playable racial combo records resolve within the original 34-row bank.
// Monster banks contain no combo lessons; the council separately audits them.
const records=Buffer.alloc(136*4);
clean.copy(records,0,0x52736c,0x52736c+34*4);
const added=profiles.map(([id,donor,profile])=>{
 const lesson=registry.lessons.find(l=>l.id===id);
 if(!lesson || lesson.type!=='Combo' || lesson.globalAbilityId<128 || lesson.globalAbilityId>135)
  throw Error('Combo registry changed');
 const record=clean.subarray(0x52736c+donor*4,0x527370+donor*4);
 record.copy(records,lesson.globalAbilityId*4);
 return {id,globalAbilityId:lesson.globalAbilityId,donor,profile,record:record.toString('hex')};
});
const address=builder.allocate('expanded native combo participation profiles',records);
const refs=builder.repoint(0x0852736c,address,3);
if(JSON.stringify(refs)!==JSON.stringify([0x12e19c,0x12e3e4,0x130514]))throw Error('Combo references changed');
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
for(const [offset,end,name] of [[0xcd4c0,0xcd4cc,'ffta_combo_assigned_entry'],
 [0x12e130,0x12e13c,'ffta_combo_chance_entry'],
 [0x12e3b0,0x12e3be,'ffta_combo_range_entry'],
 [0x1304e0,0x1304ee,'ffta_combo_power_entry']]){
 if(!builder.rom.subarray(offset,end).equals(clean.subarray(offset,end)))throw Error('Combo hook conflict');
 if(!symbols[name])throw Error('Missing combo symbol');
 for(let p=offset;p<end;p+=2)builder.rom.writeUInt16LE(0x46c0,p);
 builder.rom.writeUInt16LE(0xb408,offset);const jump=(offset+5)&~3;
 if(jump+8>end)throw Error('Combo hook length');
 builder.rom.writeUInt16LE(0x4b00,jump);builder.rom.writeUInt16LE(0x4718,jump+2);
 builder.rom.writeUInt32LE(symbols[name]|1,jump+4);
 builder.changes.push({offset,size:end-offset,name,expected:clean.subarray(offset,end).toString('hex')});
}
fs.writeFileSync(path.join(out,'combo-input.gba'),input);
fs.writeFileSync(path.join(out,'combo.gba'),builder.rom);
fs.writeFileSync(path.join(out,'combo.json'),JSON.stringify({status:'TEST ONLY: eight combo profiles and primary-weapon gates; native JP/chain path retained, battle acceptance pending',
 baseSha1:prior.romSha1,romSha1:sha1(builder.rom),engineSha1:sha1(engine),address,
 originalCount:34,totalCount:136,added,allocations:builder.allocations,changes:builder.changes},null,2));
console.log('Built eight combo profiles with scoped weapon gates');
