"""Native harmful-status law prediction and committed HP-result contracts."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,TARGET,LAW,MASK,RETURN,STACK=0x02000080,0x020033e4,0x0203e000,0x0203e100,0x08000100,0x03007000
symbols=meta['symbols'];tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);m.put(0x02000000,ram);checks=collections.Counter();alignment=[]

def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b)
entry=symbols['ffta_higan_harmful_law'];m.u.hook_add(UC_HOOK_CODE,lambda u,p,s,d:alignment.append(u.reg_read(UC_ARM_REG_SP)%8),begin=entry,end=entry)
bank=m.word(m.word(0x080cd538)+4)
def index(effect,kind):return next(i for i in range(1,144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==effect and m.read(bank+8*i+6,1)[0]==kind)
reaction,immunity=index(13,2),index(11,3)
items=m.word(0x08130684);original_effect=m.read(items+383*32+26,3)
def setup(condition):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 for unit in (UNIT,TARGET):m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2));m.put(unit+0x18,struct.pack('<4H',250,250,50,50))
 m.put(UNIT+5,bytes((116,1,116)));m.put(UNIT+0x35,b'\x74');m.put(UNIT+0x2a,struct.pack('<5H',383,0,0,0,0));m.put(0x02001e98,bytes(108));m.put(items+383*32+26,original_effect)
 if condition=='MP':m.put(TARGET+5,bytes((2,1,2)));m.put(TARGET+0x3a,bytes([reaction]));m.put(TARGET+0x40+reaction,b'\xff');check('equipped_MP_interception',m.call(0x080cd4d4,TARGET),13)
 if condition=='immune':m.put(TARGET+5,bytes((2,1,2)));m.put(TARGET+0x3b,bytes([immunity]));m.put(TARGET+0x40+immunity,b'\xff');check('equipped_Immunity',m.call(0x080cd50c,TARGET),11)
 if condition=='petrify':m.put(TARGET+0xe8,b'\x40')
 if condition=='KO':m.put(TARGET+0x18,bytes(2))
 if condition=='lethal':m.put(TARGET+0x18,b'\x01\x00')
 if condition=='healing':m.put(items+383*32+26,b'\x3f\x00\x00');m.put(TARGET+0x18,b'\x64\x00')
 if condition=='friend':m.put(TARGET+0x28,struct.pack('<H',int.from_bytes(m.read(TARGET+0x28,2),'little')&0x7fff))
 if condition=='confused':m.put(UNIT+0xeb,b'\x10')
 if condition=='actorKO':m.put(UNIT+0x18,bytes(2))
def invoke(kind,value,damage=0,mask=False,residue=0,move=0):
 m.put(LAW,bytes([0,0,0,0,kind,value,0,0,0,0,0,0]));m.put(MASK,bytes(8));sp=STACK+residue;m.put(sp,struct.pack('<4I',move,damage&0xffffffff,MASK if mask else 0,LAW))
 before=(m.read(UNIT,264),m.read(TARGET,264),m.read(0x02001e98,108));rng=m.word(0x030034b0)
 out=m.call(0x081343c8,UNIT,TARGET,355,0,stack=sp)
 check('live_sources_preserved',(m.read(UNIT,264),m.read(TARGET,264),m.read(0x02001e98,108)),before)
 if kind==16:check('custom_query_rng_preserved',m.word(0x030034b0),rng)
 return out
for condition,residue in itertools.product(('normal','MP','immune','petrify','KO','lethal','healing','friend','confused','actorKO'),(0,4)):
 setup(condition);check('predicted_harmful_status',(condition,invoke(16,0,residue=residue)),(condition,int(condition=='normal')))
# Native committed callers supply signed HP damage and a status-mask pointer.
# A positive MP interception therefore supplies0 HP, as native135028..5032 shows.
for record,damage,condition,residue in itertools.product((0,0x400b,0x800b,0xc00b),(-10,0,1,99),('normal','immune','petrify','KO'),(0,4)):
 setup(condition);m.put(0x02001ef4,struct.pack('<H',record))
 expected=int(condition=='normal' and damage>0 and record>>14 in (1,2))
 check('committed_HP_and_wound_gate',invoke(16,0,damage,True,residue),expected)
for kind,value,residue in itertools.product((2,10,15),(1,2,9,25),(0,4)):
 setup('normal');check('no_invented_element_or_Poison',invoke(kind,value,residue=residue),int(kind==10 and value==9))
for move,residue in itertools.product((1,2,255),(0,4)):
 setup('normal');check('native_movement_gate',invoke(16,0,residue=residue,move=move),0)
check('C_stack_alignment',set(alignment),{0})
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),scope='Complete native law kind16 prediction/committed mask branch; HP versus MP, status prevention, native gates, source/RNG isolation and no Poison-law alias. Future automatic custom cures require an application-event result marker.')
(ROM.parent/'wound-laws-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
