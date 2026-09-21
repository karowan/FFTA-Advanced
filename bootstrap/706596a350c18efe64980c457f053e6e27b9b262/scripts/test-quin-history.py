"""Native candidate differentials and persistent Quin retry ownership rules."""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
t=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
P=ROOT/'build/expansion/probes';D=P/'quin-history';meta=json.loads((D/'quin-history.json').read_text());symbols=meta['symbols']
rom=(D/'quin-history.gba').read_bytes();baseline=pathlib.Path(meta['source']).read_bytes()
if '--current' in sys.argv:
 rom=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
 symbols={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
 baseline=bytearray(rom);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
 for address,size,name in [(0xd241c,8,'ffta_quin_candidate_entry'),(0x807d4,8,'ffta_quin_accept_entry'),(0x62004,12,'ffta_quin_swap_entry')]:
  assert struct.unpack_from('<I',rom,address+(6 if address%4 else 4))[0]==symbols[name]|1
  baseline[address:address+size]=clean[address:address+size]
 D=D/meta['romSha1'];D.mkdir(exist_ok=True);(D/'current.gba').write_bytes(rom);(D/'engine.symbols').write_bytes((ROOT/'build/expansion/engine.symbols').read_bytes())
native=ARM(bytes(baseline),iwram_from_boot());patched=ARM(rom,iwram_from_boot())
ram=bytearray((P/'battle-fixture/battle-ready.ram').read_bytes());ram[0x1e79]=2
count=0
def check(a,b,why):
 global count
 assert a==b,(why,a,b);count+=1
# Scan every native code halfword for direct branch targets. Conservatively
# include data-shaped instructions too; no external branch may enter a veneer.
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();branches=[]
for p in range(0,0x145000,2):
 h=struct.unpack_from('<H',clean,p)[0];destination=None
 if h&0xf800==0xe000:
  d=(h&0x7ff)*2;destination=p+4+(d-0x1000 if d&0x800 else d)
 elif h&0xf000==0xd000 and h&0xf00<0xe00:
  d=(h&255)*2;destination=p+4+(d-0x200 if d&0x100 else d)
 elif h&0xf800==0xf000 and struct.unpack_from('<H',clean,p+2)[0]&0xf800==0xf800:
  d=((h&0x7ff)<<12)|((struct.unpack_from('<H',clean,p+2)[0]&0x7ff)<<1);destination=p+4+(d-0x800000 if d&0x400000 else d)
 if destination is not None:branches.append((p,destination))
for a,n in ((0xd241c,8),(0x807d4,8),(0x62004,12)):
 check([(p,d) for p,d in branches if a<d<a+n and not a<=p<a+n],[],('no external branch into veneer',hex(a)))
check(any(d==0x62010 and p>=0x62014 for p,d in branches),True,'positive control catches old unsafe swap span')
def reset(m):m.put(0x02000000,bytes(ram))
def call(m,name,*args):return m.call(symbols[name],*args)
def align(u,address,size,data):check(u.reg_read(UC_ARM_REG_SP)%8,0,'C stack alignment')
for name in ('ffta_quin_candidate','ffta_quin_retry_blocked','ffta_quin_observe'):
 patched.u.hook_add(UC_HOOK_CODE,align,begin=symbols[name],end=symbols[name])
for record,seed in itertools.product(range(406),(0,1)):
 result=[]
 for m in (native,patched):
  reset(m);m.put(0x030034b0,struct.pack('<I',seed));value=m.call(0x080d241c,record,0x02002fc4)
  result.append((value,m.read(0x02002fc4,264),m.read(0x030034b0,4)))
 check(result[0],result[1],('native candidate/rng',record,seed))
for history,complete,present,format_ok in itertools.product((0,1,2,3,0x80,0x82,0x83),(False,True),(False,True),(False,True)):
 reset(patched);state=0x02024000;fixture=bytearray(ram[:0x4000]);fixture[0x1e79]=history
 fixture[0x1fd8]=(fixture[0x1fd8]&~2)|(2 if complete else 0)
 for i in range(24):fixture[0x84+264*i]=0
 if present:fixture[0x80:0x87]=bytes.fromhex('5f165508011b03')
 if not format_ok:fixture[0x1e78]=0
 patched.put(state,bytes(fixture));call(patched,'ffta_quin_prepare',state)
 expected=history
 if format_ok:expected=history|(1 if present else 0) if history&2 else (history&~3)|2|(1 if complete or present else 0)
 after=patched.read(state,len(fixture));check(after[0x1e79],expected,'migration policy');fixture[0x1e79]=expected
 check(after,bytes(fixture),'staging write scope')
 # Once accepted, removing the unit never clears the history bit.
 patched.put(state+0x84,b'\0');call(patched,'ffta_quin_prepare',state)
 check(patched.read(state+0x1e79,1)[0],expected,'absent/dead history preserved')
for history in (0,1,2,3,0x82,0x83):
 reset(patched);patched.put(0x02001e79,bytes((history,)));patched.put(0x02002fc4,b'\xa5'*264);patched.put(0x030034b0,struct.pack('<I',2))
 value=patched.call(0x080d241c,111,0x02002fc4)
 if history&3!=2:
  check(value,0,'blocked retry return');check(patched.read(0x02002fc4,264),bytes(264),'blocked clears candidate');check(patched.read(0x030034b0,4),struct.pack('<I',2),'blocked does not roll RNG')
 else:check(value,1,'missed offer remains eligible')
# Whole native swap/replacement commit, with the UI's actual encoded name form.
for machine in (native,patched):
 reset(machine);machine.put(0x030034b0,struct.pack('<I',0));check(machine.call(0x080d241c,111,0x02002fc4),1,'swap candidate')
 machine.put(0x02002fc4,struct.pack('<I',97));machine.put(0x020030ca,b'\x01')
 machine.put(0x02030000,bytes(0x200));machine.put(0x0200f450,struct.pack('<I',0x02030000));machine.put(0x0203005c,struct.pack('<II',0x02002fc4,0x020006b0))
 machine.call(0x08061f54,1)
check(patched.read(0x020006b0,264),native.read(0x020006b0,264),'native whole swap unit unchanged')
check(patched.read(0x02001e79,1),b'\x03','native whole swap records accepted Quin')
report={'romSha1':meta['romSha1'],'checks':count,'nativeMissions':406,'nativeSeeds':[0,1],'scope':'Native candidate generator, staging initialization, monotonic accepted/death history; actual UI/save tested separately.'}
(D/'native-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
