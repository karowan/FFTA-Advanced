export function patchMobilitySupports(rom,symbols) {
  const offset=0xca394,size=12,expected='f0b5041c1e21fef7a9ff0006';
  if(rom.subarray(offset,offset+size).toString('hex')!==expected)throw Error('Movement getter bytes changed');
  const name='ffta_move_support_entry',target=symbols[name];
  if(!Number.isInteger(target))throw Error('Missing movement support hook');
  rom.writeUInt16LE(0xb408,offset);rom.writeUInt16LE(0x46c0,offset+2);
  rom.writeUInt16LE(0x4b00,offset+4);rom.writeUInt16LE(0x4718,offset+6);
  rom.writeUInt32LE(target|1,offset+8);
  return [{offset,size,name,expected}];
}
