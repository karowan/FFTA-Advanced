"""Static contract for the inert Physician/Sapper data stage, not gameplay acceptance."""
import hashlib
import json
import pathlib
import struct

ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'build/expansion/chemist-progressions/data-only/manifest.json'
meta=json.loads(MANIFEST.read_text(encoding='utf-8'))
base=pathlib.Path(meta['input']).read_bytes()
rom=pathlib.Path(meta['target']).read_bytes()
design=json.loads((ROOT/meta['design']).read_text(encoding='utf-8'))
equipment=json.loads((ROOT/meta['equipment']).read_text(encoding='utf-8'))
assert hashlib.sha1(base).hexdigest()==meta['inputSha1']
assert hashlib.sha1(rom).hexdigest()==meta['targetSha1']
assert len(base)==len(rom)==0x2000000
assert meta['status'].startswith('INERT DATA STAGE')

allowed=bytearray(len(rom))
start,end=meta['reservation']
assert 0x1a00000<=start<end<=0x1a10000
allowed[start:end]=bytes([1])*(end-start)
assert base[start:end]==bytes([255])*(end-start)
for group,sites in meta['pointerSites'].items():
    new=meta['addresses'][group]
    for site in sites:
        assert site%4==0 and 0<=site<0x1000000
        assert struct.unpack_from('<I',rom,site)[0]==new
        assert struct.unpack_from('<I',base,site)[0]!=new
        allowed[site:site+4]=b'\1\1\1\1'
assert not any(a!=b and not allowed[i] for i,(a,b) in enumerate(zip(base,rom)))
ptr=lambda at:struct.unpack_from('<I',rom,at)[0]-0x08000000
jobs=ptr(0xc8598)
races=ptr(0x257e8)
requirements=ptr(0xc8b18)
items=meta['addresses']['items']-0x08000000
teaching=meta['addresses']['teaching']-0x08000000
names=meta['addresses']['jobNames']-0x08000000
assert len(design['jobs'])==2 and len(equipment['items'])==10
observed=set()
for n,job in enumerate(design['jobs']):
    record=rom[jobs+job['id']*52:jobs+(job['id']+1)*52]
    assert job['id']==126+n and record[4]==job['race'] and record[5]==0
    assert struct.unpack_from('<H',record)[0]==848+n
    assert record[0x10]==job['id'] and record[0x28:0x2a]==bytes((job['move'],job['jump']))
    assert record[0x2d]==47+n and record[0x30]==30+n
    assert rom[requirements+(30+n)*4:requirements+(31+n)*4]==bytes(sum(job['prerequisites'],[]))
    first=record[0x2e]
    assert (first,record[0x2f])==((124,133) if n==0 else (116,125))
    bank=ptr(races+job['race']*4)
    for i,(_,display,kind,ability,ap) in enumerate(job['lessons']):
        row=bank+(first+i)*8
        assert struct.unpack_from('<H',rom,row)[0]==896+n*10+i
        assert struct.unpack_from('<H',rom,row+2)[0]==0 # Help/effect stage still pending.
        assert struct.unpack_from('<H',rom,row+4)[0]==ability
        assert rom[row+6]=={'Action':1,'Reaction':2,'Support':3,'Combo':5}[kind]
        assert rom[row+7]==ap//10 and len(display)<=11
        assert struct.unpack_from('<I',rom,names+(848+n)*4)[0]>=0x08000000
for i,item in enumerate(equipment['items']):
    assert item['id']==461+i and item['job'] in (126,127)
    row=items+item['id']*32
    assert struct.unpack_from('<H',rom,row)[0]==850+i
    assert struct.unpack_from('<H',rom,row+2)[0]==0 # Not shop-ready without help.
    assert struct.unpack_from('<H',rom,row+4)[0]==item['price']
    assert rom[row+8]==item['type'] and rom[row+16]==item['attack'] and rom[row+18]==item['power']
    assert struct.unpack_from('<H',rom,row+29)[0]==310+i
    setrow=teaching+(310+i)*20
    assert rom[setrow]==2
    job=next(x for x in design['jobs'] if x['id']==item['job'])
    first=124 if job['race']==3 else 116
    for k,lesson in enumerate(item['lessons']):
        assert rom[setrow+2+2*k]==item['job']
        assert rom[setrow+3+2*k]==first+lesson
        observed.add((item['job'],lesson))
assert observed=={(job['id'],lesson) for job in design['jobs'] for lesson in range(10)}
print('PASS: inert Physician/Sapper data allocation, pointer delta, and complete teaching map')
