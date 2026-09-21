"""Bounded observation of a retained native idle-layout reset during walking."""
import ctypes as C,datetime,json,hashlib,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import actors
from native_battle_wrappers import from_emulator
capture=ROOT/'build/art/explicit-walk/20260918T010505.036658Z'
assert sha((capture/'failed.json').read_bytes())=='4b887de402736ec935d363ec70987152e370e72ed2f347b43e8d2db3f44eb8ef'
assert sha((capture/'parent-failed.state').read_bytes())=='c9d9c82aea949bc324cdaa7ad7364a32d90d35490cfe0ee7bd9521205b6bc540'
meta=json.loads((ROOT/'build/art/generated-actions/mapped-walk-current.json').read_text())
rom=Path(meta['comparisonSource']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['comparisonRomSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(Path(meta['comparisonSource']))
out=ROOT/'build/art/walk-layout-transition'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
observations=[]
try:
    e.load(capture/'parent-failed.state');assert e.memory()==(capture/'parent-failed.ram').read_bytes()
    w=from_emulator(rom,e)[0x290]
    for frame in range(17):
        r=e.memory();body=struct.unpack_from('<I',r,w+0x44)[0]-0x02000000;v=C.string_at(*e.maps[0x06000000])
        parsed=[a for a in actors(rom,r,v) if a['address']==body]
        row=dict(frame=frame,body=body,raw=r[body:body+72].hex(),parsed=parsed,vramSha256=sha(v))
        observations.append(row)
        (out/f'frame-{frame:02}.ram').write_bytes(r);(out/f'frame-{frame:02}.vram').write_bytes(v)
        (out/f'frame-{frame:02}.oam').write_bytes(C.string_at(*e.maps[0x07000000]))
        if frame<16:e.run(1)
    report=dict(status='observed',romSha1=meta['comparisonRomSha1'],sourceReportSha256=sha((capture/'failed.json').read_bytes()),sourceStateSha256=sha((capture/'parent-failed.state').read_bytes()),observations=observations,scope='17-frame retained parent observation only. Does not accept the original failed walking test.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='observed',report=str(out/'report.json'),configured=[bool(r['parsed']) for r in observations])))
finally:e.close()
