"""Deterministic native ARM tests for clan discovery and per-unit eligibility."""
import ast, ctypes as C, hashlib, importlib.util, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,RETURN,STACK=0x02000080,0x08000100,0x03007000
LIST,MENU=0x02007040,0x02008000
meta=json.loads(Path(json.loads((ROOT/'build/expansion/job-visibility/current.json').read_text())['manifest']).read_text())
out=Path(meta['path']).parent;rom=Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
parent=json.loads(Path(meta['jobVisibility']['parent']).read_text());base=Path(parent['path']).read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')]
for n in nodes:
    for c in ast.walk(n):
        if isinstance(c,ast.Constant) and c.value==50000:c.value=1500000
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<native-harness>','exec'))
iw=iwram_from_boot();native,changed=ARM(base,iw),ARM(rom,iw)
initial=next(p['offset']+0x08000000 for p in meta['jobVisibility']['patches'] if p['name']=='ffta_wheel_initial')
turn=next(p['offset']+0x08000000 for p in meta['jobVisibility']['patches'] if p['name']=='ffta_wheel_turn')
checks=[];cases=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def member(m,slot,race,job,master=False,active=True):
    raw=bytearray(264);raw[4]=1 if active else 0;raw[5]=job;raw[6]=race;raw[7]=job
    raw[0x34]=[0,178,111,124,118,116][race]
    if master:raw[0x40:0x40+min(raw[0x34],142)]=bytes([100])*min(raw[0x34],142)
    m.put(UNIT+264*slot,raw)
    if race==1:m.put(0x02001b40+34*slot,bytes([100 if master else 0])*34)
def setup(m,race=1,job=2):
    m.put(0x02000000,bytes(0x40000));m.put(0x02001e70,b'FFTAEXP1\x01\x03')
    member(m,0,race,job);m.put(LIST-16,b'\xa5'*44)
    m.put(0x03002818,struct.pack('<I',MENU));m.put(MENU+0x1d0c,struct.pack('<I',UNIT))
def wheel(m,residue=0):
    n=m.call(initial,UNIT,LIST,stack=STACK+residue)
    check(0<n<=12,'bounded wheel')
    check(m.read(LIST-16,16)==b'\xa5'*16 and m.read(LIST+12,16)==b'\xa5'*16,'12-byte array guards')
    return list(m.read(LIST,n))
def discovery(m):return int.from_bytes(m.read(0x02001e7a,2),'little')
try:
    for race,job in [(1,2),(2,13),(3,22),(4,28),(5,36)]:
        for residue in (0,4):
            for m in (native,changed):setup(m,race,job)
            expected=native.call(0x080c8a24,UNIT,LIST)
            old=sorted(native.read(LIST,expected),key=lambda x:x&127)
            base_job={3:120,5:122}.get(race)
            check(wheel(changed,residue)==old+([base_job|128] if base_job else []),f'race {race} native jobs plus eligible base Chemist only')
            check(discovery(changed)==(1<<(base_job-116) if base_job else 0),'only prerequisite-free Chemist discovered from blank clan')
    races=[1,1,2,2,3,3,5,5,4,4];defaults={1:2,2:13,3:22,4:28,5:36}
    for job,race in zip(range(116,126),races):
        for mode in ('qualified','current','learned','equipment-only','inactive','other-race'):
            setup(changed,race,defaults[race]);other=2 if race!=2 else 3
            member(changed,23,other if mode=='other-race' else race,job if mode=='current' else defaults[race],mode in ('qualified','inactive','other-race'),mode!='inactive')
            if mode in ('learned','equipment-only'):
                idx=changed.call(meta['jobVisibility']['helpers']['ffta_job_lesson_at']['address'],job,0)
                at=0x02001b40+23*34+idx-144 if race==1 and idx>=144 else UNIT+23*264+0x40+idx
                changed.put(at,bytes([1 if mode=='learned' else 128]))
            before=changed.read(0x02000000,0x1f20)
            page=wheel(changed);row=next((x for x in page if x&127==job),None)
            visible=job in (120,122) or mode in ('qualified','current','learned')
            check((row is not None)==visible,f'{job} visibility {mode}')
            if visible:check(row==(job|128 if job in (120,122) else job),f'{job} selected member eligibility independent of clan knowledge')
            check(bool(discovery(changed)&(1<<(job-116)))==visible,f'{job} remembered {mode}')
            after=changed.read(0x02000000,0x1f20)
            # Native wheel updates its original clan flags at 1F70+, not owned data.
            check(before[:0x1e7a]==after[:0x1e7a] and before[0x1e7c:]==after[0x1e7c:],'roster AP inventory Quin and preferences unchanged')
            if visible:
                changed.put(UNIT+23*264,bytes(264));changed.put(0x02001b40+23*34,bytes(34))
                check(any(x&127==job for x in wheel(changed)),'discovery remains after member leaves')
            cases.append(dict(job=job,mode=mode,rows=page))
        setup(changed,race,defaults[race]);member(changed,0,race,defaults[race],True)
        page=wheel(changed)
        # Human expanded jobs are on page two; test actual paging below.
        if race!=1:check(job|128 in page,f'{job} personally qualified bright')
    # Actual installed paging helper, with graphics disposal/sound stubbed only.
    for addr in (0x0804c7a0,0x08141540):
        changed.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)),begin=addr,end=addr)
    setup(changed);member(changed,0,1,2,True)
    first=wheel(changed);check([x&127 for x in first]==list(range(2,9)),'Human first page')
    changed.put(MENU+0x1278,bytes(first));changed.put(MENU+0x1270,struct.pack('<I',len(first)))
    changed.put(0x03000002,struct.pack('<H',0x100))
    n=changed.call(turn);second=list(changed.read(MENU+0x1278,n))
    check([x&127 for x in second]==[9,10,11,12,116,117] and all(x&128 for x in second),'Human second page remains bright and complete')
    changed.put(MENU+0x1270,struct.pack('<I',n));n=changed.call(turn)
    check(list(changed.read(MENU+0x1278,n))==first,'page roundtrip')
    for identity in (9,10,94):
        setup(changed);changed.put(UNIT+4,bytes([identity]))
        check(changed.call(initial,UNIT,LIST)==0,'native story restriction '+str(identity))
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,cases=cases)
except Exception as error:
    report=dict(status='failed',romSha1=meta['romSha1'],checks=checks,cases=cases,error=str(error))
    raise
finally:
    (out/'native-test.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],report=str(out/'native-test.json'),checks=len(checks),romSha1=meta['romSha1'])))
