import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1,missions,itemName} from '../src/rom-data.mjs';
const vanilla=cleanROM(),build=path.join(root,'build/foundation'),vendor=path.join(build,'engine');
const finalize=process.argv.includes('--finalize');
const out=path.join(build,'FFTA_vanillaplus_dev.gba');
if(!finalize){
fs.mkdirSync(build,{recursive:true});
fs.cpSync(path.join(root,'tools/ffta-engine-hacks/Engine Hacks'),vendor,{recursive:true});
const p=f=>path.join(vendor,f).replaceAll('\\','/');
let sort=fs.readFileSync(p('manualSorting.event'),'utf8').replace('#define marcheSwap 1','#define marcheSwap 0').replace('#define montblancSwap 1','#define montblancSwap 0');
// Keeping both story units fixed removes the need for unrelated story/save hooks.
sort=sort.slice(0,sort.indexOf('PUSH; ORG $122630'));
fs.writeFileSync(p('manualSorting.event'),sort);
// Upstream loops visit 25 coordinates, but the table holds 24. Repair both comparisons.
let buttons=fs.readFileSync(p('manualSorting/buttonmanualsorting.dmp')),repairs=0;
for(let i=0;i<buttons.length-1;i+=2)if(buttons.readUInt16LE(i)===0x2830){buttons.writeUInt16LE(0x282e,i);repairs++;}
if(repairs!==2)throw Error('Upstream sorting bytecode changed');
fs.writeFileSync(p('manualSorting/buttonmanualsorting.dmp'),buttons);
// Allocate beyond the entire original ROM, rather than assume its tail is empty.
fs.writeFileSync(out,Buffer.concat([vanilla,Buffer.alloc(0x1000000,0xff)]));
const event=`#include "Extensions/Hack Installation.txt"
#define FreeSpace 0x1000000
ORG FreeSpace
#define installManualSorting
#define fixMorpherAnimations
#include "${p('manualSorting.event')}"
#include "${p('morphingMorphersMorph.event')}"
// Hook the unit-aware getter only. Bare job-table queries have no unit pointer.
PUSH
ORG $C92F0
jumpToHack(unitVisualStat)
POP
ALIGN 4
unitVisualStat:
SHORT $B5F0 $1C04 $1C0D
BL(originalUnitStat)
SHORT $22EA $5CA1 $2204 $4211
SHORT ($D000|(((visualReturn-currentOffset-4)>>1)&$FF))
SHORT $2100 $1C2A $1C23
BL(newGetAnimation)
SHORT $2100 $1C2A $1C23
BL(newGetAnimationWater)
SHORT $2100 $1C2A $1C23
BL(newGetMoving)
SHORT $2100 $1C2A $1C23
BL(newGetStanding)
visualReturn:
SHORT $BCF0 $BC02 $4708
ALIGN 4
originalUnitStat:
SHORT $B500 $1C03 $0609 $0E0A
SHORT $4E00 $4730
POIN $C92F9
PUSH
ORG $5D23C
SHORT 0x46C0 0xB408
jumpToHack(pubAction)
POP
ALIGN 4
pubAction:
#incbin "${p('ASM/customPubOptions.dmp')}"
POIN pubOrder
pubOrder:
BYTE 0 1 1 0 2 2 3 3
PUSH
ORG $5567F0+(4*0x29)
POIN $55431E $554316 $554328 $554341
ORG $4C5170
SHORT $E90 $E50 $EE4 $F44
POP
ALIGN 4
foundationEnd:
MESSAGE "Foundation ends at" currentOffset
MESSAGE "unitVisualStat" unitVisualStat
MESSAGE "newGetAnimation" newGetAnimation
MESSAGE "newGetAnimationWater" newGetAnimationWater
MESSAGE "newGetMoving" newGetMoving
MESSAGE "newGetStanding" newGetStanding
`;
const source=path.join(build,'foundation.event');fs.writeFileSync(source,event);
console.log('Prepared foundation source');
}else{
const log=fs.readFileSync(path.join(build,'assembler.log'),'utf8');
if(!log.includes('No errors.')||/^error:/im.test(log))throw Error('Assembler failed');
let rom=fs.readFileSync(out),edits=[];
const ms=missions(vanilla);
function editMission(id,at,expected,value,width,why){const m=ms[id];const offset=m.offset+at;const old=width===2?rom.readUInt16LE(offset):rom[offset];if(old!==expected)throw Error(`Unexpected mission ${id} field ${at}`);if(width===2)rom.writeUInt16LE(value,offset);else rom[offset]=value;edits.push({mission:m.name,record:id,offset,old,value,why});}
editMission(69,0x24,0xfff7,397,2,'Wyrmstone refund replaces one random equipment reward; first random reward retained');
editMission(183,0x24,0xfff3,379,2,"Elda's Cup refund replaces random equipment reward; Caravan Musk retained");
editMission(111,0x35,1,ms[66].recruit,1,'Reuse Missing Prof recruitment rule on repeatable Mythril Rush');
function replaceMonster(offset,expectedJob,template,why){
  if(vanilla[offset+1]!==expectedJob)throw Error('Unexpected encounter species');
  const before=Buffer.from(rom.subarray(offset,offset+48));
  rom[offset+1]=vanilla[template+1];
  // Native ability bits and reaction/support; retain level, position, equipment and AI.
  vanilla.copy(rom,offset+0x14,template+0x14,template+0x2a);
  edits.push({offset,template,oldJob:expectedJob,newJob:rom[offset+1],before:before.toString('hex'),after:rom.subarray(offset,offset+48).toString('hex'),why});
}
replaceMonster(0x53bbd0,0x2d,0x53f530,'Tricky Spirits: replace Red Cap with native Goblin carrying Goblin Punch and no reaction/support');
replaceMonster(0x53bde0,0x33,0x5395c0,'Wild Monsters: replace Icedrake with native Thundrake carrying Dragon Force, Bolt Breath, Reflex and Geomancy');
fs.writeFileSync(out,rom);
const ranges=[];let start=null;
for(let i=0;i<vanilla.length;i++){if(rom[i]!==vanilla[i]){if(start===null)start=i;}else if(start!==null){ranges.push({offset:start,length:i-start});start=null;}}
if(start!==null)ranges.push({offset:start,length:vanilla.length-start});
const manifest={build:'foundation-dev-1',status:'experimental; feature testing required',baseSha1:sha1(vanilla),outputSha1:sha1(rom),bytes:rom.length,engineCommit:'14ad10060ee21474c56272fd94bcc21d5a92264c',enabled:['mission-refunds-two-cases','Quin-retry-Mythril-Rush','manual-sorting-story-units-fixed','Morpher-visuals','pub-missions-first','Goblin-and-Thundrake-encounter-edits'],notYetImplemented:['remaining-completion-audit','rare-equipment-recovery','expanded-ability-UI','new-jobs-and-abilities','new-weapon-stock'],changes:edits,changedOriginalRanges:ranges,assemblerLog:log};
fs.writeFileSync(path.join(build,'manifest.json'),JSON.stringify(manifest,null,2));
console.log(JSON.stringify({output:out,sha1:manifest.outputSha1,edits,originalChangedBytes:ranges.reduce((n,r)=>n+r.length,0),log},null,2));
}

