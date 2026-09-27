/**
 * Allocate Physician/Sapper identity and AP records over the accepted local ROM.
 * This is an inert development stage. No new action, teaching item, UI path or
 * effect is installed, and its result must never be selected as a release.
 */
import fs from 'node:fs';
import path from 'node:path';
import {root,sha1} from '../src/rom-data.mjs';
import {ROMBuilder,encodeText} from '../src/rom-builder.mjs';

const input=path.join(root,'build/expansion/probes/pub-return/candidate/FFTA_Reviewed_All_Classes.gba');
const expected='dd20c5771418cf470594c3e79c6d197b3bae4848';
const base=fs.readFileSync(input);
if(sha1(base)!==expected)throw Error('Accepted parent changed');
const design=JSON.parse(fs.readFileSync(path.join(root,'notes/chemist-progression-abilities.json')));
if(design.schema!==1||design.jobs.length!==2)throw Error('Unexpected progression allocation');
const equipment=JSON.parse(fs.readFileSync(path.join(root,'notes/chemist-progression-equipment.json')));
if(equipment.schema!==1||equipment.items.length!==10)throw Error('Unexpected teaching item allocation');
const builder=new ROMBuilder(base,{start:0x1a00000,end:0x1a10000});
const readPointer=offset=>base.readUInt32LE(offset);
const offsetOf=address=>{
  if(address<0x08000000||address>=0x0a000000)throw Error('Invalid ROM address');
  return address-0x08000000;
};
const patchPointer=(oldAddress,newAddress,expectedCount)=>{
  const sites=[];
  for(let at=0;at<base.length-3;at+=4)if(base.readUInt32LE(at)===oldAddress)sites.push(at);
  if(sites.length!==expectedCount)throw Error(`Pointer consumers changed for ${oldAddress.toString(16)}: ${sites.length}`);
  for(const at of sites)builder.rom.writeUInt32LE(newAddress,at);
  return sites;
};
const oldJobs=readPointer(0xc8598),oldNames=0x090208d8;
const oldRequirements=readPointer(0xc8b18),oldPermissions=0x09027000;
const oldOtherNames=0x0902e508;
const oldItems=0x090270bc,oldTeaching=0x0902aa5c;
if(oldJobs!==0x09021618||oldRequirements!==0x09023064)throw Error('Native table identity changed');
const jobRows=Buffer.alloc(128*52);
base.copy(jobRows,0,offsetOf(oldJobs),offsetOf(oldJobs)+126*52);
const jobNames=Buffer.alloc(860*4);
base.copy(jobNames,0,offsetOf(oldNames),offsetOf(oldNames)+848*4);
const requirements=Buffer.alloc(32*4);
base.copy(requirements,0,offsetOf(oldRequirements),offsetOf(oldRequirements)+30*4);
const permissions=Buffer.alloc(49*4);
base.copy(permissions,0,offsetOf(oldPermissions),offsetOf(oldPermissions)+47*4);
const abilityNames=Buffer.alloc(916*4);
base.copy(abilityNames,0,offsetOf(oldOtherNames),offsetOf(oldOtherNames)+896*4);
const items=Buffer.alloc(471*32);
base.copy(items,0,offsetOf(oldItems),offsetOf(oldItems)+461*32);
const teaching=Buffer.alloc(320*20);
base.copy(teaching,0,offsetOf(oldTeaching),offsetOf(oldTeaching)+310*20);
const racePointerBase=offsetOf(readPointer(0x257e8));
const nativeRaceCount=24;
const racePointers=Buffer.from(base.subarray(racePointerBase,racePointerBase+nativeRaceCount*4));
const oldCounts={3:124,5:116};
const types={Action:1,Reaction:2,Support:3,Combo:5};
const proof=[];

