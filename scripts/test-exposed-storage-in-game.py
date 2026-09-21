"""Private-ROM native sort/save and actual battle preview/suspend state tests."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/expansion/probes/exposed-storage'
sha=lambda b:hashlib.sha1(b).hexdigest()
if '--current' in sys.argv:OUT=OUT/'current'/sha((ROOT/'build/expansion/probes/combat.gba').read_bytes())
ROM=OUT/'isolated.gba';report=json.loads((OUT/'report.json').read_text());assert sha(ROM.read_bytes())==report['romSha1']
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));seedpath=ROOT/'build/test-lab/early-town.sav';seed=seedpath.read_bytes();checks=[]
def tap(e,key,wait=40):e.run(8,key);e.run(wait)
def cold(saved):
 e=h['Emulator'](ROM);e.set_memory(0,saved,0);e.run(3600)
 for k,w in [(8,180),(256,60),(256,60),(256,180)]:tap(e,k,w)
 return e
def state(e):return e.memory()[0x1e98:0x1f04]
def wound_pattern():return b''.join(struct.pack('<H',(0x8000 if i%2 else 0x4000)+71*i+1) for i in range(36))
e=cold(seed)
try:
 assert state(e)==bytes(108),'Migration did not initialize saved statuses'
 pattern=bytes(i%2 for i in range(36))+wound_pattern();e.set_memory(0x1e98,pattern);before=e.memory()
 tap(e,8);tap(e,256,120)
 for k in [128,128,4,128,4]:tap(e,k,100)
 expected=bytearray(pattern);expected[2],expected[3]=expected[3],expected[2]
 expected[40:42],expected[42:44]=pattern[42:44],pattern[40:42]
 assert state(e)==expected,('Native sort',state(e),expected)
 ap=bytearray(before[0x1b40:0x1e70]);ap[68:102],ap[102:136]=ap[102:136],ap[68:102]
 assert e.memory()[0x1b40:0x1e70]==ap
 tap(e,1,60)
 for k,w in [(8,40),(16,40),(256,40),(256,60),(256,60),(64,20),(256,300)]:tap(e,k,w)
 saved=e.memory(0);assert saved!=seed;(OUT/'normal.sav').write_bytes(saved)
finally:e.close()
e=cold(saved)
try:
 assert state(e)==expected,('Normal cold load',state(e),expected)
 assert e.memory()[0x1b40:0x1e70]==ap
 e.screenshot(OUT/'normal-cold.png');checks.append('Native party sort, normal SRAM save and fresh cold load preserve108 status bytes and AP')
finally:e.close()
# Fresh native battle from SRAM on this precise private ROM, no cross-ROM state.
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(ROM),'--out',str(OUT/'battle')],check=True,capture_output=True)
e=h['Emulator'](ROM)
try:
 e.load(OUT/'battle/battle-ready.state');e.run(1)
 pattern=bytes((i//2)%2 for i in range(36))+wound_pattern();e.set_memory(0x1e98,pattern);before=e.memory();ap=before[0x1b40:0x1e70];prefs=before[0x1e80:0x1e98];guard=before[0x3ff44:]
 for key in [32,256,256,128,256]:tap(e,key,120)
 assert state(e)==pattern,'Preview mutated live state'
 e.screenshot(OUT/'preview.png')
 for _ in range(3):tap(e,1,120)
 assert state(e)==pattern,'Cancel failed state rollback'
 # B exits an uncommitted menu; Start > Save Now invokes actual suspend.
 for key in [1,8,16,256,256]:tap(e,key,180)
 e.screenshot(OUT/'suspend-confirmation.png');initial=e.memory(0);tap(e,256,300);saved=e.memory(0);assert saved!=initial
 (OUT/'suspended.sav').write_bytes(saved)
finally:e.close()
e=h['Emulator'](ROM)
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
 assert state(e)==pattern,('Suspend cold load',state(e),pattern)
 ram=e.memory();assert ram[0x3ff44:]==guard;assert ram[0x1b40:0x1e70]==ap and ram[0x1e80:0x1e98]==prefs
 e.screenshot(OUT/'suspend-cold.png');e.save(OUT/'suspend-cold.state')
 # Prove resumed control can open and cancel an ordinary command.
 tap(e,32,120);tap(e,256,120);tap(e,1,120);assert state(e)==pattern
 checks.append('Actual Fight preview/cancel, native Save Now and fresh cold Resume Battle preserve108 state bytes/AP/preferences')
finally:e.close()
assert seedpath.read_bytes()==seed
result={'passed':True,'romSha1':sha(ROM.read_bytes()),'checks':checks,'scope':'Saved Exposed/Centered and Wound storage, native sorting, preview/cancel and normal/suspend cold imports. Higanbana application, pulse damage and expiry are not enabled.'}
(OUT/'in-game.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
