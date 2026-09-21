"""Twenty-history prefix/publish semantics against the original full planner.

Pure deterministic compiled ARM execution: high IDs, exhaustion, no-tail bank0,
disabled entries, affine tail words, both stack alignments and ROM fallback.
No fixture/save/game route or performance acceptance is established here.
"""
import argparse,ast,datetime,json,struct,subprocess,sys,random
from pathlib import Path
from native_art import ROOT,sha
from art_palette_build import write_pixel_banks
from art_scoped_build import build_scoped
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
out=ROOT/'build/art/frame-high-slots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--fused-compose',action='store_true');parser.add_argument('--compact-leaves',action='store_true');parser.add_argument('--unrolled-copy',action='store_true');parser.add_argument('--packed-plan',action='store_true');parser.add_argument('--block-scan',action='store_true');parser.add_argument('--burst-scan',action='store_true');parser.add_argument('--joined-rows',action='store_true');parser.add_argument('--prepared-preference',action='store_true');parser.add_argument('--rect-conflict',action='store_true');args=parser.parse_args()
if args.rect_conflict:args.prepared_preference=True
if args.prepared_preference:args.burst_scan=True
if args.joined_rows:args.burst_scan=True
if args.burst_scan:args.block_scan=True
if args.block_scan:args.packed_plan=True
if args.packed_plan:args.unrolled_copy=True
if args.compact_leaves or args.unrolled_copy:args.fused_compose=True
checks=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 common=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-DFFTA_ART_HISTORY_SLOTS=20']
 reference=out/'reference.o';elf=out/'test.elf';binary=out/'test.bin'
 names=['plan','apply','apply_cached','reapply','live_apply']
 command=common+['-Dffta_art_palette_'+v+'=reference_'+v for v in names]+['-c','src/engine/art-palette-plan.c','-o',str(reference)]
 result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'reference-compile.log').write_text(result.stdout+result.stderr);result.check_returncode()
 assembly,proof=build_scoped(out,20,args.fused_compose,args.fused_compose,compact_leaves=args.compact_leaves,unrolled_copy=args.unrolled_copy);lookup,_=write_pixel_banks(out)
 sources=['src/engine/art-palette-plan.c','src/engine/art-palette-scan.s','src/engine/art-palette-bank-scan.s','src/engine/art-oam-demands.s']
 command=common+(['-DFFTA_ART_RECT_CONFLICT=1','-Wa,--defsym,FFTA_ART_RECT_CONFLICT=1'] if args.rect_conflict else [])+(['-DFFTA_ART_PREPARED_PREFERENCE=1'] if args.prepared_preference else [])+(['-DFFTA_ART_JOINED_ROWS=1'] if args.joined_rows else [])+(['-Wa,--defsym,FFTA_ART_BURST_SCAN=1'] if args.burst_scan else [])+(['-Wa,--defsym,FFTA_ART_BLOCK_SCAN=1'] if args.block_scan else [])+(['-DFFTA_ART_PACKED_PLAN=1'] if args.packed_plan else [])+(['-DFFTA_ART_FUSED_COMPOSE=1'] if args.fused_compose else [])+['-DFFTA_ART_NATIVE_OAM_PREFIX=1','-DFFTA_ART_SCOPED_FRAME=1','-DFFTA_ART_FAST_OAM_PLAN=1','-DFFTA_ART_ARM_OAM_SCAN=1','-DFFTA_ART_FAST_BANK_SCAN=1','-Wl,-Ttext=0x09f90000','-Wl,-e,ffta_art_palette_live_apply',*sources,str(reference),str(assembly),str(lookup),'-o',str(elf)]
 result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);result.check_returncode()
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
 symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 code=binary.read_bytes();rom=bytearray(b'\xff'*0x2000000);rom[0x1f90000:0x1f90000+len(code)]=code;a=ARM(rom,bytes(0x8000))
 F,O,V,P,C,T,R,CACHE,BACK=0x02010000,0x02011000,0x02020000,0x02012000,0x02012400,0x02013000,0x02013100,0x02014000,0x02016000
 a.put(V,bytes(32768));a.put(C,bytes((i*31+17)&255 for i in range(640)))
 a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,20))
 palette=bytes(range(256))*2
 cases=[([i],False) for i in (0,9,10,15,16,19,20)]+[(list(range(10,20)),False),([0,5,10,19],False),(list(range(16)),False),([19]*128,False),([19]*128,True)]
 if args.fused_compose:cases += [([19,255],False)]*4
 extended={}
 if args.packed_plan:
  rng=random.Random(0x46544641)
  masks=[0,65535,0xaaaa,0x5555]+[65535^(1<<i) for i in range(16)]+[rng.randrange(65536) for _ in range(16)]
  for mask in masks:
   native=[i for i in range(16) if mask&(1<<i)]
   for owned in ([0],[19],[0,5,10,19],list(range(16))):
    extended[len(cases)]=dict(native=native,custom=20,mapping=1)
    cases.append((list(owned)+[255]*len(native),False))
  for custom,mapping in ((0,1),(1,1),(19,1),(20,0),(21,1)):
   extended[len(cases)]=dict(native=[2],custom=custom,mapping=mapping)
   cases.append(([19,255],False))
 for case,(owners,disabled) in enumerate(cases):
  count=len(owners);objects=bytearray(bytes.fromhex('a800f8000000cdab')*128);tags=bytearray([255]*128)
  for i,owner in enumerate(owners):
   struct.pack_into('<4H',objects,i*8,0x200 if disabled else 64,0x8040,0x4200+i,0xabcd);tags[i]=owner
  if 12<=case<16:
   struct.pack_into('<4H',objects,8,0x3100 if case==14 else 0x2000,0x8100 if case==13 else 0x8000,0x3fe if case==15 else 0,0xabcd)
  if case in extended:
   data=extended[case];first=len(owners)-len(data['native'])
   for index,bank in enumerate(data['native'],first):struct.pack_into('<H',objects,index*8+4,bank*4096+32)
   a.put(F+24,struct.pack('<2I',data['mapping'],data['custom']))
  else:a.put(F+24,struct.pack('<2I',1,20))
  a.put(V,bytes([0x61])*32768)
  def reset(prior):
   a.put(O,objects);a.put(T,tags);a.put(P,palette);a.put(R,prior);a.put(CACHE,bytes(2124));a.put(BACK-4,b'pre!'+b'\xc7'*512+b'end!')
  def state():return a.read(O,1024),a.read(P,512),a.read(R,32),a.read(BACK-4,520),a.read(CACHE,2124)
  reset(b'\xa5'*32);result=a.call(symbols['reference_live_apply'],F,CACHE,BACK);expected=(result,state())
  for stack in (0x03007800,0x03007804,0x03007000,0x0201c000):
   for prior in (b'\xa5'*32,expected[1][2]):
    # Preferred-bank reuse can leave the cache untouched while initial full
    # planning populates it. Compare against the same initial plan/cache, not
    # the first invocation's cache side effects.
    reset(prior);reference_result=a.call(symbols['reference_live_apply'],F,CACHE,BACK)
    case_expected=(reference_result,state())
    reset(prior);resident=a.read(0x03000000,0x6d68);executed=[]
    hook=a.u.hook_add(UC_HOOK_CODE,lambda u,pc,size,user:executed.append(pc),begin=0x03006d68,end=0x03007fff)
    if args.fused_compose:
     occupied=requested=0;eight=[];valid=True
     for i in range(count):
      x,y,z,_=struct.unpack_from('<4H',objects,i*8);owner=tags[i]
      if x&0x300==0x200:continue
      if x>>14==3:valid=False;continue
      if owner!=255:
       if owner>=20 or x&0xe100 or y>>14!=2:valid=False
       else:requested|=1<<owner
      elif x&0x2000:eight.append(i)
      else:occupied|=1<<(z>>12)
     d=0x02018000;a.put(d,struct.pack('<3I',occupied,requested,len(eight) if valid else 129)+bytes(eight))
     a.put(stack,struct.pack('<I',count))
     result=a.call(symbols['ffta_art_palette_live_apply_fused'],F,CACHE,BACK,d,stack=stack)
    else:result=a.call(symbols['ffta_art_palette_live_apply_prefix'],F,CACHE,BACK,count,stack=stack)
    a.u.hook_del(hook)
    check((result,state())==case_expected,'High-slot exact original full-plan semantics '+str((case,stack,prior[:2].hex())))
    check(a.read(0x03000000,0x6d68)==resident,'Native resident code/data fence')
    check(a.read(O,1024)[6::8]==bytes(objects)[6::8] and a.read(O,1024)[7::8]==bytes(objects)[7::8],'Affine words preserved')
    if result:check(bool(executed)==(stack in (0x03007800,0x03007804)),'Actual scoped or fallback execution')
 report=dict(rectConflict=args.rect_conflict,preparedPreference=args.prepared_preference,joinedRows=args.joined_rows,burstScan=args.burst_scan,blockScan=args.block_scan,packedPlan=args.packed_plan,fusedCompose=args.fused_compose,status='passed',checks=checks,romSha256=sha(rom),compiledSha256=sha(code),scopedFrame=proof,
  sources={s:sha((ROOT/s).read_bytes()) for s in sources},scope=__doc__)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');raise
