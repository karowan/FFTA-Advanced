// A setup-only ROM creates native saves; the lab itself runs the unchanged development ROM.
import fs from 'node:fs';
import path from 'node:path';
import {root,sha1} from '../src/rom-data.mjs';
const out=path.join(root,'build/test-lab'),engine=path.join(root,'build/foundation/engine');
fs.mkdirSync(out,{recursive:true});
const rom=fs.readFileSync(path.join(root,'build/foundation/FFTA_vanillaplus_dev.gba'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'build/foundation/manifest.json')));
if(sha1(rom)!==manifest.outputSha1)throw Error('Development ROM does not match build manifest');
fs.writeFileSync(path.join(out,'setup-only.gba'),rom);
const master=fs.readFileSync(path.join(engine,'_MasterHackInstaller.event'),'utf8');
const start=master.indexOf('PUSH; ORG $43E28'),end=master.indexOf('#endif',start);
if(start<0||end<0)throw Error('Upstream quick-start block not found');
let block=master.slice(start,end).replaceAll('"ASM/',`"${engine.replaceAll('\\','/')}/ASM/`);
fs.writeFileSync(path.join(out,'setup-only.event'),`#include "Extensions/Hack Installation.txt"\nORG 0x1010000\n#define mcNameScreenCharacter 0x02\n#define clanNameScreenCharacter 0x08\n${block}\n`);
console.log('Prepared disposable test-save generator. Development ROM unchanged.');
