// Scoped law-query copies only. Each original native copy remains264 bytes;
// the allocation carries an explicitly registered12-byte ownership tail.
export function patchEvaluatedUnits(rom, symbols) {
  const sites = [
    [0x1347d0, 12, 'ffta_law_actor_a', '84256d00281ceef633f88046'],
    [0x1347dc, 8, 'ffta_law_target_a', '281ceef62ff8061c'],
    [0x13488c, 12, 'ffta_law_actor_b', '84246400201cedf6d5ff071c'],
    [0x134898, 8, 'ffta_law_target_b', '201cedf6d1ff061c'],
  ];
  const changes=[];
  for (const [offset,size,name,expected] of sites) {
    if (rom.subarray(offset,offset+size).toString('hex')!==expected) throw new Error(`Law evaluator bytes differ at ${offset.toString(16)}`);
    const target=symbols[name];
    if (!Number.isInteger(target)) throw new Error(`Missing ${name}`);
    rom.writeUInt16LE(0x4800,offset);rom.writeUInt16LE(0x4700,offset+2);
    rom.writeUInt32LE(target|1,offset+4);
    for (let p=offset+8;p<offset+size;p+=2) rom.writeUInt16LE(0x46c0,p);
    changes.push({offset,size,name,expected});
  }
  return changes;
}
