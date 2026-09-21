"""Historical two-pixel feasibility audit, not current renderer acceptance.

The current production stroke and independent-animation bound are covered by
 test-geomancer-ring-capacity.py --animation-union. This retained experiment
 describes the original feasibility alternatives only.

Use production quarter projection, native captured map components and every
8-pixel camera window. Full-board outlines deliberately exceed ordinary field
coverage. Count the exact distinct8x8 graphics required in a31x21 viewport,
excluding a lower tile only when native foreground pixels fully occlude it.
No video-memory reservation is inferred from a quiet emulator screenshot.
"""
import collections,hashlib,json,pathlib,struct,sys
from ffta_maps import Maps,COUNT,CLEAN_SHA1
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-geomancer-map.py';ns={'__file__':str(source),'__name__':'capacity_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('for first,second,center in itertools.product')[0],str(source),'exec'),ns)
m,meta,OUT,fresh=(ns[k] for k in ('m','meta','OUT','fresh'))
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();maps=Maps(clean)
native=ROOT/'build/expansion/terrain'/CLEAN_SHA1/'native-loader'
loader=json.loads((native/'report.json').read_text(encoding='utf-8'))
assert loader['passed'] and loader['cleanRomSha1']==CLEAN_SHA1 and len(loader['maps'])==COUNT
fresh(380);base=m.read(0x02000000,0x40000)
project=meta['symbols']['ffta_geo_project_tile'];output=0x03007e00
folder=OUT/'geomancer-display-capacity';folder.mkdir(exist_ok=True)
results=[];peaks=[];mixed='--mixed-bound' in sys.argv;flips='--flip-cache' in sys.argv

def peak(ids):
 """Exact union over31x21 tile windows; includes sub-tile camera margins."""
 rows=[]
 for y in range(64):
  row=[]
  for x in range(34):
   bits=0
   for xx in range(x,x+31):
    for plane in range(2):
     i=ids[plane][y*64+xx]
     if i:bits|=1<<i
   row.append(bits)
  rows.append(row)
 best=(0,0,0)
 for y in range(44):
  for x in range(34):
   bits=0
   for yy in range(y,y+21):bits|=rows[yy][x]
   n=bits.bit_count()+1 # Reserve transparent tile0.
   if n>best[0]:best=(n,x,y)
 return best

def mixed_peak(variants):
 """Upper bound allowing each8x8 cell independent whole-edge choices.

 Group-identical choice sets for a quick bound. Only windows above640 need
 exact maximum matching. Independent choices relax real field correlations,
 so even an unattainable maximum remains a safe capacity bound.
 """
 groups={frozenset():0};choices=[()];grid=[]
 for plane in variants:
  row=[]
  for values in plane:
   key=frozenset(v for v in values if v)
   if key not in groups:groups[key]=len(choices);choices.append(tuple(sorted(key)))
   row.append(groups[key])
  grid.append(row)
 sizes=list(map(len,choices));best=(0,0,0);refinements=0
 def exact(nodes):
  matched={}
  def visit(n,seen):
   for graphic in nodes[n]:
    if graphic in seen:continue
    seen.add(graphic)
    if graphic not in matched or visit(matched[graphic],seen):matched[graphic]=n;return True
   return False
  for n in range(len(nodes)):visit(n,set())
  return len(matched)+1
 for y in range(44):
  counts=[0]*len(choices);bound=1
  def change(group,delta):
   nonlocal bound
   bound-=min(counts[group],sizes[group]);counts[group]+=delta
   bound+=min(counts[group],sizes[group])
  for yy in range(y,y+21):
   for x in range(31):
    for plane in range(2):change(grid[plane][yy*64+x],1)
  for x in range(34):
   value=bound
   if value>640:
    nodes=[choices[g] for g,n in enumerate(counts) for _ in range(min(n,sizes[g])) if g]
    value=exact(nodes);refinements+=1
   if value>best[0]:best=(value,x,y)
   if x<33:
    for yy in range(y,y+21):
     for plane in range(2):
      change(grid[plane][yy*64+x],-1);change(grid[plane][yy*64+x+31],1)
 return best,refinements

