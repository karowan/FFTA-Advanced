import fs from 'node:fs';
import path from 'node:path';
import {root,sha1,cleanROM} from '../src/rom-data.mjs';
const out=path.join(root,'build/expansion/probes');
fs.mkdirSync(out,{recursive:true});
const setup=process.argv.includes('--setup');
const core=process.argv.includes('--inventory-core');
const menus=process.argv.includes('--menus');
const content=process.argv.includes('--content');
if(content&&setup)throw Error('Content and setup probes are separate');
if(menus&&!core)throw Error('Menu probe requires inventory core');
const base=fs.readFileSync(path.join(root,content?'build/expansion/probes/content-data.gba':setup?'build/test-lab/setup-only.gba':'build/foundation/FFTA_vanillaplus_dev.gba'));
const clean=cleanROM();
const binary=fs.readFileSync(path.join(root,'build/expansion/engine.bin'));
const symbols=Object.fromEntries(fs.readFileSync(path.join(root,'build/expansion/engine.symbols'),'utf8').trim().split(/\r?\n/).map(l=>{const [address,,name]=l.trim().split(/\s+/);return [name,parseInt(address,16)];}));
const rom=Buffer.from(base);
if(content){
  if(!rom.subarray(0x1100000,0x1100000+binary.length).equals(binary))throw Error('Content engine is stale');
}else if(!rom.subarray(0x1100000,0x1100000+binary.length).every(b=>b===0xff))throw Error('Engine overlaps allocated ROM');
binary.copy(rom,0x1100000);
const changes=[];
const hooks=[[0x13aa48,'ffta_load_normal','174c184a281c211c'],[0x13aad8,'ffta_load_suspend','194c1a4a281c211c']];
if(core){
  if(base.readUInt32LE(0x36d4b8)!==0x03005e79)throw Error('Native clear dispatcher changed');
  rom.writeUInt32LE(symbols.ffta_native_clear_entry|1,0x36d4b8);
  changes.push({offset:0x36d4b8,name:'ffta_native_clear_entry',size:4,expected:0x03005e79});
  const sortOffset=0x1000530;
  if(base.subarray(sortOffset,sortOffset+4).toString('hex')!=='37480021')throw Error('Foundation sort integration conflict');
  const delta=symbols.ffta_sort_sidecars-(0x08000000+sortOffset+4);
  if(delta%2 || delta < -0x400000 || delta>=0x400000)throw Error('Sort sidecar call out of range');
  rom.writeUInt16LE(0xf000|((delta>>12)&0x7ff),sortOffset);
  rom.writeUInt16LE(0xf800|((delta>>1)&0x7ff),sortOffset+2);
  changes.push({offset:sortOffset,name:'ffta_sort_sidecars',size:4,expected:'37480021'});
  for(const [offset,name] of [[0x227fc,'ffta_battle_heap_limit'],[0x4ca14,'ffta_results_heap_limit'],[0x13c078,'ffta_global_heap_limit']])
    hooks.push([offset,name,clean.subarray(offset,offset+8).toString('hex')]);
  // Native battle lists allocate from these u16 descriptor capacities. Keep
  // their allocation/free lifecycle and admit every expanded equipment ID.
  for(const offset of [0x3914f8,0x39150c]) {
    if(base.readUInt16LE(offset)!==252)throw Error('Battle list capacity guard changed');
    rom.writeUInt16LE(446,offset);
    changes.push({offset,expected:252,value:446,width:2});
  }
  for(const [offset,name] of [[0xca900,'ffta_native_give_item'],[0xca9e8,'ffta_native_lose_item'],[0xcb2b4,'ffta_native_free_count'],[0xcb320,'ffta_native_has_item'],[0x388c8,'ffta_native_owned'],[0xcb210,'ffta_native_inventory'],[0xcb1f4,'ffta_native_is_weapon'],[0xcab24,'ffta_native_equipment_event'],[0x6807c,'ffta_native_has_transferable'],[0x6c942,'ffta_sell_commit'],[0x5b872,'ffta_feed_commit'],[0x61dfe,'ffta_reward_equipment_cap']]){
    const size=offset%4?12:8;
    hooks.push([offset,name,clean.subarray(offset,offset+size).toString('hex')]);
  }
}
if(menus){
  for(const [offset,name] of [[0x8cbdc,'ffta_party_item_list'],[0x799c0,'ffta_equip_item_list'],[0xcbdc0,'ffta_shop_buy_entry'],[0xcc7f8,'ffta_shop_sell_list']])hooks.push([offset,name,clean.subarray(offset,offset+(name==='ffta_shop_buy_entry'?12:8)).toString('hex')]);
  const put=(offset,expected,value,width=4)=>{
    const old=width===4?base.readUInt32LE(offset):base.readUInt16LE(offset);
    if(old!==expected)throw Error('UI buffer patch conflict at '+offset.toString(16));
    if(width===4)rom.writeUInt32LE(value,offset);else rom.writeUInt16LE(value,offset);
    changes.push({offset,expected,value,width});
  };
  put(0x71228,base.readUInt32LE(0x71228),0x203c000-0x200f3b8);
  // The shop owns its expanded list. A fixed high-RAM scratch pointer would
  // write inside the shop's free heap block and could collide with allocation.
  put(0x68b5c,0x9c08,0xa360);
  // Wide count, absolute selection and six saved scroll positions. Visible
  // row cursors stay native bytes; generic list+18/+1A are already halfwords.
  const shopWideFields=new Map([[0x446d,0xa338],[0x44ee,0xa33a],[0x44f1,0xa33c]]);
  for(let at=0x68a00;at<0x6f600;at+=4){
    const old=clean.readUInt32LE(at);
    if(shopWideFields.has(old))put(at,old,shopWideFields.get(old));
  }
  const shopWideAccesses=[0x69ee2,0x69f54,0x6a066,0x6a074,0x6a096,0x6a0dc,0x6a0f0,0x6a2a4,0x6b29e,0x6b324,0x6bfe4,0x6c054,0x6c15a,0x6c168,0x6c18a,0x6c1d0,0x6c1e4,0x6c380,0x6e1ba,0x6e2d8,0x6e2fa,0x6e3b6,0x6e3da,0x6e41a,0x69fc0,0x69fc6,0x6a150,0x6a156,0x6a328,0x6a332,0x6a338,0x6a474,0x6b4f0,0x6b4f6,0x6c0b8,0x6c0be,0x6c23c,0x6c242,0x6c400,0x6c40e,0x6c414,0x6c504,0x6d450,0x6d456,0x6d4c0,0x6e19c,0x6e1a2,0x69c60,0x69da6,0x69e60,0x6a00c,0x6a19c,0x6a382,0x6ab08,0x6b522,0x6bd7e,0x6beac,0x6bf60,0x6c104,0x6c288,0x6c45e,0x6cbd2,0x6d482];
  for(const at of shopWideAccesses){
    const old=clean.readUInt16LE(at),op=old&0xf800;
    if(op!==0x7800&&op!==0x7000)throw Error('Shop byte access changed at '+at.toString(16));
    if(old&0x7c0)throw Error('Unexpected shop byte immediate');
    put(at,old,(old&0x7ff)|(op===0x7800?0x8800:0x8000),2);
  }
  // A fresh tab result is scaled solely for the following saved-scroll access.
  for(const at of [0x69c58,0x69d9e,0x69e58,0x69ffe,0x6a18e,0x6a374,0x6ab00,0x6b514,
      0x6bd76,0x6bea4,0x6bf58,0x6c0f6,0x6c27a,0x6c450,0x6cbca,0x6d474]){
    put(at,0x0e00,0x0dc0,2); // lsrs r0,r0,24 ->23: unsigned tab *2
  }
  for(const at of [0x6e2aa,0x6e2ac,0x6e396,0x6e398,0x6e42a,0x6e42c,
      0x6a30a,0x6a30c,0x6b37e,0x6b380,0x6b402,0x6b404,
      0x6c3e2,0x6c3e4,0x6d346,0x6d348,0x6d3ca,0x6d3cc,
      0x6e220,0x6e222,0x6e818,0x6e81a,0x6f6be,0x6f6c0]){
    const old=clean.readUInt16LE(at);
    if(((old>>6)&31)!==24)throw Error('Shop index shift changed');
    put(at,old,(old&~0x7c0)|(16<<6),2);
  }
  // Initial row drawing reads the absolute top index from native list+1A.
  {const at=0x6e1e8,old=clean.readUInt16LE(at);
    if(old!==0x7eb4)throw Error('Shop renderer top-index load changed');
    put(at,old,0x8b74,2); // ldrb r4,[r6,26] -> ldrh r4,[r6,26]
  }
  for(const [at,name] of [[0x6e1a8,'ffta_shop_selected_setup'],[0x6d45c,'ffta_shop_selected_refresh'],
      [0x69af8,'ffta_shop_buy_positions_reset'],[0x6bb60,'ffta_shop_sell_positions_reset']])
    hooks.push([at,name,clean.subarray(at,at+12).toString('hex')]);
  put(0x7a8ce,clean.readUInt16LE(0x7a8ce),0xe000,2);
  put(0x82458,clean.readUInt16LE(0x82458),0xe000,2);
  const installer=fs.readFileSync(path.join(root,'tools/ffta-engine-hacks/Engine Hacks/newInventory/installer.event'),'utf8');
  const matches=[...installer.matchAll(/ORG \$([0-9A-Fa-f]+); WORD \(0x2030000-0x2022F5C\+([023])\)/g)];
  if(matches.length!==27)throw Error('Upstream shop buffer manifest changed: '+matches.length);
  for(const [,at,extra] of matches)put(parseInt(at,16),0x2027460-0x2022f5c+Number(extra),0x9c08+Number(extra));
}
for(const [offset,name,expected] of hooks){
  if(base.subarray(offset,offset+expected.length/2).toString('hex')!==expected)throw Error('Hook bytes changed: '+name);
  const preserveTown=name==='ffta_shop_buy_entry'||name.startsWith('ffta_shop_selected_')||name.endsWith('_positions_reset');
  const aligned=preserveTown?offset+4:(offset+3)&~3;
  for(let p=offset;p<offset+expected.length/2;p+=2)rom.writeUInt16LE(0x46c0,p);
  if(preserveTown)rom.writeUInt16LE(0xb408,offset);
  rom.writeUInt16LE(0x4b00,aligned);rom.writeUInt16LE(0x4718,aligned+2);
  rom.writeUInt32LE(symbols[name]|1,aligned+4);
  changes.push({offset,name,expected,address:symbols[name]});
}
const name=content?'content-inventory':setup?'inventory-startup':menus?'inventory-menus':core?'inventory-core':'storage-only';
fs.writeFileSync(path.join(out,name+'.gba'),rom);
fs.writeFileSync(path.join(out,name+'.json'),JSON.stringify({status:'TEST ONLY: inventory UI is not adapted; never distribute as playable expansion',baseSha1:sha1(base),romSha1:sha1(rom),engineSha1:sha1(binary),changes},null,2));
console.log('Built isolated native-load migration probe');
