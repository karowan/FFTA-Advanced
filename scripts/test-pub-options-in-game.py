"""All four reordered pub options from a real paid dispatch checkpoint.

Native action mapping, real menu inputs, cancel/leave and ownership checks.
No new RAM inputs or altered game ROM are needed for these player flows.
"""
import ast,ctypes,datetime,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_INSN_INVALID
from unicorn.arm_const import *
sha=lambda b:hashlib.sha1(b).hexdigest()
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']).read_bytes();assert sha(rom)==meta['romSha1']
base=pathlib.Path(meta['path']).parent
prior_path=pathlib.Path(json.loads((base/'quest-recovery-cycle-latest.json').read_text())['report'])
prior=json.loads(prior_path.read_text());assert prior['passed'] and prior['romSha1']==meta['romSha1']
anchor=next(r for r in prior['observations'] if r['label']=='paid1');folder=pathlib.Path(anchor['directory'])
for ext,key in [('state','stateSha1'),('ram','ramSha1'),('srm','sramSha1')]:assert sha((folder/('paid1.'+ext)).read_bytes())==anchor[key]
OUT=base/('pub-options-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));OUT.mkdir()
ROM=OUT/'fixture.gba';ROM.write_bytes(rom)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
RETURN,STACK=0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
checks=[];cases=[];inputs=[];e=None;failure=None
def check(ok,label):assert ok,label;checks.append(label)
def word(b,p):return struct.unpack_from('<I',b,p)[0]
def tap(k,wait=180):inputs.append([8,k,wait]);e.run(8,k);e.run(wait)
def capture(label):
    e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(e.memory())
def owned(b):return [b[0x80:0x1f40],b[0x1f64:0x1f68],b[0x2b08:0x2c10]]
try:
    for index,name,mapped in [(0,'missions',1),(1,'rumors',0),(2,'quit-mission',2),(3,'leave',3)]:
        e=Emulator(ROM);e.load(folder/'paid1.state');e.set_memory(0,(folder/'paid1.srm').read_bytes(),0);e.run(1)
        before=e.memory();capture(name+'-world')
        # Execute the installed dispatch prefix up to the unchanged original
        # handler. This observes the actual R4 argument after reordering.
        m=ARM(rom,ctypes.string_at(*e.maps[0x03000000]))
        def legacy_bl(u,data):
            # ARM7 standalone BL suffix; model only this CPU instruction.
            pc=u.reg_read(UC_ARM_REG_PC)
            if bytes(u.mem_read(pc,2))!=b'\x00\xf8':return False
            target=u.reg_read(UC_ARM_REG_LR);u.reg_write(UC_ARM_REG_LR,(pc+2)|1);u.reg_write(UC_ARM_REG_PC,target|1);return True
        m.u.hook_add(UC_HOOK_INSN_INVALID,legacy_bl)
        m.u.reg_write(UC_ARM_REG_SP,0x03007000);m.u.reg_write(UC_ARM_REG_R0,index)
        m.u.emu_start(0x0805d23d,0x0805d248,count=1000)
        check(m.u.reg_read(UC_ARM_REG_PC)==0x0805d248,name+': original handler reached')
        check(m.u.reg_read(UC_ARM_REG_R4)==mapped,name+': exact native option mapping')
        tap(256,240);tap(256,180)
        for _ in range(index):tap(32,60)
        capture(name+'-selected');tap(256,240);capture(name+'-opened')
        if index==0:
            tap(256,120);ram=e.memory();ctx=word(ram,0xf448)-0x02000000
            check(0<=ctx<0x3e000,'Missions opens native pub context')
            count=ram[ctx+0x11a9];pointers=[word(ram,ctx+0x11ac+i*4) for i in range(count)]
            check(0<count<=16 and all(0x020021c8<=p<0x020025c8 for p in pointers),'Missions opens bounded actual offer list')
            capture(name+'-list')
        if index==3:tap(256,240)
        else:
            for _ in range(4):tap(1,180)
        capture(name+'-finished');after=e.memory()
        check(owned(after)==owned(before),name+': roster/AP/equipment/gil/quest items unchanged')
        check(struct.unpack_from('<H',after,0x2a6)[0]==407 and struct.unpack_from('<H',after,0x2b8)[0]&4,
              name+': accepted dispatch remains with Ford')
        cases.append(dict(option=index,name=name,nativeAction=mapped,opened=str(OUT/(name+'-opened.png'))))
        e.close();e=None
except Exception as exc:
    failure=repr(exc)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close()
report=dict(passed=failure is None,romSha1=meta['romSha1'],sourceReport=str(prior_path),sourceReportSha1=sha(prior_path.read_bytes()),
            anchor=anchor,checks=checks,assertions=len(checks),cases=cases,inputs=inputs,failure=failure,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],assertions=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
