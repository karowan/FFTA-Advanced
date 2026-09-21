import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8').replace(/\r\n/g,'\n');
const write=(f,s)=>fs.writeFileSync(path.join(root,f),s);
const data=JSON.parse(read('notes/job-theme-audit.json'));
if(data.version!=='0.6')throw new Error('Expected 0.6');
let spec=read('JOB-CLASS-SPECIFICATION.md');
const changes={
 'MYK-A12': ['0.85P using ordinary primary weapon element; on a successful hit remove one selected dispellable beneficial status even if HP damage is zero.', '0.85P using ordinary primary weapon element. Resolve A and applicable defensive interceptions first; on a successful hit remove one selected dispellable beneficial status if still present, then calculate HP damage using remaining defenses and resolved interception modifiers. Removal does not require positive HP damage. If an interception already consumed the selected status, do not select another or refund the action.'],
 'MYK-A13': ['Use the ordinary damaging-spell hit resolution per target and preview it; immunity and defensive effects remain applicable.', 'A per target under the shared accuracy rules; preview each target. Immunity and defensive effects remain applicable. A committed miss still establishes Magic; invalid actions spend neither MP nor enchantment and establish no category.'],
 'MYK-A14': ['Magic sequencing; Spellweave cannot improve Petrify chance.', 'Magic sequencing; Spellweave cannot improve Petrify chance. Ordinary legal accuracy supports retain their native eligibility and occupy the same single support slot; this is not a ban on accuracy support.']
};
for(const [id,[from,to]] of Object.entries(changes)){
 const a=data.abilities.find(x=>x.id===id);
 if(a.effect.includes(to))continue;
 if(!a.effect.includes(from))throw new Error('Missing expected text '+id);
 const old=a.effect;
 a.effect=old.replace(from,to);
 spec=spec.replace(old,a.effect);
}
write('JOB-CLASS-SPECIFICATION.md',spec);
write('notes/job-theme-audit.json',JSON.stringify(data,null,2)+'\n');
let expansion=read('SPELLBLADE-EXPANSION.md');
expansion=expansion.replace('Half MP and Clear Voice eligibility','Half MP eligibility (Clear Voice is Moogle-only and cannot be equipped by this Viera)');
if(!expansion.includes('## Council integration clarification')) expansion+='\n## Council integration clarification\n\nSpellbreak resolves its successful hit and applicable defensive interceptions, removes its selected status if still present, then calculates HP damage. A status already consumed by an interception gives no replacement target or refund. Release explicitly uses A per target, with Magic established only for a committed action. Break excludes a Spellweave accuracy bonus, not the ordinary effects of legal accuracy supports. These clarify the new provisional rows without changing their approved concepts or categories.\n\nThe reviewer also proposed making Spell Parry consume only against positive pending physical HP damage. That is a separate change to the previously adopted reaction and remains a candidate: current 0.6 still consumes after a successful eligible physical hit check, even if the eventual HP damage is zero. The canonical reaction row takes precedence over the reviewer recommendation.\n';
write('SPELLBLADE-EXPANSION.md',expansion);
let axe=read('AXE-SKILL-EXPANSION.md');
axe=axe.replace('Design version 0.5 — adopted council balance pass, September 14, 2026. Design only; no ROM patch applied.','Axe ability rules retain adopted version 0.5; global references updated for project version 0.6, September 14, 2026. Design only; no ROM patch applied.');
axe=axe.replaceAll('116 entries','122 entries').replaceAll('72 teaching items','78 teaching items').replaceAll('72 items','78 items');
write('AXE-SKILL-EXPANSION.md',axe);
console.log('Clarified new action resolution and current totals; retained original Spell Parry rule.');
