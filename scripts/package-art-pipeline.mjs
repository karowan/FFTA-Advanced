/* Package only the exact tested technical candidate; never touch player saves. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const hash=(b,a='sha256')=>crypto.createHash(a).update(b).digest('hex');
const read=n=>fs.readFileSync(path.resolve(root,n));
const candidateManifest=process.argv[2]??'build/art/pipeline/current.json';
const candidate=JSON.parse(read(candidateManifest));
const target=read(candidate.path),source=read('roms/clean/FFTA_US_clean.gba');
assert.equal(hash(source,'sha1'),'4ac05441f4de70a4ec3dd932116346c61b8783d9');
assert.equal(hash(target,'sha1'),candidate.romSha1);
assert.equal(hash(target),candidate.romSha256);
assert([undefined,1,2,3].includes(candidate.schema),'Unsupported art candidate schema');
const required=candidate.schema===3?
  ['test-connected-art-rebuild','test-connected-art-native','test-connected-art-portraits-ui',
   'test-connected-art-equipment-ui','test-connected-art-preview-party','test-connected-art-preview-buy',
   'test-connected-art-preview-sell','test-connected-art-status-current','test-connected-art-held-weapon',
   'test-connected-art-projectile-impact','test-art-compact-status-battle-ui','test-art-delivery-phase-evidence',
   'test-art-delivery-frame-events','test-art-native-highlight','test-art-damage-palettes',
   'test-art-damage-additional-operations','test-art-damage-boundaries','test-art-highlight-thundaga',
   'test-art-larger-encounter']:
  candidate.schema===2?
  ['test-assembled-art-rebuild','test-assembled-portraits-ui','test-assembled-equipment-ui',
   'test-assembled-preview-native','test-assembled-preview-party','test-assembled-preview-buy','test-assembled-preview-sell',
   'test-generated-effect-native','test-generated-effect-battle','test-repaired-map-consumers']:
  ['icons','preview-native','preview-party','preview-buy','preview-sell','miniature','battle','rebuild'].map(n=>'test-art-pipeline-'+n);
const evidence={};
const retained={};
const retainedIDs=['test-generated-weapon-native','test-generated-weapon-battle-fresh','test-generated-projectile'];
for(const dir of fs.readdirSync(path.join(root,'build/expansion/test-runs')).sort()) {
  const file=path.join(root,'build/expansion/test-runs',dir,'report.json');
  if(!fs.existsSync(file))continue;
  const run=JSON.parse(fs.readFileSync(file));
  // A later failed step does not erase an earlier completed, isolated pass.
  // Retain the enclosing run's status and failures instead of hiding them.
  if(!['passed','failed'].includes(run.status)||!run.inputsUnchanged)continue;
  for(const step of run.steps??[]) {
    if((!required.includes(step.id)&&!(candidate.schema===2&&retainedIDs.includes(step.id)))||step.status!=='passed')continue;
    const log=fs.readFileSync(step.log,'utf8');
    let output;
    for(const line of log.split(/\r?\n/)) {
      try {const value=JSON.parse(line);if(value.report)output=value;}catch{}
    }
    if(!output||!fs.existsSync(output.report))continue;
    const result=JSON.parse(fs.readFileSync(output.report));
    if(result.status!=='passed')continue;
    const current=required.includes(step.id)&&result.romSha1===candidate.romSha1;
    const parent=candidate.schema===2&&retainedIDs.includes(step.id)&&result.romSha1===candidate.components.effect.baseRomSha1;
    if(!current&&!parent)continue;
    (current?evidence:retained)[step.id]={runner:path.relative(root,file),runnerSha256:hash(fs.readFileSync(file)),
      runnerStatus:run.status,otherFailedSteps:run.steps.filter(s=>!['passed','not_run'].includes(s.status)).map(s=>s.id),
      report:path.relative(root,output.report),reportSha256:hash(fs.readFileSync(output.report)),
      log:path.relative(root,step.log),logSha256:hash(fs.readFileSync(step.log)),checks:result.checks.length,
      scope:result.scope,...(result.fixtureRomSha1?{fixtureRomSha1:result.fixtureRomSha1}: {})};
  }
}
assert(required.every(id=>evidence[id]),'Missing current-candidate evidence: '+required.filter(id=>!evidence[id]).join(', '));
if(candidate.schema===3) {
  const live=candidate.components.livePalette;
  assert(live.allClasses&&live.compactBattleStatus&&live.compactUsKeyboard&&!live.traceTarget,
    'Connected delivery requires the repaired all-class/menu configuration, never diagnostic instrumentation');
  assert.equal(hash(read(candidate.sourcePaletteManifest)),candidate.sourcePaletteManifestSha256);
  for(const [name,digest] of Object.entries(live.sources))assert.equal(hash(read(name)),digest,'Changed palette source: '+name);
}
if(candidate.schema===2) {
  assert(retainedIDs.every(id=>retained[id]),'Missing applicable held-weapon/projectile evidence');
  const effect=candidate.components.effect,parent=read(effect.source);
  assert.equal(hash(parent,'sha1'),effect.baseRomSha1);
  assert.equal(parent.length,target.length);
  for(let i=0;i<target.length;i++)assert(parent[i]===target[i]||
    (i>=effect.hook&&i<effect.hook+8)||(i>=effect.used[0]&&i<effect.used[1]),'Unexpected change beyond tested impact stage');
}
const require=createRequire(import.meta.url);
const vendor=path.join(root,'tools/rom-patcher-source/marcrobledo-RomPatcher.js-3183884/rom-patcher-js');
globalThis.BinFile=require(path.join(vendor,'modules/BinFile.js'));
const patcher=require(path.join(vendor,'RomPatcher.js'));
const bin=b=>new BinFile(Uint8Array.from(b).buffer);
function patch(){return Buffer.from(patcher.createPatch(bin(source),bin(target),'bps').export('FFTA_Art_Pipeline')._u8array);}
const bytes=patch(),parsed=patcher.parsePatchFile(bin(bytes));
assert(patcher.validateRom(bin(source),parsed));
assert.deepEqual(Buffer.from(patcher.applyPatch(bin(source),parsed,{requireValidation:true})._u8array),target);
assert.deepEqual(patch(),bytes,'Nondeterministic patch');
const wrong=Buffer.from(source);wrong[0]^=1;assert.equal(patcher.validateRom(bin(wrong),parsed),false);
// A documentation/evidence revision gets a distinct immutable bundle even
// when the tested ROM is identical. Prior player paths remain ROM-scoped.
const bundleId=hash(Buffer.from(JSON.stringify({rom:candidate.romSha1,
  guide:hash(read('ART-PIPELINE.md')),candidate:hash(read(candidateManifest)),evidence,retained})));
const directory='build/art/pipeline/delivery/'+candidate.romSha1+'/bundle-'+bundleId.slice(0,16);
function writeImmutable(name,bytes){
  const file=path.resolve(root,directory,name);assert(file.startsWith(path.join(root,directory)+path.sep));
  for(let p=file;p!==root;p=path.dirname(p))if(fs.existsSync(p))assert(!fs.lstatSync(p).isSymbolicLink(),'Linked output');
  fs.mkdirSync(path.dirname(file),{recursive:true});
  if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),bytes,'Existing package differs: '+name);
  else fs.writeFileSync(file,bytes,{flag:'wx'});
}
const connectedCoverage={
  equipmentPreview:'All ten new jobs on the second L/R page in Item List, Buy and Sell; actual current-candidate UI checked.',
  portraits:'Ten independent large portraits, menu figures and idle actors; generated uploads and fixed-character isolation checked. Draft designs remain unaccepted.',
  battle:'All ten class palette transports enabled. Current mixed Move/cancel, Viking held-axe action, Tomahawk projectile/impact with coexisting classes, status glyphs and battle Status/help/return checked.',
  targetingAndDamage:'Exact native highlight-copy provenance and colors1..15 damage/restore operations pass all-ten-palette native oracles and refusal controls. Actual Thundaga371 targeting/cast/hit/next-turn return matches the control outcome.',
  capacity:'A declared private formation-record fixture reaches13 actors: four native allies, four enemies, four party members including two custom classes, and judge. Status entry/return passes with minimum sampled20888 free heap bytes. This is bounded capacity, not a maximum or campaign eligibility.',
  timing:'Measured mixed-scene cancel overhead is four to five frames; exact native background phases and VBlank boundaries reconciled. No zero-overhead or all-scene timing claim.',
  retainedWater:'All-ten natural-water presentation-profile evidence remains historical coverage of unchanged assets; not rerun on this final ROM.',
  limitations:'Temporary repeated poses and water crops are not final animation. Maximum encounter/effect capacity, every natural caster/weapon/effect family and a full campaign replay on this art candidate remain unverified.'
};
const manifest={schema:1,bundleId,status:'verified technical preview',rom:{path:directory+'/FFTA_Art_Pipeline.gba',sha1:candidate.romSha1,sha256:hash(target)},
  patch:{file:'FFTA_Art_Pipeline.bps',sha256:hash(bytes),sourceSha1:hash(source,'sha1'),roundtrip:true,wrongSourceRejected:true,deterministic:true},
  saves:{directory:'saves/art-pipeline/'+candidate.romSha1,importsPlayerSave:false},coverage:candidate.schema===3?connectedCoverage:candidate.coverage,
  guideSha256:hash(read('ART-PIPELINE.md')),candidateManifestSha256:hash(read(candidateManifest)),evidence,
  retainedEvidence:retained,retainedScope:candidate.schema===2?'Held weapon and projectile parent results; whole-ROM comparison permits only action425 impact hook and owned payload. Current-candidate impact and menu checks recorded separately.':'none'};
writeImmutable('FFTA_Art_Pipeline.gba',target);writeImmutable('FFTA_Art_Pipeline.bps',bytes);
writeImmutable('ART-PIPELINE.md',read('ART-PIPELINE.md'));
writeImmutable('candidate.json',read(candidateManifest));
writeImmutable('manifest.json',Buffer.from(JSON.stringify(manifest,null,2)+'\n'));
fs.writeFileSync(path.join(root,'build/art/pipeline/delivery/current.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'passed',romSha1:candidate.romSha1,patchBytes:bytes.length,evidence:Object.keys(evidence).length,launched:false}));
