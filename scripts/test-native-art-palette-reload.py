"""Actual native copy callback reloads, fade continuation and unrelated copies."""
import ast,collections,datetime,hashlib,itertools,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
arm_source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000')
arm_source=arm_source.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/live-palette/poc.json').read_text());rom=Path(meta['path']).read_bytes();old=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(old).hexdigest()==meta['baseRomSha1']
source=ROOT/'build/art/live-palette/battle/20260918T075021.733381Z';ram=(source/'candidate-ready.ram').read_bytes();iw=(source/'candidate-ready.iwram').read_bytes()
assert sha(ram)=='a7fa401e99806ad8b6c9be5004b98aaaa716194fc71e121f661fd2bfceaa4dad' and sha(iw)=='d7250d07c74b2ece6ea6ba4151a82b28d8b2657f720920e21683aa5812570280'
BASE,LIMIT=meta['ramReservation'];B=BASE+meta['bindingOffset'];ENTRY=B+252;V=BASE+meta['variantOffset'];PAL=0x03003a60;TEMP=0x02028000
out=ROOT/'build/art/palette-reload'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=collections.Counter();records=[];case=None
def check(name,a,b):checks[name]+=1;assert a==b,(case,name,repr(a)[:200],repr(b)[:200])
def machine(data):
 a=ARM(data,iw);a.put(0x02000000,ram);return a
