import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {ROMBuilder,encodeHelp} from '../src/rom-builder.mjs';
import {samuraiHelp} from '../src/samurai-help.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [input,output,manifest]=process.argv.slice(2);
if(!input||!output||!manifest)throw Error('Expected input ROM, output ROM, help manifest');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,'build/expansion',name)));
const registry=read('registry.json'),content=read('probes/content-data.json'),main=read('probes/combat.json');
const image=fs.readFileSync(input),pointer=0x36d6c4,ranges=content.addresses.helpBanks-0x08000000;
const previous=main.help.address,first=main.help.last+1,last=first+Object.keys(samuraiHelp).length-1;
if(image.readUInt32LE(pointer)!==previous||image.readUInt16LE(ranges+84)!==first-1)
 throw Error('Unexpected existing lesson help bank');
const builder=new ROMBuilder(image,{start:0x11c9000,end:0x11cb000});
const table=Buffer.alloc((last-0x1de+1)*4);
image.copy(table,0,previous-0x08000000,previous-0x08000000+(first-0x1de)*4);
const lessons=[];
for(const [index,[id,text]] of Object.entries(samuraiHelp).entries()) {
 const lesson=registry.lessons.find(l=>l.id===id),bytes=encodeHelp(text,27),helpId=first+index;
 if(!lesson||!((lesson.type==='Action'&&lesson.globalAbilityId>=347&&lesson.globalAbilityId<=355)||
    (id==='SAM-S2'&&lesson.type==='Support'&&lesson.globalAbilityId===129)||
    ((id==='SAM-R1'||id==='SAM-R2')&&lesson.type==='Reaction'&&lesson.globalAbilityId===(id==='SAM-R1'?128:129))||
    (id==='SLD-AX-S1'&&lesson.type==='Support'&&lesson.globalAbilityId===144)||
    (id==='SLD-AX-R1'&&lesson.type==='Reaction'&&lesson.globalAbilityId===144)))
  throw Error('Unexpected Samurai lesson '+id);
 if([...bytes].filter((b,n)=>b===0x40&&bytes[n+1]===0x6e).length>2)throw Error('More than three lines: '+id);
 const address=builder.allocate(id+' description',bytes);
 table.writeUInt32LE(address,(helpId-0x1de)*4);
 for(const owner of lesson.owners) {
  const race=content.races.find(r=>r.id===owner.race),offset=race.address-0x08000000+owner.abilityIndex*8+2;
  if(builder.rom.readUInt16LE(offset)!==0)throw Error('Existing Samurai help '+id);
  builder.rom.writeUInt16LE(helpId,offset);
  builder.changes.push({offset,size:2,name:id+' help ID',original:0,value:helpId});
 }
 lessons.push({id,text,helpId,address});
}
const address=builder.allocate('Samurai lesson help bank',table);
builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
builder.changes.push({offset:pointer,size:4,name:'Samurai help bank',original:previous,address},
 {offset:ranges+84,size:2,name:'Samurai help range',original:first-1,value:last});
fs.writeFileSync(output,builder.rom);
fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,lessons,changes:builder.changes,allocations:builder.allocations},null,2));
