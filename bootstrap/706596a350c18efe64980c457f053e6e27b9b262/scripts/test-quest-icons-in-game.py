"""Compare actual Mission Item list/help pixels across overlapping namespaces.

Cold-loads the same ordinary native save in isolated mGBA for both ROMs. The
only quest fixture changes are RAM-only; no emulated save command is used.
"""
import hashlib,importlib.util,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=ROOT/'build/expansion/probes/quest-icons'
OUT.mkdir(exist_ok=True)
SEED=ROOT/'build/test-lab/early-town.sav'
SOURCES={'foundation':ROOT/'build/foundation/FFTA_vanillaplus_dev.gba',
         'expanded':ROOT/'build/expansion/probes/content-inventory.gba'}
ROMS={}
rom_hashes={}
for label,source in SOURCES.items():
    image=source.read_bytes()
    assert len(image)==0x2000000,'Incomplete source build'
    frozen=OUT/f'{label}-fixture.gba'
    frozen.write_bytes(image)
    ROMS[label]=frozen
    rom_hashes[label]=hashlib.sha1(image).hexdigest()
seed=SEED.read_bytes()

def sha(raw):return hashlib.sha1(raw).hexdigest()
def tap(e,key,wait=40):e.run(8,key);e.run(wait)
def cold(rom):
    e=h.Emulator(rom);e.set_memory(0,seed,0);e.run(3600)
    tap(e,8,180);tap(e,256,60);tap(e,256,60);tap(e,256,180)
    return e

frames={};samples=[]
for label,rom in ROMS.items():
    frames[label]={}
    # Native quest inventory has64 slots, so two independent fixtures cover
    # every global icon ID376..460 that overlaps an added equipment ID.
    for batch,ids in enumerate((range(1,65),range(65,86))):
        ids=list(ids)
        e=cold(rom)
        try:
            ram=e.memory()
            original_roster=ram[0x80:0x1940]
            original_sram=e.memory(0)
            # Native flag303 = Thesis Hunt/internal mission4 complete. A
            # single-bit differential verified it unlocks the Clan menu.
            e.set_memory(0x1fd0,bytes([ram[0x1fd0]|8]))
            quest=bytearray(64*4)
            for n,ident in enumerate(ids):quest[n*4]=ident
            e.set_memory(0x2b08,bytes(quest))
            if label=='expanded':
                # Exercise real coexistence: all85 new equipment IDs owned
                # while the same numeric IDs represent quest icons here.
                e.set_memory(0x1940+376,bytes([1])*85)
            inventory_before=e.memory()[0x1940:0x1f1c]
            tap(e,8);tap(e,32);tap(e,256,120)
            for _ in range(3):tap(e,32)
            tap(e,256,80)
            for n,ident in enumerate(ids):
                key=f'{batch}-{ident}-list'
                frames[label][key]=sha(e.frame[0])
                capture=n==0 or n==len(ids)-1 or n%16==0
                if capture:
                    path=OUT/f'{label}-{ident:03}-list.png';e.screenshot(path)
                    if label=='expanded':samples.append(str(path.relative_to(ROOT)))
                # Native quest help can have multiple pages; B advances them.
                # Keep this build's selected-list checkpoint and restore it
                # after inspecting the first description page, so scrolling
                # cannot be accidentally swallowed by a remaining help page.
                checkpoint=OUT/f'{label}-{batch}-selection.state'
                e.save(checkpoint)
                tap(e,4,80)
                frames[label][f'{batch}-{ident}-help']=sha(e.frame[0])
                if capture:e.screenshot(OUT/f'{label}-{ident:03}-help.png')
                e.load(checkpoint)
                if n+1<len(ids):tap(e,32,80)
            current=e.memory()
            assert current[0x80:0x1940]==original_roster,'Quest UI changed party'
            assert current[0x1940:0x1f1c]==inventory_before,'Quest UI changed equipment/AP storage'
            assert current[0x2b08:0x2c08]==quest,'Quest UI changed quest IDs/flags'
            assert e.memory(0)==original_sram,'Read-only menu test changed emulated SRAM'
        finally:e.close()

assert frames['foundation'].keys()==frames['expanded'].keys()
for label in ROMS:
    list_hashes=[v for k,v in frames[label].items() if k.endswith('-list')]
    assert len(set(list_hashes))==85,'Did not visit85 distinct selected list screens'
    assert all(frames[label][key]!=frames[label][key.replace('-list','-help')]
               for key in frames[label] if key.endswith('-list')),'Help did not open for a selected item'
failures=[key for key in frames['foundation'] if frames['foundation'][key]!=frames['expanded'][key]]
assert SEED.read_bytes()==seed,'Source native save changed'
report={'passed':not failures,'romSha1':rom_hashes,
        'seedSha1':sha(seed),'screenComparisons':len(frames['foundation']),
        'questLocalIds':'1..85','overlappingGlobalIds':'376..460',
        'fixture':'RAM-only flag303 (Thesis Hunt complete), unique quest entries in two batches of64/21; expanded ROM also owns all85 new equipment IDs',
        'failures':failures,'samples':samples,'frames':frames,
        'checks':['Ordinary native cold load, then actual Clan > Mission Item menu',
                  'All85 selected list screens and all85 selected help screens pixel-identical',
                  'Full64-slot quest inventory and21-slot remainder exercised',
                  'Original roster, equipment/AP storage, quest records and SRAM unchanged by viewing',
                  'Source seed and user play files never written'],
        'limitation':'Does not exercise quest consumption/rewards or new axe artwork'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='frames'},indent=2))
if failures:raise SystemExit(1)
