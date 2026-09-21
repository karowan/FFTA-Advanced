"""Retained native trail upload boundary and strict negative controls.

The previous captured command queues entry3 through opcode0 entry4. At57 its
five tiles finish uploading while entry5's seven tiles are newly queued. Native
update reproduction uses a controlled actor and available transfer queue, not
a whole-game rewind or reconstruction of the previous complete queue state.
"""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_queued_upload import completed
from actor_render_evidence import actors
index_path=ROOT/'notes/native-art-queued-trail-inputs.json';index=json.loads(index_path.read_text())
source=ROOT/index['source'];raw={name:(source/name).read_bytes() for name in index['sha256']}
assert all(sha(raw[name])==digest for name,digest in index['sha256'].items())
rom=raw['native-held-donor.gba'];prior=json.loads(raw['failed.json']);body=135432
assert hashlib.sha1(rom).hexdigest()==index['controlSha1']
r=raw['baseline-attack-57.ram'];v=raw['baseline-attack-57.vram']
old=next(a for a in prior['observations']['baseline']['attack-56']['heldWeapons'] if a['address']==body)
a=next(a for a in prior['observations']['baseline']['attack-57']['heldWeapons'] if a['address']==body)
p=0x10000+a['tile']*32;n=a['allocation']*32;block=v[p:p+n]
previous=dict(actor=old,identity=(a['resource'],a['tile'],a['allocation']),block=raw['baseline-attack-53.vram'][p:p+n])
out=ROOT/'build/art/queued-trail-upload'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
(out/'input-index.json').write_bytes(index_path.read_bytes())
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    check(old['index']==5 and a['index']==6 and old['tileCount']==5 and a['tileCount']==7,'Actual prior/current queued command records')
    check(old['displayProof']=='bounded pending upload from direct anchor','Previous frame retained the directly proven allocation')
    anchor=next(x for x in prior['observations']['baseline']['attack-53']['heldWeapons'] if x['address']==body)
    check(anchor['displayedFrames']==[1] and anchor['displayProof']=='current','Actual earlier direct upload anchor')
    result=completed(rom,a,block,previous,1,1);check(bool(result),'Exact queued upload plus complete retained allocation tail')
    check(not completed(rom,a,block,previous,2,1),'Reject stale previous observation')
    check(not completed(rom,a,block,previous,1,0),'Reject different native descriptor channel')
    for field,value in [('tileOffset',old['tileOffset']+32),('oam',old['oam']+4),('flags',old['flags']&~0x120000),('current',old['first']),('tileCount',old['tileCount']+1)]:
        damaged=dict(previous,actor=dict(old,**{field:value}))
        check(not completed(rom,a,block,damaged,1,1),'Reject altered previous '+field)
    for field,value in [('tileOffset',a['tileOffset']+32),('flags',a['flags']&~0x120000),('index',a['index']-1),('tile',a['tile']+1),('first',a['first']+20)]:
        check(not completed(rom,dict(a,**{field:value}),block,previous,1,1),'Reject altered current '+field)
    for offset in (0,159,160,n-1):
        damaged=bytearray(block);damaged[offset]^=1
        check(not completed(rom,a,damaged,previous,1,1),'Reject changed uploaded pixel or retained tail '+str(offset))
    image=bytearray(rom);image[old['first']-0x08000000+4*20+9]=9
    check(not completed(image,a,block,previous,1,1),'Reject unsupported intervening command')
    sys.path.insert(0,str(ROOT/'tools/arm-python'))
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
    from unicorn.arm_const import *
    UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
    code=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
    exec(compile(ast.Module(body=[x for x in ast.parse(code).body if isinstance(x,ast.ClassDef) and x.name=='ARM'],type_ignores=[]),'<native actor update>','exec'))
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    check(rom[0x210e4:0x21378]==clean[0x210e4:0x21378],'Original full dispatcher/update bytes')
    for residue in (0,4):
        m=ARM(rom,bytes(0x8000));m.put(0x02000000,r);addr=0x02000000+body
        for offset,fmt,value in [(0,'I',old['flags']),(10,'H',old['timer']),(12,'H',old['index']),
            (0x20,'I',old['tileOffset']),(0x24,'H',old['tileCount']),(0x28,'I',old['oam']),(0x2c,'I',old['oam']),(0x38,'I',old['current'])]:
            m.put(addr+offset,struct.pack('<'+fmt,value))
        # Graphics opcode1 needs an actual transfer context. The earlier
        # opcode0 proof could pass null because it queues no graphics. Native
        #21194 compares queue count+1CA with capacity+1CC; declare available
        #space in this isolated context rather than silently deferring it.
        transfer=0x02008000;m.put(transfer,bytes(0x200));m.put(transfer+0x1cc,struct.pack('<H',4))
        m.call(0x08021290,addr,transfer,stack=STACK+residue)
        observed=m.read(addr,72);expected=r[body:body+72]
        (out/('native-update-'+str(residue)+'.json')).write_text(json.dumps(dict(observed=observed.hex(),expected=expected.hex(),differences=[dict(offset=i,observed=x,expected=y) for i,(x,y) in enumerate(zip(observed,expected)) if x!=y]),indent=2)+'\n',encoding='utf-8')
        check(observed==expected,'Original update with available queue reproduces all72 actual actor bytes at stack residue '+str(residue))
        check(struct.unpack('<H',m.read(transfer+0x1ca,2))[0]==1,'Original native update enqueues exactly one transfer')
    report=dict(status='passed',checks=checks,romSha1=index['controlSha1'],inputIndexSha256=sha(index_path.read_bytes()),proof=result,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,error=str(error)),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
