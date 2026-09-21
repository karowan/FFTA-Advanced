/* Extra visual keys do not alias native statuses. Four dedicated OBJ tiles
 * are reserved in the battle graphics constructor; no global atlas overwrite.
 * Call only when the compiled status/ownership routines are present. */
export function patchStatusDisplay(rom, symbols) {
  const changes=[];
  function expect(offset, hex) {
    const bytes=Buffer.from(hex,'hex');
    if(!rom.subarray(offset,offset+bytes.length).equals(bytes))
      throw Error(`Status display conflict at ${offset.toString(16)}`);
    return bytes;
  }
  function symbol(name) {
    if(!symbols[name])throw Error(`Missing status display symbol ${name}`);
    return symbols[name]|1;
  }
  expect(0x97098,'f0235b00');
  rom.writeUInt16LE(0x23f2,0x97098);
  changes.push({offset:0x97098,bytes:2,name:'battle upper OBJ pool1E0 to1E4',expected:'f023'});
  expect(0x9da0c,'10b5041c0904080c');
  rom.writeUInt16LE(0x4b00,0x9da0c);rom.writeUInt16LE(0x4718,0x9da0e);
  rom.writeUInt32LE(symbol('ffta_status_icon_entry'),0x9da10);
  changes.push({offset:0x9da0c,bytes:8,name:'ffta_status_icon_entry',expected:'10b5041c0904080c'});
  for(const [offset,hex,name] of [
    [0x9dd52,'a0780130a07000060016182800dda570','ffta_status_next_entry'],
    [0x97ad0,'b06c4246002151568904114bc918090c00228af7cff8','ffta_status_visual_entry']
  ]) {
    const original=expect(offset,hex);
    for(let p=offset;p<offset+original.length;p+=2)rom.writeUInt16LE(0x46c0,p);
    rom.writeUInt16LE(0xb408,offset);const jump=(offset+5)&~3;
    if(jump+8>offset+original.length)throw Error('Status display hook exceeds its span');
    rom.writeUInt16LE(0x4b00,jump);rom.writeUInt16LE(0x4718,jump+2);
    rom.writeUInt32LE(symbol(name),jump+4);
    changes.push({offset,bytes:original.length,name,expected:hex});
  }
  return changes;
}
