"""Declared original-map fixture for generated actor water acceptance.

The existing encounter shell selects map70. Redirect its complete88-byte map
record to original map92; retain every original component, height and water flag.
This tests natural map graphics/geometry, not that map's campaign encounter.
"""
import hashlib, json, struct
from pathlib import Path
from native_art import ROOT, sha
from ffta_maps import Maps, TABLE, CLEAN_SHA1
from native_battle_wrappers import from_emulator

MAP, SHELL = 92, 70
LAND, WATER = (5,5), (6,5)

def build(rom, out):
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();native=Maps(clean)
    record=native.record(MAP);offset=TABLE+88*SHELL
    assert rom[TABLE:TABLE+162*88]==clean[TABLE:TABLE+162*88]
    patched=bytearray(rom);patched[offset:offset+88]=record
    assert patched[:offset]==rom[:offset] and patched[offset+88:]==rom[offset+88:]
    path=out/'natural-water.gba';path.write_bytes(patched)
    evidence=dict(cleanRomSha1=CLEAN_SHA1,sourceRomSha1=hashlib.sha1(rom).hexdigest(),
        fixtureRomSha1=hashlib.sha1(patched).hexdigest(),originalMap=MAP,encounterMap=SHELL,
        changedRecord=[offset,88],recordSha256=sha(record),heightSha256=sha(native.heights(MAP)),
        clippingSha256=sha(native.clipping(MAP)),arrangementSha256=sha(native.planar(MAP)),
        land=list(LAND),water=list(WATER),scope='Intact original map through existing encounter shell, not original campaign mission. No terrain flags modified.')
    (out/'fixture.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return path,bytes(patched),native,evidence

def formation(rom, emulator, native, focus=0x398):
    wrappers=from_emulator(rom,emulator);ram=emulator.memory();heights=native.heights(MAP)
    assert set(wrappers)=={0x80,0x188,0x290,0x398,0x4a0,0x5a8,0x2fc4,0x30cc,0x31d4,0x32dc,0x33e4,0x34ec}
    cells=[(x,y) for y in range(16) for x in range(16) if heights[2*(y*16+x)] and not heights[2*(y*16+x)+1]&11]
    occupied=set();positions=[]
    assert focus in wrappers
    for unit in [focus,*sorted(p for p in wrappers if p!=focus)]:
        x,y=LAND if unit==focus else min((c for c in cells if c not in occupied),key=lambda c:(abs(c[0]-ram[unit+0xf6])+abs(c[1]-ram[unit+0xf7]),c[1],c[0]))
        assert (x,y) in cells and (x,y) not in occupied;occupied.add((x,y))
        height=heights[2*(y*16+x)]*16;w=wrappers[unit]
        emulator.set_memory(unit+0xf6,bytes((x,y)))
        emulator.set_memory(w+8,struct.pack('<3H',x*32+16,height,y*32+16))
        emulator.set_memory(w+0x1f,bytes([3]));positions.append([unit,x,y,height,3])
    return positions
