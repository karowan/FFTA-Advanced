"""Installed late equipment services: gates, queues and native lifecycle.

One deterministic cold world supplies IWRAM/roster inputs. Native posting,
assignment, day advancement and retirement run unchanged. Controlled success
and failure are explicitly separate from actual return/reward UI acceptance.
Also exhaustively verify the unchanged clan-battle reward selector by seeding
its real LCG; no RNG function or reward result is replaced.
"""
import atexit
import ctypes
import hashlib
import itertools
import json
import pathlib
import runpy
import struct
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom=pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
gear=meta['missionRecovery']['gear']; routes=gear['routes']
CLAN_ONLY='--clan-only' in sys.argv
OUT=pathlib.Path(meta['path']).parent/('clan-rewards' if CLAN_ONLY else 'gear-recovery'); OUT.mkdir(exist_ok=True)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
seed=(ROOT/'build/test-lab/early-town.sav').read_bytes()
private=OUT/'fixture.gba'; private.write_bytes(rom)
e=h['Emulator'](private)
try:
    e.set_memory(0,seed,0); e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):
        e.run(8,key); e.run(wait)
    base=e.memory(); iwram=ctypes.string_at(*e.maps[0x03000000])
    assert base[0x1e70:0x1e79]==b'FFTAEXP1\x01'
    e.save(OUT/'cold-world.state'); e.screenshot(OUT/'cold-world.png')
finally:e.close()
(OUT/'cold-world.ram').write_bytes(base); (OUT/'cold-world.iwram').write_bytes(iwram)
m=a['ARM'](iwram); m.put(0x08000000,rom)
checks=[]; observations=[]

def check(ok,label):
    assert ok,label
    checks.append(label)

