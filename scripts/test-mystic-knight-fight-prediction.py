"""Fight status law forecasts against fixed native executions and ownership.

No injected outcomes. A forecast is a possible ordinary successful application,
not a promise that a particular random hit succeeds. Committed masks are read
from the native primary component before later weapons/reactions can clear it.
"""
import pathlib,json,struct,itertools,collections,argparse
parser=argparse.ArgumentParser();parser.add_argument('--follow-up',action='store_true');parser.add_argument('--weapon-follow-up',action='store_true');options=parser.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-fight-status.py'
ns={'__file__':str(source),'__name__':'fight_prediction_fixture'}
exec(compile(source.read_text().split('samples = []')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,fixture,call,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','STACK','fixture','call','record'))
base=ns['ns'];checks=collections.Counter();samples=[];failures=[];case=None
from unicorn import UC_HOOK_MEM_INVALID,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
def invalid(u,access,address,size,value,data):
 detail=dict(case=case,access=access,address=hex(address),size=size,value=value,
  regs=[hex(u.reg_read(r)) for r in (UC_ARM_REG_PC,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)])
 print(json.dumps(detail));(OUT/'fight-prediction-fault.json').write_text(json.dumps(detail,indent=2));return False
m.u.hook_add(UC_HOOK_MEM_INVALID,invalid)
rolls=[]
def observe_roll(u,pc,size,data):
 rolls.append(dict(chance=u.reg_read(UC_ARM_REG_R0),caller=hex(u.reg_read(UC_ARM_REG_LR)),targetHP=base['half'](T+0x18)))
m.u.hook_add(UC_HOOK_CODE,observe_roll,begin=0x0812f1dc,end=0x0812f1dc)
LAW=0x0203e000
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,case=case,actual=repr(a),expected=repr(b)))
def protected():
 return m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)+m.read(0x030034b0,4)+m.read(0x0200f3f0,0x34)+m.read(0x03005e80,64)
def setup(kind,condition,pair,seed):
 ns['restore_items'](m);fixture(0,seed);base['job'](A,1,7)
 m.put(A+0x2a,struct.pack('<5H',*pair,0,0,0))
 if condition=='asleep':base['grant'](T,26)
 if condition=='astra':base['grant'](T,4)
 if condition=='inoculated':call('ffta_inoculated_grant',T,0)
 if condition=='warcry':call('ffta_viking_grant_war_cry',T,0)
 if condition=='immune':
  base['job'](T,1,2);ns['native_lesson'](T,11,3)
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='lethal':base['hp'](T,1,500,99)
 if condition=='zero':base['grant'](T,33)
 if condition=='damage-mp':
  base['job'](T,1,2);ns['native_lesson'](T,13,2);m.put(T+0x1c,struct.pack('<HH',999,999))
 if condition=='restorative':m.put(ns['item_table']+pair[0]*32+26,b'\x3f\0\0')
 if condition=='offhand-healing':
  m.put(ns['item_table']+pair[1]*32+26,b'\x3f\0\0');base['hp'](T,1,500,99)
 if condition in ('offhand-drain','offhand-removal'):
  m.put(ns['item_table']+pair[1]*32+26,bytes((0x3d if condition=='offhand-drain' else 0x3e,0,0)))
  base['grant'](T,20)
 if condition in ('offhand-miss','offhand-surehit'):
  # Data-only strong secondary weapon. Its hit defeats the recipient, but a
  # miss leaves a nonlethal primary application. No rolls are overridden.
  m.put(ns['item_table']+pair[1]*32+10,b'\x57');base['hp'](T,60,500,99)
  if condition=='offhand-surehit':base['grant'](T,26)
 if condition=='silenced':base['grant'](A,27)
 if condition=='parry':
  base['equip'](T,'MYK-R2');call('ffta_myk_grant',T,1)
 call('ffta_myk_grant',A,kind)

conditions=('normal','asleep','astra','inoculated','warcry','immune','ally',
 'lethal','zero','damage-mp','restorative','silenced','parry')
cases=list(itertools.product((4,5,6,9),conditions,((88,0),(88,89),(89,88),(88,88))))
cases += [(k,'offhand-healing',(88,89)) for k in (4,5,6,9)]
cases += [(k,c,(88,89)) for k,c in itertools.product((4,5,6,9),('offhand-drain','offhand-removal','offhand-miss','offhand-surehit'))]
if options.follow_up:cases=[c for c in cases if c[1] in ('immune','inoculated','offhand-healing') or c[2]==(88,88)]
if options.weapon_follow_up:cases=[c for c in cases if c[1].startswith('offhand-')]
for kind,condition,pair in cases:
 case=(kind,condition,pair);setup(kind,condition,pair,0)
 bit={4:9,5:26,6:27,9:22}[kind];predicted=None
 for residue in (0,4):
  for typ,value in ((15,bit),(16,0),(15,25)):
   m.put(LAW,bytes(4)+bytes((typ,value))+bytes(10))
   m.put(STACK+residue,struct.pack('<4I',0,0,0,LAW));before=protected()
   result=m.call(0x081343c8,A,T,0,0,stack=STACK+residue)
   check('forecast-preserves-live-state-context-RNG',protected(),before)
   check('forecast-retires-scope',m.read(0x0203f730,4),bytes(4))
   check('forecast-retires-snapshot',m.read(0x0203ff44,8),bytes(8))
   if predicted is None:predicted=result
   check('specific-and-harmful-agree',result,predicted if typ==16 or value==bit else 0)
 if condition in ('normal','asleep','ally','silenced','parry','offhand-healing'):
  check('ordinary-damaging-Fight-can-apply',predicted,1)
 if condition in ('lethal','zero','damage-mp','restorative','astra') or (condition in ('immune','inoculated') and kind!=9):
  check('blocked-or-no-HP-damage-cannot-apply',predicted,0)
 if condition in ('immune','inoculated') and kind==9:check('Slow-outside-Cureall-Immunity-whitelist',predicted,1)
 outcomes=[];details=[]
 for seed in (0,1,2,3,4,5,6,7):
  setup(kind,condition,pair,seed);ns['captured'].clear();ns['writes'].clear();rolls.clear();ns['execute'](0)
  container=ns['regs'][0];receipt=call('ffta_battle_workspace',0x2620)
  applied=False
  for i,k in enumerate(m.read(receipt+16,14)):
   if k!=kind:continue
   obj=container+i*0x2c4
   for j in range(m.read(obj+0x2c0,1)[0]):
    row=obj+0x20+j*0x2c;w=m.word(row)
    if w and m.word(w)==T:
     applied|=bool(m.read(row+0x14+bit//8,1)[0]&(1<<(bit%8)))
  check('native-application-never-hidden-by-forecast',not applied or bool(predicted),True)
  outcomes.append(applied)
  details.append(dict(seed=seed,rolls=list(rolls),writes=list(ns['writes']),finalHP=base['half'](T+0x18)))
 samples.append(dict(kind=kind,condition=condition,pair=pair,predicted=predicted,nativeApplied=outcomes,details=details))
for kind in (4,5,6,9):
 check('nonvacuous-native-positive-'+str(kind),any(s['kind']==kind and any(s['nativeApplied']) for s in samples),True)
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,failures=failures,
 limits=['Forecast assumes ordinary successful components as native laws do; random hit/critical outcomes are not promises.',
 'AI scoring and resource predictions remain separate integration.'])
(OUT/('mystic-knight-fight-prediction'+('-weapon-follow-up' if options.weapon_follow_up else '-follow-up' if options.follow_up else '')+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures, str(len(failures))+' prediction failures'
