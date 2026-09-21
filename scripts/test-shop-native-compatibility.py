"""Compare original shop rendering/navigation with empty, short and full native tabs."""
import pathlib,runpy,struct,json,hashlib
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
OUT=ROOT/'build/expansion/probes/shop-native-compatibility';OUT.mkdir(parents=True,exist_ok=True)
ROM=OUT/'frozen.gba';ROM.write_bytes((ROOT/'build/expansion/probes/content-inventory.gba').read_bytes())
seed=(ROOT/'build/test-lab/early-town.sav').read_bytes()
def tap(e,key,wait=24):e.run(8,key);e.run(wait)
def u16(ram,n):return struct.unpack_from('<H',ram,n)[0]
def snap(e,label,wide):
 ram=e.memory();base=struct.unpack_from('<I',ram,0xf428)[0]-0x02000000
 file=OUT/(label+'.png');e.screenshot(file)
 return {'count':u16(ram,base+0xa338) if wide else ram[base+0x446d],
         'index':u16(ram,base+0xa33a) if wide else ram[base+0x44ee],
         'item':u16(ram,base+0x44ec),'scroll':u16(ram,base+0x14da),'image':str(file)}
all_samples={}
for variant,rom in [('native',ROOT/'roms/clean/FFTA_US_clean.gba'),('expanded',ROM)]:
 wide=variant=='expanded';e=h['Emulator'](rom);samples=[]
 try:
  e.set_memory(0,seed,0);e.run(3600)
  for key,wait in [(8,180),(256,60),(256,60),(256,180)]:tap(e,key,wait)
  world=OUT/(variant+'.state');e.save(world)
  for count in [0,1,4,5,252]:
   e.load(world)
   for slot in range(24):e.set_memory(0x80+slot*264+0x2a,bytes(10))
   if wide:
    fixture=bytearray(512)
    for item in list(range(1,count+1))+[265,288,253,339,362]:fixture[item]=2
   else:
    fixture=bytearray(1500)
    for item in range(1,376):struct.pack_into('<HBB',fixture,(item-1)*4,item,2 if item<=count or item in [265,288,253,339,362] else 0,0)
   e.set_memory(0x1940,bytes(fixture))
   for key,wait in [(256,240),(32,40),(256,180),(256,120),(1,120),(32,40),(256,120),(128,60),(128,120)]:tap(e,key,wait)
   for action in ['first','down','tab-return']:
    if action=='down':
     for _ in range(6):tap(e,32,16)
    elif action=='tab-return':tap(e,128,100);tap(e,64,100)
    result=snap(e,f'{variant}-{count}-{action}',wide);result.update({'size':count,'action':action});samples.append(result)

 finally:e.close()
 all_samples[variant]=samples
for a,b in zip(all_samples['native'],all_samples['expanded']):
 assert {k:v for k,v in a.items() if k!='image'}=={k:v for k,v in b.items() if k!='image'},(a,b)
 x=Image.open(a['image']);y=Image.open(b['image'])
 # Arrow animation can be one frame apart because native/C list costs differ.
 # Selection state is checked above; compare every pixel outside that arrow.
 x.paste((0,0,0),(0,48,54,240));y.paste((0,0,0),(0,48,54,240))
 x=x.tobytes();y=y.tobytes()
 assert x==y,('Native screenshot differs',a['size'],a['action'],sum(c!=d for c,d in zip(x,y)))
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'pixelComparisonsOutsideCursorAnimation':15,'sizes':[0,1,4,5,252],'actions':['first','down','tab-return'],'samples':all_samples}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print('PASS: 15 native shop image/state comparisons (cursor animation masked)')
