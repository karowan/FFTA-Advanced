"""Installed native rotation/cycling versus the original ARMv4T engine.

The generated-color oracle executes the original game on independent colors.
This component invokes the original native dispatcher on retained state.
"""
import ast, collections, datetime, hashlib, itertools, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha

sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
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
out=ROOT/'build/art/rotation'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'); out.mkdir(parents=True)
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

try:
 for kind,bank,right,delay,steps,with_fade,residue,partial in itertools.product(
     ('rotate','cycle'),(0,9),(False,True),(1,3),(1,3),(False,True),(0,4),(False,True)):
  case=(kind,bank,right,delay,steps,with_fade,residue,partial)
  a,n,o=machine(rom),machine(old),machine(old);machines=(a,n,o)
  a.put(BASE,bytes(4));call(a,meta['symbols']['ffta_art_heap_reset'])
  first=256+bank*16;low=first+3 if partial else first;high=first+12 if partial else first+15
  for m,colors in ((a,old[0x419d60:0x419d80]),(n,old[0x419d60:0x419d80]),(o,custom)):
   m.put(PAL+bank*32,colors)
  if with_fade:
   fade=[call(m,0x08147ad0,first,16,17,residue=residue) for m in machines]
   for tick in range(3):
    for m in machines:call(m,0x08147288,residue=residue)
  tasks=[]
  for m in machines:
   if kind=='rotate':
    task=call(m,0x08146fb8,low,high,8,2 if right else 1,delay,residue=residue)
    call(m,0x0814862c,task,steps,residue=residue)
   else:
    # Eight literal colors are declared constructor inputs, not fabricated outputs.
    m.put(0x02028000,struct.pack('<8H',0x1234,0x7fff,0,0x421f,0x5294,0x7c00,0x3e0,0x1f))
    task=call(m,0x08147068,low,high,8,2 if right else 1,delay,0x02028000,residue=residue)
   tasks.append(task)
  check('native constructors unchanged',(tasks[0],native(a)),(tasks[1],native(n)))
  for tick in range(28):
   for m in machines:call(m,0x08147288,residue=residue)
   compare(a,n,o)
   if kind=='rotate' and with_fade:
    for slot,entry,entrybank in entries(a):
     address=256+entrybank*16
     check('rotation carries generated fade targets',a.read(entry+32,32),b''.join(o.read(0x03003e68+(address+i)*12,2) for i in range(16)))
  check('rotation finishes native task',struct.unpack('<H',a.read(tasks[0],2))[0],0)
  records.append(dict(kind=kind,bank=bank,right=right,delay=delay,steps=steps,concurrentFade=with_fade,stackResidue=residue,partial=partial))
 # Explicit boundary: a two-bank rotation has no authenticated cross-bank
 # generated source mapping, and must be counted rather than silently accepted.
 case=('cross-bank refusal',);a,n=machine(rom),machine(old)
 a.put(BASE,bytes(4));call(a,meta['symbols']['ffta_art_heap_reset'])
 for m in (a,n):
  m.put(PAL,old[0x419d60:0x419d80]*2);call(m,0x08146fb8,256,287,2,1,1)
 for m in (a,n):call(m,0x08147288)
 check('cross-bank operation preserves native state',native(a),native(n))
 check('cross-bank generated ambiguity explicitly refused',a.word(B+2848),2)
 report=dict(status='passed',romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records,source=str(source),
  scope='ARMv4T installed type2/type4 callbacks via original dispatcher, both directions, delays, step counts, partial/full single-bank ranges, first appearance, concurrent fades, exact native state and generated oracle. Cross-bank identity explicitly refused. No live hardware, natural triggers or all-class/capacity/timing acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n');print(out);raise
