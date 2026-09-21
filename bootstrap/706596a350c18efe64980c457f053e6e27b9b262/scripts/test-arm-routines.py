import pathlib,sys,json,struct,hashlib
root=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
class ARM:
    def __init__(self,rom):
        self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for a,n in [(0,0x4000),(0x02000000,0x40000),(0x03000000,0x8000),(0x08000000,0x2000000)]:self.u.mem_map(a,n)
        self.u.mem_write(0x08000000,rom)
    def call(self,pc,args):
        regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
        for reg,arg in zip(regs,args):self.u.reg_write(reg,arg)
        for i,reg in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7]):self.u.reg_write(reg,0x77000000+i)
        self.u.reg_write(UC_ARM_REG_SP,0x03007000);self.u.reg_write(UC_ARM_REG_LR,0x08000101)
        self.u.emu_start(pc|1,0x08000100,count=10000)
        assert self.u.reg_read(UC_ARM_REG_PC)==0x08000100, f'Function did not return: {pc:x}'
        assert self.u.reg_read(UC_ARM_REG_SP)==0x03007000,'Stack imbalance'
        for i,reg in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7]):assert self.u.reg_read(reg)==0x77000000+i,'Callee register corruption'
        return self.u.reg_read(UC_ARM_REG_R0)
base=(root/'roms/clean/FFTA_US_clean.gba').read_bytes();patched=(root/'build/foundation/FFTA_vanillaplus_dev.gba').read_bytes()
a=ARM(base);b=ARM(patched);cases=0
for job in range(2,0x48):
    unit=bytearray(264);unit[4]=1;unit[5]=job;unit[7]=job
    for machine in (a,b):machine.u.mem_write(0x02000080,bytes(unit))
    for stat in range(48):
        original=a.call(0x080c92f0,[0x02000080,stat,0,0])
        actual=b.call(0x080c92f0,[0x02000080,stat,0,0])
        assert actual==original,f'Unmorphed stat changed: job={job:x} stat={stat:x} {original} -> {actual}'
        cases+=1
for species,monster in enumerate([0x2c,0x2e,0x31,0x33,0x36,0x38,0x3e,0x40,0x42]):
    unit=bytearray(264);unit[4]=1;unit[5]=0x1a;unit[7]=0x1a;unit[0xea]=4;unit[0xe6]=species
    for machine in (a,b):machine.u.mem_write(0x02000080,bytes(unit))
    for stat in range(48):
        original=a.call(0x080c92f0,[0x02000080,stat,0,0]);actual=b.call(0x080c92f0,[0x02000080,stat,0,0])
        if stat in (4,5,0x22,0x23):
            expected=a.call(0x080c8570,[monster,monster,stat,0])
            if stat==5 and expected==0xffff:expected=a.call(0x080c8570,[monster,monster,4,0])
            assert actual==expected,f'Morph {species} visual {stat:x}: {actual} != {expected}'
        else:assert actual==original,f'Morph changes gameplay stat {stat:x}'
        cases+=1
    assert bytes(b.u.mem_read(0x02000080,264))==bytes(unit),'Getter mutated unit'
report={'passed':True,'cases':cases,'romSha1':hashlib.sha1(patched).hexdigest(),'scope':'Real Thumb routines executed in Unicorn: 70 original jobs, 48 stat selectors, all nine morph species; stack and preserved registers checked. Not a full battle-animation or campaign test.'}
(root/'build/reports/arm-routines.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
