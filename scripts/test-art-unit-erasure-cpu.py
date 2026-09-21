"""Bounded ARMv4T write attribution from the retained last-intact foreground.

No video/IRQ/DMA model and no gameplay acceptance. The retained Thumb PC is
two bytes beyond the next instruction; authenticate its interrupted clear loop.
Stop rather than invent BIOS execution if reached.
"""
import collections,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
p=ROOT/'build/art/live-palette/battle/20260918T112523.117303Z'
state=(p/'last-intact.state').read_bytes();ram=(p/'last-intact.ram').read_bytes();iw=(p/'last-intact.iwram').read_bytes()
assert sha(state)=='2422186e562e73dd8ab6bb05e468adaba566940098e5b95fb556fcb77ca60ced'
assert sha(ram)=='f26237b43782a511fe1451cf2a37ff685fa94308a7043e4cca02c96c433223c5'
assert sha(iw)=='f997b20f021d3280d69db3afdfda4952c77e6afeb25e27cbfbdaea0cdf48c2ff'
meta=json.loads((p/'unit-write-trace.json').read_text());rom=Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']=='d7239a41f74eeb43325c747b5ff2f56db8dbf8cf'
registers=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC]
values=struct.unpack_from('<16I',state,0x20);cpsr=struct.unpack_from('<I',state,0x60)[0]
assert values[15]==0x03005e92 and iw[0x5e8e:0x5e96].hex()=='01c204390329fbd8'
# STM has advanced r2 but the following SUB at5E90 has not reduced r1 yet.
# Executing at saved PC, or saved PC-4, incorrectly clears one extra word.
assert values[2]+values[1]-4==values[4]+0x5684
out=ROOT/'build/art/unit-erasure-cpu'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
rows=[]
for adjustment in (-2,):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)
    for address,size in [(0,0x4000),(0x02000000,0x40000),(0x03000000,0x8000),(0x04000000,0x1000),(0x05000000,0x1000),(0x06000000,0x20000),(0x07000000,0x1000),(0x08000000,0x2000000)]:u.mem_map(address,size)
    for address,data in [(0x02000000,ram),(0x03000000,iw),(0x08000000,rom)]:u.mem_write(address,data)
    u.reg_write(UC_ARM_REG_CPSR,cpsr)
    for reg,value in zip(registers,values):u.reg_write(reg,value)
    tail=collections.deque(maxlen=32);writes=[];stop=[];invalid=[]
    def unmapped(machine,access,address,size,value,data):
        invalid.append(dict(access=access,address=address,size=size,value=value));return False
    def code(machine,address,size,data):
        tail.append(address)
        if address<0x4000:
            stop.append('BIOS execution unsupported');machine.emu_stop()
    def write(machine,address,size,value,data):
        writes.append(dict(address=address,size=size,value=value,pc=machine.reg_read(UC_ARM_REG_PC),
            registers=[machine.reg_read(r) for r in registers],tail=list(tail)))
        machine.emu_stop()
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x02000080,end=0x02000083)
    u.hook_add(UC_HOOK_MEM_INVALID,unmapped)
    error=None
    try:u.emu_start((values[15]+adjustment)|1,0,count=2000000)
    except Exception as e:error=str(e)
    rows.append(dict(savedPcAdjustment=adjustment,writes=writes,stop=stop,error=error,invalid=invalid,registers=[u.reg_read(r) for r in registers],finalPc=u.reg_read(UC_ARM_REG_PC),tail=list(tail)))
report=dict(status='observed',source=str(p),sourceRomSha1=meta['romSha1'],sourceStateSha256=sha(state),rows=rows,
    scope=__doc__)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(report=str(out/'report.json'),rows=rows),indent=2))
