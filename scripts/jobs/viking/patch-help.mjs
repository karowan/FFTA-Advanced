import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {ROMBuilder,encodeHelp} from '../../../src/rom-builder.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const [input,output,manifest]=process.argv.slice(2);
if(!input||!output||!manifest)throw Error('Expected input, output and manifest');
const read=n=>JSON.parse(fs.readFileSync(path.join(root,'build/expansion',n)));
const registry=read('registry.json'),content=read('probes/content-data.json'),parent=read('probes/samurai/current.json');
const descriptions={
 'VIK-A1':'Lightning magic to one target.',
 'VIK-A2':'Steals gil using normal theft rules. Depleted loot stays depleted.',
 'VIK-A3':'Steals an accessory, then strikes with an axe. Theft rolls separately.',
 'VIK-A4':'Cures Blind, Silence, Confuse. Resists hostile ailments for two turns.',
 'VIK-A5':'Lightning magic. Slows after dealing HP damage.',
 'VIK-A6':'Steals body armor, then strikes with an axe. Theft rolls separately.',
 'VIK-A7':'Strong lightning magic in a cross. Can strike allies.',
 'VIK-A8':'Water magic pushes targets. Nearby water adds MP loss.',
 'VIK-A9':'Challenges one foe. Weakens its damage to others for one turn.',
 'VIK-S1':'Prevents Immobilize and forced movement. Does not prevent Slow.',
 'VIK-S2':'Deals more direct HP damage to foes with harmful ailments.',
 'VIK-R1':'After surviving an attack, recovers part of HP damage. Recovery is capped.',
 'VIK-R2':'Gain gil after surviving a critical hit. Up to 50 gil each battle.',
 'VIK-C1':'Uses 3 JP to initiate a combo. An axe is required.',
};
const image=fs.readFileSync(input),pointer=0x36d6c4,ranges=content.addresses.helpBanks-0x08000000;
const previous=parent.help.address,first=parent.help.last+1,last=first+Object.keys(descriptions).length-1;
if(image.readUInt32LE(pointer)!==previous||image.readUInt16LE(ranges+84)!==first-1)throw Error('Unexpected parent help');
const builder=new ROMBuilder(image,{start:0x1270000,end:0x1280000});
const table=Buffer.alloc((last-0x1de+1)*4);
image.copy(table,0,previous-0x08000000,previous-0x08000000+(first-0x1de)*4);
const lessons=[];
for(const [index,[id,text]] of Object.entries(descriptions).entries()){
 const lesson=registry.lessons.find(l=>l.id===id),bytes=encodeHelp(text,27),helpId=first+index;
 if(!lesson||!id.startsWith('VIK-'))throw Error('Wrong lesson');
 if([...bytes].filter((b,n)=>b===0x40&&bytes[n+1]===0x6e).length>2)throw Error('Too many lines '+id);
 const address=builder.allocate(id+' help',bytes);table.writeUInt32LE(address,(helpId-0x1de)*4);
 for(const owner of lesson.owners){
  const race=content.races.find(r=>r.id===owner.race),offset=race.address-0x08000000+owner.abilityIndex*8+2;
  const expected=id==='VIK-C1'?0x6b2:0; // accepted Tempest Combo profile help
  if(builder.rom.readUInt16LE(offset)!==expected)throw Error('Unexpected prior help '+id);
  builder.rom.writeUInt16LE(helpId,offset);
 }
 lessons.push({id,text,helpId,address});
}
const address=builder.allocate('Viking help bank',table);
builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
fs.writeFileSync(output,builder.rom);fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,lessons,allocations:builder.allocations},null,2));
