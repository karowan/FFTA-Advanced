"""Native UI rotation/blocked-center diagnostic using isolated arc ROM."""
import ctypes as C,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];LAB=ROOT/'build/expansion/probes/arc-ui-lab'
OUT=LAB/'facings';OUT.mkdir(exist_ok=True);Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
def tap(e,k,w=180):e.run(8,k);e.run(w)
def shot(e,d,n):e.screenshot(d/(n+'.png'));e.save(d/(n+'.state'));(d/(n+'.ram')).write_bytes(e.memory())
facings={0:((0,1),32),1:((-1,0),64),2:((0,-1),16),3:((1,0),128)}
records=[]
for facing,blocked,diagonal in [(d,False,False) for d in range(4)]+[(d,True,False) for d in range(4)]+[(d,'hole',False) for d in range(4)]+[(3,False,True)]:
 d=OUT/f'{facing}-blocked{blocked}-diagonal{diagonal}';d.mkdir(exist_ok=True)
 e=Emulator(LAB/'frozen.gba')
 try:
  e.load(LAB/'reaping-initial.state');e.run(1);r=e.memory();grid=struct.unpack_from('<I',r,0x7f14)[0]-0x02000000
  for y in range(13,16):
   for x in range(3):e.set_memory(grid+2*(y*16+x),bytes((2,0)))
  def place(unit,x,y):
   # Actual 0x90-byte battlefield wrappers, identified in frozen fixture.
   wrapper={0x80:0x226c4,0x188:0x22754,0x290:0x227e4,0x4a0:0x22904,0x5a8:0x22994}[unit]
   e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrapper+8,struct.pack('<3H',x*32+16,32,y*32+16))
   e.set_memory(unit+0x18,struct.pack('<HH',999,999))
  for i,unit in enumerate((0x80,0x188,0x290,0x4a0,0x5a8)):place(unit,8,8+i)
  (dx,dy),key=facings[facing];tiles=[(1+dx,14+dy),(1+dx-dy,14+dy+dx),(1+dx+dy,14+dy-dx)]
  for unit,xy in zip((0x80,0x188,0x4a0),tiles):place(unit,*xy)
  if blocked:e.set_memory(grid+2*(tiles[0][1]*16+tiles[0][0]),bytes((0 if blocked=='hole' else 5,0)))
  if blocked=='hole':place(0x80,8,13)
  shot(e,d,'initial')
  for k in (32,256,32,256,32,256,key):tap(e,k)
  if diagonal:tap(e,16)
  shot(e,d,'target');tap(e,256);shot(e,d,'preview');tap(e,256);shot(e,d,'confirmation')
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',0),4)
  tap(e,256,2400);shot(e,d,'executed');after=e.memory()
  records.append({'direction':facing,'blockedCenter':blocked,'diagonalCursor':diagonal,'tiles':tiles,'MP':struct.unpack_from('<H',after,0x398+28)[0],'HP':{hex(u):struct.unpack_from('<H',after,u+24)[0] for u in (0x80,0x188,0x4a0,0x398)}})
 finally:e.close()
 trial=bytearray((LAB/'frozen.gba').read_bytes());trial[0xa24a8:0xa24aa]=b'\xfe\xe7';trappath=d/'trap.gba';trappath.write_bytes(trial)
 e=Emulator(trappath)
 try:
  e.load(d/'confirmation.state');tap(e,256,300);shot(e,d,'members')
  regs=struct.unpack_from('<17I',(d/'members.state').read_bytes(),0x20);assert regs[15]==0x080a24aa,hex(regs[15])
  r=e.memory();obj=regs[9]-0x02000000;count=struct.unpack_from('<I',r,obj+0x2c0)[0]
  members=[]
  for i in range(min(count,15)):
   pointer=struct.unpack_from('<I',r,obj+0x20+i*0x2c)[0]
   members.append(hex(struct.unpack_from('<I',r,pointer-0x02000000)[0]) if pointer else None)
  records[-1]['count']=count;records[-1]['members']=members
 finally:e.close()
(OUT/'diagnostic.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
