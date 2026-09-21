"""Real ARM entrypoints for AP flags, explicit job lists and per-unit gates.

Direct consumers and copy lifetimes have their own independent tests.
"""
import hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/probes'
ROM=(OUT/'ability-core.gba').read_bytes()
BASE=(OUT/'content-inventory.gba').read_bytes()
M=json.loads((OUT/'ability-core.json').read_text())
R=json.loads((ROOT/'build/expansion/registry.json').read_text())
assert hashlib.sha1(ROM).hexdigest()==M['romSha1']
assert hashlib.sha1(BASE).hexdigest()==M['baseSha1']
SYMBOLS={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
CASES={}
def check(value,label,group):
    assert value,label
    CASES[group]=CASES.get(group,0)+1
class ARM:
    def __init__(self,rom):
        self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for a,n in ((0x08000000,0x2000000),(0x02000000,0x40000),(0x03000000,0x8000)):self.u.mem_map(a,n)
        self.u.mem_write(0x08000000,rom)
    def call(self,pc,*args,residue=0):
        if isinstance(pc,str):pc=SYMBOLS[pc]
        u=self.u
        for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,val)
        regs=(UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)
        for i,reg in enumerate(regs):u.reg_write(reg,0x77cc0000+i)
        u.reg_write(UC_ARM_REG_SP,0x03007000+residue);u.reg_write(UC_ARM_REG_LR,0x03000001)
        u.emu_start(pc|1,0x03000000,count=300000)
        assert u.reg_read(UC_ARM_REG_PC)==0x03000000,(hex(pc),args,'return')
        assert u.reg_read(UC_ARM_REG_SP)==0x03007000+residue,(hex(pc),'stack')
        assert all(u.reg_read(reg)==0x77cc0000+i for i,reg in enumerate(regs)),(hex(pc),'callee registers')
        return u.reg_read(UC_ARM_REG_R0)
    def setup(self,race=1,slot=0):
        self.u.mem_write(0x02000000,bytes(0x1f1c))
        self.u.mem_write(0x02001e70,b'FFTAEXP1\x01')
        unit=0x02000080+slot*264
        self.u.mem_write(unit+4,bytes((1,2,race,2)))
        return unit
    def address(self,unit,index):
        return 0x02001b40+((unit-0x02000080)//264)*34+index-144 if index>=144 else unit+0x40+index
    def ap(self,unit,index,value):self.u.mem_write(self.address(unit,index),bytes((value,)))
    def record(self,race,index):
        pointers=struct.unpack('<I',self.u.mem_read(0x080257e8,4))[0]
        table=struct.unpack('<I',self.u.mem_read(pointers+race*4,4))[0]
        return bytes(self.u.mem_read(table+index*8,8))

a,b=ARM(ROM),ARM(BASE)
unit=a.setup();b.setup()
for index in range(142):
    for value in range(256):
        a.ap(unit,index,value);b.ap(unit,index,value)
        check(a.call(0x080cd560,unit,index)==b.call(0x080cd560,unit,index),f'native availability {index}/{value}','native availability')
for residue in (0,4):
    for slot in range(24):
        unit=a.setup(slot=slot)
        for index in range(144,178):
            for value in (0,1,99,100,127,128,129,228,255):
                a.ap(unit,index,value)
                before=bytes(a.u.mem_read(0x02000000,0x1f1c))
                check(a.call(0x080cd560,unit,index,residue=residue)==int(bool(value&128)),f'extended availability {slot}/{index}/{value}','extended availability')
                a.call(0x080cd544,unit,index,residue=residue)
                expected=bytearray(before);expected[a.address(unit,index)-0x02000000]=value|128
                check(bytes(a.u.mem_read(0x02000000,0x1f1c))==expected,f'grant isolation {slot}/{index}/{value}','grant isolation')
for race in range(1,6):
    unit=a.setup(race)
    for index in (142,143,178,255):
        check(a.call('ffta_ap_address',unit,index)==0,f'reserved index {race}/{index}','invalid ownership')
    for index in range(144,178):
        if race!=1:check(a.call('ffta_ap_address',unit,index)==0,'nonhuman sidecar','invalid ownership')
unit=a.setup()
a.u.mem_write(0x02024000,bytes(a.u.mem_read(unit,264)))
check(a.call('ffta_ap_address',0x02024000,144)==0,'Unbound preview must not alias a roster slot','invalid ownership')
a.u.mem_write(0x02001e70,bytes(9))
check(a.call('ffta_ap_address',unit,144)==0,'Unconverted save must not interpret inventory as AP','invalid ownership')
check(a.call(0x080cd560,0,144)==0,'Null ability','invalid ownership')

# Unchanged original mastery uses the installed native function as oracle.
for race in range(1,6):
    for pattern in (0,0x80,0xe4,0xff):
        unit=a.setup(race);b.setup(race)
        for cpu in (a,b):cpu.u.mem_write(unit+0x40,bytes((pattern,))*142)
        # Native CD2C4 itself is undefined for fallback-only NPC aliases
        # (e.g. job80 loops with fallback80). Exercise selectable jobs.
        for job in range(2,44):
            if job in (2,16):continue
            check(a.call(0x080cd2c4,unit,job)==b.call(0x080cd2c4,unit,job),f'native mastery {race}/{job}/{pattern}','native mastery')

for job in R['jobs']:
    unit=a.setup(job['race'])
    expected=[]
    if job.get('existing'):
        first=b.call(0x080c8570,job['id'],job['id'],0x25);last=b.call(0x080c8570,job['id'],job['id'],0x26)
        expected=list(range(first,last+1))
    expected += [o['abilityIndex'] for lesson in R['lessons'] for o in lesson['owners'] if o['jobId']==job['id']]
    check(a.call('ffta_job_lesson_count',job['id'])==len(expected),job['name'],'job lists')
    actual=[a.call('ffta_job_lesson_at',job['id'],i) for i in range(len(expected))]
    check(actual==expected,f'exact list {job["id"]}','job lists')
    check(a.call('ffta_job_lesson_at',job['id'],len(expected))==0,'list bound','job lists')
    for index in expected:
        row=a.record(job['race'],index)
        if row[6]:a.ap(unit,index,row[7])
    check(a.call(0x080cd2c4,unit,job['id'])==1,'all lessons mastered','expanded mastery')
    for index in expected:
        row=a.record(job['race'],index)
        if row[6] and row[7]:
            a.ap(unit,index,128|row[7]-1)
            check(a.call(0x080cd2c4,unit,job['id'])==0,f'equipped not mastered {job["id"]}/{index}','expanded mastery')
            a.ap(unit,index,row[7])

for job in R['jobs']:
    if job.get('existing'):continue
    unit=a.setup(job['race'])
    check(a.call('ffta_new_job_eligible',unit,job['id'])==int(not job['prerequisites']),'starter gate','job gates')
    chosen=[]
    for prerequisite in job['prerequisites']:
        ids=[]
        for i in range(a.call('ffta_job_lesson_count',prerequisite['jobId'])):
            index=a.call('ffta_job_lesson_at',prerequisite['jobId'],i)
            row=a.record(job['race'],index)
            if row[6] in (1,4) and row[7]:ids.append((index,row[7]))
        chosen+=ids[:prerequisite['actions']]
    for index,cost in chosen:a.ap(unit,index,128)
    check(a.call('ffta_new_job_eligible',unit,job['id'])==int(not chosen),'equipment cannot satisfy prerequisites','job gates')
    for index,cost in chosen:a.ap(unit,index,cost)
    check(a.call('ffta_new_job_eligible',unit,job['id'])==1,'earned prerequisites','job gates')
    for index,cost in chosen:
        a.ap(unit,index,cost-1)
        check(a.call('ffta_new_job_eligible',unit,job['id'])==0,'each prerequisite necessary','job gates')
        a.ap(unit,index,cost)
    for race in range(1,6):
        if race==job['race']:continue
        a.u.mem_write(unit+6,bytes((race,)))
        check(a.call('ffta_new_job_eligible',unit,job['id'])==0,'racial gate','job gates')

report={'romSha1':M['romSha1'],'cases':CASES,'total':sum(CASES.values()),'passed':True,'limitations':['Remaining direct AP consumers and count normalization need integration','Unknown transient owners are deliberately rejected','Battle ability effects are not enabled']}
(OUT/'ability-core-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
