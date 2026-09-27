/** Append native help without replacing an old help ID or resizing lettering.
 * This stage remains a private integration candidate until combined acceptance.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {ROMBuilder,encodeHelp} from '../src/rom-builder.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p)));
const parent=read('build/expansion/chemist-progressions/actions/current.json').manifest;
const meta=read(parent),image=fs.readFileSync(meta.path);
const sha=b=>crypto.createHash('sha1').update(b).digest('hex');
if(sha(image)!==meta.romSha1)throw Error('Action parent hash mismatch');
const design=read('notes/chemist-progression-abilities.json');
const equipment=read('notes/chemist-progression-equipment.json');
const content=read('build/expansion/probes/content-data.json');
const help=[
 'Heal 1/5 max HP plus 1/4 missing HP. Living allies only.',
 'Next enemy hit: heal 1/4 HP and cure a new ailment. Two turns.',
 'Cure harmful ailments and prevent new ones for two turns.',
 'Heal 1/4 max HP and grant Regen to a living ally.',
 'Revive fallen allies in a cross with 35 percent HP.',
 'Heal living allies in a cross for 1/4 max HP.',
 'Next enemy hit deals 40 percent less HP damage. Two turns.',
 'Curing another ally heals 1/4 max HP. Once per action.',
 'Hit below half HP: heal 1/5 HP and cure an ailment. Once per turn.',
 'Join a combo with a staff or mace. Costs one JP.',
 'Fire damage. Choose Protect or Shell to ignore and remove on a hit.',
 'Lightning damage in a cross. Hits may cause Blind.',
 'Damage and push an enemy one tile if the destination is clear.',
 'Place a trap. Enemy entry triggers lightning and Slow. Two turns.',
 'Allies in a cross take 1/4 less ranged HP damage for two turns.',
 'Move another willing ally up to two tiles. Grants no extra Move or turn.',
 'Fire hit plants a fuse. Next turn end: blast. Move or cure to stop it.',
 'Ranged single attacks gain accuracy and damage near another ally.',
 'Enemy area attacks deal 40 percent less HP damage.',
 'Join a combo with a knife or mace. Costs one JP.'
];
const ranges=content.addresses.helpBanks-0x08000000,site=0x36d6c4;
const previous=image.readUInt32LE(site),first=image.readUInt16LE(ranges+84)+1;
const last=first+30-1,base=0x1de;
const table=Buffer.alloc((last-base+1)*4);
image.copy(table,0,previous-0x08000000,previous-0x08000000+(first-base)*4);
const builder=new ROMBuilder(image,{start:0x1a90000,end:0x1aa0000});
const patches=[],entries=[];
function writeHalf(offset,value,label){
 const before=builder.rom.readUInt16LE(offset);builder.rom.writeUInt16LE(value,offset);
 patches.push({offset,before,after:value,label});
}
function add(text,label,offset){
 const bytes=encodeHelp(text,27);
 if([...bytes].filter((b,i)=>b===0x40&&bytes[i+1]===0x6e).length>2)throw Error('Help exceeds three lines: '+label);
 const id=first+entries.length,address=builder.allocate(label,bytes);
 table.writeUInt32LE(address,(id-base)*4);writeHalf(offset,id,label);
 entries.push({id,label,text,address,bytes:bytes.length});
}
const races=image.readUInt32LE(0x257e8)-0x08000000;
let h=0;
for(const job of design.jobs){
 const bank=image.readUInt32LE(races+job.race*4)-0x08000000;
 const firstLesson=job.race===3?124:116;
 for(const [i,lesson] of job.lessons.entries()){
  const offset=bank+(firstLesson+i)*8;
  if(image.readUInt16LE(offset+4)!==lesson[3])throw Error('Lesson mismatch '+lesson[0]);
  add(help[h++],lesson[0],offset+2);
 }
}
const items=image.readUInt32LE(0x79aec)-0x08000000;
for(const item of equipment.items){
 const job=design.jobs.find(j=>j.id===item.job);
 const names=item.lessons.map(n=>job.lessons[n][1]);
 add('Teaches '+names.join(' and ')+'.',item.name,items+item.id*32+2);
}
const address=builder.allocate('Expanded help bank',table);
builder.rom.writeUInt32LE(address,site);writeHalf(ranges+84,last,'last help ID');
if(!builder.rom.subarray(address-0x08000000,address-0x08000000+(first-base)*4).equals(
 image.subarray(previous-0x08000000,previous-0x08000000+(first-base)*4)))throw Error('Old help pointer changed');
const romSha1=sha(builder.rom),out=path.join(root,'build/expansion/chemist-progressions/help',romSha1);
fs.mkdirSync(out,{recursive:true});const output=path.join(out,'INCOMPLETE_TEST_ONLY.gba');fs.writeFileSync(output,builder.rom);
const manifest=path.join(out,'manifest.json');
fs.writeFileSync(manifest,JSON.stringify({...meta,parent,path:output,romSha1,help:{first,last,address,previous,entries,patches,allocations:builder.allocations}},null,2)+'\n');
fs.writeFileSync(path.join(out,'../current.json'),JSON.stringify({manifest})+'\n');
console.log(JSON.stringify({romSha1,entries:entries.length,manifest}));
