"""Compile the bounded equipment-lesson row fix on the job-visibility release.

Native equipment help (C8D14) stores at most three rows. Expansion items that
teach two lessons to two racial jobs produced four rows and overwrote adjacent
UI state. Merge same-family racial entries into one cycling-badge row, cap the
builder at three rows, and make each AP lookup match the row's lesson as well
as its job. Mixed-type items show the first row's type icon, as the shop list
does.
"""
import datetime, hashlib, json, struct, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='267fd273bffe2c26a7ed3507d236af80a29b74a8'
OUT=ROOT/'build/expansion/teaching-rows'
START,END=0x1ff1000,0x1ff2000
SOURCES=['src/engine/teaching-rows.c','src/engine/teaching-rows.s']
# name, offset, native bytes replaced, trampoline scratch register
SITES=[('ffta_teaching_row_group',0xc8dc0,'3888013038805046',0),
       ('ffta_party_info_row_match',0x8c842,'007a0b7898425ed10978081c0122',3),
       ('ffta_shop_info_row_match',0x6fc8c,'007a0b7898422fd10978081c0122',3),
       ('ffta_shop_row_match',0x67236,'18780e78b0423ed10978081c0122',6),
       ('ffta_party_info_type',0x8c8a8,'b879fff747fe31e0',0),
       ('ffta_shop_info_type',0x6fd10,'0f9b987902281bd0',0)]
def sha(raw):return hashlib.sha256(raw).hexdigest()

def trampoline(offset,size,register,target):
    """Thumb ldr/bx to an aligned literal inside the replaced bytes."""
    literal=(offset+4)&~3
    if literal<offset+4:literal+=4
    code=bytearray(struct.pack('<H',0x46c0)*(size//2))
    struct.pack_into('<HH',code,0,0x4800|register<<8|(literal-((offset+4)&~3))//4,0x4700|register<<3)
    struct.pack_into('<I',code,literal-offset,target|1)
    assert literal-offset+4<=size
    return bytes(code)

def families():
    registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
    jobs=sorted(registry['jobs'],key=lambda j:j['id'])
    groups={}
    for job in jobs:groups.setdefault(job['group'],[]).append(job['id'])
    shared={g:i+1 for i,g in enumerate(sorted(g for g,ids in groups.items() if len(ids)>1))}
    new=[j for j in jobs if j['id']>=116]
    first=min(j['id'] for j in new);last=max(j['id'] for j in new)
    table=[0]*(last-first+1)
    for job in new:table[job['id']-first]=shared.get(job['group'],0)
    return first,table,{g:groups[g] for g in shared}

def main():
    parent=Path(json.loads((ROOT/'build/expansion/job-visibility/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==BASE==meta['romSha1']
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    assert original[START:END]==b'\xff'*(END-START),'Teaching-row reservation occupied'
    # Builder, jump table and consumer instructions remain native; literal
    # pools between them were already repointed by the expansion.
    for lo,hi in ((0xc8d14,0xc8d54),(0xc8d58,0xc8d88),(0xc8d8c,0xc8de4),(0xc8de8,0xc8ebc),(0x8c53c,0x8c56c),
                  (0x8c836,0x8c8b0),(0x8c908,0x8c914),(0x6fc80,0x6fcec),(0x6fcf4,0x6fd2c),
                  (0x6722c,0x67298),(0x672bc,0x672c6)):
        assert original[lo:hi]==clean[lo:hi],f'native teaching code changed at {lo:x}'
    for name,offset,before,_ in SITES:assert original[offset:offset+len(before)//2].hex()==before,name
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    first,table,groups=families()
    (out/'teaching-families.h').write_text('/* Generated from build/expansion/registry.json job groups. */\n'
        f'#define FFTA_TEACHING_FAMILY_FIRST {first}u\n'
        'static const unsigned char ffta_teaching_family[]={'+','.join(map(str,table))+'};\n')
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'teaching-rows.elf';binary=out/'teaching-rows.bin'
    command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib',
             '-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-Wl,--gc-sections',
             '-Wl,-Ttext='+hex(0x08000000+START),'-Wl,-e,ffta_teaching_row_group',
             *[f'-Wl,-u,{n}' for n,*_ in SITES[1:]],'-I'+str(out),*SOURCES,'-o',str(elf)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (out/'compile.log').write_text(result.stdout+result.stderr);result.check_returncode()
    subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.text','-j','.rodata',str(elf),str(binary)],check=True,capture_output=True)
    sections=subprocess.check_output([prefix+'objdump.exe','-h',str(elf)],text=True)
    (out/'sections.txt').write_text(sections)
    assert '.data' not in sections and '.bss' not in sections,'Unexpected RAM state'
    disassembly=subprocess.check_output([prefix+'objdump.exe','-d',str(elf)],text=True)
    (out/'disassembly.txt').write_text(disassembly)
    # ARM7TDMI interworking: no ARM-state linker veneers or pc loads.
    assert 'veneer' not in disassembly and 'ldr\tpc' not in disassembly,'Unsafe interworking veneer'
    built={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    code=binary.read_bytes();assert 0<len(code)<=END-START
    text=next(line.split() for line in sections.splitlines() if line.split()[1:2]==['.text'])
    assert int(text[3],16)==0x08000000+START,'Code does not start at reservation'
    assert all(0x08000000+START<=built[n]<0x08000000+START+len(code) for n,*_ in SITES)
    rom=bytearray(original);rom[START:START+len(code)]=code;patches=[]
    for name,offset,before,register in SITES:
        size=len(before)//2;new=trampoline(offset,size,register,built[name])
        rom[offset:offset+size]=new;patches.append(dict(name=name,offset=offset,before=before,after=new.hex()))
    allowed=set(range(START,START+len(code)))|{p['offset']+i for p in patches for i in range(len(p['before'])//2)}
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['teachingRows']=dict(parent=str(parent),baseSha1=BASE,reservation=[START,END],used=[START,START+len(code)],
        patches=patches,symbols=built,compileCommand=command,families=groups,familyFirst=first,familyTable=table,
        sourceSha256={s:sha((ROOT/s).read_bytes()) for s in SOURCES},
        registrySha256=sha((ROOT/'build/expansion/registry.json').read_bytes()))
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],codeBytes=len(code))))

if __name__=='__main__':main()
