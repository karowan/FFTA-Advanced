"""Every teaching association through native equip, AP award and removal.

The current installed ROM executes complete equipment setters and the native
results AP-award block. Fixed initial unit/job and award quantities are inputs;
AP mastery, equipment usability and notifications are never supplied results.
This checks learning mechanics, not campaign acquisition or results-screen art.
"""
import ast,collections,datetime,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
path=pathlib.Path(meta['path']);rom=path.read_bytes();sha=lambda x:hashlib.sha1(x).hexdigest()
assert sha(rom)==meta['romSha1']
fix=path.parent/'fixture';proof=json.loads((fix/'prepare-cache.json').read_text())
assert (fix/'frozen.gba').read_bytes()==rom
iw=(fix/'battle-ready.iwram').read_bytes();assert sha(iw)==proof['outputs']['battle-ready.iwram']
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
lessons={x['id']:x for x in registry['lessons']}
counts={x['id']:x['totalCount'] for x in registry['races']}
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
m=ARM(rom,iw);checks=collections.Counter();cases=[];failure=None;case=None
OUT=path.parent/('integrated-learning-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));OUT.mkdir()

def check(label,a,b):
    assert a==b,(case,label,a,b)
    checks[label]+=1

def address(race,index):
    return 0x02001b40+index-144 if race==1 and index>=144 else UNIT+0x40+index

def value(race,index):return m.read(address(race,index),1)[0]

def award(index,gain,residue):
    # Original results loop's single-lesson body, through mastery notification.
    # All counter, cost and AP decisions execute from installed native code.
    stack=STACK+residue
    m.put(0x03002810,struct.pack('<I',0x02022000));m.put(0x02022000,bytes(0x800))
    m.put(0x0201f514,bytes([gain]));m.put(stack,bytes(0x80))
    m.put(stack+0x64,struct.pack('<I',index))
    for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,
                UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11):
        m.u.reg_write(reg,0)
    m.u.reg_write(UC_ARM_REG_R8,UNIT);m.u.reg_write(UC_ARM_REG_R6,index)
    m.u.reg_write(UC_ARM_REG_SP,stack);m.u.reg_write(UC_ARM_REG_LR,RETURN|1)
    m.u.emu_start(0x08049033,0x080490a6,count=50000)
    check('native-results-continuation',m.u.reg_read(UC_ARM_REG_PC),0x080490a6)
    check('native-results-stack',m.u.reg_read(UC_ARM_REG_SP),stack)
    return m.read(0x02022696,1)[0]

try:
 for item in registry['items']:
  for teaching in item['teaching']:
   ident,race,index,job=item['romItemId'],teaching['race'],teaching['abilityIndex'],teaching['jobId']
   lesson=lessons[teaching['lesson']];cost=lesson['ap']//10
   assert 1<cost<128 and lesson['ap']%10==0
   for residue in (0,4):
    case=(ident,teaching['lesson'],race,job,residue)
    m.put(0x02000000,bytes(0x40000));m.put(0x03000000,iw)
    m.put(0x02001e70,b'FFTAEXP1\x01');m.fixture(job)
    m.put(UNIT+0x34,bytes([counts[race]]));m.put(UNIT+0x35,bytes([job]))
    m.put(0x02001940+ident,b'\1')
    check('teacher-legal-on-job',m.call(0x080cb48c,UNIT,ident,0)&1,0)
    check('initial-unlearned',value(race,index),0)
    m.call(0x080caf78,UNIT,ident,0,stack=STACK+residue)
    check('native-equipped-item',int.from_bytes(m.read(UNIT+0x2a,2),'little'),ident)
    check('equipped-lesson-usable',value(race,index),128)
    # Unearned lesson loses usability when its teaching equipment is removed.
    m.call(0x080caf78,UNIT,0,0,stack=STACK+residue)
    check('unmastered-removed-lesson',value(race,index),0)
    m.call(0x080caf78,UNIT,ident,0,stack=STACK+residue)
    check('partial-award-no-mastery-notification',award(index,cost-1,residue),0)
    check('earned-partial-AP',value(race,index),128|cost-1)
    m.call(0x080caf78,UNIT,0,0,stack=STACK+residue)
    check('partial-progress-survives-removal',value(race,index),cost-1)
    m.call(0x080caf78,UNIT,ident,0,stack=STACK+residue)
    check('mastery-notifies-correct-racial-index',award(index,1,residue),index)
    check('earned-mastery-byte',value(race,index),128|cost)
    m.call(0x080caf78,UNIT,0,0,stack=STACK+residue)
    check('mastered-usability-survives-removal',value(race,index),128|cost)
    check('mastered-award-no-duplicate-notification',award(index,5,residue),0)
    check('mastered-AP-does-not-overflow',value(race,index),128|cost)
    check('teaching-does-not-consume-inventory',m.read(0x02001940+ident,1),b'\1')
    check('learning-retains-job-race',m.read(UNIT+6,2),bytes([race,job]))
    cases.append(dict(item=ident,lesson=lesson['id'],race=race,job=job,index=index,cost=cost*10,stackResidue=residue))
 check('all-teaching-weapons-covered',len({x['item'] for x in cases}),85)
 check('all-lessons-covered',len({x['lesson'] for x in cases}),129)
 expected={(x['id'],o['race'],o['abilityIndex']) for x in registry['lessons'] for o in x['owners']}
 actual={(x['lesson'],x['race'],x['index']) for x in cases}
 check('every-racial-lesson-covered',actual,expected)
except BaseException as error:
 failure=repr(error);(OUT/'failure.ram').write_bytes(m.read(0x02000000,0x40000))
report=dict(passed=failure is None,romSha1=meta['romSha1'],registrySha1=sha((ROOT/'build/expansion/registry.json').read_bytes()),
            fixture=proof['outputs'],assertions=sum(checks.values()),checks=dict(checks),cases=cases,failure=failure,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],assertions=report['assertions'],cases=len(cases),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
