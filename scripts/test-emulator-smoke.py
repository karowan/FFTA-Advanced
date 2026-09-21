"""Compare the unmodified intro with the development ROM in actual mGBA."""
import importlib.util,pathlib,json,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',root/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
results=[];frames=[]
for label,rom in [('vanilla','roms/clean/FFTA_US_clean.gba'),('foundation','build/foundation/FFTA_vanillaplus_dev.gba')]:
    e=h.Emulator(root/rom);screens=[]
    for name,steps in [('title',[(3600,0),(8,8),(180,0)]),('opening',[(8,256),(1800,0)])]:
        for n,keys in steps:e.run(n,keys)
        e.screenshot(root/f'build/test/smoke-{label}-{name}.png');screens.append(e.frame)
    state=root/f'build/test/smoke-{label}.state';e.save(state);e.run(60);expected=e.frame
    e.load(state);e.run(60);assert e.frame==expected,'State replay differs'
    results.append({'rom':rom,'sha1':hashlib.sha1((root/rom).read_bytes()).hexdigest(),'stateReplay':True})
    frames.append(screens);e.close()
assert frames[0]==frames[1],'Intro differs from vanilla; inspect screenshots'
report={'passed':True,'roms':results,'scope':'Actual mGBA title and opening scene match vanilla pixel-for-pixel; emulator state roundtrip checked. No quick-start patch or user save used. Does not test completed battles, campaign save/load or the added features.'}
(root/'build/reports/emulator-smoke.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
