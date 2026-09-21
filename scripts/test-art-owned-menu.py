"""Native party allocation, full expanded list, copy tail and teardown bounds."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native party ARM>','exec'))
m=json.loads((ROOT/'build/art/connected/current.json').read_text());rom=Path(m['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==m['romSha1']
live=m['components']['livePalette'];contract=live['partyList']
iw=(Path(m['fixtureSource']).parent/'fixture/battle-ready.iwram').read_bytes()
out=ROOT/'build/art/owned-menu/native'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 for mode in (0,1):
  for residue in (0,4):
   a=ARM(rom,iw);a.u.mem_map(0x05000000,0x1000)
   # Actual scene child heap size, at both a world and a movable battle address.
   for heap in (0x0200f3a4,0x02021000):
    a.put(0x02000000,bytes(0x40000));a.put(0x02001e70,b'FFTAEXP1\x01')
    a.put(heap-4,b'\xd7'*4);a.put(heap+contract['parentBytes'],b'\xe9'*4)
    a.put(0x03002778,struct.pack('<I',heap));a.put(0x03000e54,struct.pack('<I',contract['parentBytes']))
    a.put(0x0203c000,b'\xa5'*0x3000)
    def cpu_set(u,pc,size,data):
     src,dst,control=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
     width=4 if control&(1<<26) else 2;count=control&0x1fffff
     a.put(dst,a.read(src,width)*count if control&(1<<24) else a.read(src,width*count))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    hook=a.u.hook_add(UC_HOOK_CODE,cpu_set,begin=0x0814186c,end=0x0814186c)
    a.call(0x0807109c,mode,stack=STACK-residue);a.u.hook_del(hook)
    ctx=a.word(0x03002818);p=a.word(ctx+0x2d50);label=str((mode,residue,hex(heap)))
    check(a.call(0x0800717c,0,ctx)==contract['ownerBytes'],label+' actual native context allocation')
    check(p==ctx+contract['offset'] and p+contract['bytes']==ctx+contract['ownerBytes'],label+' list belongs to context tail')
    check(a.read(ctx+0x7240,64)==bytes(64),label+' existing AP/status/job-copy tail initialized')
    # Deliberate component worst case: all 460 IDs owned and typed as weapons.
    # Only the test machine item-type bytes change; no on-disk ROM is patched.
    table=a.word(0x08079aec)
    for ident in range(1,461):
     a.put(table+ident*32+8,b'\x02');a.call(0x080ca900,ident,1)
    a.put(p+0x230+460*20,b'\xd3'*16)
    tail=a.read(ctx+0x7240,64);units=a.read(0x02000080,0x1df0)
    count=a.call(0x0808cbdc,2,p,stack=STACK-residue)
    check(count==a.word(p)==460,label+' full 460-row native inventory')
    check([a.word(p+0x234+20*i) for i in range(count)]==list(range(1,461)),label+' exact ordered full-width IDs')
    check(a.read(p+0x230+460*20,16)==b'\xd3'*16,label+' maximum list upper fence')
    check(a.read(ctx+0x7240,64)==tail and a.read(0x02000080,0x1df0)==units,label+' list preserves player data and copy tail')
    check(a.read(0x0203c000,0x3000)==b'\xa5'*0x3000,label+' palette reservation untouched')
    a.call(0x08071234,mode,stack=STACK-residue)
    check(a.word(0x0203ff40)==0,label+' native teardown retires party owner')
    check(a.read(heap-4,4)==b'\xd7'*4 and a.read(heap+contract['parentBytes'],4)==b'\xe9'*4,label+' scene heap fences')
 report=dict(status='passed',romSha1=m['romSha1'],checks=checks,scope='Actual constructor/destructor, both party modes and stack residues at world and movable battle heap addresses; synthetic all460 weapon inventory capacity, native allocator and copy-tail/palette fences. Does not prove in-battle parent allocation capacity or full gameplay.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=m['romSha1'],checks=checks,error=str(error)),indent=2)+'\n')
 print('Artifacts: '+str(out));raise
