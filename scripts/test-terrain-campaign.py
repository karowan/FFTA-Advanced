"""Production material bytes, native campaign geometry and fixed native casts.

This is function/executor acceptance, not player UI, AI or a campaign playthrough.
Surfaces are reviewed content; the independent native height captures constrain
coordinates and neighborhood membership. Private zero-mask controls preserve
the same native map, units and RNG rather than substituting a flat test board.
"""
import pathlib,json,struct,hashlib,collections,itertools
from PIL import ImageDraw
from ffta_maps import Maps,COUNT,CLEAN_SHA1,tile_center
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-fields.py';ns={'__file__':str(source),'__name__':'campaign_fixture'}
exec(compile(source.read_text().split('for action,seed in itertools.product')[0],str(source),'exec'),ns)
m,meta,OUT,A,T,STACK,regs=(ns[k] for k in ('m','meta','OUT','A','T','STACK','regs'))
call,half,state=(ns[k] for k in ('call','half','state'))
wrappers=ns['ns']['ns']['wrappers'];MATERIALS=0x091f0000;GRID=0x02026000
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();maps=Maps(clean)
terrain=ROOT/'build/expansion/terrain'/CLEAN_SHA1;native=terrain/'native-loader'
loader=json.loads((native/'report.json').read_text())
assert loader['passed'] and loader['cleanRomSha1']==CLEAN_SHA1 and len(loader['maps'])==COUNT
catalog=json.loads((ROOT/'notes/terrain-materials.json').read_text());reviewed={e['map']:e for e in catalog['maps']}
assert len(catalog['maps'])==COUNT and set(reviewed)==set(range(COUNT)),'Incomplete campaign material coverage'
# Deliberately independent of the builder's table serialization function.
symbols={'.':0,'R':1,'V':2,'W':4,'H':8,'I':16,'S':18,'G':3,'T':10,'M':6}
expected=b''.join(bytes(symbols[s] for row in reviewed[i]['rows'] for s in row) if i in reviewed else bytes(256) for i in range(163))
production=pathlib.Path(meta['path']).read_bytes()[0x11f0000:0x11fa300]
assert production==expected,'Assembled terrain table differs from reviewed source'
heights={i:(native/f'map-{i:03}-height.bin').read_bytes() for i in range(COUNT)}
for row in loader['maps']:
 assert len(heights[row['map']])==512 and hashlib.sha1(heights[row['map']]).hexdigest()==row['heightSha1']
checks=collections.Counter();failures=[];samples=[];case=None;executions=0
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,actual=repr(a),expected=repr(b),case=case))

# Removing a map must fail the production build, not quietly emit neutral bytes.
from ffta_terrain import material_table
try:
 material_table(clean,dict(catalog,maps=catalog['maps'][:-1]))
except AssertionError as exc:
 check('build-rejects-missing-map',str(exc),'Terrain review must cover every native map')
else:check('build-rejects-missing-map',False,True)
def install(index,enabled=True):
 m.put(MATERIALS,production if enabled else bytes(163*256));m.put(GRID,heights[index])
 info=bytearray(16);struct.pack_into('<H',info,0,index)
 struct.pack_into('<I',info,4,GRID);info[8]=info[9]=info[13]=info[15]=16;m.put(0x02007f10,info)
def affinity(index,x,y):
 h=heights[index];z=h[2*(16*y+x)]
 if not z:return 0
 value=0
 for dx,dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1)):
  xx,yy=x+dx,y+dy
  if not (0<=xx<16 and 0<=yy<16):continue
  p=16*yy+xx;hz,flags=h[2*p:2*p+2]
  if not hz or abs(z-hz)>2:continue
  value|=expected[index*256+p]
  if flags&2:value|=4
 return value

