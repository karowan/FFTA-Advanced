"""Build relocation-free ARM leaves and bounded temporary-IWRAM wrappers.

Only local function sections are copied. No external address/call relocation is
allowed. Compiler stack-usage output supplies the exact leaf stack reservation;
512 bytes remain below it for interrupts, above resident native code03006D68.
"""
import json,re,struct,subprocess
from native_art import ROOT,sha

SOURCES=['src/engine/art-frame-fast.c','src/engine/art-frame-fast.h',
         'scripts/art_scoped_build.py']

def build_scoped(work,history_slots,native_owners=False,fused_compose=False,word_reads=False,compact_leaves=False,unrolled_copy=False):
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
    obj=work/'frame-fast.o';assembly=work/'frame-fast.s'
    command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb' if compact_leaves else '-marm','-Os' if compact_leaves else '-O2','-ffreestanding',
        '-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables',
        '-ffunction-sections','-fstack-usage','-Wall','-Wextra','-Werror',
        '-DFFTA_ART_HISTORY_SLOTS='+str(history_slots),'-c',SOURCES[0],'-o',str(obj)]
    assert not word_reads or fused_compose
    assert not unrolled_copy or (fused_compose and not compact_leaves)
    if word_reads:command.insert(1,'-DFFTA_ART_FUSED_WORD_READS=1')
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (work/'frame-fast-compile.log').write_text(result.stdout+result.stderr)
    result.check_returncode()
    usage={}
    for line in obj.with_suffix('.su').read_text().splitlines():
        name,size,kind=line.split('\t');assert kind=='static',line
        usage[name.rsplit(':',1)[-1]]=int(size)
    text=['.syntax unified','.cpu arm7tdmi','.arm','.text'];leaves=[]
    for stem in ('owners','publish')+(('native_owners',) if native_owners else ())+(('fused_owners',) if fused_compose else ()):
        name='ffta_art_frame_'+stem;leaf=name+'_leaf';section='.text.'+leaf
        reloc=subprocess.check_output([prefix+'objdump.exe','-r','-j',section,str(obj)],text=True)
        rawpath=work/(stem+'.bin')
        subprocess.run([prefix+'objcopy.exe','-O','binary','-j',section,str(obj),str(rawpath)],check=True,capture_output=True)
        raw=rawpath.read_bytes();size=(len(raw)+15)&~15;stack=usage[leaf]
        for offset,kind in re.findall(r'^([0-9a-f]+)\s+(R_ARM_\w+)',reloc,re.M):
            # GNU emits a V4BX compatibility annotation even for ARM7TDMI.
            # This actual BX-register instruction is position independent;
            # no symbol/address relocation may survive extraction.
            assert not compact_leaves and kind=='R_ARM_V4BX' and (struct.unpack_from('<I',raw,int(offset,16))[0]&0x0ffffff0)==0x012fff10,reloc
        assert 0<len(raw)<=1024 and stack<=256,(leaf,len(raw),stack)
        raw+=bytes(size-len(raw));rawpath.write_bytes(raw)
        minimum=0x03006d68+512+stack+size
        leaves.append(dict(name=leaf,bytes=size,stackBytes=stack,minimumWrapperSP=minimum,sha256=sha(raw)))
        if compact_leaves:leaves[-1]['instructionSet']='thumb'
        # These instructions remain in ROM, not in the copied leaf. Eliminate
        # per-16-byte branch/refill overhead without extra scratch registers,
        # stack, overreading the source or retaining code across invocations.
        copy_code=(' ldmia r1!,{r3,r8,ip,lr}\n stmia r0!,{r3,r8,ip,lr}\n')*(size//16) if unrolled_copy else f''' mov r2,#{size//16}
1:
 ldmia r1!,{{r3,r8,ip,lr}}
 stmia r0!,{{r3,r8,ip,lr}}
 subs r2,r2,#1
 bne 1b
'''
        # ARM code may enter with either 4- or 8-byte alignment. BX preserves
        # interworking; r4-r8 and the incoming return address survive the copy.
        text.extend(f'''
.align 2
.arm
.global {name}
.type {name},%function
{name}:
 stmdb sp!,{{r4-r8,lr}}
 mov r4,r0
 mov r5,r1
 mov r6,r2
 ldr r8,={minimum:#x}
 cmp sp,r8
 blo 3f
 ldr r8,=0x03008000
 cmp sp,r8
 bhi 3f
 ldr r7,={size}
 sub sp,sp,r7
 mov r0,sp
 ldr r1,={leaf}
{ ' bic r1,r1,#1' if compact_leaves else '' }
{copy_code}
 mov r8,sp
{ ' orr r8,r8,#1' if compact_leaves else '' }
 mov r0,r4
 mov r1,r5
 mov r2,r6
 adr lr,2f
 bx r8
2:
 add sp,sp,r7
 b 4f
3:
 mov r0,r4
 mov r1,r5
 mov r2,r6
 bl {leaf}
4:
 ldmia sp!,{{r4-r8,lr}}
 bx lr
.size {name},.-{name}
.ltorg
.align 2
{ '.thumb' if compact_leaves else '.arm' }
.global {leaf}
.type {leaf},%function
{ '.thumb_func' if compact_leaves else '' }
{leaf}:
 .incbin "{rawpath.as_posix()}"
.size {leaf},.-{leaf}
'''.splitlines())
    assembly.write_text('\n'.join(text)+'\n',encoding='utf-8',newline='\n')
    proof=dict(historySlots=history_slots,leaves=leaves,command=command,
        compilerSha256=sha((ROOT/'tools/arm-gnu/bin/arm-none-eabi-gcc.exe').read_bytes()),
        sources={p:sha((ROOT/p).read_bytes()) for p in SOURCES})
    if compact_leaves:proof['compactLeaves']=True
    if unrolled_copy:proof['unrolledCopy']=True
    (work/'frame-fast.json').write_text(json.dumps(proof,indent=2)+'\n')
    return assembly,proof
