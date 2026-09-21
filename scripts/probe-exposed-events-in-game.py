"""Freeze current native battle and capture candidate event frames, without user saves."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/probes/exposed-events';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha1(b).hexdigest()
base=(ROOT/'build/expansion/probes/combat.gba').read_bytes()
meta=json.loads((ROOT/'build/expansion/probes/combat.json').read_text())
fix=ROOT/'build/expansion/probes/exposed-storage/current'/sha(base)/'battle'
assert sha(base)==meta['romSha1']==sha((fix/'frozen.gba').read_bytes())
OUT=OUT/sha(base);OUT.mkdir(exist_ok=True)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
def tap(e,k,w=120):e.run(8,k);e.run(w)
report={}
for name,site,keys in [('own-turn',0x93022,[32,32,256,256])]:
 image=bytearray(base);image[site:site+2]=b'\xfe\xe7'
 rom=OUT/(name+'.gba');rom.write_bytes(image)
 e=h['Emulator'](rom)
 try:
  e.load(fix/'battle-ready.state');e.run(1);initial=e.memory()
  for k in keys:tap(e,k,600)
  e.run(1200);e.save(OUT/(name+'.state'));ram=e.memory()
  iw=C.string_at(*e.maps[0x03000000]);(OUT/(name+'.ram')).write_bytes(ram);(OUT/(name+'.iwram')).write_bytes(iw)
  regs=struct.unpack_from('<17I',(OUT/(name+'.state')).read_bytes(),0x20)
  assert regs[15]==0x08000000+site+2,(name,hex(regs[15]))
  unit=struct.unpack_from('<I',ram,regs[0]-0x02000000)[0]
  report[name]={'site':hex(site),'registers':[hex(v) for v in regs],'unit':hex(unit),'beforeMP':struct.unpack_from('<H',ram,unit-0x02000000+0x1c)[0]}
  e.screenshot(OUT/(name+'.png'))
 finally:e.close()
image=bytearray(base);image[0xa45ce:0xa45d0]=b'\xfe\xe7'
rom=OUT/'payment.gba';rom.write_bytes(image)
e=h['Emulator'](rom)
try:
 e.load(fix/'battle-ready.state');e.run(1)
 actor=0x398
 for offset in (5,7,0x35):e.set_memory(actor+offset,b'\x10')
 e.set_memory(actor+0x2a,struct.pack('<5H',459,0,0,0,0));e.set_memory(actor+0x40+107,b'\x9e')
 e.set_memory(actor+0x1c,struct.pack('<HH',50,50));e.set_memory(0x33e4+0x18,struct.pack('<HHHH',125,250,49,49))
 for k in [256,128,128,128]:tap(e,k)
 tap(e,256,600)
 for k in [256,32,256,32,256,128,256,256]:tap(e,k)
 e.save(OUT/'payment-confirmation.state');tap(e,256,1200)
 e.save(OUT/'payment.state');ram=e.memory();(OUT/'payment.ram').write_bytes(ram);(OUT/'payment.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
 regs=struct.unpack_from('<17I',(OUT/'payment.state').read_bytes(),0x20)
 assert regs[15]==0x080a45d0,hex(regs[15])
 sp=regs[13]-0x03000000;iw=C.string_at(*e.maps[0x03000000])
 report['payment']={'registers':[hex(v) for v in regs],'stackAction':struct.unpack_from('<I',iw,sp+0x4c)[0],'stackActorWrapper':hex(struct.unpack_from('<I',iw,sp+0x74)[0]),'beforeMP':struct.unpack_from('<H',ram,actor+0x1c)[0],'paidMP':regs[4]}
 assert report['payment']['stackAction']==430 and report['payment']['beforeMP']==50 and regs[4]==40
finally:e.close()
(OUT/'capture.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
