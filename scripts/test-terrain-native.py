"""Independent native decompression and captured height-grid differentials."""
import pathlib,sys,json,hashlib,struct,runpy,ctypes as C
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
from ffta_maps import Maps,COUNT,TABLE,tile_center
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();maps=Maps(rom)
OUT=ROOT/'build/expansion/terrain'/hashlib.sha1(rom).hexdigest();OUT.mkdir(parents=True,exist_ok=True)
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
for address,size in ((0x08000000,0x2000000),(0x02000000,0x40000),(0x03000000,0x8000)):u.mem_map(address,size)
u.mem_write(0x08000000,rom);streams={}
for i in range(COUNT):
 for s in (maps.graphics(i),maps.palette(i)):
  if s.codec=='lzss':streams[s.address]=s
results=[]
for address,s in streams.items():
 u.mem_write(0x02000000,b'\xa5'*0x20020)
 for r,v in ((UC_ARM_REG_R0,0x02000010),(UC_ARM_REG_R1,0x08000000+address),(UC_ARM_REG_SP,0x03007e00),(UC_ARM_REG_LR,0x08000101)):u.reg_write(r,v)
 u.emu_start(0x0800543d,0x08000100,count=5000000)
 assert u.reg_read(UC_ARM_REG_PC)==0x08000100,('Native decompressor did not return',hex(address))
 got=bytes(u.mem_read(0x02000010,len(s.data)))
 assert got==s.data,('Native LZSS mismatch',hex(address),next(i for i,(a,b) in enumerate(zip(got,s.data)) if a!=b))
 assert bytes(u.mem_read(0x02000000,16))==b'\xa5'*16 and bytes(u.mem_read(0x02000010+len(s.data),16))==b'\xa5'*16
 results.append(dict(address=address,bytes=len(got),sha1=hashlib.sha1(got).hexdigest()))
# Independently derive every valid cell's projection through both original
# coordinate routines. The ROM map loader initializes this canvas origin.
u.mem_write(0x02007f60,struct.pack('<2H',256,256));projected=0
def native(address,*args):
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(r,v)
 for r,v in ((UC_ARM_REG_SP,0x03007e00),(UC_ARM_REG_LR,0x08000101)):u.reg_write(r,v)
 u.emu_start(address|1,0x08000100,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x08000100,('Projection did not return',hex(address))
for index in range(COUNT):
 h=maps.heights(index)
 for y in range(16):
  for x in range(16):
   z=h[(y*16+x)*2]
   if not z:continue
   u.mem_write(0x02030000,bytes((x,z,y)))
   native(0x0801ca98,0x02030000,0x02030010)
   world=struct.unpack('<3h',u.mem_read(0x02030010,6))
   assert world==(32*x+16,16*z,32*y+16),(index,x,y,'world',world)
   u.mem_write(0x03007e00,struct.pack('<2I',0x02030022,0x02030024))
   native(0x0801c918,*world,0x02030020)
   got=struct.unpack('<3h',u.mem_read(0x02030020,6))
   assert got==(*tile_center(x,y,z),32*(x+y+1)),(index,x,y,'canvas',got)
   projected+=1
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text());fixture=pathlib.Path(meta['path']).parent/'executor'
OUT=OUT/meta['romSha1'];OUT.mkdir(exist_ok=True)
assert json.loads((fixture/'manifest.json').read_text())['romSha1']==meta['romSha1']
ram=(fixture/'execute-trap.ram').read_bytes();index=struct.unpack_from('<H',ram,0x7f10)[0];pointer=struct.unpack_from('<I',ram,0x7f14)[0]-0x02000000
assert index==70 and ram[0x7f18]==16,('Unexpected fixed battle map',index)
assert struct.unpack_from('<2H',ram,0x7f60)==(256,256),'Captured native canvas origin'
height=maps.heights(index)[:512];native=ram[pointer:pointer+512]
assert height==native,('Captured native height mismatch',[(i,a,b) for i,(a,b) in enumerate(zip(height,native)) if a!=b][:12])
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(meta['path'])
try:
 e.load(pathlib.Path(meta['path']).parent/'fixture/battle-ready.state');e.run(1)
 regions={hex(a):n for a,(_,n) in e.maps.items()};vram=C.string_at(*e.maps[0x06000000])
 (OUT/'giza-native.vram').write_bytes(vram);e.screenshot(OUT/'giza-native.png')
 static=maps.graphics(70).data
 offsets=[i for i in range(0,len(vram)-len(static)+1,32) if vram[i:i+512]==static[:512]]
 graphicsMatches=[dict(offset=i,exact=vram[i:i+len(static)]==static) for i in offsets]
 assert graphicsMatches==[dict(offset=0x820,exact=True)],graphicsMatches
 # A frame-boundary capture may split the native two-chunk animation upload.
 # Validate all bytes against the original ROM's adjacent animation phases,
 # then require multiple complete native frames. Do not assume a fixed phase
 # after source changes alter the number of frames needed to reach the menu.
 record=maps.record(70);animation=TABLE+struct.unpack_from('<i',record,0x14)[0]
 count=struct.unpack_from('<H',rom,animation+2)[0]
 length=struct.unpack_from('<H',rom,animation)[0]&0xffe0
 skip=struct.unpack_from('<I',record,0x1c)[0]&0xffffff
 assert (count,length,skip)==(4,2048,32),'Unexpected native Giza animation layout'
 catalog=[maps.tiles(70,i) for i in range(count)];observations=[];complete=set()
 for tick in range(32):
  if tick:e.run(1)
  current=C.string_at(*e.maps[0x06000000])[:len(catalog[0])]
  assert current[:skip]==catalog[0][:skip] and current[skip+length:]==catalog[0][skip+length:],'Static Giza bytes changed'
  matches=[i for i,b in enumerate(catalog) if b==current]
  chunks=[[i for i,b in enumerate(catalog) if b[start:start+1024]==current[start:start+1024]] for start in (skip,skip+1024)]
  assert any((left-right)%count in (0,1) for left in chunks[0] for right in chunks[1]),('Invalid native animation bytes/order',tick,chunks)
  observations.append(dict(tick=tick,completeFrames=matches,chunkFrames=chunks,sha1=hashlib.sha1(current).hexdigest()))
  if matches:
   complete.update(matches);(OUT/('giza-complete-'+str(matches[0])+'.vram')).write_bytes(current)
 assert len(complete)>=2,('Native animation did not produce distinct complete frames',observations)
 print('Native graphics placement',graphicsMatches,'regions',regions,flush=True)
finally:e.close()
report=dict(passed=True,cleanRomSha1=hashlib.sha1(rom).hexdigest(),fixtureRomSha1=meta['romSha1'],nativeLzss=results,nativeProjectedCells=projected,capturedMap=index,heightSha1=hashlib.sha1(height).hexdigest(),graphicsMatches=graphicsMatches,regions=regions,animationObservations=observations,completeAnimationFrames=sorted(complete))
(OUT/'native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=True,nativeStreams=len(results),capturedMap=index),indent=2))
