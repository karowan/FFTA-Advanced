"""ARMv4T late first appearance, effect-history retention and absent DMA latch.

Runs actual installed setters/callbacks against an independent original-engine
oracle. The compositor portion uses the previously authenticated synchronous
DMA0 model; it is not live mGBA scheduler or natural scene-entry acceptance.
"""
import ast,collections,datetime,hashlib,itertools,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
code=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')
code=code.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(code)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARMv4T>','exec'))
meta=json.loads((ROOT/'build/art/live-palette/poc.json').read_text())
rom=Path(meta['path']).read_bytes();old=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(old).hexdigest()==meta['baseRomSha1']
source=ROOT/'build/art/live-palette/battle/20260918T075021.733381Z'
ram=(source/'candidate-ready.ram').read_bytes();iw=(source/'candidate-ready.iwram').read_bytes()
assert sha(ram)=='a7fa401e99806ad8b6c9be5004b98aaaa716194fc71e121f661fd2bfceaa4dad'
assert sha(iw)=='d7250d07c74b2ece6ea6ba4151a82b28d8b2657f720920e21683aa5812570280'
BASE,LIMIT=meta['ramReservation'];B=BASE+meta['bindingOffset'];V=BASE+meta['variantOffset'];ENTRY=B+252
PAL=0x03003a60;TEMP=0x02028000;VISIBLE=BASE+meta['visibleColorsOffset']
custom=rom[meta['symbols']['ffta_art_custom_colors']-0x08000000+32:meta['symbols']['ffta_art_custom_colors']-0x08000000+64]
out=ROOT/'build/art/late-entry'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=collections.Counter();records=[];case=None

def check(name,a,b):checks[name]+=1;assert a==b,(case,name,repr(a)[:180],repr(b)[:180])
def call(a,pc,*args,residue=0):
 a.put(STACK+residue,struct.pack('<'+'I'*len(args[4:]),*args[4:]));return a.call(pc,*args[:4],stack=STACK+residue)
def machine(data):
 a=ARM(data,iw);a.put(0x02000000,ram)
 for address,size in ((0x04000000,0x1000),(0x05000000,0x1000),(0x06000000,0x18000),(0x07000000,0x1000)):a.u.mem_map(address,size)
 return a
def native(a):return a.read(0x03003860,0x1e09)
def outside(a):
 # TEMP..TEMP+2048 contains declared independent oracle/appearance arguments.
 return a.read(0x02000000,TEMP-0x02000000)+a.read(TEMP+2048,BASE-TEMP-2048)+a.read(LIMIT,0x02040000-LIMIT)
def reset(a):
 a.put(BASE,bytes(4));call(a,meta['symbols']['ffta_art_heap_reset'])
def prepare(a,bank=0):
 tags,objects,banks=TEMP+256,TEMP+512,TEMP+1600
 a.put(tags,bytes([1]+[255]*127));a.put(objects,struct.pack('<4H',0,0x8000,bank<<12,0)+bytes(1016))
 a.put(banks,struct.pack('<10H',0,1<<bank,*([0]*8)))
 return call(a,meta['symbols']['ffta_art_variants_prepare'],V,B,tags,objects,banks,PAL,
  meta['symbols']['ffta_art_native_reference'],meta['symbols']['ffta_art_custom_colors'],VISIBLE)
def colors(a,values,dim):
 a.put(TEMP,values)
 if dim:call(a,0x08148104,TEMP,TEMP+64,16,153);return a.read(TEMP+64,32)
 return values
operations=[('black',0x08147a7c,()),('white',0x08147ad0,()),('gray',0x08147b28,()),
 ('tint',0x08147ba4,()),('rgb',0x08147c2c,(128,320,192)),('solid',0x08147cc0,(5,17,29)),('restore',0x08147d2c,(TEMP+128,)),
 ('blend',0x08147d94,(0x421f,8,8)),('brighten',0x08147ec8,(8,)),('darken',0x08147f50,(8,)),
 ('exposure',0x0814731c,(384,)),('exposure_rgb',0x081473e4,(128,256,384)),
 ('table_exposure',0x081474bc,(TEMP+128,128,256,384)),('table_blend',0x08147e28,(TEMP+128,0x421f,8,8))]
