"""Retained native queued upload at a bounded layout-reset boundary."""
import datetime,hashlib,json,struct
from native_art import ROOT,TILES,sha
from native_body_display import layout_reset_display

source=ROOT/'build/art/live-palette/battle/20260918T051043.520776Z'
payload=(source/'failed.json').read_bytes()
assert sha(payload)=='0477b06a9d28b11fa0f833170ee050c471651300fa874a44ca3d81176c94c23b'
report=json.loads(payload)
rom=(ROOT/'build/art/live-palette/fb62e2e0d3abc69c28b75210682ac5fefcb0e1b0/FFTA_Live_Palette_POC.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==report['romSha1']=='fb62e2e0d3abc69c28b75210682ac5fefcb0e1b0'
ram=(source/'candidate-failed.ram').read_bytes();vram=(source/'candidate-failed.vram').read_bytes()
assert sha(ram)=='3d78a83065497dc4e1b09a6469749d48363928dddaec90d23878cefbffe76904'
assert sha(vram)=='ce3efc9da868cc047a66a66d6f354f68d7ee5e9a612ab95377776d52f6d71b70'
old=report['observations']['candidate']['move-180'];a=old['actor'];address=a['address']
assert old['displayProof']=='current' and a['declaredSequence'] and a['displayedFrames']==[2]
tile=struct.unpack_from('<I',rom,a['first']-0x08000000+20*2)[0]
block=rom[TILES+tile:TILES+tile+a['allocation']*32]
assert sha(block)==old['blockSha256']
prior=bytes.fromhex(report['paletteTraces']['candidate']['move-180']['oam'])
hardware=bytes.fromhex(report['paletteTraces']['candidate']['move-181']['oam'])
objects=[struct.unpack_from('<3H',prior,i*8) for i in range(128)]
anchor=dict(direct=True,actor=a,identity=(a['resource'],a['tile'],a['allocation']),block=block,
            hardware=[x for x in objects if x[0]&0x300!=0x200 and x[2]&1023==a['tile']])
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
out=ROOT/'build/art/layout-queued-commit'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
try:
    result=layout_reset_display(rom,ram,vram,hardware,address,anchor,1)
    check(result is not None and result['displayProof']=='exact previously queued native frame commits during bounded layout reset','Exact actual pending frame commits with unchanged native geometry')
    for age in (0,5):check(layout_reset_display(rom,ram,vram,hardware,address,anchor,age) is None,'Reject age '+str(age))
    for changes,label in [(dict(flags=a['flags']&~0x120000),'no queued transfer'),(dict(current=a['current']-20),'different prior command')]:
        check(layout_reset_display(rom,ram,vram,hardware,address,dict(anchor,actor=dict(a,**changes)),1) is None,'Reject '+label)
    changed=bytearray(vram);changed[0x10000+a['tile']*32]^=1
    check(layout_reset_display(rom,ram,changed,hardware,address,anchor,1) is None,'Reject a single changed output pixel')
    changed=bytearray(hardware);owned=next(i for i,x in enumerate(objects) if x[0]&0x300!=0x200 and x[2]&1023==a['tile']);changed[owned*8]^=1
    check(layout_reset_display(rom,ram,vram,changed,address,anchor,1) is None,'Reject changed hardware geometry')
    check(layout_reset_display(rom,ram,vram,hardware,address,dict(anchor,direct=False),1) is None,'Reject inferred anchor')
    (out/'report.json').write_text(json.dumps(dict(status='passed',checks=checks,sourceReportSha256=sha(payload),romSha1=report['romSha1'],scope='Authenticated retained one-frame native queued command, exact full allocation and hardware geometry; age, pending-command, pixel, geometry and direct-anchor rejection controls. No new gameplay acceptance.'),indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');raise
