"""Static and native-harness checks for the item-icons stage.

Against the item-icons candidate and its memory-fixes parent:
- only the reservation and the equipment draw pointer changed; the container
  decodes (native 05318 format) to the approved pixels of every weapon;
- native calls at the six equipment draw callers and the shared shop (modes
  4, 5, 6) for every ID 0..460: the 85 weapons draw their own icon at the
  equipment callers and in shop mode 4, every other caller, mode and ID draws
  exactly what the parent drew (quest icons included), with ABI, stack and
  destination bounds checked by the harness;
- the generic icon API and the palette selector are unchanged for all IDs.
"""
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tools/arm-python'))
from PIL import Image
from native_art import pack_tiles
from native_miniatures import decode
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
tree=ast.parse((ROOT/'scripts/test-equipment-icons.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native icon ABI>','exec'))
meta=json.loads(Path(json.loads((ROOT/'build/expansion/item-icons/current.json').read_text())['manifest']).read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
stage=meta['itemIcons'];parent=Path(json.loads(Path(stage['parent']).read_text())['path']).read_bytes()
assert hashlib.sha1(parent).hexdigest()==stage['baseSha1']
receipt=json.loads((ROOT/'src/art/imagegen/new-item-icons-approved.json').read_text(encoding='utf-8'))
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

# 1. Declared bytes, hook and container.
allowed=set(range(*stage['used']))|set(range(stage['hook']['offset'],stage['hook']['offset']+4))
check(len(rom)==len(parent) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(parent,rom))),'only the reservation and the draw pointer differ')
check(rom[stage['used'][1]:stage['reservation'][1]]==b'\xff'*(stage['reservation'][1]-stage['used'][1]),'rest of the reservation still erased')
check(struct.unpack_from('<I',rom,0xcb984)[0]==stage['symbols']['ffta_item_icon_entry']|1,'equipment draw pointer -> item icon dispatcher')
approved={}
for row in receipt['items']:
    raw=(ROOT/row['path']).read_bytes();check(hashlib.sha256(raw).hexdigest()==row['sha256'],f"{row['id']} approved PNG unchanged")
    approved[row['id']]=pack_tiles(Image.open(ROOT/row['path']),4)
container=stage['symbols']['ffta_item_icon_container']-0x08000000
check(all(decode(rom,container,i-376)==approved[i] for i in range(376,461)),'container decodes to all 85 approved icons')

# 2. Native draw callers, shop modes, generic API and palette selector.
a,b=ARM(rom),ARM(parent)
SITES=(0x8168a,0x7031c,0x749e8,0x8e3f2,0x6e6a4,0xd6614)
owned=0
for site,mode in [(s,4) for s in SITES]+[(0x6796e,m) for m in (4,5,6)]:
    for ident in range(461):
        actual=a.icon(0x08000000+site,ident,True,block=True,mode=mode)
        mine=376<=ident<=460 and mode==4
        expected=approved[ident] if mine else b.icon(0x08000000+site,ident,True,block=True,mode=mode)
        assert actual==expected,(hex(site),mode,ident)
        owned+=mine
checks.append(f'{len(SITES)+3} draw contexts x 461 IDs: {owned} own-icon draws, all others identical to the parent')
count=int.from_bytes(parent[0x3c83fe:0x3c8400],'big')
for ident in range(count):
    assert a.icon(0x080cb980,ident,True)==b.icon(0x080cb980,ident,True),ident
checks.append(f'generic icon API unchanged for all {count} native icons')
for ident in range(461):assert a.icon(0x080cb99c,ident,False)==b.icon(0x080cb99c,ident,False),ident
checks.append('palette selector unchanged for IDs 0..460')

out=Path(meta['path']).parent/('item-icons-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=stage['baseSha1'],checks=checks)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),report=str(out/'report.json'))))
