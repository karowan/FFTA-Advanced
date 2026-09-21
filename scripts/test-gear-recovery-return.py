"""Actual20-day equipment returns, reward UI and cold Save/Continue.

The declared fixture supplies original progress, missing gear and level50 Ford.
Native generation/assignment supplies the mission, reward, duration and quality.
Ordinary world travel and confirmation keys own the entire return/collection.
This does not certify the separate pub acceptance/payment flow.
"""
import atexit
import ctypes
import hashlib
import json
import pathlib
import runpy
import struct
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom=pathlib.Path(meta['path']).read_bytes(); assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
selected=int(sys.argv[sys.argv.index('--mission')+1]) if '--mission' in sys.argv else None
full_stock='--full-stock' in sys.argv
routes=[r for r in meta['missionRecovery']['gear']['routes'] if selected is None or r['mission']==selected]
assert routes,'Unknown recovery selection'
source=pathlib.Path(meta['path']).parent/'gear-recovery'
prior=json.loads((source/'report.json').read_text(encoding='utf-8'))
assert prior['romSha1']==meta['romSha1']
# The preceding run completed all gear cases before a separate unchanged-code
# assertion failed. Reuse only its authenticated cold fixture, not that failure
# as a blanket passing report. Successful per-route lifecycle checks are explicit.
for rule in routes:
    assert f"{rule['mission']}/success: held gear suppresses repeat offer" in prior['checks']
for name,digest in prior['files'].items():
    assert hashlib.sha1((source/name).read_bytes()).hexdigest()==digest
OUT=pathlib.Path(meta['path']).parent/('gear-return'+(f'-{selected}' if selected else '')+('-full-stock' if full_stock else '')); OUT.mkdir(exist_ok=True)
private=OUT/'fixture.gba'; private.write_bytes(rom)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
checks=[]; observations=[]; inputs=[]; current_mission=0

def check(ok,label):
    assert ok,(current_mission,label)
    checks.append(dict(mission=current_mission,label=label))

