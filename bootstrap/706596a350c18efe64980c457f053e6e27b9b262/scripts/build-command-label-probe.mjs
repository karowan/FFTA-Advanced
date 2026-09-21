import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
const out=path.join(root,'build/expansion/probes');
const rom=fs.readFileSync(path.join(out,'axe-visual.gba'));
const prior=JSON.parse(fs.readFileSync(path.join(out,'axe-visual.json')));
const engine=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(sha1(rom)!==prior.romSha1 || sha1(engine)!==prior.engineSha1 ||
 !rom.subarray(0x1100000,0x1100000+engine.length).equals(engine))throw Error('Stale axe visual/engine');
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
const offset=0x74c34,name='ffta_party_command_label_entry',clean=cleanROM();
const expected=Buffer.from('8000401902683fe0','hex');
if(!clean.subarray(offset,offset+8).equals(expected) || !rom.subarray(offset,offset+8).equals(expected))throw Error('Party command label hook conflict');
if(!symbols[name])throw Error('Missing party command label hook');
rom.writeUInt16LE(0x4b00,offset);rom.writeUInt16LE(0x4718,offset+2);rom.writeUInt32LE(symbols[name]|1,offset+4);
const changes=[{offset,name,size:8,expected:expected.toString('hex')}];
fs.writeFileSync(path.join(out,'command-label.gba'),rom);
fs.writeFileSync(path.join(out,'command-label.json'),JSON.stringify({status:'TEST ONLY: full-width new command labels in native party renderer; custom combat effects pending',baseSha1:prior.romSha1,romSha1:sha1(rom),engineSha1:sha1(engine),changes},null,2));
console.log('Built isolated native command label integration');
