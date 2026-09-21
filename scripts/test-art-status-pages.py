"""Inspect native read-only battle Status pages from an exact retained state."""
import ctypes as C
import datetime
import hashlib
import json
import runpy
import struct
import sys
from pathlib import Path
from native_art import ROOT, sha

SOURCE = ROOT/'build/art/owned-menu/battle/20260918T171936.852610Z'
PIN = {'report.json':'63c9cb6987a151ab0a8588ab9cb2dfac69a40d4fdf2d1c38a7cab76250baa571',
       'status.state':'240c10095b52fc16f293079d05d1b8b1bfaec04cfd8e61c6e1b424862d001da3',
       'status.ram':'b69d644dc39e817f479081107ac4734ed72d53217ddf42f3f334bf092fa95e1d',
       'status.iwram':'f8eda6ef6857eb88c5d5b269e52461f4152f24aaed56d32e7963572b2f10e41a'}
META = ROOT/'build/art/connected/7b966543796975a6dea474d0a360495b57d8e6a3/manifest.json'
E = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out = ROOT/'build/art/status-pages'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks, captures, inputs = [], {}, {}
e = None
details = '--details' in sys.argv


def check(ok, label):
    assert ok, label
    checks.append(label)


def word(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


try:
    for name, digest in PIN.items():
        check(sha((SOURCE/name).read_bytes()) == digest, 'Authenticated '+name)
    meta = json.loads(META.read_text(encoding='utf-8'))
    rom = Path(meta['path']).read_bytes()
    check(hashlib.sha1(rom).hexdigest() == meta['romSha1'] ==
          '7b966543796975a6dea474d0a360495b57d8e6a3', 'Exact state ROM identity')
    initial = (SOURCE/'status.ram').read_bytes()
    original_iw = (SOURCE/'status.iwram').read_bytes()
    ctx = word(original_iw, 0x2818)
    canonical = initial[0x80:0x1e70]
    def capture(label):
        ram = e.memory()
        iw = C.string_at(*e.maps[0x03000000])
        check(ram[0x80:0x1e70] == canonical, label+' canonical player records unchanged')
        check(word(iw, 0x2818) == ctx and word(ram, 0x3ff40) == ctx,
              label+' original Status context and live copy owner agree')
        root = meta['components']['livePalette']['partyHeapRoot']-0x02000000
        check(struct.unpack_from('<4I',ram,root) == (0x50485231,word(ram,0xf434),1,0)
              and ram[ctx-0x02000000-8:ctx-0x02000000-6] == b'la',
              label+' live shared heap lifetime and allocation header')
        e.screenshot(out/(label+'.png'))
        e.save(out/(label+'.state'))
        for ext, data in [('ram', ram), ('iwram', iw)]:
            (out/(label+'.'+ext)).write_bytes(data)
        pointer = word(ram, ctx-0x02000000+0x2d50)
        check(pointer == ctx+0x7280, label+' context-owned list pointer unchanged')
        data = ram[pointer-0x02000000:pointer-0x02000000+0x2700]
        captures[label] = dict(ramSha256=sha(ram), iwramSha256=sha(iw),
            listNonzero=sum(x != 0 for x in data), listSha256=sha(data),
            listHeader=data[:0x30].hex(), contextSha256=sha(ram[ctx-0x02000000:ctx-0x02000000+0x9980]))
    cases=[(p,n) for p in range(2) for n in range(6)] if details else [(p,5) for p in range(5)]
    for pages,cursor_steps in cases:
        case='right-'+str(pages)+('-cursor-'+str(cursor_steps) if details else '')
        inputs[case]=[]
        e=E(Path(meta['path']))
        e.load(SOURCE/'status.state')
        check(e.memory() == initial and C.string_at(*e.maps[0x03000000]) == original_iw,
              case+' exact retained memory')
        e.run(1)
        for index in range(pages):
            e.run(8, 128); e.run(180); inputs[case].append([8,128,180])
        capture(case+'-page')
        if details:
            e.run(8, 4); e.run(180); inputs[case].append([8,4,180])
            capture(case+'-details')
        for index in range(cursor_steps):
            e.run(8, 32); e.run(180); inputs[case].append([8,32,180])
        capture(case+'-cursor')
        if details:
            e.run(8, 256); e.run(180); inputs[case].append([8,256,180])
            capture(case+'-open')
        else:
            for index in range(pages):
                e.run(8, 64); e.run(180); inputs[case].append([8,64,180])
            capture(case+'-left-return')
        e.close(); e=None
    for name,digest in PIN.items():
        check(sha((SOURCE/name).read_bytes()) == digest, 'Source unchanged '+name)
    report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],source=str(SOURCE),
        inputs=inputs,inputHashes=PIN,captures=captures,details=details,
        scope=('Twelve bounded native panel/Select/cursor/A-help cases.' if details else 'Five bounded native directional-page/down/left-return cases.')+
        ' Exact retained battle Status; canonical player records, actual shared lifetime, live copy owner, allocated context and list pointer checked. Raw list usage and screenshots are observations; no proof of all reachable menu states, maximum rows, memory optimization or current-candidate acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'),
        listNonzero={k:v['listNonzero'] for k,v in captures.items()})))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,
        inputs=inputs,captures=captures),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out))
    raise
finally:
    if e:e.close()