for entry in loader['maps']:
 index=entry['map'];m.put(0x02000000,base);parts={}
 for name,address in (('height',0x02007cb0),('arrangement',0x020091a0),('clipping',0x0200d1a0)):
  data=(native/f'map-{index:03}-{name}.bin').read_bytes()
  assert hashlib.sha1(data).hexdigest()==entry[name+'Sha1'],(index,name,'changed capture')
  parts[name]=data;m.put(address,data)
 m.put(0x02007f14,struct.pack('<I',0x02007cb0));m.put(0x02007f18,bytes((16,16,0,0,0,16,0,16)))
 m.put(0x02007f60,struct.pack('<2H',256,256))
 # Each mask covers a pixel in one native plane; union duplicate edges.
 masks=[{},{}];contributions=[{},{}];projected=0
 for y in range(16):
  for x in range(16):
   if not parts['height'][2*(16*y+x)]:continue
   assert m.call(project,x,y,output,stack=0x03007c00)==1
   px,py,*planes=struct.unpack('<hh4B',m.read(output,8));projected+=1
   for q,plane in enumerate(planes):
    for ly in range(8):
     start=(2*ly) if q in (1,2) else 14-2*ly
     for lx in (start,start+1):
      sx,sy=px+(q&1)*16+lx,py+(q>>1)*8+ly
      if not(0<=sx<512 and 0<=sy<512):continue
      cell=(sy//8)*64+sx//8;bit=(sy%8)*8+sx%8
      masks[plane][cell]=masks[plane].get(cell,0)|(1<<bit)
      c=contributions[plane].setdefault(cell,{})
      c[16*y+x]=c.get(16*y+x,0)|(1<<bit)
 graphics=maps.tiles(index);pal=maps.palette(index).data
 assert len(graphics)<=0x5000
 words=[list(struct.unpack('<4096H',parts['arrangement'][p*8192:(p+1)*8192])) for p in range(2)]
 colors=struct.unpack('<'+'H'*(len(pal)//2),pal)
 light=[];dark=[]
 for bank in range(len(colors)//16):
  values=colors[bank*16:(bank+1)*16]
  intensity=lambda i:3*(values[i]&31)+6*((values[i]>>5)&31)+((values[i]>>10)&31)
  light.append(max(range(1,16),key=intensity));dark.append(min(range(1,16),key=intensity))
 patterns={bytes(32):0};ids=[[0]*4096 for _ in range(2)];base_ids=[[0]*4096 for _ in range(2)]
 variants=[[()]*4096 for _ in range(2)]
 invisible_lower=0;affected=0
 def tile(word):
  number=word&4095
  return graphics[number*32:number*32+32] if number*32+32<=len(graphics) else None
 def ident(b):
  if flips:
   rows=[b[i:i+4] for i in range(0,32,4)]
   horizontal=[bytes((v>>4)|((v&15)<<4) for v in reversed(row)) for row in rows]
   b=min(b,b''.join(reversed(rows)),b''.join(horizontal),b''.join(reversed(horizontal)))
  if b not in patterns:patterns[b]=len(patterns)
  return patterns[b]
 def paint(original,mask,bank):
  b=bytearray(original)
  for bit in range(64):
   if mask>>bit&1:
    shift=(bit&1)*4
    ink=(light[bank] if bit&1 else dark[bank]) if mixed else light[bank]
    b[bit//2]=(b[bit//2]&~(15<<shift))|(ink<<shift)
  return bytes(b)
 for cell in range(4096):
  upper=tile(words[0][cell]);assert upper is not None
  opaque=all(b&15 and b>>4 for b in upper)
  for plane in range(2):
   original=tile(words[plane][cell])
   if plane==1 and opaque:
    invisible_lower+=1;continue
   assert original is not None,(index,plane,cell,'visible missing graphic')
   base_ids[plane][cell]=ident(original)
   mask=masks[plane].get(cell,0);bank=(words[plane][cell]>>12)&7
   if mask:
    affected+=1
   ids[plane][cell]=ident(paint(original,mask,bank))
   if mixed:
    possibilities={0}
    for edge in set(contributions[plane].get(cell,{}).values()):
     possibilities|={p|edge for p in possibilities}
    assert len(possibilities)<=4096,(index,plane,cell,'unbounded edge combinations')
    variants[plane][cell]=tuple({ident(paint(original,p,bank)) for p in possibilities})
 baseline=peak(base_ids);composed=peak(ids)
 result=dict(map=index,nativeTiles=len(graphics)//32,projectedCells=projected,affected8x8Tiles=affected,
  baselinePeak=dict(tiles=baseline[0],x=baseline[1]*8,y=baseline[2]*8),
  solidOutlinePeak=dict(tiles=composed[0],x=composed[1]*8,y=composed[2]*8),
  hiddenLowerTiles=invisible_lower,withinExisting640=composed[0]<=640)
 if mixed:
  upper,refined=mixed_peak(variants)
  result['independentEdgeBound']=dict(tiles=upper[0],x=upper[1]*8,y=upper[2]*8,refinedWindows=refined)
  result['withinExisting640']=upper[0]<=640
 results.append(result);peaks.append((composed[0],index,composed[1],composed[2]))
report=dict(passed=True,romSha1=meta['romSha1'],cleanRomSha1=CLEAN_SHA1,maps=results,
 worst=sorted(peaks,reverse=True)[:12],allWithin640=all(r['withinExisting640'] for r in results),
 mixedBound=mixed,flipCanonicalization=flips,failures=[r for r in results if not r['withinExisting640']],
 limits=['Feasibility counts only; no live allocation or rendering hook',
  'Independent per-cell edge choices bound arbitrary field occupancy; legal whole-field correlations are relaxed' if mixed else
  'Uniform solid outlines on every nonzero-height cell; arbitrary mixed field patterns not bounded',
  'First animation frame only; camera guards cover31x21 tiles; mission camera limits deliberately not narrowed',
  'Two-tone edges use brightest/darkest existing nontransparent palette entries; final styling not accepted' if mixed else
  'White means brightest existing nontransparent palette entry; final styling not accepted'])
(folder/('flip-report.json' if flips else 'mixed-report.json' if mixed else 'report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='maps'},indent=2))