def copy(a,dst,src,count,residue=0):return a.call(a.word(0x0836d4bc),dst,src,count,stack=STACK+residue)
def native(a):return a.read(0x03003860,0x1e09)
def other(a):return a.read(0x02000000,BASE-0x02000000)+a.read(LIMIT,0x02040000-LIMIT)
try:
 check('authenticated actual deployment copy call',old[0x2c122:0x2c134].hex(),'0f4a49010f4840181368211c202216f18ef8')
 check('native copy return register is caller continuation',iw[0x5f20:0x5f26].hex(),'10bc01bc0047')
 # The old default Unicorn CPU silently accepted ARMv5-style LDR-PC
 # interworking. Use its ARMv4T TI925T model and require rejection of the
 # exact retained bad veneer before relying on the corrected positive cases.
 badmeta=json.loads((ROOT/'build/art/live-palette/1ee4c46b4c91acd9c6b34dba8d73d2e8096ea175/manifest.json').read_text())
 badrom=Path(badmeta['path']).read_bytes();assert hashlib.sha1(badrom).hexdigest()==badmeta['romSha1']
 bad=machine(badrom);modes=[]
 def mode(u,pc,size,data):modes.append(bool(u.reg_read(UC_ARM_REG_CPSR)&32));u.emu_stop()
 bad.u.hook_add(UC_HOOK_CODE,mode,begin=0x091046c8,end=0x091046c8)
 bad.u.reg_write(UC_ARM_REG_R0,PAL);bad.u.reg_write(UC_ARM_REG_R1,0x08419d60);bad.u.reg_write(UC_ARM_REG_R2,32)
 bad.u.reg_write(UC_ARM_REG_SP,STACK);bad.u.reg_write(UC_ARM_REG_LR,RETURN|1)
 bad.u.emu_start(bad.word(0x0836d4bc),RETURN,count=10000)
 check('ARMv4T negative control catches retained invalid Thumb entry',modes,[False])
 for dim,completed,residue in itertools.product((False,True),(False,True),(0,4)):
  case=('reload',dim,completed,residue);a,n,o=machine(rom),machine(old),machine(old)
  colors=a.read(ENTRY,32);o.put(PAL,colors)
  # Original conversion creates both native and generated dim inputs.
  for m in (a,n,o):
   m.put(TEMP,old[0x419d60:0x419d80]);m.put(TEMP+64,colors)
   if dim:
    m.call(0x08148104,TEMP,TEMP+32,16,153);m.call(0x08148104,TEMP+64,TEMP+96,16,153)
   else:m.put(TEMP+32,m.read(TEMP,32));m.put(TEMP+96,colors)
  tasks=[m.call(0x08147a7c,256,16,17) for m in (a,n,o)];advance=17 if completed else 3
  for tick in range(advance):
   for m,t in zip((a,n,o),tasks):m.call(0x08148740,t)
  preserved=a.read(ENTRY+32,180)+a.read(ENTRY+244,8)
  result=copy(a,PAL,TEMP+32,32,residue);control=copy(n,PAL,TEMP+32,32,residue);copy(o,PAL,TEMP+96,32,residue)
  check('native copy return and all native effect state exact',(result,native(a)),(control,native(n)))
  check('generated current colors reload exactly',a.read(ENTRY,32),o.read(PAL,32))
  check('reload preserves fade target errors remaining and task',a.read(ENTRY+32,180)+a.read(ENTRY+244,8),preserved)
  check('native baseline and brightness refresh',(a.read(ENTRY+212,32),a.read(V+11,1)),(a.read(PAL,32),bytes([19 if dim else 32])))
  check('display source colors refresh',a.read(B+2520+32,32),a.read(ENTRY,32))
  check('reload does not preempt hardware palette latch',a.read(BASE+meta['visibleColorsOffset'],320),ram[BASE-0x02000000+meta['visibleColorsOffset']:BASE-0x02000000+meta['visibleColorsOffset']+320])
  check('no extra refusal',a.word(B+2848),0)
  check('no other gameplay memory change',other(a),other(n))
  for tick in range(advance,17):
   for m,t in zip((a,n,o),tasks):m.call(0x08148740,t)
   check('active reload native continuation exact',native(a),native(n))
   check('active reload generated continuation exact',a.read(ENTRY,32),o.read(PAL,32))
  records.append(dict(dim=dim,completed=completed,stackResidue=residue,afterCopy=sha(a.read(ENTRY,32))))
 # Same shared callback still owns canonical copy notifications. Compare
 # complete native outputs for whole/partial unit copies, BG, ordinary RAM,
 # a span ending exactly at OBJ shadow, and zero-length copies.
 for dst,src,size in ((UNIT+264,UNIT,264),(UNIT+264+24,UNIT+24,8),(0x03003860,0x08419d60,32),(TEMP,UNIT,264),(PAL-32,0x08419d60,32),(PAL,0x08419d60,0)):
  for residue in (0,4):
   case=('unrelated',hex(dst),size,residue);a,n=machine(rom),machine(old)
   check('unrelated original return exact',copy(a,dst,src,size,residue),copy(n,dst,src,size,residue))
   check('unrelated full EWRAM including owned job state exact',a.read(0x02000000,0x40000),n.read(0x02000000,0x40000))
   check('unrelated IWRAM below call stack exact',a.read(0x03000000,0x7000),n.read(0x03000000,0x7000))
 for dst,size,unknown in ((PAL,2,False),(PAL+1,31,False),(PAL,32,True)):
  case=('refuse',dst,size,unknown);a,n=machine(rom),machine(old)
  for m in (a,n):m.put(TEMP,b'\x34\x12'*16 if unknown else old[0x419d60:0x419d80])
  before=a.read(ENTRY,212);copy(a,dst,TEMP,size);copy(n,dst,TEMP,size)
  check('refused reload preserves original copy',native(a),native(n))
  check('refused reload does not invent generated colors',a.read(ENTRY,212),before)
  check('refused reload retires stale ownership',(a.read(V+1,1),a.word(ENTRY+248),a.word(ENTRY+244)),(b'\xff',255,0))
  check('refused reload explicit diagnostics',(a.word(B+2848),a.word(BASE+meta['refusalOffset'])),(1,1))
 case=('retire dormant variant',);a=machine(rom)
 # Plan.requested at offset2594 is the prior authenticated displayed-slot
 # mask. This slot is no longer present, although its history is retained.
 a.put(BASE+2594,bytes(2));a.put(TEMP,b'\x34\x12'*16);copy(a,PAL,TEMP,32)
 check('dormant unknown reload retires history without visible refusal',(a.read(V+1,1),a.word(ENTRY+248),a.word(B+2848)),(b'\xff',255,0))
 tags,objects,banks=TEMP+64,TEMP+192,TEMP+1216
 a.put(tags,bytes([1]+[255]*127));a.put(objects,struct.pack('<4H',0,0x8000,0,0)+bytes(1016));a.put(banks,struct.pack('<10H',0,1,*([0]*8)))
 arguments=[V,B,tags,objects,banks,PAL,meta['symbols']['ffta_art_native_reference'],meta['symbols']['ffta_art_custom_colors'],BASE+meta['visibleColorsOffset']]
 a.put(STACK,struct.pack('<5I',*arguments[4:]));result=a.call(meta['symbols']['ffta_art_variants_prepare'],*arguments[:4])
 check('dormant retirement cannot authenticate a future unknown appearance',result,0)
 report=dict(status='passed',romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records,source=str(source),scope='Actual authenticated native deployment copy callback, completed/active fade reloads with normal/dim native conversion and exact independent generated-color native continuation, unchanged latch, all nonreserved gameplay memory, both stack alignments and original unit/partial/unowned copies. Explicit displayed partial/unknown refusal and dormant retirement requiring future reauthentication. Not live hardware reload/late entry or every copy mechanism.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n');print(out);raise
