import fs from 'node:fs';
import {cleanROM,missions,itemName,root} from '../src/rom-data.mjs';
const b=cleanROM(),ms=missions(b);
fs.mkdirSync(root+'/build/reports',{recursive:true});
fs.writeFileSync(root+'/build/reports/vanilla-missions.json',JSON.stringify(ms,null,2));
for(const m of ms.filter(m=>/Dragon's Aid|Caravan Guard|Mythril Rush|Missing Prof|Tricky Spirits|Wild Monsters|Pale Company|Desert Patrol|Twisted Flow/.test(m.name))) console.log({...m,rewardNames:m.rewards.map(i=>itemName(b,i)),requiredNames:m.required.map(i=>i?itemName(b,i+0x177):'none')});
console.log('Items',Array.from({length:490},(_,i)=>({id:i,name:itemName(b,i)})).filter(i=>/Wyrmstone|Elda|Materia Blade|Zeus|Dark Gear|Genji Armor/.test(i.name)));
console.log('Free space',b.length,[...new Set(b.subarray(0xa39920))]);
