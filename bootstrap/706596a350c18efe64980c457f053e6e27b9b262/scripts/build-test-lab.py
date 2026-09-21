"""Generate a native save through game menus, then test the unmodified dev ROM.

No user ROM or save is opened for writing. Snapshots are rebuild-specific; the
portable test seed is an ordinary SRAM save, loaded through Continue -> Load.
"""
import importlib.util,pathlib,json,hashlib,time,shutil
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',root/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
out=root/'build/test-lab';out.mkdir(parents=True,exist_ok=True)
screens=out/'screenshots';screens.mkdir(exist_ok=True)
dev=root/'build/foundation/FFTA_vanillaplus_dev.gba'
started=time.monotonic();checks=[]
def digest(p):return hashlib.sha1(p.read_bytes()).hexdigest()
protected=[p for p in [root/'roms/clean/FFTA_US_clean.gba',root/'roms/play/vanilla/FFTA_US_vanilla.gba',root/'roms/play/vanilla/FFTA_US_vanilla.sav',root/'build/foundation/FFTA_vanillaplus_dev.sav',dev] if p.exists()]
before={str(p):digest(p) for p in protected}
def steps(e,seq):
    for frames,keys in seq:e.run(frames,keys)
def tap(e,key,wait=40):steps(e,[(8,key),(wait,0)])
def photo(e,name):e.screenshot(screens/f'{name}.png')
def roster(e):return e.memory()[0x80:0x80+24*264]
def native_save(e,overwrite=False):
    tap(e,8);tap(e,16);tap(e,256);tap(e,256,60);tap(e,256,60)
    if overwrite:tap(e,64,20);tap(e,256,300)
    else:e.run(300)
def cold_load(seed):
    e=h.Emulator(dev);e.set_memory(0,seed,0)
    steps(e,[(3600,0),(8,8),(180,0),(8,256),(60,0),(8,256),(60,0),(8,256),(180,0)])
    return e

# One-time setup fixture: names, original starting clan, and Sprohm placement.
e=h.Emulator(out/'setup-only.gba')
try:
    steps(e,[(3600,0),(8,8),(300,0),(8,256),(300,0),
        (8,8),(60,0),(8,64),(30,0),(8,256),(180,0),
        (8,8),(60,0),(8,64),(30,0),(8,256),(300,0),
        (8,16),(60,0),(8,256),(120,0),
        (30,0),(40,128),(16,16),(30,0),(8,256),(120,0)])
    initial=roster(e)
    assert [initial[i*264+4] for i in range(6)]==[2,8,1,1,1,1],'Starting clan not initialized'
    native_save(e);photo(e,'01-native-save-created')
    seed=e.memory(0);assert len(seed)==65536
    (out/'early-town.sav').write_bytes(seed)
finally:e.close()

# Cold boot the normal development build: setup-only engine changes are gone.
e=cold_load(seed)
try:
    assert roster(e)==initial,'Native save failed to restore original clan'
    e.save(out/'early-town.state');photo(e,'02-normal-rom-loaded-seed')
    checks.append('Native seed save loads in normal development ROM and restores all 24 roster records')
    tap(e,8);tap(e,256,120);photo(e,'03-party-before-sort')
    original=roster(e)
    # Story characters cannot be selected for sorting.
    tap(e,4);assert e.memory()[0x2fc4]==0
    tap(e,128);tap(e,4);assert e.memory()[0x2fc4]==0
    tap(e,128);tap(e,4);assert e.memory()[0x2fc4]==3
    photo(e,'04-generic-selected')
    tap(e,128);tap(e,4,100)
    expected=bytearray(original);expected[2*264:3*264]=original[3*264:4*264];expected[3*264:4*264]=original[2*264:3*264]
    assert roster(e)==bytes(expected),'In-game sorting corrupted a roster record'
    assert e.memory()[0x2fc4]==0,'Sorting left a pending selection'
    photo(e,'05-party-after-sort');checks.append('Actual party menu rejects Marche/Montblanc and swaps two generic units byte-for-byte')
    tap(e,1,60);native_save(e,True);photo(e,'06-sorted-clan-saved')
    sorted_seed=e.memory(0);assert sorted_seed!=seed,'Save did not update SRAM'
    (out/'sorted-clan.sav').write_bytes(sorted_seed)
finally:e.close()
e=cold_load(sorted_seed)
try:
    assert roster(e)==bytes(expected),'Sort did not persist through native save and cold load'
    photo(e,'07-sorted-clan-cold-loaded');checks.append('All 24 roster records survive actual game save, emulator restart and Continue/Load after sorting')
finally:e.close()

# Reuse a clean seed for pub coverage; screenshots verify rendered labels/dialogs.
e=cold_load(seed)
try:
    tap(e,256,240);tap(e,256,180);photo(e,'08-pub-missions-first')
    e.save(out/'pub.state');tap(e,256,120);tap(e,256,120)
    photo(e,'09-first-option-opens-mission-list');e.save(out/'mission-list.state')
    checks.append('Pub and first-option mission-list interaction executed; rendered screenshots saved for visual review')
finally:e.close()

for p in protected:assert digest(p)==before[str(p)],f'Protected game/save changed: {p}'
# A separate user-facing lab copy has the exact same ROM bytes, plus the seed save.
play=root/'roms/play/test-lab';play.mkdir(parents=True,exist_ok=True)
save=play/'FFTA_test_lab.sav'
if save.exists():
    backups=out/'save-backups';backups.mkdir(exist_ok=True)
    shutil.copy2(save,backups/f'FFTA_test_lab-{time.time_ns()}.sav')
shutil.copy2(dev,play/'FFTA_test_lab.gba');save.write_bytes(seed)
report={'passed':True,'developmentRomSha1':digest(dev),'setupRomSha1':digest(out/'setup-only.gba'),'nativeSeedSha1':hashlib.sha1(seed).hexdigest(),'elapsedSeconds':round(time.monotonic()-started,2),'checks':checks,'protectedFilesUnchanged':True,'visualReview':'Inspect screenshots 01-09; assertions validate roster state, not OCR/menu text.','notCovered':['dispatch associations','mission refunds/full inventory','recruitment retries','Morpher battle animations','monster ability learning','postgame recovery','new jobs and cross-class effects'],'labROM':'roms/play/test-lab/FFTA_test_lab.gba','labSave':'roms/play/test-lab/FFTA_test_lab.sav','note':'Seed accelerates setup only. Lab ROM equals normal development ROM. No full campaign playthrough is required to run these tests.'}
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
