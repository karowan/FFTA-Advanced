"""Read actual live renderer publication, never supply graphics or field state."""
import ctypes as C,struct,hashlib
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
FRAME=6884
def observe(e,expected=True):
 for frames in range(61):
  ram=e.memory();manager=word(ram,0xf4b0)-0x02000000;owner=0
  if 0<=manager<=len(ram)-0x440:
   pool=word(ram,manager+0x438)-0x02000000
   if 0<=pool<len(ram)-0x2660:owner=word(ram,pool+12)
  if not expected:
   if not owner:return dict(present=False,settleFrames=frames)
  elif owner:
   p=owner-0x02000000
   assert 0<=p<=0x3f000-18332 and word(ram,p)==0x31524746 and word(ram,p+4)==owner
   if word(ram,p+20) and not word(ram,p+28) and half(ram,p+FRAME+2)==1 and not ram[0x9198]:
    iw=C.string_at(*e.maps[0x03000000]);vram=C.string_at(*e.maps[0x06000000])
    bg=tuple(ram[0x7f40:0x7f42]);count=half(ram,p+FRAME)
    if all(half(iw,0x942+2*b)>>14==0 for b in bg):
     assert 1<=count<=672
     assert any(ram[p+348:p+604]),'Published frame has no field cells'
     assert vram[0x7000:0x7800]==ram[p+FRAME+4:p+FRAME+2052]
     assert vram[0x6000:0x6800]==ram[p+FRAME+2052:p+FRAME+4100]
     address=word(ram,p+FRAME+4100)-0x02000000
     assert 0<=address<=0x3f000-672*32
     assert half(ram,address-8)==0x616c
     graphics=ram[address:address+count*32]
     assert vram[:min(count,640)*32]==graphics[:640*32]
     if count>640:assert vram[0x6800:0x6800+(count-640)*32]==graphics[640*32:]
     return dict(present=True,owner=hex(owner),tiles=count,backgrounds=bg,
       cells=sum(bool(v) for v in ram[p+348:p+604]),settleFrames=frames,
       mapsSha1=hashlib.sha1(vram[0x6000:0x6800]+vram[0x7000:0x7800]).hexdigest())
  if frames<60:e.run(1)
 raise AssertionError(('Live field display did not settle',expected,hex(owner),hex(word(ram,0xf4b0)),ram[0x9198]))
