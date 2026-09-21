import {ROMBuilder,encodeHelp} from '../src/rom-builder.mjs';
import {lessonHelp} from '../src/lesson-help.mjs';

export function patchLessonHelp(rom,registry,content,enabledActions,enabledSupports) {
 const first=0x6a5,last=first+Object.keys(lessonHelp).length-1;
 const pointer=0x36d6c4,old=content.addresses.help;
 if(rom.readUInt32LE(pointer)!==old)throw Error('Unexpected help bank pointer');
 const ranges=content.addresses.helpBanks-0x08000000;
 if(rom.readUInt16LE(ranges+80)!==0x13 || rom.readUInt16LE(ranges+84)!==first-1)throw Error('Help range changed');
 // Separate, guarded arena preserves every previously allocated table address.
 const builder=new ROMBuilder(rom,{start:0x10e0000,end:0x10f0000});
 const table=Buffer.alloc((last-0x1de+1)*4);
 rom.copy(table,0,old-0x08000000,old-0x08000000+(first-0x1de)*4);
 const lessons=[];
 for(const [i,[id,text]] of Object.entries(lessonHelp).entries()) {
  const lesson=registry.lessons.find(l=>l.id===id);
  if(!lesson)throw Error('Unknown lesson help '+id);
  if(lesson.type==='Action' && !enabledActions.includes(lesson.globalAbilityId) ||
     lesson.type==='Support' && !enabledSupports.includes(lesson.globalAbilityId))throw Error('Description for inactive lesson '+id);
  const bytes=encodeHelp(text,27);
  if([...bytes].filter((b,n)=>b===0x40 && bytes[n+1]===0x6e).length>2)throw Error('Lesson help exceeds three lines');
  const address=builder.allocate(id+' description',bytes),helpId=first+i;
  table.writeUInt32LE(address,(helpId-0x1de)*4);
  for(const owner of lesson.owners) {
   const race=content.races.find(r=>r.id===owner.race);
   const offset=race.address-0x08000000+owner.abilityIndex*8+2;
   if(builder.rom.readUInt16LE(offset)!==0)throw Error('Lesson help already populated');
   builder.rom.writeUInt16LE(helpId,offset);
   builder.changes.push({offset,size:2,name:id+' help ID',original:'0000',value:helpId});
  }
  lessons.push({id,helpId,text,address});
 }
 const address=builder.allocate('implemented lesson help bank',table);
 builder.rom.writeUInt32LE(address,pointer);builder.rom.writeUInt16LE(last,ranges+84);
 builder.changes.push({offset:pointer,size:4,name:'lesson help pointers',original:old,address},
  {offset:ranges+84,size:2,name:'lesson help range',original:first-1,value:last});
 builder.rom.copy(rom);
 return {changes:builder.changes,allocations:builder.allocations,lessons,first,last,address};
}
