"""Native two-transaction reaction aggregation with original damage controls."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-doublecast.py'
ns={'__file__':str(source),'__name__':'doublecast_reactions_fixture'}
exec(compile(source.read_text().split('# Compare every register')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,B,call,half,setup,cast,finish,dispose,h=(ns[x] for x in
 ('m','S','meta','OUT','A','T','STACK','B','call','half','setup','cast','finish','dispose','h'))
# The source fixture casts from a party unit onto a canonical enemy. Reverse
# those exact owners here so inventory reactions belong to a real party unit.
A,T=T,A;ns['A']=A;ns['T']=T
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0
checks=collections.Counter();failures=[];samples=[];objects=[];case=None

def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(case=case,check=k,actual=repr(a),expected=repr(b)))

def observe(u,pc,size,data):
 p=u.reg_read(UC_ARM_REG_R0)
 objects.append((m.read(B+0xaf,1)[0],half(p+0x10),m.word(m.word(p))))
p=S['ffta_snapshot_result'];m.u.hook_add(UC_HOOK_CODE,observe,begin=p,end=p)

jobs={'VIK-R1':(2,118),'DRK-R1':(1,117),'DRK-R2':(1,117),
 'CHM-R1':(3,120),'CHM-R2':(3,120),'BRD-R1':(5,123),'DNC-R1':(4,124),'GEO-R2':(3,121)}
hidden={'VIK-R1':436,'DRK-R1':433,'DRK-R2':434,'CHM-R1':251,'BRD-R1':439,'DNC-R1':441,'GEO-R2':444}

def configure(reaction,enabled,seed,center=5,mp=99,hp=500,barrier=False,poise=False):
 setup(previous=-1,seed=seed)
 for unit,x in ((A,4),(T,5)):
  m.put(unit+0xf6,bytes((x,14)))
  m.put(ns['wrappers'][unit]+8,struct.pack('<3H',x*32+16,32,14*32+16))
 race,job=jobs.get(reaction,(1,117));ns['ns']['job'](T,race,job)
 m.put(A+0x29,b'\x80');m.put(T+0x29,b'\0')
 h(A+0x1c,mp);h(T+0x18,hp);m.put(B+0xcc,bytes((center,)))
 if reaction=='CHM-R1':check('Potion-recipient-has-party-origin',1<=call('ffta_job_origin',T)<=24,True)
 if enabled:ns['ns']['equip'](T,reaction)
 if barrier:check('owned-barrier-granted',call('ffta_drk_grant_tbn',T,T),1)
 if poise:ns['ns']['equip'](T,'SAM-S2')
 m.put(0x02001940+362,bytes((5,5)))
 preference=call('ffta_job_potion',T)
 if preference:m.put(preference,b'\0')
 objects.clear()

def run(residue,second=True):
 outputs=[cast(0,residue)]
 first=dict(hp=half(T+0x18),actorHP=half(A+0x18),objects=list(objects),
            barrier=call('ffta_drk_tbn',T),stock=m.read(0x02001940+362,1)[0])
 if second:outputs.append(cast(1,residue))
 finish(residue)
 result=dict(first=first,hp=half(T+0x18),actorHP=half(A+0x18),objects=list(objects),
  status=m.read(T+0xe8,8).hex(),barrier=call('ffta_drk_tbn',T),
  stock=m.read(0x02001940+362,1)[0],rng=m.read(0x030034b0,4).hex())
 dispose(outputs)
 check('native-snapshot-retired',m.read(0x0203ff44,8),bytes(8))
 check('continuation-retired',m.read(call('ffta_battle_workspace',0x2610),16),bytes(16))
 return result

# Same recipient and a second spell whose area misses the first recipient.
# Every check compares full native execution; no injury/hit result is injected.
for reaction,center,seed,residue in itertools.product(hidden,(5,7),range(4),(0,4)):
 case=(reaction,center,seed,residue);hp=260 if reaction=='CHM-R1' else 500
 configure(reaction,False,seed,center,hp=hp);base=run(residue)
 configure(reaction,True,seed,center,hp=hp);actual=run(residue)
 loss=hp-base['hp'];eligible=loss>0 and base['hp']>0
 if reaction=='CHM-R1':eligible=eligible and base['hp']<=250
 ids=[x for x in actual['objects'] if x[1]==hidden[reaction]]
 check('nothing-queued-before-second-spell',[x for x in actual['first']['objects'] if x[1] in hidden.values()],[])
 expected_first=hp-(hp-base['first']['hp'])*3//4 if reaction=='DRK-R1' else base['first']['hp']
 check('first-spell-no-recovery-or-retaliation',actual['first']['hp'],expected_first)
 check('one-after-pair-native-object',len(ids),int(eligible))
 if ids:check('reaction-belongs-to-second-result',ids[0][0],1)
 if reaction=='VIK-R1':check('aggregate-actual-loss-and-cap',actual['hp'],min(500,base['hp']+min(loss*3//10,75)) if eligible else base['hp'])
 if reaction=='DRK-R1':
  first_loss=hp-base['first']['hp'];second_loss=base['first']['hp']-base['hp']
  check('Dark-Ward-no-premature-Shell-bonus',actual['hp'],hp-first_loss*3//4-second_loss*3//4)
  check('Dark-Ward-Shell-after-pair',bool(int.from_bytes(bytes.fromhex(actual['status']),'little')&(1<<24)),eligible)
 if reaction=='CHM-R1':
  check('one-Potion-after-total-damage',actual['hp'],min(500,base['hp']+25) if eligible else base['hp'])
  check('exact-one-Potion-debit',actual['stock'],5-int(eligible))
  check('no-first-cast-stock-debit',actual['first']['stock'],5)
 if reaction=='BRD-R1':check('one-Magick-Boost-charge',bool(call('ffta_bard_passive_flags',T)&32),eligible)
 if reaction=='DNC-R1':check('one-Fury-charge',bool(call('ffta_dancer_flags',T)&4096),eligible)
 if reaction=='DRK-R2' and eligible:
  affinity=m.call(0x080c7ea4,A,0x12,stack=STACK);item=m.call(0x0812fa90,A,8,0,stack=STACK)
  if item:affinity=m.call(0x0812fc74,item,stack=STACK)
  n=min(loss//2,125);n={0:n*3//2,1:n,2:0,3:-n,4:n//2}[affinity]
  check('Vengeance-total-loss-oracle',base['actorHP']-actual['actorHP'],n)
 samples.append(dict(case=case,base=base,actual=actual))

# Whole-action TBN and Poise remain frozen when the ward is consumed. Both
# damage components use the native unprotected control and final rounding.
for poise,seed,residue in itertools.product((False,True),range(4),(0,4)):
 case=('whole-pair-TBN',poise,seed,residue)
 configure('DRK-R1',False,seed,barrier=False,poise=False);base=run(residue)
 configure('DRK-R1',False,seed,barrier=True,poise=poise);actual=run(residue)
 losses=(500-base['first']['hp'],base['first']['hp']-base['hp'])
 want=[v*(3 if poise else 1)//(8 if poise else 2) for v in losses]
 check('whole-pair-frozen-barrier-and-Poise',actual['hp'],500-sum(want))
 check('barrier-consumed-at-complete-action',actual['barrier'],int(not any(losses)))
 samples.append(dict(case=case,base=base,actual=actual))

# A second cast that cannot pay is known to be unavailable at the first
# queue boundary. The completed first cast must still receive its recovery.
for seed,residue in itertools.product(range(4),(0,4)):
 case=('second-unaffordable',seed,residue)
 configure('VIK-R1',False,seed,mp=6);base=run(residue)
 configure('VIK-R1',True,seed,mp=6);actual=run(residue)
 loss=500-base['hp'];eligible=loss>0 and base['hp']>0
 check('cancelled-pair-recovery',actual['hp'],base['hp']+min(loss*3//10,75) if eligible else base['hp'])
 check('cancelled-pair-one-recovery-object',sum(x[1]==436 for x in actual['objects']),int(eligible))
 if eligible:check('cancelled-pair-recovery-not-lost',any(x[1]==436 for x in actual['first']['objects']),True)

check('nonvacuous-first-only-recipient',any(s['case'][1]==7 and any(o[1]==436 for o in s['actual']['objects']) for s in samples if s['case'][0]=='VIK-R1'),True)

# A single Cureall intercepts both original Sleep spells. Put the caster two
# tiles away so its own cross does not cancel the second cast by putting the
# caster to sleep. These are fixed pre-action positions, never outcome edits.
cureall_positive=0
for seed,quantity,residue in itertools.product(range(8),(1,3),(0,4)):
 case=('whole-pair-Auto-Cureall',seed,quantity,residue);pair=[]
 for enabled in (False,True):
  configure('CHM-R2',enabled,seed)
  m.put(A+0xf6,bytes((3,14)));m.put(ns['wrappers'][A]+8,struct.pack('<H',3*32+16))
  h(B+0xaa,32);h(B+0xac,32);m.put(0x02001940+374,bytes((quantity,)))
  value=run(residue);value['curealls']=m.read(0x02001940+374,1)[0];pair.append(value)
 slept=bool(int.from_bytes(bytes.fromhex(pair[0]['status']),'little')&(1<<26))
 check('Cureall-intercepts-both-Sleep-attempts',bool(int.from_bytes(bytes.fromhex(pair[1]['status']),'little')&(1<<26)),False)
 check('one-Cureall-debit-for-pair',pair[1]['curealls'],quantity-int(slept))
 check('one-Cureall-presentation-for-pair',sum(o[1]==432 for o in pair[1]['objects']),int(slept))
 cureall_positive+=int(slept)
check('nonvacuous-paired-Sleep-interception',cureall_positive>0,True)

# Recovery requires survival through the final spell, not merely the first.
for hp,seed,residue in itertools.product((1,15,25),range(4),(0,4)):
 case=('survival-after-pair',hp,seed,residue)
 configure('VIK-R1',False,seed,hp=hp);base=run(residue)
 configure('VIK-R1',True,seed,hp=hp);actual=run(residue)
 loss=hp-base['hp'];eligible=loss>0 and base['hp']>0
 check('no-mid-pair-rescue-from-KO',actual['hp'],base['hp']+min(loss*3//10,75) if eligible else base['hp'])
 check('survival-required-for-queued-recovery',sum(o[1]==436 for o in actual['objects']),int(eligible and loss*3//10>0))

# Natural friendly fire can stop the caster. The native continuation checks
# then resolve pending recovery on the first result, before the shared finish.
cancel_positive=0
for seed,residue in itertools.product(range(8),(0,4)):
 case=('native-caster-KO-cancellation',seed,residue)
 configure('VIK-R1',False,seed);h(A+0x18,1);base=run(residue,second=False)
 if base['actorHP']:continue
 configure('VIK-R1',True,seed);h(A+0x18,1);actual=run(residue,second=False)
 loss=500-base['hp'];eligible=loss>0 and base['hp']>0
 check('caster-KO-does-not-lose-defender-recovery',actual['hp'],base['hp']+min(loss*3//10,75) if eligible else base['hp'])
 check('caster-KO-one-pending-reaction',sum(o[1]==436 for o in actual['objects']),int(eligible))
 cancel_positive+=int(eligible)
check('nonvacuous-natural-caster-KO',cancel_positive>0,True)
report=dict(passed=not failures,romSha1=meta['romSha1'],assertions=sum(checks.values()),checks=dict(checks),failures=failures,samples=samples)
(OUT/'doublecast-reactions.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Doublecast reaction failures',len(failures))
