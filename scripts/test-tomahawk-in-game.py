"""Disposable native range-four Tomahawk target/cancel/hit/miss/MP lifecycle."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1];FIX=ROOT/'build/expansion/probes/battle-fixture'
rom=(FIX/'frozen.gba').read_bytes();sha=hashlib.sha1(rom).hexdigest()
FAMILY=ROOT/'build/expansion/probes/tomahawk-in-game';OUT=FAMILY/sha;OUT.mkdir(parents=True,exist_ok=True)
ROM=OUT/'frozen.gba';ROM.write_bytes(rom);(OUT/'initial.state').write_bytes((FIX/'battle-ready.state').read_bytes())
control=bytearray(rom);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
control[0x1300e2:0x1300f2]=clean[0x1300e2:0x1300f2]
CONTROL=OUT/'native-P-control.gba';CONTROL.write_bytes(control)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));hp=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
guard=bytes([0xd7])*0xbc;invariants=None;samples=[]
def half(r,p):return struct.unpack_from('<H',r,p)[0]
def word(r,p):return struct.unpack_from('<I',r,p)[0]
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def capture(e,label):
 r=e.memory();e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'))
 (OUT/(label+'.ram')).write_bytes(r);(OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 assert r[0x3ff44:]==guard,(label,'Reserved guard')
 assert hp['heap'](r)['end']==0x0203f800
 if invariants:
  for offset,data in invariants:assert r[offset:offset+len(data)]==data,(label,'Persistent mutation',hex(offset))
 samples.append({'label':label,'actorHP':half(r,0x98),'actorMP':half(r,0x9c),'targetHP':half(r,0x33fc),'actorEXP':r[0x8a]})
 return r
e=h['Emulator'](ROM)
try:
 e.load(OUT/'initial.state');e.run(1)
 e.set_memory(0xaa,struct.pack('<H',454));e.set_memory(0xae,b'\0\0');e.set_memory(0x1b5d,b'\x8f')
 e.set_memory(0x33fc,struct.pack('<HH',250,250))
 start=capture(e,'initial')
 invariants=[(0x1940,start[0x1940:0x1e70]),(0x1e80,start[0x1e80:0x1e98]),(0xaa,start[0xaa:0xb4])]
 for turn in range(4):
  for key in [32,32,256]:tap(e,key)
  tap(e,256,4500 if turn==3 else 900)
 ready=capture(e,'marche-turn')
 assert word(ready,word(ready,0xf438)-0x02000000+0x18)==0x02000080
 assert ready[0x176:0x178]==bytes([2,13]) and ready[0x34da:0x34dc]==bytes([5,14])
 for key in [32,256,32,256,32]:tap(e,key)
 capture(e,'tomahawk-menu')
 for key in [256,128,128,128,32]:tap(e,key)
 capture(e,'range-four-target')
 tap(e,256);preview=capture(e,'preview')
 assert half(preview,0x9c)==16 and half(preview,0x33fc)==250
 tap(e,1);cancel=capture(e,'cancelled')
 assert half(cancel,0x9c)==16 and half(cancel,0x33fc)==250
 assert hp['heap'](cancel)['freePayload']>=hp['heap'](preview)['freePayload']
 tap(e,256);again=capture(e,'repreview')
 assert hp['heap'](again)['freePayload']==hp['heap'](preview)['freePayload']
 tap(e,256);capture(e,'confirmation')
 outcomes=[];seen=set();successful=None
 for seed in range(16):
  pair=[]
  for kind,path in [('native-P',CONTROL),('tomahawk',ROM)]:
   e.close();e=h['Emulator'](path);e.load(OUT/'confirmation.state')
   C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
   e.run(8,256);frames=[]
   if kind=='tomahawk':
    for frame in range(0,720,36):
     e.run(36);path=OUT/f'seed-{seed}-frame-{frame:03}.png';e.screenshot(path);frames.append(path)
    e.run(1080)
   else:e.run(1800)
   result=capture(e,f'{kind}-seed-{seed}-executed')
   assert half(result,0x9c)==12,(seed,'Expected exactly4MP',half(result,0x9c))
   assert result[0x98:0x9c]==ready[0x98:0x9c] and result[0x176:0x178]==bytes([2,13])
   assert result[0x34da:0x34dc]==bytes([5,14]),'Unexpected target displacement'
   damage=250-half(result,0x33fc);pair.append((damage,result[0x8a]))
   if kind=='tomahawk':
    strip=Image.new('RGB',(480*4,340*5),'#18202b');draw=ImageDraw.Draw(strip)
    for i,p in enumerate(frames):
     strip.paste(Image.open(p).resize((480,320)),((i%4)*480,(i//4)*340));draw.text(((i%4)*480+5,(i//4)*340+320),p.stem,fill='white')
    strip.save(OUT/f'seed-{seed}-filmstrip.png')
    for key in [32,32,256]:tap(e,key)
    tap(e,256,900);next_turn=capture(e,f'seed-{seed}-next-turn')
    assert word(next_turn,word(next_turn,0xf438)-0x02000000+0x18)==0x02000188,'Native turn did not advance'
    if damage:successful=(OUT/f'seed-{seed}-next-turn.state',next_turn)
  assert pair[1][0]==pair[0][0]*9//10,('Tomahawk coefficient versus nativeP',seed,pair)
  assert pair[0][1]==pair[1][1] and bool(pair[1][1])==bool(pair[1][0]),('Native EXP',seed,pair)
  outcomes.append(dict(seed=seed,nativeP=pair[0][0],damage=pair[1][0],experience=pair[1][1]));seen.add(pair[1][0]>0)
  if seen=={False,True}:break
 assert seen=={False,True},'Bounded native seed set did not exercise hit/miss'
 e.load(successful[0]);e.run(1);executed=successful[1]
 for key in [1,8,16,256,256]:tap(e,key)
 capture(e,'before-suspend');old=e.memory(0);tap(e,256,300);saved=e.memory(0)
 assert saved!=old,'Native suspend did not save'
 (OUT/'suspended.sav').write_bytes(saved)
finally:e.close()
e=h['Emulator'](ROM)
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
 resumed=capture(e,'cold-resumed')
 assert half(resumed,0x9c)==12 and resumed[0x33fc:0x3404]==executed[0x33fc:0x3404] and resumed[0x8a]==executed[0x8a]
 assert resumed[0x176:0x178]==bytes([2,13]) and resumed[0x34da:0x34dc]==bytes([5,14])
 tap(e,32);tap(e,256);capture(e,'resumed-action-menu');tap(e,1);capture(e,'resumed-action-cancel')
finally:e.close()
report={'passed':True,'romSha1':sha,'samples':samples,'outcomes':outcomes,'controlSha1':hashlib.sha1(control).hexdigest(),
 'checks':['Native range4 enemy target','Cancel/reopen preserves HP/MP and heap','Real hit and miss pay4MP once','No weapon consumption or movement','Native Wait/facing advances turn','SaveNow and cold Resume Battle preserve outcome and4MP payment','AP/inventory/preferences/gear and reserved guard preserved'],
 'scope':'Actual player-selected Tomahawk lifecycle; targetHP250 and bounded native RNG0..15; final coefficient compared to an independent nativeP control. Wall/height/AI list and coefficient matrices are separate native tests'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));(FAMILY/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