# Independently reviewed semantic anchors prevent a broad palette-based rewrite
# from silently turning canvas into snow, green stone into grass, or crystal
# into ice. These expectations are not generated from the catalog being tested.
for index,x,y,mask,label in (
 (23,6,6,1,'red mineral crystal'),(32,0,0,1,'orange rock'),
 (32,7,0,4,'green water'),(38,5,4,3,'mossy pavers'),
 (38,5,2,10,'palm'),(42,2,0,1,'green patterned masonry'),
 (50,6,2,0,'white canvas'),(58,8,1,1,'blue crystal'),
 (63,0,0,0,'unrendered boundary'),(67,7,1,0,'scene perimeter'),
 (73,1,0,2,'night grass'),(76,7,4,0,'basin void'),
 (80,13,3,10,'conifer crown'),(80,14,3,1,'rock behind conifer'),
 (84,5,5,8,'cut stump'),(86,0,10,0,'ridge boundary'),
 (88,6,2,8,'forest stump'),(90,0,11,2,'ground behind tree'),
 (96,8,1,2,'autumn leaves'),(96,0,3,8,'dead trunk footprint'),
 (98,6,0,0,'loose desert sand'),(99,6,0,0,'night desert sand'),
 (98,10,1,1,'desert stone'),(106,4,2,2,'orange flowers'),
 (108,11,0,6,'waterlogged reeds'),(110,0,0,8,'wooden boardwalk'),
 (122,6,1,16,'snow plateau'),(126,4,10,8,'fallen log'),
 (129,3,5,1,'blue mineral formation'),(130,6,5,8,'cavern lava'),
 (135,3,0,1,'purple masonry'),(137,0,2,0,'decorative pole'),
 (143,1,5,10,'pool palm'),(149,4,0,2,'dry orange grass'),
 (155,6,7,4,'courtyard fountain'),(158,6,10,0,'blue carpet'),
 (160,1,1,8,'wooden bookcase'),(161,7,6,1,'prismatic mineral')):
 case=('reviewed material',index,x,y,label)
 check('independent-surface-anchor',production[index*256+16*y+x],mask)

ns['fresh'](381)
for index in range(COUNT):
 install(index)
 for y,x in itertools.product(range(16),repeat=2):
  case=('native neighborhood',index,x,y);m.put(A+0xf6,bytes((x,y)))
  want=affinity(index,x,y)
  check('production-native-affinity',call('ffta_geo_affinity',A),want)
  if not heights[index][2*(y*16+x)]:continue
  choices=[2]+[element for bit,element in ((1,3),(4,4),(8,1),(16,5)) if want&bit]
  count=call('ffta_geo_choices',A,381,0x02030000)
  check('campaign-Gaia-options',list(m.read(0x02030000,count)),choices)

# Save inspectable material overlays. No screenshot or color classifier writes
# material decisions; the source rows remain the explicit reviewed content.
colors={1:'#ffb870',2:'#70ff70',4:'#60cfff',8:'#ff6565',16:'#ffffff',18:'#d5ef80',3:'#c5ff70',10:'#ffa5a5',6:'#60ffc0'}
for index,entry in reviewed.items():
 pic,_,_=maps.render(index);draw=ImageDraw.Draw(pic)
 for y,row in enumerate(entry['rows']):
  for x,symbol in enumerate(row):
   mask=symbols[symbol]
   if not mask:continue
   cx,cy=tile_center(x,y,heights[index][2*(16*y+x)])
   draw.ellipse((cx-3,cy-3,cx+3,cy+3),outline=colors[mask],width=2)
 pic.save(terrain/f'map-{index:03}-materials.png')

