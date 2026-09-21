"""Bounded native menu ID lifetime checks using retained, authenticated UI RAM.

Runs native helpers in isolated ARM memory, never changes a player save.
The regular menu test separately proves actual visible display equivalence.
"""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/class-resources/current.json').read_text())
captures=[]
candidate_bytes=Path(meta['path']).read_bytes()
def compatible_capture(digest):
    if digest==meta['romSha1']:return True
    old_path=ROOT/'build/art/class-resources'/digest/'manifest.json'
    if not old_path.exists():return False
    old=json.loads(old_path.read_text());before=Path(old['path']).read_bytes()
    if hashlib.sha1(before).hexdigest()!=digest:return False
    # The retained racial header capture never constructs the common widget.
    # Its RAM remains applicable when only the widget's mode-change read and
    # field literal change; do not generalize this to arbitrary ROM changes.
    allowed=set(range(0x29cf8,0x29cfa))|set(range(0x29d1c,0x29d20))
    return len(before)==len(candidate_bytes) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,candidate_bytes)))
for p in sorted((ROOT/'build/art/class-resources/menus').glob('*/report.json')):
    d=json.loads(p.read_text())
    if d['status']=='passed' and compatible_capture(d['romSha1']):captures.append((p.parent,d))
assert captures,'Run test-native-class-menus for this candidate first'
capture,evidence=captures[-1]
out=ROOT/'build/art/class-resources/width-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True);checks=[];inputs=[];sources={}

def check(ok,label):
    assert ok,label
    checks.append(label)

def half(a,p):return struct.unpack('<H',a.read(p,2))[0]

def machine(kind):
    path=meta['path'] if kind=='private' else meta['source']
    rom=Path(path).read_bytes();digest=meta['romSha1'] if kind=='private' else meta['baseRomSha1']
    check(hashlib.sha1(rom).hexdigest()==digest,kind+' authenticated ROM')
    stem=capture/(kind+'-slot2-wheel')
    ram=stem.with_suffix('.ram').read_bytes()
    iw=stem.with_suffix('.iwram').read_bytes()
    sources[kind]=dict(ramSha256=sha(ram),iwramSha256=sha(iw))
    check(sha(ram[0x80:0x1e70])==evidence['observations'][kind]['2']['wheel']['owned'],kind+' retained owned RAM')
    a=ARM(rom,iw);a.put(0x02000000,ram)
    for base,size in [(0x04000000,0x10000),(0x05000000,0x1000),(0x06000000,0x20000),(0x07000000,0x1000)]:a.u.mem_map(base,size)
    return a

