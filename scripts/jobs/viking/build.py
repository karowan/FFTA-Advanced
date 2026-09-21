"""Compose explicit Viking consumers over the reproducible private Samurai base.

Never rewrite the accepted engine or infer completion from allocated lessons.
The manifest enumerates enabled behavior and outstanding requirements.
"""
import hashlib
import json
import pathlib
import struct
import subprocess
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[3]
P = ROOT / 'build/expansion/probes'
sha = lambda b: hashlib.sha1(b).hexdigest()
samurai = json.loads((P / 'samurai/current.json').read_text())
parent = json.loads((P / 'job-state/current.json').read_text())
base = pathlib.Path(parent['path']).read_bytes()
assert sha(base) == parent['romSha1']
clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
rom = bytearray(base)
assert rom[0x1240000:0x1280000] == b'\xff' * 0x40000, 'Viking reservation is occupied'
table = struct.unpack_from('<I', rom, 0xccd84)[0] - 0x08000000
changes = []
work = P / 'viking-code'
work.mkdir(exist_ok=True)
prefix = str(ROOT / 'tools/arm-gnu/bin/arm-none-eabi-')
elf = work / 'viking.elf'
binary = work / 'viking.bin'
sources = [ROOT / 'src/engine/viking.c', ROOT / 'src/engine/viking.s', ROOT/'src/engine/viking-state.c', ROOT/'src/engine/viking-status-display.c', ROOT/'src/engine/viking-damage.c', ROOT/'src/engine/viking-tsunami.c', ROOT/'src/engine/viking-reactions.c']
samurai_work = pathlib.Path(samurai['path']).parent.parent
combat=(samurai_work/'combat.c').read_text()
start=combat.index('typedef struct { unsigned action,numerator,denominator; }')
end=combat.index('/* Same ordered search',start)
final=combat[combat.index('int ffta_physical_final('):]
final=final.replace('ffta_physical_final(', 'ffta_viking_shared_final(')
old='/(definition->denominator*1600u)'
assert old in final
final=final.replace(old,'*((reference>0 && !restorative)?ffta_viking_outgoing_numerator(actor,target,action):1000)/(definition->denominator*1600000u)')
imports='\n'.join('extern '+x+';' for x in [
 'unsigned ffta_primary_weapon(const uint8_t *)','unsigned ffta_finisher_numerator(unsigned,const uint8_t *)',
 'unsigned ffta_exposed_incoming_numerator(int,const uint8_t *)','unsigned ffta_viking_outgoing_numerator(const uint8_t *,const uint8_t *,unsigned)'])
(work/'shared-final.c').write_text('#include <stdint.h>\n#include "registry.h"\n#include "action-snapshot.h"\n#include "execution-scope.h"\n'+imports+'\n'+combat[start:end]+final)
sources.append(work/'shared-final.c')

asm = (samurai_work/'combat-hooks.s').read_text()
for reg,value,label in [('r0','r1','8f'),('r2','r0','9f')]:
    original=f'    ldr {reg},=FFTA_DRK_A2'
    assert asm.count(original)==1
    asm=asm.replace(original,''.join(f'    ldr {reg},=FFTA_VIK_A{a}\n    cmp {value},{reg}\n    beq {label}\n' for a in (3,6))+original)
for name in ('physical_final','physical_eligibility','physical_magnitude','weapon_drain','weapon_effect'):
    asm=asm.replace('ffta_'+name,'ffta_viking_'+name)
