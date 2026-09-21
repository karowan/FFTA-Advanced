"""All-map/all-animation capacity bound for the proposed terrain ring cache.

Native quarter-plane queries use an authenticated existing map-state capture.
Each contributing field may independently be absent, dashed or continuous in
each8x8 cell: this over-approximates every legal36-caster board. Palette and
animation pixels are exact. This audit does not allocate live video memory.
"""
import hashlib,json,pathlib,struct,sys
from ffta_maps import Maps,COUNT,CLEAN_SHA1,TABLE,tile_center
from ffta_geo_assets import tile_variants,graphics_animations
animation_union='--animation-union' in sys.argv
ROOT=pathlib.Path(__file__).resolve().parents[1]
fixture=ROOT/'scripts/test-geomancer-compositor.py'
ns={'__file__':str(fixture),'__name__':'ring_capacity_fixture'}
exec(compile(fixture.read_text(encoding='utf-8').split('for kind,camera in ')[0],str(fixture),'exec'),ns)
u,call,symbols,OUT,CAPACITY=(ns[k] for k in ('u','call','symbols','OUT','CACHE'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_PC,UC_ARM_REG_LR
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert hashlib.sha1(clean).hexdigest()==CLEAN_SHA1
maps=Maps(clean);u.mem_write(0x08000000,clean)
frozen=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1/ecfa1755355cc1e5e512e2ec825dc5be8c0782ea/executor'
captures={}
for name,want,address in (('ram','a8e6c2ef237bac2b2774c281e94a7323bf0033ac',0x02000000),('iwram','761ee39d19804c61525588f0df390bc2803f41fc',0x03000000)):
 data=(frozen/f'execute-trap.{name}').read_bytes();assert hashlib.sha1(data).hexdigest()==want
 captures[name]=want;u.mem_write(address,data)
native=ROOT/'build/expansion/terrain'/CLEAN_SHA1/'native-loader'
loader=json.loads((native/'report.json').read_text(encoding='utf-8'))
assert loader['passed'] and loader['cleanRomSha1']==CLEAN_SHA1 and len(loader['maps'])==COUNT
symbols['native_project']=0x0801d624;observed=[]
def observe(u,address,size,data):
 ptr=int.from_bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4),'little')
 observed.append((u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3),bytes(u.mem_read(ptr,4))))
 u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
hook=u.hook_add(UC_HOOK_CODE,observe,begin=0x0801d130,end=0x0801d130)

def bound(variants):
 groups={frozenset():0};sizes=[0];grid=[]
 for plane in variants:
  row=[]
  for values in plane:
   key=frozenset(v for v in values if v)
   if key not in groups:groups[key]=len(sizes);sizes.append(len(key))
   row.append(groups[key])
  grid.append(row)
 best=(0,0,0)
 # Outside-canvas windows are subsets of a containing in-canvas window.
 for y in range(44):
  counts=[0]*len(sizes);total=1
  def change(g,d):
   nonlocal total
   total-=min(counts[g],sizes[g]);counts[g]+=d;total+=min(counts[g],sizes[g])
  for yy in range(y,y+21):
   for x in range(31):
    for p in range(2):change(grid[p][yy*64+x],1)
  for x in range(34):
   if total>best[0]:best=total,x,y
   if x<33:
    for yy in range(y,y+21):
     for p in range(2):change(grid[p][yy*64+x],-1);change(grid[p][yy*64+x+31],1)
 return dict(tiles=best[0],x=best[1]*8,y=best[2]*8)

