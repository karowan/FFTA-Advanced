"""Real mGBA shop boundary and purchase check with a retained disposable save.

Cold-load early-town, then replay the same shop inputs at 9/10/20 battles and
an early story clear. Only declared counters/flags/gil differ; no player save
is read or written. The native engine constructs the displayed list. The
10-battle case buys Infernal Edge through the actual quantity/confirm dialogs.
"""
import datetime, hashlib, json, runpy, struct
from pathlib import Path
from chemist_candidate import candidate
from shop_progression import ROOT, catalog

meta=candidate();rom=Path(meta['path']);raw=rom.read_bytes()
out=rom.parent/('shop-ui-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
seedpath=ROOT/'build/test-lab/early-town.sav';seed=seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest()=='b0199e7490f7c22f84512825a4a1bde08d3b3eec'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
e=E(rom);inputs=[];checks=[];samples=[];failure=None
rows=catalog()
def check(ok,label):
    assert ok,label
    checks.append(label)
def tap(key,wait=120):inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
def u16(r,p):return struct.unpack_from('<H',r,p)[0]
def u32(r,p):return struct.unpack_from('<I',r,p)[0]
try:
    e.set_memory(0,seed,0);e.run(3600)
    for key in (8,256,256,256):tap(key,300)
    e.save(out/'cold-world.state')
    for battles,story in ((9,False),(10,False),(20,False),(9,True)):
        e.load(out/'cold-world.state');e.set_memory(0x1f6c,struct.pack('<H',battles))
        for flag in (774,780,786):
            at=0x1f70+flag//8;value=e.memory()[at]&~(1<<(flag&7))
            if flag==774 and story:value|=1<<(flag&7)
            e.set_memory(at,bytes([value]))
        e.set_memory(0x1f64,struct.pack('<I',50000))
        for key,wait in ((256,240),(32,120),(256,180),(256,120),(128,80),(128,120)):tap(key,wait)
        ram=e.memory();base=u32(ram,0xf428)-0x02000000
        check(0<=base<=0x40000-0xa350,'Native shop context')
        town=ram[base+0x4bfb];count=u16(ram,base+0xa338)
        check(town==3 and 0<count<256,'Retained seed enters Sprohm weapon tab')
        ids=[u16(ram,base+0x9c08+4*i) for i in range(count)]
        unlocked=(True,story or battles>=10,battles>=20,False)
        wanted=[r['id'] for r in rows if r['towns']&(1<<town) and unlocked[r['stage']]]
        check([i for i in ids if i>=376]==wanted,'Actual menu stock '+str((battles,story)))
        check(not any(r['id'] in ids for r in rows if r['stage']==3),'Final shipment stays gated')
        stem=f'battles-{battles}-story-{int(story)}';e.screenshot(out/(stem+'.png'))
        sample=dict(battles=battles,story=story,town=town,ids=ids);samples.append(sample)
        if battles==10:
            row=next(r for r in rows if r['name']=='Infernal Edge');ident=row['id'];index=ids.index(ident)
            check(ram[0x1940+ident]==0,'Target starts unowned')
            for _ in range(index):tap(32,16)
            r=e.memory();check(u16(r,base+0x44ec)==ident,'New first-shipment item selected')
            e.screenshot(out/'new-weapon-selected.png')
            item_table=u32(raw,0x79aec)-0x08000000
            record=raw[item_table+32*ident:item_table+32*(ident+1)]
            discount_table=u32(raw,0xcbc78)-0x08000000
            rank_at=u32(raw,0xcbc7c)+u32(raw,0xcbc80)-0x02000000
            clan=raw[discount_table+r[rank_at]*10+8]
            # Sprohm's native category mask, authenticated by the native matrix.
            favored=bool(u32(raw,0x528aa4)&(1<<(record[8]-1)))
            quote=max(row['price']//2,row['price']*(100-clan-10*int(favored))//100) if record[12]&8 else row['price']
            before=r[0x1940:0x1b40];money=u32(r,0x1f64)
            for wait in (80,120,180):tap(256,wait)
            r=e.memory();wanted_owned=bytearray(before);wanted_owned[ident]+=1
            check(r[0x1940:0x1b40]==wanted_owned,'Native dialogs grant exactly one new teacher')
            check(u32(r,0x1f64)==money-quote,'Native dialogs charge revised discounted price')
            sample['purchase']=dict(item=ident,basePrice=row['price'],paid=quote)
            e.screenshot(out/'purchased.png')
    check(seedpath.read_bytes()==seed,'Retained save unchanged')
except BaseException as error:
    failure=repr(error)
    if e.frame:e.screenshot(out/'failed.png')
    raise
finally:
    e.close()
    report=dict(passed=failure is None,romSha1=meta['romSha1'],seedSha1=hashlib.sha1(seed).hexdigest(),checks=checks,inputs=inputs,samples=samples,error=failure,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],romSha1=meta['romSha1'],checks=len(checks),report=str(out/'report.json'))),flush=True)
