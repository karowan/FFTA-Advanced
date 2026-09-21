"""Native Higanbana P input, bound and original-support contracts.

Only initial units, equipment power bytes and RNG seed are fixture inputs.
Observers never alter execution; the native formula and cap run unchanged.
"""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(FIX/'execute-trap.ram').read_bytes();iw=(FIX/'execute-trap.iwram').read_bytes()
UNIT,TARGET,CTX,RETURN,STACK=0x02000080,0x020033e4,0x0200f3f0,0x08000100,0x03007000
symbols=meta['symbols'];tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);m.put(0x02000000,ram);counts=collections.Counter();captures=[];arguments=[];scalars=[];powers=[]
def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def signed(x):return x if x<0x80000000 else x-0x100000000
def observe(u,p,size,data):
 if p==symbols['ffta_execution_capture']:captures.append(signed(u.reg_read(UC_ARM_REG_R0)))
 elif p==0x0812fe38:
  sp=u.reg_read(UC_ARM_REG_SP);arguments.append((u.reg_read(UC_ARM_REG_R2),*struct.unpack('<3I',m.read(sp,12))))
 elif p==0x0812feb0:scalars.append((signed(u.reg_read(UC_ARM_REG_R0)),signed(u.reg_read(UC_ARM_REG_R1))))
 elif p==0x0812ff6e:powers.append(u.reg_read(UC_ARM_REG_R0))
for pc in (symbols['ffta_execution_capture'],0x0812fe38,0x0812feb0,0x0812ff6e):m.u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
# Original racial support records are used, with no synthetic support handler.
bank=m.word(m.word(0x080cd538)+4)
indices={struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]:i for i in range(1,144) if m.read(bank+8*i+6,1)==b'\x03'}
supports=(0,*sorted(indices));check('native_attack_up_and_doublehand_records',all(x in indices for x in (1,7)),True)
items=m.word(0x08130684);gear=[i for i in range(1,376) if m.call(0x080ca7a4,i,6)==0 and m.call(0x080ca7a4,i,3)!=20][:4]
check('four_nonweapon_fixtures',len(gear),4);equipment=(383,*gear)
original_power={i:m.read(items+32*i+16,1) for i in equipment}
def fixture(offense,defense,power,support,protect,packed,exposed,mode,seed):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 for unit in (UNIT,TARGET):m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2))
 m.put(UNIT+5,bytes((116,1,116)));m.put(UNIT+0x35,b'\x74');m.put(UNIT+0x2a,struct.pack('<5H',*equipment));m.put(TARGET+0x2a,bytes(10))
 m.put(UNIT+0x20,struct.pack('<H',offense));m.put(TARGET+0x22,struct.pack('<H',defense))
 if support:m.put(UNIT+0x3b,bytes([indices[support]]));m.put(UNIT+0x40+indices[support],b'\xff')
 if protect:m.put(TARGET+0xeb,b'\x02')
 m.put(0x02001e98,bytes([packed])+bytes(35));m.put(0x02001eb4,bytes([exposed]));m.put(0x0203ff44,bytes(4))
 for i in equipment:m.put(items+32*i+16,original_power[i] if power is None else bytes([power]))
 context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,UNIT,TARGET,TARGET,355,0);context[0x26]=0x10 if mode==2 else 0;m.put(CTX,context);m.put(0x030034b0,struct.pack('<I',seed))
 captures.clear();arguments.clear();scalars.clear();powers.clear()
 before=(m.read(UNIT,264),m.read(TARGET,264),m.read(0x02001e98,108))
 result=signed(m.call(symbols['ffta_physical_magnitude_entry'],CTX))
 check('native_support_assignment',m.call(0x080cd50c,UNIT),support)
 check('exact_native_call_args',arguments,[(355,0,mode,0)])
 check('one_reference_capture',len(captures),1)
 check('native_scalar_bounds',all(0<=a<=999 and 0<=d<=999 for a,d in scalars) and bool(scalars),True)
 check('native_power_bounds',bool(powers) and all(0<=p<=6*255 for p in powers),True)
 check('captured_P_bound',0<=captures[0]<=25218,True)
 check('fits_lossless_record',captures[0]//2<0x4000,True)
 check('query_no_unit_or_custom_state_change',(m.read(UNIT,264),m.read(TARGET,264),m.read(0x02001e98,108)),before)
 return result,captures[0],scalars[0],powers[0]
maximum=0
for offense,defense,power,support,protect,mode,seed in itertools.product((1,500,999),(0,999),(0,255),supports,(False,True),(0,2),(0,1)):
 result,p,scalar,total=fixture(offense,defense,power,support,protect,0,0,mode,seed);maximum=max(maximum,p)
 check('initial_hit_coefficient_before_cap',result,min(999,p*80//100))
check('exercised_uncapped_large_reference',maximum>999,True)
comparisons=[]
for support,protect,seed in itertools.product((0,1,7),(False,True),range(4)):
 rows=[fixture(200,100,None,support,protect,packed,exposed,0,seed) for packed,exposed in ((0,0),(4,0),(0,1),(4,1))]
 check('final_modifiers_do_not_change_P',len({row[1] for row in rows}),1)
 for row,(packed,exposed) in zip(rows,((0,0),(4,0),(0,1),(4,1))):
  check('one_round_immediate_damage',row[0],min(999,row[1]*80*(5 if packed else 4)*(6 if exposed else 5)//2000))
 comparisons.append(dict(support=support,protect=protect,seed=seed,P=rows[0][1],offense=rows[0][2][0],defense=rows[0][2][1]))
# Specification explicitly retains native attack/defense supports in P's inputs.
for protect,seed in itertools.product((False,True),range(4)):
 row=lambda s:next(x for x in comparisons if (x['support'],x['protect'],x['seed'])==(s,protect,seed))
 check('Attack_Up_is_native_offense_input',row(1)['offense']>row(0)['offense'],True)
 check('Doublehand_stays_Fight_only',row(7),dict(row(0),support=7))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),observedMaximumP=maximum,conservativeBound=25218,comparisons=comparisons,scope='Real native formula with bounded unit/equipment inputs, original support lookup, noncritical arguments, exact pre-final capture and Centered/Exposed exclusion; future new multipliers must join the later final phase')
(ROM.parent/'wound-reference-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
