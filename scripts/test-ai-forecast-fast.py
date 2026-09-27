"""Current-ROM equivalence and refusal tests for forecast hot-path changes.

Compare Viking flags to the retained pre-optimization release, including every
native status bit, equipped/unequipped reactions, KO and challenger tokens.
Exhaustively reject interior canonical record addresses. No player saves.
"""
import ast, collections, ctypes as C, hashlib, json, random, runpy, struct, sys
from pathlib import Path
from chemist_candidate import ROOT, candidate
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
meta=candidate();rom=Path(meta['path']).read_bytes();base=Path(meta['path']).parent
old_sha='b7d011755c998e23935a53d416bea252fef356ef'
old_meta=json.loads((ROOT/f'build/expansion/chemist-progressions/help/{old_sha}/manifest.json').read_text())
old_rom=Path(old_meta['path']).read_bytes();assert hashlib.sha1(old_rom).hexdigest()==old_sha
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
with E(Path(meta['path'])) as e:
    e.load(base/'fixture/battle-ready.state');ram=e.memory();iw=C.string_at(*e.maps[0x03000000])
m=ARM(rom,iw);old=ARM(old_rom,iw);checks=collections.Counter()
def check(n,a,b):
    assert a==b,(n,a,b)
    checks[n]+=1
def call(n,*args):return m.call(meta['symbols'][n],*args)
for machine in (m,old):machine.put(0x02000000,ram)
call('ffta_job_reset')
# All byte offsets through both canonical arrays, plus nearby/outside pointers.
for start,count,first in ((0x02000080,24,0),(0x02002fc4,12,24)):
    for d in range(-1,count*264+1):
        p=start+d
        wanted=0x0203f410+(first+d//264)*27 if 0<=d<count*264 and d%264==0 else 0
        check('canonical-exact-address',call('ffta_job_state',p),wanted)
        exposed=0x02001e98+first+d//264 if wanted else 0
        check('exposed-exact-address',call('ffta_state_exposed',0x02000000,p),exposed)
for p in (0,1,0x02000000,0x02040000,0x03000000,0xffffffff):
    check('outside-canonical',call('ffta_job_state',p),0)
# Both aligned native state and all unaligned staging residues; corrupt any
# one signature byte and reject it without writing or remembering old results.
for residue in range(4):
    p=0x02020000+residue
    for version in (0,1,2,255):
        for bad in range(-1,8):
            magic=bytearray(b'FFTAEXP1'+bytes([version]))
            if bad>=0:magic[bad]^=1
            m.put(p+0x1e70,magic)
            check('format-full-signature',call('ffta_storage_format',p),0 if bad>=0 else (1 if version==1 else 0xffffffff))
            check('format-read-only',m.read(p+0x1e70,9),bytes(magic))
# Actual native reaction lookup and readiness, compared with the prior binary.
unit=0x02000080
scans=[]
m.u.hook_add(UC_HOOK_CODE,lambda uc,pc,size,data:scans.append(pc),begin=0x08133adc,end=0x08133adc)
for reaction in (0,102,103):
    for status in range(-1,44):
        for hp in (0,50):
            for challenger in (0,3,37):
                for machine,symbols in ((m,meta['symbols']),(old,old_meta['symbols'])):
                    machine.put(0x02000000,ram);machine.call(symbols['ffta_job_reset'])
                    machine.put(unit+5,bytes((118,2,118)));machine.put(unit+0x35,b'\x76')
                    machine.put(unit+0x18,struct.pack('<4H',hp,100,100,100))
                    machine.put(unit+0x3a,bytes((reaction,0)));machine.put(unit+0xe8,bytes(8))
                    if status>=0:machine.put(unit+0xe8+status//8,bytes((1<<(status%8),)))
                    machine.put(0x0203f415,bytes((challenger,)))
                before=len(scans)
                got=call('ffta_viking_snapshot_flags',unit)
                expected=old.call(old_meta['symbols']['ffta_viking_snapshot_flags'],unit)
                check('viking-flags-equivalent',got,expected)
                if not reaction:check('no-reaction-no-readiness-scan',len(scans),before)
# Native permission row5 and its incapacity predicate: all 64 status positions
# (including the ignored tail bits), then reproducible combined masks.
rng=random.Random(527)
statuses=[bytes(8)]+[(1<<i).to_bytes(8,'little') for i in range(64)]+[rng.getrandbits(64).to_bytes(8,'little') for _ in range(256)]
for status in statuses:
    for hp in (0,50):
        for machine in (m,old):
            machine.put(0x02000000,ram);machine.put(unit+0xe8,status);machine.put(unit+0x18,struct.pack('<H',hp))
        check('readiness-exact-native',call('ffta_viking_reaction_ready',unit),old.call(old_meta['symbols']['ffta_viking_reaction_ready'],unit))
# Combat-only accessors must be a projection of the old complete flags, not a
# new interpretation of statuses. Exercise all byte encodings of the packed
# medicine/timer records plus native lesson selections for both new races.
for race,job,lesson_max in ((3,126,134),(5,127,126)):
    for value in range(256):
        for machine,symbols in ((m,meta['symbols']),(old,old_meta['symbols'])):
            machine.put(0x02000000,ram);machine.call(symbols['ffta_job_reset'])
            machine.put(unit+5,bytes((job,race,job)));machine.put(unit+0x35,bytes((job,)))
            machine.put(unit+0x3a,bytes((value%lesson_max,)));machine.put(unit+0x3b,bytes((value%lesson_max,)))
            machine.put(unit+0x18,struct.pack('<4H',50 if value%5 else 0,100,100,100))
            machine.put(unit+0xe8,statuses[value%len(statuses)])
            machine.put(0x0203f410+22,bytes((value,255-value)))
        expected=old.call(old_meta['symbols']['ffta_cp_flags'],unit)
        check('full-medicine-flags-equivalent',call('ffta_cp_flags',unit),expected)
        check('combat-flags-projection',call('ffta_cp_combat_flags',unit),expected&~0x1fff)
# Retain physical-chain authentication: exact allocations, retirement/reuse,
# fabricated interior tags, live independent copies and both stack residues.
# Check every individual extra flag projection against the retained full
# provider; random packed records include valid/invalid timers and field tags.
for case in range(96):
    record=bytes(rng.randrange(256) for _ in range(27))
    status=bytes(8) if case%3 else statuses[case]
    for machine,symbols in ((m,meta['symbols']),(old,old_meta['symbols'])):
        machine.put(0x02000000,ram);machine.call(symbols['ffta_job_reset'])
        machine.put(0x0203f410,record);machine.put(unit+0xe8,status)
        machine.put(unit+0x18,struct.pack('<H',0 if case%7==0 else 50))
    expected=old.call(old_meta['symbols']['ffta_integrated_extra_snapshot_flags'],unit)
    check('full-extra-flags-equivalent',call('ffta_integrated_extra_snapshot_flags',unit),expected)
    for bit in range(32):
        check('extra-flag-projection',call('ffta_action_unit_extra_flags_masked',unit,1<<bit),expected&(1<<bit))
    expected_base=old.call(old_meta['symbols']['ffta_action_unit_flags'],unit)
    for mask in (0,4,8,16,24,0x180,0x184,0x19c,0xffffffff,*[1<<b for b in range(32)]):
        check('base-flag-projection',call('ffta_action_unit_flags_masked',unit,mask),expected_base&mask)
# All native and custom R/S lesson rows for each race, including actual
# nonzero Poise/Ward/Desperation/Opportunist outcomes. Compare pure damage
# factors with the old binary; no native outcome is stubbed into the candidate.
table=struct.unpack_from('<I',rom,0xcd500)[0]-0x08000000
outcomes=collections.defaultdict(set)
for race,count,job in ((1,178,115),(2,111,118),(3,134,126),(4,118,125),(5,126,127)):
    bank=struct.unpack_from('<I',rom,table+4*race)[0]-0x08000000
    lessons=[(i,rom[bank+8*i+6]) for i in range(1,count) if rom[bank+8*i+6] in (2,3)]
    for lesson,kind in lessons:
        for variant in range(3):
            for machine,symbols in ((m,meta['symbols']),(old,old_meta['symbols'])):
                machine.put(0x02000000,ram);machine.call(symbols['ffta_job_reset'])
                for slot,u in ((0,unit),(1,0x02000188)):
                    machine.put(u+5,bytes((job,race,job)));machine.put(u+0x18,struct.pack('<4H',30,100,80,100))
                    machine.put(u+0x3a,bytes((lesson if kind==2 else 0,lesson if kind==3 else 0)))
                    machine.put(u+0x2a,struct.pack('<5H',383 if race==1 else 399,0,0,0,0))
                    machine.put(u+0xe8,bytes((0,2 if variant==1 else 0,0,32 if variant==2 else 0,0,0,0,0)))
                    machine.put(u+0x29,bytes((128 if slot else 0,)))
                    record=bytearray(27)
                    if variant:record[0:6]=bytes((2,1,1,18,2,2));record[10]=18;record[11]=1;record[14]=7
                    machine.put(0x0203f410+27*slot,record)
            for name,args in (
                ('ffta_poise_factor',(unit,)),('ffta_blade_ward_factor',(unit,0x02000188)),
                ('ffta_viking_outgoing_numerator',(unit,0x02000188,0)),
                ('ffta_drk_outgoing_numerator',(unit,0x02000188,0,1)),
                ('ffta_bard_magick_numerator',(unit,23)),
                ('ffta_turn_damage_numerator',(unit,0x02000188,0,1))):
                expected=old.call(old_meta['symbols'][name],*args)
                check('factor-equivalence-'+name,call(name,*args),expected)
                outcomes[name].add(expected)
for name,required in (('ffta_poise_factor',{3,4}),('ffta_blade_ward_factor',{13,20}),('ffta_drk_outgoing_numerator',{8,12,15}),('ffta_bard_magick_numerator',{10,13})):
    assert required<=outcomes[name],('Vacuous modifier coverage',name,outcomes[name])
# Once an action is open, projected accessors read its snapshot even after
# source mutation; an unrecorded unit returns zero, never live fallback.
m.put(0x02000000,ram);call('ffta_job_reset')
scope=0x03007400;target=0x02000398
m.put(unit+0x18,b'\x32\0');m.put(0x0203f41a,b'\x02')
check('snapshot-open',call('ffta_snapshot_begin',scope,unit,target,0),1)
frozen_base=call('ffta_action_unit_flags',unit);frozen_extra=call('ffta_action_unit_extra_flags',unit)
frozen_cp=call('ffta_action_cp_flags',unit)
m.put(unit+0xe8,b'\xff'*8);m.put(unit+0x29,b'\x80');m.put(0x0203f410,b'\xff'*27)
for mask in (0x19c,0xffffffff,1,64,0x7ffff):
    check('frozen-base-projection',call('ffta_action_unit_flags_masked',unit,mask),frozen_base&mask)
    check('frozen-extra-projection',call('ffta_action_unit_extra_flags_masked',unit,mask),frozen_extra&mask)
check('frozen-combat-projection',call('ffta_action_cp_combat_flags',unit),frozen_cp)
check('unrecorded-base',call('ffta_action_unit_flags_masked',0x020004a0,0xffffffff),0)
check('unrecorded-extra',call('ffta_action_unit_extra_flags_masked',0x020004a0,0xffffffff),0)
call('ffta_snapshot_end',scope)
for residue in (0,4):
    m.put(0x02000000,bytes(0x40000));m.put(0x02001e70,b'FFTAEXP1\x01')
    m.put(0x0200f434,struct.pack('<I',0x02018000));m.call(0x080070c8,0x02018000,0x27000)
    call('ffta_job_reset');m.put(unit,ram[0x80:0x188])
    m.put(call('ffta_job_state',unit),bytes(range(27)))
    m.put(call('ffta_owned_exposed',unit),b'\x01');m.put(call('ffta_owned_wound',unit),b'\x23\x81')
    p=m.call(meta['symbols']['ffta_evaluated_allocate'],264,stack=STACK+residue)
    check('allocated-current-size',m.call(0x0800717c,0,p),308)
    copy=struct.unpack_from('<I',rom,0x36d4bc)[0]
    m.call(copy,p,unit,264,stack=STACK+residue)
    check('owned-copy-record',m.read(call('ffta_job_state',p),27),bytes(range(27)))
    check('owned-copy-exposed',m.read(call('ffta_owned_exposed',p),1),b'\x01')
    check('owned-copy-wound',m.read(call('ffta_owned_wound',p),2),b'\x23\x81')
    scope=0x03007500
    check('stack-init',m.call(meta['symbols']['ffta_evaluated_init'],scope,p,stack=STACK+residue),1)
    check('stack-record',m.read(call('ffta_job_state',scope),27),bytes(range(27)))
    call('ffta_evaluated_close',scope);check('closed-stack',call('ffta_job_state',scope),0)
    m.call(0x08022854,p);check('freed-heap',call('ffta_job_state',p),0)
    recycled=m.call(0x08022840,308);check('reused-unregistered',call('ffta_job_state',recycled),0)
    large=m.call(0x08022840,600);fake=large+4
    m.put(fake+264,struct.pack('<II',0x31564546,fake))
    check('interior-fake-rejected',call('ffta_job_state',fake),0)
out=base/'forecast-fast';out.mkdir(exist_ok=True)
report=out/'report.json';report.write_text(json.dumps(dict(passed=True,romSha1=meta['romSha1'],baselineSha1=old_sha,checks=dict(checks)),indent=2)+'\n')
print(json.dumps(dict(passed=True,checks=dict(checks),report=str(report))))
