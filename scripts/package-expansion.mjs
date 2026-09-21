/* Deterministic private delivery. Never reads or writes any save. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const hash=(b,algorithm='sha256')=>crypto.createHash(algorithm).update(b).digest('hex');
const read=n=>fs.readFileSync(path.join(root,n));
const expected='1b070824a8dad4995434eee3ab40fa08187a6120';
function protectedFiles(){
  const items={};
  function walk(name){
    const p=path.join(root,name);if(!fs.existsSync(p))return;
    const info=fs.lstatSync(p);assert(!info.isSymbolicLink(),'Linked player path: '+p);
    if(info.isDirectory())for(const entry of fs.readdirSync(p))walk(name+'/'+entry);
    else if(/\.(gba|sav|srm|state|ss[0-9])$/i.test(name) &&
      name!=='roms/play/expansion-v0.7/FFTA_Expansion_v0.7.gba')items[name]=hash(read(name));
  }
  for(const dir of ['roms/play','saves','build/foundation'])walk(dir);
  for(const name of ['Play FFTA.cmd','Play Development Build.cmd'])items[name]=hash(read(name));
  return items;
}
const preserved=protectedFiles();
const meta=JSON.parse(read('build/expansion/probes/integrated-jobs/current.json'));
const source=read('roms/clean/FFTA_US_clean.gba'),target=fs.readFileSync(meta.path);
assert.equal(hash(source,'sha1'),'4ac05441f4de70a4ec3dd932116346c61b8783d9');
assert.equal(hash(target,'sha1'),expected); assert.equal(meta.romSha1,expected);
const acceptance=JSON.parse(read('build/release-acceptance.json'));
assert.equal(acceptance.passed,true); assert.equal(acceptance.romSha256,hash(target));
for(const [name,digest] of Object.entries({...acceptance.shippingSources,
  ...acceptance.reusedEvidenceNotes,...acceptance.frozenReportsAndLogs}))
  assert.equal(hash(read(name)),digest,'Changed accepted source/evidence: '+name);
const require=createRequire(import.meta.url);
const vendor='tools/rom-patcher-source/marcrobledo-RomPatcher.js-3183884/rom-patcher-js';
globalThis.BinFile=require(path.join(root,vendor,'modules/BinFile.js'));
const patcher=require(path.join(root,vendor,'RomPatcher.js'));
const bin=b=>new BinFile(Uint8Array.from(b).buffer);
const patch=patcher.createPatch(bin(source),bin(target),'bps');
const bytes=Buffer.from(patch.export('FFTA_Expansion_v0.7')._u8array);
const parsed=patcher.parsePatchFile(bin(bytes));
assert(patcher.validateRom(bin(source),parsed),'Clean source rejected');
const rebuilt=patcher.applyPatch(bin(source),parsed,{requireValidation:true});
assert.deepEqual(Buffer.from(rebuilt._u8array),target,'Patch roundtrip mismatch');
const wrong=Buffer.from(source);wrong[0]^=1;
assert.equal(patcher.validateRom(bin(wrong),parsed),false,'Wrong source accepted');
const second=Buffer.from(patcher.createPatch(bin(source),bin(target),'bps').export('FFTA_Expansion_v0.7')._u8array);
assert.deepEqual(second,bytes,'Patch generation is not deterministic');
function safe(name){
  const output=path.resolve(root,name);
  assert(output.startsWith(root+path.sep),'Output escaped workspace');
  for(let p=output;p!==root;p=path.dirname(p))
    if(fs.existsSync(p))assert(!fs.lstatSync(p).isSymbolicLink(),'Linked output: '+p);
  return output;
}
function immutable(name,bytes){
  const output=safe(name);fs.mkdirSync(path.dirname(output),{recursive:true});
  if(fs.existsSync(output))assert.deepEqual(fs.readFileSync(output),bytes,'Existing delivery differs: '+name);
  else fs.writeFileSync(output,bytes,{flag:'wx'});
}
const folder='build/releases/v0.7';
const romPath='roms/play/expansion-v0.7/FFTA_Expansion_v0.7.gba';
immutable(folder+'/FFTA_Expansion_v0.7.bps',bytes);
immutable(romPath,target);
const documents=['EXPANSION-PLAYER-GUIDE.md','JOB-CLASS-SPECIFICATION.md',
  'WEAPON-ACQUISITION.md','AXE-SKILL-EXPANSION.md','REPRODUCIBLE-BUILD.md'];
for(const name of documents)immutable(folder+'/'+name,read(name));
const tools={};
for(const name of ['RomPatcher.js','modules/BinFile.js','modules/RomPatcher.format.bps.js'])
  tools[vendor+'/'+name]=hash(read(vendor+'/'+name));
const manifest={schema:1,version:'0.7',name:'FFTA Eight-Job Expansion',
  sourceCommit:acceptance.sourceCommit,
  cleanRom:{sha1:hash(source,'sha1'),sha256:hash(source),bytes:source.length},
  rom:{path:romPath,sha1:expected,sha256:hash(target),bytes:target.length},
  patch:{file:'FFTA_Expansion_v0.7.bps',format:'BPS',sha256:hash(bytes),bytes:bytes.length},
  saves:{directory:'saves/expansion-v0.7',basename:'FFTA_Expansion_v0.7'},
  documents:Object.fromEntries(documents.map(n=>[n,hash(read(n))])),
  packagingSources:Object.fromEntries(['scripts/package-expansion.mjs','scripts/launch-expansion.ps1',
    'Play Expansion.cmd'].map(n=>[n,hash(read(n))])),
  patcherSources:tools,acceptanceSha256:hash(read('build/release-acceptance.json')),
  cleanRebuildReportSha256:acceptance.cleanRebuildReportSha256,
  checks:{roundtrip:true,wrongSourceRejected:true,deterministicPatch:true},
  preservedPlayerFiles:preserved,
  coverage:acceptance.scope};
assert.deepEqual(protectedFiles(),preserved,'Existing player files changed during packaging');
// Metadata may be refreshed after a documentation/source checkpoint. Game and
// patch bytes are immutable; no existing game/save is replaced.
fs.writeFileSync(safe(folder+'/manifest.json'),JSON.stringify(manifest,null,2)+'\n');
fs.writeFileSync(safe(folder+'/acceptance.json'),read('build/release-acceptance.json'));
console.log(JSON.stringify({passed:true,romSha1:expected,patchBytes:bytes.length,
  patchSha256:hash(bytes),manifest:folder+'/manifest.json',rom:romPath}));
