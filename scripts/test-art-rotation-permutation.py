"""Exact installed ARMv4T rotation equivalence for all twenty history entries.

Compare the prior single-step algorithm with the permutation candidate,
including complete interpolation state, display colors, counters and RAM fences.
This is a component proof; live timing remains a separate declared test.
"""
import ast, datetime, hashlib, itertools, json, struct, sys
from pathlib import Path
from native_art import ROOT
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARMv4T>','exec'))
current=json.loads((ROOT/'build/art/live-palette/all-classes-workspace-current.json').read_text())
prior=json.loads((ROOT/'build/art/live-palette/f36376dee8303a4220dd0fc5c2cf37a8e2ac094e/manifest.json').read_text())
assert current['fastRotation'] and current['historySlots']==prior['historySlots']==20
machines=[]
for meta in (current,prior):
 rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
 machines.append(ARM(rom,bytes(0x8000)))
B=0x02010000; size=20*284+12
seed=bytearray((i*71+i//7)%256 for i in range(size))
for slot in range(20):
 struct.pack_into('<I',seed,slot*252+248,12)
 struct.pack_into('<I',seed,slot*252+244,0x03003c7c if slot%2 else 0)
out=ROOT/'build/art/rotation-permutation'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True);records=[];case=None
try:
 for right,feed,steps,width,residue in itertools.product((0,1),(0,1),(0,1,3,10,16,17,33),(1,10,16),(0,4)):
  case=dict(right=right,feed=feed,steps=steps,width=width,residue=residue)
  first=448+(3 if width==10 else 0);last=first+width-1
  for machine,meta in zip(machines,(current,prior)):
   machine.put(B-32,b'\xa5'*32+seed+b'\x5a'*32)
   machine.put(STACK+residue,struct.pack('<3I',steps,feed,0x421f))
   machine.call(meta['symbols']['ffta_art_binding_rotate'],B,first,last,right,stack=STACK+residue)
  assert machines[0].read(B-32,size+64)==machines[1].read(B-32,size+64),case
  records.append(case)
 report=dict(status='passed',romSha1=current['romSha1'],priorRomSha1=prior['romSha1'],checks=len(records),records=records,
  scope='Installed ARMv4T whole binding state equivalence for twenty simultaneous histories; active/inactive fade records, both directions, literal feed, zero/multiple/wrapped steps, single/partial/full ranges and ABI stack residues. Prior native dispatcher oracle evidence reused. No live hardware timing acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status='passed',checks=len(records),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=current['romSha1'],case=case,error=str(error),passed=records),indent=2)+'\n',encoding='utf-8')
 print(out);raise
