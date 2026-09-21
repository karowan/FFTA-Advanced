import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {ROMBuilder,encodeHelp} from '../../../src/rom-builder.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const [input,output,manifest]=process.argv.slice(2);
const read=name=>JSON.parse(fs.readFileSync(path.join(root,'build/expansion',name)));
const registry=read('registry.json'),content=read('probes/content-data.json');
const image=fs.readFileSync(input),pointer=0x36d6c4,ranges=content.addresses.helpBanks-0x08000000;
const previous=image.readUInt32LE(pointer),first=image.readUInt16LE(ranges+84)+1;
const help={
 'DRK-A1':'Pay one tenth of max HP for a dark sword strike. Must leave 1 HP.',
 'DRK-A6':'Sword strike. May Stop the foe after dealing HP damage.',
 'DRK-A7':'Pay 15 percent max HP. Line 3 hits allies. Stronger up close.',
 'DRK-A8':'Pay a fifth of max HP for a dark cross. May Slow after HP damage.',
 'DRK-A4':'Restore one fifth of max HP, up to 100, and gain Shell. No weapon needed.',
 'DRK-A5':'Strike or target self. Raise physical damage dealt and taken for two turns.',
 'DRK-A9':'Pay a tenth of max HP. Halve the next enemy action against an ally.',
 'DRK-S1':'Deal more physical and magic HP damage at or below 35 percent HP.',
 'DRK-S2':'Pay 2 HP per MP instead. Add other HP costs and always leave 1 HP.',
 'DRK-R1':'Reduce incoming magic HP damage. Gain Shell after surviving the action.',
 'DRK-R2':'After survival, return capped Dark damage based on HP lost. Range 3.'};
const last=first+Object.keys(help).length-1;
const builder=new ROMBuilder(image,{start:0x1230000,end:0x1240000});
const table=Buffer.alloc((last-0x1de+1)*4);
image.copy(table,0,previous-0x08000000,previous-0x08000000+(first-0x1de)*4);
const lessons=[];
for(const [index,[id,text]] of Object.entries(help).entries()) {
 const lesson=registry.lessons.find(l=>l.id===id),bytes=encodeHelp(text,27),helpId=first+index;
 if(!lesson||!['Action','Support','Reaction'].includes(lesson.type))throw Error('Unexpected Dark Knight lesson '+id);
 if([...bytes].filter((b,n)=>b===0x40&&bytes[n+1]===0x6e).length>2)throw Error('Help exceeds three lines');
 const address=builder.allocate(id+' description',bytes);table.writeUInt32LE(address,(helpId-0x1de)*4);
 for(const owner of lesson.owners) {
  const race=content.races.find(r=>r.id===owner.race),offset=race.address-0x08000000+owner.abilityIndex*8+2;
  if(builder.rom.readUInt16LE(offset)!==0)throw Error('Existing help '+id);
  builder.rom.writeUInt16LE(helpId,offset);
 }
 lessons.push({id,text,helpId,address});
}
const address=builder.allocate('Dark Knight help bank',table);
builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
fs.writeFileSync(output,builder.rom);
fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,lessons,allocations:builder.allocations},null,2));
