"""Dense projectile evidence from a completed, fresh-ROM Tomahawk fixture."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1];FAMILY=ROOT/'build/expansion/probes/tomahawk-in-game'
report=json.loads((FAMILY/'report.json').read_text());assert report['passed']
source=FAMILY/report['romSha1'];rom=source/'frozen.gba'
assert hashlib.sha1(rom.read_bytes()).hexdigest()==report['romSha1']
out=ROOT/'build/expansion/probes/tomahawk-projectile-frames'/report['romSha1'];out.mkdir(parents=True,exist_ok=True)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](rom)
try:
 e.load(source/'confirmation.state');before=e.memory()
 C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',1),4)
 e.run(8,256);frames=[]
 for frame in range(260):
  e.run(1)
  if frame>=160 and frame%4==3:
   p=out/f'frame-{frame+1:03}.png';e.screenshot(p);frames.append(p)
 e.run(1540);after=e.memory()
 for start,end in [(0x1940,0x1e70),(0x1e80,0x1e98),(0xaa,0xb4),(0x3ff44,0x40000)]:assert before[start:end]==after[start:end]
 assert struct.unpack_from('<H',after,0x9c)[0]==12 and struct.unpack_from('<H',after,0x33fc)[0]==9
finally:e.close()
canvas=Image.new('RGB',(1440,340*((len(frames)+2)//3)),'#18202b');draw=ImageDraw.Draw(canvas)
for i,p in enumerate(frames):
 x,y=i%3*480,i//3*340;canvas.paste(Image.open(p).resize((480,320)),(x,y));draw.text((x+5,y+320),p.stem,fill='white')
canvas.save(out/'projectile.png');print(json.dumps({'passed':True,'romSha1':report['romSha1'],'frames':len(frames),'output':str(out)}))
