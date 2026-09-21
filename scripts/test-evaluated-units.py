"""Explicit ephemeral law/stack unit owners; native evaluators remain effect-free."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
P=ROOT/'build/expansion/probes';OUT=P/'evaluated-units';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha1(b).hexdigest();word=lambda b,p:struct.unpack_from('<I',b,p)[0]
base=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());engine=(ROOT/'build/expansion/engine.bin').read_bytes();assert sha(base)==meta['romSha1'] and sha(engine)==meta['engineSha1']
old={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
JOB='--job-state' in sys.argv
CURRENT='--current' in sys.argv or JOB
FRAME=304 if JOB else 276
if CURRENT:
 symbols=old;binary=engine;image=bytearray(base)
 if JOB:
  job_meta=json.loads((P/'job-state/current.json').read_text())
  image=bytearray(pathlib.Path(job_meta['path']).read_bytes());assert sha(image)==job_meta['romSha1']
  symbols={**old,**job_meta['symbols']};OUT=pathlib.Path(job_meta['path']).parent/'evaluated-tests';OUT.mkdir(exist_ok=True)
  binary=(P/'job-state'/job_meta['baseSha1']/'state.bin').read_bytes()
else:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 sources=['persistent.c','unit-copies.c','battle-state.c','blade-wound.c','evaluated-units.c','evaluated-units.s','physical-riders.c','runtime.c']
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091c0000','-Wl,-e,ffta_evaluated_allocate',*[str(ROOT/'src/engine'/s) for s in sources],'-lgcc','-o',str(OUT/'isolated.elf')],check=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'isolated.elf'),str(OUT/'isolated.bin')],check=True)
 symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'isolated.elf')],text=True).splitlines() if len(p:=l.split())==3}
 image=bytearray(base);binary=(OUT/'isolated.bin').read_bytes();assert set(image[0x11c0000:0x11c0000+len(binary)])=={255};image[0x11c0000:0x11c0000+len(binary)]=binary
 for name in ('ffta_on_unit_copy','ffta_on_unit_clear','ffta_owned_exposed','ffta_copy_owner_free','ffta_clear_copy_extra','ffta_physical_rider_reference'):
  p=old[name]-0x08000000
  if p%4:struct.pack_into('<HHHI',image,p,0x46c0,0x4b00,0x4718,symbols[name]|1)
  else:struct.pack_into('<HHI',image,p,0x4b00,0x4718,symbols[name]|1)
 for p,size,name,expected in [(0x1347d0,12,'ffta_law_actor_a','84256d00281ceef633f88046'),(0x1347dc,8,'ffta_law_target_a','281ceef62ff8061c'),(0x13488c,12,'ffta_law_actor_b','84246400201cedf6d5ff071c'),(0x134898,8,'ffta_law_target_b','201cedf6d1ff061c')]:
  assert image[p:p+size].hex()==expected
  struct.pack_into('<HHI',image,p,0x4800,0x4700,symbols[name]|1)
  for offset in range(p+8,p+size,2):struct.pack_into('<H',image,offset,0x46c0)
if not CURRENT:
 builder_input=bytearray(image);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
 for offset,size in [(0x1347d0,12),(0x1347dc,8),(0x13488c,12),(0x134898,8)]:builder_input[offset:offset+size]=clean[offset:offset+size]
 (OUT/'builder-input.gba').write_bytes(builder_input);(OUT/'symbols.json').write_text(json.dumps(symbols))
 js="import fs from 'node:fs'; const {patchEvaluatedUnits}=await import(process.argv[1]); const rom=fs.readFileSync(process.argv[2]); patchEvaluatedUnits(rom,JSON.parse(fs.readFileSync(process.argv[3]))); fs.writeFileSync(process.argv[4],rom);"
 subprocess.run(['node','--input-type=module','-e',js,(ROOT/'scripts/patch-evaluated-units.mjs').as_uri(),str(OUT/'builder-input.gba'),str(OUT/'symbols.json'),str(OUT/'builder-output.gba')],check=True)
 assert (OUT/'builder-output.gba').read_bytes()==image,'Production patch helper differs from tested installation'
ROM=OUT/('current.gba' if CURRENT else 'isolated.gba');ROM.write_bytes(image)
snapshot=P/'chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-exec-seed0'
if JOB:
 snapshot=pathlib.Path(job_meta['path']).parent/'fixture'
 assert sha((snapshot/'frozen.gba').read_bytes())==job_meta['romSha1']
 ram=(snapshot/'battle-ready.ram').read_bytes();iwram=(snapshot/'battle-ready.iwram').read_bytes()
else:
 ram=(snapshot/'after.ram').read_bytes();iwram=(snapshot/'after.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
control=bytearray(image if JOB else base)
if CURRENT:
 clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
 for offset,size,name in [(0x1347d0,12,'ffta_law_actor_a'),(0x1347dc,8,'ffta_law_target_a'),(0x13488c,12,'ffta_law_actor_b'),(0x134898,8,'ffta_law_target_b')]:
  assert word(image,offset+4)==symbols[name]|1,'Installed law allocation hook mismatch'
  control[offset:offset+size]=clean[offset:offset+size]
a=ARM(bytes(image),iwram);native=ARM(bytes(control),iwram);checks={};observed=[]
alignments=[]
def alignment(u,pc,size,data):alignments.append(u.reg_read(UC_ARM_REG_SP)%8)
for name in ('ffta_evaluated_allocate','ffta_evaluated_init','ffta_evaluated_retire_heap'):
 a.u.hook_add(UC_HOOK_CODE,alignment,begin=symbols[name],end=symbols[name])
def check(label,got,want):assert got==want,(label,got,want);checks[label]=checks.get(label,0)+1
def call(name,*args,**kwargs):return a.call(symbols[name],*args,**kwargs)
def address(p):return call('ffta_owned_exposed',p)
def wound(p):return call('ffta_owned_wound',p)
def init(size=0x27000):
 a.put(0x02000000,bytes(0x40000));a.put(0x02001e70,b'FFTAEXP1\x01');a.put(0x0200f434,struct.pack('<I',0x02018000));a.call(0x080070c8,0x02018000,size)
 if JOB:call('ffta_job_reset')
entry=word(image,0x36d4bc);clear=word(image,0x36d4b8)
for residue in (0,4):
 init();a.put(UNIT,ram[0x80:0x188]);a.put(address(UNIT),b'\x01');a.put(wound(UNIT),b'\x23\x81')
 p=call('ffta_evaluated_allocate',264,stack=STACK+residue);check('actual allocated size',a.call(0x0800717c,0,p),FRAME)
 check('new law empty state',a.read(address(p),1),b'\0');a.call(entry,p,UNIT,264,stack=STACK+residue);check('law copy state',a.read(address(p),1),b'\1')
 check('law wound copied',a.read(wound(p),2),b'\x23\x81');a.put(wound(p),b'\x45\x42');check('law wound independent',a.read(wound(UNIT),2),b'\x23\x81')
 a.put(address(p),b'\0');check('law source isolated',a.read(address(UNIT),1),b'\1')
 # Independent nested stack scopes, copied from both canonical and law owners.
 for scope,source,value in [(0x03007300,UNIT,1),(0x03007500,p,0)]:
  check('stack initialize',call('ffta_evaluated_init',scope,source,stack=STACK+residue),1)
  check('stack native copy',a.read(scope,264),a.read(source,264));check('stack state copied',a.read(address(scope),1),bytes([value]))
  check('stack wound copied',a.read(wound(scope),2),a.read(wound(source),2))
  a.put(address(scope),bytes([1-value]));check('stack source isolated',a.read(address(source),1),bytes([value]))
 check('nested scopes independent',a.read(address(0x03007300),1),b'\0')
 check('nested scope copy',call('ffta_evaluated_init',0x03007700,0x03007300),1)
 a.put(address(0x03007300),b'\1');check('nested copied state independent',a.read(address(0x03007700),1),b'\0')
 call('ffta_evaluated_close',0x03007300);check('nested source retirement isolated',a.read(address(0x03007700),1),b'\0');call('ffta_evaluated_close',0x03007700)
 check('below active stack rejected',call('ffta_evaluated_init',0x03006a00,UNIT),0)
 for scope in (0x03007500,0x03007300):call('ffta_evaluated_close',scope);check('closed stack rejected',address(scope),0);check('stack tag erased',a.read(scope+264,9),bytes(9))
 before=a.read(0x03007300,FRAME);check('null init fails',call('ffta_evaluated_init',0x03007300,0),0);check('failed init unchanged',a.read(0x03007300,FRAME),before)
 a.put(address(p),b'\x01');a.call(clear,p,263);check('partial law clear retains',a.read(address(p),1),b'\1');a.call(clear,p,264);check('whole law clear resets',a.read(address(p),1),b'\0')
 check('whole law clear wound',a.read(wound(p),2),bytes(2))
 a.call(0x08022854,p,stack=STACK+residue);check('freed law rejected',address(p),0)
 check('freed law wound rejected',wound(p),0)
 recycled=a.call(0x08022840,FRAME);check('unregistered reuse rejected',address(recycled),0)
 # A copied tag at an interior payload position is not an allocation owner.
 large=a.call(0x08022840,600);fake=large+4;a.put(fake+264,struct.pack('<IIB3x',0x31564546,fake,1));check('interior fake rejected',address(fake),0)
 check('unregistered AP stays unowned',call('ffta_owned_extra_ap',recycled,144),0)
 init(280);check('allocation failure',call('ffta_evaluated_allocate',264),0)

TARGET=0x020033e4;LAW=0x0203e000;CTX=0x0200f3f0
alignments.clear()
# Real native law functions, including the four installed allocation sites.
def allocated(ram):
 base=word(ram,0xf434)-0x02000000;block=base+8;result=[]
 for _ in range(16384):
  marker=ram[block+4:block+6];assert marker in (b'la',b'ps')
  if marker==b'la':result.append((block,struct.unpack_from('<H',ram,block+6)[0]))
  following=struct.unpack_from('<H',ram,block+2)[0]
  if not following:return result
  block=base+following*4
 raise AssertionError('heap cycle')
def outer(m,action,residue,kind=15,heapsize=None):
 m.put(0x02000000,ram);m.put(0x03000000,iwram);m.put(0x02001e70,b'FFTAEXP1\x01');m.put(0x02001e98,bytes(i%2 for i in range(36)));m.put(0x02001e98,b'\x01')
 m.put(UNIT+0x2a,struct.pack('<5H',453,0,0,0,0));m.put(TARGET+0xeb,b'\x02');m.put(TARGET+0xde,b'\x0d')
 m.put(0x02001ebc,b'\x23\x81');m.put(0x02001ebc+28*2,b'\x45\x42')
 if JOB:
  if heapsize is None:heapsize=0x27000
  m.put(0x0203ff48,bytes(4));m.put(0x0203f400,struct.pack('<I',0x32534a46)+bytes(12)+bytes((i*23+7)&255 for i in range(792)))
 if heapsize is not None:
  m.put(0x0200f434,struct.pack('<I',0x02018000));m.call(0x080070c8,0x02018000,heapsize)
 m.put(LAW,bytes([0,0,0,0,kind,25,0,0,0,0,0,0]));m.put(STACK+residue,struct.pack('<4I',0,453,0,LAW));before=m.read(0x02000000,0x40000)
 events=[]
 def inspect(u,pc,size,data):
  actor=u.reg_read(UC_ARM_REG_R0);target=u.reg_read(UC_ARM_REG_R1)
  # The explicit tail itself is independently checked at actual native entry;
  # avoid re-entering this same Unicorn while its function is running.
  events.append((actor,target,m.read(actor+264,FRAME-264),m.read(target+264,FRAME-264)))
 hook=m.u.hook_add(UC_HOOK_CODE,inspect,begin=0x081342cc,end=0x081342cc)
 try:value=m.call(0x081343c8,UNIT,TARGET,action,0,stack=STACK+residue)
 finally:m.u.hook_del(hook)
 after=m.read(0x02000000,0x40000)
 check('law no heap leak',allocated(after),allocated(before));check('law root and guard unchanged',after[0x3ff30:],before[0x3ff30:])
 check('law AP and preferences unchanged',after[0x1b40:0x1e98],before[0x1b40:0x1e98]);check('law live state unchanged',after[0x1e98:0x1ebc],before[0x1e98:0x1ebc]);check('law source units unchanged',after[0x80:0x1940]+after[0x2fc4:0x3c24],before[0x80:0x1940]+before[0x2fc4:0x3c24])
 check('law live wounds unchanged',after[0x1ebc:0x1f04],before[0x1ebc:0x1f04])
 if JOB:check('law live job records unchanged',after[0x3f400:0x3f728],before[0x3f400:0x3f728])
 return value,events,m.read(0x030034b0,4),before,after
for residue in (0,4):
 for action in range(347):
  old_result=outer(native,action,residue);new_result=outer(a,action,residue)
  check('all native law results/RNG',(new_result[0],new_result[2]),(old_result[0],old_result[2]))
  for actor,target,actor_tail,target_tail in new_result[1]:
   check('actual law actor owned',actor_tail[:8],struct.pack('<II',0x31564546,actor));check('actual law target owned',target_tail[:8],struct.pack('<II',0x31564546,target))
   check('actual law state copied',(actor_tail[8],target_tail[8]),(1,0))
   check('actual law wounds copied',(actor_tail[9:11],target_tail[9:11]),(b'\x23\x81',b'\x45\x42'))
   if JOB:
    check('actual law job records copied',(actor_tail[12:34],target_tail[12:34]),(bytes((i*23+7)&255 for i in range(22)),bytes((i*23+7)&255 for i in range(28*22,29*22))))
    check('actual law origin copied',(actor_tail[34],target_tail[34]),(1,29))
   check('law actor retired',address(actor),0);check('law target retired',address(target),0)
  observed.append(len(new_result[1]))
 for kind in (15,16):
  for size in (280,560,0x27000):
   result=outer(a,427,residue,kind,size)
   if size<600:check('outer allocation failure returns false',result[0],0);check('failure no evaluation',len(result[1]),0)
   else:check('both law branches evaluated',len(result[1]),1 if kind==15 else 21)
assert sum(observed)>0,'Vacuous native law coverage'
# Actual Shatter formula observes the registered stack owner then retires it.
for residue in (0,4):
 a.put(0x02000000,ram);a.put(0x03000000,iwram);a.put(0x02001e70,b'FFTAEXP1\x01');a.put(0x02001e98+28,b'\x01')
 a.put(CTX,struct.pack('<IIIHH',UNIT,TARGET,TARGET,427,453));a.put(TARGET+0xeb,b'\x02');seen=[]
 def predicted(u,pc,size,data):
  p=u.reg_read(UC_ARM_REG_R1);seen.append((p,a.read(p+264,12),a.read(p+0xeb,1)))
 hook=a.u.hook_add(UC_HOOK_CODE,predicted,begin=0x0812fe38,end=0x0812fe38)
 try:a.call(old['ffta_physical_rider_reference_entry'],CTX,453,0,stack=STACK+residue)
 finally:a.u.hook_del(hook)
 assert len(seen)==1;pointer,tail,protect=seen[0];retired_tail=a.read(pointer+264,9)
 check('Shatter actual stack scope tag',tail[:8],struct.pack('<II',0x31564546,pointer));check('Shatter predicted Exposed',tail[8],1);check('Shatter removes Protect only in copy',protect,b'\0');check('Shatter scope retired',address(pointer),0);check('Shatter tag erased after return',retired_tail,bytes(9))
check('all native C entries aligned',any(alignments),False);assert len(alignments)>0
report={'passed':True,'current':CURRENT,'baseSha1':sha(base),'romSha1':sha(image),'binarySha1':sha(binary),'checks':checks,'total':sum(checks.values()),'alignedNativeEntries':len(alignments),'nativeLawEvaluations':sum(observed),'scope':'Independent ephemeral Exposed storage only; no damage/event integration'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