def report(passed=False):
    r=dict(passed=passed,romSha1=meta['romSha1'],assertions=len(checks),checks=checks,
           observations=observations,scope=__doc__,seedSha1=hashlib.sha1(seed).hexdigest(),
           files={name:hashlib.sha1((OUT/name).read_bytes()).hexdigest() for name in
                  ('cold-world.state','cold-world.ram','cold-world.iwram')})
    (OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    return r

atexit.register(report)

def flag(ram,index,value=True):
    at=0x1f70+(index>>3); mask=1<<(index&7)
    ram[at]=ram[at]|mask if value else ram[at]&~mask

def reset(rule,cleared=True,original=True,held=0):
    ram=bytearray(base)
    ram[0x1f70:0x2030]=bytes(0xc0); ram[0x21c8:0x28cc]=bytes(0x704)
    for r in routes:ram[0x1940+r['item']]=0
    flag(ram,gear['requiredFlag'],cleared)
    ram[0x2c08:0x2c10]=bytes(8)
    if 'originalMission' in rule:flag(ram,rule['originalMission']+0x2ff,original)
    elif original:ram[0x2c08+(rule['originalGift']>>3)]|=1<<(rule['originalGift']&7)
    ram[0x1940+rule['item']]=held
    ram[0x299]=50  # One declared ordinary dispatch member; no outcome is forced.
    m.put(0x02000000,ram); m.put(0x03000000,iwram)
    return ram

def needed(rule):return m.call(meta['symbols']['ffta_recovery_needed'],rule['mission'])

def queue():
    ptr=m.r32(0x020028c8); result={}; previous=0
    while ptr:
        assert 0x020025c8<=ptr<0x020028c8 and (ptr-0x020025c8)%12==0
        record,prev,nxt=struct.unpack('<III',m.get(ptr,12))
        assert prev==previous and 0x020021c8<=record<0x020025c8
        row=m.get(record,16); mission=row[0]|((row[1]&3)<<8)
        assert mission not in result and len(result)<64
        result[mission]=record; previous,ptr=ptr,nxt
    return result

for rule in ([] if CLAN_ONLY else routes):
    mission=rule['mission']
    for cleared,original,held in itertools.product((False,True),(False,True),(0,1,99)):
        ram=reset(rule,cleared,original,held)
        check(needed(rule)==int(cleared and original and not held),f'{mission}: gate {cleared}/{original}/{held}')
        check(m.get(0x02000000,0x40000)==ram,f'{mission}: gate is read-only')
    if 'originalGift' in rule:
        reset(rule,original=False)
        # Being postgame with maxed skills does not bypass original receipt.
        m.put(0x020021b6,bytes((99,0))*8)
        check(needed(rule)==0,f'{mission}: skill thresholds alone never grant recovery')
        # Original gift consumer owns the entitlement. Isolate its row using
        # the previously audited claim mask; all skill requirements are native.
        gift=rule['originalGift']
        m.put(0x02002c08,(((1<<64)-1)^(1<<gift)).to_bytes(8,'little'))
        check(m.call(0x08046910,0x02030000)==rule['item'],f'{mission}: original gift reward matches recovery')
        check(needed(rule)==1,f'{mission}: original gift claim authorizes missing copy')
        # An unrelated completed mission must not masquerade as a gift receipt.
        reset(rule,original=False);m.put(0x02001f70,bytes([255])*0xc0)
        check(needed(rule)==0,f'{mission}: mission flags cannot bypass gift receipt')
    reset(rule)
    for selector,want in ((0x11,1),(0x12,20),(0x36,10000),(0x38,1),(0x39,30),(0x3a,30)):
        check(m.call(0x080ce4dc,mission,selector)==want,f'{mission}: native field{selector}')
    m.call(0x080cfcd0,0); entries=queue()
    check(mission in entries,f'{mission}: full native generator posts service')
    record=entries[mission]; posted=m.get(record,16)
    check(struct.unpack_from('<HH',posted,8)==(rule['item'],0),f'{mission}: ordinary equipment reward identity')
    m.call(0x080cfcd0,0)
    check(queue()==entries,f'{mission}: no duplicate offer')
    m.put(0x02030100,b'\xa5'*4)
    count=m.call(0x080d0590,0x02030000,64,0)
    check(count<=64 and record in struct.unpack('<64I',m.get(0x02030000,256)),f'{mission}: native pub enumeration')
    check(m.get(0x02030100,4)==b'\xa5'*4,f'{mission}: pub output bound')
    m.put(0x02001940+rule['item'],b'\x01')
    m.call(meta['symbols']['ffta_recovery_prune_offers'])
    check(mission not in queue(),f'{mission}: acquired copy prunes unaccepted offer')
    m.put(0x02001940+rule['item'],b'\x00'); m.call(0x080cfcd0,0)
    record=queue()[mission]
    m.call(0x080d0b48,record,0x02000290,0,0)
    accepted=m.get(record,16)
    check(accepted[2]&0x1c==0 and accepted[3]==255,f'{mission}: native assignment')
    check((accepted[1]>>2)|((accepted[2]&3)<<6)==20,f'{mission}: accepted duration')
    check(m.r16(0x020002a6)==mission and m.r16(0x020002b8)&4,f'{mission}: assigned member identity')
    checkpoint=m.get(0x02000000,0x40000)
    for outcome in ('cancel','failure','success'):
        m.put(0x02000000,checkpoint); m.put(0x03000000,iwram)
        before_flags=m.get(0x02001f70,0xc0)
        if outcome=='cancel':
            m.call(0x080d0ed4,record)
        else:
            for day in range(1,21):
                count=m.call(0x080d1c94,0x02030000,64,1)
                row=m.get(record,16)
                check((row[1]>>2)|((row[2]&3)<<6)==20-day,f'{mission}/{outcome}: day{day}')
                check(count==int(day==20),f'{mission}/{outcome}: return on day20 only')
            m.call(0x080d1e70,record,int(outcome=='success'))
        check(m.get(0x02001f70,0xc0)==before_flags,f'{mission}/{outcome}: no service completion flag')
        check(m.r16(0x020002a6)==0 and not m.r16(0x020002b8)&4,f'{mission}/{outcome}: member returned')
        row=m.get(record,16)
        check(row[2]&0x1c==12 and row[3]==30,f'{mission}/{outcome}: native30-day cooldown')
        for day in range(30):m.call(0x080cf51c)
        check(mission not in queue(),f'{mission}/{outcome}: expired cooldown retires')
        check(needed(rule)==1,f'{mission}/{outcome}: missing gear stays recoverable')
        m.put(0x02001940+rule['item'],b'\x01')
        check(needed(rule)==0,f'{mission}/{outcome}: held gear suppresses repeat offer')
    observations.append(dict(mission=mission,item=rule['item'],accepted=accepted.hex()))

# Exact original D2114 admission: Mythril bit7 survives every shop-stage mask.
# Invert the real LCG to choose each possible residue once. The real RNG runs,
# changes its own IWRAM seed and the native selector decides the returned item.
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
for start,end in ((0xd2114,0xd2158),(0xd215c,0xd21a0),(0xd21a4,0xd21a8),(0x2804,0x2824)):
    check(rom[start:end]==clean[start:end],'Original clan reward code unchanged')
item_table=struct.unpack_from('<I',rom,0xca7c4)[0]
for literal in (0xd2158,0xd21a0):
    check(struct.unpack_from('<I',rom,literal)[0]==item_table,'Clan reward literal uses installed item table')
offset=item_table-0x08000000
check(rom[offset+32:offset+376*32]==clean[0x51d1a0:0x51d1a0+375*32], 'Original clan reward item records preserved')
mult,add=struct.unpack_from('<II',clean,0x281c)
inverse=pow(mult,-1,1<<32)
mythril=[9,27,37,48,85,101,117,132,146,159,171,185,197,212,226,238,250]
for battles in (0,10,11,20,21,65535):
    reset(routes[0]); m.w16(0x02001f6c,battles)
    mask=0x90 if battles<=10 else 0xa0 if battles<=20 else 0xc0
    candidates=[item for item in range(1,376) if clean[0x51d180+item*32+12]&mask]
    seen=[]; before=m.get(0x02000000,0x40000)
    for index,item in enumerate(candidates):
        seed_value=(((index<<16)-add)*inverse)&0xffffffff
        m.w32(0x030034b0,seed_value)
        result=m.call(0x080d2114)
        check(result==item,f'Clan rewards stage{battles}: candidate{item}')
        check(m.r32(0x030034b0)==index<<16,f'Clan rewards stage{battles}: real RNG progression')
        seen.append(result)
    check(set(mythril)<=set(seen),f'Clan rewards stage{battles}: all17 combo weapons reachable')
    check(m.get(0x02000000,0x40000)==before,f'Clan rewards stage{battles}: no saved progress mutation')
    observations.append(dict(battleCounter=battles,mask=mask,candidates=candidates))
atexit.unregister(report)
r=report(True)
print(json.dumps({k:r[k] for k in ('passed','romSha1','assertions')},indent=2))
