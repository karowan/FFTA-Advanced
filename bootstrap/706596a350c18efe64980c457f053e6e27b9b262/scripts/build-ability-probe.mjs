import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
const out=path.join(root,'build/expansion/probes');
const input=fs.readFileSync(path.join(out,'content-inventory.gba'));
const prior=JSON.parse(fs.readFileSync(path.join(out,'content-inventory.json')));
if(sha1(input)!==prior.romSha1)throw Error('Stale content/inventory probe');
const clean=cleanROM(),rom=Buffer.from(input);
const engine=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(!rom.subarray(0x1100000,0x1100000+engine.length).equals(engine))throw Error('Stale engine');
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
const changes=[];
for(const [offset,name] of [[0xcd560,'ffta_ability_available_entry'],[0xcd544,'ffta_ability_grant_entry'],[0xcd2c4,'ffta_job_mastered_entry'],[0xc9078,'ffta_secondary_job_entry'],[0xc94d0,'ffta_lesson_job_entry'],[0x7170,'ffta_native_free_entry'],[0x9de94,'ffta_snapshot_entry'],[0x97000,'ffta_manager_entry'],[0x1443fc,'ffta_library_copy_entry'],[0x7109c,'ffta_party_copy_entry'],[0x7d8ec,'ffta_command_browse_entry'],[0xc9f88,'ffta_import_abilities_entry']]) {
  if(!rom.subarray(offset,offset+8).equals(clean.subarray(offset,offset+8)))throw Error('Conflicting AP hook');
  if(!symbols[name])throw Error('Missing AP symbol');
  rom.writeUInt16LE(0x4b00,offset);rom.writeUInt16LE(0x4718,offset+2);
  rom.writeUInt32LE(symbols[name]|1,offset+4);
  changes.push({offset,name,size:8});
}
for(const [offset,previous,name] of [
  [0x13aa4c,'ffta_load_normal','ffta_load_abilities_normal'],
  [0x13aadc,'ffta_load_suspend','ffta_load_abilities_suspend'],
  [0xca904,'ffta_native_give_item','ffta_give_abilities_entry']]) {
  if(rom.readUInt32LE(offset)!==(symbols[previous]|1))throw Error('Conflicting ability lifecycle hook');
  rom.writeUInt32LE(symbols[name]|1,offset);changes.push({offset,name,size:4});
}
for(const [offset,end,name] of [
  [0xcafea,0xcaff6,'ffta_ap_remove_read'],[0xcb148,0xcb154,'ffta_ap_replace_read'],
  [0xcaec4,0xcaed0,'ffta_ap_candidate_read'],[0x49032,0x4903e,'ffta_ap_results'],
  [0xccf7e,0xccf8c,'ffta_ap_item_grant'],[0xcb036,0xcb044,'ffta_ap_remove_clear'],
  [0xcb192,0xcb1a0,'ffta_ap_replace_clear'],[0xcd072,0xcd07e,'ffta_ap_typed_available'],
  [0xcd19e,0xcd1aa,'ffta_ap_typed_known'],
  [0x7b9aa,0x7b9b6,'ffta_ap_party_filter'],[0x7b9cc,0x7b9d8,'ffta_ap_party_row'],
  [0x7c362,0x7c36e,'ffta_ap_menu_filter'],[0x7c49c,0x7c4a8,'ffta_ap_job_filter'],
  [0x7c5d6,0x7c5e6,'ffta_ap_reaction_row'],[0x7c694,0x7c6a4,'ffta_ap_support_row'],
  [0x7c770,0x7c780,'ffta_ap_combo_row'],[0xc8f76,0xc8f82,'ffta_ap_command_discovery'],
  [0x64f12,0x64f1e,'ffta_selection_allocate'],[0x7c4d8,0x7c4e4,'ffta_ap_preview_row'],
  [0x7c392,0x7c39c,'ffta_ap_primary_preview_row'],
  [0xc8b26,0xc8b32,'ffta_prerequisite_count'],
  [0x1291ac,0x1291b8,'ffta_ap_loss_filter'],[0x129224,0x129230,'ffta_ap_loss_read'],
  [0x129264,0x129270,'ffta_ap_loss_write'],[0x132e62,0x132e6e,'ffta_ap_theft_read'],
  [0x132fc6,0x132fd2,'ffta_ap_theft_grant'],[0x132ff8,0x13300e,'ffta_ap_theft_revoke'],
  [0x133d30,0x133d3c,'ffta_ap_theft_count']]) {
  if(!rom.subarray(offset,end).equals(clean.subarray(offset,end)))throw Error('Conflicting inline AP hook');
  if(!symbols[name])throw Error('Missing AP shim');
  for(let p=offset;p<end;p+=2)rom.writeUInt16LE(0x46c0,p);
  rom.writeUInt16LE(0xb408,offset);
  const jump=(offset+5)&~3;
  if(jump+8>end)throw Error('Inline AP stub too short');
  rom.writeUInt16LE(0x4b00,jump);rom.writeUInt16LE(0x4718,jump+2);
  rom.writeUInt32LE(symbols[name]|1,jump+4);
  changes.push({offset,name,size:end-offset,expected:clean.subarray(offset,end).toString('hex')});
}
for(const offset of [0x9e8b4,0x9f7e8,0x9f848,0x9f8dc]) {
  if(rom.readUInt32LE(offset)!==0xe1c)throw Error('Unexpected snapshot capacity');
  rom.writeUInt32LE(0x1014,offset);changes.push({offset,size:4,purpose:'Owned snapshot AP and status tails'});
}
for(const offset of [0x71118,0x711f8]) {
  if(rom.readUInt32LE(offset)!==0x7240)throw Error('Unexpected party allocation');
  rom.writeUInt32LE(0x7268,offset);changes.push({offset,size:4,purpose:'Owned party command preview AP and status tail'});
}
if(rom.readUInt16LE(0x96ef4)!==0x2084)throw Error('Unexpected manager parent capacity');
rom.writeUInt16LE(0x2090,0x96ef4);changes.push({offset:0x96ef4,size:2,purpose:'96 additional manager heap bytes'});
if(rom.readUInt32LE(0x36d4bc)!==0x03005ee9)throw Error('Unexpected native copy dispatch');
rom.writeUInt32LE(symbols.ffta_native_copy_entry|1,0x36d4bc);
changes.push({offset:0x36d4bc,size:4,purpose:'Owned whole-unit AP and preference copies'});
fs.writeFileSync(path.join(out,'ability-core.gba'),rom);
fs.writeFileSync(path.join(out,'ability-core.json'),JSON.stringify({status:'TEST ONLY: AP accessors, selected native consumers, owned copy lifetimes and job lists; remaining AP consumers, job UI and effects pending',baseSha1:sha1(input),romSha1:sha1(rom),engineSha1:sha1(engine),changes},null,2));
console.log('Built isolated ability-core native hook probe');
