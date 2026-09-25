"""Open Mystic Knight enchantments to every primary weapon.

Bounded patch on the equipment-revision build. Compiles the current
ffta_myk_weapon/ffta_myk_blade (mystic-knight-state.c), ffta_myk_geometry
(mystic-knight-actions.c) and ffta_myk_parry_factor (mystic-knight-reactions.c)
into blank ROM and redirects the three installed entries plus the native
targeting range mode B42E4 (self tile for enchantments). Strike actions A1-A12
take native weapon-relative range/height (80/80); enchantments keep their self
target. Break and Spell Parry help text follow the new weapon rules.
"""
import datetime, hashlib, json, re, struct, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/enchant-weapons'
START,END=0x1ff2000,0x1ff4000
SOURCES=['src/engine/mystic-knight-state.c','src/engine/mystic-knight-actions.c','src/engine/mystic-knight-reactions.c',
         'src/engine/mystic-knight-dispel.c','src/engine/dancer-choice.c','src/engine/mystic-knight-targeting.s']
# Native targeting range mode word B42E4: whole-entry hook, 12 bytes.
TARGETING=(0xb42e4,'f0b50004050c2f1c0904080c')
# Weapon gate, geometry and Spell Parry; Spellbreak's random buff (single menu
# row, weapon operand, no pre-selected status) replaces its 21 choice rows.
PATCHED=('ffta_myk_weapon','ffta_myk_geometry','ffta_myk_parry_factor','ffta_myk_payment_gate','ffta_myk_usable',
         'ffta_myk_eligibility','ffta_myk_magnitude','ffta_myk_success','ffta_myk_law_hit','ffta_dancer_preview_choice',
         'ffta_dancer_menu','ffta_dancer_restricted_menu','ffta_dancer_menu_name','ffta_dancer_menu_selected')
STRIKES=range(410,422)          # MYK-A1..A12; A13 Release and A14 Break keep their ranges
HELP_POINTER=0x36d6c4
HELP={'MYK-A14':('Attempt Petrify. No HP damage or enchantment change. Rapier or saber.',
                 'Attempt Petrify. No HP damage or enchantment change.'),
      'MYK-A12':('Choose one buff to remove on a hit, then strike. Keeps your enchantment.',
                 'On a hit, remove one random buff from the target. Keeps enchantment.'),
      'MYK-R2':('An enemy physical hit spends your enchantment to halve that action.',
                'Rapier or saber: an enemy physical hit spends your enchantment to halve it.')}
def sha(raw):return hashlib.sha256(raw).hexdigest()

def encode_help(text):
    script="import('./src/rom-builder.mjs').then(m=>process.stdout.write(m.encodeHelp(process.argv[1]).toString('hex')))"
    return bytes.fromhex(subprocess.check_output(['node','-e',script,text],cwd=ROOT,text=True))

