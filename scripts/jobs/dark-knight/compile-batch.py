"""Compile batch translation units without pretending pending queue linking passed."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'build/expansion/probes'
builder=ROOT/'scripts/jobs/dark-knight/build.py'
# Use the same verified-base import generation as the actual linker build.
# Stop before native source generation/linking, which requires the queue release.
prefix=builder.read_text().split('\ndef once(',1)[0]
exec(compile(prefix,str(builder),'exec'),{'__file__':str(builder)})
prior=json.loads((P/'job-state/current.json').read_text())
out=P/'dark-knight'/prior['romSha1'];out.mkdir(parents=True,exist_ok=True)
imports=out/'dark-knight-imports.h'
assert imports.exists(),'Build stage must first write exact candidate imports'
sources=sorted((ROOT/'src/engine').glob('dark-knight*.c'))+sorted((ROOT/'src/engine').glob('dark-knight*.s'))
compiler=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-gcc.exe')
records=[]
for source in sources:
    obj=out/(source.name+'.o')
    command=[compiler,'-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror',
        '-I',str(ROOT/'build/expansion'),'-I',str(ROOT/'src/engine'),'-I',str(out),'-c',str(source),'-o',str(obj)]
    subprocess.run(command,check=True,cwd=ROOT)
    records.append(dict(source=str(source.relative_to(ROOT)),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),objectSha256=hashlib.sha256(obj.read_bytes()).hexdigest()))
report=dict(passed=True,scope='ARM translation-unit compilation only; no linked ROM or gameplay acceptance',baseSha1=prior['romSha1'],records=records)
(out/'batch-compilation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
