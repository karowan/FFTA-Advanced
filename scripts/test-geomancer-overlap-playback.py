"""Two independently constructed Nu Mou cast overlapping fields by fixed input.

The declared clan profile precedes native battle construction. Formation is a
test input before either cast. Fields, MP payment, action results, rendering and
turn transitions are produced by the unchanged production ROM, without hooks.
"""
import collections,ctypes as C,hashlib,json,pathlib,runpy,struct
from native_battle_wrappers import from_emulator
from geomancer_render_observation import observe
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();LAB=ROM.parent
FIX=LAB/'fixture-two-geomancers';OUT=LAB/'geomancer-overlap';OUT.mkdir(exist_ok=True)
proof=json.loads((FIX/'prepare-cache.json').read_text())
assert proof['inputs']['romSha1']==meta['romSha1']==hashlib.sha1(image).hexdigest()
for name,value in proof['outputs'].items():assert hashlib.sha1((FIX/name).read_bytes()).hexdigest()==value
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
CASTERS=(0x290,0x4a0);checks=collections.Counter();rows=[];failures=[];case=None

def check(label,value):
 checks[label]+=1
 assert value,(case,label)

def actor(e):
 r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)-0x02000000

def mode(e):
 r=e.memory();return r[word(r,0xf438)-0x02000000+4]

def tap(e,key,release=180):e.run(8,key);e.run(release)

def menu(e,previous=None):
 for frames in range(0,9001,10):
  if menus['menu_visible'](e) and (previous is None or actor(e)!=previous):return
  if frames<9000:e.run(10)
 raise AssertionError(('Native menu timeout',case,hex(actor(e)),mode(e)))

def turn(e,wanted):
 menu(e)
 for _ in range(24):
  if actor(e)==wanted:return
  previous=actor(e)
  for key in (32,32,256,256):tap(e,key)
  menu(e,previous)
 raise AssertionError(('Caster did not receive a native turn',hex(wanted)))

def record(r,caster):
 offset=0x3f410+((caster-0x80)//264)*22
 return r[offset+15:offset+18]

def capture(e,folder,label):
 e.save(folder/(label+'.state'));e.screenshot(folder/(label+'.png'))
 r=e.memory();(folder/(label+'.ram')).write_bytes(r)
 check('native-render-code-intact',C.string_at(*e.maps[0x03000000])[0x6170:0x6d68]==image[0xa38d24:0xa3991c])
 return r

def cast(e,caster,kind,center,folder):
 check('correct-native-active-caster',actor(e)==caster)
 before=e.memory();action=380 if kind==1 else 382
 # No Move has been spent: Move is row0, Action row1. Fight is Action row0.
 for key in (32,256,32,256):tap(e,key)
 if kind==2:tap(e,32)
 tap(e,256)
 r=e.memory();command=word(r,0xf438)-0x02000000
 check('selected-native-field-action',word(r,command+20)==action)
 x,y=r[caster+0xf6:caster+0xf8]
 for _ in range(abs(center[0]-x)):tap(e,128 if center[0]>x else 64)
 for _ in range(abs(center[1]-y)):tap(e,32 if center[1]>y else 16)
 for _ in range(3):
  if mode(e)==11:break
  tap(e,256)
 check('native-field-confirmation',mode(e)==11)
 confirmed=capture(e,folder,'confirmation')
 check('no-premature-field',record(confirmed,caster)[2]&3==0)
 tap(e,256,1800)
 shown=observe(e);after=capture(e,folder,'after-cast')
 field=record(after,caster)
 check('native-field-created-at-selected-center',field[:2]==bytes(center) and field[2]&3==kind)
 check('MP-paid-once',half(before,caster+0x1c)-half(after,caster+0x1c)==12)
 check('cast-preserves-inventory-and-AP',before[0x1940:0x1e70]==after[0x1940:0x1e70])
 return shown

def expected_board(r,kinds,centers):
 grid=word(r,0x7f14)-0x02000000;board=bytearray(256)
 for kind,(x,y) in zip(kinds,centers):
  height=r[grid+2*(y*16+x)]
  for dx,dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1)):
   tx,ty=x+dx,y+dy
   if 0<=tx<16 and 0<=ty<16:
    h=r[grid+2*(ty*16+tx)]
    if h and abs(h-height)<=2:board[ty*16+tx]|=kind
 return bytes(board)

