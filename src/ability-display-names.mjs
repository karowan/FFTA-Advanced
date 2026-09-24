// Native learned-ability names fit eleven tiles, the longest original name.
// Full approved names remain in the design registry and ability help text.
const compact=new Map([
  ['SAM-A7','Kikuichimonji'],['SAM-C1','Moon Combo'],
  ['DRK-A2','Sanguine Cut'],['DRK-A8','Unholy Rite'],['DRK-A9','Black Night'],['DRK-R2','Vengeance'],
  ['VIK-R1','Absorb Harm'],['VIK-C1','Storm Combo'],
  ['GEO-A9','Nature Haven'],['GEO-R2','Nature Wrath'],
  ['CHM-A8','Resuscitate'],['CHM-A10','Guard Tonic'],
  ['BRD-A3','Refrain'],['BRD-S1','Encourage'],
  ['DNC-A1','Minuet'],['DNC-A6','Taboo Dance'],['DNC-R2','Counter Rhy.'],
  ['MYK-A1','Fire Blade'],['MYK-A2','Blizzard Blade'],['MYK-A3','Thunder Blade'],
  ['MYK-A4','Poison Blade'],['MYK-A5','Sleep Blade'],['MYK-A6','Silence Blade'],
  ['MYK-A7','Drain Blade'],['MYK-A8','Flare Blade'],['MYK-A9','Slow Blade'],
  ['MYK-A10','Osmose Blade'],['MYK-A11','Holy Blade'],['MYK-A13','Arcane Burst'],
  ['MYK-C1','Blade Combo'],['GLD-AX-S1','Followthrough'],
]);
export const abilityDisplayNames=compact;
export const abilityDisplayName=lesson=>compact.get(lesson.id)??lesson.name;
