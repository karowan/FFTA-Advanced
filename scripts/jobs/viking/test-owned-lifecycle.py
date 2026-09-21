"""Viking lifecycle operations on actual native owned copies and canonical peers."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();S=meta['symbols'];fix=ROM.parent/'executor'
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
node=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in node.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
checks=collections.Counter();copy=struct.unpack_from('<I',rom,0x36d4bc)[0]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b)
for residue in (0,4):
 m=ARM(rom,iw)
 def call(name,*args):return m.call(S[name],*args,stack=STACK+residue)
 def record(unit):return call('ffta_job_state',unit)
 m.put(0x02000000,bytes(0x40000));m.put(0x02001e70,b'FFTAEXP1\x01');m.call(0x080070c8,0x02018000,0x27000);m.put(0x0200f434,struct.pack('<I',0x02018000));call('ffta_job_reset')
 for unit in (UNIT,UNIT+264):m.put(unit+0x18,struct.pack('<4H',100,100,50,50));m.put(unit+5,bytes([118,2,118]))
 snapshot=m.call(0x08022840,0x1140);call('ffta_snapshot_register',snapshot)
 manager=m.call(0x08022840,0x430);m.put(0x0200f4b0,struct.pack('<I',manager));call('ffta_manager_register',manager)
 evaluated=call('ffta_evaluated_allocate',264)
 for copies in ([snapshot+4,snapshot+4+264],[manager+0x40,manager+0x148],[evaluated]):
  # Duplicate origin members must both clear when their represented source
  # leaves; copied events must never fall back to the live canonical bank.
  for dest in copies:m.call(copy,dest,UNIT,264,stack=STACK+residue)
  call('ffta_viking_grant_war_cry',UNIT,0);call('ffta_viking_grant_challenge',UNIT+264,UNIT)
  live=m.read(0x0203f400,808)
  for dest in copies:
   call('ffta_viking_grant_war_cry',dest,0);call('ffta_viking_grant_challenge',dest,UNIT)
  for dest in copies:
   # A canonical challenger is not represented in this owner merely because
   # its token is known. Local event sweeping is still token-precise.
   m.put(record(dest)+6,bytes([37,81]))
  call('ffta_viking_lifecycle_event',copies[0],2)
  for dest in copies:check('owned-challenger-death-clears-duplicate-links',m.read(record(dest)+5,1),b'\0')
  check('copied-event-canonical-isolation',m.read(0x0203f400,808),live)
  for dest in copies:
   call('ffta_viking_lifecycle_event',dest,4)
   check('copied-battle-end-clears-own-four-bytes',m.read(record(dest)+4,4),bytes(4))
  check('copied-battle-end-canonical-isolation',m.read(0x0203f400,808),live)
 # Real generic copyback transfers owned fields, never by pointer guessing.
 m.call(copy,evaluated,UNIT,264,stack=STACK+residue);m.put(record(evaluated)+4,bytes([2,2,37,0]));m.call(copy,UNIT,evaluated,264,stack=STACK+residue)
 check('copyback-persists-Viking-fields',m.read(record(UNIT)+4,4),bytes([2,2,37,0]))
 call('ffta_job_swap',0,1)
 check('roster-swap-follows-state-and-remaps-source',m.read(record(UNIT+264)+4,4),bytes([2,1,37,0]))
 call('ffta_evaluated_close',evaluated);check('retired-copy-has-no-record',record(evaluated),0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),scope=__doc__)
(ROM.parent/'owned-lifecycle.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
