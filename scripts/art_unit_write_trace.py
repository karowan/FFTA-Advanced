"""Private copy/clear/null-free ring; preserves selected ROM asset addresses."""
import hashlib,json,struct,subprocess
from pathlib import Path
from native_art import ROOT,sha

def build(meta,out,stop_workspace=False):
    rom=bytearray(Path(meta['path']).read_bytes())
    assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
    base,limit=meta['ramReservation'];log=(base+meta['transientStateBytes']+3)&~3
    assert limit-log>=976
    start=0x1fd0000
    assert rom[start:start+0x1000]==b'\xff'*0x1000
    clear,copy=struct.unpack_from('<2I',rom,0x36d4b8)
    assert rom[0x7170:0x7174].hex()=='004b1847'
    free=struct.unpack_from('<I',rom,0x7174)[0]
    assert rom[0x7138:0x713c].hex()=='004b1847'
    allocate=struct.unpack_from('<I',rom,0x713c)[0]
    assert clear&1 and copy&1
    source=f'''.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro observer name,kind,count,original
.align 2
.global \\name
.thumb_func
\\name:
 push {{r0-r7,lr}}
.if \\kind == 3
 ldr r4,={log+592}
 movs r5,#16
3:
 ldr r6,[r4]
 cmp r6,r1
 bne 4f
 movs r6,#0
 str r6,[r4]
4:
 adds r4,#24
 subs r5,#1
 bne 3b
 cmp r1,#0
 bne 2f
.else
 ldr r4,=0x02004000
 cmp r0,r4
 bhs 2f
 ldr r4,=0x02000000
 adds r5,r0,\\count
 cmp r5,r4
 bls 2f
.endif
 ldr r4,={log}
 ldr r5,[r4]
 movs r6,#15
 ands r6,r5
 movs r7,#36
 muls r6,r7
 adds r6,#16
 adds r6,r4,r6
 str r5,[r6]
 adds r5,#1
 str r5,[r4]
 movs r5,#\\kind
 str r5,[r6,#4]
 str r0,[r6,#8]
 str r1,[r6,#12]
 str r2,[r6,#16]
 str r3,[r6,#20]
 mov r5,lr
 str r5,[r6,#24]
.if \\kind == 3
 str r5,[r4,#8]
 @ Native public-free wrapper saved its own caller immediately above our frame.
 ldr r5,[sp,#36]
 str r5,[r4,#12]
 movs r5,#1
 str r5,[r4,#4]
.endif
 ldr r5,[r0]
 str r5,[r6,#28]
.if \\kind == 2
 ldr r5,[r1]
 str r5,[r6,#32]
.else
 movs r5,#0
 str r5,[r6,#32]
.endif
2:
 pop {{r0-r7}}
 pop {{r3}}
 mov lr,r3
 @ The native callback contract uses at most r0-r2. Preserve incoming r3 too.
 push {{r0,r1}}
 ldr r0,=\\original
 str r0,[sp,#4]
 pop {{r0,pc}}
.ltorg
.endm
observer clear_entry,1,r1,{clear}
observer copy_entry,2,r2,{copy}
observer free_entry,3,r1,{free}
.align 2
.global allocate_entry
.thumb_func
allocate_entry:
 push {{r0-r7,lr}}
 {('ldr r3,=0x2660' + chr(10) + ' cmp r1,r3' + chr(10) + ' beq workspace_stop') if stop_workspace else ''}
 ldr r3,={allocate}
 bl allocate_call
 cmp r0,#0
 bne allocate_return
 ldr r4,={log}
 movs r5,#2
 str r5,[r4,#4]
 ldr r5,[sp,#32]
 str r5,[r4,#8]
 ldr r5,[sp,#36]
 str r5,[r4,#12]
 @ Halt at the first failed allocation, before any native consumer can use NULL.
allocate_stop:
 b allocate_stop
allocate_return:
 ldr r1,[sp,#4]
 movs r2,#1
 lsls r2,#11
 cmp r1,r2
 blo allocate_restore
 ldr r4,={log+592}
 movs r5,#16
allocate_find:
 ldr r6,[r4]
 cmp r6,#0
 beq allocate_record
 adds r4,#24
 subs r5,#1
 bne allocate_find
 b allocate_restore
allocate_record:
 str r0,[r4]
 str r1,[r4,#4]
 ldr r5,[sp,#32]
 str r5,[r4,#8]
 ldr r5,[sp,#36]
 str r5,[r4,#12]
 ldr r5,[sp,#40]
 str r5,[r4,#16]
 ldr r5,[sp,#44]
 str r5,[r4,#20]
allocate_restore:
 str r0,[sp]
 ldr r3,[sp,#32]
 mov lr,r3
 pop {{r0-r7}}
 add sp,#4
 bx lr
allocate_call:
 bx r3
workspace_stop:
 ldr r4,={log}
 movs r5,#3
 str r5,[r4,#4]
 b allocate_stop
.ltorg
'''
    # Restore the original r3 after recovering LR, without disturbing caller SP.
    source=source.replace('pop {r0-r7}\n pop {r3}\n mov lr,r3',
        'ldr r3,[sp,#32]\n mov lr,r3\n pop {r0-r7}\n add sp,#4')
    asm=out/'unit-write-trace.s';asm.write_text(source)
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'unit-write-trace.elf';binary=out/'unit-write-trace.bin'
    cmd=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-Ttext='+hex(start+0x08000000),'-Wl,-e,clear_entry',str(asm),'-o',str(elf)]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(out/'trace-compile.log').write_text(p.stdout+p.stderr);p.check_returncode()
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
    symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    code=binary.read_bytes();assert len(code)<0x1000
    rom[start:start+len(code)]=code
    struct.pack_into('<2I',rom,0x36d4b8,symbols['clear_entry']|1,symbols['copy_entry']|1)
    struct.pack_into('<I',rom,0x7174,symbols['free_entry']|1)
    struct.pack_into('<I',rom,0x713c,symbols['allocate_entry']|1)
    path=out/'unit-write-trace.gba';path.write_bytes(rom)
    trace=dict(sourceRomSha1=meta['romSha1'],source=str(meta['path']),romSha1=hashlib.sha1(rom).hexdigest(),path=str(path),
        log=log,logBytes=976,slots=16,stride=36,stopWorkspace=stop_workspace,allocationRecords=dict(offset=592,count=16,stride=24),callbacks=[clear,copy,free,allocate],symbols=symbols,codeSha256=sha(code),sourceSha256=sha(asm.read_bytes()),
        scope='Diagnostic callbacks only; code in authenticated blank ROM, ring in unused owned reservation tail. Existing assets unchanged. No production acceptance.')
    (out/'unit-write-trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    return dict(meta,path=str(path),romSha1=trace['romSha1']),trace
