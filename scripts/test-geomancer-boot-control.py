"""Fixed no-field new-game prefix, current renderer versus pre-renderer content.

Compare the existing battle-fixture's exact pub inputs before changing its timing.
This is a deterministic diagnosis, not battle or display acceptance.
"""
import hashlib,json,pathlib,runpy,ctypes as C,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent/'boot-control';OUT.mkdir(exist_ok=True)
old=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1/1dbb18a25a96b0a383b5196506d46f1d141454fd/integrated.gba'
assert hashlib.sha1(old.read_bytes()).hexdigest()=='1dbb18a25a96b0a383b5196506d46f1d141454fd'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];samples=[]
for name,rom in [('pre-renderer',old),('renderer',pathlib.Path(meta['path']))]:
 e=E(rom);steps=[]
 try:
  e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0);e.run(3600)
  inputs=[(8,180),(256,60),(256,60),(256,180)]+[(256,180)]*23+[(1,180)]*4
  for i,(key,wait) in enumerate(inputs):
   e.run(8,key);e.run(wait)
   if i in (3,6,12,20,26,30):
    e.screenshot(OUT/f'{name}-{i:02}.png');e.save(OUT/f'{name}-{i:02}.state')
    r=e.memory();steps.append(dict(step=i,frameSha1=hashlib.sha1(e.frame[0]).hexdigest(),cursor=struct.unpack_from('<2H',r,0x2c16),manager=struct.unpack_from('<I',r,0xf4b0)[0]))
  # Declared additional confirmation controls, with full native release/wait.
  for i in range(8):
   e.run(8,256);e.run(180);e.screenshot(OUT/f'{name}-extra-{i:02}.png')
  samples.append(dict(name=name,romSha1=hashlib.sha1(rom.read_bytes()).hexdigest(),steps=steps))
 finally:e.close()
report=dict(passed=True,scope='fixed pub-prefix comparison only',samples=samples)
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
