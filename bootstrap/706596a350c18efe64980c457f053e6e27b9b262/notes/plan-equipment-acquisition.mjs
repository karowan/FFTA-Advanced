import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8').replace(/\r\n/g,'\n');
const write=(f,s)=>fs.writeFileSync(path.join(root,f),s.endsWith('\n')?s:s+'\n');
const data=JSON.parse(read('notes/job-theme-audit.json'));
if(data.version!=='0.7'||data.equipmentPlan)throw new Error('One-time acquisition plan requires unlinked 0.7');
const docs=['JOB-CLASS-SPECIFICATION.md','AXE-SKILL-EXPANSION.md','SUPPORT-SKILL-DESIGN.md','JOB-DESIGN-PRINCIPLES.md','JOB-THEME-AUDIT.md','JOB-EXPANSION-DESIGN.md','START-HERE.md','STARTER-JOB-INSPIRATION.md','BALANCE-COUNCIL.md','SPELLBLADE-EXPANSION.md','ABILITY-EXPANSION-COUNCIL.md','notes/job-theme-audit.json','notes/design-validation.json','notes/validate-current-design.mjs'];
fs.mkdirSync(path.join(root,'notes/design-v0.7'),{recursive:true});
for(const f of docs)fs.copyFileSync(path.join(root,f),path.join(root,'notes/design-v0.7',path.basename(f)),fs.constants.COPYFILE_EXCL);
let spec=read('JOB-CLASS-SPECIFICATION.md'), axe=read('AXE-SKILL-EXPANSION.md');
const stages=[
 {id:'S0',name:'Opening stock',condition:'From the first normal opportunity to use the Cyril equipment shop after the opening clan introduction.',missionRecord:null,missionName:null,predicate:'normal_shop_access',legacyLabel:'Initial shop-tier stock'},
 {id:'S1',name:'First shipment',condition:'After successful completion of mission #005: Twisted Flow, on the next shop visit.',missionRecord:5,missionName:'Twisted Flow',predicate:'mission_completed(005)',legacyLabel:'First expansion'},
 {id:'S2',name:'Second shipment',condition:'After successful completion of mission #011: Pale Company, on the next shop visit.',missionRecord:11,missionName:'Pale Company',predicate:'mission_completed(011)',legacyLabel:'Second expansion'},
 {id:'S3',name:'Advanced shipment',condition:'After successful completion of mission #017: Desert Patrol, on the next shop visit.',missionRecord:17,missionName:'Desert Patrol',predicate:'mission_completed(017)',legacyLabel:'Last pre-final-story expansion'}
];
const shopMap={SAM:[],DRK:['Sprohm'],VIK:['Sprohm'],GEO:['Cadoan'],CHM:['Cadoan','Baguba Port'],BRD:['Baguba Port'],DNC:['Muscadet'],MYK:['Muscadet'],'SLD-AX':['Sprohm'],'GLD-AX':['Sprohm']};
const groupInfo={SAM:['Samurai','Katana',['Human']],DRK:['Dark Knight','Sword',['Human','Bangaa']],VIK:['Viking','Axe',['Bangaa']],GEO:['Geomancer','Rod',['Nu Mou']],CHM:['Chemist','Knife',['Nu Mou','Moogle']],BRD:['Bard','Instrument',['Moogle']],DNC:['Dancer','Rapier',['Viera']],MYK:['Mystic Knight','Saber',['Viera']],'SLD-AX':['Soldier','Axe',['Human']],'GLD-AX':['Gladiator','Axe',['Bangaa']]};
const priceSteps=[300,600,1000,1600,2400,3400,4800,6500];
const atkSteps={SAM:[18,22,26,30,34,38,42,46],DRK:[18,22,26,30,34,38,42,46],VIK:[18,22,26,30,34,38,42,46],MYK:[18,22,26,30,34,38,42,46],CHM:[14,17,20,23,26,29,32,35],DNC:[14,17,20,23,26,29,32,35],BRD:[12,15,18,21,24,27,30,33],GEO:[10,12,14,16,18,20,22,24]};
const abilities=new Map(data.abilities.map(a=>[a.id,a]));
const items=[];
function item(group,slot,name,atk,mp,price,stage,lessonIds,source){
 const [job,category,races]=groupInfo[group];
 for(const id of lessonIds)if(!abilities.has(id))throw new Error('Unknown lesson '+id);
 const teachingItemId='EQ-'+group+'-'+slot;
 items.push({id:teachingItemId,name,group,category,teachingJob:job,teachingRaces:races,weaponAttack:atk,magicPowerBonus:mp,otherStatBonuses:0,innateElement:null,innateStatus:null,weaponProc:null,basePriceGil:price,stageId:stage,primaryShop:'Cyril',additionalShops:shopMap[group],additionalShopCondition:'Same stage must be unlocked AND this town\'s ordinary shop must be usable.',stock:'Unlimited repeat purchases; never removed after stage unlock.',lessons:lessonIds.map(id=>{const a=abilities.get(id);return {id,name:a.name,type:a.type,ap:a.ap};}),sourceTable:source,romItemId:null,romShopRecord:null,missionFlagAddress:null});
}
const chapter=spec.slice(spec.indexOf('## 12. Teaching'),spec.indexOf('## 13. Implementation'));
for(const group of Object.keys(atkSteps)){
 const job=groupInfo[group][0];
 const line=chapter.split('\n').find(l=>l.startsWith('| '+job+' / '));
 const names=line.split('|').slice(2,-1).map(x=>x.trim());
 if(names.length!==8)throw new Error('Wrong base weapon list '+group);
 names.forEach((name,i)=>{
  const n=i+1, lessons=[group+'-A'+n];
  const extras={2:'S1',3:'C1',4:'R1',5:'S2',6:'R2'};
  if(extras[n])lessons.push(group+'-'+extras[n]);
  item(group,'W'+n,name,atkSteps[group][i],group==='GEO'?i*2:0,priceSteps[i],'S'+Math.floor(i/2),lessons,'JOB-CLASS-SPECIFICATION.md W'+n);
 });
}
const specialLines=chapter.split('\n').filter(l=>/^\| [^|]+ \| (?:MYK|SAM|DRK|VIK|GEO|CHM|DNC)-A\d+ /.test(l));
for(const line of specialLines){
 const [name,lesson,ap,atk,price,oldStage]=line.split('|').slice(1,-1).map(x=>x.trim());
 const id=lesson.split(' ')[0], group=id.split('-')[0], n=id.split('-A')[1];
 if(Number(ap)!==abilities.get(id).ap)throw new Error('AP mismatch '+id);
 const stage=stages.find(s=>s.legacyLabel===oldStage);
 if(!stage)throw new Error('Unknown stage '+oldStage);
 item(group,'W'+n,name,Number(atk),group==='GEO'?10:0,Number(price),stage.id,[id],'JOB-CLASS-SPECIFICATION.md additional teaching weapons');
}
const axeLessons=[['SLD-AX','W1',['SLD-AX-A1']],['SLD-AX','W2',['SLD-AX-A2','SLD-AX-S1']],['SLD-AX','W3',['SLD-AX-A3','SLD-AX-R1']],['SLD-AX','W4',['SLD-AX-A4']],['GLD-AX','W1',['GLD-AX-A1']],['GLD-AX','W2',['GLD-AX-A2','GLD-AX-S1']],['GLD-AX','W3',['GLD-AX-A3','GLD-AX-R1']],['GLD-AX','W4',['GLD-AX-A4']]];
const axeRows=axe.slice(axe.indexOf('## Teaching axes'),axe.indexOf('## Learning')).split('\n').filter(l=>/^\| (?:Recruit|Throwing|Field|Breaching|Bearded|Arena|Headsman|Titan)/.test(l));
axeRows.forEach((l,i)=>{const [name,atk,price]=l.split('|').slice(1,-1).map(x=>x.trim());const [group,slot,ids]=axeLessons[i];item(group,slot,name,Number(atk),0,Number(price.replace(' gil','').replaceAll(',','')),'S'+Math.floor(i/2),ids,'AXE-SKILL-EXPANSION.md teaching axes');});
if(items.length!==85)throw new Error('Expected 85 equipment records, got '+items.length);
const index={};for(const eq of items)for(const a of eq.lessons){if(index[a.id])throw new Error('Duplicate teacher '+a.id);index[a.id]=eq.id;}
if(Object.keys(index).length!==129)throw new Error('Expected 129 mapped lessons');
const plan={schemaVersion:1,designVersion:'0.7',revision:1,date:'2026-09-14',status:'Concrete acquisition design; not implemented or verified in a patched ROM.',scope:'All 85 new teaching weapons and all 129 adopted lessons, including support, reaction and combo lessons. Existing ability rules, AP, weapon names, powers and base prices are preserved.',stages,shopPolicy:{primary:'Cyril',additionalByGroup:shopMap,unlocks:'Custom additive mission-completion checks; not native shop-upgrade numbers, battle counts, turf counts, calendar dates or merely accepted missions.',persistence:'Once unlocked, new equipment stock stays available even if turf count drops. Normal shop access restrictions still apply.',randomSources:'No placement in generic mission rewards, random drops, treasure hunts, steals, link rewards, or missable unique caches in this revision. Shops are the guaranteed source.',newGame:'Opening stock begins only when normal equipment shopping is available, not during the snowball tutorial.',existingSave:'On shop visit compute availability from completed story records; catch-up access requires validated compatibility, not a fresh-only unlock event.',pricing:'Listed prices are base targets; retain applicable original town/category/clan adjustments after validating new item categories. Actual checkout price is previewed.'},implementationUnknowns:['ROM item IDs and free item capacity','Mission-completion flag addresses/bit masks','Shop record allocation and additive stock filtering','Town/category price mapping, UI capacity and save serialization','Patch and ordinary-save compatibility'],sources:{shop:['The Lost Gamer shop guide','https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26352'],gameplay:['Crono09 gameplay guide','https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/62342'],missions:['GameSpot walkthrough and numbered mission list','https://www.gamespot.com/articles/final-fantasy-tactics-advance-walkthrough/1100-6072833/'],progression:['Thonky campaign walkthrough','https://www.thonky.com/tactics-advance/walkthrough']},items,abilityIndex:index};
write('notes/equipment-acquisition.json',JSON.stringify(plan,null,2));
data.equipmentPlan={path:'notes/equipment-acquisition.json',document:'WEAPON-ACQUISITION.md',revision:1};
write('notes/job-theme-audit.json',JSON.stringify(data,null,2));
const stageCounts=stages.map(s=>items.filter(i=>i.stageId===s.id).length);
const lessonText=eq=>eq.lessons.map(a=>`${a.name} [${a.id}; ${a.ap} AP]`).join('; ');
const shopText=eq=>[eq.primaryShop,...eq.additionalShops].join(' / ');
let md=`# Teaching weapons and acquisition

Design 0.7, equipment plan revision 1 — September 14, 2026. **Every one of the 129 adopted abilities has a named teaching weapon and a repeatable acquisition route.** This ledger covers all 85 new weapons, including their support, reaction and combo lessons. It preserves current names, AP, stats, and base prices. The placements are our mod design, not claims about items already present in vanilla or an applied patch.

## Where and when

**Cyril is the guaranteed purchase location for every unlocked teaching weapon.** Sprohm additionally carries Dark Knight/Viking/Soldier/Gladiator equipment; Cadoan carries Geomancer/Chemist; Baguba Port carries Bard/Chemist; Muscadet carries Dancer/Mystic Knight. Secondary stock appears only when both the shipment condition and that town's normal shop access permit it. Samurai is stocked in Cyril. A map symbol becoming placeable does not itself promise an immediately usable shop.

All stock is repeatably purchasable and cumulative. No new teaching item is exclusive to a mission reward, random roll, enemy steal, link feature, or one-time cache. This revision adds shop stock only; original mission rewards and loot pools remain. Earlier weapons stay available after later shipments and after turf loss. No completed job or mastered ability is required to buy gear, but only its listed teaching job/race can learn from it.

| Shipment | Exact unlock in our mod | New weapons | Total unlocked | Earlier placeholder replaced |
|---|---|---:|---:|---|
${stages.map((s,i)=>`| ${s.id} — ${s.name} | ${s.condition} | ${stageCounts[i]} | ${stageCounts.slice(0,i+1).reduce((a,b)=>a+b,0)} | ${s.legacyLabel} |`).join('\n')}

These are **new mission-based stock gates**, not vanilla shop upgrade numbers. The three mission names and record numbers follow the [numbered mission list](${plan.sources.missions[1]}). Their campaign order is independently described in [the walkthrough](${plan.sources.progression[1]}). Shop availability is evaluated after successful completion, not mission acceptance or merely entering the battle. No calendar date or assumed character level is involved. All four shipments unlock before the final story sequence.

Vanilla uses battle-count upgrades first (10/20 completed battles in the gameplay guide), then area-control requirements for selected town stock; losing areas can remove that native stock. Our added weapons use the separate persistent story gates above, while existing merchandise keeps its ordinary rules. [Gameplay reference](${plan.sources.gameplay[1]}).

## The seven most recent additions

| Ability | Teaching weapon | AP | Base gil | Shipment | Shops |
|---|---|---:|---:|---|---|
${items.filter(i=>i.lessons.some(a=>abilities.get(a.id).introducedVersion==='0.7')).map(i=>`| ${i.lessons[0].name} | ${i.name} | ${i.lessons[0].ap} | ${i.basePriceGil.toLocaleString('en-US')} | ${i.stageId} | ${shopText(i)} |`).join('\n')}

## Full teaching catalog

Rows list every lesson, including support/reaction/combo lessons that share an item. Ability IDs provide exact lookup into [the class specification](JOB-CLASS-SPECIFICATION.md) or [axe addendum](AXE-SKILL-EXPANSION.md). Lesson ownership is not equipment permission: equipping another job's weapon never grants its unmastered lessons. A shared Dark Knight or Chemist lesson applies to both approved races with the same AP; it is not counted twice.

Prices are base targets in gil; the game must display applicable native town/category/clan adjustments. No new weapon has an innate element, status proc or unlisted stat bonus. Rod MPow bonuses below are equipment Magic Power, not MP restoration. New axes are two-handed and exclude shields/second weapons; other weapons retain their existing family handedness.
`;
for(const [group,[job,category,races]] of Object.entries(groupInfo)){
 const groupItems=items.filter(i=>i.group===group).sort((a,b)=>Number(a.id.match(/W(\d+)$/)[1])-Number(b.id.match(/W(\d+)$/)[1]));
 md+=`\n### ${job} — ${races.join(' / ')} — ${category}\n\nShops: ${[...new Set(groupItems.flatMap(i=>[i.primaryShop,...i.additionalShops]))].join(', ')}. Additional towns retain normal access requirements.\n\n| Weapon | Every lesson and AP | WAtk | MPow + | Base gil | Shipment |\n|---|---|---:|---:|---:|---|\n`;
 md+=groupItems.map(i=>`| ${i.name} | ${lessonText(i)} | ${i.weaponAttack} | ${i.magicPowerBonus} | ${i.basePriceGil.toLocaleString('en-US')} | ${i.stageId} |`).join('\n')+'\n';
}
md+=`\n## Medicine supply is a separate condition\n\nLearning a recipe and owning its ingredients are different requirements. The weapon gates do not add new consumable stock or waive ingredient payment.\n\n| Lesson / preparation | Teaching access | Ingredient route / condition |\n|---|---|---|\n| Field Remedy / ordinary healing / Healing Mist / Guarding Draught | Their catalog shipment | Potion, Hi-Potion, Soft and the named basic cures are listed in ordinary initial shop stock. Use owned supplies and native prices. |\n| High Tonic / Resuscitating Draught | S1 / S3 | X-Potion and Phoenix Down are also listed as initial stock; learning the advanced recipe does not promise free or cheap ingredients. |\n| Cureall / Inoculation | S3 | Baguba Port's ordinary Cureall stock additionally requires 10 currently controlled/freed areas and an accessible shop. Losing areas can remove that consumable stock. Any legitimately obtained existing Cureall can still be used. |\n| Ether | S2, Ether Knife | The knife teaches the action, not an Ether supply. Ether is absent from the ordinary shop catalog checked here; no shop route or new Ether stock is invented. Use legitimately acquired vanilla inventory; a guaranteed mission-specific Ether route remains unverified. |\n\nThe basic consumable listings come from [the shop catalog](${plan.sources.shop[1]}); Baguba Port's 10-area Cureall condition and possible loss of turf-based stock are documented in [the gameplay guide](${plan.sources.gameplay[1]}). This matters particularly to Inoculation: S3 unlocks its teaching weapon even when the clan has not met the independent Cureall supply condition.\n\n## Design decisions and remaining implementation work\n\nThe ledger fixes which item teaches every lesson, where it is sold, its exact design unlock, and its base-price/stat target. It deliberately does not fabricate ROM item IDs, free-record capacity, shop record numbers or mission-bit addresses. UI mission record numbers are semantic identifiers, not ROM offsets. [Structured equipment ledger](notes/equipment-acquisition.json).\n\nImplementation must append stock without replacing original merchandise; resolve the actual completed-record flags; validate Cyril and secondary shop access; keep new stock persistent independently of native turf upgrades; prevent these new item IDs entering generic reward/steal/treasure tables ahead of their gates; preserve existing mission rewards; and support ordinary save serialization. On loading a compatible progressed save, recompute gates from completed records so previously cleared missions need not be replayed. Save compatibility itself is not yet proven.\n\nTest each gate immediately before/after success, after mission acceptance/failure, after unrelated battles, after turf gain/loss, in each named shop, and after save/load. Verify all 85 item records, all 129 unique lesson links, equipment eligibility for every teaching race, simultaneous AP learning, ownership after job changes, displayed prices, actual stock persistence and menu capacity. Repeat purchases must remain possible after selling a copy. A story gate is not an excuse to raise weapon power or alter ability AP.\n\nThe former broad shipment labels in older council reports are historical; S0–S3 here own current acquisition timing. No ROM has been changed by this planning work.\n`;
write('WEAPON-ACQUISITION.md',md);
spec=spec.replace('## 12. Teaching equipment and availability','## 12. Teaching equipment and availability\n\n**Exact acquisition plan:** [Every weapon, all lessons, and shop locations](WEAPON-ACQUISITION.md) and [structured ledger](notes/equipment-acquisition.json). Cyril carries every unlocked item; additional town stock follows the ledger. Opening stock is S0; clear #005 Twisted Flow for S1, #011 Pale Company for S2, and #017 Desert Patrol for S3. These are additive mod gates, separate from native shop upgrades.');
spec=spec.replace('W1–2 are initial shop-tier stock; W3–4 first expansion; W5–6 second; W7–8 last pre-final-story expansion. These anchors require real story-flag mapping.','W1–2 use S0 (opening stock); W3–4 use S1 (clear #005 Twisted Flow); W5–6 use S2 (clear #011 Pale Company); W7–8 use S3 (clear #017 Desert Patrol). The acquisition ledger fixes design gates; their ROM flag addresses and shop record allocation remain to be verified.');
spec=spec.replace('Story-flag mapping and item-record capacity remain unverified.','Exact design gates are fixed in the acquisition ledger; ROM flag mapping and item-record capacity remain unverified.');
spec=spec.replace('Match actual story flags and confirm item-record capacity. These prices, AP and shop placements are provisional targets;','Use the acquisition ledger\'s exact S0–S3 gates, then verify their actual story flags and item-record capacity. Prices and AP remain tuning targets;');
// Replace labels only inside the extra-teaching rows, not historical prose.
spec=spec.split('\n').map(l=>{
 if(!/^\| [^|]+ \| (?:MYK|SAM|DRK|VIK|GEO|CHM|DNC)-A\d+ /.test(l))return l;
 for(const s of stages)l=l.replace(' | '+s.legacyLabel+' |',' | '+s.id+' — '+(s.missionName?'clear #'+String(s.missionRecord).padStart(3,'0')+' '+s.missionName:'opening stock')+' |');
 return l;
}).join('\n');
write('JOB-CLASS-SPECIFICATION.md',spec);
axe=axe.replace('Release the first pair in initial shops, then subsequent pairs at ordinary shop expansions, all before the final story stretch and repeatably obtainable. Actual flags need mapping. Viking has eight separate teaching axes in the main specification; sharing the weapon family grants no cross-job lesson access.','Acquire every listed axe in Cyril, with matching stock in Sprohm when usable. Recruit/Throwing use S0 (opening stock); Field/Breaching use S1 (clear #005 Twisted Flow); Bearded/Arena use S2 (clear #011 Pale Company); Headsman\'s/Titan use S3 (clear #017 Desert Patrol). Stock is permanent and repeatably purchasable. These are our added stock gates, not native shop upgrades; ROM flags still require verification. Viking has nine separate teaching axes in the main specification. See [the complete acquisition ledger](WEAPON-ACQUISITION.md) for every weapon and lesson; sharing the family grants no cross-job lesson access.');write('AXE-SKILL-EXPANSION.md',axe);
write('START-HERE.md',read('START-HERE.md')+'\nThe [weapon acquisition guide](WEAPON-ACQUISITION.md) maps all 129 lessons to 85 weapons with base prices, permanent shop locations, and exact opening/#005/#011/#017 story gates. Those planned items are not installed in the vanilla ROM yet.\n');
write('JOB-EXPANSION-DESIGN.md',read('JOB-EXPANSION-DESIGN.md')+'\n## Equipment access\n\n[The complete weapon ledger](WEAPON-ACQUISITION.md) gives each lesson a named item and each item a repeatable shop route. Cyril carries all unlocked teaching equipment; regional shops carry the specified additional stock. Four permanent shipments use opening access and completed story records #005, #011, and #017. These gates do not change any job prerequisite and are distinct from the vanilla battle/turf shop upgrades.\n');
write('JOB-DESIGN-PRINCIPLES.md',read('JOB-DESIGN-PRINCIPLES.md')+'\n## Equipment acquisition revision 1\n\nEvery teaching lesson must have a repeatable acquisition route. The [weapon ledger](WEAPON-ACQUISITION.md) binds all 129 lessons to the existing 85 planned items, with Cyril access plus appropriate regional stock. Opening/#005/#011/#017 stock is permanent and independent of turf loss or battle grinding. No exclusive random drops, single-copy rewards or new consumable stock are introduced by this plan. Ability rules, AP, growths and job gates are unchanged.\n');
console.log(JSON.stringify({weapons:items.length,lessons:Object.keys(index).length,stageCounts,primaryShop:'Cyril',implemented:false},null,2));
