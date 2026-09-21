"""Twenty history slots with ten real class palettes and sixteen hardware banks.

Compiled ARMv4T component proof using retained native deployment colors. This
does not enlarge the installed live reservation or run an all-class game.
"""
import ast,datetime,hashlib,json,struct,subprocess,sys
from pathlib import Path
from native_art import ROOT,sha
from art_palette_build import write_pixel_banks
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
arm_source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
out=ROOT/'build/art/history-capacity'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];a=None

def check(ok,label):
 assert ok,label
 checks.append(label)

try:
 capture=ROOT/'build/art/live-palette/battle/20260918T101335.606659Z/observed.json'
 raw=capture.read_bytes();check(sha(raw)=='adc3ad125d84b9d33222b1866cd1ac26fe80b167b3f04033d345cef887c18578','Native deployment capture authenticated')
 native=bytes.fromhex(json.loads(raw)['entryPaletteTraces']['candidate']['entry-10']['nativeShadow'])[512:]
 classpath=ROOT/'build/art/generated-classes/595782ba32f4a20ff2053218f8722ab5e491112d/manifest.json'
 check(sha(classpath.read_bytes())=='9c30db597818297809590dbf2c2e08b3ed060466815c4964de83fabf872368d5','Ten class reference manifest authenticated')
 classes=json.loads(classpath.read_text());classrom=Path(classes['path']).read_bytes()
 check(hashlib.sha1(classrom).hexdigest()==classes['romSha1'],'Class reference ROM authenticated')
 refs=b''.join(classrom[j['nativePaletteReference']:j['nativePaletteReference']+32] for j in classes['jobs'])
 catalog=json.loads((ROOT/'src/art/imagegen/catalog.json').read_text());colors=b'';art_inputs=[]
 for job in catalog['jobs']:
  manifest=ROOT/job['technicalConversion'];art=json.loads(manifest.read_text());palette=(manifest.parent/'palette.bin').read_bytes()
  check(len(palette)==32 and sha(palette)==art['paletteSha256'],'Authenticated generated palette '+str(job['job']))
  check(sha((ROOT/job['privateSource']).read_bytes())==art['sourceSha256']==job['sourceSha256'],'Authenticated generated source '+str(job['job']))
  colors+=palette;art_inputs.append(dict(job=job['job'],manifest=str(manifest),manifestSha256=sha(manifest.read_bytes()),paletteSha256=sha(palette)))
 check(len(colors)==len(refs)==320 and len({colors[i:i+32] for i in range(0,320,32)})==10,'Ten independent generated palettes, no extra class definitions')
 parent=json.loads((ROOT/'build/art/generated-actions/refined-samurai-current.json').read_text());rom=bytearray(Path(parent['path']).read_bytes())
 check(hashlib.sha1(rom).hexdigest()=='0fa7d1707e2d85fb2a8602f061b5eb4479ff3211','Original native-code parent authenticated')
 sources=['src/engine/art-palette-binding.c','src/engine/art-palette-variants.c','src/engine/art-palette-fade.c','src/engine/art-palette-plan.c','src/engine/art-palette-scan.s']
 probe=out/'layout.c';probe.write_text('#include <stddef.h>\n#include "art-palette-variants.h"\n#include "art-palette-plan.h"\nunsigned history_layout(unsigned i) {return i==0?sizeof(FFTA_ArtBindings):i==1?sizeof(FFTA_ArtVariants):i==2?sizeof(FFTA_ArtPalettePlan):i==3?offsetof(FFTA_ArtPalettePlan,requested):offsetof(FFTA_ArtPalettePlan,bank);}\n')
 lookup,_=write_pixel_banks(out);prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'history.elf';binary=out/'history.bin'
 command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-DFFTA_ART_HISTORY_SLOTS=20','-Isrc/engine','-Wl,-Ttext=0x09f90000','-Wl,-e,history_layout',*sources,str(probe),str(lookup),'-o',str(elf)]
 compiled=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'compile.log').write_text(compiled.stdout+compiled.stderr);compiled.check_returncode()
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
 symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 code=binary.read_bytes();check(len(code)<0x40000 and rom[0x1f90000:0x1f90000+len(code)]==b'\xff'*len(code),'Standalone component owns blank reservation')
 rom[0x1f90000:0x1f90000+len(code)]=code;a=ARM(rom,bytes(0x8000))
 B,S,N,R,C,V,T,O,M,F,P,H,OBJ=0x02010000,0x02012000,0x02013000,0x02013400,0x02013800,0x02013c00,0x02014000,0x02014400,0x02014800,0x02014c00,0x02014d00,0x02015000,0x02020000
 def call(name,*args):
  if len(args)>4:a.put(STACK,struct.pack('<'+'I'*(len(args)-4),*args[4:]))
  return a.call(symbols[name],*args[:4])
 sizes=[call('history_layout',i) for i in range(5)]
 check(sizes==[5692,40,32,4,8],'Twenty-slot layout and 32-bit request mask confirmed by compiled ABI')
 for address,size in ((B,5692),(S,40),(V,640),(R,320),(C,320),(P,32)):
  a.put(address-4,b'\xd7'*4);a.put(address,bytes(size));a.put(address+size,b'\xe9'*4)
 a.put(N,native);a.put(R,refs);a.put(C,colors);call('ffta_art_bindings_reset',B,C);call('ffta_art_variants_reset',S)
 check(a.read(B+5040,320)==colors and a.read(B+5360,320)==bytes(320),'Extra histories reset without reading nonexistent class palettes')
 call('ffta_art_variants_track',S,B,N,R,C,256,511,1023,V)
 mapping=a.read(S,40);keys=mapping[:20];used=[i for i,k in enumerate(keys) if k!=255]
 expected_keys=[]
 def scaled(raw,factor):
  return struct.pack('<16H',*[sum((((value>>shift)&31)*factor//32)<<shift for shift in (0,5,10)) for value in struct.unpack('<16H',raw)])
 for owner in range(10):
  for bank in range(16):
   if any(scaled(refs[owner*32:owner*32+32],factor)==native[bank*32:bank*32+32] for factor in (32,19)):expected_keys.append(owner*16+bank)
 check(len(used)==17 and sorted(keys[i] for i in used)==expected_keys,'All seventeen captured class/native-bank histories retained')
 for slot in used:
  key=keys[slot];expected=scaled(colors[(key>>4)*32:(key>>4)*32+32],mapping[20+slot])
  check(a.read(B+252*slot,32)==expected and a.read(B+5040+slot*32,32)==expected and a.read(V+slot*32,32)==expected,'Correct class/brightness in history '+str(slot))
 def fade(kind,task):
  call('ffta_art_binding_start_mapped',B,256,511,3,task,kind,N,C,S)
  for remaining in (3,2,1):call('ffta_art_binding_tick',B,task,remaining,remaining-1,int(remaining>1),0)
 fade(1,0x1234)
 check(a.read(B+5680,12)==struct.pack('<3I',17,17,0),'Whole-range black affects all seventeen histories, including slots above15')
 for slot in used:check(a.read(B+slot*252,32)==bytes(32),'Completed absent black history '+str(slot))
 # A late visible body selects a high history slot without dropping the other
 # sixteen completed transformations or confusing history slots with classes.
 slot=next(i for i in used if i>=16);key=keys[slot];owner=key>>4;bank=key&15
 objects=bytearray(struct.pack('<4H',0x200,0,0,0)*128);struct.pack_into('<4H',objects,0,64,0x8040,bank<<12,0)
 tags=bytes([owner]+[255]*127);banks=[0]*10;banks[owner]=1<<bank
 a.put(O,objects);a.put(T,tags);a.put(M,struct.pack('<10H',*banks));before=a.read(B,5692)
 requested=call('ffta_art_variants_prepare',S,B,T,O,M,N,R,C,V)
 check(requested==1<<slot and a.read(T,128)==bytes([slot]+[255]*127),'Late appearance preserves high history-slot mask and tag')
 check(a.read(B,5692)==before and a.read(S,40)==mapping,'Late appearance does not evict absent transformed histories')
 # Fill the remaining three slots using declared additional native aliases.
 for bank in (2,3,4):a.put(N+bank*32,refs[:32])
 call('ffta_art_variants_track',S,B,N,R,C,288,335,1,V)
 check(255 not in a.read(S,20),'All twenty slots may retain separate histories')
 fade(1,0x2234)
 saved=(a.read(S,40),a.read(B,5692),a.read(V,640))
 a.put(N+5*32,refs[:32]);call('ffta_art_variants_track',S,B,N,R,C,336,351,1,V)
 check(saved==(a.read(S,40),a.read(B,5692),a.read(V,640)),'Twenty-first pretrack never overwrites existing transformed history')
 a.put(T,bytes([0]+[255]*127));a.put(M,struct.pack('<10H',1<<5,*([0]*9)));struct.pack_into('<H',objects,4,5<<12);a.put(O,objects)
 check(call('ffta_art_variants_prepare',S,B,T,O,M,N,R,C,V)==0 and saved==(a.read(S,40),a.read(B,5692),a.read(V,640)) and a.read(T,128)==bytes([0]+[255]*127),'Twenty-first appearance refuses atomically while all twenty histories are transformed')
 fade(3,0x3234);mapping=a.read(S,40)
 for slot,key in enumerate(mapping[:20]):
  expected=scaled(colors[(key>>4)*32:(key>>4)*32+32],mapping[20+slot])
  check(a.read(B+slot*252,32)==expected and a.read(B+5040+slot*32,32)==expected,'Mapped baseline restore uses source class for slot '+str(slot))
 check(a.read(B+5680,12)==struct.pack('<3I',57,57,0),'All starts/completions reconcile without unsupported effects')
 # Hardware can allocate sixteen palettes even when history indices are4..19.
 for count in (16,17):
  objects=bytearray(struct.pack('<4H',0x200,0,0,0)*128);tags=bytearray([255]*128)
  selected=list(range(4,20)) if count==16 else list(range(17))
  for index,slot in enumerate(selected):struct.pack_into('<4H',objects,index*8,64,0x8040,0,0);tags[index]=slot
  a.put(O,objects);a.put(T,tags);a.put(H,native);a.put(P,b'\xa5'*32);a.put(OBJ,bytes(32768));a.put(F,struct.pack('<8I',O,OBJ,T,H,B+5040,P,1,20))
  result=call('ffta_art_palette_apply',F)
  if count==16:
   check(result==1 and a.word(P+4)==0xffff0,'High history indices preserve all sixteen allocated request bits')
   for index,slot in enumerate(selected):
    target=a.read(P+8+slot,1)[0]
    check(target==index and a.read(H+target*32,32)==a.read(B+5040+slot*32,32),'History '+str(slot)+' maps to exact available hardware bank')
   check(a.read(O,1024)==b''.join(struct.pack('<4H',64,0x8040,index<<12,0) for index in range(16))+objects[128:],'Only owned palette nibbles change in sixteen-bank allocation')
  else:check(result==0 and a.read(O,1024)==objects and a.read(H,512)==native and a.read(P,32)==b'\xa5'*32,'Seventeen visible palettes refuse without modifying OAM, colors or plan')
 for address,size in ((B,5692),(S,40),(V,640),(R,320),(C,320),(P,32)):
  check(a.read(address-4,4)==b'\xd7'*4 and a.read(address+size,4)==b'\xe9'*4,'Exact allocation canaries '+hex(address))
 headers=['src/engine/art-palette-binding.h','src/engine/art-palette-variants.h','src/engine/art-palette-plan.h','src/engine/art-palette-limits.h']
 report=dict(status='passed',checks=checks,compiledSha256=sha(code),historySlots=20,sourceCapture=str(capture),sourceCaptureSha256=sha(raw),sources={name:sha((ROOT/name).read_bytes()) for name in sources+headers},artInputs=art_inputs,scope='ARMv4T compiled20-history component with ten authenticated generated class palettes, retained native17-pair deployment demand, absent black/restore effects, high-slot late appearance, twenty-slot retention/overflow and sixteen-bank allocation versus seventeen-bank atomic refusal. Not installed live hooks, enlarged heap acceptance, all effect kinds, natural scenes, timing or final art.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print(out);raise
