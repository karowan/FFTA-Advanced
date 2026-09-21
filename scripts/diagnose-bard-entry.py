"""Bounded fixed-input comparison for the observed executor-entry regression."""
import pathlib,json,runpy,struct,ctypes as C
from native_battle_wrappers import fixed_giza_formation,from_emulator
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);OUT=ROM.parent/'entry-diagnostic';OUT.mkdir(exist_ok=True)
image=bytearray(ROM.read_bytes());image[0xa433c:0xa433e]=bytes.fromhex('fee7');TRAP=OUT/'trap.gba';TRAP.write_bytes(image)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
rows=[]
for wait in (180,600):
    e=E(TRAP)
    try:
        e.load(ROM.parent/'fixture/battle-ready.state');e.run(1);fixed_giza_formation(image,e)
        e.set_memory(0x33fc,struct.pack('<HH',250,250));e.set_memory(0x1e98,bytes(36));e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4)
        wraps=from_emulator(image,e)
        for step,key in enumerate((256,128,128,128,256,256,256,128,256,256,256)):
            e.run(8,key);e.run(wait);r=e.memory();ctl=word(r,0xf438)-0x2000000;u=word(r,ctl+24)-0x2000000
            f=OUT/f'{wait}-{step}.state';e.save(f);registers=struct.unpack_from('<17I',f.read_bytes(),0x20)
            rows.append(dict(wait=wait,step=step,key=key,flags=r[0x1f70:0x1f74].hex(),pc=hex(registers[15]),actor=hex(u),position=list(struct.unpack_from('<3H',r,wraps[u]+8)),menu=observe['menu_visible'](e)))
            e.screenshot(OUT/f'{wait}-{step}.png')
            if registers[15]==0x080a433e:
                (OUT/f'{wait}-entry.ram').write_bytes(r);(OUT/f'{wait}-entry.iwram').write_bytes(C.string_at(*e.maps[0x3000000]));break
    finally:e.close()
playback=ROM.parent/'reaction-playback';state=playback/'SAM-R2-off/1/after-playback.state'
if state.exists():
    e=E(playback/'playback.gba')
    try:
        e.load(playback/'SAM-R2-off/confirmation.state');before=C.string_at(*e.maps[0x3000000])
        e.load(state)
        after=C.string_at(*e.maps[0x3000000]);diff=[i for i in range(0x7000) if before[i]!=after[i]]
        rows.append(dict(iwramChangedBelow7000=len(diff),firstDifferences=[hex(x) for x in diff[:20]],lastDifferences=[hex(x) for x in diff[-20:]]))
        (OUT/'before-playback.iwram').write_bytes(before);(OUT/'after-playback.iwram').write_bytes(after)
        for step in range(4):
            r=e.memory();ctl=word(r,0xf438)-0x2000000
            rows.append(dict(playback=True,step=step,flags=r[0x1f70:0x1f74].hex(),actor=hex(word(r,ctl+24)),menu=observe['menu_visible'](e),controller=r[ctl:ctl+32].hex()))
            e.run(8,256);e.run(600)
    finally:e.close()
(OUT/'report.json').write_text(json.dumps(dict(romSha1=meta['romSha1'],rows=rows),indent=2));print(json.dumps(rows,indent=2))
