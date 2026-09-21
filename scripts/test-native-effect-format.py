"""Original impact extraction, native unpack and captured DMA byte equality."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_effect_art import SOURCE,LAYOUT,PALETTE,export,literal_lz
from ffta_maps import lz77
out=ROOT/'build/art/native-effect-format'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();check(hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9','Clean reference identity')
    m=json.loads((ROOT/'build/art/generated-weapon/current.json').read_text());rom=Path(m['path']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==m['romSha1'],'Current candidate identity')
    ref=export(clean,out/'original-reference');pixels=ref['pixels'];packed=ref['packed']
    for lo,hi,label in ((SOURCE,packed.end,'compressed source'),(LAYOUT,LAYOUT+112,'OAM and frame script'),(PALETTE,PALETTE+44,'all seven palettes')):
        check(clean[lo:hi]==rom[lo:hi],label+' exact in current candidate')
    blob=bytes.fromhex('0402fd7f')+literal_lz(pixels)
    check(lz77(blob,4).data==pixels,'Lossless4bpp container re-encoding')
    (out/'original-reencoded.bin').write_bytes(blob)
    sys.path.insert(0,str(ROOT/'tools/arm-python'))
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
    from unicorn.arm_const import *
    UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
    tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native effect unpack>','exec'))
    iw=(Path(m['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes();arm=ARM(rom,iw)
    source,dest=0x02022000,0x02024020
    for stack in (0x03007000,0x03006ffc):
        arm.put(source,packed.data);arm.put(dest-32,b'\xa5'*(len(pixels)+65))
        arm.call(0x080d6f64,source,len(packed.data),dest,stack=stack)
        check(arm.read(dest,len(pixels))==pixels,f'{stack:x} actual native2bpp-to4bpp unpack')
        # NativeD6F94 clears the next byte after each group. Its staging
        # scratch has slack; explicitly measure the one-byte terminal zero.
        check(arm.read(dest+len(pixels),1)==b'\0',f'{stack:x} native documented terminal staging zero')
        check(arm.read(dest-32,32)==b'\xa5'*32 and arm.read(dest+len(pixels)+1,32)==b'\xa5'*32,f'{stack:x} bounded native writes including staging slack')
    prior=ROOT/'build/art/generated-projectile/20260917T233435.237211Z/report.json'
    proof=json.loads(prior.read_text());check(proof['status']=='passed' and proof['romSha1']==m['romSha1'],'Accepted actual current-candidate projectile capture')
    for case in ('baseline','generated'):
        for sample in proof['observations'][case][:4]:
            p=prior.parent/f'{case}-projectile-{sample["frame"]}'
            vram=p.with_suffix('.vram').read_bytes();pal=p.with_suffix('.palette').read_bytes()
            check(vram[0x17c80:0x17fe0]==pixels,f'{case}/{sample["frame"]} original impact actual DMA equals clean extraction')
            check(pal[704:736].hex() in [v['raw'] for v in ref['palettes']],f'{case}/{sample["frame"]} actual bank6 equals native palette phase')
    report=dict(status='passed',romSha1=m['romSha1'],checks=checks,source=SOURCE,layout=LAYOUT,palette=PALETTE,
        sourceEnd=packed.end,pixelsSha256=sha(pixels),encodedSha256=sha(blob),frames=ref['frames'],palettes=ref['palettes'],
        retained=dict(report=str(prior),sha256=sha(prior.read_bytes())),
        scope='Clean Throw primary impact27tiles/three24x24 OAM frames plus blank frame/seven palette phases, lossless4bpp container encoding, actual native2bpp expansion and retained current-candidate DMA/palette identity. No custom effect dispatcher/import or onscreen impact-frame acceptance yet. Other effect resources separate.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
