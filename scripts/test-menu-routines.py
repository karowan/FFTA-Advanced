"""Exercise installed Thumb menu hooks; UI rendering calls are stubbed explicitly."""
import pathlib,sys,json,hashlib
root=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INSN_INVALID
from unicorn.arm_const import *
rom=(root/'build/foundation/FFTA_vanillaplus_dev.gba').read_bytes()
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
for a,n in [(0x02000000,0x40000),(0x03000000,0x8000),(0x06000000,0x20000),(0x08000000,0x2000000)]:u.mem_map(a,n)
u.mem_write(0x08000000,rom)
stubs={0x08072130,0x08071378,0x080725b8,0x08087b30,0x08141540}
def stub(machine,address,size,data):
    if address>=0x09000000 and bytes(machine.mem_read(address,2))==b'\x00\xf8':
        target=machine.reg_read(UC_ARM_REG_LR)
        machine.reg_write(UC_ARM_REG_LR,(address+2)|1)
        machine.reg_write(UC_ARM_REG_PC,target|1)
        return
    if address in stubs:machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR)|1)
u.hook_add(UC_HOOK_CODE,stub)
def legacy_bl(machine,data):
    pc=machine.reg_read(UC_ARM_REG_PC)
    if bytes(machine.mem_read(pc,2))!=b'\x00\xf8':return False
    target=machine.reg_read(UC_ARM_REG_LR)
    machine.reg_write(UC_ARM_REG_LR,(pc+2)|1)
    machine.reg_write(UC_ARM_REG_PC,target|1)
    return True
# ARM7TDMI permits a stand-alone second half of BL. Unicorn's newer CPU rejects it.
u.hook_add(UC_HOOK_INSN_INVALID,legacy_bl)
roster=bytearray()
for i in range(24):
    unit=bytearray((i*7+j)%256 for j in range(264));unit[4]=2 if i==0 else 8 if i==1 else 1
    roster.extend(unit)
def select(slot):
    u.mem_write(0x0200fd40,bytes([slot]));u.mem_write(0x03000002,b'\x04\x00')
    u.reg_write(UC_ARM_REG_SP,0x03007000);u.reg_write(UC_ARM_REG_R5,0)
    try:u.emu_start(0x08073c3f,0x08073c78,count=20000)
    except Exception:
        print(hex(u.reg_read(UC_ARM_REG_PC)));raise
    assert u.reg_read(UC_ARM_REG_PC)==0x08073c78,'Sorting hook did not reach native continuation'
    assert u.reg_read(UC_ARM_REG_SP)==0x03007000,'Sorting stack imbalance'
cases=0
for a in range(24):
    for b in range(24):
        u.mem_write(0x02000080,bytes(roster));u.mem_write(0x02002fc4,bytes(264))
        u.mem_write(0x0200fd72,bytes(range(24)))
        u.mem_write(0x03002818,(0x02010000).to_bytes(4,'little'))
        select(a);select(b)
        expected=bytearray(roster)
        if a>=2 and b>=2 and a!=b:
            expected[a*264:(a+1)*264]=roster[b*264:(b+1)*264]
            expected[b*264:(b+1)*264]=roster[a*264:(a+1)*264]
        assert bytes(u.mem_read(0x02000080,len(roster)))==bytes(expected),f'Incorrect roster after {a},{b}'
        cases+=1
for choice,expected in enumerate([1,0,2,3]):
    u.reg_write(UC_ARM_REG_SP,0x03007000);u.reg_write(UC_ARM_REG_R0,choice)
    u.emu_start(0x0805d23d,0x0805d248,count=100)
    assert u.reg_read(UC_ARM_REG_R4)==expected,'Pub option routed incorrectly'
    assert u.reg_read(UC_ARM_REG_SP)==0x03006fe8,'Pub native prologue stack mismatch'
    cases+=1
report={'passed':True,'cases':cases,'romSha1':hashlib.sha1(rom).hexdigest(),'scope':'576 roster-selection pairs preserve all 264 bytes of each unit and keep Marche/Montblanc fixed; four pub options route correctly. Sorting UI drawing, external dispatch references and save/reload are not covered. Five native drawing/audio functions stubbed.'}
(root/'build/reports/menu-routines.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
