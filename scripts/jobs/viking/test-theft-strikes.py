"""Independent theft stages, native loot depletion and following physical damage."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
parent=json.loads((P/'job-state/current.json').read_text());fix=pathlib.Path(meta['path']).parent/'executor'
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,EQUIPMENT,RETURN,STACK=0x02000080,0x020033e4,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
control=bytearray(rom);pc=meta['symbols'].get('ffta_integrated_physical_final',meta['symbols']['ffta_viking_physical_final'])-0x08000000;control[pc:pc+2]=bytes.fromhex('7047')
n,m=ARM(control,iw),ARM(rom,iw)
original=ARM(rom,iw)
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};counts=collections.Counter();seen=collections.Counter();samples=[]
old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
def check(k,a,b):
 counts[k]+=1
 assert a==b,(k,a,b)
def setup(machine,action,seed,item,weapon=399):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw)
 actor=bytearray(ram[0x80:0x80+264]);target=bytearray(ram[0x33e4:0x33e4+264])
 actor[5]=actor[7]=actor[0x35]=118;actor[6]=2;actor[0x3a]=actor[0x3b]=0
 actor[0xe8:0xf0]=target[0xe8:0xf0]=bytes(8)
 struct.pack_into('<4H',actor,0x18,100,100,50,50);struct.pack_into('<4H',target,0x18,250,250,49,49)
 struct.pack_into('<5H',actor,0x2a,weapon,0,0,0,0);struct.pack_into('<5H',target,0x2a,item,0,0,0,0)
 actor[0xf6:0xf8]=bytes([4,14]);target[0xf6:0xf8]=bytes([5,14])
 machine.put(UNIT,actor);machine.put(TARGET,target)
 machine.put(wrappers[UNIT]+8,struct.pack('<H',4<<5));machine.put(wrappers[UNIT]+12,struct.pack('<H',14<<5))
 machine.put(0x02001e98,bytes(108));machine.put(0x0203ff44,bytes(8));machine.put(0x030034b0,struct.pack('<I',seed));machine.put(regs[13],struct.pack('<4I',action,0,0,255))
def execute(machine):
 machine.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13]);return machine.read(0x02000000,0x40000)
for action,item,seed in itertools.product((367,370),(0,288,302,354),range(64)):
 results=[]
 for machine in (n,m):
  setup(machine,action,seed,item);before=machine.call(old['ffta_owned'],0x02000000,item) if item else 0;r=execute(machine);after=machine.call(old['ffta_owned'],0x02000000,item) if item else 0
  results.append((r,before,after))
 (nr,nb,na),(r,b,a)=results
 damage=250-struct.unpack_from('<H',r,0x33fc)[0];Pdamage=250-struct.unpack_from('<H',nr,0x33fc)[0]
 check('native-P-single-coefficient',damage,Pdamage*(85 if action==367 else 100)//100)
 check('native-cost-once',struct.unpack_from('<H',r,0x9c)[0],50-(6 if action==367 else 10))
 check('same-native-theft-outcome',r[0x340e:0x3418],nr[0x340e:0x3418])
 check('same-native-inventory-transaction',(b,a),(nb,na))
 # Independent native original-command oracle, with no patched callback,
 # forced result or overwritten expected state. Each case starts at the same
 # seed and equipment and executes original Steal Accessory/Armor end to end.
 # The later HP stage consumes extra RNG but cannot change the earlier theft.
 setup(original,165 if action==367 else 163,seed,item)
 original_before=original.call(old['ffta_owned'],0x02000000,item) if item else 0
 original_result=execute(original)
 original_after=original.call(old['ffta_owned'],0x02000000,item) if item else 0
 check('independent-original-steal-equipment',r[0x340e:0x3418],original_result[0x340e:0x3418])
 check('independent-original-steal-inventory',(b,a),(original_before,original_after))
 stolen=bool(item and not struct.unpack_from('<H',r,0x340e)[0]);seen[(action,'theft' if stolen else 'noTheft','damage' if damage else 'noDamage')]+=1
 if stolen:
  check('native-single-item-grant',a-b,1)
  before=a;r2=execute(m);after=m.call(old['ffta_owned'],0x02000000,item)
  check('depleted-item-cannot-be-stolen-again',after,before)
 samples.append(dict(action=action,item=item,seed=seed,stolen=stolen,damage=damage,reference=Pdamage,ownedBefore=b,ownedAfter=a))
(ROM.parent/'theft-strikes-observed.json').write_text(json.dumps(dict(outcomes={str(k):v for k,v in seen.items()},samples=samples),indent=2))
print({str(k):v for k,v in seen.items()})
for action in (367,370):
 check('nonvacuous-theft-independent-of-damage',seen[(action,'theft','noDamage')]>0,True)
 check('nonvacuous-damage-independent-of-theft',seen[(action,'noTheft','damage')]>0,True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),outcomes={str(k):v for k,v in seen.items()},samples=samples,scope=__doc__)
(ROM.parent/'theft-strikes.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
