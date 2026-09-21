"""Actual native constructor and negative guards for the retained hidden reset."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_hidden_constructor import observe
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007800
text=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(text).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native constructor>','exec'))
source=ROOT/'build/art/native-combo-participation/20260919T072442.986387Z'
meta=json.loads((ROOT/'build/art/native-palettes/current.json').read_text());rom=Path(meta['path']).read_bytes()
retained=json.loads((source/'failed.json').read_text());assert retained['romSha1']==meta['romSha1']==hashlib.sha1(rom).hexdigest()
ram=(source/'expanded-failed.ram').read_bytes();iw=(source/'expanded-failed.iwram').read_bytes();vram=(source/'expanded-failed.vram').read_bytes();oam=(source/'expanded-failed.oam').read_bytes()
last=retained['samples'][-1];old=next(x for x in last['rows'] if x['job']==117);a=old['actor'];body=a['address'];p=0x10000+a['tile']*32
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
anchor=dict(direct=True,frame=last['frame'],actor=a,identity=(a['resource'],a['tile'],a['allocation']),block=vram[p:p+a['allocation']*32])
assert sha(anchor['block'])==old['blockSha256'] and old['displayProof']=='current'
event=next(e for e in reversed(retained['events']) if e['site']=='native-composed');boundary=bytearray(iw)
for key,offset in [('main',0),('auxiliary',0x2c50)]:
    raw=bytes.fromhex(event['memory'][key]);boundary[offset:offset+len(raw)]=raw
out=ROOT/'build/art/native-hidden-constructor'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    check(observe(rom,ram,boundary,vram,oam,body,anchor,last['frame']+1,check) is not None,'Exact hidden reset accepted without claiming visible new pose')
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    check(rom[0x21618:0x216f8]==clean[0x21618:0x216f8],'Original constructor body and literals unchanged')
    before=bytearray(ram)
    for offset,value in ((0,a['flags']),(0x20,a['tileOffset']),(0x28,a['oam']),(0x2c,a['oam']),(0x34,a['first']),(0x38,a['current'])):struct.pack_into('<I',before,body+offset,value)
    for offset,value in ((8,a['mode']),(0xa,a['timer']),(0xc,a['index']),(0xe,word(rom,a['first']-0x08000004))):struct.pack_into('<H',before,body+offset,value)
    machine=ARM(rom,iw)
    for stack in (STACK,STACK+4):
        machine.put(0x02000000,before);machine.put(stack,struct.pack('<3I',a['resource'],half(ram,body+8),0))
        result=machine.call(0x08021618,word(before,body+0x40),0x02000000+body,0,a['allocation'],stack=stack)
        check(result==0x02000000+body and machine.read(0x02000000+body,72)==ram[body:body+72],'Actual original constructor reproduces complete captured72 bytes '+str(stack))
    for offset,value in ((0,0x45),(0xa,1),(0xc,1),(0xe,1),(0x20,0),(0x28,0),(0x2c,a['oam']),(0x38,0)):
        changed=bytearray(ram);struct.pack_into('<H' if offset in (0xa,0xc,0xe) else '<I',changed,body+offset,value)
        check(observe(rom,changed,boundary,vram,oam,body,anchor,last['frame']+1,check) is None,'Changed constructor field rejected '+str(offset))
    changed=bytearray(vram);changed[p]^=1
    check(observe(rom,ram,boundary,changed,oam,body,anchor,last['frame']+1,check) is None,'Changed retained pixels rejected')
    check(observe(rom,ram,boundary,vram,oam,body,anchor,last['frame']+5,check) is None,'Expired direct anchor rejected')
    altered=bytearray(oam);altered[0]^=1
    try:observe(rom,ram,boundary,vram,altered,body,anchor,last['frame']+1,lambda ok,label:(_ for _ in ()).throw(AssertionError(label)) if not ok else None)
    except AssertionError:check(True,'Changed hardware rejected by original producer proof')
    else:raise AssertionError('Changed OAM accepted')
    report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],source=str(source),scope=__doc__,
        pins={n:sha((source/n).read_bytes()) for n in ('failed.json','expanded-failed.ram','expanded-failed.iwram','expanded-failed.vram','expanded-failed.oam')})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');raise
