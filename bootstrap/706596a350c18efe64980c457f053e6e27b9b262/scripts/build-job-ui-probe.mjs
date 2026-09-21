import fs from 'node:fs';
import path from 'node:path';
import {root,sha1,cleanROM} from '../src/rom-data.mjs';
const out=path.join(root,'build/expansion/probes');
const rom=fs.readFileSync(path.join(out,'action-data.gba'));
const prior=JSON.parse(fs.readFileSync(path.join(out,'action-data.json')));
const engine=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(sha1(rom)!==prior.romSha1 || !rom.subarray(0x1100000,0x1100000+engine.length).equals(engine))throw Error('Stale action/engine for job UI');
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
const clean=cleanROM(),changes=[];
for(const [offset,end,name,saved] of [
  [0x85c90,0x85c98,'ffta_wheel_initial_entry',false],
  [0x8616c,0x86178,'ffta_wheel_input_entry',true],
  [0x861be,0x861c8,'ffta_wheel_confirm_entry',true],
  [0xcb9e0,0xcb9e8,'ffta_job_icon_entry',false],
  [0xcba14,0xcba1c,'ffta_job_palette_entry',false],
  [0x12e6a4,0x12e6ac,'ffta_reaction_guard_entry',false]
]) {
  if(!rom.subarray(offset,end).equals(clean.subarray(offset,end)))throw Error('Conflicting job UI hook '+name);
  if(!symbols[name])throw Error('Missing job UI hook '+name);
  for(let p=offset;p<end;p+=2)rom.writeUInt16LE(0x46c0,p);
  if(saved)rom.writeUInt16LE(0xb408,offset);
  const jump=saved ? (offset+5)&~3 : offset;
  if(jump%4 || jump+8>end)throw Error('Job UI hook size/alignment');
  rom.writeUInt16LE(0x4b00,jump);rom.writeUInt16LE(0x4718,jump+2);rom.writeUInt32LE(symbols[name]|1,jump+4);
  changes.push({offset,name,size:end-offset,savesR3:saved,expected:clean.subarray(offset,end).toString('hex')});
}
fs.writeFileSync(path.join(out,'job-ui.gba'),rom);
fs.writeFileSync(path.join(out,'job-ui.json'),JSON.stringify({status:'TEST ONLY: paged job wheel and donor icons; page hint and all custom combat effects pending; new reactions explicitly inactive',baseSha1:prior.romSha1,romSha1:sha1(rom),engineSha1:sha1(engine),changes},null,2));
console.log('Built isolated job wheel integration');
