"""Retained native weapon command markers never count as image-frame proof."""
import datetime,json,struct
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import actors
source=ROOT/'build/art/generated-actions/battle/20260918T132505.952963Z'
out=ROOT/'build/art/command-marker'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    pins={'baseline-failed.ram':'9d22ff10dcb4c52a1617c5633eee88a9877daee6281a578e4e923a469a33679d',
          'baseline-failed.vram':'cbfc3b9a378d16cc50db10dd5f838fde27c5d51f157486161e1aa82547dc738c',
          'failed.json':'ccc5076171afc43649a828658989e48d65833c4a5f2e997bd9c5b3be386d4f90'}
    data={k:(source/k).read_bytes() for k in pins}
    for k,v in data.items():check(sha(v)==pins[k],'Authenticated '+k)
    m=json.loads((ROOT/'build/art/generated-equipment/ed8632de8cebcf87398b9aa778fe395cbb31c713/manifest.json').read_text())
    import hashlib
    rom=Path(m['path']).read_bytes();check(hashlib.sha1(rom).hexdigest()==m['romSha1'],'Exact failed control ROM')
    ram,vram=data['baseline-failed.ram'],data['baseline-failed.vram'];address=0x21084
    a,=actors(rom,ram,vram,{address})
    check((a['resource'],a['mode'],a['index'])==(128,7,2),'Actual held stream at command/image boundary')
    check(0 not in a['displayedFrames'] and set(a['displayedFrames'])<={1},'Only current image can establish upload, never command marker')
    first=a['first']-0x08000000
    check(struct.unpack_from('<II',rom,first)==(65535,0xffffffff),'Exact native sentinel encoding')
    damaged=bytearray(rom);struct.pack_into('<I',damaged,first,65534)
    try:actors(damaged,ram,vram,{address})
    except (AssertionError,struct.error):pass
    else:raise AssertionError('Malformed sentinel was silently accepted')
    checks.append('Near-match sentinel remains an error')
    commands=bytearray(rom);struct.pack_into('<II',commands,first+20,65535,0xffffffff)
    empty,=actors(commands,ram,vram,{address})
    check(not empty['displayedFrames'],'Two commands cannot manufacture a rendered image proof')
    check(all((source/k).read_bytes()==v for k,v in data.items()),'Original failed evidence unchanged')
    report=dict(status='passed',romSha1=m['romSha1'],checks=checks,source=str(source),sha256=pins,
        scope='Read-only decoder correction and in-memory rejection controls from retained failure. No emulator, new battle fixture or actual held-action acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');print(out);raise
