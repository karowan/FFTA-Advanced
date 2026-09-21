"""Installed Centered end-turn hook through real native Wait, both packed bits."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];g=runpy.run_path(str(ROOT/'scripts/test-samurai-state.py'));OUT=g['OUT'];symbols=g['symbols'];base=g['base'];rom=bytearray(g['rom']);FIX=OUT/'fixture'
assert hashlib.sha1((FIX/'frozen.gba').read_bytes()).hexdigest()==hashlib.sha1(base).hexdigest()
assert rom[0x92f94:0x92fa0].hex()=='686005203880286806f0d2fa'
struct.pack_into('<HHHHI',rom,0x92f94,0xb408,0x46c0,0x4b00,0x4718,symbols['ffta_centered_turn_end_entry']|1)
(OUT/'turn.gba').write_bytes(rom);h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));checks=0;cases=[]
for value in range(256):
 v=(value>>1)&7;nv=0 if v in (3,7) else v&3 if v&4 else max(0,v-1);wanted=(value&~14)|(nv<<1)
 results=[]
 for kind,path in (('native',FIX/'frozen.gba'),('centered',OUT/'turn.gba')):
  e=h['Emulator'](path)
  try:
   e.load(FIX/'battle-ready.state');e.set_memory(0x1e9b,bytes([wanted if kind=='native' else value]))
   for key in (32,32,256,256):e.run(8,key);e.run(180)
   results.append(e.memory())
  finally:e.close()
 expected=results[0]
 checks+=1;assert results[1]==expected,('Native Wait differential',value,[(hex(i),a,b) for i,(a,b) in enumerate(zip(results[1],expected)) if a!=b][:15])
 if value in (1,3,5,9,13,15):cases.append(dict(before=value,after=results[1][0x1e9b]))
report=dict(passed=True,baseSha1=hashlib.sha1(base).hexdigest(),romSha1=hashlib.sha1(rom).hexdigest(),checks=checks,cases=cases,scope='256 actual native Wait executions paired with native expected-state control, exact complete EWRAM including downstream scheduler owner copies')
(OUT/'turn-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
