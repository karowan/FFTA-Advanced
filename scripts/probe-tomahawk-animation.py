"""Compare animation-field-only Tomahawk variants in a preserved native battle.

Does not rebuild or change shared ROMs, original evidence, effects, or saves.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1]
SHA='e967ee06310e0358348298d574c06cc956f8578f'
LAB=ROOT/'build/expansion/probes/tomahawk-in-game'/SHA
OUT=ROOT/'build/expansion/probes/tomahawk-animation'/SHA;OUT.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha1(b).hexdigest();half=lambda b,p:struct.unpack_from('<H',b,p)[0]
original={p.name:sha(p.read_bytes()) for p in LAB.iterdir() if p.is_file()}
rom=(LAB/'frozen.gba').read_bytes();assert sha(rom)==SHA
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
table=struct.unpack_from('<I',rom,0x23320)[0]-0x08000000;field=table+425*28+20
assert half(rom,field)==0x90 and half(clean,0x55187c+147*28+20)==0x90
assert half(clean,0x55187c+148*28+20)==0x91
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
report={'sourceRomSha1':SHA,'animationFieldOffset':hex(field),'variants':[]}
for name,animation in [('nighthawk',0x90),('throw',0x91),('throw-primary-454',0x91),('throw-icon-donor-52',0x91)]:
 data=bytearray(rom);struct.pack_into('<H',data,field,animation)
 assert data[:field]==rom[:field] and data[field+2:]==rom[field+2:]
 # Diagnostic visual-only override at Throw's DD488 item-lookup return.
 # This feeds the renderer, never the damage or inventory/consume routines.
 if name=='throw-primary-454':data[0xfe41a:0xfe41e]=bytes.fromhex('e3204000')
 if name=='throw-icon-donor-52':data[0xfe41a:0xfe41e]=bytes.fromhex('3420c046')
 folder=OUT/name;folder.mkdir(exist_ok=True);path=folder/'frozen.gba';path.write_bytes(data)
 e=h['Emulator'](path)
 try:
  e.load(LAB/'confirmation.state');before=e.memory()
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',1),4)
  e.run(8,256);frames=[];detail=[]
  for frame in range(720):
   e.run(1)
   if frame%36==35 or (160<=frame<=352 and frame%8==7):
    shot=folder/f'frame-{frame+1:03}.png';e.screenshot(shot)
    if frame%36==35:frames.append(shot)
    if 160<=frame<=352 and frame%8==7:detail.append(shot)
  e.run(1080);after=e.memory();e.screenshot(folder/'finished.png');e.save(folder/'finished.state')
  (folder/'finished.ram').write_bytes(after)
  unchanged=all(before[start:end]==after[start:end] for start,end in [(0x1940,0x1e70),(0x1e80,0x1e98),(0xaa,0xb4),(0x3ff44,0x40000)])
  outcome={'name':name,'animation':animation,'romSha1':sha(data),'actorMP':half(after,0x9c),
   'targetHP':half(after,0x33fc),'damage':half(before,0x33fc)-half(after,0x33fc),'actorEXP':after[0x8a],
   'actorCoordinates':list(after[0x176:0x178]),'targetCoordinates':list(after[0x34da:0x34dc]),
   'inventoryAPPreferencesGearGuardUnchanged':unchanged}
  assert unchanged and half(after,0x9c)==12 and half(after,0x33fc)==9 and after[0x8a]==8,outcome
  assert after[0x176:0x178]==bytes([2,13]) and after[0x34da:0x34dc]==bytes([5,14]),outcome
  for label,paths,columns in [('filmstrip',frames,4),('projectile',detail,4)]:
   tilew,tileh=480,340;canvas=Image.new('RGB',(tilew*columns,tileh*((len(paths)+columns-1)//columns)),'#18202b');draw=ImageDraw.Draw(canvas)
   for i,shot in enumerate(paths):
    x,y=(i%columns)*tilew,(i//columns)*tileh
    canvas.paste(Image.open(shot).resize((480,320)),(x,y));draw.text((x+5,y+320),shot.stem,fill='white')
   canvas.save(folder/(label+'.png'))
  # Repeat the isolated variant with a deterministic native miss. This checks
  # animation-only reuse does not acquire Throw's item-consumption behavior.
  e.load(LAB/'confirmation.state')
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',0),4)
  e.run(8,256);e.run(1800);miss=e.memory()
  assert half(miss,0x9c)==12 and half(miss,0x33fc)==27 and miss[0x8a]==0
  for start,end in [(0x1940,0x1e70),(0x1e80,0x1e98),(0xaa,0xb4),(0x3ff44,0x40000)]:
   assert before[start:end]==miss[start:end],(name,'Miss persistent/gear/guard mutation',hex(start))
  for key in [32,32,256,256]:e.run(8,key);e.run(900 if key==256 else 180)
  next_turn=e.memory();manager=struct.unpack_from('<I',next_turn,0xf438)[0]-0x02000000
  assert struct.unpack_from('<I',next_turn,manager+0x18)[0]==0x02000188,'Native turn did not advance'
  outcome['miss']={'damage':0,'actorMP':12,'actorEXP':0,'invariantsPreserved':True,'nextActor':'0x02000188'}
  report['variants'].append(outcome)
 finally:e.close()
diagnostic=bytearray((OUT/'throw/frozen.gba').read_bytes())
diagnostic[0xfe41e:0xfe420]=bytes.fromhex('fee7')
path=OUT/'throw-lookup-break.gba';path.write_bytes(diagnostic)
e=h['Emulator'](path)
try:
 e.load(LAB/'confirmation.state');e.run(8,256);e.run(400)
 state=OUT/'throw-lookup-break.state';e.save(state)
 registers=struct.unpack_from('<17I',state.read_bytes(),0x20)
 assert registers[15] in (0x080fe41e,0x080fe420,0x080fe422),hex(registers[15])
 assert registers[0]==454,'Native Tomahawk animation already receives the equipped axe'
 report['nativeThrowLookup']={'returnValue':registers[0],'registers':[hex(x) for x in registers]}
 (OUT/'throw-lookup-break.ram').write_bytes(e.memory())
finally:e.close()
assert {p.name:sha(p.read_bytes()) for p in LAB.iterdir() if p.is_file()}==original,'Original evidence changed'
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