(work/'physical-hooks.s').write_text(asm)
stage=(ROOT/'src/engine/exposed-effects.s').read_text().split('.global ffta_exposed_combo_entry')[0]
stage=stage.replace('ffta_exposed_', 'ffta_viking_exposed_').replace('ffta_original_exposed_preview','ffta_viking_original_exposed_preview')
(work/'stage-hooks.s').write_text(stage)
status_asm=(ROOT/'src/engine/status-display.s').read_text().replace('ffta_status_', 'ffta_viking_status_').replace('ffta_original_status_icon','ffta_unused_viking_original_status_icon')
(work/'status-hooks.s').write_text(status_asm)
sources.append(work/'status-hooks.s')
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'
names={name:'ffta_'+name.removeprefix('ffta_previous_') for name in ('ffta_previous_physical_eligibility','ffta_previous_physical_magnitude','ffta_previous_physical_final','ffta_previous_exposed_native_stage')}
names.update({name:name for name in ('ffta_primary_weapon','ffta_exposed_incoming_numerator','ffta_poise_hp_factor','ffta_blade_ward_factor')})
names.update({name:name for name in ('ffta_job_state','ffta_job_origin','ffta_job_peers')})
names.update({name:name for name in ('ffta_action_phase','ffta_action_id','ffta_action_hp_lost','ffta_action_unit_flags','ffta_action_origin','ffta_snapshot_begin','ffta_snapshot_end','ffta_exposed_native_physical','ffta_finisher_numerator','ffta_centered_factor','ffta_execution_capture','ffta_action_result_object','ffta_action_reactions_enabled','ffta_action_category','ffta_action_actor','ffta_action_claim','ffta_action_claimed','ffta_action_unit_at','ffta_reaction_queue_append','ffta_action_reaction_kind','ffta_action_reaction_value')})
names.update(ffta_previous_centered_event='ffta_centered_event',ffta_previous_centered_turn_end='ffta_centered_turn_end')
names.update({f'ffta_previous_viking_status_{name}':f'ffta_wound_status_{name}' for name in ('icon','next_key','visual')})
for name,previous in names.items():
    bindings+=f'.align 2\n.global {name}\n.thumb_func\n{name}:\n push {{r3}}\n ldr r3,={parent["symbols"][previous]|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(work/'bindings.s').write_text(bindings)
native_callbacks={'ELIGIBILITY':0x3a8604+15*4,'ACCURACY':0x3a8678+14*4,'ACCESSORY':0x3a86f8+7*4,'ARMOR':0x3a86f8+15*4,'APPLY':0x3a87b0+59*12}
(work/'viking-native.h').write_text('\n'.join(f'#define VIK_NATIVE_THEFT_{key} 0x{struct.unpack_from("<I",base,offset)[0]:08x}u' for key,offset in native_callbacks.items())+f'\n#define VIK_NATIVE_ZERO_MAGNITUDE 0x{struct.unpack_from("<I",base,0x3a86f8)[0]:08x}u\n#define VIK_APPLICATION_BANK 0x09260400u\n')
sources += [work/'physical-hooks.s',work/'stage-hooks.s',work/'bindings.s']
subprocess.run([prefix+'gcc.exe', '-mcpu=arm7tdmi', '-mthumb', '-Os', '-std=c11',
                '-ffreestanding', '-fno-builtin', '-Wall', '-Wextra', '-Werror',
                '-nostdlib', '-I', str(ROOT/'src/engine'), '-I', str(ROOT/'build/expansion'), '-I', str(work),
                '-Wl,-Ttext=0x09240000,-e,ffta_viking_compatibility_entry',
                *map(str,sources), '-lgcc', '-o', str(elf)], check=True)
