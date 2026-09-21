"""Execute native manual phase selection and verify its exact uploaded frame."""
import ast,copy,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import actors
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
capture=ROOT/'build/art/explicit-walk/20260918T011701.829752Z'
assert sha((capture/'failed.json').read_bytes())=='dc733600278c96a9e9b05924e8b520a11e3b5683515132070ead34a1311d88b5'
prior=json.loads((capture/'failed.json').read_text());meta=json.loads((ROOT/'build/art/generated-actions/mapped-walk-current.json').read_text())
rom=Path(meta['comparisonSource']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['comparisonRomSha1']
ram=(capture/'parent-failed.ram').read_bytes();vram=(capture/'parent-failed.vram').read_bytes();iw=(capture/'parent-failed.iwram').read_bytes()
obs=prior['observations']['parent']['move-92'];old=prior['observations']['parent']['move-90'];p=obs['actor']['address'];a=ARM(rom,iw);a.put(0x02000000,ram)
initial=bytearray(ram[p:p+72]);struct.pack_into('<HH',initial,0xa,8,4);a.put(0x02000000+p,initial)
a.call(0x08021e28,0x02000000+p,3);actual=a.read(0x02000000+p,72)
expected=bytearray(initial);struct.pack_into('<HH',expected,0xa,0,3);struct.pack_into('<I',expected,0x38,struct.unpack_from('<I',initial,0x34)[0]+60)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
check(actual==expected==ram[p:p+72],'Native21E28 reproduces exact retained manual frame record')
def find(r,v):return next((x for x in actors(rom,r,v) if x['address']==p),None)
found=find(ram,vram);check(found is not None and found['displayedFrames']==[3] and found['declaredSequence'],'Exact selected native frame3 recognized')
start=0x10000+found['tile']*32;check(sha(vram[start:start+found['allocation']*32])==obs['blockSha256']==old['blockSha256'],'Full retained allocation equals preceding direct proof')
for offset,value,label in ((0,struct.pack('<I',found['flags']&~0x100),'missing manual flag'),(0xa,b'\x01\0','nonzero timer'),(0x38,struct.pack('<I',found['current']-20),'wrong current entry'),(0x20,struct.pack('<I',0),'wrong tile source'),(0x2c,bytes(4),'missing layout')):
    bad=bytearray(ram);bad[p+offset:p+offset+len(value)]=value;b=find(bad,vram)
    check(b is None or 3 not in b['displayedFrames'],'Reject '+label)
bad=bytearray(vram);bad[start]^=1;b=find(ram,bad);check(b is not None and not b['displayedFrames'],'Reject corrupt visible tile')
out=ROOT/'build/art/manual-animation-frame'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',romSha1=meta['comparisonRomSha1'],checks=checks,sourceReportSha256=sha((capture/'failed.json').read_bytes()),scope='Actual native21E28 phase setter reproduces retained record; uploaded frame recognized only for exact manual-control/index/current/timer/source/layout contract. No new full movement acceptance.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
