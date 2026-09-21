import fs from 'node:fs';
import path from 'node:path';
import {root} from '../src/rom-data.mjs';
const stages=['ability-core','command-core','job-ui','axe-visual','command-label','combo','combat'];
const spans=stages.flatMap(stage=>JSON.parse(fs.readFileSync(path.join(root,`build/expansion/probes/${stage}.json`))).changes
  .filter(c=>c.name?.startsWith('ffta_') && c.size>=8).map(c=>({...c,stage})));
const failures=[];let checks=0;
for(const file of fs.readdirSync(path.join(root,'src/engine')).filter(f=>f.endsWith('.s'))) {
  const source=fs.readFileSync(path.join(root,'src/engine',file),'utf8');
  for(const match of source.matchAll(/\b(?:ap_tail|combo_tail|rider_tail|tail)\s+(0x[0-9a-f]+)/gi)) {
    const address=(Number(match[1])&~1)-0x08000000;
    for(const span of spans) {
      ++checks;
      if(address>span.offset && address<span.offset+span.size)
        failures.push({file,target:match[1],hook:span.name,stage:span.stage});
    }
  }
}
if(failures.length)throw Error('Continuation enters displaced native bytes: '+JSON.stringify(failures));
console.log(`Validated ${checks} explicit continuation/hook-span pairs`);
