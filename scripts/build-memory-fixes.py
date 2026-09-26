"""Fix the memory/table defects found by the September 25 RAM audit.

Bounded patch on the palette-removal candidate:
- Native reaction status masks: the integrated table relocation moved the
  reaction mask base (literal at 1339EC, 16-row table at 527D5C that starts
  at application row 92) into the new application-mask copy, so reactions
  1..15 read the added application masks (Petrify/Silence/etc. no longer
  blocked them). The literal points at the unchanged original table again.
- Old-layout inventory list builders 7A094/8D0C4 now call the expansion C
  builders instead of reading count bytes as 4-byte records (fake entries,
  and a stack list buffer that overflows past 270 matches).
- Executor stack: ffta_samurai_execute (native executor entry, every action)
  held an 820-byte action snapshot on the IWRAM stack under all nested
  result/reaction/Doublecast chains. It now borrows a root result-bank frame
  (src/engine/snapshot-lend.c, src/engine/samurai-execute.c) and keeps the
  stack frame only as a fallback, guarded by stack headroom.
- Result fallback: stack_result (no free bank frame) added an 880-byte stack
  snapshot below deep chains; it now keeps it only with measured headroom
  (src/engine/result-fallback.c), else resolves without one.
- Suspend marker: ffta_job_load clears the JST1 marker from loaded state so
  later normal saves never carry it (src/engine/job-save.c).
- Menu recolor bounds: native 0808B890 recolors two map rows at a caller's
  pointer. The unit menu un-highlights its 0xFF "no previous row" as row 512,
  which with the lower heap end overran the fixed state and wrapped past EWRAM
  into unit records. The replacement (src/engine/bg-recolor.c) writes only
  inside the layer's map buffers.
- Job wheel label: the wheel clears 11 glyph columns (CpuSet fill, 0x160
  halfwords at 0x0600B4E0) before drawing a job name; the 11-tile "Mystic
  Knight" draws a 12th column (VRAM 0x0600B7A0) that was never cleared, leaving
  a fragment after the next, shorter name. That column is blank in the original
  game; the fill now covers 12 columns.
- EXP for expansion jobs: native 0812E5B4 treats jobs above 82 as special
  units (EXP only for story characters behind flags, else 0), so every unit
  in jobs 116..125 earned no EXP from any action. Those jobs now take the
  ordinary path (src/engine/exp-job-gate.s).
- Chemist target shape: every Chemist recipe carried Healing Mist's cross
  area (shape 5, size 2), so single-ally recipes such as Potion or Phoenix
  Down also affected adjacent units. The nine single-target recipes now use
  the single-target shape (1, 0) of the other new single-target actions.
- Chemist softlock: a refused Chemist payment took the executor's "cannot pay"
  branch, which never ends the turn. Targeting accepts enemies and empty
  tiles for single-ally recipes (e.g. Potion on an adjacent enemy), so the
  battle stopped. The gate (src/engine/chemist-payment.c) now pays only for a
  party recipient and always continues; eligibility keeps others unaffected.
Compiled code goes to blank ROM 0x1FD0000..0x1FDFFFF; calls into installed
code use generated Thumb BX stubs authenticated against the integrated build.
"""
import datetime, hashlib, json, re, struct, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/memory-fixes'
START,END=0x1fd0000,0x1fe0000
SOURCES=['src/engine/samurai-execute.c','src/engine/snapshot-lend.c','src/engine/result-fallback.c','src/engine/job-save.c','src/engine/bg-recolor.c','src/engine/chemist-payment.c','src/engine/exp-job-gate.s']
# installed symbol -> compiled replacement
PATCHED={'ffta_samurai_execute':'ffta_samurai_execute','stack_result':'ffta_result_fallback','ffta_job_load':'ffta_job_load',
         'ffta_chemist_payment_gate':'ffta_chemist_payment_gate'}
