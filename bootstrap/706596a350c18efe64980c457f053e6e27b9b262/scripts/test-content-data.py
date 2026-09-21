"""Council-owned data and native ARM text/getter regression tests.

Runs against the data probe. This does not claim battle/AP/UI integration.
"""
import hashlib, json, pathlib, struct, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

OUT = ROOT / 'build/expansion/probes'
manifest = json.loads((OUT / 'content-data.json').read_text())
registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
ledger = json.loads((ROOT / 'notes/equipment-acquisition.json').read_text())
clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
base = (OUT / 'job-data.gba').read_bytes()
rom = (OUT / 'content-data.gba').read_bytes()
addresses = manifest['addresses']
cases = 0
failures = []

def check(condition, message):
    global cases
    cases += 1
    if not condition:
        failures.append(message)

def u16(data, offset): return struct.unpack_from('<H', data, offset)[0]
def u32(data, offset): return struct.unpack_from('<I', data, offset)[0]
def data(address, size): return rom[address - 0x08000000:address - 0x08000000 + size]

def decode_name(address):
    raw = data(address, 512)
    result = ''
    for n in range(0, len(raw), 2):
        if raw[n] == 0: return result
        prefix, value = raw[n:n+2]
        if prefix == 0x80 and 0xb0 <= value <= 0xc9: result += chr(65 + value - 0xb0)
        elif prefix == 0x80 and 0xca <= value <= 0xe3: result += chr(97 + value - 0xca)
        elif prefix == 0x80 and 0xa6 <= value <= 0xaf: result += chr(48 + value - 0xa6)
        else: result += {(0x40,0x73):' ',(0x81,0x0b):'-',(0x80,0xf4):"'",(0x80,0xe4):'.'}[(prefix,value)]
    raise AssertionError('Unterminated name')

