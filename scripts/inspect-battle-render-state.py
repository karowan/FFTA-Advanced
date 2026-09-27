"""Inspect a user-captured mGBA state without writing player saves or inputs.

Accepts native PNG states or raw libretro states. Records actor allocation and
upload evidence at fixed video boundaries; diagnostic findings are not a pass
claim for gameplay. Use through the declared battle-render test plan.
"""
import argparse,ast,ctypes as C,hashlib,json,runpy,struct,zlib,sys
from pathlib import Path
from actor_render_evidence import actors
from chemist_candidate import candidate
from native_battle_wrappers import from_memory

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--state',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--verify-status-records',action='store_true')
args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
meta=candidate();rom=Path(meta['path']).read_bytes()
raw=args.state.read_bytes();source_hash=hashlib.sha256(raw).hexdigest()
if raw.startswith(b'\x89PNG\r\n\x1a\n'):
    cursor=8;decoded=None
    while cursor<len(raw):
        size=struct.unpack_from('>I',raw,cursor)[0]
        kind=raw[cursor+4:cursor+8];data=raw[cursor+8:cursor+8+size]
        if kind==b'gbAs':decoded=zlib.decompress(data)
        cursor+=size+12
    assert decoded is not None,'No native state chunk'
    raw=decoded
state=args.out/'input.state';state.write_bytes(raw)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observations=[]
with E(Path(meta['path'])) as e:
    e.load(state)
    for frame,count in ((1,1),(2,1),(62,60),(362,300)):
        e.run(count)
        stem=args.out/f'frame-{frame:03}'
        e.screenshot(stem.with_suffix('.png'));e.save(stem.with_suffix('.state'))
        ram=e.memory();vram=C.string_at(*e.maps[0x06000000])
        for name,region in (('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)):
            stem.with_suffix('.'+name).write_bytes(C.string_at(*e.maps[region]))
        found=actors(rom,ram,vram)
        observations.append(dict(frame=frame,actors=found))
units=[]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,(args.out/'frame-362.iwram').read_bytes());m.put(0x02000000,ram)
wrappers=from_memory(rom,ram,(args.out/'frame-362.iwram').read_bytes())
for unit,wrapper in wrappers.items():
    u=ram[unit:unit+264];w=ram[wrapper:wrapper+0x90]
    name=struct.unpack_from('<I',u)[0]
    namebytes=rom[name-0x08000000:name-0x08000000+24].hex() if 0x08000000<=name<0x0a000000 else None
    icons={key:m.call(0x0809da0c,0x02000000+unit,key,stack=0x03007000) for key in range(1,60)}
    units.append(dict(unit=hex(unit),wrapper=hex(wrapper),name=hex(name),nameBytes=namebytes,job=u[5],race=u[6],hp=struct.unpack_from('<H',u,24)[0],nativeStatus=u[0xe0:0x108].hex(),wrapperBytes=w.hex(),icons={k:v for k,v in icons.items() if v}))
report=dict(passed=True,diagnosticOnly=True,romSha1=meta['romSha1'],units=units,
            sourceStateSha256=source_hash,inputs=[],observations=observations)
if args.verify_status_records:
    checks=[]
    code=json.loads((ROOT/'build/expansion/chemist-progressions/code/manifest.json').read_text())
    # The captured user's bank contains only Montblanc's movement ledger.
    # Preserve it exactly; never clear effects to make the picture look right.
    for i in range(36):
        record=bytearray(ram[0x3f410+i*27:0x3f410+(i+1)*27])
        record[12]=record[13]=record[14]=0;record[19]&=7
        assert not any(record),('Capture has additional effects',i,record.hex())
    for entry in code['installedEntries']['ffta_job_state']:
        for i in range(36):
            unit=0x02000080+i*264 if i<24 else 0x02002fc4+(i-24)*264
            result=m.call(entry,unit)
            assert result==0x0203f410+27*i,('Retired accessor stride',hex(entry),i,hex(result))
    checks.append('Every authenticated old accessor resolves all 36 current records')
    for u in units:
        assert not {k:v for k,v in u['icons'].items() if k>=25},('Phantom custom status',u)
    checks.append('Captured movement ledger produces no custom buffs on any actor')
    report['checks']=checks;report['diagnosticOnly']=False
(args.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(report=str(args.out/'report.json'),actors=[len(o['actors']) for o in observations])))
