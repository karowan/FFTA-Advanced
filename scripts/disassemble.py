import sys,pathlib
root=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools/arm-python'))
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
b=(root/(sys.argv[3] if len(sys.argv)>3 else 'roms/clean/FFTA_US_clean.gba')).read_bytes()
start=int(sys.argv[1],0);size=int(sys.argv[2],0)
for ins in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(b[start:start+size],0x08000000+start):print(f'{ins.address:08x} {ins.bytes.hex():10} {ins.mnemonic:8} {ins.op_str}')
