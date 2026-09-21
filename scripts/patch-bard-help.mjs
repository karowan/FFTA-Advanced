import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {ROMBuilder,encodeHelp} from '../src/rom-builder.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [input,output,manifest]=process.argv.slice(2);
if(!input||!output||!manifest)throw Error('Expected input, output and manifest');
const read=n=>JSON.parse(fs.readFileSync(path.join(root,'build/expansion',n)));
const registry=read('registry.json'),content=read('probes/content-data.json');
const image=fs.readFileSync(input),pointer=0x36d6c4,ranges=content.addresses.helpBanks-0x08000000;
const previous=image.readUInt32LE(pointer),first=image.readUInt16LE(ranges+84)+1;
const help={
 'BRD-A1':'Heal an ally and cure Poison, Blind, Silence and Confuse.',
 'BRD-A2':'Grant Protect and boost physical damage for two turns.',
 'BRD-A3':'Grant Shell and boost magic damage for two turns. No healing bonus.',
 'BRD-A4':'Holy song damages undead foes in a cross.',
 'BRD-A5':'Heal nearby allies and grant Regen.',
 'BRD-A6':'Become Invisible. Works while Silenced. No weapon needed.',
 'BRD-A7':'Restore up to 20 MP to another ally. Cannot target self.',
 'BRD-A8':'Grant Protect, Shell and Regen to nearby allies.',
 'BRD-S1':'A new buff on another ally also restores a little HP. Refreshes do not heal.',
 'BRD-S2':'Immune to Silence. Spells and songs cost one quarter less MP.',
 'BRD-R1':'Survive a hit to boost the next spell or song. Lasts through next turn.',
 'BRD-R2':'Survive a physical hit to gain Haste for two turns. Silence prevents this.'
};
const last=first+Object.keys(help).length-1,builder=new ROMBuilder(image,{start:0x12c0000,end:0x12d0000});
const table=Buffer.alloc((last-0x1de+1)*4);image.copy(table,0,previous-0x08000000,previous-0x08000000+(first-0x1de)*4);
const lessons=[];
for(const [index,[id,text]] of Object.entries(help).entries()){
 const lesson=registry.lessons.find(l=>l.id===id),bytes=encodeHelp(text,27),helpId=first+index;
 if(!lesson||!['Action','Support','Reaction'].includes(lesson.type))throw Error('Unexpected lesson '+id);
 if([...bytes].filter((b,n)=>b===0x40&&bytes[n+1]===0x6e).length>2)throw Error('Too many help lines '+id);
 const address=builder.allocate(id+' help',bytes);table.writeUInt32LE(address,(helpId-0x1de)*4);
 for(const owner of lesson.owners){
  const race=content.races.find(r=>r.id===owner.race),offset=race.address-0x08000000+owner.abilityIndex*8+2;
  if(builder.rom.readUInt16LE(offset)!==0)throw Error('Existing help '+id);
  builder.rom.writeUInt16LE(helpId,offset);
 }
 lessons.push({id,text,helpId,address});
}
const address=builder.allocate('Bard help bank',table);builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
fs.writeFileSync(output,builder.rom);fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,lessons,allocations:builder.allocations},null,2));
