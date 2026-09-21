// Test-only intro bypass. Never incorporated into the playable foundation artifact.
import fs from 'node:fs';
import path from 'node:path';
import {root} from '../src/rom-data.mjs';
const qa=path.join(root,'build/test'),engine=path.join(root,'build/foundation/engine');
fs.copyFileSync(path.join(root,'build/foundation/FFTA_vanillaplus_dev.gba'),path.join(qa,'fixture.gba'));
const master=fs.readFileSync(path.join(engine,'_MasterHackInstaller.event'),'utf8');
let block=master.slice(master.indexOf('PUSH; ORG $43E28'),master.indexOf('#endif',master.indexOf('PUSH; ORG $43E28')));
block=block.replaceAll('"ASM/',`"${engine.replaceAll('\\','/')}/ASM/`);
fs.writeFileSync(path.join(qa,'fixture.event'),`#include "Extensions/Hack Installation.txt"\nORG 0x1010000\n#define mcNameScreenCharacter 0x02\n#define clanNameScreenCharacter 0x08\n${block}\n`);
