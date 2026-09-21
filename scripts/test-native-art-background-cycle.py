"""Background rotation entry bypass and exact native output on ARMv4T.

The generated-color oracle executes the original game on independent colors.
This component invokes the original native dispatcher on retained state.
"""
import ast, collections, datetime, hashlib, itertools, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha

sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
code=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000')
code=code.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(code)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARMv4T>','exec'))
meta=json.loads((ROOT/'build/art/live-palette/poc.json').read_text())
rom=Path(meta['path']).read_bytes(); old=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(old).hexdigest()==meta['baseRomSha1']
source=ROOT/'build/art/live-palette/battle/20260918T075021.733381Z'
ram=(source/'candidate-ready.ram').read_bytes(); iw=(source/'candidate-ready.iwram').read_bytes()
assert sha(ram)=='a7fa401e99806ad8b6c9be5004b98aaaa716194fc71e121f661fd2bfceaa4dad'
assert sha(iw)=='d7250d07c74b2ece6ea6ba4151a82b28d8b2657f720920e21683aa5812570280'
BASE,LIMIT=meta['ramReservation']; B=BASE+meta['bindingOffset']; V=BASE+meta['variantOffset']; PAL=0x03003a60
custom=rom[meta['symbols']['ffta_art_custom_colors']-0x08000000+32:meta['symbols']['ffta_art_custom_colors']-0x08000000+64]
out=ROOT/'build/art/background-cycle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'); out.mkdir(parents=True)
checks=collections.Counter(); records=[]; case=None

def check(name,a,b):
 checks[name]+=1
 assert a==b,(case,name,repr(a)[:220],repr(b)[:220])
def call(a,pc,*args,residue=0):
 a.put(STACK+residue,struct.pack('<'+'I'*len(args[4:]),*args[4:]));return a.call(pc,*args[:4],stack=STACK+residue)
def machine(data):
 a=ARM(data,iw); a.put(0x02000000,ram); return a
def native(a): return a.read(0x03003860,0x1e09)
def outside(a): return a.read(0x02000000,BASE-0x02000000)+a.read(LIMIT,0x02040000-LIMIT)
def entries(a):
 return [(slot,B+slot*252,a.word(B+slot*252+248)) for slot in range(10) if a.read(V+slot,1)!=b'\xff']
def compare(a,n,o):
 check('complete native palette task heap and colors preserved',native(a),native(n))
 for slot,entry,bank in entries(a):
  check('generated colors match original independent oracle',a.read(entry,32),o.read(PAL+bank*32,32))
  check('contiguous display colors match current binding',a.read(B+2520+slot*32,32),a.read(entry,32))
 check('no unsupported effect silently accepted',a.word(B+2848),0)
 check('outside gameplay memory unchanged',outside(a),outside(n))

before_meta=json.loads((ROOT/'build/art/live-palette/21f24d6f69d5864d28366ee1a515e72b84e2cf59/manifest.json').read_text())
before_rom=Path(before_meta['path']).read_bytes()
assert hashlib.sha1(before_rom).hexdigest()==before_meta['romSha1']
try:
 for kind,(first,last),residue in itertools.product(('rotate','cycle'),((162,168),(169,175),(250,255),(255,256),(256,271)),(0,4)):
  case=(kind,first,last,residue);a,b,n=machine(rom),machine(before_rom),machine(old);machines=(a,b,n)
  tasks=[]
  for m in machines:
   pc=0x08146fb8 if kind=='rotate' else 0x08147068
   args=(first,last,6,1,1) if kind=='rotate' else (first,last,6,1,1,0x08419d60)
   tasks.append(call(m,pc,*args,residue=residue))
  check('all constructor task handles identical',tasks,[tasks[0]]*3)
  frozen=a.read(BASE,LIMIT-BASE);counts=[0,0,0];entered=[0,0]
  def counter(index,entry):
   def callback(u,pc,size,data):
    counts[index]+=1
    if index<2 and pc==entry:entered[index]+=1
   return callback
  for i,m in enumerate(machines):
   entry=(meta if i==0 else before_meta)['symbols']['ffta_art_live_fade_'+kind] if i<2 else 0
   m.u.hook_add(UC_HOOK_CODE,counter(i,entry))
  pc=0x08146864 if kind=='rotate' else 0x08146bb0
  for tick in range(3):
   result=[call(m,pc,t,residue=residue) for m,t in zip(machines,tasks)]
   check('observable callback return preserved',result,[result[2]]*3)
   check('native state remains identical',native(a),native(n));check('preceding build native state identical',native(b),native(n))
   check('all outside gameplay memory preserved',outside(a),outside(n))
  if last<256:
   check('background callbacks bypass C bookkeeping',entered,[0,3])
   check('background leaves complete art reservation unchanged',a.read(BASE,LIMIT-BASE),frozen)
   check('background instruction overhead reduced',counts[0]<counts[1],True)
  else:check('OBJ and crossing boundaries retain C bookkeeping',entered,[3,3])
  records.append(dict(kind=kind,first=first,last=last,stackResidue=residue,currentInstructions=counts[0],beforeInstructions=counts[1],nativeInstructions=counts[2],cEntries=entered))
 report=dict(status='passed',romSha1=meta['romSha1'],beforeRomSha1=before_meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records,
  scope='Actual callbacks on ARMv4T: native/background and OBJ-boundary behavior, complete art-memory immutability on background path, register/stack ABI and instruction count versus preceding candidate. Instruction counts are not hardware cycles or frame timing.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n');print(out);raise