def trampoline(offset,target):
    """push{r3}; ldr r3,lit; mov ip,r3; pop{r3}; bx ip: all argument registers survive."""
    code=bytearray(struct.pack('<5H',0xb408,0x4b00,0x469c,0xbc08,0x4760))
    if (offset+len(code))%4:code+=struct.pack('<H',0x46c0)
    literal=offset+len(code);code+=struct.pack('<I',target|1)
    base=(offset+2+4)&~3;assert (literal-base)%4==0 and 0<=literal-base<1024
    struct.pack_into('<H',code,2,0x4b00|(literal-base)//4)
    return bytes(code)

def main():
    parent=Path(json.loads((ROOT/'build/expansion/equipment-revision/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']
    assert original[START:END]==b'\xff'*(END-START),'Enchant-weapon reservation occupied'
    integrated=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
    image=Path(integrated['path']).read_bytes();assert hashlib.sha1(image).hexdigest()==integrated['romSha1']
    symbols=integrated['symbols'];addresses=sorted(set(v for v in symbols.values() if 0x08000000<=v<0x0a000000))
    proofs={}
    for name in PATCHED:
        at=symbols[name]&~1;end=next(x for x in addresses if x>at)
        body=original[at-0x08000000:end-0x08000000]
        assert body==image[at-0x08000000:end-0x08000000],'Installed code differs from integrated build: '+name
        proofs[name]=dict(address=at,bytes=len(body),sha256=sha(body))
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    # Explicit Thumb BX stubs (ARM7TDMI cannot interwork through linker
    # veneers) for every installed function the compiled code calls.
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'enchant.elf';binary=out/'enchant.bin'
    include=Path(integrated['path']).parents[1];helpers=out/'helpers.s';needed=[]
    flags=['-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror',
           '-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion'),'-I',str(include)]
    for attempt in range(4):
        helpers.write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'+''.join(
            f'.align 2\n.global {n}\n.thumb_func\n{n}:\n push {{r3}}\n ldr r3,={hex(symbols[n]|1)}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n' for n in needed))
        command=[prefix+'gcc.exe',*flags,'-nostdlib','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',
                 '-Wl,-Ttext='+hex(0x08000000+START),'-Wl,-e,ffta_myk_weapon',*[f'-Wl,-u,{n}' for n in PATCHED[1:]],
                 '-Wl,-u,ffta_myk_target_mode_entry',*SOURCES,str(helpers),'-o',str(elf)]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        (out/'compile.log').write_text(result.stdout+result.stderr)
        missing=sorted(set(re.findall(r"undefined reference to `([A-Za-z0-9_]+)'",result.stderr))-set(needed))
        if result.returncode==0:break
        assert missing and all(m in symbols for m in missing),result.stderr[-2000:]
        needed+=missing
    result.check_returncode()
    for name in needed:
        at=symbols[name]&~1;end=next(x for x in addresses if x>at)
        body=original[at-0x08000000:end-0x08000000]
        assert body==image[at-0x08000000:end-0x08000000],'Installed helper differs from integrated build: '+name
        proofs[name]=dict(address=at,bytes=len(body),sha256=sha(body))
    subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.text','-j','.rodata',str(elf),str(binary)],check=True,capture_output=True)
    sections=subprocess.check_output([prefix+'objdump.exe','-h',str(elf)],text=True);(out/'sections.txt').write_text(sections)
    for line in sections.splitlines():
        cells=line.split()
        if len(cells)>2 and cells[1] in ('.data','.bss') and int(cells[2],16):raise AssertionError('Unexpected RAM state')
    disassembly=subprocess.check_output([prefix+'objdump.exe','-d',str(elf)],text=True);(out/'disassembly.txt').write_text(disassembly)
    assert 'veneer' not in disassembly and 'ldr\tpc' not in disassembly,'Unsafe interworking veneer'
    built={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    code=binary.read_bytes()
    text=next(line.split() for line in sections.splitlines() if line.split()[1:2]==['.text'])
    assert int(text[3],16)==0x08000000+START and all(0x08000000+START<=built[n]<0x08000000+START+len(code) for n in PATCHED)
    rom=bytearray(original);rom[START:START+len(code)]=code;allowed=set(range(START,START+len(code)));patches=[]
    for name in PATCHED:
        at=(symbols[name]&~1)-0x08000000;new=trampoline(at,built[name])
        assert len(new)<=proofs[name]['bytes'],name
        patches.append(dict(name=name,offset=at,before=original[at:at+len(new)].hex(),after=new.hex()))
        rom[at:at+len(new)]=new;allowed|=set(range(at,at+len(new)))
    at,before=TARGETING;assert original[at:at+12].hex()==before,'Target mode entry changed'
    new=struct.pack('<4HI',0xb408,0x46c0,0x4b00,0x4718,built['ffta_myk_target_mode_entry']|1)
    patches.append(dict(name='ffta_myk_target_mode_entry',offset=at,before=before,after=new.hex()))
    rom[at:at+12]=new;allowed|=set(range(at,at+12))
    actions=struct.unpack_from('<I',original,0xccd84)[0]-0x08000000;ranges=[]
    for action in STRIKES:
        at=actions+action*28+6;assert original[at:at+2]==b'\x01\x02',action
        rom[at:at+2]=b'\x80\x80';allowed|={at,at+1};ranges.append(dict(action=action,offset=at))
    registry=json.loads((ROOT/'build/expansion/registry.json').read_text());lessons={l['id']:l for l in registry['lessons']}
    table=struct.unpack_from('<I',original,HELP_POINTER)[0]-0x08000000;cursor=(START+len(code)+3)&~3;help=[]
    for lesson_id,(before,after) in HELP.items():
        old=encode_help(before);new=encode_help(after)
        entries=[i for i in range(0x1de,0x800) if (p:=struct.unpack_from('<I',original,table+(i-0x1de)*4)[0])>>25==4
                 and original[(p&0x1ffffff):(p&0x1ffffff)+len(old)]==old]
        assert len(entries)==1,(lesson_id,entries)
        help_id=entries[0]
        # The lesson rows must already point at this help entry.
        races=struct.unpack_from("<I",original,0x257e8)[0]-0x08000000
        for owner in lessons[lesson_id]['owners']:
            bank=struct.unpack_from('<I',original,races+owner['race']*4)[0]-0x08000000
            assert struct.unpack_from('<H',original,bank+owner['abilityIndex']*8+2)[0]==help_id,(lesson_id,owner)
        cursor=(cursor+3)&~3;assert cursor+len(new)<=END
        rom[cursor:cursor+len(new)]=new;allowed|=set(range(cursor,cursor+len(new)))
        struct.pack_into('<I',rom,table+(help_id-0x1de)*4,cursor+0x08000000);allowed|=set(range(table+(help_id-0x1de)*4,table+(help_id-0x1de)*4+4))
        help.append(dict(lesson=lesson_id,helpId=help_id,address=cursor+0x08000000,text=after,previous=before));cursor+=len(new)
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['enchantWeapons']=dict(parent=str(parent),baseSha1=hashlib.sha1(original).hexdigest(),reservation=[START,END],used=[START,cursor],
        patches=patches,installed=proofs,symbols=built,ranges=ranges,help=help,compileCommand=command,
        integratedSha1=integrated['romSha1'],sourceSha256={s:sha((ROOT/s).read_bytes()) for s in SOURCES})
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],codeBytes=len(code),help=len(help))))

if __name__=='__main__':main()
