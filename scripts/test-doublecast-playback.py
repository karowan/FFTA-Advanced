"""Fixed Red Magic inputs through both native casts, reactions and turn return.

Declared mastery/formation/stats are set before player inputs. The recorder
fixes RNG at executor entry and copies results; it never supplies game results.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("OUT=LAB/'reaction-playback'","OUT=LAB/'doublecast-playback'")
start=support.index("source=r'''")+len("source=r'''");end=support.index("'''",start)
support=support[:start]+r'''
#include <stdint.h>
extern unsigned playback_original(uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
static unsigned h(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
unsigned playback_call(uint8_t *out,unsigned actor,unsigned x,unsigned y,unsigned action,unsigned mode,unsigned a,unsigned b){
 volatile uint32_t *log=(volatile uint32_t *)0x0203ff50u;
 if(log[37])*(volatile uint32_t *)0x030034b0u=log[38];
 unsigned result=playback_original(out,actor,x,y,action,mode,a,b);
 unsigned n=log[1];
 if(n<2){
  volatile uint32_t *row=log+4+n*16;
  row[0]=action;row[1]=*(volatile uint8_t *)0x0200f597u;
  row[2]=out[0x26bd];row[3]=(unsigned)out;
  for(unsigned i=0;i<3;i++){
   for(unsigned j=0;j<4;j++)row[4+i*4+j]=0;
   if(i>=out[0x26bd])continue;
   const uint8_t *o=out+i*0x2c4,*target=o+0x20;
   row[4+i*4]=h(o+0x10);row[5+i*4]=**(const uint32_t *const *)o;
   if(!o[0x2c0])continue;
   row[6+i*4]=(int16_t)h(target+0x1e);row[7+i*4]=h(target+12);
  }
 }
 log[1]=n+1;log[0]=0x504c4159;return result;
}
'''+support[end:]
exec(compile(support,'<deterministic Doublecast recorder>','exec'))
ACTOR,TARGET=0x5a8,0x398
interrupt_only='--interrupt-only' in sys.argv
armns={'STACK':0x03007000,'RETURN':0x08000100,'struct':struct}
exec('from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB\nfrom unicorn.arm_const import *',armns)
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<read-only native accessors>','exec'),armns)

def owned(e):
 m=armns['ARM'](image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
 state=m.call(meta['symbols']['ffta_job_state'],0x02000000+ACTOR)
 slot=m.call(meta['symbols']['ffta_battle_workspace'],0x2610)
 return state-0x02000000,m.call(meta['symbols']['ffta_myk_sequence'],0x02000000+ACTOR),m.read(slot,16) if slot else bytes(16)

def mode(e):
 r=e.memory();return r[word(r,0xf438)-0x02000000+4]

def checkpoint(e,label,folder):
 r=capture(e,label,folder)
 check('native-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 return r

def formation(e,wrappers):
 for unit,x,y,height in ((ACTOR,0,14,16),(TARGET,1,13,32),
  (0x290,2,12,32),(0x80,4,13,32),(0x188,3,14,32),(0x4a0,1,15,16)):
  e.set_memory(unit+0xf6,bytes((x,y)))
  e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))

e=E(TEST_ROM)
try:
 e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
 check('real-Viera-caster',e.memory()[ACTOR+6]==4)
 check('real-Bangaa-recipient',e.memory()[TARGET+6]==2)
 for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((30,)))
 e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2))
 e.set_memory(ACTOR+0x40,bytes(0x90))
 # Exact original Viera racial lessons: Fire and Doublecast only. This fixes
 # the menu order without granting new actions Doublecast eligibility.
 bank=word(image,word(image,0xcd538)-0x08000000+4*4)-0x08000000
 for index,action in ((23,23),(29,33)):
  check('original-lesson-identity',half(image,bank+index*8+4)==action and image[bank+index*8+6]==1)
  e.set_memory(ACTOR+0x40+index,b'\xff')
 e.set_memory(ACTOR+0x2a,struct.pack('<5H',88,0,0,0,0))
 for unit in (ACTOR,TARGET,0x80,0x188):
  e.set_memory(unit+0x18,struct.pack('<4H',500,500,99,99))
  e.set_memory(unit+0xe8,bytes(8));e.set_memory(unit+0x20,struct.pack('<4H',70,40,40,40))
  e.set_memory(unit+0x3a,bytes(2))
 wrappers=from_emulator(image,e);formation(e,wrappers)
 for turn in range(16):
  if active(e)==0x02000000+ACTOR:break
  previous=active(e)
  for key in (32,32,256,256):tap(e,key)
  menu(e,previous)
 check('native-Viera-turn',active(e)==0x02000000+ACTOR)
 wrappers=from_emulator(image,e);formation(e,wrappers)
 for unit in (ACTOR,TARGET,0x80,0x188):
  e.set_memory(unit+0x18,struct.pack('<4H',500,500,99,99));e.set_memory(unit+0xe8,bytes(8))
 e.set_memory(TARGET+0x29,b'\x80')
 e.set_memory(TARGET+0x2a,bytes(10))
 e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
 checkpoint(e,'start',OUT)
 # Move to0,13; Act -> Red Magic -> Doublecast. Select the only eligible
 # learned spell (Fire), then the adjacent target at1,13 for each cast.
 for key in (256,16,256,256,32,256,32,256):tap(e,key)
 r=checkpoint(e,'doublecast-first-choice',OUT)
finally:e.close()

for placement in (('self-first',) if interrupt_only else ('same','first-only','self-first')):
 e=E(TEST_ROM)
 try:
  e.load(OUT/'doublecast-first-choice.state')
  keys=((256,256,256,256,128,256,256) if placement=='self-first' else
   (256,128,256,256,256)+((128,) if placement=='same' else (128,128,128))+(256,256))
  for key in keys:tap(e,key)
  before=checkpoint(e,'confirmation-'+placement,OUT)
  check('native-final-confirmation',mode(e)==11)
  check('no-premature-execution',word(before,LOG+4)==0)
 finally:e.close()

# Existing no-support controls are retained once. New runs vary the actual
# second target and Spellweave fixture, not an exhaustive repeated matrix.
scenarios=[('same',False,False),('same',True,False),('same',True,True),('first-only',True,True)]
for placement,enabled,weave in ([] if interrupt_only else scenarios):
 for seed in (0,3,18):
  case=('Absorb-Damage-Doublecast',placement,enabled,weave,seed);folder=OUT/placement/str(enabled)/str(weave)/str(seed);folder.mkdir(parents=True,exist_ok=True)
  e=E(TEST_ROM)
  try:
   e.load(OUT/('confirmation-'+placement+'.state'));equip(e,TARGET,'VIK-R1',2,enabled)
   if weave:
    lesson=next(l for l in registry['lessons'] if l['id']=='MYK-S1')
    index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==4)
    e.set_memory(ACTOR+0x3b,bytes((index,)));e.set_memory(ACTOR+0x40+index,b'\xff')
    state,_,_=owned(e);check('canonical-owned-state',0x3f410<=state<0x3f780)
    e.set_memory(state+20,struct.pack('<H',1<<13))
   e.set_memory(LOG+148,struct.pack('<II',1,seed));before=e.memory()
   tap(e,256,1);rendered=set();seen={}
   for frames in range(2401):
    r=e.memory();n=word(r,LOG+4)
    if n and n not in seen:
     seen[n]=checkpoint(e,'cast-'+str(n),folder)
     _,sequence,continuation=owned(e)
     check('continuation-survives-native-ticks',continuation!=bytes(16))
     if weave:check('sequence-frozen-through-both-constructors',sequence==1)
    rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
    if frames%240==0:e.screenshot(folder/f'frame-{frames:04}.png')
    if n==2 and frames>300 and half(r,0xf4e8+0xdc)==47:break
    if frames<2400:e.run(1)
   after=checkpoint(e,'after-playback',folder)
   _,sequence,continuation=owned(e)
   check('continuation-retired-at-native-completion',continuation==bytes(16))
   if weave:check('one-final-Magic-sequence',sequence==2)
   check('two-native-executors',word(after,LOG+4)==2 and set(seen)=={1,2})
   rows=[list(struct.unpack_from('<16I',after,LOG+16+i*64)) for i in range(2)]
   check('native-Fire-pair',all(row[0]==23 and row[1]==i and row[4]==23 and row[5]==0x02000000+ACTOR for i,row in enumerate(rows)))
   check('bounded-result-counts',all(1<=row[2]<=3 for row in rows))
   check('no-reaction-between-casts',rows[0][2]==1)
   reactions=[row[4+j*4] for row in rows for j in range(1,row[2])]
   check('only-one-final-Absorb',reactions in ([],[436]) and (enabled or not reactions))
   damage=500-half(seen[1],TARGET+0x18)
   if placement=='same':damage+=max(0,rows[1][6] if rows[1][6]<0x80000000 else 0)
   recovery=min(damage*30//100,75) if enabled else 0
   check('native-cumulative-recovery-amount',half(seen[2],TARGET+0x18)==500-damage+recovery)
   check('two-native-MP-payments',half(before,ACTOR+0x1c)-half(seen[2],ACTOR+0x1c)==12)
   check('rendering-no-repeated-cost',half(after,ACTOR+0x1c)==half(seen[2],ACTOR+0x1c))
   check('rendering-no-reapplied-HP',all(after[u+0x18:u+0x20]==seen[2][u+0x18:u+0x20] for u in (ACTOR,TARGET)))
   check('inventory-AP-unchanged',after[0x1940:0x1e70]==before[0x1940:0x1e70])
   check('real-rendering',len(rendered)>3)
   previous=active(e);tap(e,256,900);menu(e,previous);checkpoint(e,'next-turn',folder)
   outcomes.append(dict(placement=placement,enabled=enabled,weave=weave,seed=seed,results=rows,reactions=reactions,frames=frames,uniqueFrames=len(rendered)))
  finally:e.close()
if not interrupt_only:check('nonvacuous-queued-Absorb',any(x['enabled'] and x['reactions']==[436] for x in outcomes))
interruptions=[]
for enabled in (False,True):
 for seed in (3,18):
  case=('native-caster-KO',enabled,seed);folder=OUT/'interrupt'/str(enabled)/str(seed);folder.mkdir(parents=True,exist_ok=True)
  e=E(TEST_ROM)
  try:
   e.load(OUT/'confirmation-self-first.state');equip(e,TARGET,'VIK-R1',2,enabled)
   e.set_memory(ACTOR+0x18,struct.pack('<H',1))
   e.set_memory(LOG+148,struct.pack('<II',1,seed));before=e.memory()
   tap(e,256,1);executed=None;rendered=set()
   for frames in range(3601):
    r=e.memory();n=word(r,LOG+4)
    if n and executed is None:executed=checkpoint(e,'native-result',folder)
    rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
    if frames%240==0:e.screenshot(folder/f'frame-{frames:04}.png')
    if n and active(e)!=0x02000000+ACTOR and observe['menu_visible'](e):break
    if frames<3600:e.run(1)
   after=checkpoint(e,'next-turn',folder)
   check('KO-reaches-next-player-menu',active(e)!=0x02000000+ACTOR and observe['menu_visible'](e))
   check('native-first-spell-KOs-caster',executed is not None and half(executed,ACTOR+0x18)==0)
   check('KO-cancels-second-executor',word(after,LOG+4)==1)
   check('cancelled-second-spell-costs-no-MP',half(before,ACTOR+0x1c)-half(executed,ACTOR+0x1c)==6)
   _,_,continuation=owned(e);check('KO-retires-continuation',continuation==bytes(16))
   out=word(executed,LOG+28)-0x02000000;damage=None
   for i in range(executed[out+0x2c0]):
    row=out+0x20+i*44;wrapper=word(executed,row)-0x02000000
    if word(executed,wrapper)==0x02000000+TARGET:damage=struct.unpack_from('<h',executed,row+0x1e)[0]
   check('KO-first-cast-has-positive-defender-damage',damage is not None and damage>0)
   count=word(executed,LOG+24);actions=[half(executed,out+i*0x2c4+0x10) for i in range(count)]
   check('partial-action-one-recovery',actions==([23,436] if enabled else [23]))
   check('partial-action-recovery-amount',half(executed,TARGET+0x18)==500-damage+(min(damage*30//100,75) if enabled else 0))
   check('partial-action-no-repeat-on-render',after[TARGET+0x18:TARGET+0x20]==executed[TARGET+0x18:TARGET+0x20])
   check('partial-action-real-rendering',len(rendered)>3)
   check('partial-action-inventory-AP-unchanged',after[0x1940:0x1e70]==before[0x1940:0x1e70])
   interruptions.append(dict(enabled=enabled,seed=seed,damage=damage,actions=actions,frames=frames,uniqueFrames=len(rendered)))
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 interruptions=interruptions,
 limits=['Fixed Red Magic/Absorb scenario; no campaign, AI or combined Shell-menu prediction acceptance.','Changing frames does not certify every animation frame or banner text.'])
(OUT/('interrupt-report.json' if interrupt_only else 'report.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
