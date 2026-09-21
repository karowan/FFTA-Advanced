import fs from 'node:fs';
import path from 'node:path';
import {root,sha1} from '../src/rom-data.mjs';
import {ROMBuilder,encodeHelp} from '../src/rom-builder.mjs';
import {completionLessonHelp} from '../src/completion-lesson-help.mjs';
const [input,output,manifest]=process.argv.slice(2);
if(!input||!output||!manifest)throw Error('Expected input, output and manifest');
const registry=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/registry.json')));
const content=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/probes/content-data.json')));
const image=fs.readFileSync(input),pointer=0x36d6c4,ranges=content.addresses.helpBanks-0x08000000;
const previous=image.readUInt32LE(pointer),first=image.readUInt16LE(ranges+84)+1;
const builder=new ROMBuilder(image,{start:0x1380000,end:0x1390000});
const last=first+Object.keys(completionLessonHelp).length-1;
const table=Buffer.alloc((last-0x1de+1)*4);
image.copy(table,0,previous-0x08000000,previous-0x08000000+(first-0x1de)*4);
const lessons=[],replacements={'GEO-C1':0x6b3,'CHM-C1':0x6b4};
for(const [n,[id,text]] of Object.entries(completionLessonHelp).entries()){
 const lesson=registry.lessons.find(l=>l.id===id),bytes=encodeHelp(text,27),helpId=first+n;
 if(!lesson)throw Error('Unknown lesson '+id);
 if([...bytes].filter((b,i)=>b===0x40&&bytes[i+1]===0x6e).length>2)throw Error('Help exceeds three lines '+id);
 const address=builder.allocate(id+' help',bytes);table.writeUInt32LE(address,(helpId-0x1de)*4);
 for(const owner of lesson.owners){
  const race=content.races.find(r=>r.id===owner.race),offset=race.address-0x08000000+owner.abilityIndex*8+2;
  if(builder.rom.readUInt16LE(offset)!==(replacements[id]??0))throw Error('Unexpected prior help '+id);
  builder.rom.writeUInt16LE(helpId,offset);
 }
 lessons.push({id,text,helpId,address});
}
const address=builder.allocate('Complete lesson help bank',table);
builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
fs.writeFileSync(output,builder.rom);
fs.writeFileSync(manifest,JSON.stringify({first,last,address,previous,inputSha1:sha1(image),
 lessons,allocations:builder.allocations},null,2));
