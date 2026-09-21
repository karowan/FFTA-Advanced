import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8').replace(/\r\n/g,'\n');
const plan=JSON.parse(read('notes/equipment-acquisition.json'));
const current=JSON.parse(read('notes/job-theme-audit.json'));
const before=JSON.parse(read('notes/design-v0.7/job-theme-audit.json'));
const spec=read('JOB-CLASS-SPECIFICATION.md'),axe=read('AXE-SKILL-EXPANSION.md'),guide=read('WEAPON-ACQUISITION.md');
const errors=[];
const check=(ok,msg)=>{if(!ok)errors.push(msg);};
const aMap=new Map(current.abilities.map(a=>[a.id,a]));
check(JSON.stringify(current.abilities)===JSON.stringify(before.abilities),'Ability definitions changed during placement pass');
check(JSON.stringify(current.commandRules)===JSON.stringify(before.commandRules),'Command rules changed during placement pass');
check(plan.designVersion===current.version && plan.items.length===85,'Wrong design version/item count');
check(new Set(plan.items.map(i=>i.id)).size===85 && new Set(plan.items.map(i=>i.name)).size===85,'Duplicate item ID/name');
check(JSON.stringify(plan.stages.map(s=>s.missionRecord))===JSON.stringify([null,5,11,17]),'Wrong story gates');
check(current.equipmentPlan.path==='notes/equipment-acquisition.json','Equipment reference mismatch');
const stageIds=new Set(plan.stages.map(s=>s.id));
const seen=new Map();
const catalog=guide.slice(guide.indexOf('## Full teaching catalog'),guide.indexOf('## Medicine supply'));
const extraRows=spec.split('\n').filter(l=>/^\| [^|]+ \| (?:MYK|SAM|DRK|VIK|GEO|CHM|DNC)-A\d+ /.test(l)).map(l=>l.split('|').slice(1,-1).map(x=>x.trim()));
const allDeclaredNames=[];
const gearChapter=spec.slice(spec.indexOf('## 12. Teaching'),spec.indexOf('## 13. Implementation'));
for(const l of gearChapter.split('\n').filter(l=>/^\| (?:Samurai|Dark Knight|Viking|Geomancer|Chemist|Bard|Dancer|Mystic Knight) \/ /.test(l)))allDeclaredNames.push(...l.split('|').slice(2,-1).map(x=>x.trim()));
allDeclaredNames.push(...extraRows.map(r=>r[0]));
const axeRows=axe.slice(axe.indexOf('## Teaching axes'),axe.indexOf('## Learning')).split('\n').filter(l=>/^\| (?:Recruit|Throwing|Field|Breaching|Bearded|Arena|Headsman|Titan)/.test(l)).map(l=>l.split('|').slice(1,-1).map(x=>x.trim()));
allDeclaredNames.push(...axeRows.map(r=>r[0]));
check(allDeclaredNames.length===85 && allDeclaredNames.every(n=>plan.items.filter(i=>i.name===n).length===1),'Missing/orphan teaching weapon');
const shops=new Set(['Cyril','Sprohm','Cadoan','Baguba Port','Muscadet']);
for(const eq of plan.items){
 check(eq.primaryShop==='Cyril' && eq.additionalShops.every(s=>shops.has(s)&&s!=='Cyril'),'Invalid shop '+eq.name);
 check(stageIds.has(eq.stageId) && eq.stock==='Unlimited repeat purchases; never removed after stage unlock.','No persistent valid gate '+eq.name);
 check(Number.isInteger(eq.basePriceGil) && eq.basePriceGil>0 && Number.isInteger(eq.weaponAttack) && eq.weaponAttack>0,'Invalid price/power '+eq.name);
 check(eq.romItemId===null && eq.romShopRecord===null && eq.missionFlagAddress===null,'Unverified binary identifier '+eq.name);
 check(eq.lessons.length>0 && eq.lessons.filter(a=>a.type==='Action').length===1,'Expected one active lesson per weapon '+eq.name);
 const catalogRows=catalog.split('\n').filter(l=>l.startsWith('| '+eq.name+' |'));
 check(catalogRows.length===1,'Catalog row missing/duplicated '+eq.name);
 const fields=catalogRows[0]?.split('|').slice(1,-1).map(x=>x.trim());
 check(Number(fields?.[2])===eq.weaponAttack && Number(fields?.[3])===eq.magicPowerBonus && Number(fields?.[4]?.replaceAll(',',''))===eq.basePriceGil && fields?.[5]===eq.stageId,'Catalog stats/gate mismatch '+eq.name);
 for(const a of eq.lessons){
  const canonical=aMap.get(a.id);
  check(!!canonical && a.name===canonical.name && a.type===canonical.type && a.ap===canonical.ap,'Lesson mismatch '+a.id);
  check(a.id.replace(/-[ASRC]\d+$/,'')===eq.group,'Wrong teaching group '+a.id);
  check(catalogRows[0]?.includes(a.name+' ['+a.id+'; '+a.ap+' AP]'),'Missing printed lesson '+a.id);
  check(!seen.has(a.id),'Duplicate teacher '+a.id);seen.set(a.id,eq.id);
  check(plan.abilityIndex[a.id]===eq.id,'Reverse index mismatch '+a.id);
 }
 const special=extraRows.find(r=>r[0]===eq.name);
 if(special){
  check(eq.lessons.length===1 && special[1]===eq.lessons[0].id+' '+eq.lessons[0].name && Number(special[2])===eq.lessons[0].ap,'Special lesson mapping '+eq.name);
  check(Number(special[3])===eq.weaponAttack && Number(special[4])===eq.basePriceGil && special[5].startsWith(eq.stageId+' '),'Special stats/gate mismatch '+eq.name);
 }
 const ax=axeRows.find(r=>r[0]===eq.name);
 if(ax)check(Number(ax[1])===eq.weaponAttack && Number(ax[2].replace(/[^0-9]/g,''))===eq.basePriceGil,'Axe stats/price mismatch '+eq.name);
 check(eq.innateElement===null && eq.innateStatus===null && eq.weaponProc===null && eq.otherStatBonuses===0,'Unapproved innate bonus '+eq.name);
}
check(seen.size===129 && current.abilities.every(a=>seen.has(a.id)) && Object.keys(plan.abilityIndex).length===129,'Ability coverage incomplete');
const stageCounts=plan.stages.map(s=>plan.items.filter(i=>i.stageId===s.id).length);
check(JSON.stringify(stageCounts)===JSON.stringify([18,23,23,21]),'Wrong shipment sizes');
check(!/\bNaN\b|\bundefined\b/.test(guide),'Invalid rendered table values');
for(const match of guide.matchAll(/\]\(([^)]+)\)/g)){
 const p=match[1].split('#')[0];if(p&&!/^https?:/i.test(p))check(fs.existsSync(path.resolve(root,p)),'Broken catalog link '+p);
}
const result={designVersion:plan.designVersion,equipmentRevision:plan.revision,weapons:plan.items.length,lessons:seen.size,stageCounts,allAbilityDefinitionsAndCommandRulesPreserved:true,scope:'Document/ledger validation only; stock gates and ROM offsets not implemented.',errors,passed:errors.length===0};
fs.writeFileSync(path.join(root,'notes/equipment-validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));if(errors.length)process.exitCode=1;