scenarios=[
 ('stone floor',10,374,(6,4),(7,4),0),
 ('stone ward',10,378,(6,4),(7,4),0),
 ('wood platform',54,379,(3,0),(4,0),0),
 ('snow basin',118,380,(4,1),(5,1),0),
 ('grassland',70,375,(8,0),(9,0),0),
 ('volcanic edge',151,379,(4,14),(5,14),0),
 ('stream outside reach',68,376,(9,4),(10,4),1),
 ('stream',68,376,(10,5),(10,4),1),
 ('mossy masonry',38,374,(5,4),(6,4),0),
 ('palm canopy',38,379,(5,1),(6,1),0),
 ('mineral cavern',58,380,(6,8),(7,8),0),
 ('forest stump',88,379,(6,3),(7,3),0),
 ('autumn leaves',96,379,(8,1),(9,1),0),
 ('desert sand',98,379,(6,0),(7,0),0),
 ('night desert sand',99,380,(6,0),(7,0),0),
 ('desert stone',98,374,(10,1),(11,1),0),
 ('wetland boardwalk',110,379,(0,0),(1,0),0),
 ('snow plateau',122,380,(6,1),(7,1),0),
 ('fallen winter log',126,379,(3,10),(3,11),0),
 ('volcanic cavern',130,379,(6,6),(7,6),0),
 ('blue mineral cavern',129,380,(6,5),(7,5),0),
 ('prismatic cavern',161,379,(7,6),(8,6),0),
 ('wetland reeds',108,376,(11,1),(10,1),3),
]
costs={374:4,375:6,376:8,378:10,379:10,380:12}
for label,index,action,apos,tpos,choice in scenarios:
 for seed in range(8):
  values=[]
  for enabled in (False,True):
   case=('native campaign cast',label,seed,enabled);ns['fresh'](action,seed);install(index,enabled)
   if action==378:m.put(T+0x29,b'\x00')
   for unit,wrapper in wrappers.items():
    x,y=apos if unit==A else tpos if unit==T else (15,15)
    z=heights[index][2*(16*y+x)]
    m.put(unit+0xf6,bytes((x,y)));m.put(wrapper+8,struct.pack('<3H',32*x+16,16*z,32*y+16))
   m.put(regs[13],struct.pack('<4I',action,choice,0,255))
   m.call(0x080a433c,regs[0],wrappers[A],*tpos,stack=regs[13]);executions+=1
   loss=500-half(T+0x18)
   check('native-campaign-single-payment',half(A+0x1c),100-costs[action])
   check('native-campaign-command',half(regs[0]+0x10),action)
   check('native-campaign-roots-retire',m.read(0x0203ff44,8),bytes(8))
   values.append(dict(loss=loss,wisp=call('ffta_geo_wisp',T),steady=call('ffta_geo_steady',T),slow=bool(m.read(T+0xea,1)[0]&64),position=list(m.read(T+0xf6,2))))
  a,b=values
  if action==374:check('campaign-Stone-bonus',b['loss'],a['loss']*6//5)
  if action==378:check('campaign-Ward-Steady',(a['steady'],b['steady']),(0,1))
  if action==379:
   heat=label not in ('autumn leaves','desert sand','prismatic cavern')
   check('declared-Wisp-caster-affinity',bool(affinity(index,*apos)&8),heat)
   check('campaign-Wisp-heat',(a['wisp'],b['wisp']),(1,2 if heat else 1) if a['loss']>0 else (0,0))
  if action==380:check('campaign-no-ice-control-Slow',a['slow'],False)
  if label=='mineral cavern':check('crystal-is-not-ice-Slow',b['slow'],False)
  if label=='night desert sand':check('night-sand-is-not-ice-Slow',b['slow'],False)
  if label=='blue mineral cavern':check('blue-mineral-is-not-ice-Slow',b['slow'],False)
  if action==376:
   water=label in ('stream','wetland reeds')
   check('declared-stream-caster-affinity',bool(affinity(index,*apos)&4),water)
   for enabled,value in zip((False,True),values):
    if label=='wetland reeds':
     h=heights[index]
     check('reed-caster-has-no-native-water',any(h[2*(16*y+x)+1]&2 for x,y in ((11,1),(10,1),(12,1),(11,0),(11,2))),False)
     check('native-reed-south-push',value['position'],[10,2] if value['loss']>0 and enabled else list(tpos))
    else:check('native-stream-north-push',value['position'],[10,3] if value['loss']>0 and water else list(tpos))
  samples.append(dict(label=label,map=index,action=action,seed=seed,values=values))
for label,index,action,*rest in scenarios:
 if action!=378:check('positive-damage-'+label,any(s['label']==label and s['values'][1]['loss']>0 for s in samples),True)
check('production-ice-positive-Slow',any(s['action']==380 and s['values'][1]['slow'] for s in samples),True)
check('snow-plateau-positive-Slow',any(s['label']=='snow plateau' and s['values'][1]['slow'] for s in samples),True)
m.put(MATERIALS,production)
report=dict(passed=not failures,romSha1=meta['romSha1'],cleanRomSha1=CLEAN_SHA1,reviewedMaps=len(reviewed),annotatedCells=sum(bool(x) for x in production),checks=dict(checks),nativeExecutions=executions,samples=samples,failures=failures,scope='Native coordinate lookup and direct executor; no UI/AI/campaign-playback acceptance')
(OUT/'terrain-campaign.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('samples','failures')},indent=2))
assert not failures,failures[:20]