# One starting profile/formation; native wrappers and sprite races already exist.
e=E(ROM)
try:
 e.load(FIX/'battle-ready.state');e.run(1);menu(e);wrappers=from_emulator(image,e)
 for caster in CASTERS:
  check('independent-native-Nu-Mou-Geomancer',e.memory()[caster+6]==3 and e.memory()[caster+7]==121 and caster in wrappers)
 positions={0x80:(5,14),0x188:(4,15),0x290:(0,13),0x398:(4,14),0x4a0:(1,11),0x5a8:(1,15)}
 for unit,(x,y) in positions.items():
  r=e.memory();grid=word(r,0x7f14)-0x02000000;height=r[grid+2*(y*16+x)]
  check('valid-declared-formation-tile',height>0)
  e.set_memory(unit+0xf6,bytes((x,y)))
  e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height*16,y*32+16))
 turn(e,CASTERS[0]);capture(e,OUT,'first-caster-ready')
finally:e.close()

for first in (1,2):
 folder=OUT/f'first-{first}';folder.mkdir(exist_ok=True);e=E(ROM);case=('first-cast',first)
 try:
  e.load(OUT/'first-caster-ready.state');e.run(1)
  cast(e,CASTERS[0],first,(2,12),folder)
  # Casting before Move returns to the native menu with Move still enabled.
  # Select Wait and confirm facing; a single A would enter movement targeting.
  previous=actor(e)
  for key in (32,32,256,256):tap(e,key)
  menu(e,previous);turn(e,CASTERS[1])
  check('first-field-survives-other-turns',record(e.memory(),CASTERS[0])[2]&3==first)
  capture(e,folder,'second-caster-ready')
 finally:e.close()
 for second in (1,2):
  for center in ((2,12),(3,12)):
   case=(first,second,center);folder2=folder/f'second-{second}-{center[0]}';folder2.mkdir(exist_ok=True);e=E(ROM)
   try:
    source=folder/'second-caster-ready.state';e.load(source);e.run(1)
    old=record(e.memory(),CASTERS[0]);shown=cast(e,CASTERS[1],second,center,folder2)
    r=e.memory();check('second-caster-keeps-first-field',record(r,CASTERS[0])==old)
    owner=int(shown['owner'],16)-0x02000000;board=r[owner+348:owner+604]
    expected=expected_board(r,(first,second),((2,12),center))
    check('actual-published-board-is-independent-field-union',board==expected)
    check('mixed-overlap-visible-in-board',first==second or 3 in board)
    check('both-independent-fields-live',all(record(r,c)[2]&3==k for c,k in zip(CASTERS,(first,second))))
    rows.append(dict(first=first,second=second,center=center,sourceSha1=hashlib.sha1(source.read_bytes()).hexdigest(),
      fields=[record(r,c).hex() for c in CASTERS],display=shown,boardSha1=hashlib.sha1(board).hexdigest(),mixedCells=board.count(3)))
   except BaseException as error:
    failures.append(dict(case=case,error=repr(error)));capture(e,folder2,'failure')
   finally:e.close()
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),outcomes=rows,failures=failures,
 inputs=dict(profile=proof['inputs'],formation=positions,firstCenter=[2,12],secondCenters=[[2,12],[3,12]]),
 limits=['This proves actual two-caster field creation/publication, not every heavy action or campaign encounter.','Human review of screenshots is separate from deterministic pixel and board assertions.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
assert not failures,('Overlap playback failures',len(failures))
