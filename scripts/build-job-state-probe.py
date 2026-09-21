"""Shared private status persistence layer over the current Samurai build.

Canonical/save transport and explicitly enlarged native owned copies.
"""
import hashlib,json,pathlib,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta=json.loads((P/'samurai/current.json').read_text());base=pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(base).hexdigest()==meta['romSha1']
old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
OUT=P/'job-state'/meta['romSha1'];OUT.mkdir(parents=True,exist_ok=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'state.elf';binary=OUT/'state.bin'
flags=['-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding',
 '-fno-builtin','-Wall','-Wextra','-Werror','-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion')]
# The sole stack-allocated evaluated-unit consumer must be recompiled with its
# larger frame. Preserve the existing Samurai copy observer around that frame.
rider=(ROOT/'src/engine/physical-riders.c').read_text()
rider=rider.replace('ffta_evaluated_init(', 'ffta_snapshotted_evaluated_init(').replace('ffta_evaluated_close(', 'ffta_snapshotted_evaluated_close(')
rider='extern unsigned ffta_snapshotted_evaluated_init(void *,const unsigned char *);\nextern void ffta_snapshotted_evaluated_close(void *);\n'+rider
(OUT/'physical-riders.c').write_text(rider)
sources=[ROOT/'src/engine'/n for n in ('job-state.c','job-save.c','job-save.s','runtime.c','unit-copies.c','evaluated-units.c')]+[OUT/'physical-riders.c']
objects=[];defined=set();unresolved=set();replacements=set()
for i,source in enumerate(sources):
 obj=OUT/f'part{i}.o';objects.append(obj)
 subprocess.run([prefix+'gcc.exe',*flags,'-c',str(source),'-o',str(obj)],check=True)
 for line in subprocess.check_output([prefix+'nm.exe','-g',str(obj)],text=True).splitlines():
  p=line.split()
  if len(p)==3:
   defined.add(p[2])
   if source.name in ('unit-copies.c','evaluated-units.c','physical-riders.c'):replacements.add(p[2])
  elif len(p)==2 and p[0] in ('U','w'):unresolved.add(p[1])
imports={'ffta_job_original_migrate':'ffta_load_migrate_abilities',
 'ffta_job_original_give':'ffta_give_with_abilities','ffta_job_original_clear':'ffta_on_unit_clear',
 'ffta_job_original_swap':'ffta_swap_extra'}
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n';bound={}
for name in sorted(unresolved-defined):
 if name.startswith('__aeabi_'):continue # Link ARM/Thumb interworking helpers, never assume Thumb.
 target=imports.get(name,name)
 address=old.get(target,meta['symbols'].get(target))
 if address is None:
  assert name.startswith('__aeabi_'),('Unknown common prerequisite',name)
  continue
 bound[name]=address
 bindings+=f'.align 2\n.global {name}\n.thumb_func\n{name}:\n push {{r3}}\n ldr r3,={address|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(OUT/'bindings.s').write_text(bindings)