REACTION_LITERAL,REACTION_TABLE=0x1339ec,0x08527d5c
WHEEL_CLEAR,WHEEL_FILL=0x857ec,(0x01000160,0x01000180)   # CpuSet fill, 16-bit halfword count
CHEMIST_SINGLE=(383,384,385,386,388,389,390,391,392)   # CHM-A1..A10 except Healing Mist (A5, 387)
# Native list builders still parsing the pre-expansion 4-byte inventory
# records at 02001940 (now one count byte per item): equip-tab rebuild 7A094
# (after every equip, 7AF22; sort path 7ACDC) and item-list variant 8D0C4
# (8E838). Their siblings 799C0/8CBDC already call the C builders; these
# entries now do too (same (tab, destination) signature and list layout).
# Native entries replaced by compiled code: (offset, original bytes, symbol).
NATIVE=((0x8b890,bytes.fromhex('f0b50c1c1204170c1b041d0c0f4a4c21'),'ffta_bg_recolor'),
        (0x12e5b4,bytes.fromhex('70b5061c0d1c042199f772fc522833d9'),'ffta_exp_job_gate'))
OLD_BUILDERS=((0x7a094,0x799c0,'ffta_equip_item_list'),(0x8d0c4,0x8cbdc,'ffta_party_item_list'))   # site, sibling hook
def sha(raw):return hashlib.sha256(raw).hexdigest()
def u32(b,p):return struct.unpack_from('<I',b,p)[0]

