"""Native shared battle-menu heap lifecycle on the retained fragmented heap."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native party ARM>','exec'))
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<read-only heap>','exec'))
compact_test='--compact-status' in sys.argv
m=json.loads((ROOT/('build/art/live-palette/status-current.json' if compact_test else 'build/art/live-palette/shared-menu-current.json')).read_text());rom=Path(m['path']).read_bytes();S=m['symbols']
assert m['sharedBattleMenuHeap'] and hashlib.sha1(rom).hexdigest()==m['romSha1']
fixture=ROOT/'build/art/live-palette/battle/20260918T164311.010995Z';prior=json.loads((fixture/'observed.json').read_text())
assert prior['status']=='passed' and prior['romSha1']=='5ee3099323fe1af8b2348b772786435d1e011cb6'
ram=(fixture/'candidate-ready.ram').read_bytes();iw=(fixture/'candidate-ready.iwram').read_bytes()
assert sha(ram)=='efbc68638d0c7ee8ca38cfab4a1e877c3503aeed5b4e50d92497a9809060cca0'
assert sha(iw)=='a37927a10c0ecbb73f6e78ccc5bfabf621b574f4972f6ca92c9287207185e632'
out=ROOT/'build/art/owned-menu/shared-native'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];observations=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
def w32(a,p,v):a.put(p,struct.pack('<I',v))
try:
 for residue,compact,pressure in ([(r,c,p) for r in (0,4) for c,p in ((False,0),(True,0),(True,8192))] if compact_test else [(r,False,0) for r in (0,4)]):
  label=str((residue,compact,pressure));owner_bytes=0x7280 if compact else 0x9980;list_offset=0x4340 if compact else 0x7280;magic=0x50485232 if compact else 0x50485231
  a=ARM(rom,iw);a.u.mem_map(0x05000000,0x1000);a.put(0x02000000,ram)
  a.call(S['ffta_art_party_heap_reset'])
  if compact_test:
   a.call(S['ffta_art_party_mark_readonly'])
   check(a.word(m['partyHeapRoot'])==0,'Unowned menu cannot become compact '+label)
  if pressure:
   held=a.call(0x08022840,pressure,stack=STACK-residue)
   check(held!=0,'Extra pressure uses actual native allocation '+label)
   a.put(held,b'\x5a'*pressure)
  # Native Status first backs up its 1024-byte palette region. Reproduce that
  # actual allocation before testing the fragmented heap; no free-list edits.
  a.call(0x08022e24,stack=STACK-residue)
  before=a.read(0x02000000,0x40000);before_heap=heap(before);root=before_heap['base']
  check(before_heap['largestFree']==41640 and before_heap['freePayload']==53596-(pressure+12 if pressure else 0),'Retained live fragmentation and native Status backup '+label)
  payloads={b['address']+12:a.read(b['address']+12,b['payloadBytes']) for b in before_heap['allocationBlocks'] if b['marker']=='la'}
  check(a.call(S['ffta_art_party_parent_allocate'],stack=STACK-residue)==root,'Borrow exact live root '+str(residue))
  check(a.read(root,20)==before[root-0x02000000:root-0x02000000+20],'Borrow does not clear or allocate '+str(residue))
  if compact:a.call(S['ffta_art_party_mark_readonly'])
  check(a.call(S['ffta_art_party_parent_allocate'])==0,'Already owned parent cannot be borrowed twice '+label)
  state=m['partyHeapRoot'];claimed=a.read(state,16)
  for caller in (RETURN|1,0x080710b1,0x08071133,0x08071273,0x080712c1):
   check(a.call(S['ffta_art_party_heap_bypass'],root,caller)==0 and a.read(state,16)==claimed,'Unrelated/near-miss caller remains native '+str((residue,caller)))
  for caller in (0x080710b3,0x08071131,0x08071275,0x080712bf):
   check(a.call(S['ffta_art_party_heap_bypass'],root+4,caller)==0 and a.read(state,16)==claimed,'Wrong root cannot bypass '+str((residue,caller)))
  w32(a,0x03002778,root);w32(a,0x03000e54,0xed00)
  def cpu_set(u,pc,size,data):
   src,dst,control=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
   width=4 if control&(1<<26) else 2;count=control&0x1fffff
   a.put(dst,a.read(src,width)*count if control&(1<<24) else a.read(src,width*count))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  hook=a.u.hook_add(UC_HOOK_CODE,cpu_set,begin=0x0814186c,end=0x0814186c)
  a.call(0x0807109c,1,stack=STACK-residue);a.u.hook_del(hook)
  ctx=a.word(0x03002818);opened=heap(a.read(0x02000000,0x40000))
  check(a.call(0x0800717c,0,ctx)==owner_bytes,'Context actually allocated '+label)
  check(a.word(ctx)==root and a.word(ctx+0x2d50)==ctx+list_offset,'Context/list use owned native allocations '+label)
  check(struct.unpack('<4I',a.read(state,16))==(magic,root,1,0),'Only exact constructor bypassed '+label)
  check(opened['freePayload']==1068+(0x2700 if compact else 0)-(pressure+12 if pressure else 0),'Exact measured free headroom '+label)
  check(all(a.read(p,len(b))==b for p,b in payloads.items()),'All preexisting battle allocations byte-exact during menu '+str(residue))
  check(a.read(0x02000080,0x1df0)==before[0x80:0x1e70],'Roster inventory AP preserved '+str(residue))
  a.call(0x08071234,1,stack=STACK-residue)
  check(a.word(0x0203ff40)==0,'Party copy owner retired '+str(residue))
  check(struct.unpack('<4I',a.read(state,16))==(magic,root,1,1),'Only exact destructor skips outer clear '+label)
  check(heap(a.read(0x02000000,0x40000))==before_heap,'All native child allocations freed and free topology restored '+str(residue))
  a.call(S['ffta_art_party_parent_free'],root,stack=STACK-residue)
  check(a.word(state)==0 and a.read(root,20)==before[root-0x02000000:root-0x02000000+20],'Outer release retires borrowing without freeing battle heap '+str(residue))
  check(all(a.read(p,len(b))==b for p,b in payloads.items()),'All original allocations exact after round trip '+str(residue))
  observations.append(dict(stackResidue=residue,compact=compact,extraPressureBytes=pressure,before=before_heap,during=opened))
 scope='Native constructors/destructor and heap guards on exact retained fragmented memory with actual native Status palette backup. Original allocated payloads, free topology and copy roots preserved. '
 scope+=('Full-width fallback plus compact read-only ownership, including an extra 8192-byte native allocation. ' if compact_test else 'Full-width list ownership. ')
 scope+='Component clone, not resumed gameplay or maximum encounter capacity.'
 report=dict(status='passed',romSha1=m['romSha1'],checks=checks,observations=observations,source=dict(report=str(fixture/'observed.json'),ramSha256=sha(ram),iwramSha256=sha(iw)),scope=scope)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=m['romSha1'],checks=checks,error=str(error),observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