subprocess.run([prefix+'objcopy.exe', '-O', 'binary', str(elf), str(binary)], check=True)
symbols = {p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
# Install the shared native entry directly; a C import veneer would clobber r12.
symbols['ffta_reaction_queue_entry']=parent['symbols']['ffta_reaction_queue_entry']
code = binary.read_bytes()
assert len(code) < 0x20000
rom[0x1240000:0x1240000+len(code)] = code
# Shared optional providers have independently reserved 16-byte stubs. Root
# combines job providers instead of letting job overlays replace one another.
for prior,replacement in [('ffta_additional_snapshot_flags','ffta_viking_snapshot_flags'),('ffta_additional_beneficial','ffta_viking_war_cry'),('ffta_additional_action_category','ffta_viking_action_category'),('ffta_additional_action_event','ffta_viking_action_event'),('ffta_additional_hp_loss','ffta_viking_hp_loss'),('ffta_additional_reaction_queue','ffta_viking_reaction_queue')]:
    offset=parent['symbols'][prior]-0x08000000
    assert offset%4==0 and rom[offset:offset+16]==bytes.fromhex('00207047')+bytes(12),(prior,rom[offset:offset+16].hex())
    rom[offset:offset+8]=struct.pack('<HHI',0x4b00,0x4718,symbols[replacement]|1)
    changes.append(dict(name=prior,offset=offset,provider=replacement,size=8))

def hook(offset,end,name,previous=None):
    jump=(offset+5)&~3
    if previous:
        assert struct.unpack_from('<I',rom,jump+4)[0]==parent['symbols'][previous]|1,(hex(offset),previous)
    else:assert rom[offset:end]==clean[offset:end]
    original=rom[offset:end].hex()
    rom[offset:end]=b'\xc0\x46'*((end-offset)//2)
    struct.pack_into('<H',rom,offset,0xb408)
    struct.pack_into('<HHI',rom,jump,0x4b00,0x4718,symbols[name]|1)
    changes.append(dict(name=name,offset=offset,size=end-offset,original=original))
hook(0x133a58,0x133a64,'ffta_viking_compatibility_entry')
hook(0x131220,0x13122c,'ffta_viking_status_accuracy_entry')
hook(0xa4adc,0xa4ae8,'ffta_reaction_queue_entry')
hook(0x130200,0x13020c,'ffta_viking_exposed_preview_entry','ffta_exposed_preview_entry')
assert rom[0x97098:0x9709c]==bytes.fromhex('f3235b00')
changes.append(dict(name='shared-status-OBJ-pool',offset=0x97098,original='f3',replacement='f8',vikingTiles=[0x1ec,0x1ef]))
rom[0x97098]=0xf8
assert struct.unpack_from('<I',rom,0x9da10)[0]==parent['symbols']['ffta_status_icon_entry']|1
struct.pack_into('<I',rom,0x9da10,symbols['ffta_viking_status_icon_entry']|1)
hook(0x9dd52,0x9dd62,'ffta_viking_status_next_entry','ffta_status_next_entry')
hook(0x97ad0,0x97ae4,'ffta_viking_status_visual_entry','ffta_status_visual_entry')
for offset,end,name in [(0x1300e2,0x1300f2,'physical_final'),(0x130654,0x130660,'weapon_drain'),(0x130688,0x130694,'weapon_effect'),(0x131b4a,0x131b56,'exposed_stage')]:
    hook(offset,end,'ffta_viking_'+name+'_entry','ffta_'+name+'_entry')
for offset,name in [(0x3a8604+8*4,'physical_eligibility'),(0x3a86f8+30*4,'physical_magnitude')]:
    assert struct.unpack_from('<I',rom,offset)[0]==parent['symbols']['ffta_'+name+'_entry']|1
    struct.pack_into('<I',rom,offset,symbols['ffta_viking_'+name+'_entry']|1)
struct.pack_into('<I',rom,0x3a86f8,symbols['ffta_viking_zero_magnitude_entry']|1)
for key,offset in native_callbacks.items():
    struct.pack_into('<I',rom,offset,symbols['ffta_viking_theft_'+key.lower()+'_entry']|1)

# Rebind callers, preserving original targets for explicit delegation. Parent
# modules and the accepted engine are bounded by their actual binary extents.
regions=[(0x1100000,len((ROOT/'build/expansion/engine.bin').read_bytes())),
         (0x11c0000,len((samurai_work/'samurai.bin').read_bytes())),
         (0x11d0000,len((P/'job-state'/parent['baseSha1']/'state.bin').read_bytes()))]
for original,replacement in [('ffta_centered_event','ffta_viking_lifecycle_event'),
                             ('ffta_centered_turn_end','ffta_viking_lifecycle_turn_end')]:
    target=parent['symbols'][original]&~1;sites=[]
    for start,length in regions:
        for offset in range(start,start+length-2,2):
            a,b=struct.unpack_from('<HH',rom,offset)
            if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
            delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
            if delta&0x400000:delta-=0x800000
            if 0x08000000+offset+4+delta!=target:continue
            replacement_delta=(symbols[replacement]&~1)-(0x08000000+offset+4)
            assert -0x400000<=replacement_delta<0x400000
            struct.pack_into('<HH',rom,offset,0xf000|((replacement_delta>>12)&0x7ff),0xf800|((replacement_delta>>1)&0x7ff));sites.append(offset)
        for offset in range(start,start+length-3,4):
            if struct.unpack_from('<I',rom,offset)[0]==target|1:
                struct.pack_into('<I',rom,offset,symbols[replacement]|1);sites.append(offset)
    assert sites,('No lifecycle callers rebound',original)
    changes.append(dict(name=replacement,originalTarget=target,sites=sites))

def relocate_bank(old_offset,count,stride,new_offset,extra,expected_users):
    bank=bytearray(rom[old_offset:old_offset+count*stride])+bytearray(extra*stride)
    original_address=0x08000000+old_offset;users=[]
    for offset in range(0,len(clean)-3,4):
        if struct.unpack_from('<I',rom,offset)[0]==original_address:
            struct.pack_into('<I',rom,offset,0x08000000+new_offset);users.append(offset)
    assert set(users)==set(expected_users),(hex(old_offset),list(map(hex,users)))
    changes.append(dict(name='native bank relocation',source=old_offset,offset=new_offset,users=users))
    return bank

descriptors=relocate_bank(0x553e70,209,4,0x1260000,14,[0xb4cec,0xc1ca4,0xc230c,0x12f2a0,0x12f348,0x12f3c8])
applications=relocate_bank(0x3a87b0,93,12,0x1260400,9,[0x1323b8,0x132430,0x133920,0x133984,0x1339a4])
masks=relocate_bank(0x52790c,93,12,0x1260c00,9,[0x1339c8])
descriptors[211*4:212*4]=bytes([8,93,23,0])
descriptors[212*4:213*4]=bytes([8,94,21,0])
descriptors[218*4:219*4]=bytes([8,99,23,0])
descriptors[221*4:222*4]=bytes([8,100,23,0])
descriptors[222*4:223*4]=bytes([8,101,23,0])
for kind,name,sign in [(93,'war_cry',255),(94,'challenged',1),(99,'tsunami',0),(101,'gil_reaction',1)]:
    struct.pack_into('<III',applications,kind*12,symbols['ffta_viking_'+name+'_apply_entry']|1,0,sign)
    mask=bytearray(masks[82*12:83*12])
    for status in range(44):mask[(2*status+1)//8]&=~(1<<((2*status+1)%8))
    if kind==93:
        for status in (10,27,28):mask[(2*status+1)//8]|=1<<((2*status+1)%8)
    masks[kind*12:(kind+1)*12]=mask
applications[100*12:101*12]=applications[21*12:22*12]
struct.pack_into('<I',applications,100*12+8,255)
masks[100*12:101*12]=masks[101*12:102*12]
for offset,bank in [(0x1260000,descriptors),(0x1260400,applications),(0x1260c00,masks)]:
    assert rom[offset:offset+len(bank)]==b'\xff'*len(bank)
    rom[offset:offset+len(bank)]=bank

def install(ident, donor, edits):
    lesson = next(x for x in registry['lessons'] if x['id'] == ident)
    action = lesson['globalAbilityId']
    row = bytearray(clean[0x55187c + donor * 28:0x55187c + (donor + 1) * 28])
    struct.pack_into('<H', row, 0, lesson['nameId'])
    # The racial lesson record owns contextual help. Do not retain a donor's
    # spell-specific help in the global record.
    struct.pack_into('<H', row, 22, 0)
    for offset, value in edits.items():
        row[offset] = value
    if ident != 'VIK-A2':
        # Preserve native magical, Reflect and Return Magic classification;
        # Reaving cannot be enumerated as a Doublecast spell command.
        flags = struct.unpack_from('<I', row, 16)[0]
        flags &= ~(1 << (19-11))
        if ident in ('VIK-A4','VIK-A9'):
            # Native usable predicate 133E18 consults flag20 under Silence.
            # These vocal/weapon-free commands retain their approved bypass.
            flags |= 1 << (20-11)
        if ident=='VIK-A8':flags &= ~((1 << (18-11)) | (1 << (26-11)))
        # Native AI C241C rejects self without selector11, even though the
        # executed self-centered cross already includes the caster.
        if ident=='VIK-A4':flags |= 1
        struct.pack_into('<I',row,16,flags)
    offset = table + action * 28
    assert not any(rom[offset:offset + 28]), ident + ' is already enabled'
    rom[offset:offset + 28] = row
    changes.append(dict(lesson=ident, action=action, donor=donor, offset=offset,
                        size=28, record=row.hex()))

# Byte11 is the native magical power coefficient, byte10 area radius.
# All ordinary native admission, defense, elemental, accuracy, payment,
# protection, theft ownership/depletion, law and reaction consumers remain.
install('VIK-A1', 26, {4: 6, 6: 4, 9: 1, 10: 0, 11: 24})
install('VIK-A2', 168, {})
install('VIK-A3', 147, {4: 6, 5: 1, 6: 1, 7: 2, 12: 117, 13: 63})
install('VIK-A4', 120, {4: 8, 5: 0, 6: 0, 7: 2, 8: 3, 9: 5, 10: 2, 12: 211})
install('VIK-A5', 26, {4: 12, 6: 4, 9: 1, 10: 0, 11: 28, 13: 104})
install('VIK-A6', 147, {4: 10, 5: 1, 6: 1, 7: 2, 12: 118, 13: 63})
install('VIK-A7', 28, {4: 20, 6: 3, 7: 2, 9: 5, 10: 2, 11: 40})
install('VIK-A8', 28, {2:4, 4:18, 6:4, 7:2, 9:5, 10:2, 11:36, 13:218})
install('VIK-A9', 120, {4: 6, 5: 0, 6: 3, 7: 2, 8: 1, 9: 1, 10: 1, 12: 212})

# Two named hidden self-reactions, outside every teaching/AI command list.
actions=bytearray(rom[table:table+432*28])+bytearray(6*28)
for action,lesson_id,donor,descriptor in [(436,'VIK-R1',251,221),(437,'VIK-R2',168,222)]:
    lesson=next(x for x in registry['lessons'] if x['id']==lesson_id)
    row=bytearray(clean[0x55187c+donor*28:0x55187c+(donor+1)*28])
    struct.pack_into('<H',row,0,lesson['nameId']);struct.pack_into('<H',row,22,0)
    row[2]=0;row[4]=0;row[5]=0;row[6]=0;row[7]=2;row[8]=3;row[9]=1;row[10]=0
    row[12:16]=bytes((descriptor,1,1,1))
    flags=struct.unpack_from('<I',row,16)[0]
    flags=(flags|(1<<(20-11)))&~((1<<(18-11))|(1<<(19-11))|(1<<(26-11)))
    struct.pack_into('<I',row,16,flags);actions[action*28:(action+1)*28]=row
users=[0x23320,0x236ac,0x25998,0x26c9c,0x26d3c,0x26e18,0x27048,0x27170,0x279a0,0x27a94,0xa784c,0xb5d18,0xc3080,0xc3474,0xccd84,0x133e70,0x13416c]
for pointer in users:
    assert struct.unpack_from('<I',rom,pointer)[0]==0x08000000+table
    struct.pack_into('<I',rom,pointer,0x09262000)
assert rom[0x1262000:0x1262000+len(actions)]==b'\xff'*len(actions)
rom[0x1262000:0x1262000+len(actions)]=actions
changes.append(dict(name='hidden reaction actions',offset=0x1262000,rows=438,users=users,owned=[436,437]))
(work/'help-input.gba').write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/jobs/viking/patch-help.mjs'),str(work/'help-input.gba'),str(work/'help-output.gba'),str(work/'help.json')],check=True)
rom=bytearray((work/'help-output.gba').read_bytes())
help_meta=json.loads((work/'help.json').read_text())

out = P / 'viking' / sha(rom)
out.mkdir(parents=True, exist_ok=True)
(out / 'viking.gba').write_bytes(rom)
(out / 'input.gba').write_bytes(base)
report = dict(
    status='PRIVATE IMPLEMENTATION IN PROGRESS: Stormcall and outgoing factors installed; nine actions installed; reactions installed; full Viking acceptance pending',
    baseSha1=sha(base), romSha1=sha(rom), path=str(out / 'viking.gba'),
    reservation=[0x1240000, 0x1280000], changes=changes, symbols={**parent['symbols'],**symbols}, help=help_meta,
    fixtureSha1=sha(rom), heapEnd=parent['heapEnd'], sharedSourceCommits=['77efe09','2eb9e52','eff9489','ce83f72'],
    enabledActions=[365, 366, 367, 368, 369, 370, 371, 372, 373], inheritedCombo=130,
    pending=['Tsunami full UI/law/elemental acceptance', 'copied lifecycle integration',
             'cross-class outgoing acceptance', 'reaction presentation and lifecycle acceptance',
             'native UI/help and complete integration acceptance'],
)
(out / 'manifest.json').write_text(json.dumps(report, indent=2))
(P / 'viking').mkdir(exist_ok=True)
(P / 'viking/current.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
