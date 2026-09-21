"""Bounded retained-state diagnosis of the all-ten entry timeout.

Observe no-input and one-confirm branches without modifying the fixture, ROM,
unit records or game state. This is diagnostic evidence, not capacity acceptance.
"""
import argparse,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator
from mgba_instruction_trace import InstructionTrace

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=ROOT/'build/art/all-class-capacity/20260919T065417.931001Z')
source=parser.parse_args().source
report=json.loads((source/'failed.json').read_text())
rom=(source/'fixture.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==report['fixtureRomSha1']
pins={name:sha((source/name).read_bytes()) for name in ('fixture.gba','failed.state','failed.ram','failed.iwram','failed.json')}
out=ROOT/'build/art/capacity-entry'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
rows=[];e=None
try:
    for case,key in [('idle',0),('confirm',256)]:
        e=E(source/'fixture.gba');e.load(source/'failed.state')
        assert e.memory()==(source/'failed.ram').read_bytes()
        assert C.string_at(*e.maps[0x03000000])==(source/'failed.iwram').read_bytes()
        observer=InstructionTrace(e,{})
        wrappers=from_emulator(rom,e)
        samples=[]
        for frame in range(601):
            if frame:e.run(1,key if frame<=8 else 0)
            if frame%60==0:
                r=e.memory();w=lambda p:struct.unpack_from('<I',r,p)[0]
                controller=w(0xf438)-0x02000000
                samples.append(dict(frame=frame,menu=menus['menu_visible'](e),pc=observer.registers[15],
                    controller=controller,controllerBytes=r[controller:controller+96].hex(),
                    actors={hex(u):dict(job=r[u+7],position=list(struct.unpack_from('<3H',r,p+8)),
                        wrapper=r[p:p+104].hex()) for u,p in wrappers.items()},ramSha256=sha(r)))
                if e.frame:e.screenshot(out/(case+'-'+str(frame)+'.png'))
        e.save(out/(case+'.state'))
        for ext,address in [('ram',0x02000000),('iwram',0x03000000)]:
            (out/(case+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
        rows.append(dict(case=case,input=[8,key,592],samples=samples));e.close();e=None
    assert all(sha((source/n).read_bytes())==s for n,s in pins.items())
    result=dict(status='passed',diagnosticOnly=True,source=str(source),pins=pins,records=rows,scope=__doc__)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',report=str(out/'report.json'),menus={r['case']:[s['frame'] for s in r['samples'] if s['menu']] for r in rows})))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),pins=pins,records=rows),indent=2)+'\n',encoding='utf-8')
    raise
finally:
    if e:e.close()
