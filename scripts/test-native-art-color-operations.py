"""Four native color setters, exact generated targets and callback sequences.

The independent reference runs each original setter/callback on generated
colors as native inputs. The installed hooks must preserve all native output.
"""
import argparse, ast, collections, datetime, hashlib, itertools, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--extended',action='store_true')
args=parser.parse_args()
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
arm_source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000')
arm_source=arm_source.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/live-palette/poc.json').read_text());rom=Path(meta['path']).read_bytes();original=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(original).hexdigest()==meta['baseRomSha1']
source=ROOT/'build/art/live-palette/battle/20260918T075021.733381Z'
ram=(source/'candidate-ready.ram').read_bytes();iw=(source/'candidate-ready.iwram').read_bytes()
assert sha(ram)=='a7fa401e99806ad8b6c9be5004b98aaaa716194fc71e121f661fd2bfceaa4dad' and sha(iw)=='d7250d07c74b2ece6ea6ba4151a82b28d8b2657f720920e21683aa5812570280'
BASE,LIMIT=meta['ramReservation'];BIND=BASE+meta['bindingOffset'];ENTRY=BIND+meta['bindingEntryBytes']
out=ROOT/'build/art/color-operations'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=collections.Counter();records=[];case=None
def check(name,a,b):checks[name]+=1;assert a==b,(case,name,repr(a)[:200],repr(b)[:200])
def machine(data):
 a=ARM(data,iw);a.put(0x02000000,ram);return a
def call(a,pc,*args,residue=0):
 a.put(STACK+residue,struct.pack('<'+'I'*len(args[4:]),*args[4:]));return a.call(pc,*args[:4],stack=STACK+residue)
def native_state(a):return a.read(0x03003860,0x1e09)
def outside(a):return a.read(0x02000000,BASE-0x02000000)+a.read(LIMIT,0x02040000-LIMIT)
operations=[('gray',0x08147b28,()),('preset tint',0x08147ba4,())]
for coefficients in ((0,0,0),(256,256,256),(294,273,204),(128,320,192),(65535,1,257),(0x100ff,0x10100,0x10001)):
 operations.append(('rgb '+str(coefficients),0x08147c2c,coefficients))
for channels in ((0,0,0),(31,31,31),(5,17,29),(65535,33,1024),(0x10005,0x10011,0x1001d)):
 operations.append(('solid '+str(channels),0x08147cc0,channels))
if args.extended:
 operations=[]
 for amount in (0,1,8,16,255,0x10008):
  for name,pc in (('brighten',0x08147ec8),('darken',0x08147f50)):
   operations.append((name+' '+str(amount),pc,(amount,)))
 for values in ((0x1234,0,16),(0x7fff,8,8),(0x10123,0x100ff,0x10108)):
  operations.append(('blend '+str(values),0x08147d94,values))
 for amount in (0,128,256,384,65535,0x10100):
  operations.append(('exposure '+str(amount),0x0814731c,(amount,)))
 for values in ((128,256,384),(0,0,0),(65535,1,257),(0x10080,0x10100,0x10180)):
  operations.append(('exposure_rgb '+str(values),0x081473e4,values))
try:
 for (name,pc,values),duration,interrupt,residue in itertools.product(operations,(0,1,8,17),(False,True),(0,4)):
  case=(name,duration,interrupt,residue);a,n,o=machine(rom),machine(original),machine(original)
  bank=a.word(ENTRY+248);first=256+bank*16;colors=a.read(ENTRY,32)
  check('retained owned bank and idle task', (bank,a.word(ENTRY+244)),(0,0))
  o.put(0x03003860+first*2,colors)
  if interrupt:
   tasks=[call(m,0x08147a7c,first,16,17,residue=residue) for m in (a,n,o)]
   for tick in range(3):
    for m,t in zip((a,n,o),tasks):call(m,0x08148740,t,residue=residue)
   check('interrupted custom source is exact native interpolation',a.read(ENTRY,32),o.read(0x03003860+first*2,32))
  old_ewram=outside(a);before=struct.unpack('<3I',a.read(BIND+2840,12))
  task=call(a,pc,first,16,duration,*values,residue=residue);ntask=call(n,pc,first,16,duration,*values,residue=residue);otask=call(o,pc,first,16,duration,*values,residue=residue)
  check('native setter task and complete palette state exact',(task,native_state(a)),(ntask,native_state(n)))
  check('generated binding owns actual native task',a.word(ENTRY+244),task)
  target=b''.join(o.read(0x03003e68+(first+i)*12,2) for i in range(16))
  check('all generated target colors exact original setter',a.read(ENTRY+32,32),target)
  check('generated source colors reflect original immediate setter writes',a.read(ENTRY,32),o.read(0x03003860+first*2,32))
  check('immediate display source agrees with generated current colors',a.read(BIND+2520+32,32),a.read(ENTRY,32))
  check('one supported operation registered',struct.unpack('<3I',a.read(BIND+2840,12)),(before[0]+1,before[1],before[2]))
  for tick in range(max(1,duration)):
   for m,t in ((a,task),(n,ntask),(o,otask)):call(m,0x08148740,t,residue=residue)
   check('native callback state exact',native_state(a),native_state(n))
   check('all generated colors exact original callback',a.read(ENTRY,32),o.read(0x03003860+first*2,32))
   check('contiguous display colors match binding',a.read(BIND+2520+32,32),a.read(ENTRY,32))
  check('native completion retires generated binding',a.word(ENTRY+244),0)
  check('one supported operation completed',struct.unpack('<3I',a.read(BIND+2840,12)),(before[0]+1,before[1]+1,before[2]))
  check('no unit heap save or other EWRAM writes',outside(a),old_ewram)
  check('other generated owners untouched',a.read(BIND,252)+a.read(ENTRY+252,252*8),ram[BIND-0x02000000:BIND-0x02000000+252]+ram[ENTRY-0x02000000+252:ENTRY-0x02000000+252*9])
  records.append(dict(operation=name,duration=duration,interrupt=interrupt,stackResidue=residue,targetSha256=sha(target)))
 for name,pc,values in operations:
  for first,count,duration,accepted in ((0,16,8,True),(257,15,8,False),(256,15,8,False),(256,16,256,False)):
   case=('boundary',name,first,count,duration);a,n=machine(rom),machine(original);before=a.read(ENTRY,32)
   task=call(a,pc,first,count,duration,*values);ntask=call(n,pc,first,count,duration,*values)
   check('boundary native operation preserved',(task,native_state(a)),(ntask,native_state(n)))
   check('boundary has no invented generated colors',a.read(ENTRY,32),before)
   check('unowned stays unbound and incomplete cases explicit',struct.unpack('<3I',a.read(BIND+2840,12)),(0,0,0 if accepted else 1))
 report=dict(status='passed',romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records,source=str(source),scope='Installed gray/preset tint/six-argument RGB/six-argument solid setters and actual native callbacks, exact independent generated-color native oracle, both stack alignments, interruptions, durations0/1/8/17, argument truncation, unowned/partial/unsupported-duration boundaries. Does not establish real hardware playback, late entry, reload, partial-bank support or all native effects.')
 if args.extended:report['scope']='ARMv4T installed weighted blend, partial brighten/darken, uniform/per-channel exposure setters and actual original callbacks. Exact generated/native targets, immediate source floor, interruption, both stack alignments, duration and argument truncation, unrelated native/gameplay memory, partial/unowned/duration refusal. No live hardware/scene, table-source variants or every native effect acceptance.'
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n');print(out);raise
