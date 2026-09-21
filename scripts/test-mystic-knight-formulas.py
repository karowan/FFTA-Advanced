"""Independent native Fight/Fira controls and frozen Spellbreak defenses."""
import pathlib,json,struct,itertools,collections,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py'
ns={'__file__':str(source),'__name__':'mystic_formula_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs,call,half,fixture,grant,execute=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','regs','call','half','fixture','grant','execute'))
checks=collections.Counter();failures=[];case=None;samples=[]
scope=0x0203f72c

def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(case=case,check=k,actual=repr(a),expected=repr(b)))

def signed(n):return n if n<0x80000000 else n-0x100000000

# Unmodified native Fight supplies P without a custom art coefficient. The
# only Flare control change is independently reducing the target's base WDef.
for action,attack,defense in itertools.product(range(410,422),(60,90,120),(10,25,60)):
 case=('P-oracle',action,attack,defense);fixture(action)
 m.put(A+0x20,struct.pack('<H',attack));m.put(T+0x22,struct.pack('<H',defense))
 m.put(T+0x0d,b'\x01'*8);m.put(C+0x26,b'\x10')
 if action==421:grant(T,2);m.put(C+14,struct.pack('<H',1))
 if action==417:m.put(T+0x22,struct.pack('<H',defense*3//4))
 m.put(STACK,struct.pack('<3I',0,2,0))
 p=signed(m.call(0x0812fe38,A,T,0,88,stack=STACK))
 m.put(T+0x22,struct.pack('<H',defense))
 before=m.read(A,264)+m.read(T,264);rng=m.read(0x030034b0,4);old=m.read(scope,4)
 got=signed(call('ffta_myk_magnitude',C));coefficient=80 if action in (414,418,419) else 85 if action==421 else 100
 check('native-P-approved-coefficient',got,p*coefficient//100)
 check('P-query-unit-purity',m.read(A,264)+m.read(T,264),before)
 check('P-query-RNG-purity',m.read(0x030034b0,4),rng)
 check('P-query-scope-retirement',m.read(scope,4),old)

# Fira24 is a native M40 Fire control. A separately hashed reference image
# changes only that original spell's power to44 and element to neutral for
# Flare; it never calls Mystic's internal445 or dynamic Release element.
rom=pathlib.Path(meta['path']).read_bytes();control=bytearray(rom)
row=meta['tables']['actions']+24*28
assert control[row+11]==40 and control[row+2]==1
control[row+11]=44;control[row+2]=0
oracle=m.__class__(bytes(control),m.read(0x03000000,0x8000))
for blade,magic,defense,affinity in itertools.product((1,8),(30,50,90),(10,25,60),range(5)):
 case=('M-oracle',blade,magic,defense,affinity);fixture(422);call('ffta_myk_grant',A,blade)
 m.put(A+0x24,struct.pack('<H',magic));m.put(T+0x26,struct.pack('<H',defense));m.put(T+0x0d,bytes((affinity,)))
 m.put(C+0x26,b'\x10');before=m.read(C,0x34);rng=m.read(0x030034b0,4)
 if blade==8:
  oracle.put(0x02000000,m.read(0x02000000,0x40000));oracle.put(0x03000000,m.read(0x03000000,0x8000))
  oracle.put(C+12,struct.pack('<H',24));expected=signed(oracle.call(0x0813189c,C,stack=STACK))
 else:
  m.put(C+12,struct.pack('<H',24));expected=signed(m.call(0x0813189c,C,stack=STACK));m.put(C,before)
 check('native-M40-and-M44',signed(call('ffta_myk_magnitude',C)),expected)
 check('Release-query-no-consumption',call('ffta_myk_enchantment',A),blade)
 check('Release-query-RNG-purity',m.read(0x030034b0,4),rng)

# Each actual cast starts with the ordinary frozen snapshot. Removing a chosen
# defense must change this strike's damage while retaining all other defenses.
for selected,seed in itertools.product((10,11),range(8)):
 values=[]
 for scenario in ('absent','selected','retained'):
  case=('frozen-selected-defense',selected,seed,scenario);fixture(421,seed);grant(T,2)
  if scenario!='absent':
   call('ffta_drk_grant_last_resort' if selected==10 else 'ffta_drk_grant_tbn',T,0 if selected==10 else T)
  old=m.read(scope,4);execute(421,choice=selected if scenario=='selected' else 1)
  values.append(500-half(T+0x18));check('native-scope-retired',m.read(scope,4),old)
  if scenario=='selected' and values[-1]>0:
   check('native-selected-defense-removed',call('ffta_drk_last_resort' if selected==10 else 'ffta_drk_tbn',T),0)
 check('selected-defense-damage-equals-absent',values[1],values[0])
 if selected==11:check('unselected-TBN-still-protects',values[2],values[0]//2)
 elif values[0]:check('unselected-Last-Resort-still-exposes',values[2]>values[0],True)
 samples.append(dict(selected=selected,seed=seed,damage=values))
for selected in (10,11):check('nonvacuous-selected-defense',any(s['selected']==selected and s['damage'][0]>0 for s in samples),True)

# Foreign RAM, expired stack and bad self tags cannot alter incoming flags.
flags=(1<<22)|(1<<23)|0x12345
for pointer in (0,0x02027000,0x03006000,0x03007500):
 case=('scope-authentication',hex(pointer));fixture(421)
 if pointer:m.put(pointer,struct.pack('<4I',0,A,T,11))
 m.put(scope,struct.pack('<I',pointer));before=m.read(scope,4)
 check('unauthenticated-scope-no-override',call('ffta_myk_incoming_flags',A,T,421,flags),flags)
 check('scope-getter-no-repair',m.read(scope,4),before)

report=dict(passed=not failures,romSha1=meta['romSha1'],referenceM44Sha1=hashlib.sha1(control).hexdigest(),
 referenceChanges=[dict(action=24,field='power',old=40,new=44),dict(action=24,field='element',old=1,new=0)],
 assertions=sum(checks.values()),checks=dict(checks),nativeCasts=48,failures=failures,samples=samples)
(OUT/'mystic-knight-formulas.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert not failures,('Mystic formula failures',len(failures))