class ARM:
    def __init__(self, image):
        self.image = image
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        for address, size in [(0x02000000,0x40000),(0x03000000,0x8000),(0x08000000,0x2000000)]:
            self.u.mem_map(address,size)
        self.u.mem_write(0x08000000,image)

    def call(self, address, *args):
        registers = [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
        saved = [UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
                 UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for reg, value in zip(registers, args): self.u.reg_write(reg,value)
        for n, reg in enumerate(saved): self.u.reg_write(reg,0x55000000+n)
        sp = 0x03007000
        for n, value in enumerate(args[4:]): self.u.mem_write(sp+4*n,struct.pack('<I',value))
        self.u.reg_write(UC_ARM_REG_SP,sp)
        self.u.reg_write(UC_ARM_REG_LR,0x08000101)
        self.u.emu_start(address|1,0x08000100,count=1000000)
        assert self.u.reg_read(UC_ARM_REG_PC)==0x08000100, ('Did not return',hex(address))
        assert self.u.reg_read(UC_ARM_REG_SP)==sp, ('Stack',hex(address))
        assert all(self.u.reg_read(reg)==0x55000000+n for n,reg in enumerate(saved)), ('ABI',hex(address))
        return self.u.reg_read(UC_ARM_REG_R0)

    def map_help(self, help_id):
        self.u.mem_write(0x02022000,b'\xff'*4)
        self.call(0x08019a50,help_id,0x02022000,0x02022002)
        raw = bytes(self.u.mem_read(0x02022000,4))
        return raw[0], u16(raw,2)

    def decode_help(self, bank, index):
        bank_pointer = u32(self.image,0x36d678+bank*4)
        self.u.mem_write(0x0201ffe0,b'\xa5'*0x3040)
        returned = self.call(0x08013e9c,0x02020000,bank_pointer,0x02021000,index,0x02022000,0x02022001)
        assert bytes(self.u.mem_read(0x0201ffe0,32))==b'\xa5'*32, 'Decoder underflow'
        assert bytes(self.u.mem_read(0x02022fe0,32))==b'\xa5'*32, 'Decoder overflow'
        return returned,bytes(self.u.mem_read(0x02020000,4096)),bytes(self.u.mem_read(0x02022000,2))

check(hashlib.sha1(rom).hexdigest()==manifest['romSha1'],'Probe hash mismatch')
check(len(registry['items'])==85 and len(registry['lessons'])==129,'Approved content cardinality')
check(data(addresses['items'],376*32)==clean[0x51d180:0x51d180+376*32], 'Original 376 equipment records including index zero changed')
check(data(addresses['teaching'],225*20)==clean[0x520080:0x520080+225*20], 'Original 225 teaching sets changed')
check(data(addresses['others'],767*4)==base[0x5567f0:0x5567f0+767*4], 'Original Other pointers changed')
for race in manifest['races']:
    check(data(race['address'],race['nativeCount']*8)==clean[race['base']:race['base']+race['nativeCount']*8], f"Original {race['name']} ability entries changed")

race_by_id = {race['id']:race for race in manifest['races']}
lesson_by_id = {lesson['id']:lesson for lesson in registry['lessons']}
ledger_by_id = {item['id']:item for item in ledger['items']}
native, foundation, patched = ARM(clean), ARM(base), ARM(rom)
covered_lessons = set()
name_table = json.loads((OUT / 'job-data.json').read_text())['addresses']['names']

for item, profile in zip(registry['items'],manifest['itemProfiles']):
    ident = item['romItemId']
    row = data(addresses['items']+ident*32,32)
    approved = ledger_by_id[item['id']]
    for field in ('name','category','weaponAttack','magicPowerBonus','basePriceGil','stageId','primaryShop','additionalShops','lessons'):
        check(item[field]==approved[field], f'{ident}: registry differs from approved {field}')
    display=next(p['displayName'] for p in manifest['itemProfiles'] if p['id']==ident)
    check(decode_name(u32(data(name_table+u16(row,0)*4,4),0))==display,f'{ident}: compact display name')
    check(next(p['helpText'] for p in manifest['itemProfiles'] if p['id']==ident).startswith(approved['name']+'. '),f'{ident}: full approved name in help')
    check(u16(row,4)==approved['basePriceGil'] and u16(row,6)==approved['basePriceGil']//2,f'{ident}: prices')
    check(row[16]==approved['weaponAttack'] and row[18]==approved['magicPowerBonus'],f'{ident}: attack/power')
    check(all(row[n]==0 for n in (9,17,19,20,21,22,23,26,27,28)),f'{ident}: unauthorized bonus/element/proc')
    donor = clean[0x51d180+profile['donor']*32:0x51d180+(profile['donor']+1)*32]
    if item['category']=='Axe':
        check(row[11]==2 and row[12]&7==0,f'{ident}: axe two-hand/Double Sword/Doublehand/Monkey Grip')
    else:
        check(row[11]==donor[11] and row[12]&7==donor[12]&7,f'{ident}: native family handedness')
    check(row[14:16]==donor[14:16],f'{ident}: donor icon removed')
    check(row[13]==donor[13],f'{ident}: donor weapon graphic parameter removed')
    check(row[24]==0,f'{ident}: leaked Nono mystery-item category')
    check(row[12]&0xf0==0,f'{ident}: leaked native random/shop tier flags')
    set_id = u16(row,29)
    check(set_id==profile['set'],f'{ident}: teaching index')
    teaching = data(addresses['teaching']+set_id*20,20)
    check(teaching[0]==len(item['teaching']) and teaching[0]<=9,f'{ident}: lesson count/capacity')
    for n, owner in enumerate(item['teaching']):
        check(tuple(teaching[2+n*2:4+n*2])==(owner['jobId'],owner['abilityIndex']),f'{ident}: teaching owner {n}')
        check(owner['lesson'] in {a['id'] for a in approved['lessons']},f'{ident}: unapproved taught lesson')
        covered_lessons.add(owner['lesson'])
    check(patched.call(0x080ca7a4,ident,0x12)==set_id,f'{ident}: native teaching getter truncates set {set_id}')
    check(patched.call(0x080ca7a4,ident,9)==u16(donor,14),f'{ident}: native icon getter')

check(covered_lessons==set(lesson_by_id),'Every approved lesson must be taught')
for lesson in registry['lessons']:
    check(decode_name(u32(data(addresses['others']+lesson['nameId']*4,4),0))==lesson['name'],f"{lesson['id']}: name text")
    for owner in lesson['owners']:
        race = race_by_id[owner['race']]
        row = data(race['address']+owner['abilityIndex']*8,8)
        check((u16(row,0),u16(row,4),row[6],row[7])==(lesson['nameId'],lesson['globalAbilityId'],lesson['nativeType'],lesson['ap']//10),f"{lesson['id']}: native race record")

for ident in range(376):
    for selector in range(19):
        check(patched.call(0x080ca7a4,ident,selector)==native.call(0x080ca7a4,ident,selector),f'{ident}: original native item getter selector {selector}')

# These four callers inline the teaching-index read instead of CA7A4. Test the
# actual blocks through the computed row pointer, including all >255 sets.
for site, stop, result_register in ((0x48ffc,0x49008,UC_ARM_REG_R0),
                                    (0x6717a,0x67186,UC_ARM_REG_R0),
                                    (0x6fc5c,0x6fc68,UC_ARM_REG_R6),
                                    (0x8c822,0x8c82e,UC_ARM_REG_R5)):
    for ident in range(461):
        u = patched.u
        sp = 0x03007000
        u.reg_write(UC_ARM_REG_SP,sp)
        u.reg_write(UC_ARM_REG_R0,addresses['items']+ident*32)
        u.reg_write(UC_ARM_REG_R1,0xdeadbeef)
        u.emu_start(0x08000000+site|1,0x08000000+stop,count=10000)
        assert u.reg_read(UC_ARM_REG_PC)==0x08000000+stop,(hex(site),'block did not return')
        assert u.reg_read(UC_ARM_REG_SP)==sp,(hex(site),'block damaged stack')
        set_id = u16(data(addresses['items']+ident*32,32),29)
        check(u.reg_read(result_register)==addresses['teaching']+20*set_id,
              f'{ident}: inlined teaching getter {site:x} truncates set {set_id}')

# The real helper picks the bank/index; the real decoder must produce identical
# original text including formatting and preserve ABI on both versions.
for help_id in range(0x650):
    original_bank = native.map_help(help_id)
    check(patched.map_help(help_id)==original_bank,f'{help_id:04x}: original help bank routing')
    # Approved foundation swaps Pub help 0028/0029 to match Missions first.
    check(patched.decode_help(*original_bank)==foundation.decode_help(*original_bank),f'{help_id:04x}: foundation native decoded help changed')

for profile in manifest['itemProfiles']:
    bank,index = patched.map_help(profile['helpId'])
    check((bank,index)==(0x13,profile['helpId']-0x1de),f"{profile['id']}: new help routing")
    decoded = patched.decode_help(bank,index)
    check(decoded[2]==b'\x00\x02',f"{profile['id']}: new help header flags")
    pointer = u32(data(addresses['help']+index*4,4),0)
    raw = data(pointer,512)
    end = raw.index(0,2)
    expected = raw[2:end+1]
    check(decoded[1][:len(expected)]==expected,f"{profile['id']}: new help body decoding")

report = {'romSha1':manifest['romSha1'],'cases':cases,'passed':not failures,'failures':failures,
          'scope':'Data contracts, native teaching/icon getter, all original/new help routing and native decoding; no battle integration claim'}
(OUT/'content-data-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if failures: raise SystemExit(1)
