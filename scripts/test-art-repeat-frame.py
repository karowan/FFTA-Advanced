"""Exact repeated-frame key, pixel coverage, invalidation and scoped ARM ABI.

Pure compiled component on deterministic inputs, not battle timing acceptance.
The live caller must authenticate current ownership before every lookup.
"""
import ast,datetime,json,struct,subprocess,sys
from native_art import ROOT,sha
from art_palette_build import write_pixel_banks
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
out=ROOT/'build/art/repeat-frame-contract'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'repeat.elf';binary=out/'repeat.bin'
sources=['src/engine/art-repeat-frame.c','src/engine/art-repeat-probe.s','src/engine/art-palette-plan.c','src/engine/art-palette-scan.s']
lookup,_=write_pixel_banks(out)
checks=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-DFFTA_ART_HISTORY_SLOTS=20','-DFFTA_ART_REPEAT_FRAME=1','-Wl,-Ttext=0x09f90000','-Wl,-e,ffta_art_repeat_hit',*sources,str(lookup),'-o',str(elf)]
 compiled=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'compile.log').write_text(compiled.stdout+compiled.stderr);compiled.check_returncode()
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
 symbols={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 code=binary.read_bytes();rom=bytearray(b'\xff'*0x2000000);rom[0x1f90000:0x1f90000+len(code)]=code
 a=ARM(rom,bytes(0x8000))
 F,O,V,P,C,T,R,CACHE,BACK,KEY,VAR=0x02010000,0x02011000,0x02020000,0x02012000,0x02012400,0x02013000,0x02013100,0x02014000,0x02015000,0x02016000,0x02017000
 oam=bytearray(struct.pack('<4H',0x200,0,0,0)*128);tags=bytearray([255]*128)
 for i in range(4):struct.pack_into('<4H',oam,i*8,16,0x8000+i*32,0x7000,0xbeef);tags[i]=i
 struct.pack_into('<4H',oam,6*8,0x6000,0xc000,64,0x1234)
 obj=bytearray(32768)
 for i in range(2048):obj[2048+i]=(1+i%15) if i%3 else 32+i%16
 palette=bytes((i*7+11)%256 for i in range(512));colors=bytes((i*13+19)%256 for i in range(640))
 variants=bytes([i*16+7 for i in range(10)]+[255]*10)+bytes([32]*20)
 def semantic(objects,owners):
  result=[]
  for index,owner in enumerate(owners):
   av,bv,cv,_=struct.unpack_from('<4H',objects,index*8)
   if av&0x300==0x200:result.append(('disabled',));continue
   if av>>14==3:return None
   if owner!=255:
    if owner>=10 or av&0xe100 or bv>>14!=2:return None
    result.append(('custom',owner,cv>>12))
   elif av&0x2000:result.append(('pixels',av&0xf3ff,bv&0xf1ff,cv&1022))
   else:result.append(('native',cv>>12))
  return result
 baseline_key=semantic(oam,tags)
 def setup():
  for address,data in [(O,oam),(V,obj),(P,palette),(C,colors),(T,tags),(R,bytes(32)),(CACHE,bytes(2124)),(BACK,bytes(512)),(KEY,bytes(928)),(VAR,variants)]:a.put(address,bytes(data))
  a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,20));a.put(KEY-4,b'pre!');a.put(KEY+928,b'end!')
  a.call(symbols['ffta_art_repeat_begin'],KEY,F)
  check(a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,BACK)==1,'Full planner accepts declared four-class scene')
  a.put(STACK,bytes(4));a.call(symbols['ffta_art_repeat_finish'],KEY,F,CACHE,VAR)
  check(a.word(KEY)==1,'Complete exact pixel footprint permits reuse')
  a.put(O,bytes(oam));a.put(P,palette)
 setup();saved=a.read(0x02010000,0x20000)
 def restore():a.put(0x02010000,saved)
 def hit(stack=STACK,highlight=0):
  a.put(stack,struct.pack('<I',highlight))
  return a.call(symbols['ffta_art_repeat_hit'],KEY,F,CACHE,VAR,stack=stack)
 check(hit()==1,'Unchanged entire scene hits')
 check(a.read(KEY-4,4)==b'pre!' and a.read(KEY+928,4)==b'end!','Repeat reservation fences')
 # Every used source byte and every semantically consumed OAM bit matters.
 for index in range(128):
  for lane in range(3):
   for bit in range(16):
    restore();p=O+index*8+lane*2;value=struct.unpack('<H',a.read(p,2))[0]
    a.put(p,struct.pack('<H',value^(1<<bit)))
    changed=a.read(O,1024);expected=semantic(changed,tags)==baseline_key
    result=hit();check(bool(result)==expected,f'Palette demand object{index} attribute{lane} bit{bit}')
    if result:
     a.call(symbols['ffta_art_palette_apply_validated'],F,BACK)
     reused=(a.read(O,1024),a.read(P,512));a.put(O,changed);a.put(P,palette)
     check(a.call(symbols['ffta_art_palette_apply'],F)==1 and (a.read(O,1024),a.read(P,512))==reused,'Reuse equals full planner for accepted OAM change')
 for index in range(2048):
  restore();a.put(V+2048+index,bytes([obj[2048+index]^1]))
  check(hit()==0,'Reject changed source pixel '+str(index))
 for address,size,label in ((VAR,40,'history'),(R,32,'plan')):
  for offset in range(size):
   restore();value=a.read(address+offset,1)[0];a.put(address+offset,bytes([value^1]))
   check(hit()==0,'Reject changed '+label+' byte '+str(offset))
 for offset in range(128):
  restore();a.put(O+offset*8+6,b'\xab\xcd');check(hit()==1,'Unconsumed affine word '+str(offset))
 for address,data,label in ((KEY,bytes(4),'key invalidation'),(CACHE+2120,bytes(4),'pixel cache invalidation'),(F+24,bytes(4),'mapping mode'),(F+28,struct.pack('<I',19),'history count'),(KEY+916,struct.pack('<I',33),'overlarge footprint'),(KEY+852,struct.pack('<H',512),'invalid tile')):
  restore();a.put(address,data);check(hit()==0,'Reject '+label)
 restore();check(hit(highlight=1)==0,'Reject changed native highlight consumer')
 for index,owner in ((0,1),(0,255),(6,0)):
  restore();a.put(T+index,bytes([owner]));before=a.read(T,128)
  check(hit()==0 and a.read(T,128)==before,'Changed actual ownership rejects without remapping partial tags')
 restore();a.put(T+127,b'\0');check(hit()==1,'Disabled object has no palette demand even with a tag')
 a.call(symbols['ffta_art_palette_apply_validated'],F,BACK);reused=(a.read(O,1024),a.read(P,512))
 a.put(O,bytes(oam));a.put(P,palette)
 check(a.call(symbols['ffta_art_palette_apply'],F)==1 and (a.read(O,1024),a.read(P,512))==reused,'Disabled tagged object agrees with full native palette planner')
 # Rebuild keys after misses: reuse only the independently unchanged8bpp
 # footprint, while fresh full planning still owns allocation and pixel masks.
 for name,offset,data,same_footprint in (
     ('body position',2,struct.pack('<H',0x8010),True),
     ('portrait position',6*8+2,struct.pack('<H',0xc008),False),
     ('portrait flipped',6*8+2,struct.pack('<H',0xd000),False),
     ('portrait mosaic',6*8,struct.pack('<H',0x7000),False),
     ('portrait disabled',6*8,struct.pack('<H',0x200),False),
     ('portrait clipped',6*8+2,struct.pack('<H',0xc12c),False)):
  restore();a.put(O+offset,data);native_objects=a.read(O,1024)
  a.call(symbols['ffta_art_repeat_begin'],KEY,F)
  check(bool(a.word(KEY+916)&0x80000000)==same_footprint,'Capture identifies pixel footprint change '+name)
  check(a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,BACK)==1,'Changed scene full planning '+name)
  a.put(STACK,bytes(4));a.call(symbols['ffta_art_repeat_finish'],KEY,F,CACHE,VAR)
  check(a.word(KEY)==1,'Changed scene creates fully validated key '+name)
  a.put(O,native_objects);a.put(P,palette);check(hit()==1,'Changed scene exact next hit '+name)
 restore();a.put(O+7*8,struct.pack('<4H',0x2000,0,128,0));a.call(symbols['ffta_art_repeat_begin'],KEY,F)
 check(a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,BACK)==1,'Larger footprint remains supported by full planner')
 a.put(STACK,bytes(4));a.call(symbols['ffta_art_repeat_finish'],KEY,F,CACHE,VAR)
 check(a.word(KEY)==0,'Thirty-third pixel tile disables reuse without truncation')
 # A class using a high history slot must map freshly authenticated tags.
 restore();split=bytearray(variants);split[0]=255;split[10]=7;a.put(VAR,bytes(split))
 a.call(symbols['ffta_art_repeat_begin'],KEY,F);a.put(T,b'\x0a')
 check(a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,BACK)==1,'Actual high-slot allocation')
 a.put(STACK,bytes(4));a.call(symbols['ffta_art_repeat_finish'],KEY,F,CACHE,VAR)
 a.put(O,bytes(oam));a.put(T,bytes(tags));a.put(P,palette)
 check(hit()==1 and a.read(T,4)==bytes((10,1,2,3)),'Fresh class tag remaps to high history slot on reuse')
 # Pixel writes outside consumed footprint cannot affect this decision.
 for offset in (0,2047,4096,32767):
  restore();a.put(V+offset,b'\xfe');check(hit()==1,'Ignore unrelated OBJ byte '+str(offset))
 # New displayed custom colors and current native backups remain live inputs.
 restore();changed=bytes(x^31 for x in colors);native=bytes(x^7 for x in palette)
 a.put(C,changed);a.put(P,native);check(hit()==1,'Current colors are independent of plan reuse')
 a.call(symbols['ffta_art_palette_apply_validated'],F,BACK)
 banks=a.read(R+8,20)
 for owner in range(4):
  bank=banks[owner]
  check(a.read(P+bank*32,32)==changed[owner*32:owner*32+32],'Current generated colors applied '+str(owner))
  check(a.read(BACK+bank*32,32)==native[bank*32:bank*32+32],'Current native colors backed up '+str(owner))
 for stack in (0x03007800,0x03007804,0x03007000,0x0201c000):
  restore();a.put(0x03006d00,b'\x7b'*0x68);pcs=[]
  hook=a.u.hook_add(UC_HOOK_CODE,lambda u,p,n,d:pcs.append(p))
  result=hit(stack);a.u.hook_del(hook)
  check(result==1,'Exact hit on stack '+hex(stack))
  check(a.read(0x03006d00,0x68)==b'\x7b'*0x68,'Resident IWRAM fence '+hex(stack))
  check(any(0x03007000<=p<0x03007800 for p in pcs)==(stack in (0x03007800,0x03007804)),'Scoped leaf or ROM fallback '+hex(stack))
 report=dict(status='passed',checks=checks,compiledSha256=sha(code),sources={p:sha((ROOT/p).read_bytes()) for p in sources},scope=__doc__)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
