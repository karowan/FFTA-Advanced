"""All present action/water sequences: native mode selection and frame contracts."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,TILES,OAM,sha,layout
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/generated-actions/current.json').read_text())
rom=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseRomSha1']
iw=(Path(meta['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes()
a=ARM(rom,iw);b=ARM(base,iw);checks=[];modes=[]
out=ROOT/'build/art/generated-actions/native-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    check(rom[meta['table']:meta['table']+256*4]==base[meta['table']:meta['table']+256*4],'All unowned actor entries preserved')
    check(rom[meta['sizeTable']:meta['sizeTable']+276*2]==base[meta['sizeTable']:meta['sizeTable']+276*2],'All native allocation sizes preserved')
    for r in meta['resources']:
        n=r['id'];size=a.call(0x08021054,n);check(size==r['size']==16,str(n)+' original16-tile allocation')
        for mode in range(r['slots']*2):
            p=a.call(0x08021004,n,mode);q=b.call(0x08021004,n,mode)
            new=a.read(p,12);old=b.read(q,12)
            check(new[4:]==old[4:],f'{n}/{mode} exact descriptor metadata')
            check(bool(struct.unpack_from('<I',new)[0])==bool(struct.unpack_from('<I',old)[0]),f'{n}/{mode} null/present sequence preserved')
        if r['lifetime']=='land':check(rom[r['descriptors']:r['descriptors']+24]==base[r['sourceDescriptors']:r['sourceDescriptors']+24],str(n)+' accepted idle descriptors unchanged')
        for seq in r['sequences']:
            count=struct.unpack_from('<I',rom,seq['target'])[0]
            check(count==len(seq['frames'])==struct.unpack_from('<I',base,seq['source'])[0],f'{n}/{seq["slot"]} frame count')
            for f,frame in enumerate(seq['frames']):
                old=base[seq['source']+4+20*f:seq['source']+24+20*f];new=rom[seq['target']+4+20*f:seq['target']+24+20*f]
                check(old[8:]==new[8:],f'{n}/{seq["slot"]}/{f} command duration and all metadata intact')
                t,o=struct.unpack_from('<II',new);objects,_=layout(rom,OAM+o)
                check(len(objects)==1 and objects[0]['width']==objects[0]['height']==32 and objects[0]['tile']==0,f'{n}/{seq["slot"]}/{f} bounded16-tile OAM')
                check(TILES+t==frame['tile'] and OAM+o==frame['oam'] and sha(rom[TILES+t:TILES+t+512])==frame['sha256'],f'{n}/{seq["slot"]}/{f} exact generated frame payload')
                check(objects[0]['y']+frame['generatedBottom']==frame['nativeBottom'],f'{n}/{seq["slot"]}/{f} original opaque baseline')
    # Reuse authenticated retained menu RAM only as an isolated native allocator
    # context. The new widget owns a separate buffer; this is not a display test.
    candidates=[]
    for p in (ROOT/'build/art/class-resources/width-tests').glob('*/report.json'):
        v=json.loads(p.read_text())
        if v.get('status')=='passed':candidates.append((p,v))
    assert candidates
    proofpath,proof=sorted(candidates)[-1];capture=Path(proof['capture']);stem=capture/'private-slot2-wheel'
    ram=stem.with_suffix('.ram').read_bytes();menu_iw=stem.with_suffix('.iwram').read_bytes()
    check(sha(ram)==proof['sources']['private']['ramSha256'] and sha(menu_iw)==proof['sources']['private']['iwramSha256'],'Retained allocator context authenticated')
    for r in meta['resources']:
        a=ARM(rom,menu_iw);a.put(0x02000000,ram)
        for addr,size in ((0x04000000,0x10000),(0x05000000,0x1000),(0x06000000,0x20000),(0x07000000,0x1000),(0x10000000,0x2000)):a.u.mem_map(addr,size)
        widget=0x10000000;a.put(STACK,struct.pack('<6I',0,r['id'],0,1,1,0));a.call(0x08029864,widget,2,2,7)
        a.u.reg_write(UC_ARM_REG_R5,widget);a.u.reg_write(UC_ARM_REG_SP,STACK-0x34);a.u.emu_start(0x080299a7,0x08029a0a,count=50000)
        check(a.u.reg_read(UC_ARM_REG_PC)==0x08029a0a,str(r['id'])+' real native widget actor created')
        for slot in range(r['slots']):
            pointer=struct.unpack_from('<I',rom,r['descriptors']+12*slot)[0]
            if not pointer:continue
            for direction in ((1,2) if slot%2 else (0,3)):
                mode=(slot//2)*4+direction;modes.append([r['id'],mode]);a.call(0x08029cd8,widget,mode,0)
                actor=a.word(widget+0x7c)
                check(struct.unpack('<HH',a.read(actor+6,4))==(r['id'],mode),f'{r["id"]}/{mode} actual actor identity/mode')
                check(a.word(actor+0x34)==pointer+4,f'{r["id"]}/{mode} actual actor uses owned sequence')
    from generated_action_transport import build
    rebuilt=build();check(rebuilt['romSha1']==meta['romSha1'] and Path(rebuilt['path']).read_bytes()==rom,'Exact all-action transport rebuild')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,modes=modes,allocatorContext=str(proofpath),allocatorContextSha256=sha(proofpath.read_bytes()),
        scope='All20 owned resource modes/nulls,770 replaced descriptor slots, exact frame command/timing/metadata, tile/OAM/baseline contracts, real native widget actor recreation for every present mode/facing and exact rebuild. Repeated draft poses and water crops; no full action/water visual playback, custom palette or final-art acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,modes=modes),indent=2)+'\n');print('Artifacts: '+str(out));raise
