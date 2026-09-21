"""Native wide-ID actor queries and relocated sequence/tile/OAM fidelity."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,ANIM,SIZES,TILES,OAM,layout,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
all_classes='--all-classes' in sys.argv
folder='build/art/class-resources' if all_classes else 'build/art/actor-import'
meta=json.loads((ROOT/folder/'current.json').read_text())
data=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
assert hashlib.sha1(data).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseRomSha1']
iw=(Path(meta['source']).parent/'fixture/battle-ready.iwram').read_bytes()
original,changed=ARM(base,iw),ARM(data,iw)
out=ROOT/folder/'tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False);checks=[]
def check(ok,name):
    assert ok,name
    checks.append(name)
try:
    check(data[meta['table']:meta['table']+248*4]==base[ANIM:ANIM+248*4],'All original animation table entries preserved')
    check(data[meta['sizeTable']:meta['sizeTable']+248*2]==base[SIZES:SIZES+248*2],'All original allocation sizes preserved')
    check(data[meta['partyTable']:meta['partyTable']+512]==base[0x393f0c:0x393f0c+512],'All pre-existing miniature mapping bytes preserved')
    for job in range(2,126):
        for selector in (4,5,6,7,9,10,11):
            # Alias records (for example job80) require a real fallback class;
            # passing the alias as its own fallback loops in the unmodified ROM.
            old=original.call(0x080c8570,job,2,selector)
            value=changed.call(0x080c8570,job,2,selector)
            owned=(116<=job<=125) if all_classes else job==116
            expected=256+(job-116)*2+(selector-4) if owned and selector in (4,5) else old
            check(value==expected,f'job{job}/selector{selector} only owned land/water reassigned; palette/portrait preserved')
    for resource in meta['resources']:
        old_id,new_id=resource['originalID'],resource['id']
        check(data[meta['partyTable']+2*new_id:meta['partyTable']+2*new_id+2]==base[0x393f0c+2*old_id:0x393f0c+2*old_id+2],'Separate miniature mapping '+str(new_id))
        check(changed.call(0x08021054,new_id)==original.call(0x08021054,old_id),'Wide-ID allocation size '+str(new_id))
        for mode in range(resource['slots']*2):
            old=original.call(0x08021004,old_id,mode)
            new=changed.call(0x08021004,new_id,mode)
            check(meta['used'][0]+0x08000000<=new<meta['used'][1]+0x08000000,f'{new_id}/{mode} relocated descriptor ownership')
            a=original.read(old,12);b=changed.read(new,12)
            check(a[4:]==b[4:],f'{new_id}/{mode} descriptor metadata')
            sa,sb=struct.unpack_from('<I',a)[0],struct.unpack_from('<I',b)[0]
            check(bool(sa)==bool(sb),f'{new_id}/{mode} empty/present sequence')
        for sequence in resource['sequences']:
            a,b=sequence['sourceSequence'],sequence['sequence']
            count=struct.unpack_from('<I',base,a)[0]
            check(struct.unpack_from('<I',data,b)[0]==count,f'{new_id}/{sequence["slot"]} frame count')
            for f in range(count):
                old=base[a+4+20*f:a+24+20*f];new=data[b+4+20*f:b+24+20*f]
                check(old[8:]==new[8:],f'{new_id}/{sequence["slot"]}/{f} duration command and five metadata words')
                ot,oo=struct.unpack_from('<II',old);nt,no=struct.unpack_from('<II',new)
                objects,raw=layout(base,OAM+oo);new_objects,new_raw=layout(data,OAM+no)
                check(objects==new_objects and raw==new_raw,f'{new_id}/{sequence["slot"]}/{f} exact OAM/flip/layout')
                size=max(x['tile']+x['width']*x['height']//64 for x in objects)*32
                check(base[TILES+ot:TILES+ot+size]==data[TILES+nt:TILES+nt+size],f'{new_id}/{sequence["slot"]}/{f} exact visible and hidden tiles')
                check(TILES+nt>=meta['used'][0] and OAM+no>=meta['used'][0],f'{new_id}/{sequence["slot"]}/{f} private tile/OAM ownership')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,
                coverage='Unchanged land/water actor relocation, wide resource IDs, native queries, complete metadata/tile/OAM preservation. No generated artwork, real water playback or palette allocation acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),romSha1=meta['romSha1'],checks=checks),indent=2)+'\n');raise
