import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
const data=JSON.parse(read('notes/equipment-acquisition.json'));
let doc=read('WEAPON-ACQUISITION.md');
for(const eq of data.items.filter(i=>i.group.endsWith('-AX'))){
 const line=read('AXE-SKILL-EXPANSION.md').split('\n').find(l=>l.startsWith('| '+eq.name+' |'));
 eq.basePriceGil=Number(line.split('|')[3].trim().replace(' gil','').replaceAll(',',''));
 if(!Number.isInteger(eq.basePriceGil)||eq.basePriceGil<=0)throw new Error('Invalid price '+eq.name);
 doc=doc.split('\n').map(l=>l.startsWith('| '+eq.name+' |')?l.replace(' | NaN |',' | '+eq.basePriceGil.toLocaleString('en-US')+' |'):l).join('\n');
}
fs.writeFileSync(path.join(root,'notes/equipment-acquisition.json'),JSON.stringify(data,null,2)+'\n');
fs.writeFileSync(path.join(root,'WEAPON-ACQUISITION.md'),doc);
