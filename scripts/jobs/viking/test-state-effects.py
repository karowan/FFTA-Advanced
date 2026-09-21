"""Native War Cry and Challenged application, cures, accuracy and owned timers.

This does not accept Provoke's outgoing penalty or shared reaction consumers.
"""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();S=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];fix=ROM.parent/'executor'
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,ALLY,TARGET,EQUIPMENT,RETURN,STACK=0x02000080,0x02000398,0x020033e4,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);m.u.mem_map(0x06000000,0x20000);checks=collections.Counter();samples=[]
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
def check(name,got,want):
 checks[name]+=1;assert got==want,(name,got,want,globals().get('case'))
def state(unit):return m.call(S['ffta_job_state'],unit)
def half(unit,offset):return struct.unpack('<H',m.read(unit+offset,2))[0]
def setup():
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.call(S['ffta_job_reset']);m.put(0x0203ff44,bytes(8))
 for unit in wrappers:
  if unit not in (UNIT,ALLY,TARGET):
   m.put(unit+0xf6,bytes([0,0]));m.put(wrappers[unit]+8,bytes(2));m.put(wrappers[unit]+12,bytes(2))
 for unit,xy in [(UNIT,(4,14)),(ALLY,(4,13)),(TARGET,(5,14))]:
  m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2));m.put(unit+0x18,struct.pack('<4H',100,100,50,50))
  m.put(unit+0xf6,bytes(xy));m.put(wrappers[unit]+8,struct.pack('<H',xy[0]<<5));m.put(wrappers[unit]+12,struct.pack('<H',xy[1]<<5))
 m.put(UNIT+5,bytes([118,2,118]));m.put(UNIT+0x35,b'\x76')
def execute(action,x,y,seed=0):
 m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
 m.call(0x080a433c,regs[0],wrappers[UNIT],x,y,stack=regs[13])

