"""Diagnostic-only changes against a frozen confirmation state."""
import pathlib,runpy,struct,json,ctypes as C,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];LAB=ROOT/'build/expansion/probes/chop-in-game'
OUT=ROOT/'build/expansion/probes/chop-animation-variants';OUT.mkdir(exist_ok=True)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));source=(LAB/'frozen.gba').read_bytes()
table=struct.unpack_from('<I',source,0xccd84)[0]-0x08000000;row=table+423*28
results=[]
variants=[('first-aid',None,None,False)] if '--first-aid' in sys.argv else [('native-id-sword',None,None,False)] if '--sword' in sys.argv else [('baseline',None,None,False),('native-id',None,None,False),('blitz-both',0x70,0xa8,False)]
for name,animation,extra,knock in variants:
 rom=bytearray(source)
 if animation is not None:struct.pack_into('<H',rom,row+20,animation)
 if extra is not None:struct.pack_into('<H',rom,row+22,extra)
 if knock:rom[row+13]=0x4b
 if name.startswith('native-id'):
  rom[table+112*28:table+113*28]=rom[row:row+28]
  racebank=struct.unpack_from('<I',rom,0x257e8)[0]-0x08000000
  human=struct.unpack_from('<I',rom,racebank+4)[0]-0x08000000
  struct.pack_into('<H',rom,human+172*8+4,112)
 p=OUT/(name+'.gba');p.write_bytes(rom);e=h['Emulator'](p)
 try:
  e.load(LAB/'initial.state');e.run(1)
  e.set_memory(0xaa,struct.pack('<H',1 if name=='native-id-sword' else 453));e.set_memory(0xae,b'\x00\x00');e.set_memory(0x1b5c,b'\x8a')
  def tap(k,n=180):e.run(8,k);e.run(n)
  for index in range(4):
   for key in [32,32,256]:tap(key)
   tap(256,4500 if index==3 else 900)
  if name=='first-aid':
   e.set_memory(0x98,struct.pack('<H',49))
   for key in [32,256,32,256,256,256,256]:tap(key)
   e.screenshot(OUT/'first-aid-confirmation.png');tap(256,1800)
  else:
   for key in [256,128,128,32]:tap(key)
   tap(256,600)
   for key in [256,32,256,32,256,128,256,256]:tap(key)
   tap(256,1800)
  e.screenshot(OUT/(name+'.png'));e.save(OUT/(name+'.state'));r=e.memory()
  (OUT/(name+'.ram')).write_bytes(r);(OUT/(name+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
  results.append({'name':name,'targetHP':struct.unpack_from('<H',r,0x33fc)[0],'actorHP':struct.unpack_from('<H',r,0x98)[0],'actorEXP':r[0x8a],
                  'actorXY':list(r[0x176:0x178]),'targetXY':list(r[0x34da:0x34dc])})
  print(json.dumps(results[-1]),flush=True)
 finally:e.close()
(OUT/'report.json').write_text(json.dumps(results,indent=2))
