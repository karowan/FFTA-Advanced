"""Native AI row selection and exact scoped forecast transport; no score stubs."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-dancer.py';ns={'__file__':str(source),'__name__':'ai_choice_fixture'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs=(ns[k] for k in ('m','S','meta','OUT','A','T','C','STACK','regs'))
fixture=ns['fixture'];wrappers=ns['ns']['wrappers']
checks=collections.Counter();case=None;rows=[];failures=[]
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
trace=[]
def traced(u,address,size,data):
 if case and case[:4]==('native-choice-row',STACK,0,0) and len(trace)<160:
  trace.append([hex(address),*[hex(u.reg_read(r)) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP)],m.read(0x0200f41c,8).hex()])
for address in (0x080c2314,0x080c244a,0x080c2474,0x080c247e,0x080c248a,0x080c2492,0x080c24be):
 m.u.hook_add(UC_HOOK_CODE,traced,begin=address,end=address)
ROW=0x02028000;ROOT_PTR=0x0203f728;TOKEN=0x03007d00
def check(k,ok):
 checks[k]+=1
 if not ok:failures.append((k,case))
def half(p):return struct.unpack('<H',m.read(p,2))[0]
def invoke(address,row,action,choice,sp):
 m.put(sp,struct.pack('<II',choice,0))
 m.call(address,row,wrappers[A],wrappers[T],action,stack=sp)
def arm(choice):
 m.put(TOKEN,struct.pack('<7I',0x41494348,TOKEN,A,406,choice,0,0));m.put(ROOT_PTR,struct.pack('<I',TOKEN))

# Ailment combinations force every option to win at least once using actual
# native status eligibility. Both stack alignments and held weapon operands
# must retain one action record and leave live units/AP untouched.
winners=set()
for sp,mask,weapon in itertools.product((STACK,STACK+4),range(16),(0,1,416)):
 case=('native-choice-row',sp,mask,weapon);fixture(406,weapon=weapon)
 manager=m.word(0x0200f438);m.put(manager+4,b'\x00')
 statuses=bytearray(8)
 for i,bit in enumerate((10,27,9,28)):
  if mask&(1<<i):statuses[bit//8]|=1<<(bit%8)
 m.put(T+0xe8,statuses);m.put(ROOT_PTR,bytes(4));m.put(ROW-16,b'\xa5'*52)
 live=m.read(A,264)+m.read(T,264);rng=m.read(0x030034b0,4);expected=[]
 for choice in range(1,5):
  arm(choice);m.put(ROW,bytes(20));invoke(S['ffta_ai_original_row'],ROW,406,choice,sp)
  row=m.read(ROW,20);score=abs(struct.unpack_from('<h',row,12)[0]) if half(ROW+10) else 0
  if mask&(1<<(choice-1)):score=0;row=row[:4]+bytes(16)
  expected.append((score,row));m.put(ROOT_PTR,bytes(4))
 best=max(range(4),key=lambda i:expected[i][0])
 m.put(ROW,bytes(20));invoke(0x080c2618,ROW,406,0,sp)
 actual=m.read(ROW,20)
 check('best-native-row-exact',actual==expected[best][1]);check('choice-root-retired',m.read(ROOT_PTR,4)==bytes(4))
 check('row-guards',m.read(ROW-16,16)==b'\xa5'*16 and m.read(ROW+20,16)==b'\xa5'*16)
 check('live-units-AP-unchanged',m.read(A,264)+m.read(T,264)==live)
 check('forecast-RNG-unchanged',m.read(0x030034b0,4)==rng)
 if expected[best][0]:winners.add(half(ROW+2))
 rows.append(dict(mask=mask,weapon=weapon,choice=half(ROW+2),values=[e[0] for e in expected],row=actual.hex()))
check('all-four-options-selected',winners=={1,2,3,4})

# Matching action alone cannot borrow another unit's choice; stale/out-of-stack
# roots and zero/out-of-range options remain unavailable.
fixture(406);manager=m.word(0x0200f438);m.put(manager+4,b'\x00')
for choice in range(6):
 arm(choice)
 for actor,action in ((A,406),(T,406),(A,23),(A,381)):
  case=('scope',choice,actor,action)
  result=m.call(S['ffta_ai_preview_choice'],actor,action,stack=STACK)
  check('exact-owner-action-option',result==(choice if actor==A and action==406 and 1<=choice<=4 else 0))
for pointer in (0,1,0x02028000,0x03008000,0xffffffff):
 m.put(ROOT_PTR,struct.pack('<I',pointer));case=('stale-root',pointer)
 check('reject-stale-root',m.call(S['ffta_ai_preview_choice'],A,406,stack=STACK)==0)
m.put(ROOT_PTR,bytes(4))

# Completed AI decisions may supply the operand after the synchronous scoring
# frame has retired. Reject each stale/foreign publication independently.
NODE=0x02015488;AI=0x020101f8
for choice,invalid in itertools.product(range(1,5),('none','player','wrapper','owner','phase','success','action','published-action','published-choice')):
 case=('published-decision',choice,invalid);fixture(406);m.put(ROOT_PTR,bytes(4))
 m.put(A+0x29,b'\x80');m.put(0x0200f4ec,struct.pack('<I',wrappers[A]))
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',406,choice));m.put(NODE+0x1b1,b'\x01')
 m.put(AI+0x54f4,struct.pack('<H',8));m.put(AI+0x54be,struct.pack('<HH',406,choice))
 if invalid=='player':m.put(A+0x29,b'\x00')
 if invalid=='wrapper':m.put(0x0200f4ec,struct.pack('<I',wrappers[T]))
 if invalid=='owner':m.put(NODE,struct.pack('<I',wrappers[T]))
 if invalid=='phase':m.put(AI+0x54f4,bytes(2))
 if invalid=='success':m.put(NODE+0x1b1,b'\x00')
 if invalid=='action':m.put(NODE+8,bytes(2))
 if invalid=='published-action':m.put(AI+0x54be,bytes(2))
 if invalid=='published-choice':m.put(AI+0x54c0,bytes(2))
 check('authenticated-published-choice',m.call(S['ffta_ai_preview_choice'],A,406,stack=STACK)==(choice if invalid=='none' else 0))

# The installed score wrapper must use this action's one choice for any
# recipient; keep native permission, formulas and status results intact.
for choice,sp in itertools.product(range(1,5),(STACK,STACK+4)):
 case=('native-score-transport',choice,sp);fixture(406)
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',406,choice));m.put(ROOT_PTR,bytes(4))
 live=m.read(A,264)+m.read(T,264);rng=m.read(0x030034b0,4)
 arm(choice);expected=m.call(S['ffta_ai_original_score'],wrappers[A],wrappers[T],406,0,stack=sp)
 m.put(ROOT_PTR,bytes(4));actual=m.call(0x080bdecc,wrappers[A],wrappers[T],406,0,stack=sp)
 check('native-score-explicit-choice',actual==expected)
 check('score-live-units-unchanged',m.read(A,264)+m.read(T,264)==live)
 check('score-RNG-unchanged',m.read(0x030034b0,4)==rng)
 check('score-scope-retired',m.read(ROOT_PTR,4)==bytes(4))

# Installed wrapper delegates native actions byte-for-byte at the row boundary.
for action,sp in itertools.product((0,1,23,41,265),(STACK,STACK+4)):
 case=('native-compatibility',action,sp);fixture(action);m.put(ROOT_PTR,bytes(4))
 before=m.read(0x02000000,0x40000);iw=m.read(0x03000000,0x8000)
 m.put(ROW,bytes(20));invoke(S['ffta_ai_original_row'],ROW,action,1,sp)
 expected=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 m.put(0x02000000,before);m.put(0x03000000,iw);m.put(ROW,bytes(20));invoke(0x080c2618,ROW,action,1,sp)
 check('original-row-memory',m.read(0x02000000,0x40000)==expected)
 check('original-row-RNG',m.read(0x030034b0,4)==rng)
report=dict(passed=not failures,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),rows=rows,failures=failures,winners=sorted(winners),trace=trace)
(OUT/'ai-choice.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not failures,failures
