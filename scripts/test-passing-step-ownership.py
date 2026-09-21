"""Native callbacks on captured player state: ownership, payment and cleanup.

Boundary inputs deliberately vary origin, actor, phase and payment events.
They do not replace the separate actual player transaction/movement test.
"""
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
STACK,RETURN=0x03007000,0x08000100
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text());image=pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(image).hexdigest()==meta['romSha1']
OUT=pathlib.Path(meta['path']).parent/'passing-step-playback';proof=json.loads((OUT/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==meta['romSha1']
ram=(OUT/'route-0/final-confirmation.ram').read_bytes();iw=(OUT/'route-0/final-confirmation.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ownership callbacks>','exec'))
m=ARM(image,iw);S=meta['symbols'];STACK=0x03007000;STATE=0x0203f000;FRAME=0x03007500
actor=struct.unpack_from('<I',ram,0x3f010)[0];other=0x02000080;copied=0x02028000
assert actor==0x020005a8 and struct.unpack_from('<2I',ram,0x3f000)==(0x50535450,3)
checks=collections.Counter();case=None
def check(k,v):checks[k]+=1;assert v,(k,case)
def call(name,*args):return m.call(S[name],*args,stack=STACK)
def reset():
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 m.put(copied,m.read(actor,264));m.put(STATE-4,b'\xd7'*4);m.put(STATE+512,b'\xd7'*4)
def guards():check('reservation-neighbors',m.read(STATE-4,4)==b'\xd7'*4 and m.read(STATE+512,4)==b'\xd7'*4)

for unit in (copied,other,actor):
 for event in range(1,9):
  case=('lifecycle',hex(unit),event);reset();before=m.read(STATE,512)
  call('ffta_passing_lifecycle',unit,event)
  clears=unit!=copied and (event in (1,4) or unit==actor and event in (2,3,5))
  check('exact-lifecycle-owner',m.read(STATE,8)==bytes(8) if clears else m.read(STATE,512)==before)
  guards()
for unit in (copied,other,actor):
 case=('turn end',hex(unit));reset();before=m.read(STATE,512);call('ffta_passing_turn_end',unit)
 check('turn-end-exact-owner',m.read(STATE,8)==bytes(8) if unit==actor else m.read(STATE,512)==before);guards()

# Completion claims need the installed shared snapshot callbacks, a native
# primary origin, the exact live actor, the selected action and a paid event.
for unit in (actor,copied):
 for origin in (0,1,2,3):
  for action in (0,401,409):
   for paid in (False,True):
    case=('completion',hex(unit),origin,action,paid);reset();m.put(STATE+4,struct.pack('<I',4))
    # Snapshot helpers own the adjacent extra bank in this part of the test.
    m.put(STATE+512,bytes(2080))
    call('ffta_snapshot_begin',FRAME,unit,other,1)
    call('ffta_action_started',unit,action,origin,1)
    if paid:call('ffta_action_paid',unit,action)
    call('ffta_action_completed',unit)
    completed,started=struct.unpack('<2I',m.read(STATE+44,8))
    admitted=unit==actor and origin==1 and action==409
    check('started-exact-primary-action',started==int(admitted))
    check('completed-requires-payment',completed==int(admitted and paid))
    call('ffta_snapshot_end',FRAME)
    check('snapshot-retired',m.read(FRAME,820)==bytes(820))
    check('route-data-preserved-by-callbacks',m.read(STATE+52,292)==ram[0x3f034:0x3f158])
    check('heap-boundary-preserved',m.read(STATE-4,4)==b'\xd7'*4)

case='retired route';reset();m.put(STATE+4,struct.pack('<I',7));before=m.read(0x02000000,0x40000)
check('retired-route-cannot-move',call('ffta_passing_after_action')==0)
check('retired-route-is-inert',m.read(0x02000000,0x40000)==before)
case='AI map is not a completed action';reset();m.put(STATE+4,struct.pack('<I',8));before=m.read(0x02000000,0x40000)
check('AI-map-cannot-enter-post-action-movement',call('ffta_passing_after_action')==0)
check('AI-map-post-action-is-inert',m.read(0x02000000,0x40000)==before)
# Native command2 is Move;1 advances without doing anything. The completing
# AI route must skip only future Move commands, preserving Act/Wait and the
# already consumed prefix. Player-owned routes must not touch this manager.
AI=0x020101f8;BATTLE=0x0200f4e8
for bit in (0,6,30,32):
 case=('selected AI409 cannot move',bit);reset()
 m.put(actor+0xe8,struct.pack('<Q',1<<bit))
 m.put(AI+0x54be,struct.pack('<H',409));m.put(AI+0x5290,m.read(BATTLE+4,4))
 m.put(AI+0x5298,struct.pack('<H',409));m.put(AI+0x5441,b'\x01')
 before=m.read(0x02000000,0x40000)
 check('immobile-selected-AI409-does-not-delay-strike',call('ffta_passing_ai_prepare')==0)
 check('immobile-selected-AI409-does-not-create-route',m.read(0x02000000,0x40000)==before)
for commands in ((3,2,0),(2,3,0),(3,2,2,0),(2,3,2,0)):
 for current in range(len(commands)):
  for player in (False,True):
   case=('AI command closure',commands,current,player);reset()
   m.put(STATE+4,struct.pack('<I',6))
   if not player:m.put(STATE+8,bytes(4))
   m.put(AI+0x54e4,bytes(commands)+bytes(4-len(commands))+bytes((len(commands),)))
   m.put(BATTLE+0x1ac,bytes((current,)));before=m.read(AI,0x54e9)
   check('completed-native-movement-returns',call('ffta_passing_after_action')==0)
   expected=bytearray(before)
   if not player:
    for i,c in enumerate(commands):
     if i>current and c==2:expected[0x54e4+i]=1
   check('AI-command-manager-only-future-Move-changes',m.read(AI,0x54e9)==bytes(expected))
   check('completed-owner-retires',m.word(STATE+4)==7);guards()
case='independent Passing Step coefficient';reset()
for unit in (actor,other):
 m.put(unit+0x3a,bytes(2));m.put(unit+0xe8,bytes(8))
 p=call('ffta_job_state',unit)
 if p:m.put(p,bytes(22))
for raw in (0,1,3,17,99,511,997,1500):
 check('exact-95-percent-reference',call('ffta_integrated_physical_final',raw,409,actor,other)==raw*95//100)
hp_results=[]
for seed in (0,3,18):
 r=(OUT/('route-'+str(seed))/'after-playback.ram').read_bytes()
 hp_results.append(struct.unpack_from('<H',r,0x33e4+24)[0])
 check('hit-and-miss-step-endpoint',r[0x5a8+0xf6:0x5a8+0xf8]==bytes((0,11)))
check('native-hit-and-miss-both-covered',500 in hp_results and any(hp<500 for hp in hp_results))
report=dict(passed=True,romSha1=meta['romSha1'],fixtureSha1=hashlib.sha1(ram).hexdigest(),checks=dict(checks),total=sum(checks.values()))
(OUT/'ownership.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
