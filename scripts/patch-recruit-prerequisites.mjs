export function patchRecruitPrerequisites(rom,symbols) {
 const offset=0x620ac,size=12,expected='281c291c252266f05dfa041c';
 if(rom.subarray(offset,offset+size).toString('hex')!==expected)throw Error('Recruit prerequisite preimage changed');
 const name='ffta_recruit_prerequisite_entry',target=symbols[name];
 if(!Number.isInteger(target))throw Error('Missing recruit prerequisite hook');
 rom.writeUInt16LE(0xb408,offset);rom.writeUInt16LE(0x46c0,offset+2);
 rom.writeUInt16LE(0x4b00,offset+4);rom.writeUInt16LE(0x4718,offset+6);
 rom.writeUInt32LE(target|1,offset+8);
 return [{offset,size,name,expected}];
}
