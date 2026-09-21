import pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools/arm-python'))
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
b=(root/'roms/clean/FFTA_US_clean.gba').read_bytes();target=int(sys.argv[1],0);cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB);hits=[]
for i in range(0,0x150000-4,2):
    a=int.from_bytes(b[i:i+2],'little');z=int.from_bytes(b[i+2:i+4],'little')
    if a&0xf800==0xf000 and z&0xf800==0xf800:
        v=((a&0x7ff)<<12)|((z&0x7ff)<<1)
        if v&0x400000:v-=0x800000
        if i+4+v==target:hits.append(i)
print('calls',len(hits))
for i in hits[:int(sys.argv[2]) if len(sys.argv)>2 else 12]:
    print('\n',hex(i))
    for s in cs.disasm(b[i-12:i+6],0x08000000+i-12):print(hex(s.address),s.mnemonic,s.op_str)
