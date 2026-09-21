import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
const out=path.join(root,'build/expansion/probes');
const rom=fs.readFileSync(path.join(out,'job-ui.gba'));
const prior=JSON.parse(fs.readFileSync(path.join(out,'job-ui.json')));
const engine=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(sha1(rom)!==prior.romSha1 || !rom.subarray(0x1100000,0x1100000+engine.length).equals(engine))throw Error('Stale jobUI/engine');
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
const clean=cleanROM(),changes=[];
for(const [offset,end,name] of [
 [0x986da,0x986e6,'ffta_axe_actor_visual'],[0xa58a0,0xa58ac,'ffta_axe_hit_sound'],
 [0xa7edc,0xa7ee8,'ffta_axe_swing_sound'],[0xb3c64,0xb3c70,'ffta_axe_effect_visual']
]) {
 if(!rom.subarray(offset,end).equals(clean.subarray(offset,end)))throw Error('Visual hook conflict');
 if(!symbols[name])throw Error('Missing visual hook');
 for(let p=offset;p<end;p+=2)rom.writeUInt16LE(0x46c0,p);
 rom.writeUInt16LE(0xb408,offset);const jump=(offset+5)&~3;
 if(jump+8>end)throw Error('Visual hook length');
 rom.writeUInt16LE(0x4b00,jump);rom.writeUInt16LE(0x4718,jump+2);rom.writeUInt32LE(symbols[name]|1,jump+4);
 changes.push({offset,name,size:end-offset,expected:clean.subarray(offset,end).toString('hex')});
}
fs.writeFileSync(path.join(out,'axe-visual.gba'),rom);
fs.writeFileSync(path.join(out,'axe-visual.json'),JSON.stringify({status:'TEST ONLY: axe visual switches use existing heavy-blade donor; custom combat effects pending',baseSha1:prior.romSha1,romSha1:sha1(rom),engineSha1:sha1(engine),changes},null,2));
console.log('Built isolated axe visual integration');