for(const [ordinal,job] of design.jobs.entries()){
  if(job.id!==126+ordinal||![3,5].includes(job.race)||job.lessons.length!==10)
    throw Error('Unexpected job identity or lesson count');
  if(job.lessons.filter(x=>x[2]==='Action').length!==7)throw Error('Expected seven actions');
  const donor=base.subarray(offsetOf(oldJobs)+job.donor*52,offsetOf(oldJobs)+(job.donor+1)*52);
  if(donor[4]!==job.race)throw Error('Cross-race donor');
  const row=Buffer.from(donor);
  row.writeUInt16LE(848+ordinal,0);row[4]=job.race;row[5]=0;row[0x10]=job.id;row[0x11]=0;
  row.writeUInt32LE(0x01249248,0x12);row[0x16]=50;
  const [hp,mp,atk,def,pow,res,spd]=job.base;
  row[0x17]=hp;row[0x18]=mp;row[0x19]=spd;
  if([atk,def,pow,res].some(x=>x<0||x>4095))throw Error('Stat field overflow');
  row.writeUIntLE(atk|(def<<12),0x1a,3);row.writeUIntLE(pow|(res<<12),0x1d,3);
  const growth=[job.growth[0],job.growth[1],job.growth[6],job.growth[2],job.growth[3],job.growth[4],job.growth[5]].map(x=>Math.round(10*x));
  if(growth.some(x=>x<0||x>255))throw Error('Growth field overflow');
  Buffer.from(growth).copy(row,0x20);
  row[0x28]=job.move;row[0x29]=job.jump;row[0x2a]=job.evade;row[0x2b]=0x21;
  row[0x2c]=0;row[0x2d]=47+ordinal;row[0x30]=30+ordinal;row[0x31]=0;
  if(job.prerequisites.length!==2)throw Error('Paired prerequisites required');
  Buffer.from(job.prerequisites.flat()).copy(requirements,(30+ordinal)*4);
  const mask=[...job.equipmentTypes,27,28,29].reduce((m,type)=>m|(1<<(type-1)),0)>>>0;
  permissions.writeUInt32LE(mask,(47+ordinal)*4);
  const first=oldCounts[job.race];row[0x2e]=first;row[0x2f]=first+9;
  row.copy(jobRows,job.id*52);
  jobNames.writeUInt32LE(builder.allocate(job.name+' job name',encodeText(job.name)),(848+ordinal)*4);
  const oldRace=offsetOf(racePointers.readUInt32LE(job.race*4));
  const abilityRows=Buffer.alloc((first+11)*8);
  base.copy(abilityRows,0,oldRace,oldRace+first*8);
  for(const [n,[name,display,type,id,ap]] of job.lessons.entries()){
    if(!types[type]||ap%10||ap/10>127||display.length>11)throw Error('Invalid lesson '+name);
    const nameId=896+ordinal*10+n,index=first+n;
    abilityNames.writeUInt32LE(builder.allocate(name+' ability name',encodeText(display)),nameId*4);
    abilityRows.writeUInt16LE(nameId,index*8);
    abilityRows.writeUInt16LE(0,index*8+2); // Help installed with effects, not a fake donor description.
    abilityRows.writeUInt16LE(id,index*8+4);
    abilityRows[index*8+6]=types[type];abilityRows[index*8+7]=ap/10;
  }
  racePointers.writeUInt32LE(builder.allocate(job.name+' race abilities',abilityRows),job.race*4);
  proof.push({job:job.name,id:job.id,race:job.race,firstAbility:first,lastAbility:first+9,
    prerequisiteIndex:30+ordinal,permissionIndex:47+ordinal,permissionMask:mask,
    record:row.toString('hex')});
}
const taught=new Set();
for(const [i,item] of equipment.items.entries()){
  if(item.id!==461+i||item.name.length>14||item.price<0||item.price>65535||item.lessons.length!==2)
    throw Error('Invalid teaching equipment identity');
  const job=design.jobs.find(x=>x.id===item.job);
  if(!job||job.equipmentTypes.includes(item.type)===false)throw Error('Teacher outside job equipment');
  const donor=base.subarray(offsetOf(oldItems)+item.donor*32,offsetOf(oldItems)+(item.donor+1)*32);
  if(donor[8]!==item.type)throw Error('Wrong equipment donor type');
  const row=Buffer.from(donor),set=310+i,nameId=850+i;
  row.writeUInt16LE(nameId,0);row.writeUInt16LE(0,2); // Help is an effect-stage dependency.
  row.writeUInt16LE(item.price,4);row.writeUInt16LE(Math.floor(item.price/2),6);
  row[8]=item.type;row[9]=0;row[10]=1;row[11]=donor[11];row[12]=donor[12]&15;
  row.fill(0,16,24);row[16]=item.attack;row[18]=item.power;
  row[24]=0;row[25]=0;row.fill(0,26,29);row.writeUInt16LE(set,29);row[31]=0;
  row.copy(items,item.id*32);
  const setRow=teaching.subarray(set*20,(set+1)*20);setRow[0]=2;
  for(const [n,lesson] of item.lessons.entries()){
    if(!Number.isInteger(lesson)||lesson<0||lesson>=10)throw Error('Invalid lesson index');
    const key=`${job.id}:${lesson}`;
    if(taught.has(key))throw Error('Duplicate teaching source '+key);
    taught.add(key);setRow[2+2*n]=job.id;setRow[3+2*n]=oldCounts[job.race]+lesson;
  }
  jobNames.writeUInt32LE(builder.allocate(item.name+' equipment name',encodeText(item.name)),nameId*4);
}
if(taught.size!==20)throw Error('Not every lesson has one teaching source');
const addresses={jobs:builder.allocate('128 job records',jobRows),
  jobNames:builder.allocate('860 item/job names',jobNames),
  requirements:builder.allocate('32 prerequisite pairs',requirements),
  permissions:builder.allocate('49 permission masks',permissions),
  abilityNames:builder.allocate('916 ability names',abilityNames),
  races:builder.allocate('24 race bank pointers',racePointers),
  items:builder.allocate('471 equipment records',items),
  teaching:builder.allocate('320 teaching sets',teaching)};
const pointerSites={jobs:patchPointer(oldJobs,addresses.jobs,8),
  jobNames:patchPointer(oldNames,addresses.jobNames,74),
  requirements:patchPointer(oldRequirements,addresses.requirements,2),
  permissions:patchPointer(oldPermissions,addresses.permissions,3),
  abilityNames:patchPointer(oldOtherNames,addresses.abilityNames,99),
  races:patchPointer(readPointer(0x257e8),addresses.races,22),
  items:patchPointer(oldItems,addresses.items,67),
  teaching:patchPointer(oldTeaching,addresses.teaching,12)};
const out=path.join(root,'build/expansion/chemist-progressions/data-only');
fs.mkdirSync(out,{recursive:true});
const target=path.join(out,'inert-data.gba');fs.writeFileSync(target,builder.rom);
const manifest={status:'INERT DATA STAGE; NOT PLAYABLE OR RELEASE-ELIGIBLE',input,inputSha1:expected,
  target,targetSha1:sha1(builder.rom),design:'notes/chemist-progression-abilities.json',
  equipment:'notes/chemist-progression-equipment.json',
  reservation:[0x1a00000,0x1a10000],addresses,pointerSites,proof,allocations:builder.allocations,
  remaining:['Native action records and effects','Teaching equipment help/shop availability and AP admission',
    'Job wheel/command UI and battle command dispatch','AI/laws/combo/reaction/support',
    'Exact save/copy lifetime and native art','Gameplay acceptance and packaging']};
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:manifest.status,targetSha1:manifest.targetSha1,addresses,proof},null,2));
