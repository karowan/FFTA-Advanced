"""Added Moon/Higan law predictions must preserve native global context and RNG.

Call the installed helpers with disposable actor/recipient copies, as native
law evaluation does. Native formula calls are observed, never replaced. Regen
may intentionally change the disposable actor; original units stay untouched.
"""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
JOB='--job-state' in sys.argv
meta=json.loads((ROOT/('build/expansion/probes/job-state/current.json' if JOB else 'build/expansion/probes/samurai/current.json')).read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();symbols=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
if JOB:
 import ctypes as C,runpy
 E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(ROM)
 try:
  assert (ROM.parent/'fixture/frozen.gba').read_bytes()==rom
  e.load(ROM.parent/'fixture/battle-ready.state');e.run(1);ram=e.memory();iw=C.string_at(*e.maps[0x03000000])
 finally:e.close()
else:
 fix=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,TARGET,RETURN,STACK=0x02000080,0x020033e4,0x08000100,0x03007000
ACTOR_COPY,TARGET_COPY,QUERY,FRAME,CTX=0x02022000,0x02022200,0x02022400,0x02022600,0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);checks=collections.Counter();failures=[];samples=[];formula_calls=[]
m.u.hook_add(UC_HOOK_CODE,lambda u,p,s,d:formula_calls.append(p),begin=symbols['ffta_physical_magnitude'],end=symbols['ffta_physical_magnitude'])

def check(kind,actual,expected,case):
 checks[kind]+=1
 if actual!=expected:
  failures.append(dict(kind=kind,case=case,actual=actual.hex() if isinstance(actual,bytes) else actual,expected=expected.hex() if isinstance(expected,bytes) else expected))

for action,residue,seed,alias in itertools.product((354,355),(0,4),range(8),(False,True)):
 case=dict(action=action,stackResidue=residue,seed=seed,globalQuery=alias)
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x02001e98,bytes(108));m.put(0x0203ff44,bytes(8))
 for unit in (UNIT,TARGET):
  m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2));m.put(unit+0x18,struct.pack('<4H',250,250,50,50))
 m.put(UNIT+5,bytes((116,1,116)));m.put(UNIT+0x35,b'\x74');m.put(UNIT+0x2a,struct.pack('<5H',383,0,0,0,0))
 m.put(ACTOR_COPY,m.read(UNIT,264));m.put(TARGET_COPY,m.read(TARGET,264))
 # A different valid native caller context proves prediction restores all
 # fields, rather than happening to write the same action or descriptor.
 original=bytearray(0x34);struct.pack_into('<IIIHH',original,0,UNIT,TARGET,TARGET,0,383)
 original[0x26]=0x20;original[0x28]=1;struct.pack_into('<I',original,0x30,0x08553e70)
 m.put(CTX,original)
 query=bytearray(0x34);struct.pack_into('<IIIHH',query,0,ACTOR_COPY,TARGET_COPY,TARGET_COPY,action,383)
 query_address=CTX if alias else QUERY
 m.put(query_address,query);original=m.read(CTX,0x34);frame=[0]*64;frame[5]=ACTOR_COPY;frame[6]=TARGET_COPY;m.put(FRAME,struct.pack('<64I',*frame))
 m.put(0x030034b0,struct.pack('<I',seed));before=m.read(UNIT,264)+m.read(TARGET,264)+m.read(0x02001e98,108);formula_calls.clear()
 if action==354:result=m.call(symbols['ffta_samurai_law_hit'],query_address,0,query_address+0x10,3,stack=STACK+residue)
 else:result=m.call(symbols['ffta_higan_harmful_law'],FRAME,stack=STACK+residue)
 check('positive_native_prediction',result,1,case)
 check('native_magnitude_exercised',len(formula_calls),1,case)
 check('native_global_context_preserved',m.read(CTX,0x34),bytes(original),case)
 check('native_RNG_preserved',m.word(0x030034b0),seed,case)
 check('caller_query_preserved',m.read(query_address,0x34),bytes(query),case)
 check('live_units_and_status_bank_preserved',m.read(UNIT,264)+m.read(TARGET,264)+m.read(0x02001e98,108),before,case)
 samples.append(dict(**case,result=result))
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),failures=failures,samples=samples,scope=__doc__)
(ROM.parent/'preview-context-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not failures,(len(failures),'preview context regression',failures[:2])
