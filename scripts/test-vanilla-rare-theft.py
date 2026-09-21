"""Original rare-gear theft consumers using actual repeatable-source loadouts.

The template supplies job, gear, mastery, reaction and support. A declared
ordinary opposing unit supplies level/stats/position; this is not encounter
construction or a rendered battle. Native admission, accuracy, RNG, application,
equipment depletion and inventory transactions run without substituted results.
"""
import atexit
import hashlib
import json
import pathlib
import runpy
import struct

ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom=pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
ledger=json.loads((ROOT/'build/reports/vanilla-teaching-sources.json').read_text(encoding='utf-8'))
assert ledger['candidateSha1']==meta['romSha1']
source=pathlib.Path(meta['path']).parent/'gear-recovery'
pr=json.loads((source/'report.json').read_text(encoding='utf-8'))
assert pr['romSha1']==meta['romSha1']
for name,value in pr['files'].items():assert hashlib.sha1((source/name).read_bytes()).hexdigest()==value
ram=(source/'cold-world.ram').read_bytes();iwram=(source/'cold-world.iwram').read_bytes()
m=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))['ARM'](iwram)
m.put(0x08000000,rom)
OUT=pathlib.Path(meta['path']).parent/'rare-theft';OUT.mkdir(exist_ok=True)
A,T,C=0x02000080,0x020033e4,0x02008000
checks=[];cases=[]


def check(ok,label):
    assert ok,label
    checks.append(label)


def report(passed=False):
    r=dict(passed=passed,romSha1=meta['romSha1'],assertions=len(checks),checks=checks,
           cases=cases,fixtureFiles=pr['files'],scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    return r


atexit.register(report)
items=[i for i in ledger['rows'] if i['id'] in (68,116,183,313,314)]
for item in items:
    sources=[f for f in item['formationPossession'] if any(e['roamingClan'] or
             any(x['repeatable'] for x in e['missions']) for e in f['events'])]
    acquired=False
    for f in sources:
        template=f['unitOffset'];job=f['job'];action=163 if f['gear'] else 167
        check(f['type']==1,'Original ordinary source template')
        check(struct.unpack_from('<H',rom,template+8+f['gear']*2)[0]==item['id'], 'Actual template holds rare item')
        m.put(0x02000000,ram);m.put(0x03000000,iwram)
        for pointer,which in ((A,5),(T,job)):
            u=bytearray(ram[0x80:0x188]);u[4]=1;u[5]=u[7]=which
            u[6]=rom[0x521a14+which*52+4];u[9]=30
            u[0x28:0x2a]=bytes((0,0 if pointer==A else 128))
            u[0x2a:0x34]=rom[template+8:template+18] if pointer==T else struct.pack('<5H',74,0,0,0,0)
            u[0x3a:0x3d]=bytes(3);u[0xe8:0xf0]=bytes(8)
            u[0xf6:0xf9]=bytes((4 if pointer==A else 5,14,0))
            struct.pack_into('<4H',u,0x18,100,100,50,50)
            struct.pack_into('<4H',u,0x20,100,50,100,50)
            m.put(pointer,u)
        # Original constructor's packed mastery import; actual assigned
        # reaction/support are not cleared to make stealing easier.
        m.call(0x080c9f88,T,0x08000000+template+20)
        m.put(T+0x3a,rom[template+40:template+42])
        m.put(0x02001940+item['id'],b'\0')
        m.put(C,bytes(52));m.call(0x0812f230,C,action,0,0);m.call(0x0812f3b0,C,0)
        m.put(C,struct.pack('<III',A,T,T))
        before=m.get(0x02000000,0x40000)
        support=m.call(0x080cd50c,T)
        eligible=m.call(0x08130c44,C)
        chance=m.call(0x08131188,C)
        check(m.get(0x02000000,0x40000)==before,'Theft admission/accuracy is read-only')
        check(eligible==1,'Living opposing target is eligible')
        row=dict(item=item['id'],formation=f['formation'],slot=f['slot'],job=job,
                 support=support,action=action,chance=chance,events=f['events'])
        cases.append(row)
        if support==9:
            check(chance==0,'Maintenance blocks theft; not counted as an acquisition witness')
            row['acquired']=False
            continue
        check(0<chance<=100,'Original source has a positive theft chance')
        m.w16(C+0x26,0x10);before=m.get(0x02000000,0x40000)
        m.call(0x08132ee8,C)
        check(m.get(0x02000000,0x40000)==before,'Theft preview cannot deplete equipment or grant loot')
        m.w16(C+0x26,0)
        # Fixed seeds, bounded16 attempts. The real hit RNG makes the choice;
        # no forced hit or callback result. Retain the successful seed.
        for seed in range(16):
            m.w32(0x030034b0,seed)
            if m.call(0x0812f1dc,chance):break
        else:raise AssertionError(('No native hit in fixed seed set',row))
        before_bag=m.get(0x02001940,512);before_gear=m.get(T+0x2a,10)
        m.call(0x08132ee8,C)
        expected=bytearray(before_bag);expected[item['id']]+=1
        check(m.get(0x02001940,512)==expected,'Exactly one rare item granted by native theft')
        expected_gear=bytearray(before_gear);expected_gear[f['gear']*2:f['gear']*2+2]=bytes(2)
        check(m.get(T+0x2a,10)==expected_gear,'Only stolen equipment slot depleted')
        check(m.r16(C+0x18)==item['id'],'Native theft result reports the actual rare item')
        row.update(acquired=True,seed=seed)
        acquired=True
    check(acquired,f'At least one unprotected repeatable-source loadout grants item{item["id"]}')
check(any(r['support']==9 and not r['acquired'] for r in cases),'Nonvacuous Maintenance control')
atexit.unregister(report)
r=report(True)
print(json.dumps({k:r[k] for k in ('passed','romSha1','assertions')},indent=2))
