"""Exact-ROM shop admission, original stock, price and checkout regression.

Declared state inputs: five towns, 0/7/30 territories, battle counts at both
upgrade boundaries, and all independent story-flag combinations. No campaign
completion is simulated and no player save is used. Native list/price/purchase
entry points execute on ARM; the separate UI case covers real ARM7TDMI menus.
"""
import ast, collections, datetime, hashlib, json, struct, sys
from pathlib import Path
from shop_progression import ROOT, PARENT, PARENT_SHA1, CLEAN_SHA1, catalog
from chemist_candidate import candidate
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *

meta=candidate(); image=Path(meta['path']).read_bytes()
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(clean).hexdigest()==CLEAN_SHA1
out=Path(meta['path']).parent/('shop-tests-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
out.mkdir(); checks=collections.Counter(); case=None; failure=None
def check(label,condition):
    assert condition,(case,label)
    checks[label]+=1
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
STACK,RETURN=0x03007000,0x08000100
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
integrated=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
fixture=Path(integrated['path']).parent/'fixture'
iw=(fixture/'battle-ready.iwram').read_bytes()
check('authenticated retained IWRAM',hashlib.sha1(iw).hexdigest()==json.loads((fixture/'prepare-cache.json').read_text())['outputs']['battle-ready.iwram'])
m=ARM(image,iw); native=ARM(clean,iw)
def half(machine,address):return int.from_bytes(machine.read(address,2),'little')
def w16(machine,address,value):machine.put(address,struct.pack('<H',value))
def w32(machine,address,value):machine.put(address,struct.pack('<I',value))
def flag(value,on):m.call(0x080c9574,value,int(on))
rows=catalog(); dest=0x0203c000
try:
    parent=json.loads(PARENT.read_text()); original=Path(parent['path']).read_bytes()
    check('authenticated gameplay baseline',hashlib.sha1(original).hexdigest()==PARENT_SHA1)
    receipt=meta['shopProgression']; allowed=set()
    for p in receipt['patches']:
        before,after=bytes.fromhex(p['before']),bytes.fromhex(p['after']);at=p['offset']
        check('patch before/after bytes',original[at:at+len(before)]==before and image[at:at+len(after)]==after)
        allowed.update(range(at,at+len(after)))
    check('all non-shop gameplay bytes preserved',len(image)==len(original) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,image))))
    items=m.word(0x08079aec)
    check('375 original item records unchanged',m.read(items+32,375*32)==clean[0x51d1a0:0x51d1a0+375*32])
    check('original town stock unchanged',image[0x528a44:0x528c24]==clean[0x528a44:0x528c24])
    check('Flamberge price parity',next(r for r in rows if r['name']=='Polka Foil')['price']==5000)
    check('opening prices unchanged',all(r['price']==r['oldPrice'] for r in rows if r['stage']==0))
    # Read story/town assignments independently from the two source ledgers.
    ledger=json.loads((ROOT/'notes/equipment-acquisition.json').read_text())['items']
    registry=json.loads((ROOT/'build/expansion/registry.json').read_text())['items']
    ids={i['id']:i['romItemId'] for i in registry}
    towns={'Cyril':2,'Sprohm':3,'Muscadet':4,'Cadoan':5,'Baguba Port':6}
    expected_rows=[(ids[i['id']],int(i['stageId'][1:]),[towns[t] for t in [i['primaryShop'],*i['additionalShops']]]) for i in ledger]
    expected_rows += [(i['id'],int(i['stage'][1:])-1,[2]) for i in json.loads((ROOT/'notes/chemist-progression-equipment.json').read_text())['items']]
    turf=native.word(0x080ced28)
    for territory in (0,7,30):
        for inst in (m,native):
            for n in range(30):inst.put(turf+n*12+1,bytes([3 if n<territory else 0]))
        for town in range(2,7):
            for battles in (0,9,10,19,20,65535):
                for tab in range(6):
                    old_count=native.call(0x080cbdc0,dest,tab,battles,town)
                    old=native.read(dest,old_count*4)
                    for bits in range(8):
                        case=(territory,town,battles,tab,bits)
                        for bit,value in enumerate((774,780,786)):flag(value,bits&(1<<bit))
                        unlocked=(True,bool(bits&1) or battles>=10,bool(bits&2) or battles>=20,bool(bits&4))
                        wanted=[ident for ident,stage,shops in expected_rows if tab==2 and town in shops and unlocked[stage]]
                        m.put(dest,b'\xb7'*2000)
                        count=m.call(0x080cbdc0,dest,tab,battles,town)
                        check('native prefix exact',m.read(dest,len(old))==old)
                        check('exact unlocked teachers',count==old_count+len(wanted) and m.read(dest+len(old),len(wanted)*4)==b''.join(struct.pack('<HBB',i,0,0) for i in wanted))
                        check('tail guard',m.read(dest+count*4,32)==b'\xb7'*32)
        print('Stock matrix passed for territory count',territory,flush=True)
    discount=m.word(0x080cbc78);rank_address=m.word(0x080cbc7c)+m.word(0x080cbc80)
    for rank in (0,1,5):
        m.put(rank_address,bytes([rank]));clan=m.read(discount+rank*10+8,1)[0]
        for town in range(2,7):
            mask=m.word(m.call(0x080cccf0,town))
            for r in rows:
                case=('price',rank,town,r['id']);row=m.read(items+r['id']*32,32)
                check('buy/sell records',struct.unpack_from('<HH',row,4)==(r['price'],r['price']//2))
                favored=bool(mask&(1<<(row[8]-1)));reduction=clan+10*int(favored)
                wanted=max(r['price']//2,r['price']*(100-reduction)//100) if row[12]&8 else r['price']
                check('native checkout quote',m.call(0x080cbc14,town,r['id'])==max(1,wanted))
    # The native commit receives the quoted total after confirmation. Execute
    # that real block rather than replacing the inventory grant with a mock.
    state=0x02020000;w32(m,0x0200f428,state)
    selected=m.word(0x0806a948);quantity=m.word(0x0806a94c)+0x79
    for r in rows:
        for qty in (1,3):
            case=('purchase',r['id'],qty)
            m.put(0x02001940,bytes(512));quest=bytes((n*17+3)&255 for n in range(120));m.put(0x02002b08,quest)
            w16(m,state+selected,r['id']);m.put(state+quantity,bytes([qty]));w32(m,state+0x4500,r['price']*qty);w32(m,0x02001f64,100000)
            for reg,value in ((UC_ARM_REG_SP,STACK),(UC_ARM_REG_LR,RETURN|1),(UC_ARM_REG_R6,0x0200f428)):m.u.reg_write(reg,value)
            m.u.emu_start(0x0806a8c3,0x0806a900,count=100000)
            check('native commit returns',m.u.reg_read(UC_ARM_REG_PC)==0x0806a900)
            wanted=bytearray(512);wanted[r['id']]=qty
            check('correct inventory and charge',m.read(0x02001940,512)==wanted and m.word(0x02001f64)==100000-r['price']*qty)
            check('quest namespace preserved',m.read(0x02002b08,120)==quest)
except BaseException as error:
    failure=repr(error);raise
finally:
    report=dict(passed=failure is None,romSha1=meta['romSha1'],baselineSha1=PARENT_SHA1,checks=dict(checks),case=case,error=failure,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],romSha1=meta['romSha1'],checks=sum(checks.values()),report=str(out/'report.json'))),flush=True)
