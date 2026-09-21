import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
import {patchEvaluatedUnits} from './patch-evaluated-units.mjs';
import {patchQuinHistory} from './patch-quin-history.mjs';
import {patchGraceSupport} from './patch-grace-support.mjs';
import {patchRecruitPrerequisites} from './patch-recruit-prerequisites.mjs';
import {patchMobilitySupports} from './patch-mobility-supports.mjs';
import {patchLessonHelp} from './patch-lesson-help.mjs';
import {patchExposedEffects} from './patch-exposed-effects.mjs';
import {patchStatusDisplay} from './patch-status-display.mjs';
const out=path.join(root,'build/expansion/probes');
const input=fs.readFileSync(path.join(out,'combo.gba'));
const prior=JSON.parse(fs.readFileSync(path.join(out,'combo.json')));
const action=JSON.parse(fs.readFileSync(path.join(out,'action-data.json')));
const engine=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(sha1(input)!==prior.romSha1 || sha1(engine)!==prior.engineSha1 ||
 !input.subarray(0x1100000,0x1100000+engine.length).equals(engine))throw Error('Stale combo/engine');
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
const clean=cleanROM(),rom=Buffer.from(input),changes=[];
changes.push(...patchEvaluatedUnits(rom,symbols));
changes.push(...patchMobilitySupports(rom,symbols));
changes.push(...patchGraceSupport(rom,symbols));
changes.push(...patchRecruitPrerequisites(rom,symbols));
changes.push(...patchQuinHistory(rom,symbols));
for(const patch of [b=>patchExposedEffects(b,symbols,{application:true,incoming:true}),b=>patchStatusDisplay(b,symbols)]) {
 const before=Buffer.from(rom);
 for(const change of patch(rom))changes.push({...change,size:change.bytes,
  expected:before.subarray(change.offset,change.offset+change.bytes).toString('hex')});
}
for(const [offset,end,name] of [
 [0x1300e2,0x1300f2,'ffta_physical_final_entry'],
 [0xa0014,0xa0020,'ffta_combat_geometry_entry'],
 [0xb4a1c,0xb4a28,'ffta_area_list_entry'],
 [0xb6fb6,0xb6fc0,'ffta_arc_confirm_entry'],
 [0xa3aba,0xa3ac4,'ffta_arc_commit_entry'],
 [0x93a66,0x93a70,'ffta_arc_ai_entry'],
 [0x96a40,0x96a4c,'ffta_arc_launch_entry'],
 [0x12f8a4,0x12f8b0,'ffta_dark_sword_element_entry'],
 [0xa315a,0xa3166,'ffta_dark_sword_apply_entry'],
 [0x13467a,0x134686,'ffta_dark_sword_law_weapon_entry'],
 [0x130654,0x130660,'ffta_weapon_drain_entry'],
 [0x130688,0x130694,'ffta_weapon_effect_entry'],
 [0xa3072,0xa307c,'ffta_physical_success_entry']
 ,[0x131378,0x131384,'ffta_executioner_chance_entry']
 ,[0xa3004,0xa3010,'ffta_executioner_roll_entry']
 ,[0xb5816,0xb5820,'ffta_executioner_preview_entry']
]) {
 if(!rom.subarray(offset,end).equals(clean.subarray(offset,end)))throw Error('Combat hook conflict');
 if(!symbols[name])throw Error('Missing combat hook');
 for(let p=offset;p<end;p+=2)rom.writeUInt16LE(0x46c0,p);
 rom.writeUInt16LE(0xb408,offset);const jump=(offset+5)&~3;
 if(jump+8>end)throw Error('Combat hook length');
 rom.writeUInt16LE(0x4b00,jump);rom.writeUInt16LE(0x4718,jump+2);rom.writeUInt32LE(symbols[name]|1,jump+4);
 changes.push({offset,name,size:end-offset,expected:clean.subarray(offset,end).toString('hex')});
}
for(const [offset,name] of [[0x12fea8,'ffta_physical_defense_entry'],[0x13434c,'ffta_physical_law_entry']]){
 if(!rom.subarray(offset,offset+8).equals(clean.subarray(offset,offset+8)) || !symbols[name])throw Error('Rider hook conflict');
 rom.writeUInt16LE(0x4800,offset);rom.writeUInt16LE(0x4700,offset+2);rom.writeUInt32LE(symbols[name]|1,offset+4);
 changes.push({offset,name,size:8,expected:clean.subarray(offset,offset+8).toString('hex')});
}
for(const [offset,original,name] of [
 [0x3a8604+8*4,0x08130a95,'ffta_physical_eligibility_entry'],
 [0x3a86f8+30*4,0x0813189d,'ffta_physical_magnitude_entry']
]) {
 if(rom.readUInt32LE(offset)!==original || !symbols[name])throw Error('Combat descriptor conflict');
 rom.writeUInt32LE(symbols[name]|1,offset);changes.push({offset,name,size:4,original,address:symbols[name]|1});
}
const registry=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/registry.json')));
const enabled=[];
for(const [id,expectedId,expectedName,donor,mp] of [
 ['DRK-A2',357,782,147,6],['DRK-A3',358,783,147,4],
 ['SLD-AX-A1',424,884,112,0],['SLD-AX-A2',425,885,147,4],
 ['SLD-AX-A3',426,886,103,4],['SLD-AX-A4',427,887,112,6],
 ['GLD-AX-A1',428,890,112,8],['GLD-AX-A2',429,891,103,8],
 ['GLD-AX-A3',430,892,112,10],['GLD-AX-A4',431,893,112,16]
]){
const lesson=registry.lessons.find(l=>l.id===id);
if(lesson.globalAbilityId!==expectedId || lesson.nameId!==expectedName)throw Error('Physical registry changed');
const offset=action.addresses.actions-0x08000000+lesson.globalAbilityId*28;
if(!input.subarray(offset,offset+28).equals(Buffer.alloc(28)))throw Error('Physical action is not inert');
const record=Buffer.from(clean.subarray(0x55187c+donor*28,0x55187c+(donor+1)*28));
record.writeUInt16LE(lesson.nameId,0);record[12]=0x3f;record[13]=record[14]=record[15]=1;
record[4]=mp;
if(id==='GLD-AX-A4')record[7]=2;
if(id==='DRK-A2' || id==='DRK-A3'){
 record[2]=0;record[5]=1;record[6]=2;record[7]=3;
}
if(id==='SLD-AX-A3' || id==='GLD-AX-A2'){
 // Earth Render retains native directional UI and AI dispatch. The custom
 // list replaces its full ray with three independently filtered front cells.
 record[2]=0;record[5]=1;record[7]=2;record[9]=0;record.writeUInt16LE(110,20);
}
if(id==='SLD-AX-A2'){
 record[7]=3;
 // Native Throw's visual-only callback reads the selected primary axe.
 // Keep Nighthawk's physical descriptors; no throwing-item transaction.
 record.writeUInt16LE(0x91,20);
}
// +22 is an independent preview-message ID. Rush's A5 says Knock back even
// after its knockback descriptor is removed; Chop has no secondary effect.
record.writeUInt16LE(0,22);
record.copy(rom,offset);changes.push({offset,name:`${lesson.name} action${lesson.globalAbilityId}`,size:28,original:input.subarray(offset,offset+28).toString('hex'),value:record.toString('hex')});
enabled.push(lesson.globalAbilityId);
}
const supports=[140,141];
const help=patchLessonHelp(rom,registry,JSON.parse(fs.readFileSync(path.join(out,'content-data.json'))),enabled,supports);
changes.push(...help.changes);
fs.writeFileSync(path.join(out,'combat-input.gba'),input);
fs.writeFileSync(path.join(out,'combat.gba'),rom);
fs.writeFileSync(path.join(out,'combat.json'),JSON.stringify({status:'TEST ONLY: eight axe techniques, two Dark Knight sword arts, Exposed and status icons, Grace, Light Foot and eight combo profiles; complete expansion not implemented; current-build acceptance tracked by test reports',
 baseSha1:prior.romSha1,romSha1:sha1(rom),engineSha1:sha1(engine),actions:enabled,supports,help,changes},null,2));
console.log('Built ten physical techniques, Exposed, status icons, Grace and Light Foot');
