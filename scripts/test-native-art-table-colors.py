"""Seven-argument palette-table setters versus original ARMv4T execution."""
import ast,collections,datetime,hashlib,itertools,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
code=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000')
code=code.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(code)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARMv4T>','exec'))
meta=json.loads((ROOT/'build/art/live-palette/poc.json').read_text());rom=Path(meta['path']).read_bytes();old=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(old).hexdigest()==meta['baseRomSha1']
source=ROOT/'build/art/live-palette/battle/20260918T075021.733381Z';ram=(source/'candidate-ready.ram').read_bytes();iw=(source/'candidate-ready.iwram').read_bytes()
assert sha(ram)=='a7fa401e99806ad8b6c9be5004b98aaaa716194fc71e121f661fd2bfceaa4dad' and sha(iw)=='d7250d07c74b2ece6ea6ba4151a82b28d8b2657f720920e21683aa5812570280'
BASE,LIMIT=meta['ramReservation'];B=BASE+meta['bindingOffset'];ENTRY=B+252;V=BASE+meta['variantOffset'];TEMP=0x02028000;PAL=0x03003a60
custom=rom[meta['symbols']['ffta_art_custom_colors']-0x08000000+32:meta['symbols']['ffta_art_custom_colors']-0x08000000+64]
out=ROOT/'build/art/table-colors'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=collections.Counter();records=[];case=None
def check(name,a,b):checks[name]+=1;assert a==b,(case,name,repr(a)[:180],repr(b)[:180])
def call(a,pc,*args,residue=0):
 a.put(STACK+residue,struct.pack('<'+'I'*len(args[4:]),*args[4:]));return a.call(pc,*args[:4],stack=STACK+residue)
def machine(data):
 a=ARM(data,iw);a.put(0x02000000,ram);return a
def native(a):return a.read(0x03003860,0x1e09)
def outside(a):return a.read(0x02000000,TEMP-0x02000000)+a.read(TEMP+4096,BASE-TEMP-4096)+a.read(LIMIT,0x02040000-LIMIT)
def prepare(a,bank):
 call(a,meta['symbols']['ffta_art_bindings_reset'],B,meta['symbols']['ffta_art_custom_colors']);call(a,meta['symbols']['ffta_art_variants_reset'],V)
 tags,objects,banks=TEMP+256,TEMP+512,TEMP+1600
 a.put(tags,bytes([1]+[255]*127));a.put(objects,struct.pack('<4H',0,0x8000,bank<<12,0)+bytes(1016));a.put(banks,struct.pack('<10H',0,1<<bank,*([0]*8)))
 check('authenticated actual normal/dim source binding',call(a,meta['symbols']['ffta_art_variants_prepare'],V,B,tags,objects,banks,PAL,meta['symbols']['ffta_art_native_reference'],meta['symbols']['ffta_art_custom_colors'],BASE+meta['visibleColorsOffset']),2)
def dim(a,raw):
 a.put(TEMP+2048,raw);call(a,0x08148104,TEMP+2048,TEMP+2080,16,153);return a.read(TEMP+2080,32)
operations=[('table exposure',0x081474bc,p) for p in ((128,256,384),(0,0,0),(65535,0x10001,0x10100))]
operations += [('table blend',0x08147e28,p) for p in ((0x421f,8,8),(0,0,16),(0x17fff,0x100ff,0x10010))]
try:
 for (name,pc,params),bank,uniform,duration,interrupt,residue,offset in itertools.product(operations,(0,9),(False,True),(0,1,8,17),(False,True),(0,4),(0,5)):
  case=(name,params,bank,uniform,duration,interrupt,residue,offset)
  a,n,o=machine(rom),machine(old),machine(old);index=256+bank*16;address=0x03003860+index*2
  native_base=old[0x419d60:0x419d80];generated=custom
  if bank==9:native_base=dim(a,native_base);generated=dim(a,generated)
  for m,base in ((a,native_base),(n,native_base),(o,generated)):m.put(address,base)
  prepare(a,bank)
  if interrupt:
   tasks=[call(m,0x08147a7c,index,16,17) for m in (a,n,o)]
   for tick in range(3):
    for m,t in zip((a,n,o),tasks):call(m,0x08148740,t)
  first=index-offset;count=16+offset;payloads=[]
  for m,base in ((a,native_base),(n,native_base),(o,generated)):
   payload=m.read(0x03003860+first*2,offset*2)+(b'\x34\x12'*16 if uniform else base)
   m.put(TEMP,payload);payloads.append(payload)
  before=a.read(ENTRY,32);counters=struct.unpack('<3I',a.read(B+2840,12))
  tasks=[call(m,pc,first,count,duration,TEMP,*params,residue=residue) for m in (a,n,o)]
  check('complete native setter state and task exact',(tasks[0],native(a)),(tasks[1],native(n)))
  check('table transform never alters generated starting colors',a.read(ENTRY,32),before)
  check('generated target exactly original table conversion',a.read(ENTRY+32,32),b''.join(o.read(0x03003e68+(index+i)*12,2) for i in range(16)))
  for m,payload in zip((a,n,o),payloads):check('all source-table bytes unchanged',m.read(TEMP,len(payload)),payload)
  for tick in range(max(1,duration)):
   for m,t in zip((a,n,o),tasks):call(m,0x08148740,t,residue=residue)
   check('complete native callback state exact',native(a),native(n))
   check('generated callback colors exactly original oracle',a.read(ENTRY,32),o.read(address,32))
  check('exact supported completion counts',struct.unpack('<3I',a.read(B+2840,12)),(counters[0]+1,counters[1]+1,0))
  check('no writes outside art reservation or declared test inputs',outside(a),outside(n))
  records.append(dict(operation=name,parameters=params,bank=bank,uniform=uniform,duration=duration,interrupted=interrupt,stackResidue=residue,prefixColors=offset))
 for name,pc,params in operations:
  for first,count,duration,unknown,expected in ((256,16,8,True,1),(257,15,8,False,1),(256,15,8,False,1),(256,16,256,False,1),(0,16,8,False,0)):
   case=('refusal',name,first,count,duration,unknown);a,n=machine(rom),machine(old);prepare(a,0)
   payload=bytearray(old[0x419d60:0x419d80]);payload[2]^=1 if unknown else 0
   for m in (a,n):m.put(TEMP,payload)
   before=a.read(ENTRY,212)
   tasks=[call(m,pc,first,count,duration,TEMP,*params) for m in (a,n)]
   check('refused case preserves native operation',(tasks[0],native(a)),(tasks[1],native(n)))
   check('refused case cannot invent generated targets',a.read(ENTRY,212),before)
   check('unknown partial duration boundaries explicitly counted',a.word(B+2848),expected)
 report=dict(status='passed',romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records,source=str(source),scope='ARMv4T two seven-argument source-table setters, normal/dim authenticated baselines and uniform sources, prefixed table ranges, parameter truncation, both stack alignments, immediate source immutability, interruptions/durations, exact original native and generated target/callback oracle, unknown/partial/duration/unowned boundaries. No live hardware, arbitrary transformed table identities, all classes/capacity or natural scene acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n');print(out);raise
