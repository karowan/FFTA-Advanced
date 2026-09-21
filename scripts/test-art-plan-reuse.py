"""Installed plan reuse: exact-input invalidation and legacy output differential."""
import argparse, ast, datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text(encoding='utf-8').replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
out=ROOT/'build/art/plan-reuse'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path,required=True,
                    help='Immutable retained trial; does not compile or enable its rejected source.')
args=parser.parse_args()
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 meta=json.loads(args.candidate_manifest.read_text(encoding='utf-8'))
 rom=Path(meta['path']).read_bytes();symbols=meta['symbols']
 check(meta['planReuse'] and hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Installed candidate authenticated')
 check(meta['planReuseOffset']==11312 and meta['planReuseBytes']==948 and meta['transientStateBytes']==12260,
       'Cache appended within existing reservation, no prior live offsets moved')
 check(meta['ramReservation'][0]+meta['transientStateBytes']<=meta['partyHeapRoot'],'Separate native party root retained')
 a=ARM(rom,bytes(0x8000))
 F,O,V,P,C,T,R,CACHE,BACKUP,SCENE=0x02010000,0x02011000,0x02020000,0x02012000,0x02012400,0x02013000,0x02013100,0x02014000,0x02016000,0x02017000
 colors=bytes((i*7)%256 for i in range(640));palette=bytes((i*13)%256 for i in range(512))
 default_frame=struct.pack('<8I',O,V,T,P,C,R,1,20)
 a.put(F,default_frame);a.put(C,colors)
 apply=symbols['ffta_art_palette_scene_apply'];validate=symbols['ffta_art_palette_scene_reusable'];legacy=symbols['ffta_art_palette_live_apply']
 oam=bytearray(struct.pack('<4H',0x200,0,0,0)*128);tags=bytearray([255]*128)
 # One native 64x32 8bpp consumer, four custom classes including history19.
 struct.pack_into('<4H',oam,0,0x6000,0xc000,0,0)
 for i,owner in enumerate((0,4,15,19),1):
  struct.pack_into('<4H',oam,i*8,32,0x8040,0,0);tags[i]=owner
 struct.pack_into('<4H',oam,127*8,0,0,0,0) # Native bank0 consumer.
 pixels=bytes([16])*2048+bytes(32768-2048)
 a.put(O,oam);a.put(T,tags);a.put(V,pixels);a.put(P,palette);a.put(R,bytes(32));a.put(CACHE,bytes(2124));a.put(SCENE,bytes(948));a.put(BACKUP,b'\xc7'*512)
 check(a.call(apply,F,CACHE,BACKUP,SCENE)==1,'Cold installed composition succeeds')
 prior=a.read(R,32);saved_cache=a.read(CACHE,2124);saved_scene=a.read(SCENE,948)
 check([prior[8+x] for x in (0,4,15,19)]==[2,3,4,5],'Independent native bank occupancy assigns banks2..5')
 check(struct.unpack_from('<3I',saved_scene,936)==(0x504c4e31,0,1),'Cold plan records one miss and a valid key')
 def setup(objects=oam,owners=tags,tiles=pixels,native=palette,custom=colors,plan=prior,cache=saved_cache,scene=saved_scene,frame=default_frame):
  for address,data in ((O,objects),(T,owners),(V,tiles),(P,native),(C,custom),(R,plan),(CACHE,cache),(SCENE,scene),(F,frame),(BACKUP,b'\xc7'*512)):
   a.put(address,data)
 def reusable(label,expected=1,**kw):
  setup(**kw);before=a.read(0x02010000,0x18000)
  check(a.call(validate,F,CACHE,SCENE)==expected,label)
  check(a.read(0x02010000,0x18000)==before,label+' validation is read-only')
 def differential(label,hit=None,**kw):
  setup(**kw);result=a.call(legacy,F,CACHE,BACKUP)
  expected=(result,a.read(O,1024),a.read(P,512),a.read(R,32),a.read(BACKUP,512))
  setup(**kw);result=a.call(apply,F,CACHE,BACKUP,SCENE,stack=STACK-4)
  check((result,a.read(O,1024),a.read(P,512),a.read(R,32),a.read(BACKUP,512))==expected,label+' matches original planner/apply/backup')
  if hit is not None:check(a.word(SCENE+940)==hit,label+' expected cache hit count')
 reusable('Unchanged full mixed frame reuses')
 differential('Unchanged mixed frame',hit=1)
 # Differential every bit in every OAM attribute against the original full
 # planner, rather than treating irrelevant position/tile changes as misses.
 # Attr3 is irrelevant to full affine tile reservation and stays native.
 for i in range(128):
  for lane in range(3):
   for bit in range(16):
    changed=bytearray(oam);offset=i*8+lane*2+bit//8;changed[offset]^=1<<(bit%8)
    differential('Changed OAM bit '+str((i,lane,bit)),objects=changed)
  changed=bytearray(tags);changed[i]^=1
  reusable('Changed owner '+str(i),0,owners=changed)
  a.u.ctl_flush_tb()
 for i in range(1,5):
  changed=bytearray(oam);struct.pack_into('<3H',changed,i*8,72,0x8080,352)
  reusable('Custom movement and animation do not change planning '+str(i),objects=changed)
  differential('Custom movement and animation '+str(i),hit=1,objects=changed)
 changed=bytearray(oam)
 for i in range(128):struct.pack_into('<H',changed,i*8+6,(i*113)&65535)
 reusable('Affine coefficients do not alter conservative source footprint',objects=changed)
 differential('Native affine coefficients preserved',hit=1,objects=changed)
 # Every visible source byte invalidates even if its high palette nibble is
 # unchanged. The cache never treats an equal bank mask as equal pixels.
 for i in range(2048):
  changed=bytearray(pixels);changed[i]=17
  reusable('Changed visible pixel '+str(i),0,tiles=changed)
 a.u.ctl_flush_tb()
 for i in (0,3,63,64,1023,2047):
  changed=bytearray(pixels);changed[i]=32
  differential('New native conflict '+str(i),hit=0,tiles=changed)
 for i in (2048,32767):
  changed=bytearray(pixels);changed[i]=32
  reusable('Unused tile byte '+str(i),tiles=changed)
  differential('Unused tile byte '+str(i),hit=1,tiles=changed)
 for i in range(32):
  changed=bytearray(prior);changed[i]^=1
  reusable('Changed plan representation '+str(i),0,plan=changed)
 for field,value in ((6,0),(7,19),(7,21)):
  frame=bytearray(default_frame);struct.pack_into('<I',frame,field*4,value)
  reusable('Changed frame contract '+str((field,value)),0,frame=frame)
 for tile in range(32):
  changed=bytearray(saved_cache);struct.pack_into('<I',changed,2120,0xffffffff^(1<<tile))
  reusable('Missing cached tile '+str(tile),0,cache=changed)
 for native,custom in ((bytes([93])*512,colors),(palette,bytes([28])*640),(bytes([73])*512,bytes([51])*640)):
  differential('Current native/custom color values '+str((native[0],custom[0])),hit=1,native=native,custom=custom)
 # Changed dimensions, clipping, flips, affine/mosaic and a second8bpp object
 # must take a complete fallback. After that, a hit is optional, but output
 # must remain identical on the next frame too.
 for attr0,attr1,attr2 in [(0x2000,0xc000,0),(0x6000,0x8000|232,0),(0x6000|152,0x9000|232,0),(0x6100,0x8000,0),(0x7000,0x8000,0),(0x6000,0x8000,1022)]:
  changed=bytearray(oam);struct.pack_into('<3H',changed,0,attr0,attr1,attr2)
  differential('Changed geometry '+str((attr0,attr1,attr2)),hit=0,objects=changed)
  next_plan,next_cache,next_scene=a.read(R,32),a.read(CACHE,2124),a.read(SCENE,948)
  differential('Repeated geometry '+str((attr0,attr1,attr2)),objects=changed,
               plan=next_plan,cache=next_cache,scene=next_scene)
 changed=bytearray(oam);struct.pack_into('<4H',changed,8*10,0x6000,0xc000,64,0)
 changed_pixels=bytearray(pixels);changed_pixels[2048:4096]=bytes([32])*2048
 differential('Second8bpp object alias falls back',hit=0,objects=changed,tiles=changed_pixels)
 next_plan,next_cache,next_scene=a.read(R,32),a.read(CACHE,2124),a.read(SCENE,948)
 reusable('Second8bpp object cannot reuse overwritten tile cache',0,objects=changed,tiles=changed_pixels,
          plan=next_plan,cache=next_cache,scene=next_scene)
 differential('Repeated second8bpp object remains exact',objects=changed,tiles=changed_pixels,
              plan=next_plan,cache=next_cache,scene=next_scene)
 # Failure is atomic for hardware outputs and cannot publish a reusable key.
 changed=bytearray(oam);struct.pack_into('<H',changed,0,0xc000)
 differential('Invalid shape fails without palette/OAM writes',hit=0,objects=changed)
 check(a.word(SCENE+936)==0,'Failed planning clears reuse validity')
 base=meta['ramReservation'][0]
 a.put(base,bytes(meta['transientStateBytes']))
 a.put(base+meta['planReuseOffset']+936,struct.pack('<3I',0x504c4e31,77,99))
 a.put(meta['partyHeapRoot']-12,b'\xd7'*12)
 a.call(symbols['ffta_art_heap_reset'])
 check(a.read(base+meta['planReuseOffset']+936,12)==bytes(12),'Heap reset invalidates an existing key and both counters')
 check(a.read(meta['partyHeapRoot']-12,12)==b'\xd7'*12,'Twelve-byte gap before native party root preserved')
 report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],sources=meta['sources'],
   scope='Installed twenty-slot exact-input plan reuse; exhaustive OAM/key/visible-byte invalidation, read-only validation, changed colors and native backup, original-function differential, invalid and larger footprints. Synthetic component inputs, not natural scene timing or final art.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
