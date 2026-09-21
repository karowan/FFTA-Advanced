/* Full engineering delivery. No save migration, game launch or publication. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const hash=(b,a='sha256')=>crypto.createHash(a).update(b).digest('hex');
const read=n=>fs.readFileSync(path.resolve(root,n));
const expected='a28b624bb13c8f2f2597a4d4bd3999b17c234b99';
const romPath='roms/play/expansion-v0.7-engineering/FFTA_Expansion_v0.7.gba';
function protectedFiles(){
  const result={};
  function walk(name){
    const p=path.join(root,name);if(!fs.existsSync(p))return;
    const stat=fs.lstatSync(p);assert(!stat.isSymbolicLink(),'Linked player path: '+name);
    if(stat.isDirectory())for(const child of fs.readdirSync(p))walk(name+'/'+child);
    else if(/\.(gba|sav|srm|state|ss[0-9])$/i.test(name)&&name!==romPath)result[name]=hash(read(name));
  }
  for(const name of ['roms/play','saves','build/foundation'])walk(name);
  for(const name of fs.readdirSync(root).filter(n=>/^Play.*\.cmd$/i.test(n)))result[name]=hash(read(name));
  return result;
}
const before=protectedFiles();
const certificate=read('build/engineering-acceptance.json'),acceptance=JSON.parse(certificate);
assert(acceptance.passed&&acceptance.approvedForPackaging&&acceptance.romSha1===expected,'Full engineering acceptance required');
for(const [name,digest] of Object.entries({...acceptance.shippingSources,...acceptance.evidence}))assert.equal(hash(read(name)),digest,'Accepted source/evidence changed: '+name);
for(const row of acceptance.historicalSources)assert.equal(hash(execFileSync('git',['show',row.commit+':'+row.path],{cwd:root})),row.sha256);
const candidate=JSON.parse(read(acceptance.candidateManifest));
assert.equal(hash(read(acceptance.candidateManifest)),acceptance.candidateManifestSha256);
const target=read(candidate.path),source=read('roms/clean/FFTA_US_clean.gba');
assert.equal(hash(target,'sha1'),expected);assert.equal(hash(target),acceptance.romSha256);
assert.equal(hash(source,'sha1'),'4ac05441f4de70a4ec3dd932116346c61b8783d9');
assert.equal(hash(read(acceptance.rebuildReport)),acceptance.rebuildReportSha256);
const require=createRequire(import.meta.url),vendor='tools/rom-patcher-source/marcrobledo-RomPatcher.js-3183884/rom-patcher-js';
globalThis.BinFile=require(path.join(root,vendor,'modules/BinFile.js'));
const patcher=require(path.join(root,vendor,'RomPatcher.js')),bin=b=>new BinFile(Uint8Array.from(b).buffer);
const patch=()=>Buffer.from(patcher.createPatch(bin(source),bin(target),'bps').export('FFTA_Expansion_v0.7')._u8array);
const bytes=patch(),parsed=patcher.parsePatchFile(bin(bytes));
assert(patcher.validateRom(bin(source),parsed));
assert.deepEqual(Buffer.from(patcher.applyPatch(bin(source),parsed,{requireValidation:true})._u8array),target);
const wrong=Buffer.from(source);wrong[0]^=1;assert.equal(patcher.validateRom(bin(wrong),parsed),false);
assert.deepEqual(patch(),bytes,'Nondeterministic patch output');
const documents=['EXPANSION-PLAYER-GUIDE.md','JOB-CLASS-SPECIFICATION.md','WEAPON-ACQUISITION.md','AXE-SKILL-EXPANSION.md','REPRODUCIBLE-BUILD.md','ART-PLACEHOLDERS.md'];
// Ship the transitive local reference documents so the standalone guide has no
// broken links to checkout-only design notes. Private binaries are never copied.
for(let i=0;i<documents.length;i++){
  for(const match of read(documents[i]).toString('utf8').matchAll(/\]\(([^)]+)\)/g)){
    const link=match[1];if(link.includes('://')||link.startsWith('#'))continue;
    const relative=path.posix.normalize(path.posix.join(path.posix.dirname(documents[i]),link.split('#')[0]));
    assert(!relative.startsWith('../')&&!path.posix.isAbsolute(relative),'Reference outside checkout');
    assert(/\.(md|json)$/.test(relative),'Unexpected packaged reference type: '+relative);
    assert(fs.existsSync(path.join(root,relative)),'Missing guide reference: '+relative);
    if(!documents.includes(relative))documents.push(relative);
  }
}
const sources=['scripts/package-engineering-expansion.mjs','scripts/launch-engineering-expansion.ps1','Play Expansion.cmd','Play Previous Expansion.cmd'];
const docHashes=Object.fromEntries(documents.map(n=>[n,hash(read(n))]));
const sourceHashes=Object.fromEntries(sources.map(n=>[n,hash(read(n))]));
const sourceCommit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
const bundleId=hash(Buffer.from(JSON.stringify({sourceCommit,rom:expected,acceptance:hash(certificate),documents:docHashes,sources:sourceHashes})));
const folder='build/releases/v0.7-engineering/'+expected+'/bundle-'+bundleId.slice(0,16);
function safe(name){
  const output=path.resolve(root,name);assert(output.startsWith(root+path.sep));
  for(let p=output;p!==root;p=path.dirname(p))if(fs.existsSync(p))assert(!fs.lstatSync(p).isSymbolicLink(),'Linked output: '+p);
  return output;
}
function immutable(name,data){
  const p=safe(name);fs.mkdirSync(path.dirname(p),{recursive:true});
  if(fs.existsSync(p))assert.deepEqual(fs.readFileSync(p),data,'Existing immutable delivery differs: '+name);
  else fs.writeFileSync(p,data,{flag:'wx'});
}
const manifest={schema:1,version:'0.7-engineering',name:'FFTA v0.7 Full Engineering Expansion',status:'full engineering with placeholder artwork',bundleId,directory:folder,
  sourceCommit,
  rom:{path:romPath,sha1:expected,sha256:hash(target),bytes:target.length},
  patch:{file:'FFTA_Expansion_v0.7.bps',sha256:hash(bytes),bytes:bytes.length,format:'BPS',sourceSha1:hash(source,'sha1')},
  saves:{directory:'saves/expansion-v0.7-engineering',basename:'FFTA_Expansion_v0.7',importsPlayerSave:false},
  documents:docHashes,packagingSources:sourceHashes,acceptanceSha256:hash(certificate),cleanRebuildReportSha256:acceptance.rebuildReportSha256,
  checks:{roundtrip:true,wrongSourceRejected:true,deterministicPatch:true},preservedPlayerFiles:before,
  coverage:acceptance.scope,artwork:'Temporary generated images and repeated poses; replaceable through source catalogs and native action plans.'};
immutable(folder+'/FFTA_Expansion_v0.7.bps',bytes);immutable(romPath,target);
for(const name of documents)immutable(folder+'/'+name,read(name));
immutable(folder+'/acceptance.json',certificate);immutable(folder+'/manifest.json',Buffer.from(JSON.stringify(manifest,null,2)+'\n'));
assert.deepEqual(protectedFiles(),before,'Existing games, saves or launchers changed during packaging');
fs.writeFileSync(safe('build/releases/v0.7-engineering/current.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'passed',romSha1:expected,manifest:folder+'/manifest.json',patchBytes:bytes.length,protectedFiles:Object.keys(before).length,launched:false}));
