/* Isolated Exposed layer. Lifecycle is default; application/incoming are
 * explicit opt-ins. This helper alone never enables431 action availability. */
export function patchExposedEffects(rom,symbols,{application=false,incoming=false}={}) {
 const changes=[];
 const hooks=[
  [0x93022,'006882214900401801783420','ffta_exposed_turn_entry'],
  [0x95214,'0648182105f09afb05499431','ffta_exposed_battle_end_entry'],
  [0x97298,'10b5041c002136f03dfd201c','ffta_exposed_reset_entry'],
  [0x1230f2,'a178002903d1286801832868','ffta_exposed_event_ko_entry'],
  [0xcddd0,'00b50906021ce83241235b42','ffta_exposed_petrify_entry'],
  [0xcd884,'10b509041206cb0ce833c418','ffta_exposed_status_entry'],
  [0xc8c3c,'e671207ab04200d127726079','ffta_exposed_job_entry']
 ];
 if(application)hooks.push([0xa45c6,'041b002c00dacce11d9908688483','ffta_exposed_paid_entry']);
 if(incoming)hooks.push(
  [0x131b4a,'041c01f01cff4443fdf701fc','ffta_exposed_stage_entry'],
  [0x130200,'f0b5474680b483b0061c8846','ffta_exposed_preview_entry'],
  [0x130454,'f0b584b0051c0e1c171c00f003fa','ffta_exposed_combo_entry']
 );
 for(const [offset,expected,name] of hooks) {
  const bytes=Buffer.from(expected,'hex');
  if(!rom.subarray(offset,offset+bytes.length).equals(bytes))throw Error(`Exposed lifecycle conflict ${offset.toString(16)}`);
  if(!symbols[name])throw Error(`Missing ${name}`);
  for(let p=offset;p<offset+bytes.length;p+=2)rom.writeUInt16LE(0x46c0,p);
  rom.writeUInt16LE(0xb408,offset);const jump=(offset+5)&~3;
  if(jump+8>offset+bytes.length)throw Error('Exposed span too small');
  rom.writeUInt16LE(0x4b00,jump);rom.writeUInt16LE(0x4718,jump+2);rom.writeUInt32LE(symbols[name]|1,jump+4);
  changes.push({offset,bytes:bytes.length,name});
 }
 // Both native broad-remedy families use no-op callbacks: ordinary cures
 // are applied by13388C afterward. Preserve all native masks and admission.
 for(const [effect,original] of [[11,0x08131eed],[79,0x0813353d]]) {
  const offset=0x3a87b0+effect*12;
  if(rom.readUInt32LE(offset)!==original)throw Error('Native broad-remedy callback changed');
  if(!symbols.ffta_exposed_cureall_entry)throw Error('Missing broad-remedy entry');
  rom.writeUInt32LE(symbols.ffta_exposed_cureall_entry|1,offset);
  changes.push({offset,bytes:4,name:'ffta_exposed_cureall_entry'});
 }
 return changes;
}
