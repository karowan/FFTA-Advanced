"""Read-only native combo callsite/data audit, never installs a game change."""
import json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
def calls(target):
    result=[]
    for at in range(0,0x150000,2):
        hi,lo=struct.unpack_from('<HH',rom,at)
        if hi&0xf800!=0xf000 or lo&0xf800!=0xf800:continue
        off=((hi&0x7ff)<<12)|((lo&0x7ff)<<1)
        if off&(1<<22):off-=1<<23
        if at+4+off==target:result.append(hex(at))
    return result
def dis(at,size):
    decoder=Cs(CS_ARCH_ARM,CS_MODE_THUMB);decoder.skipdata=True
    return '\n'.join(f'{i.address:08x} {i.bytes.hex():10} {i.mnemonic:8} {i.op_str}' for i in decoder.disasm(rom[at:at+size],0x8000000+at))
if len(sys.argv)>1 and sys.argv[1]=='calls':
    print(json.dumps({v:calls(int(v,0)) for v in sys.argv[2:]},indent=2))
elif len(sys.argv)>1 and sys.argv[1]=='dis':print(dis(int(sys.argv[2],0),int(sys.argv[3],0)))
else:
    print(json.dumps({hex(v):calls(v) for v in (0xcd4c0,0xcd480,0xcd50c)},indent=2))
    print(dis(0xcd4c0,0x100))