try:
 for (name,pc,args),dim,elapsed,residue in itertools.product(operations,(False,True),(0,3,17),(0,4)):
  case=(name,dim,elapsed,residue);a,n,o=machine(rom),machine(old),machine(old);reset(a)
  native_base=colors(a,old[0x419d60:0x419d80],dim);generated=colors(a,custom,dim)
  for m,base in ((a,native_base),(n,native_base),(o,generated)):
   m.put(PAL,base);m.put(TEMP+128,base)
  check('no character binding before command',a.read(V,10),bytes([255]*10))
  tasks=[call(m,pc,256,16,17,*args,residue=residue) for m in (a,n,o)]
  check('installed setter preserves complete native effect state',(tasks[0],native(a)),(tasks[1],native(n)))
  check('authenticated unseen class bound before native effect',(a.read(V+1,1),a.word(ENTRY+248),a.word(ENTRY+244)),(b'\x10',0,tasks[0]))
  for tick in range(elapsed):
   for m,t in zip((a,n,o),tasks):call(m,0x08148740,t,residue=residue)
  check('unseen generated colors follow original engine exactly',a.read(ENTRY,32),o.read(PAL,32))
  before=a.read(ENTRY,252);check('late appearance reuses authenticated effect history',prepare(a),2)
  check('appearance preserves all colors targets errors and task',a.read(ENTRY,252),before)
  for tick in range(elapsed,17):
   for m,t in zip((a,n,o),tasks):call(m,0x08148740,t,residue=residue)
   check('late continuation native state exact',native(a),native(n))
   check('late continuation generated colors exact',a.read(ENTRY,32),o.read(PAL,32))
  check('one effect completes with no refusal',struct.unpack('<3I',a.read(B+2840,12)),(1,1,0))
  check('no outside gameplay-memory changes',outside(a),outside(n))
  records.append(dict(operation=name,dim=dim,appearanceAfterTicks=elapsed,stackResidue=residue))
 # Another variant cannot replace an absent active or completed black history.
 for elapsed in (3,17):
  case=('history protection',elapsed);a=machine(rom);reset(a);a.put(PAL,old[0x419d60:0x419d80]*2)
  task=call(a,0x08147a7c,256,16,17)
  for tick in range(elapsed):call(a,0x08148740,task)
  before=a.read(ENTRY,252);check('new variant uses another slot',prepare(a,1),1)
  check('absent effect survives preferred-slot pressure',a.read(ENTRY,252),before)
  check('return to affected character restores exact history',prepare(a),2)
 case=('alternate-slot initial latch',);a=machine(rom);reset(a);a.put(PAL,old[0x419d60:0x419d80]*2)
 call(a,0x08147a7c,256,32,17)
 check('second pretracked bank has its own nonidentity slot',a.read(V,2),bytes([17,16]))
 check('first appearance before any tick or DMA uses correct source class',prepare(a,1),1)
 check('alternate slot baseline latch belongs to source class',a.read(VISIBLE,32),custom)
 case=('history capacity',);a=machine(rom);reset(a);a.put(PAL,old[0x419d60:0x419d80]*16)
 task=call(a,0x08147a7c,256,256,17)
 check('bounded pretracking fills ten slots only',sorted(a.read(V,10)),list(range(16,26)))
 before=a.read(V,20)+a.read(B,2852)
 check('eleventh appearance cannot evict active history',prepare(a,10),0)
 check('capacity refusal keeps all existing effects exact',a.read(V,20)+a.read(B,2852),before)
 case=('unknown prehistory',);a=machine(rom);reset(a);a.put(PAL,b'\x34\x12'*16)
 call(a,0x08147a7c,256,16,17)
 check('unknown source never gets speculative generated history',a.read(V,10),bytes([255]*10))
 check('unknown first appearance remains explicitly refused',prepare(a),0)
 # No actor emissions: DMA advances the saved displayed phase; skipped DMA
 # preserves it. Execute original compositor DMA completions synchronously.
 for skipped in (0,1):
  case=('absent latch',skipped);a=machine(rom);reset(a);a.put(PAL,old[0x419d60:0x419d80])
  task=call(a,0x08147a7c,256,16,17)
  for tick in range(3):call(a,0x08148740,task)
  prior=a.read(VISIBLE,320);expected=a.read(B+2520,320)
  a.put(0x03000e10,struct.pack('<H',skipped));a.put(0x04000006,struct.pack('<H',180))
  def dma(u,pc,size,data):
   src,dst,flags=struct.unpack('<3I',a.read(0x040000b0,12));count=(flags&65535)*4
   assert flags>>16==0x8400 and 0x03000000<=src<=0x03008000-count and 0x07000000<=dst<=0x07000400-count
   a.put(dst,a.read(src,count));a.put(0x040000b8,struct.pack('<I',flags&0x7fffffff))
  for pc in (0x08001322,0x08001396,0x080013e2,0x08001430):a.u.hook_add(UC_HOOK_CODE,dma,begin=pc,end=pc)
  call(a,0x080012bc)
  check('absent history respects actual palette-DMA decision',a.read(VISIBLE,320),prior if skipped else expected)
  check('tracking alone never allocates a hardware overlay',a.word(BASE+2572),0)
 report=dict(status='passed',romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records,
  scope='ARMv4T installed effect setters before first ownership, normal/dim palettes, fourteen operations, appearance at0/3/17 callbacks, exact original-engine native/generated continuation, both stack alignments, history retention across slot pressure, absent fresh/skipped DMA latch with synchronous native DMA model. Not actual mGBA late scene entry, all capacity/mixed-class/interruption cases, unknown prior effects or timing acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n');print(out);raise
