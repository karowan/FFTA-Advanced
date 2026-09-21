"""Read-only native Thumb disassembly / BL references for lifecycle tracing."""
import pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
md.skipdata=True
if sys.argv[1]=='refs':
 targets={int(x,16)|0x08000000 for x in sys.argv[2:]}
 for p in range(0,0x160000,2):
  a,b=struct.unpack_from('<HH',rom,p)
  if a&0xf800==0xf000 and b&0xf800==0xf800:
   delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
   if delta&0x400000:delta-=0x800000
   t=0x08000000+p+4+delta
   if t in targets:print(f'{p:06X} -> {t:08X}')
else:
 start=int(sys.argv[1],16)&0x1ffffff
 end=int(sys.argv[2],16)&0x1ffffff
 for i in md.disasm(rom[start:end],0x08000000+start):
  extra=''
  if i.mnemonic=='ldr' and '[pc,' in i.op_str:
   off=int(i.op_str.split('#')[1].split(']')[0],0)
   p=((i.address+4)&~3)+off-0x08000000
   extra=f' ; [{p:06X}]={struct.unpack_from("<I",rom,p)[0]:08X}'
  print(f'{i.address:08X} {i.bytes.hex():8} {i.mnemonic:7} {i.op_str}{extra}')
