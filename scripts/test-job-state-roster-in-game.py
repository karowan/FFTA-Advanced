"""Native party reorder, normal save and cold load for shared job state."""
import hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta=json.loads((P/'job-state/current.json').read_text());ROM=pathlib.Path(meta['path'])
assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
OUT=ROM.parent/'roster-tests';OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
seed=(ROOT/'build/test-lab/early-town.sav').read_bytes();checks=[]
def tap(e,key,wait=40):e.run(8,key);e.run(wait)
def cold(saved):
 e=E(ROM);e.set_memory(0,saved,0);e.run(3600)
 for k,w in [(8,180),(256,60),(256,60),(256,180)]:tap(e,k,w)
 return e
e=cold(seed)
try:
 assert e.memory()[0x3f400:0x3f404]==struct.pack('<I',0x32534a46)
 pattern=bytes((i*31+j*17+9)&255 for i in range(36) for j in range(22))
 e.set_memory(0x3f410,pattern);before=e.memory()
 tap(e,8);tap(e,256,120)
 for k in (128,128,4,128,4):tap(e,k,100)
 after=e.memory();e.save(OUT/'reordered.state');(OUT/'reordered.ram').write_bytes(after)
 e.screenshot(OUT/'reordered.png')
 expected=bytearray(pattern);expected[44:66],expected[66:88]=pattern[66:88],pattern[44:66]
 # Token-indexed links follow the native physical slot permutation too.
 for i in range(36):
  for byte in (1,5):
   p=i*22+byte
   if expected[p] in (3,4):expected[p]=7-expected[p]
 assert after[0x3f410:0x3f728]==expected,'Job records/links did not follow native roster order'
 ap=bytearray(before[0x1b40:0x1e70]);ap[68:102],ap[102:136]=ap[102:136],ap[68:102]
 assert after[0x1b40:0x1e70]==ap,'Reorder altered native AP behavior'
 prefs=bytearray(before[0x1e80:0x1e98]);prefs[2],prefs[3]=prefs[3],prefs[2]
 assert after[0x1e80:0x1e98]==prefs
 checks.append('Native party UI reorders independent job records, links, AP and preferences')
 tap(e,1,60)
 for k,w in [(8,40),(16,40),(256,40),(256,60),(256,60),(64,20),(256,300)]:tap(e,k,w)
 saved=e.memory(0);assert saved!=seed;(OUT/'normal.sav').write_bytes(saved)
 assert e.memory()[0x3f410:0x3f728]==expected,'Ordinary save mutated transient live state'
finally:e.close()
e=cold(saved)
try:
 assert e.memory()[0x3f410:0x3f728]==bytes(792),'Ordinary cold load retained transient battle statuses'
 assert e.memory()[0x1b40:0x1e70]==ap and e.memory()[0x1e80:0x1e98]==prefs
 e.save(OUT/'normal-cold.state');e.screenshot(OUT/'normal-cold.png')
 checks.append('Native ordinary save/cold load preserves AP/preferences and initializes transient battle state')
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
