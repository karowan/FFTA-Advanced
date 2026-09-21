"""Original ending montage, connected scenes, credits and clear-save transition.

Declared entry: the next native queued scene is replaced once by scene101
from a loaded disposable ordinary
save. Original scene scripts, their transitions and the ending-save opcode run
unchanged. This verifies the ending scene chain, not the preceding final battles
or natural campaign eligibility for its initial scene. No result is injected.
"""
import ast
import datetime
import hashlib
import json
import pathlib
import runpy
import struct
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
sha = lambda data: hashlib.sha1(data).hexdigest()
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM = pathlib.Path(meta['path']); image = ROM.read_bytes()
assert sha(image) == meta['romSha1']
clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert sha(clean) == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
NATIVE_RANGES = [(0x9afc,0x9bf8),(0xc9540,0xc9574),(0x121fb8,0x1223c8),
                 (0x1224b8,0x122598),(0x123a60,0x123b00),(0x12c170,0x12c530),
                 (0x3a7ee4,0x3a818e),(0x9a5d54,0x9a5df0),
                 (0x9b7024,0x9b83cc),(0xa19970+101*4,0xa19970+106*4)]
for a,b in NATIVE_RANGES:
    assert image[a:b] == clean[a:b], ('Native ending range changed',hex(a),hex(b))
producer = ROM.parent/'clear-save-20260917T091908.745148Z'
producer_report = (producer/'report.json').read_bytes()
assert sha(producer_report) == 'caeea467c2af4b202ece2a4716335720c5129e23'
prior = json.loads(producer_report)
assert prior['passed'] and prior['romSha1'] == meta['romSha1']
seed = (producer/'before-clear.sav').read_bytes()
assert sha(seed) == '5ba126d8cb06a7389ad8286fae9a73e884a380f2'
OUT = ROM.parent/('ending-scenes-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
LOG, COPY, SHIM = 0x3ff50, 0x09fff000, 0x09fff100
assert image[COPY-0x08000000:] == b'\xff'*(len(image)-(COPY-0x08000000))
probe_source = r'''
#include <stdint.h>
#define L ((volatile uint32_t *)0x0203ff50u)
unsigned scene_probe(unsigned scene) {
    if(L[0]==0x53434e45u) {
        L[0]=0; L[1]++; scene=101;
    }
    return ((unsigned (*)(unsigned))0x09fff001u)(scene);
}
unsigned script_observer(void *task,void *context,void *state) {
    unsigned scene=*(volatile uint16_t *)0x02002192u;
    if(scene!=L[2]) {
        L[2]=scene;
        if(L[3]<32) { L[10+L[3]]=scene; L[3]++; }
    }
    return ((unsigned (*)(void *,void *,void *))0x08121fb9u)(task,context,state);
}
unsigned credit_observer(void *context,const unsigned char *op) {
    L[4]++;
    return ((unsigned (*)(void *,const unsigned char *))0x08123a61u)(context,op);
}
unsigned transition_observer(void *context,const unsigned char *op) {
    if(op[1]==14) { L[5]++; L[6]=(unsigned)op; L[7]=(unsigned)context; }
    return ((unsigned (*)(void *,const unsigned char *))0x081224b9u)(context,op);
}
unsigned save_observer(void *task,void *context,void *state) {
    L[8]=*(uint16_t *)context; L[9]++;
    return ((unsigned (*)(void *,void *,void *))0x0812c2b9u)(task,context,state);
}
'''
(OUT/'probe.c').write_text(probe_source)
prefix = ROOT/'tools/arm-gnu/bin/arm-none-eabi-'
def command(tool,args):
    done = subprocess.run([str(prefix)+tool+'.exe',*map(str,args)],capture_output=True,text=True)
    (OUT/(tool+'.log')).write_text(done.stdout+done.stderr)
    assert done.returncode == 0, done.stderr
command('gcc',['-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-nostdlib',
               '-Wl,-Ttext=0x09fff100','-Wl,-e,scene_probe',OUT/'probe.c','-o',OUT/'probe.elf'])
command('objcopy',['-O','binary',OUT/'probe.elf',OUT/'probe.bin'])
command('nm',['--defined-only',OUT/'probe.elf'])
symbols = {line.split()[2]:int(line.split()[0],16) for line in (OUT/'nm.log').read_text().splitlines() if len(line.split())==3}
blob = (OUT/'probe.bin').read_bytes(); assert len(blob)<0xe00
patched = bytearray(image)
# The first four instructions are PC-independent. Replay the displaced
# prologue, then branch to its original continuation with the same registers.
assert image[0x9afc:0x9b04] == bytes.fromhex('f0b5474680b40004')
patched[COPY-0x08000000:COPY-0x08000000+16] = image[0x9afc:0x9b04]+struct.pack('<HHI',0x4b00,0x4718,0x08009b05)
patched[SHIM-0x08000000:SHIM-0x08000000+len(blob)] = blob
patched[0x9afc:0x9b04] = struct.pack('<HHI',0x4b00,0x4718,symbols['scene_probe']|1)
HOOKS = [(0x1223c4,0x08121fb9,'script_observer'),(0x12c52c,0x0812c2b9,'save_observer'),
         (0x3a7ee4+0x18*6+2,0x081224b9,'transition_observer'),
         (0x3a7ee4+0x62*6+2,0x08123a61,'credit_observer')]
for offset,expected,name in HOOKS:
    assert struct.unpack_from('<I',image,offset)[0]==expected
    struct.pack_into('<I',patched,offset,symbols[name]|1)
TEST_ROM = OUT/'fixture.gba'; TEST_ROM.write_bytes(patched)
E = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
tree = ast.parse((ROOT/'scripts/test-independent-save-slots.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owned'],
                       type_ignores=[]),'<owned profile>','exec'))
