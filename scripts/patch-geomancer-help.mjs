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
 'GEO-A1':'Earth damage in a cross. Nearby stone strengthens the pulse.',
 'GEO-A2':'Damage and attempt Immobilize. Nearby plants improve the binding.',
 'GEO-A3':'Water damage. Nearby water adds a push in the chosen direction.',
 'GEO-A4':'Float and Move up for allies. Lower allies also gain Jump. Lasts 2 turns.',
 'GEO-A5':'Protect allies. Nearby stone also prevents pushes for 2 turns.',
 'GEO-A6':'Fire damage exposes a foe to magic. Nearby heat strengthens exposure.',
 'GEO-A7':'Ice damage and a field that slows ground movement. One field per caster.',
 'GEO-A8':'Strong magic in a cross. Choose Wind or an element from nearby terrain.',
 'GEO-A9':'Place a field that shields grounded allies from enemy magic. Lasts 2 turns.',
 'GEO-S1':'Boost weakness damage. Refund a quarter of MP spent after a weakness hit.',
 'GEO-S2':'Raise Jump by 1. Ignore extra tile costs. Blocked ground stays blocked.',
 'GEO-R1':'Take less physical damage. Survive a hit to gain Protect.',
 'GEO-R2':'Survive a hit to counter with Wind magic within 4 tiles.'
};
const last=first+Object.keys(help).length-1,builder=new ROMBuilder(image,{start:0x12f0000,end:0x1300000});
// The native reaction preview has a fixed twelve-tile name allocation. Keep
// the full approved name in the design and use a bounded display label.
const reaction=registry.lessons.find(l=>l.id==='GEO-R2');
const others=image.readUInt32LE(0x2c08c);
if(others!==read('probes/command-data.json').addresses.others)throw Error('Unexpected live reaction-name table');
const compact='Nature Wrath',namePointer=others-0x08000000+reaction.nameId*4;
const previousName=image.readUInt32LE(namePointer),compactAddress=builder.allocate('Nature Wrath compact display name',encodeText(compact));
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
const address=builder.allocate('Geomancer support and reaction help bank',table);builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
fs.writeFileSync(output,builder.rom);fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,lessons,displayNames:[{id:'GEO-R2',full:reaction.name,compact,previousName,address:compactAddress}],allocations:builder.allocations},null,2));
