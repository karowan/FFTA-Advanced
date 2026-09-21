import fs from 'node:fs';
import path from 'node:path';
import {root,sha1,cleanROM} from '../src/rom-data.mjs';
const out=path.join(root,'build/expansion/probes');
const rom=fs.readFileSync(path.join(out,'command-data.gba'));
const prior=JSON.parse(fs.readFileSync(path.join(out,'command-data.json')));
if(sha1(rom)!==prior.romSha1)throw Error('Stale command data');
const engine=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(!rom.subarray(0x1100000,0x1100000+engine.length).equals(engine))throw Error('Stale command engine');
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
const clean=cleanROM(),changes=[];
for(const [offset,name] of [[0x25fdc,'ffta_battle_command_entry'],[0x26ab8,'ffta_special_action_entry'],[0x133d78,'ffta_action_command_entry'],[0x1341ec,'ffta_action21_entry']]) {
  if(!rom.subarray(offset,offset+8).equals(clean.subarray(offset,offset+8)))throw Error('Conflicting command predicate');
  if(!symbols[name])throw Error('Missing command predicate');
  rom.writeUInt16LE(0x4b00,offset);rom.writeUInt16LE(0x4718,offset+2);rom.writeUInt32LE(symbols[name]|1,offset+4);
  changes.push({offset,name,size:8});
}
for(const [offset,end,name,saved] of [
  [0x26d58,0x26d6a,'ffta_ordinary_init',true],
  [0x26f6c,0x26f78,'ffta_ordinary_next',true],
  [0x26fb0,0x26fbe,'ffta_restricted_init',true],
  [0x2709c,0x270a4,'ffta_restricted_next',false],
  [0x279fa,0x27a0a,'ffta_second_init',true],
  [0x27ab4,0x27abe,'ffta_second_next',false],
  [0x133fe6,0x133ff8,'ffta_ai_init',true],
  [0x13406e,0x13407a,'ffta_ai_next',true],
  [0x7b990,0x7b99c,'ffta_party_list_init',true],
  [0x7b9fe,0x7ba0c,'ffta_party_list_next',true],
  [0x7c338,0x7c344,'ffta_primary_init',true],
  [0x7c410,0x7c41e,'ffta_primary_next',true],
  [0x7c476,0x7c482,'ffta_secondary_init',true],
  [0x7c53a,0x7c548,'ffta_secondary_next',true]
]) {
  if(!rom.subarray(offset,end).equals(clean.subarray(offset,end)))throw Error(`Conflicting command loop ${name}`);
  if(!symbols[name])throw Error(`Missing command loop ${name}`);
  for(let p=offset;p<end;p+=2)rom.writeUInt16LE(0x46c0,p);
  if(saved)rom.writeUInt16LE(0xb408,offset);
  const jump=saved ? (offset+5)&~3 : offset;
  if(jump%4 || jump+8>end)throw Error('Command loop stub too short/alignment');
  rom.writeUInt16LE(0x4b00,jump);rom.writeUInt16LE(0x4718,jump+2);
  rom.writeUInt32LE(symbols[name]|1,jump+4);
  changes.push({offset,name,size:end-offset,savesR3:saved,expected:clean.subarray(offset,end).toString('hex')});
}
fs.writeFileSync(path.join(out,'command-core.gba'),rom);
fs.writeFileSync(path.join(out,'command-core.json'),JSON.stringify({status:'TEST ONLY: explicit predicates and paired native command iterators; all new battle effects pending',baseSha1:prior.romSha1,romSha1:sha1(rom),engineSha1:sha1(engine),changes},null,2));
console.log('Built isolated command predicate integration');
