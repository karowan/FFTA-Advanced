import fs from 'node:fs';
import assert from 'node:assert/strict';
import {root,cleanROM,sha1,missions} from '../src/rom-data.mjs';
const original=cleanROM(),rom=fs.readFileSync(`${root}/build/foundation/FFTA_vanillaplus_dev.gba`);
const manifest=JSON.parse(fs.readFileSync(`${root}/build/foundation/manifest.json`));
assert.equal(rom.length,0x2000000);assert.equal(sha1(rom),manifest.outputSha1);
// Review boundary: fail if an engine include changes any unapproved original byte.
const allowed=[
  [0x5d23c,12,'pub dispatch'],[0x72634,8,'sort drawing'],[0x736b2,10,'sort tiles'],
  [0x739b4,12,'sort erase'],[0x73bae,10,'sort R'],[0x73c3e,10,'sort input'],[0x7472c,8,'sort drawing'],
  [0x975f2,10,'morph size'],[0x9764c,2,'morph standing'],[0xc817c,8,'morph generic'],[0xc92f0,8,'unit visual getter'],
  [0x4c5170,8,'pub help'],[0x5567f0+0x29*4,16,'pub labels'],
  [0x55ae4c+69*70+0x24,2,'Wyrmstone'],[0x55ae4c+183*70+0x24,2,'Cup'],[0x55ae4c+111*70+0x35,1,'recruit'],
  [0x53bbd1,1,'Goblin species'],[0x53bbe4,22,'Goblin abilities'],
  [0x53bde1,1,'Thundrake species'],[0x53bdf4,22,'Thundrake abilities']
];
let changed=0;
for(let i=0;i<original.length;i++)if(original[i]!==rom[i]){
  assert(allowed.some(([p,n])=>i>=p&&i<p+n),`Unapproved original byte changed at ${i.toString(16)}`);changed++;
}
for(const [p,n,label] of [[0x521a14,0x48*0x34,'job definitions'],[0x51d1a0,375*32,'vanilla equipment'],[0x51ba84,0x16d0,'racial abilities']])
  assert.deepEqual(rom.subarray(p,p+n),original.subarray(p,p+n),`${label} changed`);
assert.deepEqual(fs.readFileSync(`${root}/roms/play/vanilla/FFTA_US_vanilla.gba`),original,'Vanilla playing ROM changed');
const ms=missions(rom),base=missions(original);
assert.equal(ms[111].recruit,base[66].recruit);assert.equal(ms[111].repeatable,true);
for(const i of [69,111,183]){assert.equal(ms[i].flags,base[i].flags);assert.deepEqual(ms[i].required,base[i].required);}
assert.equal(ms[69].rewards[0],base[69].rewards[0]);assert.equal(ms[183].rewards[0],base[183].rewards[0]);
for(const [formation,p,count] of [[0x54ee60,0x53bb40,5],[0x54ef00,0x53bd80,5]]){
  assert.equal(rom[formation+0x14],count);assert.equal(rom.readUInt32LE(formation+0x18)&0x1ffffff,p);
}
for(const [offset,job,mask] of [[0x53bbd0,0x2c,1],[0x53bde0,0x35,0x0f00]]){
  assert.equal(rom[offset+1],job);assert.equal(rom.readUInt16LE(offset+0x14),mask);
  for(let i=0;i<48;i++)if(i!==1&&(i<0x14||i>=0x2a))assert.equal(rom[offset+i],original[offset+i]);
}
const report={passed:true,romSha1:sha1(rom),changedOriginalBytes:changed,allowedRanges:allowed,scope:'All original-byte changes confined to reviewed hooks and five data cases; vanilla jobs, equipment, ability tables, requirements, encounter sizes and unaffected unit fields preserved.'};
fs.writeFileSync(`${root}/build/reports/foundation-verification.json`,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:true,romSha1:report.romSha1,changedOriginalBytes:changed}));
