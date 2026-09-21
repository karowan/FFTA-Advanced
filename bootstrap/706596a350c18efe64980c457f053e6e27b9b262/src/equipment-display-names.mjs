// Native equipment lists have an eleven-tile name column. Full approved names
// remain in the design registry and equipment descriptions.
const compact=new Map([
  [379,'Mura. Echo'],[381,'Guard Blade'],[398,'Thunder Axe'],
  [409,'RemedyKnife'],[411,'HiTonic Knf'],[415,'ReviveKnife'],
  [436,'Ward Rod'],[440,'Time Saber'],[443,'Sever Saber'],
  [446,'Red Spider'],[447,'Nightward'],[448,'Challenger'],
  [450,'Preventive'],[451,'Fortifying'],[459,'Headsman'],
]);
export const equipmentDisplayName=item=>compact.get(item.romItemId)??item.name;
