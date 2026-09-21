"""Installed palette cancellation/deletion versus the original ARMv4T engine.

The generated-color oracle executes the original game on independent colors.
This component drives callbacks explicitly; it does not model the scheduler.
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
out=ROOT/'build/art/task-controls'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'); out.mkdir(parents=True)
checks=collections.Counter(); records=[]; case=None

def check(name,a,b):
 checks[name]+=1
 assert a==b,(case,name,repr(a)[:220],repr(b)[:220])
def call(a,pc,*args,residue=0): return a.call(pc,*args,stack=STACK+residue)
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

scenarios=('whole','cover','lower','upper','middle','before','after','wrong type',
 'paused cancel','delete','delete null','collect active','collect paused','collect completed',
 'collect null','delete all','bank lower','bank upper')
try:
 for name,bank,residue,elapsed,skip in itertools.product(scenarios,(0,9),(0,4),(0,4,16),(False,True)):
  case=(name,bank,residue,elapsed,skip)
  a,n,o=machine(rom),machine(old),machine(old); machines=(a,n,o)
  a.put(BASE,bytes(4)); call(a,meta['symbols']['ffta_art_heap_reset'])
  count=32 if name.startswith('bank ') else 16; first=256+bank*16
  # Both variants use the original normal source; bank number is independent of brightness.
  for m,colors in ((a,old[0x419d60:0x419d80]),(n,old[0x419d60:0x419d80]),(o,custom)):
   m.put(PAL+bank*32,colors*(count//16))
  tasks=[call(m,0x08147a7c,first,count,17,residue=residue) for m in machines]
  check('task handles preserved',tasks[0],tasks[1])
  for m,t in zip(machines,tasks):
   if skip: m.put(t+2,struct.pack('<H',struct.unpack('<H',m.read(t+2,2))[0]|16))
  for tick in range(elapsed):
   for m,t in zip(machines,tasks): call(m,0x08148740,t,residue=residue)
  compare(a,n,o)
  if name in ('paused cancel','collect paused'):
   for m,t in zip(machines,tasks): call(m,0x08148518,t,residue=residue)
  if name=='collect completed':
   for tick in range(elapsed,17):
    for m,t in zip(machines,tasks): call(m,0x08148740,t,residue=residue)
  frozen=[(slot,entry,bank,a.read(entry,32)) for slot,entry,bank in entries(a)]
  counters=a.read(B+2840,12)
  ranges={'whole':(first,first+15,0xffff),'cover':(0,511,0xffff),
   'lower':(first,first+5,0xffff),'upper':(first+10,first+15,0xffff),
   'middle':(first+5,first+10,0xffff),'before':(first-16,first-1,0xffff),
   'after':(first+count,first+count+15,0xffff),'wrong type':(first,first+count-1,0),
   'paused cancel':(first,first+count-1,0xffff),
   'bank lower':(first,first+15,0xffff),'bank upper':(first+16,first+31,0xffff)}
  results=[]
  for m,t in zip(machines,tasks):
   if name in ranges: result=call(m,0x08146dc8,*ranges[name],residue=residue)
   elif name=='delete all': result=call(m,0x08148540,residue=residue)
   elif name.startswith('delete'): result=call(m,0x08148498,0 if name=='delete null' else t,residue=residue)
   else: result=call(m,0x081484cc,0 if name=='collect null' else t,residue=residue)
   results.append(result)
  check('control observable return including caller continuation',results[0],results[1])
  compare(a,n,o)
  check('cancellation does not invent starts completions or refusals',a.read(B+2840,12),counters)
  for slot,entry,before_bank,colors in frozen: check('control preserves current colors',a.read(entry,32),colors)
  dead=name in ('whole','cover','middle','delete','delete all','collect completed')
  if dead:
   for slot,entry,before_bank in entries(a): check('deleted task cannot remain attached',a.word(entry+244),0)
  else:
   if name in ('paused cancel','collect paused'):
    for m,t in zip(machines,tasks): call(m,0x0814852c,t,residue=residue)
   for tick in range(elapsed,17):
    for m,t in zip(machines,tasks): call(m,0x08148740,t,residue=residue)
    compare(a,n,o)
  # New white fade exercises slot reuse and common setup's nested cancellation.
  fresh=[call(m,0x08147ad0,first,count,8,residue=residue) for m in machines]
  for tick in range(8):
   for m,t in zip(machines,fresh): call(m,0x08148740,t,residue=residue)
   compare(a,n,o)
  records.append(dict(control=name,bank=bank,stackResidue=residue,elapsed=elapsed,skipTransparent=skip))
 report=dict(status='passed',romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records,source=str(source),
  scope='ARMv4T actual cancellation, range trims, whole deletion, type filtering, paused cancellation/collection, active/completed/null collection, direct/all deletion, two-bank tasks and reuse. Full native effect region and generated oracle per callback, ABI, both stack alignments and transparent-color flag. Callbacks explicitly driven: no live scheduler/hardware, native heap destruction, other constructors or natural scene acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n'); print(out); raise
