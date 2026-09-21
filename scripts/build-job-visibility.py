"""Compile a bounded menu hotfix on the authenticated approved-art release."""
import datetime, hashlib, json, struct, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='f53fedb8421f48fd10faabf60700a5d7ed60ddf8'
OUT=ROOT/'build/expansion/job-visibility'
START,END=0x1ff0000,0x1ff1000
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    parent=ROOT/'build/art/approved-first-pass-2026-09-20/candidate.json'
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==BASE==meta['romSha1']
    assert original[START:END]==b'\xff'*(END-START)
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
    # These stable helper bodies must match the engine whose symbol map we use.
    lines=[s.split() for s in (ROOT/'build/expansion/engine.symbols').read_text().splitlines()]
    symbols={s[2]:int(s[0],16) for s in lines if len(s)==3}
    addresses=sorted(set(symbols.values()))
    engine=(ROOT/'build/expansion/engine.bin').read_bytes()
    required=['ffta_storage_format','ffta_new_job_eligible','ffta_ap_value','ffta_job_lesson_count','ffta_job_lesson_at','memset']
    proofs={}
    for name in required:
        at=symbols[name];end=next(x for x in addresses if x>at)
        raw=original[at-0x08000000:end-0x08000000]
        assert raw==engine[at-0x09100000:end-0x09100000],name
        proofs[name]=dict(address=at,bytes=len(raw),sha256=sha(raw))
    elf=out/'wheel.elf';binary=out/'wheel.bin'
    # Explicit Thumb interworking stubs: ARM7TDMI does not switch instruction
    # sets on ARM LDR pc. Untyped distant linker symbols produce unsafe veneers
    # which a newer-CPU ARM simulator can erroneously accept.
    wrappers=out/'helpers.s'
    wrappers.write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'+''.join(
        '.align 2\n.global '+n+'\n.thumb_func\n'+n+':\n ldr r3,='+hex(symbols[n]|1)+'\n bx r3\n.ltorg\n' for n in required))
    command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib',
             '-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-Wl,--gc-sections',
             '-Wl,-Ttext='+hex(0x08000000+START),'-Wl,-e,ffta_wheel_initial','-Wl,-u,ffta_wheel_turn',
             'src/engine/job-wheel.c',str(wrappers),'-o',str(elf)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (out/'compile.log').write_text(result.stdout+result.stderr);result.check_returncode()
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
    built={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    code=binary.read_bytes();assert len(code)<=END-START
    rom=bytearray(original);rom[START:START+len(code)]=code;patches=[]
    for name in ('ffta_wheel_initial','ffta_wheel_turn'):
        at=symbols[name]-0x08000000;assert at%4==0
        old=original[at:at+8];assert old==engine[at-0x1100000:at-0x1100000+8]
        new=struct.pack('<HHI',0x4b00,0x4718,built[name]|1)
        rom[at:at+8]=new;patches.append(dict(name=name,offset=at,before=old.hex(),after=new.hex()))
    allowed=set(range(START,START+len(code)))|{p['offset']+i for p in patches for i in range(8)}
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['jobVisibility']=dict(parent=str(parent),baseSha1=BASE,reservation=[START,END],used=[START,START+len(code)],
        patches=patches,helpers=proofs,symbols=built,compileCommand=command,
        sourceSha256=sha((ROOT/'src/engine/job-wheel.c').read_bytes()),savedDiscoveryBytes=[0x1e7a,0x1e7b])
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],codeBytes=len(code))))

if __name__=='__main__':main()
