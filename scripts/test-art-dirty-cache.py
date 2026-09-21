"""Compiled ARMv4T dirty-mask cache and native queued-upload hook contracts.

This tests the private queue-only prototype, not complete native writer coverage.
No game save, installed ROM or current delivery index is changed.
"""
import ast,datetime,json,struct,subprocess,sys
from native_art import ROOT,sha
from art_palette_build import write_pixel_banks
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARMv4T>','exec'))
out=ROOT/'build/art/dirty-cache'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');entry=0x09f90000
lookup,_=write_pixel_banks(out)
stub=out/'hook-target.c';stub.write_text('#include "art-palette-dirty.h"\nvoid ffta_art_live_obj_write(const unsigned *p){ffta_art_dirty_dma((FFTA_ArtPaletteCache *)0x02014000,p[2],p[3]);}\n')
sources=['src/engine/art-palette-plan.c','src/engine/art-palette-scan.s','src/engine/art-palette-dirty.c','src/engine/art-palette-dirty-hooks.s']
cmd=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-DFFTA_ART_DMA_TILE_CACHE=1','-Isrc/engine','-Wl,-Ttext='+hex(entry),'-Wl,-e,ffta_art_dirty_begin',*sources,str(stub),str(lookup),'-o',str(out/'test.elf')]
compiled=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(out/'compile.log').write_text(compiled.stdout+compiled.stderr);compiled.check_returncode()
subprocess.run([prefix+'objcopy.exe','-O','binary',str(out/'test.elf'),str(out/'test.bin')],check=True,capture_output=True)
symbols={row.split()[2]:int(row.split()[0],16) for row in subprocess.check_output([prefix+'nm.exe',str(out/'test.elf')],text=True).splitlines() if len(row.split())==3}
code=(out/'test.bin').read_bytes();rom=bytearray((ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes());rom.extend(b'\xff'*(0x2000000-len(rom)));rom[entry-0x08000000:entry-0x08000000+len(code)]=code
checks=[];CACHE=0x02014000;V=0x06010000;MAGIC=0x44545931
def check(ok,label):
 assert ok,label
 checks.append(label)
def machine(data=rom):
 a=ARM(data,bytes(0x8000));a.u.mem_map(0x06000000,0x18000);a.u.mem_map(0x04000000,0x1000)
 a.put(CACHE-4,b'pre!');a.put(CACHE+2124,b'end!');return a
def call(a,name,*values):return a.call(symbols['ffta_art_dirty_'+name],CACHE,*values)
def valid(a):return int.from_bytes(a.read(CACHE,64),'little')
def full(a):
 call(a,'begin');a.put(CACHE,b'\xff'*64)
def fence(a):check(a.read(CACHE-4,4)==b'pre!' and a.read(CACHE+2124,4)==b'end!','Cache fences preserved')
try:
 a=machine();call(a,'begin');check(valid(a)==0 and a.word(CACHE+2120)==MAGIC,'Reset clears all512 tiles')
 reads=[];h=a.u.hook_add(UC_HOOK_MEM_READ,lambda u,kind,address,size,value,user:reads.append((address,size)),begin=V,end=V+32767)
 for tile in range(512):
  raw=bytes((0,1,16*(tile%15+1),255))*16;a.put(V+tile*64,raw)
  expected=sum(1<<bank for bank in {value//16 for value in raw if value})
  reads.clear();check(call(a,'mask',V+tile*64,tile)==expected and sum(n for _,n in reads)==64,'Cold exact mask '+str(tile))
  reads.clear();check(call(a,'mask',V+tile*64,tile)==expected and not reads,'Warm mask reads no pixel bytes '+str(tile))
 check(valid(a)==(1<<512)-1,'All512 physical tile identities retained without aliasing');fence(a)
 ranges=[(V,0,set()),(V,1,{0}),(V+63,2,{0,1}),(V+32767,1,{511}),
         (V-1,2,{0}),(V-64,64,set()),(V+1983,130,set(range(30,34))),
         (V,32768,set(range(512))),(0x06018000,2,set(range(512))),
         (0x05000000,4,set()),(0x07000000,4,set()),(0xfffffff0,32,set(range(512)))]
 for dst,length,dirty in ranges:
  full(a);call(a,'write',dst,length)
  check(valid(a)==((1<<512)-1)^sum(1<<i for i in dirty),'Exact write invalidation '+str((dst,length)))
  fence(a)
 for width in (2,4):
  for mode in range(4):
   for count in (1,17,64,0):
    dst=V+0x1000;control=0x80000000|(0x04000000 if width==4 else 0)|(mode<<21)|count
    n=count or 65536;start=dst-(n-1)*width if mode==1 else dst;end=dst+(width if mode==2 else n*width) if mode!=1 else dst+width
    dirty=set(range(512)) if start<0x06000000 or end>0x06018000 else set(range(max(0,(start-V)//64),max(0,(end-V+63)//64)))
    full(a);call(a,'dma',dst,control)
    check(valid(a)==((1<<512)-1)^sum(1<<i for i in dirty),'DMA range width/mode/count '+str((width,mode,count)))
 for extra in (0x10000000,0x20000000,0x30000000,0x02000000):
  full(a);call(a,'dma',V,0x84000010|extra);check(a.word(CACHE+2120)==0xffffffff,'Deferred/repeat blocks reuse '+hex(extra))
  for value in (16,32,0,255):
   a.put(V,bytes([value])*64);reads.clear()
   check(call(a,'mask',V,0)==(1<<(value//16) if value else 0) and sum(n for _,n in reads)==64,'Blocked mode always sees current pixels '+str((extra,value)))
 full(a);call(a,'dma',V,0x04000010);check(valid(a)==(1<<512)-1,'Disabled DMA does not invalidate')
 a.u.hook_del(h)
 # Exercise the actual planner consumers after a changed tile conflicts with
 # the previously preferred bank; both outputs must match uncached planning.
 F,O,P,C,T,R,BACKUP=0x02010000,0x02011000,0x02012000,0x02012400,0x02013000,0x02013100,0x02016000
 objects=bytearray(struct.pack('<4H',0x200,0,0,0)*128);struct.pack_into('<4H',objects,0,0x2000,0,640,0);struct.pack_into('<4H',objects,8,0,0x8000,0,0)
 owners=bytearray([255]*128);owners[1]=0;a.put(T,owners);a.put(C,bytes(range(32)));a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,1))
 call(a,'begin');prior=bytes([255])*16
 for value in (16,16,32,48,0,255,1,16):
  dst=V+640*32;a.put(dst,bytes([value])*64);call(a,'dma',dst,0x84000010)
  a.put(O,objects);a.put(P,bytes(512));a.put(R,prior)
  result=a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,BACKUP);actual=(result,a.read(O,1024),a.read(P,512));prior=a.read(R,16)
  a.put(O,objects);a.put(P,bytes(512));a.put(R,bytes([255])*16)
  result=a.call(symbols['ffta_art_palette_apply'],F)
  check(actual==(result,a.read(O,1024),a.read(P,512)),'Live preferred and replan exact after upload '+str(value));fence(a)
 # Enter through the exact patched native bytes and stop after the next native
 # flag-setting ADD. Compare all registers/CPSR and source/destination/control.
 check(rom[0x820:0x828].hex()=='1160a0685060e068','Original native hook bytes authenticated')
 patched=bytearray(rom);patched[0x820:0x828]=bytes.fromhex('00480047')+struct.pack('<I',symbols['ffta_art_queued_obj_write']|1)
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_CPSR]
 for channel in range(4):
  for residue in (0,4):
   pair=[]
   for image in (rom,patched):
    m=machine(image);full(m);descriptor=0x02018000;destination=V+63*64;control=0x84000011
    m.put(descriptor,struct.pack('<4I',0,0x02020000,destination,control));sp=0x03007800+residue
    values=[0xdeadbeef,0x02020000,0x040000b0+12*channel,channel,descriptor,0x55555555,0x66666666,0x77777777,0x88888888,0x99999999,0xaaaaaaaa,0xbbbbbbbb,0xcccccccc,sp,0x08123457,0xa000003f]
    # Select the CPU mode before setting its banked SP/LR.
    m.u.reg_write(UC_ARM_REG_CPSR,values[-1])
    for reg,value in zip(regs[:-1],values[:-1]):m.u.reg_write(reg,value)
    m.u.emu_start(0x08000821,0x0800082c,count=50000)
    check(m.u.reg_read(UC_ARM_REG_PC)==0x0800082c,'Hook reaches native continuation '+str((channel,residue)))
    pair.append(([m.u.reg_read(r) for r in regs],m.read(0x04000000,0x1000),m.read(0x02000000,CACHE-0x02000000),m.read(CACHE+2124,0x02040000-CACHE-2124)))
    fence(m)
    if image is patched:check(valid(m)==((1<<512)-1)^((1<<63)|(1<<64)),'Hook invalidates descriptor range '+str((channel,residue)))
   check(pair[0]==pair[1],'Native registers/CPSR/IO/noncache RAM identical '+str((channel,residue)))
 report=dict(status='passed',checks=checks,compiledSha256=sha(code),sources={p:sha((ROOT/p).read_bytes()) for p in sources+['src/engine/art-palette-dirty.h','src/engine/art-palette-plan.h']},scope=__doc__)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
