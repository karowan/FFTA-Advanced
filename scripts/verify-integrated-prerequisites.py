"""Reuse an unchanged, already-tested image and its exact native captures.

Fail closed on source/build-input drift, absent provenance or modified fixture
bytes. This verifies prerequisites only; it does not run or certify new tests.
"""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(path,algorithm='sha256'):
 return hashlib.new(algorithm,path.read_bytes()).hexdigest()
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']);assert digest(rom,'sha1')==meta['romSha1']
baseline=None;problems=[]
build_only='--build-only' in sys.argv
assembly_only='--assembly-only' in sys.argv
reports=sorted((ROOT/'build/expansion/test-runs').glob('*/report.json'),reverse=True)
native_baseline=None
if not (build_only or assembly_only):
 for path in reports:
  report=json.loads(path.read_text())
  if not report.get('inputsUnchanged'):continue
  native_step=next((s for s in report.get('steps',[]) if s['id'] in ('test-integrated-native','test-integrated-native-cached') and s.get('status')=='passed'),None)
  if not native_step:continue
  native=json.loads(pathlib.Path(native_step['log']).read_text())
  if native.get('romSha1')==meta['romSha1'] and native.get('passed'):
   native_baseline=str(path.relative_to(ROOT));break
 assert native_baseline,'No passing native differential for the exact candidate; use build-only verification to rerun that prerequisite'
for path in reports:
 report=json.loads(path.read_text())
 steps={s['id']:s for s in report.get('steps',[])}
 if not report.get('inputsUnchanged'):continue
 # A failing consumer test does not invalidate its successful, immutable
 # prerequisites. Require the entire declared preparation chain, not the
 # overall report result, so diagnosis need not rebuild identical bytes.
 prerequisites=('build-samurai-private','build-job-state-private','build-chemist',
  'build-dark-knight','build-viking','build-integrated-jobs',
  'prepare-integrated-battle','prepare-integrated-executor')
 if assembly_only:prerequisites=prerequisites[:6]
 if not all(steps.get(k,{}).get('status')=='passed' for k in prerequisites):continue
 built=json.loads(pathlib.Path(steps['build-integrated-jobs']['log']).read_text())
 # Builder stdout omits the large symbol/change maps; its on-disk manifest
 # includes them. Match every emitted field, not unlike-shaped dictionaries.
 if any(meta.get(k)!=v for k,v in built.items()):continue
 inputs=report['inputs']
 # Test edits and test selection are allowed. Build/fixture scripts, helpers,
 # native source, compiler, clean input and generated foundation stay exact.
 for name,value in inputs.items():
  p=pathlib.Path(name)
  # This diagnostic only consumes retained captures; no builder or fixture
  # imports it. Editing its observation/selection cannot alter prerequisites.
  diagnostic=p.as_posix()=='scripts/trace-mystic-knight-ai.py'
  # These read-only audits write ledgers consumed by source-access tests.
  # No assembly/fixture step imports them or reads those ledgers.
  source_audit=p.as_posix() in ('scripts/audit-monster-ability-sources.mjs', 'scripts/audit-vanilla-teaching-sources.mjs')
  # This JSON is an allocation reference document, not a builder/fixture
  # input. Actual addresses and linker limits remain source-fingerprinted.
  allocation_notes=p.as_posix()=='notes/shared-job-allocations.json'
  # Assembly-only reuse makes no fixture claim. These consumers do not affect
  # installed code/assets; fresh fixture preparation hashes its own inputs.
  fixture_only=assembly_only and p.as_posix() in ('scripts/create-battle-fixture.py','scripts/geomancer_render_observation.py')
  # The six assembly steps consume the separately fingerprinted engine.bin,
  # symbols/tables and combat image; they do not invoke Build Engine.ps1.
  # Runtime-selection parameters in that outer driver cannot change these
  # unchanged inputs. Full source reconstruction has its own explicit gate.
  outer_driver=assembly_only and p.as_posix()=='Build Engine.ps1'
  # Process admission/retention and emulator teardown cannot change the six
  # builder outputs. Keep these exact exclusions restricted to assembly reuse;
  # fixture/executor reuse still requires its own recorded harness identity.
  resource_only=assembly_only and p.as_posix() in (
   'scripts/resource_guard.py','scripts/prune-build-outputs.py',
   'scripts/run-expansion-tests.py','scripts/rebuild-expansion.py','scripts/emulator-test.py')
  if diagnostic or source_audit or allocation_notes or fixture_only or outer_driver or resource_only or p.suffix=='.md' or (p.name.startswith('test-') and p.suffix=='.py') or p.name.endswith('test-plan.json') or p.as_posix()=='scripts/verify-integrated-prerequisites.py':continue
  if digest(ROOT/p)!=value:problems.append(name)
 current={p.relative_to(ROOT).as_posix() for p in (ROOT/'src').rglob('*') if p.is_file()}
 recorded={name for name in inputs if name.startswith('src/')}
 if current!=recorded:problems.append('native source file inventory')
 if not problems:baseline=str(path.relative_to(ROOT))
 break
assert baseline,('No matching unchanged build/native baseline; run the ordinary dependency chain',problems)
if assembly_only:
 print(json.dumps(dict(passed=True,romSha1=meta['romSha1'],reusedBaseline=baseline,
  scope='Unchanged six-step ROM assembly only; no battle captures or native combat certification'),indent=2))
 sys.exit(0)
executor=rom.parent/'executor';capture=json.loads((executor/'manifest.json').read_text())
assert capture['passed'] and capture['romSha1']==meta['romSha1']
for name,value in capture['inputsHashes'].items():assert digest(ROOT/name,'sha1')==value,name
for name,value in capture['files'].items():assert digest(executor/name,'sha1')==value,name
print(json.dumps(dict(passed=True,romSha1=meta['romSha1'],reusedBaseline=baseline,
 nativeBaseline=native_baseline,verifiedCaptureFiles=list(capture['files']),
 scope='unchanged build/captures only; native differential not certified' if build_only else 'unchanged build and passing native executor prerequisites only'),indent=2))
