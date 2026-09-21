"""Native full action execution: Blade Ward reductions, Wound reference and Counter exclusion."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(FIX/'execute-trap.ram').read_bytes();iw=(FIX/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(FIX/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,RETURN,STACK=0x02000080,0x020033e4,0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
control=bytearray(rom)
for name,value in (('ffta_poise_factor',4),('ffta_blade_ward_factor',20)):
 p=meta['symbols'][name]-0x08000000;control[p:p+4]=bytes((value,0x20,0x70,0x47))
reference_rom=bytearray(control);p=meta['symbols']['ffta_physical_final']-0x08000000;reference_rom[p:p+2]=bytes.fromhex('7047')
m,n,p=ARM(rom,iw),ARM(control,iw),ARM(reference_rom,iw)
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
checks=collections.Counter();outcomes=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b)
def half(machine,address):return int.from_bytes(machine.read(address,2),'little')
def reset(machine,poise=False,exposed=0):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(0x0203ff44,bytes(8));machine.put(0x02001e98,bytes(108))
 for unit,x in ((TARGET,4),(UNIT,5)):
  machine.put(unit+5,bytes((116,1,116)));machine.put(unit+0xe8,bytes(8));machine.put(unit+0x3a,bytes(2));machine.put(unit+0x18,struct.pack('<4H',500,500,999,999));machine.put(unit+0x2a,struct.pack('<5H',383,0,0,0,0));machine.put(unit+0xf6,bytes((x,14)));machine.put(wrappers[unit]+8,struct.pack('<3H',x*32+16,32,14*32+16))
 machine.put(UNIT+0x3a,bytes((155,154 if poise else 0)));machine.put(0x02001b4a,b'\xff\xff');machine.put(UNIT+0xe8,bytes((8 if poise else 0,)));machine.put(0x02001e98,bytes((exposed,)))
def execute(machine,actor,target,action,seed):
 machine.put(0x030034b0,struct.pack('<I',seed));machine.put(regs[13],struct.pack('<4I',action,0,0,255))
 machine.call(0x080a433c,regs[0],wrappers[actor],machine.read((actor if action==354 else target)+0xf6,1)[0],14,stack=regs[13])
 check('transient_roots_retired',machine.read(0x0203ff44,8),bytes(8))
 return dict(hp=half(machine,target+0x18),mp=half(machine,target+0x1c),rng=machine.word(0x030034b0),wound=half(machine,0x02001ebc))
for action,poise,exposed,seed in itertools.product((0,23,90,112,125,266,347,348,354,355),(False,True),(0,1),range(8)):
 pair=[]
 for machine in (p,m):
  reset(machine,poise,exposed if machine is m else 0);pair.append(execute(machine,TARGET,UNIT,action,seed))
 reference=500-pair[0]['hp'];physical=action!=23;num=110 if action==347 else 80 if action==355 else 135 if action==354 else 100;pf=3 if poise else 4;wf=13 if physical else 20;xf=6 if exposed and physical else 5
 expected=reference*num*pf*wf*xf//40000
 check('actual_HP_single_round',(action,poise,exposed,seed,500-pair[1]['hp']),(action,poise,exposed,seed,expected))
 check('native_RNG_unchanged',pair[1]['rng'],pair[0]['rng'])
 check('incoming_MP_not_changed',pair[1]['mp'],999)
 if action==355:check('Wound_P_not_reduced_by_Ward',pair[1]['wound'],(0x8000|reference//2) if reference else 0)
 outcomes.append(dict(action=action,poise=poise,exposed=exposed,seed=seed,reference=reference,damage=expected))
for action in (0,23,90,112,125,266,347,348,354,355):check('each_action_positive_execution',any(x['action']==action and x['damage']>0 for x in outcomes),True)
# Reverse the attack: UNIT uses Guarding Draw, TARGET has native Counter8.
# Counter is a separate result with native reactions disabled, so Ward cannot
# answer it. Poise remains an independently eligible defensive support.
for poise,seed in itertools.product((False,True),range(4)):
 pair=[]
 for machine in (n,m):
  reset(machine,poise);machine.put(TARGET+0x3a,bytes((44,)));machine.put(TARGET+0x40+44,b'\xff')
  check('native_Counter_assigned',machine.call(0x080cd4d4,TARGET),8)
  execute(machine,UNIT,TARGET,352,seed);pair.append(500-half(machine,UNIT+0x18))
 check('Counter_excludes_Ward_preserves_Poise',pair[1],pair[0]*3//4 if poise else pair[0])
 outcomes.append(dict(counter=True,poise=poise,seed=seed,control=pair[0],damage=pair[1]))
check('positive_Counter_exercised',any(x.get('counter') and x['control']>0 for x in outcomes),True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),outcomes=outcomes,scope=__doc__)
(ROM.parent/'blade-ward-executor.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
