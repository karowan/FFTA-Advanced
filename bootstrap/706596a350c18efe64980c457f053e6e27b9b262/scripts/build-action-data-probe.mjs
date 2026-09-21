import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
import {ROMBuilder} from '../src/rom-builder.mjs';

// Data-only stage. No new action behavior, reaction masks or support hooks.
const out=path.join(root,'build/expansion/probes');
const stages=['command-core','command-data','ability-core','content-inventory','content-data'];
const sources=stages.map(name=>{
  const manifest=JSON.parse(fs.readFileSync(path.join(out,name+'.json')));
  const rom=fs.readFileSync(path.join(out,name+'.gba'));
  if(sha1(rom)!==manifest.romSha1)throw Error(`Stale ${name} manifest`);
  return {name,manifest,rom};
});
for(let i=0;i<sources.length-1;i++)
  if(sources[i].manifest.baseSha1!==sources[i+1].manifest.romSha1)
    throw Error(`Broken probe ancestry: ${sources[i].name}`);
const clean=cleanROM(),base=sources[0].rom;
const content=sources.at(-1).manifest;
if(!Array.isArray(content.allocations)||!content.allocations.length)throw Error('Missing content allocations');
const inheritedAllocations=sources.flatMap(s=>s.manifest.allocations??[]);
for(const allocation of inheritedAllocations){
  if(!Number.isInteger(allocation.offset)||!Number.isInteger(allocation.bytes)||allocation.bytes<=0||
      allocation.offset<0x1020000||allocation.offset+allocation.bytes>0x1100000)
    throw Error('Invalid content allocation bounds');
  if(sha1(base.subarray(allocation.offset,allocation.offset+allocation.bytes))!==allocation.sha1)
    throw Error(`Content allocation changed: ${allocation.name}`);
}
const start=Math.max(...inheritedAllocations.map(a=>a.offset+a.bytes));
const builder=new ROMBuilder(base,{start});
const originalBase=0x55187c,originalCount=347,recordBytes=28,totalCount=432;
// Native row346 is Blank Card, immediately before the descriptor table.
// Verify the allocator agrees instead of silently accepting a stale registry.
const registry=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/registry.json')));
const addedActions=registry.lessons.filter(l=>l.type==='Action').map(l=>l.globalAbilityId).sort((a,b)=>a-b);
if(originalBase+originalCount*recordBytes!==0x553e70 ||
 addedActions.length!==85 || addedActions.some((id,i)=>id!==originalCount+i) ||
 registry.actionDomain?.nativeCount!==originalCount || registry.actionDomain?.totalCount!==totalCount)
 throw Error('Action registry does not preserve the complete native domain');
const users=[0x23320,0x236ac,0x25998,0x26c9c,0x26d3c,0x26e18,0x27048,0x27170,0x279a0,
  0x27a94,0xa784c,0xb5d18,0xc3080,0xc3474,0xccd84,0x133e70,0x13416c];
if(!base.subarray(originalBase,originalBase+originalCount*recordBytes).equals(
    clean.subarray(originalBase,originalBase+originalCount*recordBytes)))throw Error('Original action records changed');
for(const offset of users)
  if(clean.readUInt32LE(offset)!==0x0855187c||base.readUInt32LE(offset)!==0x0855187c)
    throw Error(`Conflicting action table reference at ${offset.toString(16)}`);
// All-zero new records refer only to native no-op descriptor0. They deliberately
// have no names, flags, costs, geometry, animation or application behavior yet.
if(!clean.subarray(0x553e70,0x553e74).equals(Buffer.alloc(4)))throw Error('Native no-op descriptor changed');
const records=Buffer.alloc(totalCount*recordBytes);
clean.copy(records,0,originalBase,originalBase+originalCount*recordBytes);
const address=builder.allocate('expanded global action records (85 inert rows)',records);
const actual=builder.repoint(0x0855187c,address,17);
if(JSON.stringify(actual)!==JSON.stringify(users))throw Error('Action pointer locations changed');
// Freeze the exact composed input used by the native differential test. Upstream
// work can rebuild command-core without invalidating this stage's evidence.
fs.writeFileSync(path.join(out,'action-data-input.gba'),base);
const manifest={status:'TEST ONLY: 347 preserved action records including Blank Card plus 85 zero/inert rows; custom effects and new support/reaction dispatch are NOT enabled',
  baseSha1:sha1(base),romSha1:sha1(builder.rom),engineSha1:sources[0].manifest.engineSha1,
  ancestry:sources.map(({name,manifest})=>({name,romSha1:manifest.romSha1,baseSha1:manifest.baseSha1})),
  originalBase,originalCount,totalCount,recordBytes,addresses:{actions:address},
  allocations:builder.allocations,inheritedHighWater:start,changes:builder.changes};
fs.writeFileSync(path.join(out,'action-data.gba'),builder.rom);
fs.writeFileSync(path.join(out,'action-data.json'),JSON.stringify(manifest,null,2));
console.log(`Built inert action-data probe: ${totalCount} records at 0x${address.toString(16)}`);
