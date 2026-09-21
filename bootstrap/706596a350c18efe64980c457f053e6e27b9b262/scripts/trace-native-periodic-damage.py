"""Fixed-input native Poison trace; records scheduler/HP evidence for integration."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text())
ROM=pathlib.Path(meta['path']);FIX=ROM.parent/'fixture';OUT=ROM.parent/'native-periodic-trace';OUT.mkdir(exist_ok=True)
image=ROM.read_bytes();assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
u16=lambda b,p:struct.unpack_from('<H',b,p)[0]
u32=lambda b,p:struct.unpack_from('<I',b,p)[0]
results=[]
for label,status,hp,trap in [('healthy',0,100,False),('poison',2,100,False),('poison-lethal',2,1,False),('poison-entry',2,100,True)]:
 trial=bytearray(image)
 if trap:trial[0x9f4d8:0x9f4da]=b'\xfe\xe7'
 path=OUT/(label+'.gba');path.write_bytes(trial);e=Emulator(path)
 try:
  e.load(FIX/'battle-ready.state');menu['wait_for_menu'](e,limit=9000)
  b=e.memory();actor=u32(b,u32(b,0xf438)-0x02000000+0x18)-0x02000000
  assert actor==0x398,hex(actor)
  e.set_memory(actor+0x18,struct.pack('<HH',hp,100));e.set_memory(actor+0xe8,bytes(8));e.set_memory(actor+0xe9,bytes([status]))
  e.save(OUT/(label+'-ready.state'));timeline=[]
  for turn in range(6):
   for key in (32,32,256,256):e.run(8,key);e.run(180)
   e.run(600);b=e.memory();timeline.append(dict(turn=turn,hp=u16(b,actor+0x18),status=b[actor+0xe9]))
   if trap:
    e.save(OUT/(label+'-checking.state'))
    if u32((OUT/(label+'-checking.state')).read_bytes(),0x5c)==0x0809f4da:break
   if u16(b,actor+0x18)<hp:break
   menu['wait_for_menu'](e,limit=9000)
  e.run(600);b=e.memory();e.save(OUT/(label+'-after.state'));e.screenshot(OUT/(label+'-after.png'))
  (OUT/(label+'-after.ram')).write_bytes(b);(OUT/(label+'-after.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
  regs=struct.unpack_from('<17I',(OUT/(label+'-after.state')).read_bytes(),0x20)
  result=dict(label=label,romSha1=hashlib.sha1(trial).hexdigest(),actor=actor,beforeHP=hp,afterHP=u16(b,actor+0x18),status=list(b[actor+0xe8:actor+0xf0]),timeline=timeline,regs=list(regs),menuVisible=menu['menu_visible'](e))
  if trap:
   assert regs[15]==0x0809f4da,hex(regs[15]);scheduler=regs[7]-0x02000000
   result['scheduler']=dict(address=regs[7],wrapper=u32(b,scheduler),phase=u16(b,scheduler+0xcc),depth=u16(b,scheduler+0xce),stack=[u16(b,scheduler+0xd0+2*i) for i in range(12)])
  elif label=='healthy':assert result['afterHP']==100
  elif label=='poison':assert 0<result['afterHP']<100
  elif label=='poison-lethal':assert result['afterHP']==0
  results.append(result)
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],cases=results,scope='Native Poison bit9 end-turn entry, damage, lethal HP and downstream menu; no custom pulse enabled')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
