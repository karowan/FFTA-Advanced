// Weapon Attack revision, September 24, 2026. Each shipment is anchored to
// the original ordinary shop weapons of the same family: S0 opening tier, S1
// first upgrade, S2 second upgrade, S3 four above that. Within a shipment the
// price ladder sets the position. Values never decrease; Magic Power, prices,
// gates and lessons are unchanged. Run with --check to verify without writing.
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
const check=process.argv.includes('--check');
const clean=fs.readFileSync(path.join(root,'roms/clean/FFTA_US_clean.gba'));
const vanilla=JSON.parse(read('build/reports/vanilla-teaching-sources.json'));
// Native item category IDs. Axes compare with two-handed Greatswords and
// Broadswords, plus two for giving up a shield or second weapon.
const families={Sword:[1],Saber:[3],Knife:[7],Rapier:[8],Katana:[9],Rod:[11],Instrument:[16],Axe:[5,6]};
const shop=(cats,tier)=>vanilla.rows.filter(r=>r.id<=375&&cats.includes(clean[0x51d180+r.id*32+8])
  &&r.ordinaryTiers.length&&Math.min(...r.ordinaryTiers)<=tier).map(r=>clean[0x51d180+r.id*32+16]);
const plan=JSON.parse(read('notes/equipment-acquisition.json'));
const table=new Map(),anchors={};
for(const [family,cats] of Object.entries(families)){
  const tiers=[0,1,2].map(t=>shop(cats,t)),first=tiers.find(t=>t.length);
  const bonus=family==='Axe'?2:0;
  const high=[tiers[0].length?Math.max(...tiers[0]):Math.min(...first),Math.max(...tiers[1]),Math.max(...tiers[2])];
  for(let s=1;s<3;s++)high[s]=Math.max(high[s],high[s-1]+2);
  high.push(high[2]+4);
  const top=high.map(x=>x+bonus),low=(tiers[0].length?Math.min(...tiers[0]):Math.min(...first)-2)+bonus;
  anchors[family]={opening:low,shipments:top};
  for(let s=0;s<4;s++){
    const items=plan.items.filter(i=>i.category===family&&i.stageId==='S'+s);
    const prices=[...new Set(items.map(i=>i.basePriceGil))].sort((a,b)=>a-b),m=prices.length;
    for(const item of items){
      const j=prices.indexOf(item.basePriceGil);
      const target=s===0?low+(top[0]-low)*(m===1?0:j/(m-1))/2:top[s-1]+(top[s]-top[s-1])*(j+1)/m;
      const old=item.previousWeaponAttack??item.weaponAttack;
      table.set(item.name,{old,value:Math.max(old,Math.round(target))});
    }
  }
}
if(table.size!==85)throw Error('Expected 85 weapons');
const rows=[];let changed=0;
for(const item of plan.items){
  const {old,value}=table.get(item.name);rows.push({name:item.name,category:item.category,stage:item.stageId,old,value});
  if(item.weaponAttack!==value){item.weaponAttack=value;changed++;}
  if(old!==value)item.previousWeaponAttack=old;
}
plan.weaponAttackRevision={date:'2026-09-24',script:'notes/revise-weapon-attack-2026-09-24.mjs',anchors};
// Markdown copies checked by notes/validate-equipment-plan.mjs.
const replaceColumn=(text,matcher,column)=>text.split('\n').map(line=>{
  if(!line.startsWith('| '))return line;
  const cells=line.split('|');const name=cells[1].trim();
  if(!table.has(name)||!matcher(line))return line;
  const value=String(table.get(name).value),current=cells[column].trim();
  if(!/^\d+$/.test(current))throw Error('Unexpected Weapon Attack cell '+name);
  cells[column]=cells[column].replace(current,value);return cells.join('|');
}).join('\n');
const docs={
  'WEAPON-ACQUISITION.md':t=>replaceColumn(t,l=>/\[[A-Z-]+-[ASRC]\d+; \d+ AP\]/.test(l),3),
  'AXE-SKILL-EXPANSION.md':t=>replaceColumn(t,l=>/ gil \|/.test(l),2),
  'JOB-CLASS-SPECIFICATION.md':t=>replaceColumn(t,l=>/^\| [^|]+ \| (?:MYK|SAM|DRK|VIK|GEO|CHM|DNC)-A\d+ /.test(l),4)
    .replace(/Weapon Attack targets, W1–W8: [^\n]*?Magic Power bonuses 0\/2\/4\/6\/8\/10\/12\/14\./,
      'Weapon Attack follows the September 24, 2026 revision in [the acquisition ledger](WEAPON-ACQUISITION.md): each shipment matches the original shop weapons of the same family available at about that time. Geomancer rods keep Magic Power bonuses 0/2/4/6/8/10/12/14.'),
};
const outputs={'notes/equipment-acquisition.json':JSON.stringify(plan,null,2)+'\n'};
for(const [file,edit] of Object.entries(docs))outputs[file]=edit(read(file));
for(const [file,text] of Object.entries(outputs)){
  if(check){if(read(file).replace(/\r\n/g,'\n')!==text.replace(/\r\n/g,'\n'))throw Error('Revision not applied: '+file);}
  else fs.writeFileSync(path.join(root,file),text);
}
console.log(JSON.stringify({status:check?'verified':'applied',changed:rows.filter(r=>r.old!==r.value).length,anchors,rows}));
