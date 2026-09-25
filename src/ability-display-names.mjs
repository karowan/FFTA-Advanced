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
  // Enchantments and Break work with any primary weapon ("Ench." for
  // enchant); Blade Combo remains rapier/saber-only.
  ['MYK-A1','Fire Ench.'],['MYK-A2','Blizzard Ench.'],['MYK-A3','Thunder Ench.'],
  ['MYK-A4','Poison Ench.'],['MYK-A5','Sleep Ench.'],['MYK-A6','Silence Ench.'],
  ['MYK-A7','Drain Ench.'],['MYK-A8','Flare Ench.'],['MYK-A9','Slow Ench.'],
  ['MYK-A10','Osmose Ench.'],['MYK-A11','Holy Ench.'],['MYK-A13','Arcane Burst'],
  ['MYK-A14','Break Ench.'],
  ['MYK-C1','Blade Combo'],['GLD-AX-S1','Followthrough'],
]);
export const abilityDisplayNames=compact;
export const abilityDisplayName=lesson=>compact.get(lesson.id)??lesson.name;
