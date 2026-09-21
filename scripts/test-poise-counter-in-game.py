"""Actual incoming Counter has its own Poise status snapshot after an art."""
import sys
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/('build/expansion/probes/job-state/current.json' if '--job-state' in sys.argv else 'build/expansion/probes/samurai/current.json')).read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
proof=json.loads((LAB/'game-report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
OUT=LAB/'poise-counter';OUT.mkdir(exist_ok=True);control=bytearray(rom);p=meta['symbols']['ffta_poise_factor']-0x08000000;control[p:p+4]=bytes.fromhex('04207047');CONTROL=OUT/'disabled-factor.gba';CONTROL.write_bytes(control)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];outcomes=[];checks=0
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def half(r,p):return struct.unpack_from('<H',r,p)[0]
for action,regen,centered,expected_active in ((352,False,False,True),(353,False,True,False),(353,True,True,True),(347,False,False,True)):
 successful=False
 for seed in range(16):
  pair=[]
  for name,path in (('control',CONTROL),('poise',ROM)):
   e=E(path)
   try:
    e.load(LAB/f'game-{action}/confirmation.state')
    e.set_memory(0x80+0x3b,bytes([154]));e.set_memory(0x1b4a,b'\xff');e.set_memory(0x1e98,bytes([4 if centered else 0]));e.set_memory(0x80+0xe8,bytes([8 if regen else 0]));e.set_memory(0x80+0xeb,b'\x00');e.set_memory(0x98,struct.pack('<HH',500,500));e.set_memory(0x3ff48,bytes(4))
    # Native Human Paladin Counter, independently mastered in the initial fixture.
    e.set_memory(0x33e4+5,bytes((16,2,16)));e.set_memory(0x33e4+0x3a,bytes([53]));e.set_memory(0x33e4+0x40+53,b'\xff');e.set_memory(0x33e4+0x2a,struct.pack('<5H',460,0,0,0,0))
    C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
    e.run(8,256);e.run(2100);r=e.memory()
    label=f'{action}-{int(regen)}-{seed}-{name}';e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(r)
    check(r[0x3ff44:]==bytes(8)+b'\xd7'*0xb4,(label,'root/guard'))
    pair.append(dict(strike=250-half(r,0x33fc),counter=500-half(r,0x98),centered=r[0x1e98],protect=bool(r[0x16b]&2),regen=bool(r[0x168]&8)))
   finally:e.close()
  check(pair[0]['strike']==pair[1]['strike'],('outgoing unchanged',action,seed,pair))
  # Ashura only grants Centered on a successful hit. Guarding grants Protect
  # on its admitted attempt; Kiku consumes Centered before the Counter.
  active=expected_active and (action!=347 or pair[0]['strike']>0)
  expected=pair[0]['counter']*3//4 if active else pair[0]['counter']
  print(action,regen,seed,pair,'expected',expected,flush=True)
  check(pair[1]['counter']==expected,('incoming-action snapshot',action,regen,seed,pair,expected))
  outcomes.append(dict(action=action,regen=regen,seed=seed,active=active,control=pair[0],poise=pair[1]))
  if pair[0]['counter']>0 and (action!=347 or pair[0]['strike']>0):successful=True;break
 check(successful,('No positive Counter within fixed seeds',action,regen))
report=dict(passed=True,romSha1=meta['romSha1'],controlSha1=hashlib.sha1(control).hexdigest(),checks=checks,outcomes=outcomes,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
