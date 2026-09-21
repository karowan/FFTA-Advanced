export function patchGraceSupport(rom,symbols) {
  const offset=0x12c89c,size=12,expected='00214156301c15f009ff041c';
  if(rom.subarray(offset,offset+size).toString('hex')!==expected)throw Error('Grace accuracy bytes changed');
  const name='ffta_grace_evade_entry',target=symbols[name];
  if(!Number.isInteger(target))throw Error('Missing Grace hook');
  rom.writeUInt16LE(0xb408,offset);rom.writeUInt16LE(0x46c0,offset+2);
  rom.writeUInt16LE(0x4b00,offset+4);rom.writeUInt16LE(0x4718,offset+6);
  rom.writeUInt32LE(target|1,offset+8);
  return [{offset,size,name,expected}];
}
