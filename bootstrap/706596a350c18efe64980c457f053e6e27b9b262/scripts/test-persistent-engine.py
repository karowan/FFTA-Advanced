"""Execute compiled ARM7 persistence code, including native differential tests."""
import hashlib, json, pathlib, random, struct, sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

BASE=0x02000000
symbols={line.split()[2]:int(line.split()[0],16) for line in
         (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(line.split())==3}
binary=(ROOT/'build/expansion/engine.bin').read_bytes()
vanilla=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()

class ARM:
    def __init__(self):
        self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for address,size in [(BASE,0x40000),(0x03000000,0x8000),(0x08000000,0x2000000)]:
            self.u.mem_map(address,size)
        self.u.mem_write(0x08000000,vanilla)
        self.u.mem_write(0x09100000,binary)
    def write(self,data,offset=0): self.u.mem_write(BASE+offset,bytes(data))
    def read(self,offset=0,size=0x3ca8): return bytes(self.u.mem_read(BASE+offset,size))
    def call(self,function,*args):
        address=symbols[function] if isinstance(function,str) else function
        registers=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
               UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for r,a in zip(registers,args): self.u.reg_write(r,a)
        for i,r in enumerate(saved): self.u.reg_write(r,0x55000000+i)
        sp=0x03007000
        for i,a in enumerate(args[4:]): self.u.mem_write(sp+i*4,struct.pack('<I',a))
        self.u.reg_write(UC_ARM_REG_SP,sp)
        self.u.reg_write(UC_ARM_REG_LR,0x08000101)
        self.u.emu_start(address|1,0x08000100,count=100000)
        assert self.u.reg_read(UC_ARM_REG_PC)==0x08000100, f'No return: {function}'
        assert self.u.reg_read(UC_ARM_REG_SP)==sp, f'Stack damaged: {function}'
        for i,r in enumerate(saved): assert self.u.reg_read(r)==0x55000000+i, f'ABI damaged: {function}'
        return self.u.reg_read(UC_ARM_REG_R0)

machine=ARM()
native=ARM()
cases=0
rng=random.Random(7407)

# Sparse and full inventories, including zero-count retained records. Guard
# all other saved data and prove migration idempotence with nonzero sidecars.
for item_count in (0,1,25,375):
    state=bytearray(rng.randbytes(0x3ca8))
    state[0x1940:0x1f1c]=bytes(1500)
    expected=bytearray(512)
    order=list(range(1,376));rng.shuffle(order)
    for i,item in enumerate(order[:item_count]):
        owned=rng.randrange(100);equipped=rng.randrange(owned+1)
        struct.pack_into('<HBB',state,0x1940+i*4,item,owned,equipped)
        expected[item]=owned
    for staging in (0,0x3cb0):
        machine.write(state,staging)
        assert machine.call('ffta_migrate_inventory',BASE+staging)==1
        result=machine.read(staging)
        assert result[:0x1940]==state[:0x1940] and result[0x1f1c:]==state[0x1f1c:]
        assert result[0x1940:0x1b40]==expected
        assert result[0x1b40:0x1e70]==bytes(816)
        assert machine.call('ffta_storage_format',BASE+staging)==1
        machine.write(bytes([0x57])*816,staging+0x1b40)
        before=machine.read(staging)
        assert machine.call('ffta_migrate_inventory',BASE+staging)==0
        assert machine.read(staging)==before
        cases+=1

# Invalid data/version must leave every input byte intact.
bad_records=[[(376,1,0)],[(1,100,0)],[(1,2,3)],[(1,2,0),(1,3,0)],[(1,0,0),(1,0,0)]]
for records in bad_records:
    state=bytearray(0x3ca8)
    for i,record in enumerate(records):struct.pack_into('<HBB',state,0x1940+i*4,*record)
    machine.write(state)
    assert machine.call('ffta_migrate_inventory',BASE)==0xffffffff
    assert machine.read()==state
    cases+=1
state=bytearray(0x3ca8);state[0x1e70:0x1e79]=b'FFTAEXP1\x02'
machine.write(state)
assert machine.call('ffta_migrate_inventory',BASE)==0xfffffffe
assert machine.read()==state
cases+=1

# Compare real native give/lose behavior across every original item. Quantities
# here avoid native >255 sum wraparound; expanded code deliberately prevents it.
for item in range(1,376):
    offset=0x1ee4 if 362<=item<=375 else 0x1940
    for owned in (0,1,98,99):
        for quantity in (0,1,3,99):
            for function,address in [('ffta_give_item',0x080ca900),('ffta_lose_item',0x080ca9e8)]:
                new=bytearray(0x3ca8);new[0x1940+item]=owned
                old=bytearray(0x3ca8);struct.pack_into('<HBB',old,offset,item,owned,0)
                machine.write(new);native.write(old)
                expected_return=native.call(address,item,quantity)
                returned=machine.call(function,BASE,item,quantity)
                assert returned==expected_return,(function,item,owned,quantity,returned,expected_return)
                assert machine.read(0x1940+item,1)==native.read(offset+2,1)
                new[0x1940+item]=native.read(offset+2,1)[0]
                assert machine.read()==new, 'Inventory operation damaged unrelated state'
                cases+=1

for item in (376,397,460):
    state=bytearray(0x3ca8);state[0x1940+item]=98;machine.write(state)
    assert machine.call('ffta_give_item',BASE,item,255)==254
    assert machine.read(0x1940+item,1)==b'\x63'
    assert machine.call('ffta_lose_item',BASE,item,255)==0
    assert machine.read(0x1940+item,1)==b'\x00'
    assert machine.call('ffta_lose_item',BASE,item,1)==0
    assert machine.read(0x1940+item,1)==b'\x00'
    cases+=1
for item in (0,461,511,65535):
    state=bytes(0x3ca8);machine.write(state)
    assert machine.call('ffta_give_item',BASE,item,1)==0xffffffff
    assert machine.call('ffta_lose_item',BASE,item,1)==0xffffffff
    assert machine.read()==state
    cases+=1

# Every new lesson has an in-bounds address. Reserved and foreign pointers do
# not alias a real unit; AP addresses in staging map to staging, not live state.
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
for staging in (0,0x3cb0):
    for slot in range(24):
        unit=0x80+slot*264
        for race in range(1,6):
            state=bytearray(0x3ca8);state[unit+6]=race;machine.write(state,staging)
            count=registry['races'][race-1]['totalCount']
            for index in range(180):
                actual=machine.call('ffta_party_ap_address',BASE+staging,BASE+staging+unit,index)
                if index==0 or index>=count or (race==1 and index in (142,143)): expected=0
                elif race==1 and index>=144: expected=BASE+staging+0x1b40+slot*34+index-144
                else: expected=BASE+staging+unit+0x40+index
                assert actual==expected,(staging,slot,race,index,actual,expected)
                cases+=1
for pointer in (BASE+0x81,BASE+0x7f,BASE+0x1940,BASE+0x2fc4,0x03001000):
    assert machine.call('ffta_party_ap_address',BASE,pointer,144)==0
    cases+=1

# Sorting carries AP and pre-battle potion preference, without touching any
# native unit bytes. Clear removes only the departed unit's extension state.
for a in range(24):
    for b in range(24):
        state=bytearray(rng.randbytes(0x3ca8));state[0x1e70:0x1e79]=b'FFTAEXP1\x01';expected=bytearray(state)
        left=0x1b40+a*34;right=0x1b40+b*34
        expected[left:left+34],expected[right:right+34]=state[right:right+34],state[left:left+34]
        expected[0x1e80+a],expected[0x1e80+b]=state[0x1e80+b],state[0x1e80+a]
        expected[0x1e98+a],expected[0x1e98+b]=state[0x1e98+b],state[0x1e98+a]
        expected[0x1ebc+2*a:0x1ebe+2*a],expected[0x1ebc+2*b:0x1ebe+2*b]=state[0x1ebc+2*b:0x1ebe+2*b],state[0x1ebc+2*a:0x1ebe+2*a]
        machine.write(state)
        assert machine.call('ffta_swap_extra',BASE,a,b)==1
        assert machine.read()==expected
        assert machine.call('ffta_clear_extra',BASE,a)==1
        expected[left:left+34]=bytes(34);expected[0x1e80+a]=0;expected[0x1e98+a]=0
        expected[0x1ebc+2*a:0x1ebe+2*a]=bytes(2)
        assert machine.read()==expected
        cases+=1

# Recipe transactions prove no partial payment, no mission-item substitution,
# duplicate-ingredient accounting, and exclusion of equipped copies.
recipes=[([362,374],[1,1],[0,0],{362:1,374:1},True),
         ([362,374],[1,1],[0,0],{362:1,374:0},False),
         ([362,362],[1,1],[0,0],{362:1},False),
         ([362,362],[1,1],[0,0],{362:2},True),
         ([362,374],[1,1],[1,0],{362:1,374:1},False),
         ([362,397],[1,1],[0,0],{362:1,397:99},False)]
for ids,amounts,equipped,owned,succeeds in recipes:
    state=bytearray(0x3ca8)
    for item,count in owned.items():state[0x1940+item]=count
    machine.write(state)
    machine.write(struct.pack('<'+'H'*len(ids),*ids),0x10000)
    machine.write(bytes(amounts),0x10100);machine.write(bytes(equipped),0x10200)
    actual=machine.call('ffta_pay_recipe',BASE,BASE+0x10000,BASE+0x10100,BASE+0x10200,len(ids))
    assert actual==int(succeeds)
    if succeeds:
        for item,count in zip(ids,amounts):state[0x1940+item]-=count
    assert machine.read()==state
    cases+=1

# Compatibility views preserve native reader contracts with an explicit
# 446-equipment/14-consumable split and no writes past the 1840-byte view.
state=bytearray(0x3ca8)
state[0x1e70:0x1e79]=b'FFTAEXP1\x01'
equipped_counts={}
for slot in range(24):
    unit=0x80+slot*264;state[unit+4]=1
    for gear in range(5):
        item=(slot*19+gear*37)%460+1
        struct.pack_into('<H',state,unit+0x2a+gear*2,item)
        equipped_counts[item]=equipped_counts.get(item,0)+1
for item in range(1,461):state[0x1940+item]=(item*7)%100
machine.write(state)
machine.write(b'\xa5'*1856,0x3f800)
result=machine.call('ffta_inventory_view',BASE,0,BASE+0x10000,BASE+0x3f800)
assert result==BASE+0x3f800
assert struct.unpack('<I',machine.read(0x10000,4))[0]==446
for item in range(1,461):
    index=item-1 if item<=361 else 446+item-362 if item<=375 else item-15
    assert struct.unpack('<HBB',machine.read(0x3f800+index*4,4))==(item,state[0x1940+item],equipped_counts.get(item,0))
    assert machine.call('ffta_free_count',BASE,item)==max(0,state[0x1940+item]-equipped_counts.get(item,0))
    cases+=1
assert machine.read(0x3f800+1840,16)==b'\xa5'*16
assert machine.read()==state
assert machine.call('ffta_inventory_view',BASE,362,BASE+0x10000,BASE+0x3f800)==BASE+0x3f800+446*4
assert struct.unpack('<I',machine.read(0x10000,4))[0]==14
for item in range(376):
    assert machine.call('ffta_native_is_weapon',item)==native.call(0x080cb1f4,item)
    cases+=1
for item in (1,362,376,460):
    index=item-1 if item<=361 else 446+item-362 if item<=375 else item-15
    old=machine.read(0x1940+item,1)[0]
    assert machine.call('ffta_native_give_item',item,1)==max(0,old+1-99)
    assert machine.read(0x3f800+index*4+2,1)==machine.read(0x1940+item,1)
    assert machine.call('ffta_native_lose_item',item,2)==0
    assert machine.read(0x3f800+index*4+2,1)==machine.read(0x1940+item,1)
    cases+=1

# The actual load shims validate staging before live-state commit. Check both
# normal/suspend routes, both common stack alignments, and error continuations.
for name,success,failure in [('ffta_load_normal',0x0813aa50,0x0813aa30),
                             ('ffta_load_suspend',0x0813aae0,0x0813aaca)]:
    for bad in (False,True):
        for alignment in (0,4):
            live=rng.randbytes(0x3ca8);staging=bytearray(0x3ca8)
            if bad:struct.pack_into('<HBB',staging,0x1940,500,1,0)
            machine.write(live);machine.write(staging,0x3cb0)
            sp=0x03007000+alignment
            machine.u.reg_write(UC_ARM_REG_SP,sp)
            machine.u.reg_write(UC_ARM_REG_LR,0x08001235)
            machine.u.reg_write(UC_ARM_REG_R5,BASE+0x3cb0)
            machine.u.reg_write(UC_ARM_REG_R6,0x66000000)
            machine.u.reg_write(UC_ARM_REG_R7,0x77000000)
            end=failure if bad else success
            machine.u.emu_start(symbols[name]|1,end,count=100000)
            assert machine.u.reg_read(UC_ARM_REG_PC)==end
            assert machine.u.reg_read(UC_ARM_REG_SP)==sp
            assert machine.u.reg_read(UC_ARM_REG_R6)==0x66000000
            assert machine.u.reg_read(UC_ARM_REG_R7)==0x77000000
            assert machine.read()==live,'Rejected or uncommitted load modified live game'
            if bad:assert machine.read(0x3cb0)==staging
            else:
                assert machine.u.reg_read(UC_ARM_REG_R0)==BASE+0x3cb0
                assert machine.u.reg_read(UC_ARM_REG_R1)==BASE
                assert machine.u.reg_read(UC_ARM_REG_R2)==0x1e54
                assert machine.read(0x3cb0+0x1e70,9)==b'FFTAEXP1\x01'
            cases+=1

report={'passed':True,'cases':cases,'engineSha1':hashlib.sha1(binary).hexdigest(),
        'checks':['Compiled ARM code, stack and r4-r11 preservation',
                  'Sparse/full migration, staging state, rejection without writes, idempotence',
                  'Original give/lose differential execution for all375 native items',
                  'Expanded item bounds, saturation, no quantity underflow',
                  'Every party/race/AP address and all24x24 sidecar swaps',
                  'Atomic recipe payment and mission-item exclusion',
                  'Compatibility view, retained-pointer updates and native weapon predicate',
                  'Normal/suspend load success/rejection preserves live state before commit'],
        'limitations':['Engine is not yet hooked into the expansion ROM',
                       'Native inventory consumer port and AP lifecycle integration remain']}
(ROOT/'build/expansion/persistent-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
