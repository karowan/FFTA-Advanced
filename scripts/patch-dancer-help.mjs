import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {ROMBuilder,encodeHelp,encodeText} from '../src/rom-builder.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [input,output,manifest]=process.argv.slice(2);
if(!input||!output||!manifest)throw Error('Expected input, output and manifest');
const read=n=>JSON.parse(fs.readFileSync(path.join(root,'build/expansion',n)));
const registry=read('registry.json'),content=read('probes/content-data.json');
const image=fs.readFileSync(input),pointer=0x36d6c4,ranges=content.addresses.helpBanks-0x08000000;
const previous=image.readUInt32LE(pointer),first=image.readUInt16LE(ranges+84)+1;
const help={
 'DNC-A1':'A damaging dance hits foes in a cross. Power grows with level.',
 'DNC-A2':'Drain 8 to 24 MP from foes in a cross. Does not restore your MP.',
 'DNC-A3':'Attempt Slow on foes in a cross. Works while Silenced.',
 'DNC-A4':'Damage a foe and weaken physical damage for two turns.',
 'DNC-A5':'Damage a foe and weaken magical damage for two turns.',
 'DNC-A6':'Choose Blind, Silence, Poison or Confuse. Attempt it on foes in a cross.',
 'DNC-A7':'Dance to drain half the HP lost, up to a quarter of your max HP.',
 'DNC-A8':'One strong strike with your primary knife or rapier. No weapon proc.',
 'DNC-A9':'Strike, then step up to 2 unused Move. Pick a blue tile first. B skips.',
 'DNC-R1':'Survive a hit to strengthen the next physical action. Lasts through next turn.',
 'DNC-R2':'Counter Rhythm: after physical HP loss, attempt Slow within 3 tiles.'
};
const last=first+Object.keys(help).length-1,builder=new ROMBuilder(image,{start:0x12e0000,end:0x12f0000});
// The original reaction preview reserves twelve name tiles. The full title
// measures thirteen and overwrites the following heap header. Keep the
// approved title in the registry/help and use a compact native display label.
const reaction=registry.lessons.find(l=>l.id==='DNC-R2');
const others=image.readUInt32LE(0x2c08c);
if(others!==read('probes/command-data.json').addresses.others)throw Error('Unexpected live reaction-name table');
const compact='Counter Rhy.',namePointer=others-0x08000000+reaction.nameId*4;
const previousName=image.readUInt32LE(namePointer),compactAddress=builder.allocate('Counter Rhythm compact display name',encodeText(compact));
builder.rom.writeUInt32LE(compactAddress,namePointer);
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
const address=builder.allocate('Dancer help bank',table);builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
fs.writeFileSync(output,builder.rom);fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,lessons,displayNames:[{id:'DNC-R2',full:reaction.name,compact,previousName,address:compactAddress}],allocations:builder.allocations},null,2));
