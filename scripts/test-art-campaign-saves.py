"""Current engineering build cold-loads accepted ordinary and actual ending saves.

No old savestate crosses ROM layouts. The native title/Continue path allocates
fresh current state; only retained disposable flash is provided. Verify complete
24-slot profile, clear flag, retired transient state, and actual loaded postgame
mission/pub consumers on private clones. No ending playback or player files.
"""
import ast, ctypes as C, datetime, hashlib, json, runpy, struct, sys
from pathlib import Path
from native_art import ROOT, sha

index_path=ROOT/'notes/native-art-campaign-save-inputs.json';index=json.loads(index_path.read_text())
files={name:(ROOT/row['path']).read_bytes() for name,row in index['files'].items()}
assert all(sha(files[name])==row['sha256'] for name,row in index['files'].items())
ordinary=json.loads(files['ordinaryReport']);ending=json.loads(files['endingReport'])
assert ordinary['passed'] and ending['passed'] and ordinary['romSha1']==ending['romSha1']==index['producerSha1']
manifest=ROOT/'build/art/connected'/index['candidateSha1']/'manifest.json';meta=json.loads(manifest.read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==index['candidateSha1']==meta['romSha1']
out=ROOT/'build/art/campaign-saves'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
tree=ast.parse((ROOT/'scripts/test-independent-save-slots.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owned'],type_ignores=[]),'<saved profile>','exec'))
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<native heap>','exec'))
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03006800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native consumer>','exec'))
checks=[];inputs=[];captures={};consumers=[];e=None;case='setup'

def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)

def tap(key,wait=180):
    inputs.append(dict(case=case,press=8,key=key,wait=wait));e.run(8,key);e.run(wait)

def capture(label):
    stem=case+'-'+label;e.save(out/(stem+'.state'));e.screenshot(out/(stem+'.png'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(stem+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
    captures[stem]=dict(profile=owned(e.memory()),heap=heap(e.memory()),flashSha256=sha(e.memory(0)))

def queue(machine):
    node=machine.word(0x020028c8);previous=0;rows={}
    while node:
        assert 0x020025c8<=node<0x020028c8 and (node-0x020025c8)%12==0 and len(rows)<64
        ptr,prev,nxt=struct.unpack('<III',machine.read(node,12))
        assert prev==previous and 0x020021c8<=ptr<0x020025c8 and (ptr-0x020021c8)%16==0
        mid=int.from_bytes(machine.read(ptr,2),'little')&1023
        assert mid and mid not in rows;rows[mid]=ptr;previous,node=node,nxt
    return rows

try:
    for case,key,cleared in [('ordinary','ordinarySave',False),('ending','endingSave',True)]:
        saved=files[key];e=E(Path(meta['path']));e.set_memory(0,saved,0);e.run(3600)
        for button,wait in ((8,180),(256,60),(256,60),(256,180)):tap(button,wait)
        capture('cold-world');loaded=e.memory();iw=C.string_at(*e.maps[0x03000000])
        check(owned(loaded)==ordinary['profiles']['0'],'All24 roster/AP/inventory/preferences/history/gil fields preserved')
        check(all(loaded[0x84+slot*264] for slot in range(24)),'All24 occupied slots retained')
        check(bool(loaded[0x1f76]&64)==cleared,'Actual saved clear flag retained')
        check(loaded[0x3f410:0x3f728]==bytes(792),'Transient battle state retired on cold load')
        check(e.memory(0)==saved,'Continue does not rewrite saved flash')
        check(struct.unpack_from('<I',loaded,meta['components']['livePalette']['partyHeapRoot']-0x02000000)[0]==0,'No inherited borrowed battle-menu ownership')
        # Exercise the unchanged full-roster world menu allocation and teardown.
        tap(8);tap(256,600);capture('party');r=e.memory();ctx=struct.unpack_from('<I',C.string_at(*e.maps[0x03000000]),0x2818)[0]
        check(0x02000000<=ctx<ctx+0x9980<=0x0203c000,'Full world-party context allocated within owned memory')
        # World mode reuses battle globals; derive this menu's actual owner from
        # context[0]. Only a local read-only clone adapts the battle heap walker.
        owner=struct.unpack_from('<I',r,ctx-0x02000000)[0]
        clone=bytearray(r);struct.pack_into('<I',clone,0xf434,owner);h=heap(clone)
        check(0x02000000<=owner<ctx and h.get('end',0)<=0x0203c000 and
            any(b['marker']=='la' and b['address']+12==ctx and b['payloadBytes']>=0x9980 for b in h.get('allocationBlocks',[])),
            'Actual world menu heap owns the complete full-list context')
        captures[case+'-party']['activeOwnedHeap']=h
        check(struct.unpack_from('<I',r,ctx-0x02000000+0x2d50)[0]==ctx+0x7280,'World party retains full owned item list')
        check(owned(r)==ordinary['profiles']['0'],'World menu preserves complete saved profile')
        tap(1,300);tap(1,300);capture('returned-world')
        check(owned(e.memory())==ordinary['profiles']['0'] and e.memory(0)==saved,'World menu return preserves profile and flash')
        check(struct.unpack_from('<I',e.memory(),meta['components']['livePalette']['partyHeapRoot']-0x02000000)[0]==0,'World menu leaves no borrowed battle owner')
        if cleared:
            for positive in (False,True):
                m=ARM(rom,iw);state=bytearray(loaded)
                if not positive:state[0x1f76]&=~64
                m.put(0x02000000,state);m.call(0x080cfcd0,0);entries=queue(m)
                for mission in (202,378):check((mission in entries)==positive,'Loaded clear flag gates native mission '+str((mission,positive)))
                visible=set()
                for town in range(8):
                    m.put(0x02030100,b'\xa5'*4);count=m.call(0x080d0590,0x02030000,64,town)
                    check(count<=64 and m.read(0x02030100,4)==b'\xa5'*4,'Native postgame pub bounds '+str((town,positive)))
                    pointers=struct.unpack('<64I',m.read(0x02030000,256))[:count]
                    visible.update(mid for mid,p in entries.items() if p in pointers)
                for mission in (202,378):check((mission in visible)==positive,'Loaded postgame mission reaches actual pub '+str((mission,positive)))
                check(owned(m.read(0x02000000,0x40000))==owned(loaded),'Postgame selection preserves loaded profile '+str(positive))
                consumers.append(dict(cleared=positive,missions=sorted(entries),visible=sorted(visible)))
        e.close();e=None
    for name,row in index['files'].items():check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Accepted source remains unchanged '+name)
    report=dict(status='passed',romSha1=meta['romSha1'],manifestSha256=sha(manifest.read_bytes()),inputIndexSha256=sha(index_path.read_bytes()),scope=__doc__,checks=checks,inputs=inputs,captures=captures,consumers=consumers)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],scope=__doc__,case=case,error=str(error),checks=checks,inputs=inputs,captures=captures,consumers=consumers),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
