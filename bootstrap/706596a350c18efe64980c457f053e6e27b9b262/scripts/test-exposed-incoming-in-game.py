"""Disposable native Fight preview/confirmation with and without Exposed."""
import argparse,ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha1(b).hexdigest()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-sha',default='69a844aee6a536f29e2b00959acce62de1658e27');p.add_argument('--seed',type=int,default=2);p.add_argument('--fell',action='store_true');p.add_argument('--current',action='store_true');args=p.parse_args()
OUT=ROOT/'build/expansion/probes/exposed-effects'/args.base_sha
if args.fell:
 from fell_test_context import load_context
 report=load_context(args.current);ROM=pathlib.Path(report['path']);OUT=ROM.parent;fix=OUT/'fixture';args.base_sha=report['baseSha1']
 assert sha((fix/'frozen.gba').read_bytes())==report['romSha1']
else:
 report=json.loads((OUT/'report.json').read_text());ROM=OUT/'isolated.gba';assert report['incomingHooks']
 fix=ROOT/'build/expansion/probes/exposed-storage/current'/args.base_sha/'battle'
 assert sha((fix/'frozen.gba').read_bytes())==args.base_sha
assert sha(ROM.read_bytes())==report['romSha1']
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
cases=[]
for exposed in (False,True):
 e=h['Emulator'](ROM);tag='incoming-on' if exposed else 'incoming-off'
 def tap(key,wait=120):e.run(8,key);e.run(wait)
 try:
  e.load(fix/'battle-ready.state');e.run(1)
  # Native Move3East brings Jona adjacent to the actual enemy at5,14.
  e.set_memory(0x33e4+0x18,struct.pack('<HH',250,250))
  e.set_memory(0x1e98,bytes([0x0a])*36)
  e.set_memory(0x1e98+28,bytes([0x0b if exposed else 0x0a]))
  initial=e.memory()
  for key in [256,128,128,128]:tap(key)
  tap(256,600)
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',args.seed),4)
  for key in [256,256,128,256]:tap(key)
  e.save(OUT/(tag+'-preview.state'));e.screenshot(OUT/(tag+'-preview.png'))
  preview=e.memory();(OUT/(tag+'-preview.ram')).write_bytes(preview)
  # Freeze the native PRNG immediately before actual confirmation for matching
  # accuracy/variance. Same seed and UI input in both otherwise equal cases.
  tap(256) # Native Do it / Cancel confirmation.
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',args.seed),4)
  e.save(OUT/(tag+'-confirmation.state'))
  e.screenshot(OUT/(tag+'-confirmation.png'))
  tap(256,1800)
  final=e.memory();e.save(OUT/(tag+'-after.state'));e.screenshot(OUT/(tag+'-after.png'))
  (OUT/(tag+'-after.ram')).write_bytes(final)
  hp=struct.unpack_from('<H',final,0x33e4+0x18)[0]
  assert hp<250,('Native Fight did not damage intended target',tag,hp)
  assert initial[0x1940:0x1e98]==final[0x1940:0x1e98],'Inventory/AP/prefs changed'
  assert initial[0x3ff44:]==final[0x3ff44:],'Guard changed'
  assert final[0x1e98:0x1ebc]==initial[0x1e98:0x1ebc],'Packed incoming state changed before own turn'
  cases.append({'exposed':exposed,'hpBefore':250,'hpAfter':hp,'damage':250-hp})
 finally:e.close()
assert cases[1]['damage']==cases[0]['damage']*6//5,cases
result={'passed':True,'baseSha1':args.base_sha,'romSha1':report['romSha1'],'cases':cases,'scope':'Actual native Fight preview/confirmation from frozen disposable fixture; actual431 tested separately.'}
(OUT/'incoming-in-game-report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