subprocess.run([prefix+'gcc.exe',*flags,'-nostdlib','-Wl,-Ttext=0x091d0000,-e,ffta_job_save_entry',
 *map(str,objects),str(OUT/'bindings.s'),'-lgcc','-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
rom=bytearray(base);code=binary.read_bytes();assert len(code)<0x10000 and rom[0x11d0000:0x11d0000+len(code)]==b'\xff'*len(code)
changes=[]
assert rom[0x13b2a8:0x13b2b4]==bytes.fromhex('f0b557464e464546e0b48db0')
rom[0x13b2a8:0x13b2b4]=bytes.fromhex('08b4c046004b1847')+struct.pack('<I',symbols['ffta_job_save_entry']|1)
changes.append(dict(offset=0x13b2a8,size=12,name='native synchronous save/footer'))
# Rebind only known existing code regions to the enlarged implementations.
# Samurai observers retain their entrypoints and forward to the new owners.
# Patch the base before appending the new module: original imports stay intact.
engine_size=len((ROOT/'build/expansion/engine.bin').read_bytes())
samurai_size=len((P/'samurai'/meta['baseSha1']/'samurai.bin').read_bytes())
regions=[(0x1100000,engine_size),(0x11c0000,samurai_size)]
for name in sorted(replacements & old.keys()):
 sites=[];pointers=[]
 for start,size in regions:
  for offset in range(start,start+size-2,2):
   a,b=struct.unpack_from('<HH',rom,offset)
   if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
   delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
   if delta&0x400000:delta-=0x800000
   if 0x08000000+offset+4+delta!=old[name]:continue
   delta=symbols[name]-(0x08000000+offset+4);assert -0x400000<=delta<0x400000 and not delta&1
   struct.pack_into('<HH',rom,offset,0xf000|((delta>>12)&0x7ff),0xf800|((delta>>1)&0x7ff));sites.append(offset)
  for offset in range(start,start+size-3,4):
   if struct.unpack_from('<I',rom,offset)[0]==old[name]|1:
    struct.pack_into('<I',rom,offset,symbols[name]|1);pointers.append(offset)
 changes.append(dict(name=name,callSites=sites,pointerSites=pointers))
for source,target in [('ffta_load_migrate_abilities','ffta_job_load'),
                      ('ffta_give_with_abilities','ffta_job_give'),('ffta_on_unit_clear','ffta_job_clear'),
                      ('ffta_swap_extra','ffta_job_swap_persistent')]:
 sites=[]
 for offset in range(0x1100000,0x1100000+engine_size-2,2):
  a,b=struct.unpack_from('<HH',rom,offset)
  if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
  delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
  if delta&0x400000:delta-=0x800000
  if 0x08000000+offset+4+delta!=old[source]:continue
  delta=symbols[target]-(0x08000000+offset+4);assert -0x400000<=delta<0x400000 and not delta&1
  struct.pack_into('<HH',rom,offset,0xf000|((delta>>12)&0x7ff),0xf800|((delta>>1)&0x7ff));sites.append(offset)
 assert sites,source
 changes.append(dict(name=target,callSites=sites))
def word_patch(offset,before,after,name):
 assert struct.unpack_from('<I',rom,offset)[0]==before,(name,hex(offset))
 struct.pack_into('<I',rom,offset,after);changes.append(dict(offset=offset,size=4,name=name,old=before,new=after))
for offset in (0x9e8b4,0x9f7e8,0x9f848,0x9f8dc):word_patch(offset,0x1014,0x1140,'snapshot allocation')
for offset in (0x71118,0x711f8):word_patch(offset,0x7268,0x7280,'party copy allocation')
start=old['ffta_selection_allocate']-0x08000000
hits=[i for i in range((start+3)&~3,start+80,4) if struct.unpack_from('<I',rom,i)[0]==0x3828]
assert len(hits)==1,hits
word_patch(hits[0],0x3828,0x3840,'selection copy allocation')
for offset,before,after,name in [(old['ffta_original_manager']-0x08000000+6,0x2480,0x2486,'manager allocation'),
                                (0x96ef4,0x2090,0x2096,'manager parent capacity')]:
 assert struct.unpack_from('<H',rom,offset)[0]==before,(name,hex(offset))
 struct.pack_into('<H',rom,offset,after);changes.append(dict(offset=offset,size=2,name=name,old=before,new=after))
for name in ('ffta_battle_heap_limit','ffta_results_heap_limit','ffta_global_heap_limit'):
 start=old[name]-0x08000000
 hits=[i for i in range(start,start+28,4) if struct.unpack_from('<I',rom,i)[0]==0x0203f800]
 assert len(hits)==1,(name,hits)
 struct.pack_into('<I',rom,hits[0],0x0203f400)
 changes.append(dict(offset=hits[0],size=4,name=name,old=0x0203f800,new=0x0203f400))
rom[0x11d0000:0x11d0000+len(code)]=code
digest=hashlib.sha1(rom).hexdigest();ART=OUT/digest;ART.mkdir(exist_ok=True)
path=ART/'job-state.gba';path.write_bytes(rom);(ART/'input.gba').write_bytes(base)
report=dict(status='Private canonical/save and enlarged copy bridge; lifecycle acceptance pending',
 baseSha1=meta['romSha1'],romSha1=digest,path=str(path),symbols={**meta['symbols'],**symbols},
 changes=changes,imports=bound,heapEnd=0x0203f400,bank=0x0203f400,bankBytes=808,recordBytes=22,footerBytes=824,
 copySizes=dict(evaluated=304,snapshot=0x1140,manager=0x430,selection=0x3840,party=0x7280))
(ART/'manifest.json').write_text(json.dumps(report,indent=2));(P/'job-state/current.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='symbols'},indent=2))
