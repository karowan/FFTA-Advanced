import fs from 'node:fs';
import path from 'node:path';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
import {ROMBuilder,encodeText,encodeHelp} from '../src/rom-builder.mjs';
import {equipmentDisplayName} from '../src/equipment-display-names.mjs';

const out=path.join(root,'build/expansion/probes');
const prior=JSON.parse(fs.readFileSync(path.join(out,'job-data.json')));
const base=fs.readFileSync(path.join(out,'job-data.gba'));
if(sha1(base)!==prior.romSha1)throw Error('Job data manifest does not match ROM');
const registry=JSON.parse(fs.readFileSync(path.join(root,'build/expansion/registry.json')));
const clean=cleanROM();
const builder=new ROMBuilder(base,{start:Math.max(...prior.allocations.map(a=>a.offset+a.bytes))});
const previousPermissions=prior.allocations.find(a=>a.name==='equipment permission masks');
const permissions=Buffer.alloc(previousPermissions.bytes+8);
base.copy(permissions,0,previousPermissions.offset,previousPermissions.offset+previousPermissions.bytes);
const axePermissions=[];
for(const [i,jobId] of [2,16].entries()) {
  const at=prior.addresses.jobs-0x08000000+jobId*52+0x2d;
  const oldIndex=base[at],index=previousPermissions.bytes/4+i;
  const mask=(permissions.readUInt32LE(oldIndex*4)|(1<<30))>>>0;
  permissions.writeUInt32LE(mask,index*4);builder.rom[at]=index;
  builder.changes.push({offset:at,original:oldIndex,value:index,width:1});
  axePermissions.push({jobId,oldIndex,index,mask});
}
const types={Sword:1,Saber:3,Knife:7,Rapier:8,Katana:9,Rod:11,Instrument:16,Axe:31};
const donors={Sword:1,Saber:32,Knife:74,Rapier:88,Katana:106,Rod:135,Instrument:201,Axe:52};
const items=Buffer.alloc(461*32);
// Include the native biased index-zero record: some callers request item0.
clean.copy(items,0,0x51d180,0x51d180+376*32);
const teaching=Buffer.alloc((225+85)*20);
clean.copy(teaching,0,0x520080,0x520080+225*20);
const others=Buffer.alloc((767+129)*4);
base.copy(others,0,0x5567f0,0x5567f0+767*4);
const helpFirst=0x650,helpLast=helpFirst+85-1;
const help=Buffer.alloc((helpLast-0x1de+1)*4);
// Bank13 originally uses 33 relative u16 entries. Convert those to pointers
// without changing a byte of the original text, and fill holes safely.
for(let id=0x1de;id<=helpLast;id++)help.writeUInt32LE(0x084d1c78,(id-0x1de)*4);
for(let i=0;i<33;i++)help.writeUInt32LE(0x084d1c34+clean.readUInt16LE(0x4d1c34+i*2),i*4);
const itemProfiles=[];
for(const [index,item] of registry.items.entries()) {
  const donor=donors[item.category],type=types[item.category];
  if(!donor||!type)throw Error('Unsupported approved weapon family '+item.category);
  if(item.innateElement||item.innateStatus||item.weaponProc||item.otherStatBonuses)
    throw Error('New equipment effect requires explicit encoding');
  const record=Buffer.from(clean.subarray(0x51d180+donor*32,0x51d180+(donor+1)*32));
  record.writeUInt16LE(item.nameId,0);record.writeUInt16LE(helpFirst+index,2);
  record.writeUInt16LE(item.basePriceGil,4);record.writeUInt16LE(Math.floor(item.basePriceGil/2),6);
  record[8]=type;record[9]=0;record[10]=1;
  // Family handedness/support compatibility; axes forbid Monkey Grip as well
  // as Double Sword so their explicit no-shield/second-weapon rule survives.
  record[11]=item.category==='Axe'?2:record[11];
  record[12]=item.category==='Axe'?8:record[12]&15;
  // +0D is a native weapon graphics parameter, preserved with donor icon.
  // +0E is the icon ID, despite the randomizer's misleading NONO label.
  // Actual mystery merchandise category is+18; new stock is shop-only.
  record[24]=0;record[25]=0;
  record.fill(0,16,24);record[16]=item.weaponAttack;record[18]=item.magicPowerBonus;
  record.fill(0,26,29);
  const set=225+index;record.writeUInt16LE(set,29);record[31]=0;
  if(item.teaching.length>9)throw Error('Native teaching row capacity exceeded');
  const row=teaching.subarray(set*20,(set+1)*20);row[0]=item.teaching.length;
  item.teaching.forEach((owner,n)=>{row[2+n*2]=owner.jobId;row[3+n*2]=owner.abilityIndex;});
  record.copy(items,item.romItemId*32);
  const helpText=item.name+'. Teaches '+item.lessons.map(a=>a.name).join(', ')+'.';
  const bytes=encodeHelp(helpText);
  if(bytes.length>512)throw Error('Equipment help exceeds bounded decoder text size');
  help.writeUInt32LE(builder.allocate(item.id+' help',bytes),(helpFirst+index-0x1de)*4);
  itemProfiles.push({id:item.romItemId,name:item.name,displayName:equipmentDisplayName(item),donor,type,set,helpId:helpFirst+index,helpText,recordHex:record.toString('hex')});
}
// The five playable races are only part of this native namespace. Monster
// species use banks6..23, including reaction-name previews and enemy AI.
// The24-pointer table ends exactly at the first ability bank (51BAE4).
const nativeRaceCount=24;
if(clean.readUInt32LE(0x51ba84)!==0x0851ba84+nativeRaceCount*4)throw Error('Native race pointer table boundary changed');
const racePointers=Buffer.from(clean.subarray(0x51ba84,0x51ba84+nativeRaceCount*4));
const races=[];
for(const race of registry.races) {
  const records=Buffer.alloc((race.totalCount+1)*8);
  clean.copy(records,0,race.base,race.base+race.nativeCount*8);
  for(const lesson of registry.lessons)for(const owner of lesson.owners.filter(o=>o.race===race.id)) {
    const row=owner.abilityIndex*8;
    records.writeUInt16LE(lesson.nameId,row);
    // No custom effect is enabled in this probe. Effect-specific help and
    // native dispatch must be installed together before these are usable.
    records.writeUInt16LE(0,row+2);
    records.writeUInt16LE(lesson.globalAbilityId,row+4);
    records[row+6]=lesson.nativeType;records[row+7]=lesson.ap/10;
  }
  const address=builder.allocate(race.name+' learned ability records',records);
  racePointers.writeUInt32LE(address,race.id*4);races.push({...race,address});
}
for(const lesson of registry.lessons)
  others.writeUInt32LE(builder.allocate(lesson.id+' name',encodeText(lesson.name)),lesson.nameId*4);