def trampoline(offset,target):
    """push{r3}; ldr r3,lit; mov ip,r3; pop{r3}; bx ip: all argument registers survive."""
    code=bytearray(struct.pack('<5H',0xb408,0x4b00,0x469c,0xbc08,0x4760))
    if (offset+len(code))%4:code+=struct.pack('<H',0x46c0)
    literal=offset+len(code);code+=struct.pack('<I',target|1)
    base=(offset+2+4)&~3;assert (literal-base)%4==0 and 0<=literal-base<1024
    struct.pack_into('<H',code,2,0x4b00|(literal-base)//4)
    return bytes(code)

def main():
    parent=Path(json.loads((ROOT/'build/expansion/palette-removal/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']
    assert original[START:END]==b'\xff'*(END-START),'Memory-fix reservation occupied'
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    integrated=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
    image=Path(integrated['path']).read_bytes();assert hashlib.sha1(image).hexdigest()==integrated['romSha1']
    symbols=integrated['symbols'];addresses=sorted(set(v for v in symbols.values() if 0x08000000<=v<0x0a000000))
    # Offsets earlier bounded stages declared as patched (e.g. the art stage's
    # low-address workspace literal 13078C4) may differ from the integrated
    # image; every other installed byte must match it exactly.
    declared=set()
    comp=meta['components']
    for ch in comp['livePalette']['changes']:
        n=ch.get('bytes',4);declared.update(range(ch['offset'],ch['offset']+(n if isinstance(n,int) else 4)))
    for stage in ('paletteRemoval','enchantWeapons','jobVisibility','teachingRows','equipmentRevision'):
        for ch in meta.get(stage,{}).get('patches',[]):
            n=len(bytes.fromhex(ch['after'])) if 'after' in ch else 4
            declared.update(range(ch['offset'],ch['offset']+n))
    def body(name,rom,mask=False):
        at=symbols[name]&~1;end=next(x for x in addresses if x>at)
        raw=bytearray(rom[at-0x08000000:end-0x08000000])
        if mask:
            for i in range(len(raw)):
                if at-0x08000000+i in declared:raw[i]=0
        return bytes(raw)
    proofs={}
    for name in PATCHED:
        installed=body(name,original);assert installed==body(name,image),'Installed code differs from integrated build: '+name
        proofs[name]=dict(address=symbols[name]&~1,bytes=len(installed),sha256=sha(installed))
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'fixes.elf';binary=out/'fixes.bin'
    include=Path(integrated['path']).parents[1];helpers=out/'helpers.s';needed=[]
    flags=['-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror',
           '-fstack-usage','-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion'),'-I',str(include)]
    for attempt in range(6):
        helpers.write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'+''.join(
            f'.align 2\n.global {n}\n.thumb_func\n{n}:\n push {{r3}}\n ldr r3,={hex(symbols[n]|1)}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n' for n in needed))
        command=[prefix+'gcc.exe',*flags,'-nostdlib','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',
                 '-Wl,-Ttext='+hex(0x08000000+START),'-Wl,-e,ffta_samurai_execute',*[f'-Wl,-u,{n}' for n in PATCHED.values()],*[f'-Wl,-u,{n}' for _,_,n in NATIVE],
                 *SOURCES,str(helpers),'-o',str(elf)]
        result=subprocess.run(command,cwd=out,capture_output=True,text=True) if False else subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        (out/'compile.log').write_text(result.stdout+result.stderr)
        missing=sorted(set(re.findall(r"undefined reference to `([A-Za-z0-9_]+)'",result.stderr))-set(needed))
        if result.returncode==0:break
        assert missing and all(m in symbols for m in missing),result.stderr[-2000:]
        needed+=missing
    result.check_returncode()
    for name in needed:
        installed=body(name,original);assert body(name,original,True)==body(name,image,True),'Installed helper differs from integrated build: '+name
        proofs[name]=dict(address=symbols[name]&~1,bytes=len(installed),sha256=sha(installed))
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
    assert int(text[3],16)==0x08000000+START and all(0x08000000+START<=built[n]<0x08000000+START+len(code) for n in PATCHED.values())
    frames={}
    for su in [*ROOT.glob('*.su'),*out.glob('*.su')]:
        for line in su.read_text().splitlines():
            fn,size,kind=line.rsplit('\t',2);frames[Path(fn.split(':')[0]).stem+':'+fn.split(':')[-1]]=int(size)
        su.unlink()
    rom=bytearray(original);rom[START:START+len(code)]=code;allowed=set(range(START,START+len(code)));patches=[]
    def put(at,old,new,label):
        assert rom[at:at+len(old)]==old,(label,hex(at),rom[at:at+len(old)].hex())
        rom[at:at+len(new)]=new;allowed.update(range(at,at+len(new)))
        patches.append(dict(offset=at,before=old.hex(),after=new.hex(),label=label))
    for name,replacement in PATCHED.items():
        at=(symbols[name]&~1)-0x08000000;new=trampoline(at,built[replacement])
        assert len(new)<=proofs[name]['bytes'],name
        put(at,original[at:at+len(new)],new,name+' -> compiled replacement '+replacement)
    for at,expected,name in NATIVE:
        assert original[at:at+len(expected)]==expected==clean[at:at+len(expected)],hex(at)
        new=trampoline(at,built[name]);assert len(new)<=len(expected)
        put(at,original[at:at+len(new)],new,'native %X -> %s'%(at,name))
    for at,sibling,name in OLD_BUILDERS:
        assert original[at:at+16]==clean[at:at+16],hex(at)
        assert original[sibling:sibling+4]==bytes.fromhex('004b1847'),'sibling hook form '+hex(sibling)
        target=u32(original,sibling+4);assert 0x09100000<=target<0x09200000 and target&1
        new=trampoline(at,target&~1);assert len(new)<=16
        proofs[name]=dict(address=target&~1,via=sibling)
        put(at,original[at:at+len(new)],new,'old-layout list builder -> '+name)
    # Reaction masks: back to the original, unchanged 16-row table.
    assert u32(clean,REACTION_LITERAL)==REACTION_TABLE and original[0x527d5c:0x527d5c+16*12]==clean[0x527d5c:0x527d5c+16*12]
    put(REACTION_LITERAL,original[REACTION_LITERAL:REACTION_LITERAL+4],struct.pack('<I',REACTION_TABLE),'native reaction mask table restored')
    assert u32(original,WHEEL_CLEAR)==u32(clean,WHEEL_CLEAR)==WHEEL_FILL[0]
    put(WHEEL_CLEAR,struct.pack('<I',WHEEL_FILL[0]),struct.pack('<I',WHEEL_FILL[1]),'job wheel label clears 12 glyph columns')
    actions=u32(original,0xccd84)-0x08000000   # relocated action records, 28 bytes each; +9 shape, +10 size
    for action in CHEMIST_SINGLE:
        put(actions+28*action+9,bytes((5,2)),bytes((1,0)),f'Chemist action {action} single-target shape')
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['memoryFixes']=dict(parent=str(parent),baseSha1=hashlib.sha1(original).hexdigest(),reservation=[START,END],
        used=[START,START+len(code)],patches=patches,installed=proofs,symbols=built,frames=frames,compileCommand=command,
        integratedSha1=integrated['romSha1'],sourceSha256={s:sha((ROOT/s).read_bytes()) for s in SOURCES})
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],codeBytes=len(code),
        patches=len(patches),frames=frames)))

if __name__=='__main__':main()
