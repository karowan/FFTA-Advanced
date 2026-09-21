"""Native Counters bypass Damage-to-MP; Poise still protects their HP damage."""
import sys
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/('build/expansion/probes/job-state/current.json' if '--job-state' in sys.argv else 'build/expansion/probes/samurai/current.json')).read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
proof=json.loads((LAB/'game-report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
OUT=LAB/'poise-mp-game';OUT.mkdir(exist_ok=True)
control=bytearray(rom);p=meta['symbols']['ffta_poise_factor']-0x08000000;control[p:p+4]=bytes.fromhex('04207047');CONTROL=OUT/'disabled-factor.gba';CONTROL.write_bytes(control)
word=lambda p:struct.unpack_from('<I',rom,p-0x08000000)[0]
bank=word(word(0x080cd538)+4)-0x08000000
reaction=next(i for i in range(144) if struct.unpack_from('<H',rom,bank+8*i+4)[0]==13 and rom[bank+8*i+6]==2)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];outcomes=[];checks=0
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
for initial_mp in (6,55):
 pair=[]
 for name,path in (('control',CONTROL),('poise',ROM)):
  e=E(path)
  try:
   e.load(LAB/'game-352/confirmation.state')
   e.set_memory(0xba,bytes((reaction,154)));e.set_memory(0xc0+reaction,b'\xff');e.set_memory(0x1b4a,b'\xff')
   e.set_memory(0x1e98,b'\x00');e.set_memory(0x168,bytes(8));e.set_memory(0x98,struct.pack('<4H',500,500,initial_mp,55));e.set_memory(0x3ff48,bytes(4))
   e.set_memory(0x33e4+5,bytes((16,2,16)));e.set_memory(0x33e4+0x3a,bytes([53]));e.set_memory(0x33e4+0x40+53,b'\xff');e.set_memory(0x33e4+0x2a,struct.pack('<5H',460,0,0,0,0))
   C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',0),4)
   e.run(8,256);e.run(2100);r=e.memory();label=f'{initial_mp}-{name}';e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(r)
   check(r[0x3ff44:]==bytes(8)+b'\xd7'*0xb4,(label,'root/guard'))
   pair.append(dict(hp=half(r,0x98),mp=half(r,0x9c),strike=250-half(r,0x33fc),protect=bool(r[0x16b]&2)))
  finally:e.close()
 print(initial_mp,pair,flush=True)
 check(pair[0]['strike']==pair[1]['strike'] and pair[0]['strike']>0,('positive identical outgoing strike',pair))
 check(pair[0]['protect'] and pair[1]['protect'],('Guarding grants Poise qualifier',pair))
 damage=500-pair[0]['hp'];check(damage>0 and 500-pair[1]['hp']==damage*3//4,('Counter HP protection regardless of available MP',pair))
 check(pair[0]['mp']==pair[1]['mp']==initial_mp-6,('Counter does not activate MP redirection',pair))
 outcomes.append(dict(initialMP=initial_mp,seed=0,control=pair[0],poise=pair[1]))
report=dict(passed=True,romSha1=meta['romSha1'],controlSha1=hashlib.sha1(control).hexdigest(),checks=checks,outcomes=outcomes,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