const banks=Buffer.alloc(11*8);
clean.copy(banks,0,0x36da1c,0x36da1c+10*8);
banks.writeUInt16LE(0x13,80);banks.writeUInt16LE(0x1de,82);banks.writeUInt16LE(helpLast,84);
const addresses={permissions:builder.allocate('axe-owner equipment masks',permissions),items:builder.allocate('expanded equipment records',items),
  teaching:builder.allocate('expanded teaching sets',teaching),others:builder.allocate('expanded Other text pointers',others),
  races:builder.allocate('race ability pointers',racePointers),help:builder.allocate('pointer help bank13',help),
  helpBanks:builder.allocate('help bank ranges',banks)};
builder.repoint(0x0851d180,addresses.items,67);
builder.repoint(prior.addresses.permissions,addresses.permissions,3);
builder.repoint(0x08520080,addresses.teaching,12);
builder.repoint(0x085567f0,addresses.others);
builder.repoint(0x0851ba84,addresses.races);
builder.repoint(0x084d1c34,addresses.help,1);
builder.repoint(0x0836da1c,addresses.helpBanks,1);
const binary=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
if(!builder.rom.subarray(0x1100000,0x1100000+binary.length).every(x=>x===255))throw Error('Engine overlap');
binary.copy(builder.rom,0x1100000);
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const[a,,n]=l.trim().split(/\s+/);return[n,parseInt(a,16)];}));
builder.repoint(0x080ca8f2,symbols.ffta_item_teaching_index,1);
for(const [offset,name] of [[0xcad04,'ffta_equipment_weapon_class'],[0xcad54,'ffta_equipment_shield_jobs'],
  [0xcadc4,'ffta_equipment_twohand_jobs'],[0xcb980,'ffta_icon_draw_entry'],[0xcb99c,'ffta_icon_palette_entry']]) {
  if(!base.subarray(offset,offset+8).equals(clean.subarray(offset,offset+8)))throw Error('Equipment hook conflict');
  const icon=name.startsWith('ffta_icon');
  builder.rom.writeUInt16LE(icon?0x4b00:0x4800,offset);builder.rom.writeUInt16LE(icon?0x4718:0x4700,offset+2);
  builder.rom.writeUInt32LE(symbols[name]|1,offset+4);
  builder.changes.push({offset,name,size:8});
}
if(!base.subarray(0xcaba8,0xcabb4).equals(clean.subarray(0xcaba8,0xcabb4)))throw Error('Layout hook conflict');
builder.rom.writeUInt16LE(0xb408,0xcaba8);builder.rom.writeUInt16LE(0x46c0,0xcabaa);
builder.rom.writeUInt16LE(0x4b00,0xcabac);builder.rom.writeUInt16LE(0x4718,0xcabae);
builder.rom.writeUInt32LE(symbols.ffta_equipment_layout|1,0xcabb0);
builder.changes.push({offset:0xcaba8,name:'ffta_equipment_layout',size:12});
for(const [offset,name,size] of [[0x48ffc,'ffta_results_teaching',8],[0x6717a,'ffta_shop_teaching',12],
  [0x6fc5c,'ffta_shop_info_teaching',8],[0x8c822,'ffta_party_info_teaching',12]]) {
  const expected=clean.subarray(offset,offset+size);
  if(!base.subarray(offset,offset+size).equals(expected))throw Error('Direct teaching hook conflict');
  const aligned=(offset+3)&~3;
  for(let at=offset;at<offset+size;at+=2)builder.rom.writeUInt16LE(0x46c0,at);
  // r1 is overwritten by the displaced first instruction; other registers
  // may be live in these native UI/result routines.
  builder.rom.writeUInt16LE(0x4900,aligned);builder.rom.writeUInt16LE(0x4708,aligned+2);
  builder.rom.writeUInt32LE(symbols[name]|1,aligned+4);
  builder.changes.push({offset,name,size,expected:expected.toString('hex')});
}
if(base.subarray(0x13ea2,0x13eb0).toString('hex')!=='059d069c1b04db0bca1810880a18')throw Error('Text hook conflict');
builder.rom.writeUInt16LE(0xb408,0x13ea2);
builder.rom.writeUInt16LE(0x4b00,0x13ea4);builder.rom.writeUInt16LE(0x4718,0x13ea6);
builder.rom.writeUInt32LE(symbols.ffta_help_pointer|1,0x13ea8);
builder.rom.writeUInt16LE(0x46c0,0x13eac);builder.rom.writeUInt16LE(0x46c0,0x13eae);
builder.changes.push({offset:0x13ea2,name:'ffta_help_pointer',size:14});
fs.writeFileSync(path.join(out,'content-data.gba'),builder.rom);
fs.writeFileSync(path.join(out,'content-data.json'),JSON.stringify({status:'TEST ONLY: new job/effect dispatch and AP consumers are not enabled',
  baseSha1:sha1(base),romSha1:sha1(builder.rom),engineSha1:sha1(binary),addresses,itemProfiles,races,axePermissions,nativeRaceCount,
  allocations:builder.allocations,changes:builder.changes,
  remaining:['Effect-specific lesson descriptions and action dispatch','Axe battle graphics and all type consumers',
    'Native learning, job UI and sidecar integration','Story-gated additive shop stock']},null,2));
console.log(JSON.stringify({items:itemProfiles.length,lessons:registry.lessons.length,addresses,pointerChanges:builder.changes.length}));