checks,inputs,captures = [],[],[]
failure,e = None,None
def check(value,label):
    assert value,label
    checks.append(label)
def observe():
    words=struct.unpack_from('<42I',e.memory(),LOG)
    return dict(fired=words[1],currentScene=words[2],scenes=list(words[10:10+min(words[3],32)]),
                creditOps=words[4],saveOpcodeCalls=words[5],saveOpcode=hex(words[6]),
                saveParent=hex(words[7]),saveState=words[8],saveTicks=words[9])
def capture(label):
    e.save(OUT/(label+'.state'))
    (OUT/(label+'.ram')).write_bytes(e.memory())
    (OUT/(label+'.sav')).write_bytes(e.memory(0))
    if e.frame is not None:e.screenshot(OUT/(label+'.png'))
    captures.append(dict(label=label,observation=observe(),files={p.name:sha(p.read_bytes()) for p in OUT.glob(label+'.*')}))
def tap(key,wait=120):
    inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
try:
    e=E(TEST_ROM);e.set_memory(0,seed,0);e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
    check(owned(e.memory())==prior['profiles']['0'],'Authenticated ordinary saved expansion profile loaded')
    check(not e.memory()[0x1f76]&64,'Ending input has no clear flag')
    capture('ordinary-input')
    e.set_memory(LOG,bytes(168));e.set_memory(LOG,struct.pack('<I',0x53434e45))
    seen=[]
    for step in range(900):
        tap(256)
        current=observe()
        if current['scenes']!=seen:
            seen=current['scenes'];capture('scene-change-'+str(len(captures)))
            print(json.dumps(dict(step=step,observation=current)),flush=True)
        if step==60:
            check(101 in seen,'Declared initial scene entered within7808frames')
        if current['saveOpcodeCalls']:
            capture('natural-save-opcode');break
    else:raise AssertionError('Original ending scenes did not reach the clear-save opcode within115200frames')
    check(current['fired']==1,'Exactly one declared scene entry')
    check(all(scene in seen for scene in (101,102,104,105)),'Original connected ending scenes101/102/104/105 execute')
    check(current['creditOps']>=18,'Original rolling-credit instructions execute')
    check(current['saveOpcodeCalls']==1 and current['saveOpcode']=='0x89b83ca','Scene105 reaches its actual ending-save opcode once')
    for step in range(20):
        tap(256,120)
        if e.memory(0)!=seed:break
    cleared=e.memory(0);capture('native-cleared')
    check(cleared!=seed,'Scene-owned ending task writes cleared flash')
    (OUT/'cleared.sav').write_bytes(cleared)
    # A fixed wait permits the original reset countdown. The established
    # title/Continue sequence verifies the original terminal branch.
    for _ in range(4):tap(256,120)
    e.run(3600);capture('returned-title')
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
    capture('continued-world')
    check(bool(e.memory()[0x1f76]&64),'Actual scene clear survives title/Continue')
    check(owned(e.memory())==prior['profiles']['0'],'Actual ending preserves saved full expansion profile')
    check(e.memory()[0x3f410:0x3f728]==bytes(792),'Ending reset retires transient expansion records')
    check(e.memory(0)==cleared,'Title/Continue leaves cleared flash unchanged')
    e.close();e=E(ROM);e.set_memory(0,cleared,0);e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
    capture('uninstrumented-cold')
    check(bool(e.memory()[0x1f76]&64) and owned(e.memory())==prior['profiles']['0'],
          'Unmodified candidate cold-loads actual ending save and profile')
    check((producer/'before-clear.sav').read_bytes()==seed,'Source save remains unchanged')
except BaseException as error:
    import traceback
    traceback.print_exc();failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close()
report=dict(passed=failure is None,romSha1=meta['romSha1'],instrumentedSha1=sha(patched),
            sourceSha1=sha(pathlib.Path(__file__).read_bytes()),scope=__doc__,nativeRanges=NATIVE_RANGES,
            producer=dict(report=str(producer/'report.json'),sha1=sha(producer_report),seedSha1=sha(seed)),
            helperHashes={name:sha((ROOT/name).read_bytes()) for name in ('scripts/emulator-test.py','scripts/test-independent-save-slots.py')},
            assertions=len(checks),checks=checks,inputs=inputs,captures=captures,failure=failure)
(OUT/'script.py').write_bytes(pathlib.Path(__file__).read_bytes())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
