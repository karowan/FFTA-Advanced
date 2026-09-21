"""Native icon decoding: equipment-context donor mapping without quest changes."""
import hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/probes'
manifest=json.loads((OUT/'content-data.json').read_text())
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
rom=(OUT/'content-data.gba').read_bytes()
donors={p['id']:p['donor'] for p in manifest['itemProfiles']}
cases=0;failures=[]

class ARM:
    def __init__(self,image):
        self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for a,s in [(0x02000000,0x40000),(0x03000000,0x8000),(0x08000000,0x2000000)]:self.u.mem_map(a,s)
        self.u.mem_write(0x08000000,image)
    def icon(self,address,ident,draw,block=False,mode=4):
        u=self.u;sp=0x03007000;destination=0x02024040
        u.mem_write(0x02024000,b'\xa5'*512)
        u.mem_write(0x02025000,bytes(8)+bytes([mode])+bytes(7))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
               UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        values=[0x55000000+n for n in range(8)];values[1]=0x02025000
        for r,v in zip(saved,values):u.reg_write(r,v)
        u.reg_write(UC_ARM_REG_R0,destination if draw else ident)
        u.reg_write(UC_ARM_REG_R1,ident if draw else 0x12345678)
        u.reg_write(UC_ARM_REG_SP,sp)
        u.reg_write(UC_ARM_REG_LR,0x08000101)
        stop=address+4 if block else 0x08000100
        u.emu_start(address|1,stop,count=100000)
        assert u.reg_read(UC_ARM_REG_PC)==stop,('No return',hex(address),ident)
        assert u.reg_read(UC_ARM_REG_SP)==sp,('Stack',hex(address),ident)
        assert all(u.reg_read(r)==v for r,v in zip(saved,values)),('ABI',hex(address),ident)
        assert bytes(u.mem_read(0x02024000,64))==b'\xa5'*64,'Icon underflow'
        assert bytes(u.mem_read(0x020240c0,320))==b'\xa5'*320,'Icon overflow'
        return bytes(u.mem_read(destination,128)) if draw else u.reg_read(UC_ARM_REG_R0)

def check(condition,label):
    global cases
    cases+=1
    if not condition:failures.append(label)

native,patched=ARM(clean),ARM(rom)
expected={}
for ident in range(461):
    for draw in (False,True):
        fn=0x080cb980 if draw else 0x080cb99c
        expected[ident,draw]=native.icon(fn,ident,draw)
        check(patched.icon(fn,ident,draw)==expected[ident,draw],f'Generic icon API changed for {ident}, draw={draw}')

# Native callers proven to use equipment records/party equipment slots.
sites=((0x8160e,False),(0x8168a,True),(0x7031c,True),(0x70370,False),(0x70392,False),
       (0x749b0,False),(0x749e8,True),(0x8e3de,False),(0x8e3f2,True),(0x67514,False),(0x6e6a4,True),(0x6e81e,False))
for site,draw in sites:
    for ident in range(461):
        check(patched.icon(0x08000000+site,ident,draw,block=True)==expected[donors.get(ident,ident),draw],
              f'Equipment icon call {site:x}, item {ident}, draw={draw}')

# Shared shop draw: mode4 is equipment; modes5/6 are quest/mystery contexts.
for mode in (4,5,6):
    for ident in range(461):
        expected_id=donors.get(ident,ident) if mode==4 else ident
        check(patched.icon(0x0806796e,ident,True,block=True,mode=mode)==expected[expected_id,True],
              f'Shop icon mode {mode}, item {ident}')

report={'romSha1':hashlib.sha1(rom).hexdigest(),'cases':cases,'passed':not failures,'failures':failures,
        'scope':'Actual native icon pixels/palettes and context callsites; generic quest IDs preserved; no new axe artwork claim'}
(OUT/'equipment-icon-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({**report,'failures':failures[:12],'totalFailures':len(failures)},indent=2))
if failures:raise SystemExit(1)
