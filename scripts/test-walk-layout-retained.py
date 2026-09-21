"""Strict reset-lifetime checks against retained native pixels and hardware OAM."""
import copy,datetime,hashlib,json,struct
from pathlib import Path
from native_art import ROOT,sha
from native_body_display import layout_reset_display
root=ROOT/'build/art/walk-layout-transition/20260918T010747.527654Z'
prior=ROOT/'build/art/explicit-walk/20260918T010505.036658Z/failed.json';payload=prior.read_bytes()
assert sha(payload)=='4b887de402736ec935d363ec70987152e370e72ed2f347b43e8d2db3f44eb8ef'
obs=json.loads(payload)['observations']['parent']['move-166'];a=obs['actor'];address=a['address']
meta=json.loads((ROOT/'build/art/generated-actions/mapped-walk-current.json').read_text());rom=Path(meta['comparisonSource']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['comparisonRomSha1']
ram=(root/'frame-00.ram').read_bytes();vram=(root/'frame-00.vram').read_bytes();oam=(root/'frame-00.oam').read_bytes()
p=0x10000+a['tile']*32;block=vram[p:p+a['allocation']*32]
assert sha(block)==obs['blockSha256']
hardware=[struct.unpack_from('<3H',oam,i*8) for i in range(128) if struct.unpack_from('<H',oam,i*8)[0]&0x300!=0x200 and struct.unpack_from('<H',oam,i*8+4)[0]&1023==a['tile']]
anchor=dict(direct=True,actor=a,identity=(a['resource'],a['tile'],a['allocation']),block=block,hardware=hardware)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
for frame in (0,1):
    r=(root/f'frame-{frame:02}.ram').read_bytes();v=(root/f'frame-{frame:02}.vram').read_bytes();h=(root/f'frame-{frame:02}.oam').read_bytes()
    result=layout_reset_display(rom,r,v,h,address,anchor,frame+2)
    check(result is not None and not result['configured'] and not result['displayedFrames'],'Retained reset frame '+str(frame)+' has exact prior pixels and active hardware owner')
check(layout_reset_display(rom,(root/'frame-02.ram').read_bytes(),vram,oam,address,anchor,4) is None,'Normal configured state is not called a reset')
constructor=bytearray(ram);struct.pack_into('<I',constructor,address,0x167);struct.pack_into('<H',constructor,address+0xc,0);struct.pack_into('<I',constructor,address+0x38,a['first'])
check(layout_reset_display(rom,constructor,vram,oam,address,anchor,2) is not None,'Native constructor variant at index0 with exact retained display')
bad=bytearray(ram);struct.pack_into('<I',bad,address,0x167)
check(layout_reset_display(rom,bad,vram,oam,address,anchor,2) is None,'Reject constructor flag on later animation entry')
for age in (-1,0,5,16):check(layout_reset_display(rom,ram,vram,oam,address,anchor,age) is None,'Reject stale/reset age '+str(age))
for off,data,label in ((0,struct.pack('<I',0x47),'flags'),(0xa,b'\x01\0','timer'),(0x12,b'\0\0','tile'),(0x20,bytes(4),'tile sentinel'),(0x28,bytes(4),'queued layout'),(0x2c,struct.pack('<I',a['oam']),'live layout'),(0x34,bytes(4),'sequence')):
    bad=bytearray(ram);bad[address+off:address+off+len(data)]=data
    check(layout_reset_display(rom,bad,vram,oam,address,anchor,2) is None,'Reject altered '+label)
bad=bytearray(vram);bad[p]^=1
check(layout_reset_display(rom,ram,bad,oam,address,anchor,2) is None,'Reject changed retained pixels')
check(layout_reset_display(rom,ram,vram,bytes(len(oam)),address,anchor,2) is None,'Reject missing hardware owner')
check(layout_reset_display(rom,ram,vram,oam,address,dict(anchor,direct=False),2) is None,'Reject inferred anchor')
out=ROOT/'build/art/walk-layout-retained'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',romSha1=meta['comparisonRomSha1'],checks=checks,sourceReportSha256=sha(payload),scope='Exact native two-frame layout reset signature, original full allocation hash and active hardware OAM; identity/sentinel/age/pixel controls. Original failed full walk still requires corrected playback.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
