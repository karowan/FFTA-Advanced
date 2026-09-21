"""Construct every reviewed native land/water mode through the actual widget API.

Detached ARM execution uses authenticated own-ROM battle RAM as an allocator
context. No actor modes are injected into a live battle. This checks real native
construction and mode transitions; gameplay-triggered playback is separate.
"""
import argparse,ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native widget ARM>','exec'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest',type=Path,default=ROOT/'build/art/reviewed-integration/action-candidate.json')
    parser.add_argument('--entry-index',type=Path,default=ROOT/'build/art/reviewed-integration/action-entry-latest.json')
    args=parser.parse_args();meta=json.loads(args.manifest.read_text())
    rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
    index=json.loads(args.entry_index.read_text())
    entry_path=ROOT/index['report'];assert sha(entry_path.read_bytes())==index['sha256']
    entry=json.loads(entry_path.read_text());assert entry['status']=='passed' and entry['romSha1']==meta['romSha1']
    source=entry_path.parent;ram=(source/'ready.ram').read_bytes();iw=(source/'ready.iwram').read_bytes()
    out=ROOT/'build/art/reviewed-integration/mode-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    checks=[];modes=[];failure=None
    def check(ok,label):
        assert ok,label
        checks.append(label)
    try:
        for resource in meta['components']['reviewedActions']['resources']:
            a=ARM(rom,iw);a.put(0x02000000,ram)
            for address,size in ((0x04000000,0x10000),(0x05000000,0x1000),(0x06000000,0x20000),(0x07000000,0x1000),(0x10000000,0x2000)):a.u.mem_map(address,size)
            widget=0x10000000;rid=resource['id']
            a.put(STACK,struct.pack('<6I',0,rid,0,1,1,0));a.call(0x08029864,widget,2,2,7)
            a.u.reg_write(UC_ARM_REG_R5,widget);a.u.reg_write(UC_ARM_REG_SP,STACK-0x34)
            a.u.emu_start(0x080299a7,0x08029a0a,count=100000)
            check(a.u.reg_read(UC_ARM_REG_PC)==0x08029a0a,str(rid)+' native widget construction returns')
            unitbytes=a.read(0x02000080,0x1df0)
            for sequence in resource['sequences']:
                slot=sequence['slot'];pointer=struct.unpack_from('<I',rom,resource['descriptors']+slot*12)[0]
                check(pointer==sequence['target']+0x08000000,'Reviewed sequence descriptor '+str((rid,slot)))
                for direction in ((1,2) if slot%2 else (0,3)):
                    mode=(slot//2)*4+direction;a.call(0x08029cd8,widget,mode,0)
                    actor=a.word(widget+0x7c)
                    check(widget+0x84<=actor<=widget+0x1080-72,'Native widget-private actor allocation '+str((rid,mode)))
                    check(a.read(actor+6,4)==struct.pack('<HH',rid,mode),'Actual native resource/mode '+str((rid,mode)))
                    check(a.word(actor+0x34)==pointer+4,'Actual native reviewed sequence '+str((rid,mode)))
                    check(a.read(0x02000080,0x1df0)==unitbytes,'No canonical roster/AP/item mutation '+str((rid,mode)))
                    modes.append([rid,mode])
    except BaseException as error:failure=repr(error)
    report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],checks=checks,modes=modes,failure=failure,
        source=dict(report=str(entry_path),reportSha256=sha(entry_path.read_bytes()),ramSha256=sha(ram),iwramSha256=sha(iw)),scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(checks),modes=len(modes),failure=failure,report=str(out/'report.json'))))
    assert failure is None,failure


if __name__=='__main__':main()
