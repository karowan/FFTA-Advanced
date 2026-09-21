export function patchQuinHistory(rom,symbols) {
 const rows=[
  {offset:0xd241c,size:8,name:'ffta_quin_candidate_entry',expected:'f0b557464e464546'},
  {offset:0x807d4,size:8,name:'ffta_quin_accept_entry',expected:'52f0aafb28680019'},
  {offset:0x62004,size:12,name:'ffta_quin_swap_entry',expected:'381c68f0d9f838602b262e24'},
 ];
 for(const row of rows) {
  const {offset,size,name,expected}=row,target=symbols[name];
  if(rom.subarray(offset,offset+size).toString('hex')!==expected)throw Error(`Quin hook preimage changed at ${offset.toString(16)}`);
  if(!Number.isInteger(target))throw Error(`Missing Quin hook ${name}`);
  if(offset%4) {
   rom.writeUInt16LE(0x4b01,offset);rom.writeUInt16LE(0x4718,offset+2);rom.writeUInt16LE(0x46c0,offset+4);rom.writeUInt32LE(target|1,offset+6);
  } else {
   rom.writeUInt16LE(0x4b00,offset);rom.writeUInt16LE(0x4718,offset+2);rom.writeUInt32LE(target|1,offset+4);
   for(let p=offset+8;p<offset+size;p+=2)rom.writeUInt16LE(0x46c0,p);
  }
 }
 return rows;
}
