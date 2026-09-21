/* Use the established local RomPatcher.js dependency for interoperable BPS. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const require=createRequire(import.meta.url);
const vendor=path.join(root,'tools/rom-patcher-source/marcrobledo-RomPatcher.js-3183884/rom-patcher-js');
globalThis.BinFile=require(path.join(vendor,'modules/BinFile.js'));
const patcher=require(path.join(vendor,'RomPatcher.js'));
const bin=b=>new BinFile(Uint8Array.from(b).buffer);
const [mode,sourcePath,inputPath,outputPath]=process.argv.slice(2);
assert(['create','apply'].includes(mode)&&sourcePath&&inputPath&&outputPath,'create/apply source input output required');
const source=fs.readFileSync(sourcePath),input=fs.readFileSync(inputPath);
let output;
if(mode==='create'){
  const create=()=>Buffer.from(patcher.createPatch(bin(source),bin(input),'bps').export('FFTA_Expansion')._u8array);
  output=create();assert.deepEqual(create(),output,'BPS is deterministic');
  const patch=patcher.parsePatchFile(bin(output));
  assert(patcher.validateRom(bin(source),patch),'Source accepted');
  assert.deepEqual(Buffer.from(patcher.applyPatch(bin(source),patch,{requireValidation:true})._u8array),input,'BPS roundtrip');
  const wrong=Buffer.from(source);wrong[0]^=1;
  assert.equal(patcher.validateRom(bin(wrong),patch),false,'Wrong source rejected');
}else{
  assert.equal(input.subarray(0,4).toString(),'BPS1','BPS header required');
  const patch=patcher.parsePatchFile(bin(input));
  assert(patcher.validateRom(bin(source),patch),'Wrong clean ROM for this patch');
  output=Buffer.from(patcher.applyPatch(bin(source),patch,{requireValidation:true})._u8array);
}
fs.writeFileSync(outputPath,output,{flag:'wx'});