results=[];total_frames=0;unique_frames=0
for entry in loader['maps']:
 index=entry['map'];parts={}
 for name,address in (('height',0x02007cb0),('arrangement',0x020091a0),('clipping',0x0200d1a0)):
  data=(native/f'map-{index:03}-{name}.bin').read_bytes();assert hashlib.sha1(data).hexdigest()==entry[name+'Sha1']
  parts[name]=data;u.mem_write(address,data)
 u.mem_write(0x02007f10,struct.pack('<H',index));u.mem_write(0x02007f14,struct.pack('<I',0x02007cb0))
 u.mem_write(0x02007f18,bytes((16,16,0,0,0,16,0,16)));u.mem_write(0x02007f60,struct.pack('<2H',256,256))
 contributions=[{},{}]
 for i in range(256):
  x,y=i%16,i//16;h=parts['height'][2*i]
  if not h:continue
  observed.clear();call('native_project',x,y,1);assert len(observed)==1
  nx,ny,planes=observed[0];cx,cy=tile_center(x,y,h);px,py=cx-16,cy-8
  assert (nx,ny)==((px>>3)&255,(py>>3)&255) and all(p<2 for p in planes)
  for q,p in enumerate(planes):
   for ly in range(8):
    for width in (-1,0,1,2):
     if not 0<=(2*ly if q in (1,2) else 14-2*ly)+width<16:continue
     sx=px+(q&1)*16+(2*ly if q in (1,2) else 14-2*ly)+width;sy=py+(q>>1)*8+ly
     if not(0<=sx<512 and 0<=sy<512):continue
     cell=(sy//8)*64+sx//8;mask=15<<(4*((sy%8)*8+sx%8))
     choices=contributions[p].setdefault(cell,{}).setdefault(i,[0,0,0,0])
     choices[2]|=mask
     if width in (0,1):choices[3]|=mask
     if not ly&2:
      choices[0]|=mask
      if width in (0,1):choices[1]|=mask
 masks=[{},{}]
 for p in range(2):
  for cell,fields in contributions[p].items():
   possible={(0,0)}
   for rs,rc,fs,fc in set(map(tuple,fields.values())):
    possible={(s|ds,c|dc) for s,c in possible for ds,dc in ((0,0),(rs,rc),(fs,fc))}
   assert len(possible)<=4096,(index,p,cell,'unbounded field masks')
   masks[p][cell]=tuple(possible)
 words=[struct.unpack_from('<4096H',parts['arrangement'],p*8192) for p in range(2)]
 assert all(not w&0xc00 for plane in words for w in plane),'Native source unexpectedly uses graphics flips'
 palette_data=maps.palette(index).data
 assert all(((w>>12)&7)*32<len(palette_data) for plane in words for w in plane),(index,'palette bank outside map palette')
 palette=struct.unpack('<128H',palette_data[:256].ljust(256,b'\0'));ink=[]
 for bank in range(8):
  intensity=lambda i:3*(palette[bank*16+i]&31)+6*((palette[bank*16+i]>>5)&31)+((palette[bank*16+i]>>10)&31)
  bright=max(range(1,16),key=intensity);dark=min(range(1,16),key=intensity)
  ink.append((int.from_bytes(bytes([dark*17])*32,'little'),int.from_bytes(bytes([bright*17])*32,'little')))
 animation=struct.unpack_from('<i',maps.record(index),20)[0]
 frames=struct.unpack_from('<H',clean,TABLE+animation+2)[0] if animation>0 else 1
 if animation_union:frames=1
 seen={};frame_results=[];retained=set()
 for frame in range(frames):
  graphics=maps.tiles(index,frame);assert len(graphics)<=0x5000
  options=tile_variants(maps,index) if animation_union else tuple((graphics[i:i+32],) for i in range(0,len(graphics),32))
  sha=hashlib.sha1(b''.join(struct.pack('<I',len(v))+b''.join(v) for v in options)).hexdigest();total_frames+=1
  if sha in seen:frame_results.append(dict(frame=frame,graphicsSha1=sha,reusesFrame=seen[sha]));continue
  seen[sha]=frame;unique_frames+=1
  tiles=[tuple(int.from_bytes(v,'little') for v in values) for values in options]
  opacity=[all(v&15 and v>>4 for tile in values for v in tile) for values in options]
  ids={0:0};variants=[[()]*4096 for _ in range(2)]
  for cell in range(4096):
   for p in range(2):
    upper=words[0][cell]&1023
    if p and upper<len(opacity) and opacity[upper]:continue
    word=words[p][cell];number=word&1023
    if number>=len(tiles):
     assert animation_union and number<640,(index,frame,p,cell,number)
     retained.add(number);choices=[]
     # Arbitrary preserved native bytes: never assume black/transparent or
     # deduplicate them against decoded graphics. Equal identity/mask/ink
     # still guarantees equal output and supplies a conservative bound.
     for shadow,core in masks[p].get(cell,((0,0),)):
      dark,light=ink[(word>>12)&7];mask=shadow|core
      colored=(dark&shadow&~core)|(light&core)
      symbolic=('retained',number,mask,colored)
      if symbolic not in ids:ids[symbolic]=len(ids)
      choices.append(ids[symbolic])
     variants[p][cell]=tuple(choices);continue
    choices=[]
    for original in tiles[number]:
     for shadow,core in masks[p].get(cell,((0,0),)):
      dark,light=ink[(word>>12)&7]
      composed=(original&~(shadow|core))|(dark&shadow&~core)|(light&core)
      if composed not in ids:ids[composed]=len(ids)
      choices.append(ids[composed])
    variants[p][cell]=tuple(choices)
  peak=bound(variants)
  frame_results.append(dict(frame=frame,graphicsSha1=sha,bound=peak,withinCapacity=peak['tiles']<=CAPACITY))
 result=dict(map=index,frames=frame_results,retainedNativeTileIds=sorted(retained))
 if animation_union:result['animationStreams']=[dict(control=a.control,destination=a.destination,length=a.length,frames=len(a.frames)) for a in graphics_animations(maps,index)]
 results.append(result)
 if index%20==0:print(json.dumps(dict(progressMap=index,uniqueFrames=unique_frames)),flush=True)
u.hook_del(hook)
failures=[dict(map=r['map'],**f) for r in results for f in r['frames'] if f.get('withinCapacity') is False]
worst=sorted((dict(map=r['map'],**f) for r in results for f in r['frames'] if 'bound' in f),key=lambda f:f['bound']['tiles'],reverse=True)[:12]
report=dict(passed=not failures,cleanRomSha1=CLEAN_SHA1,captureHashes=captures,
 sourceSha1=ns['digest'],frames=total_frames,uniqueFrames=unique_frames,maps=results,worst=worst,failures=failures,
 independentAnimationTiles=animation_union,capacity=CAPACITY,
 animationDecoderSha1=hashlib.sha1((ROOT/'scripts/ffta_geo_assets.py').read_bytes()).hexdigest(),
 limits=['Capacity upper bound only; no live ring allocation, heap or upload timing acceptance',
 'Independent absent/dashed/continuous edges over-approximate legal field placement; no flip deduplication needed'])
(OUT/('ring-animation-capacity.json' if animation_union else 'ring-capacity.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='maps'},indent=2))
assert report['passed'],(f'{CAPACITY}-slot conservative capacity unresolved',len(failures))
