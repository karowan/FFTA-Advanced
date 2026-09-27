"""Regression: all retained callers must use the current status-record stride.

The original failure interpreted movement coordinates as custom buffs through
older import veneers. Exercise all 36 canonical slots and every authenticated
accessor entry, then compare status queries before/after a movement-only ledger.
Uses the declared cold fixture on a clone, never a player's save.
"""
import ast,hashlib,json,struct,sys
from pathlib import Path
from chemist_candidate import candidate
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
meta=candidate();rom=Path(meta['path']).read_bytes();base=Path(meta['path']).parent
code=json.loads((ROOT/'build/expansion/chemist-progressions/code/manifest.json').read_text())
state=(base/'fixture/battle-ready.state').read_bytes()
# Use the existing harness only to expose the captured RAM regions, no inputs.
import ctypes as C,runpy
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
with E(Path(meta['path'])) as e:
    e.load(base/'fixture/battle-ready.state')
    ram=e.memory();iw=C.string_at(*e.maps[0x03000000])
m=ARM(rom,iw);m.put(0x02000000,ram)
checks=[]
for i in range(36):
    unit=0x02000080+i*264 if i<24 else 0x02002fc4+(i-24)*264
    expected=0x0203f410+i*27
    m.call(meta['symbols']['ffta_job_reset'])
    for entry in code['installedEntries']['ffta_job_state']:
        assert m.call(entry,unit)==expected,(i,hex(entry))
    before=[m.call(0x0809da0c,unit,k) for k in range(1,60)]
    m.put(expected+12,bytes((9,8,25)));m.put(expected+19,b'\xc0')
    after=[m.call(0x0809da0c,unit,k) for k in range(1,60)]
    assert before==after,('Movement became a status',i,before,after)
    # A real buff must remain visible, including through old grant/query code.
    m.put(unit+0x18,b'\x30\x00');m.put(unit+0xe8,b'\0');m.put(expected,b'\x02')
    assert m.call(0x0809da0c,unit,28)==28,('Real Last Resort missing',i)
    checks.append(dict(slot=i,accessors=len(code['installedEntries']['ffta_job_state']),movementOnly=True,realBuff=True))
m.call(meta['symbols']['ffta_job_reset'])
fast=[]
entry=meta['symbols']['ffta_geo_field_fast']&~1
hook=m.u.hook_add(UC_HOOK_CODE,lambda uc,address,size,user:fast.append(address),begin=entry,end=entry)
for entry in code['installedEntries']['ffta_geo_field_at']:
    prior=len(fast)
    assert m.call(entry,0x020005a8,0,13,1)==0
    assert len(fast)==prior+1,('Canonical field shortcut lost',hex(entry))
m.u.hook_del(hook)
checks.append(dict(canonicalFieldEntries=len(fast),fastDispatch=True))
out=base/'status-records';out.mkdir(exist_ok=True)
report=out/'report.json';report.write_text(json.dumps(dict(passed=True,romSha1=meta['romSha1'],fixtureSha256=hashlib.sha256(state).hexdigest(),checks=checks),indent=2)+'\n')
print(json.dumps(dict(passed=True,report=str(report))))
