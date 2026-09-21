"""Frozen native executor and four new Samurai strike contracts."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];fix=P/'samurai-state'/meta['baseSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000;TARGET=0x020033e4
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,expanded=ARM(base,iw),ARM(rom,iw);counts=collections.Counter();samples=[]
def check(kind,a,b):
 counts[kind]+=1
 if a!=b and isinstance(a,bytes) and isinstance(b,bytes):
  (OUT/f'failure-{action}-actual.ram').write_bytes(a);(OUT/f'failure-{action}-expected.ram').write_bytes(b)
  differences=[(hex(i),x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
  raise AssertionError((kind,action,len(differences),differences[:16]))
 assert a==b,(kind,a,b)
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
WRAPPER=wrappers[UNIT]

def original(m,action):
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(regs[13],struct.pack('<I',action));m.put(0x02001e98,b'\xa1'*36)
 # The fixture's D7 guard predates the allocated action-snapshot root. Both
 # controls start with its legal empty value; all EWRAM still compares exactly.
 m.put(0x0203ff48,bytes(4))
 # A433C is a native void routine: its epilogue returns the caller address in
 # R0. Only preserved registers/SP and actual state are caller observables.
 m.call(0x080a433c,*regs[:4],stack=regs[13]);return m.read(0x02000000,0x40000)
for action in list(range(347))+[357,358,423,424,425,426,427,428,429,430,431]:
 a=original(native,action)
 check('complete-native-executor-preserved',original(expanded,action),a)

def reset(m,action,state,seed=0,weapon=376):
 m.put(0x02000000,ram);m.put(0x03000000,iw);actor=bytearray(ram[0x80:0x80+264]);target=bytearray(ram[0x33e4:0x33e4+264]);actor[5]=actor[7]=actor[0x35]=116;actor[0x3a]=actor[0x3b]=0;actor[0xe8:0xf0]=bytes(8);target[0xe8:0xf0]=bytes(8)
 struct.pack_into('<HHHH',actor,0x18,100,100,50,50);struct.pack_into('<5H',actor,0x2a,weapon,0,0,0,0);actor[0xf6:0xf8]=bytes([4,14]);struct.pack_into('<HHHH',target,0x18,250,250,49,49)
 m.put(UNIT,actor);m.put(TARGET,target);m.put(WRAPPER,struct.pack('<I',UNIT));m.put(WRAPPER+8,struct.pack('<H',4<<5));m.put(WRAPPER+12,struct.pack('<H',14<<5));m.put(0x02001e98,bytes([state]));m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
def execute(m):
 m.call(0x080a433c,regs[0],WRAPPER,5,14,stack=regs[13]);r=m.read(0x02000000,0x40000);return r,250-struct.unpack_from('<H',r,0x33fc)[0]
plain=bytearray(rom);plain[0x1300e2:0x1300f2]=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()[0x1300e2:0x1300f2];reference=ARM(plain,iw)
for action,state,seed,exposed in itertools.product((347,349,352,353),(1,5,13),(0,1),(0,1)):
 num={347:110,349:85,352:100,353:145}[action];mp={347:4,349:6,352:6,353:10}[action]
 reset(reference,action,state,seed);reference.put(0x02001eb4,bytes([exposed]));ar,p=execute(reference)
 reset(expanded,action,state,seed);expanded.put(0x02001eb4,bytes([exposed]));r,damage=execute(expanded)
 boosted=action!=347 and bool(state&6)
 expected=p*num*(5 if boosted else 4)*(6 if exposed else 5)//2000
 check('new-damage-independent-native-P',damage,expected)
 check('native-one-MP-payment',struct.unpack_from('<H',r,0x9c)[0],50-mp)
 expected_state=13 if action==347 and damage>0 else (state if action==347 else 1)
 check('grant-consume-retire-even-miss',r[0x1e98],expected_state)
 check('Osafune-actual-MP-loss',struct.unpack_from('<H',r,0x3400)[0],39 if action==349 and damage>0 else 49)
 if action==352:check('Guarding-Draw-after-attempt-Protect',(r[0x16b]&2,r[0x15e]),(2,3))
 samples.append(dict(action=action,state=state,seed=seed,targetExposed=exposed,P=p,damage=damage,finalState=r[0x1e98]))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),nativeFixtureSkipped=[],samples=samples)
(OUT/'native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
