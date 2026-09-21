import fs from 'node:fs';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import {root,cleanROM,sha1} from '../src/rom-data.mjs';
const require=createRequire(import.meta.url),vendor=`${root}/tools/rom-patcher-source/marcrobledo-RomPatcher.js-3183884/rom-patcher-js`;
globalThis.BinFile=require(`${vendor}/modules/BinFile.js`);
const patcher=require(`${vendor}/RomPatcher.js`),original=cleanROM();
const target=fs.readFileSync(`${root}/build/foundation/FFTA_vanillaplus_dev.gba`);
for(const name of ['foundation-verification','arm-routines','menu-routines','emulator-smoke']){
  const report=JSON.parse(fs.readFileSync(`${root}/build/reports/${name}.json`));assert.equal(report.passed,true);
  assert.equal(report.romSha1??report.roms.find(x=>x.rom.includes('foundation')).sha1,sha1(target),`Stale test ${name}`);
}
const bin=b=>new BinFile(Uint8Array.from(b).buffer);
const sourceFile=bin(original),targetFile=bin(target);
const patch=patcher.createPatch(sourceFile,targetFile,'bps'),file=patch.export('FFTA_foundation_dev1');
const bytes=Buffer.from(file._u8array);const parsed=patcher.parsePatchFile(bin(bytes));
assert(patcher.validateRom(bin(original),parsed));
const rebuilt=patcher.applyPatch(bin(original),parsed,{requireValidation:true});
assert.deepEqual(Buffer.from(rebuilt._u8array),target,'BPS roundtrip mismatch');
const wrong=Buffer.from(original);wrong[0]^=1;
assert.equal(patcher.validateRom(bin(wrong),parsed),false,'Wrong base was accepted');
fs.mkdirSync(`${root}/patches/development`,{recursive:true});
fs.writeFileSync(`${root}/patches/development/FFTA_foundation_dev1.bps`,bytes);
const report={passed:true,romSha1:sha1(target),patchSha1:sha1(bytes),patchBytes:bytes.length,scope:'BPS applied back to clean US ROM produces exact target; corrupted source rejected. Experimental development patch, not the complete expansion.'};
fs.writeFileSync(`${root}/build/reports/patch-roundtrip.json`,JSON.stringify(report,null,2));console.log(JSON.stringify(report));
