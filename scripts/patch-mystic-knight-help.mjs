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
 'MYK-A1':'Self: enchant. Foe: strike and enchant. Fire on primary Fight. Icon FI.',
 'MYK-A2':'Self: enchant. Foe: strike and enchant. Ice on primary Fight. Icon IC.',
 'MYK-A3':'Self: enchant. Foe: strike and enchant. Thunder on primary Fight. Icon TH.',
 'MYK-A4':'Enchant self or strike a foe. Damaging primary hits try Poison. Icon PO.',
 'MYK-A5':'Enchant self or strike a foe. Damaging primary hits try Sleep. Icon SL.',
 'MYK-A6':'Enchant self or strike a foe. Damaging primary hits try Silence. Icon SI.',
 'MYK-A7':'Enchant self or strike a foe. Capped HP drain on primary hits. Icon DR.',
 'MYK-A8':'Enchant self or strike a foe. Primary hits pierce some WDef. Icon FL.',
 'MYK-A9':'Enchant self or strike a foe. Damaging primary hits try Slow. Icon SW.',
 'MYK-A10':'Enchant self or strike a foe. Capped MP siphon on primary hits. Icon OS.',
 'MYK-A11':'Self: enchant. Foe: strike and enchant. Holy on primary Fight. Icon HO.',
 'MYK-A12':'On a hit, remove one random buff from the target. Keeps enchantment.',
 'MYK-A13':'Spend Fire, Ice, Thunder, Holy or Flare enchantment for a magical cross.',
 'MYK-A14':'Attempt Petrify. No HP damage or enchantment change.',
 'MYK-S1':'Alternate physical and magic actions for stronger hits. M or P: next.',
 'MYK-S2':'Take less magic HP damage while MP is at least half full and nonzero.',
 'MYK-R1':'Before magic HP damage would leave half HP or less, gain ordinary Shell.',
 'MYK-R2':'Rapier or saber: an enemy physical hit spends your enchantment to halve it.',
 'MYK-C1':'Use JP for a rapier or saber combo. Enchantments add no extra effects.'
};
const last=first+Object.keys(help).length-1,builder=new ROMBuilder(image,{start:0x1330000,end:0x1340000});
const table=Buffer.alloc((last-0x1de+1)*4);image.copy(table,0,previous-0x08000000,previous-0x08000000+(first-0x1de)*4);
const lessons=[];
for(const [index,[id,text]] of Object.entries(help).entries()){
 const lesson=registry.lessons.find(l=>l.id===id),bytes=encodeHelp(text,27),helpId=first+index;
 if(!lesson)throw Error('Unexpected lesson '+id);
 if([...bytes].filter((b,n)=>b===0x40&&bytes[n+1]===0x6e).length>2)throw Error('Too many help lines '+id);
 const address=builder.allocate(id+' help',bytes);table.writeUInt32LE(address,(helpId-0x1de)*4);
 for(const owner of lesson.owners){
  const race=content.races.find(r=>r.id===owner.race),offset=race.address-0x08000000+owner.abilityIndex*8+2;
  // patch-lesson-help installs this Combo's original common description.
  // Preserve that text entry and replace only our lesson's pointer.
  const expected=id==='MYK-C1'?0x6b7:0;
  if(builder.rom.readUInt16LE(offset)!==expected)throw Error('Unexpected prior help '+id);
  builder.rom.writeUInt16LE(helpId,offset);
 }
 lessons.push({id,text,helpId,address});
}
const address=builder.allocate('Mystic Knight help bank',table);builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
fs.writeFileSync(output,builder.rom);fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,lessons,allocations:builder.allocations},null,2));
