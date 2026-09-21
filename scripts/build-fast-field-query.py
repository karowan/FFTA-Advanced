"""Private current-query field optimization over the complete art candidate.

No saved/transient state is added. All noncanonical owners execute the original
query. The pinned gameplay implementation and unused integration tail are
authenticated; no installed or action-completion selector is changed.
"""
import argparse,datetime,hashlib,json,struct,subprocess
from pathlib import Path
from native_art import ROOT,sha

START,END,HOOK=0x11e7900,0x11e8000,0x11e4a4a
STAMP=lambda:datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')

def build(source,publish_current=True):
    source=Path(source);view=json.loads(source.read_bytes())
    parent_path=Path(view['connectedManifest']);parent_raw=parent_path.read_bytes();parent=json.loads(parent_raw)
    original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==view['romSha1']==parent['romSha1']
    assert parent['components'].get('actionCompletion') and not parent['components'].get('fieldQueryFast')
    upstream_path=ROOT/'build/expansion/probes/integrated-jobs/current.json';upstream_raw=upstream_path.read_bytes();upstream=json.loads(upstream_raw)
    baseline=Path(upstream['path']).read_bytes()
    assert hashlib.sha1(baseline).hexdigest()==upstream['romSha1']=='1b070824a8dad4995434eee3ab40fa08187a6120'
    # Authenticate the complete gameplay integration block, accessor bindings,
    # field body and all earlier engine exports used by those bindings.
    regions=[upstream['regions']['integration']]
    for lo,hi in regions:assert original[lo:hi]==baseline[lo:hi]
    assert upstream['regions']['integration'][1]<=START<END<=0x11e8000
    assert original[START:END]==b'\xff'*(END-START)
    assert original[HOOK:HOOK+12].hex()=='f0b5adb00290039104920593'
    # The bank accessor is provided by an authenticated earlier engine block.
    binding=upstream['symbols']['ffta_job_state']-0x08000000
    target=struct.unpack_from('<I',baseline,binding+12)[0]&~1
    assert 0x08000000<=target<0x0a000000
    assert target==upstream['priorSymbols']['ffta_job_state']==0x091d01f4
    # Authenticate ownership code and its actual format-validator dependency.
    # The broader prefix also contains intentionally replaced art/job tables.
    # The intervening save/clear routines include the existing art heap-end
    # clear hook at11D0714. Queries do not call it; keep it outside this proof.
    regions += [[0x11d0000,0x11d0350],[0x11d07dc,0x11e0000],[0x1100000,0x110003c]]
    assert upstream['priorSymbols']['ffta_job_footer_encode']==0x091d0350
    assert upstream['upstream']['imports']['ffta_storage_format']==0x09100000
    magic=struct.unpack_from('<I',baseline,0x1100034)[0]-0x08000000
    assert baseline[magic:magic+8]==b'FFTAEXP1'
    regions.append([magic,magic+8])
    for lo,hi in regions:assert original[lo:hi]==baseline[lo:hi]
    out=ROOT/'build/art/performance/field-query'/STAMP();out.mkdir(parents=True)
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
    source_file=ROOT/'src/engine/geomancer-field-fast.c'
    flags=['-mcpu=arm7tdmi','-mthumb','-O2','-std=c11','-ffreestanding','-fno-builtin','-fno-unwind-tables',
           '-fno-asynchronous-unwind-tables','-fstack-usage','-Wall','-Wextra','-Werror','-I',str(ROOT/'src/engine')]
    command=[prefix+'gcc.exe',*flags,'-c',str(source_file),'-o',str(out/'field.o')]
    subprocess.run(command,check=True,capture_output=True)
    assembly=f'''.syntax unified
.cpu arm7tdmi
.thumb
.section .hook,"ax"
.global field_hook
.thumb_func
field_hook:
 push {{r3}}
 /* Hook starts at2 mod4: at its LDR, aligned PC is the word below. */
 ldr r3,[pc,#0]
 bx r3
 .word ffta_geo_field_dispatch
 nop
.text
.align 2
.global ffta_geo_field_dispatch
.thumb_func
ffta_geo_field_dispatch:
 pop {{r3}}
 push {{r4-r7,lr}}
 sub sp,#4
 movs r4,r0
 movs r5,r1
 movs r6,r2
 movs r7,r3
 bl ffta_geo_field_canonical
 cmp r0,#0
 beq 1f
 movs r0,r4
 movs r1,r5
 movs r2,r6
 movs r3,r7
 bl ffta_geo_field_fast
 add sp,#4
 pop {{r4-r7}}
 pop {{r1}}
 bx r1
1:
 movs r0,r4
 movs r1,r5
 movs r2,r6
 movs r3,r7
 ldr r4,[sp,#20]
 mov lr,r4
 add sp,#4
 pop {{r4-r7}}
 add sp,#4
 b ffta_geo_field_original
.align 2
.global ffta_geo_field_original
.thumb_func
ffta_geo_field_original:
 push {{r4-r7,lr}}
 sub sp,#180
 str r0,[sp,#8]
 str r1,[sp,#12]
 str r2,[sp,#16]
 str r3,[sp,#20]
 ldr r3,={0x08000000+HOOK+12|1}
 bx r3
.ltorg
.align 2
.global ffta_job_state
.thumb_func
ffta_job_state:
 ldr r3,={upstream['symbols']['ffta_job_state']|1}
 bx r3
.ltorg
'''
    (out/'bridge.s').write_text(assembly)
    (out/'field.ld').write_text(f'SECTIONS {{ .hook {hex(HOOK+0x08000000)} : {{ *(.hook) }} .text {hex(START+0x08000000)} : {{ *(.text*) *(.rodata*) }} .unexpected : {{ *(.data*) *(.bss*) *(COMMON) }} /DISCARD/ : {{ *(.ARM.attributes) *(.comment) }} }}')
    subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-T,'+str(out/'field.ld'),
                    str(out/'field.o'),str(out/'bridge.s'),'-lgcc','-o',str(out/'field.elf')],check=True,capture_output=True)
    sections=subprocess.check_output([prefix+'objdump.exe','-h',str(out/'field.elf')],text=True)
    assert '.unexpected' not in sections,sections
    for section in ('hook','text'):
        subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.'+section,str(out/'field.elf'),str(out/(section+'.bin'))],check=True)
    raw=(out/'text.bin').read_bytes();hook=(out/'hook.bin').read_bytes()
    assert len(hook)==12 and START+len(raw)<=END
    symbols={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe','-g',str(out/'field.elf')],text=True).splitlines() if len(p:=line.split())==3}
    rom=bytearray(original);rom[HOOK:HOOK+12]=hook;rom[START:START+len(raw)]=raw
    assert rom[:HOOK]==original[:HOOK] and rom[HOOK+12:START]==original[HOOK+12:START] and rom[START+len(raw):]==original[START+len(raw):]
    digest=hashlib.sha1(rom).hexdigest();path=out/'FFTA_Field_Query.gba';path.write_bytes(rom)
    component=dict(path=str(path),romSha1=digest,baseRomSha1=parent['romSha1'],sourceManifest=str(parent_path),sourceManifestSha256=sha(parent_raw),
        upstreamManifest=str(upstream_path),upstreamManifestSha256=sha(upstream_raw),upstreamRomSha1=upstream['romSha1'],
        used=[START,START+len(raw)],reservation=[START,END],patch=dict(offset=HOOK,before=original[HOOK:HOOK+12].hex(),after=hook.hex()),
        symbols=symbols,sourceSha256=sha(source_file.read_bytes()),builderSha256=sha(Path(__file__).read_bytes()),
        command=command,compilerSha256=sha(Path(prefix+'gcc.exe').read_bytes()),compileDirectory=str(out),
        stackUsage=(out/'field.su').read_text(),dispatchFrameBytes=24,fallbackExtraStackBytes=0,
        authenticatedRegions=[dict(start=lo,end=hi,sha256=sha(original[lo:hi])) for lo,hi in regions],scope=__doc__)
    (out/'manifest.json').write_text(json.dumps(component,indent=2)+'\n')
    connected=dict(parent,path=str(path),romSha1=digest,romSha256=sha(rom),components=dict(parent['components'],fieldQueryFast=component),status='Private field-query engineering candidate; acceptance remains separate')
    folder=ROOT/'build/art/connected'/digest;folder.mkdir(parents=True,exist_ok=True)
    (folder/'manifest.json').write_text(json.dumps(connected,indent=2)+'\n')
    view.update(path=str(path),romSha1=digest,connectedManifest=str(folder/'manifest.json'),fieldQueryFast=str(out/'manifest.json'))
    (folder/'live-palette-view.json').write_text(json.dumps(view,indent=2)+'\n')
    if publish_current:(out.parent/'current.json').write_text(json.dumps(view,indent=2)+'\n')
    report=dict(status='passed',romSha1=digest,bytes=len(raw),manifest=str(out/'manifest.json'),view=str(folder/'live-palette-view.json'),scope='Authenticated scoped build only; no native execution.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return view

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=ROOT/'build/art/action-completion/current.json');args=parser.parse_args();build(args.source)