try:
    for kind in ('original','private'):
        a=machine(kind);task=a.word(0x03002818);manager=a.word(task+0x444)
        for job in meta['jobs']:
            a.fixture(job['job'])
            resource=job['resources'][0] if kind=='private' else job['original'][0]
            for mode in (0,4,0):
                inputs.append([kind,'header-update',job['job'],mode])
                a.call(0x080717cc,UNIT,mode,0)
                actor=a.word(task+0x448)
                check(half(a,actor+6)==resource,f'{kind}/{job["job"]}/{mode} header actual actor ID')
                check(a.read(task+0x434,1)==bytes([resource&255]),'header legacy byte retained')
                if kind=='private':check(half(a,manager+16)==resource,'header owned manager ID survives replacement')
                # Execute the native state2 rebuild, stopping immediately after
                # its create call. Rendering itself is covered by the UI run.
                a.put(task+0x43e,b'\x02')
                saved=RETURN;RETURN=0x080889fa
                a.u.reg_write(UC_ARM_REG_R0,0);a.u.reg_write(UC_ARM_REG_R1,task+0x43e)
                a.u.reg_write(UC_ARM_REG_SP,STACK);a.u.reg_write(UC_ARM_REG_LR,saved|1)
                a.u.emu_start(0x080888b5,RETURN,count=50000)
                check(a.u.reg_read(UC_ARM_REG_PC)==RETURN,'native header state2 reaches replacement result')
                actor=a.u.reg_read(UC_ARM_REG_R0)
                check(half(a,actor+6)==resource,'native header state2 retains complete ID')
                # Finish its pointer store before returning to an isolated next
                # call; the remainder is drawing, not resource lifetime.
                a.put(task+0x448,struct.pack('<I',actor));RETURN=saved
                # State3 recreates again when its requested mode changes.
                a.put(task+0x43c,bytes([4,0,3]))
                a.u.reg_write(UC_ARM_REG_R0,0);a.u.reg_write(UC_ARM_REG_R1,task+0x43e)
                a.u.reg_write(UC_ARM_REG_SP,STACK);a.u.reg_write(UC_ARM_REG_LR,RETURN|1)
                a.u.emu_start(0x080888b5,0x08088b02,count=50000)
                check(a.u.reg_read(UC_ARM_REG_PC)==0x08088b02,'native header state3 reaches replacement result')
                actor=a.u.reg_read(UC_ARM_REG_R0)
                check(half(a,actor+6)==resource and half(a,actor+8)==4,'native header state3 retains complete ID and requested mode')
                a.put(task+0x448,struct.pack('<I',actor))
        check(a.word(task+0x444)==manager,kind+' repeated updates retain manager ownership')
    # Generic widget is independently owned. Use its real constructor and
    # native allocation/actor helpers, with the same argument layout as574ce.
    for resource in (4,256,274,275):
        a=machine('private')
        # The real widget is embedded in its owning menu, not allocated from
        # the header's small graphics heap. Supply a standalone owner buffer
        # for this helper-level test; no claim about whole-menu RAM capacity.
        widget=0x10000000;a.u.mem_map(widget,0x2000)
        a.put(STACK,struct.pack('<6I',0,resource,0,1,1,0))
        a.call(0x08029864,widget,2,2,7)
        check(half(a,widget+0x1080)==resource,'generic real constructor full ID')
        fields=a.read(widget+0x1084,8)
        # Execute lifecycle entry after the UI transition-readiness gate. This
        # exercises actual arena creation and actor setup without faking a
        # running display controller or depending on rendering timing.
        a.u.reg_write(UC_ARM_REG_R5,widget);a.u.reg_write(UC_ARM_REG_SP,STACK-0x34)
        a.u.emu_start(0x080299a7,0x08029a0a,count=50000)
        check(a.u.reg_read(UC_ARM_REG_PC)==0x08029a0a,'generic native lifecycle reaches created actor')
        check(half(a,widget+0x1080)==resource,'generic ID survives allocator initialization')
        check(half(a,widget+0x8a)==1018,'generic allocator excludes reserved tail')
        check(a.read(widget+0x1084,8)==fields,'generic adjacent fields survive allocation')
        check(half(a,a.word(widget+0x7c)+6)==resource,'generic actual actor receives full ID')
        for target in (274,256,4):
            inputs.append(['generic-update',resource,target])
            a.put(STACK,struct.pack('<3I',1,1,0))
            a.call(0x08029c34,widget,0,target,0)
            check(half(a,widget+0x1080)==target,'generic update full stored ID')
            check(half(a,a.word(widget+0x7c)+6)==target,'generic update full actual actor ID')
            after=a.read(widget+0x1084,8)
            check(after[:1]+after[2:]==fields[:1]+fields[2:],'generic update adjacent native fields match constructor')
            for mode in (24,0):
                inputs.append(['generic-mode',target,mode])
                a.call(0x08029cd8,widget,mode,0)
                actor=a.word(widget+0x7c)
                check(half(a,actor+6)==target and half(a,actor+8)==mode,'generic mode-change actual actor retains ID and requested mode')
                check(half(a,widget+0x1080)==target,'generic mode-change preserves stored full ID')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,capture=str(capture),captureRomSha1=evidence['romSha1'],sources=sources,
        scope='Native header direct replacement and state2/state3 recreation across ten generic jobs. Generic widget constructor, post-readiness allocation and native update with IDs4/256/274/275, allocation extent and adjacent fields. Partial lifecycle entry excludes UI transition timing; no new display, teardown, graphics rendering or final-art acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