for ailments in (False,True):
 case=('War Cry',ailments);setup()
 if ailments:
  for unit in (UNIT,ALLY,TARGET):
   for status in (9,10,27):m.put(unit+0xe8+status//8,bytes([m.read(unit+0xe8+status//8,1)[0]|(1<<(status%8))]))
  m.put(ALLY+0xeb,b'\x18')
 before=m.read(TARGET,264)
 execute(368,4,14)
 sample=dict(ailments=ailments,actor=list(m.read(state(UNIT)+4,4)),ally=list(m.read(state(ALLY)+4,4)),enemy=list(m.read(state(TARGET)+4,4)),mp=half(UNIT,0x1c),heights=[m.call(0x0801cc18,x,y) for x,y in [(4,14),(4,13),(5,14)]]);samples.append(sample)
 (ROM.parent/'state-effects-observed.json').write_text(json.dumps(samples,indent=2))
 check('native-war-cry-cost-once',half(UNIT,0x1c),42)
 check('native-war-cry-self-timer',m.read(state(UNIT)+4,1),b'\x06')
 check('native-war-cry-ally-timer',m.read(state(ALLY)+4,1),b'\x02')
 check('native-war-cry-enemy-untouched',m.read(TARGET,264),before)
 for unit in (UNIT,ALLY):
  for status in (10,27,28):check('native-war-cry-specific-cures',bool(m.read(unit+0xe8+status//8,1)[0]&(1<<(status%8))),False)
  if ailments:check('native-war-cry-preserves-poison',bool(m.read(unit+0xe9,1)[0]&2),True)
 for expected in (2,1,0):
  m.call(S['ffta_viking_lifecycle_turn_end'],UNIT);check('T2-excludes-application-turn',m.read(state(UNIT)+4,1),bytes([expected]))

landed=0
for immune,seed in itertools.product((False,True),range(64)):
 case=('Provoke',immune,seed);setup()
 if immune:
  # Locate native Immunity through immutable racial lesson bytes.
  m.put(TARGET+5,bytes([2,1,2]))
  race=m.read(TARGET+6,1)[0]
  indices=[i for i in range(142) if (p:=m.call(0x080cd480,race,i)) and m.read(p+4,3)==bytes([11,0,3])]
  assert indices;index=indices[0];m.put(TARGET+0x3b,bytes([index]));m.put(TARGET+0x40+index,b'\xff')
  check('native-immunity-assigned',m.call(0x080cd50c,TARGET),11)
 execute(373,5,14,seed);token=m.read(state(TARGET)+5,1)[0]
 check('native-provoke-cost-once',half(UNIT,0x1c),44)
 check('native-provoke-no-damage',half(TARGET,0x18),100)
 if immune:check('native-provoke-immunity',token,0)
 elif token:
  landed+=1;check('native-provoke-explicit-origin',token,m.call(S['ffta_job_origin'],UNIT))
  m.call(S['ffta_viking_lifecycle_turn_end'],TARGET);check('challenge-next-end-turn',m.read(state(TARGET)+5,1),b'\0')
check('nonvacuous-native-challenge',landed>0,True)

for recipient,event in itertools.product((UNIT,TARGET),(2,3,4,5,6,7,8)):
 case=('Lifecycle',recipient,event);setup()
 m.call(S['ffta_viking_grant_war_cry'],recipient,0)
 m.call(S['ffta_viking_grant_challenge'],TARGET,UNIT)
 m.put(state(recipient)+6,b'\x23')
 m.call(S['ffta_viking_lifecycle_event'],recipient,event)
 check('beneficial-expiry-policy',m.read(state(recipient)+4,1),bytes([0 if event in (2,3,4,5,7) else 2]))
 check('harmful-relationship-expiry-policy',m.read(state(TARGET)+5,1),bytes([0 if event in (2,3,4,5) or (recipient==TARGET and event==6) else 1]))
 check('gil-cap-survives-job-change-and-KO',m.read(state(recipient)+6,1),bytes([0 if event==4 else 35]))
setup();m.call(S['ffta_viking_grant_war_cry'],UNIT,0);m.call(S['ffta_viking_grant_challenge'],TARGET,UNIT)
m.call(0x080cd884,UNIT,6,1)
check('native-Petrify-clears-WarCry',m.read(state(UNIT)+4,1),b'\0')
check('native-Petrify-clears-incoming-challenges',m.read(state(TARGET)+5,1),b'\0')

ctx=0x0200f3f0
for descriptor,side,ward,status,residue in itertools.product((104,78),(0,1),(0,2),(-1,0,4,6,9,22,23,25,26),(0,4)):
 case=('S chance',descriptor,side,ward,status,residue);setup()
 m.put(UNIT+0x29,bytes([side<<7]));m.put(TARGET+0x29,b'\0');m.put(state(TARGET)+4,bytes([ward]))
 if status>=0:m.put(TARGET+0xe8+status//8,bytes([1<<(status%8)]))
 m.call(0x0812f230,ctx,35,0,0);m.put(ctx,struct.pack('<III',UNIT,TARGET,TARGET));m.put(ctx+0x30,struct.pack('<I',0x09260000+descriptor*4))
 original=m.call(S['ffta_original_viking_status_accuracy'],ctx,stack=STACK+residue)
 result=m.call(0x08131220,ctx,stack=STACK+residue)
 check('hostile-final-S-minus25',result,max(0,original-25) if side and ward and descriptor==104 and status!=4 else original)

# Both added status keys enumerate through the installed native icon boundary;
# visual functions may write only their root-reserved two tiles.
for war,challenge in itertools.product((0,2),(0,1)):
 setup();m.put(state(UNIT)+4,bytes([war,challenge]))
 for key,want in [(31,31 if war else 0),(32,32 if challenge else 0)]:
  for residue in (0,4):check('native-visible-key',m.call(0x0809da0c,UNIT,key,stack=STACK+residue),want)
 for previous in range(256):
  if war or challenge:
   limit=32 if challenge else 31;next=(previous+1)&255;signed=next if next<128 else next-256
   check('status-enumeration',m.call(S['ffta_viking_status_next_key'],UNIT,previous),1 if signed>limit else next)
setup()
for key,tile in [(31,0x1ec),(32,0x1ee)]:
 sprite=0x02007000;m.put(sprite,bytes(0x40));m.put(0x06013c00,b'\xa7'*0x280)
 check('visual-tile',m.call(S['ffta_viking_status_visual'],sprite,key),tile)
 visual=m.read(0x06013c00,0x280);start=tile*32-0x3c00
 check('prior-tile-guard',visual[:start],b'\xa7'*start)
 check('later-tile-guard',visual[start+64:],b'\xa7'*(len(visual)-start-64))
 check('visible-glyph-nonempty',len(set(visual[start:start+64]))>2,True)
 shape=struct.unpack('<I',m.read(sprite+0x28,4))[0]
 check('native-eight-by-sixteen-shape',m.read(shape,8),struct.pack('<4H',1,0x80f8,0x01fc,0))

report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),samples=samples,scope=__doc__)
(ROM.parent/'state-effects.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