def report(passed=False):
    r=dict(passed=passed,romSha1=meta['romSha1'],assertions=len(checks),checks=checks,
           observations=observations,inputs=inputs,sourceFiles=prior['files'],scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    return r

atexit.register(report)

def tap(e,key,wait=240):
    inputs.append(dict(mission=current_mission,frames=8,key=key,wait=wait))
    e.run(8,key); e.run(wait)

def native(e):
    m=a['ARM'](ctypes.string_at(*e.maps[0x03000000]))
    m.put(0x08000000,rom); m.put(0x02000000,e.memory())
    return m

def row(ram):
    return next((ram[p:p+16] for p in range(0x21c8,0x25c8,16)
                 if (ram[p]|((ram[p+1]&3)<<8))==current_mission),None)

def capture(e,label):
    label=f'{current_mission}-{label}'; ram=e.memory(); rec=row(ram)
    e.save(OUT/(label+'.state')); e.screenshot(OUT/(label+'.png'))
    (OUT/(label+'.ram')).write_bytes(ram)
    observations.append(dict(mission=current_mission,label=label,cached=rec.hex() if rec else None,
         assigned=struct.unpack_from('<H',ram,0x2a6)[0],
         gear={r['item']:ram[0x1940+r['item']] for r in meta['missionRecovery']['gear']['routes']},
         stateSha1=hashlib.sha1((OUT/(label+'.state')).read_bytes()).hexdigest(),
         ramSha1=hashlib.sha1(ram).hexdigest()))
    return ram

for rule in routes:
    current_mission=rule['mission']; item=rule['item']
    e=h['Emulator'](private)
    try:
        e.load(source/'cold-world.state'); e.run(1)
        ram=bytearray(e.memory()); ram[0x21c8:0x28cc]=bytes(0x704)
        for bit in [54]+([rule['originalMission']+0x2ff] if 'originalMission' in rule else []):ram[0x1f70+(bit>>3)]|=1<<(bit&7)
        if 'originalGift' in rule:ram[0x2c08+(rule['originalGift']>>3)]|=1<<(rule['originalGift']&7)
        if full_stock:ram[0x1941:0x1940+461]=bytes([99])*460
        ram[0x1940+item]=0; ram[0x299]=50
        m=native(e); m.put(0x02000000,ram); m.call(0x080cfcd0,0)
        posted=m.get(0x02000000,0x40000)
        at=next(p for p in range(0x21c8,0x25c8,16) if (posted[p]|((posted[p+1]&3)<<8))==current_mission)
        m.call(0x080d0b48,0x02000000+at,0x02000290,0,0)
        prepared=m.get(0x02000000,0x40000); accepted=row(prepared)
        check(accepted is not None and accepted[2]&0x1c==0 and accepted[6]>0,'Native assignment/quality accepts dispatch')
        check(struct.unpack_from('<HH',accepted,8)==(item,0),'Native cached reward is exact original equipment')
        for start,end in ((0x80,0x1f40),(0x1f70,0x2030),(0x21c8,0x28cc),(0x2c08,0x2c10)):
            e.set_memory(start,prepared[start:end])
        before=capture(e,'accepted'); elapsed=0
        for leg in range(1,13):
            area=8 if leg%2 else 2
            n=native(e); tile=n.call(0x08036330,area)
            check(0<tile<32,'Declared travel destination is placed')
            target=(n.call(0x08035a20,tile-1)+6,n.call(0x08035a44,tile-1)+4)
            route=[]
            for _ in range(600):
                x,y=struct.unpack_from('<HH',e.memory(),0x2c16)
                if abs(x-target[0])<=2 and abs(y-target[1])<=2:break
                key=(128 if x<target[0] else 64) if abs(x-target[0])>2 else (32 if y<target[1] else 16)
                e.run(1,key);route.append([x,y,key])
            else:raise AssertionError((current_mission,'World cursor bound',leg))
            inputs.append(dict(mission=current_mission,leg=leg,area=area,route=route))
            e.run(30);tap(e,256,1200); ram=capture(e,f'travel-{leg:02}')
            rec=row(ram); check(rec is not None,'Accepted dispatch persists during travel')
            days=(rec[1]>>2)|((rec[2]&3)<<6)
            check(days<20-elapsed,'Ordinary travel advances native dispatch days')
            elapsed=20-days
            if not days:break
            tap(e,1,180);tap(e,1,180)
        check(elapsed==20,'All20 days elapsed without timer or outcome writes')
        tap(e,256);capture(e,'return-list');tap(e,256);capture(e,'reward-screen')
        tap(e,256);after=capture(e,'collected')
        check(after[0x1940+item]==1,'Actual reward confirmation grants exactly one missing equipment')
        expected=bytearray(before[0x1940:0x1b40]);expected[item]=1
        check(after[0x1940:0x1b40]==expected,'Every other equipment count is preserved')
        check(struct.unpack_from('<H',after,0x2a6)[0]==0 and not struct.unpack_from('<H',after,0x2b8)[0]&4,'Actual return releases Ford')
        check(after[0x1f64:0x1f68]==before[0x1f64:0x1f68],'Return charges no additional fee')
        check(all(((after[0x1f70+((mission+0x2ff)>>3)]^before[0x1f70+((mission+0x2ff)>>3)]) &
                   (1<<((mission+0x2ff)&7)))==0 for mission in range(512)),'No mission-completion bits borrowed')
        check(native(e).call(meta['symbols']['ffta_recovery_needed'],current_mission)==0,'Collected equipment suppresses new recovery')
        for _ in range(2):tap(e,1,180)
        saved=e.memory()
        for key,wait in ((8,40),(16,40),(256,40),(256,60),(256,60),(64,20),(256,300)):tap(e,key,wait)
        sram=e.memory(0); (OUT/f'{current_mission}.srm').write_bytes(sram)
        e.close(); e=h['Emulator'](private); e.set_memory(0,sram,0); e.run(3600)
        for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(e,key,wait)
        cold=capture(e,'cold-continue')
        check(cold[0x1940:0x1f40]==saved[0x1940:0x1f40],'Exact inventory/AP extension survives cold Continue')
        check(cold[0x80:0x1940]==saved[0x80:0x1940],'Returned roster/AP survives cold Continue')
        check(cold[0x1f64:0x1f68]==saved[0x1f64:0x1f68],'Gil survives cold Continue')
        check(cold[0x2c08:0x2c10]==saved[0x2c08:0x2c10],'Original clan-gift receipts survive cold Continue')
        check(native(e).call(meta['symbols']['ffta_recovery_needed'],current_mission)==0,'Saved copy still suppresses recovery')
    finally:e.close()
atexit.unregister(report)
r=report(True)
print(json.dumps({k:r[k] for k in ('passed','romSha1','assertions')},indent=2))
