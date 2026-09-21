"""Private palette/runtime experiment using the sixty approved movement poses.

Nonmovement sequences remain explicit placeholders in THIS ENGINEERING PILOT.
This is never the full-animation delivery, never installed, and never changes a
player save. The final importer must pass the separate full-art coverage gate.
"""
import importlib.util
import json
import runpy
import struct
from pathlib import Path
from PIL import Image
from native_art import ROOT, sha, pack_tiles


def module(name, file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def build():
    runpy.run_path(str(ROOT/'scripts/prepare-reviewed-palette-trial.py'),run_name='__main__')
    work=ROOT/'build/art/reviewed-integration/grouped-palette-inputs';work.mkdir(parents=True,exist_ok=True)
    palette_path=ROOT/'build/art/reviewed-integration/three-palette-trial.json';trial=json.loads(palette_path.read_text())
    art=json.loads((ROOT/'src/art/race-study/animation-generation-v1.json').read_text());overrides=[]
    for unit in art['units']:
        group=next(i for i,g in enumerate(trial['groups']) if unit['job'] in g)
        rgb=[(0,0,0)]+[tuple(c) for c in trial['palettesRGB'][group]]
        words=[sum(round(c[i]*31/255)<<(5*i) for i in range(3)) for c in rgb]
        raw=struct.pack('<16H',*words);folder=work/unit['slug'];folder.mkdir(exist_ok=True)
        (folder/'palette.bin').write_bytes(raw)
        inputs=[];frames=[];sheet=Image.new('RGBA',(96,64))
        for n,name in enumerate(['front-step-a','front-neutral','front-step-b','back-step-a','back-neutral','back-step-b']):
            path=ROOT/'build/art/approved-class-animation-2026-09-19'/unit['slug']/(name+'.png')
            im=Image.open(path).convert('RGBA');assert im.size==(32,32)
            inputs.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes())))
            sheet.alpha_composite(im,(n%3*32,n//3*32))
            def index(pixel):
                if pixel[3]<128:return 0
                color=sum(round(pixel[i]*31/255)<<(5*i) for i in range(3))
                return min(range(1,16),key=lambda k:sum((((color>>s)&31)-((words[k]>>s)&31))**2 for s in (0,5,10)))
            indexed=Image.new('P',(32,32));indexed.putpalette([v for color in rgb for v in color]+[0]*(768-48))
            indexed.putdata([index(p) for p in im.get_flattened_data()]);indexed.info['transparency']=0
            indexed.save(folder/f'frame-{n:02}.png',bits=4)
            frames.append(dict(tileSha256=sha(pack_tiles(indexed,16)),pose=name))
        source=folder/'approved-movement-source.png';sheet.save(source)
        proof=dict(source=str(source),sourceSha256=sha(source.read_bytes()),paletteSha256=sha(raw),frames=frames,
                   inputs=inputs,scope='Technical layout and 4bpp conversion of existing approved generated artwork; movement-only pilot')
        manifest=folder/'manifest.json';manifest.write_text(json.dumps(proof,indent=2)+'\n')
        overrides.append(dict(job=unit['job'],source=str(source.relative_to(ROOT)),sourceSha256=sha(source.read_bytes()),
                              conversionManifest=str(manifest.relative_to(ROOT)),conversionManifestSha256=sha(manifest.read_bytes())))
    override_path=work/'overrides.json';override_path.write_text(json.dumps(dict(schema=1,jobs=overrides),indent=2)+'\n')
    live=module('reviewed_group_live','build-live-art-palette.py')
    # The final engineering ROM authenticates this previously untouched tail.
    # Extend this private component's reservation only; defaults remain pinned.
    engineering=json.loads((ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json').read_text())
    original=Path(engineering['path']).read_bytes()
    assert original[0x1fd0000:0x2000000]==b'\xff'*0x30000
    live.END=0x2000000
    parent=live.build(history_slots=20,all_classes=True,workspace_low_address=True,provisional_history=True,fast_rotation=True,
        owned_menu_buffer=True,shared_battle_menu_heap=True,compact_us_keyboard=True,compact_battle_status=True,publish_current=False,
        fast_bank_scan=True,fast_oam_plan=True,arm_oam_scan=True,scoped_frame=True,native_oam_prefix=True,native_owner_producer=True,
        fused_compose=True,unrolled_copy=True,packed_plan=True,block_scan=True,burst_scan=True,fast_confirm=True,
        art_overrides=override_path,palette_groups=palette_path)
    connected=module('reviewed_group_connected','build-connected-art.py').build(Path(parent['path']).parent/'manifest.json',publish_current=False,build_only=True)
    final=module('reviewed_group_complete','complete-generated-actions.py').build(
        ROOT/'build/art/connected'/connected['romSha1']/'manifest.json',publish_current=False)
    final['reviewedArtPilot']=dict(productionAccepted=False,fullAnimationCoverage=False,
        scope=__doc__,sourceCatalog='src/art/race-study/full-animation-v1.json',groups=trial['groups'],
        reservationReview='Private live code/data extended through authenticated FF tail 1FD0000..2000000. Do not apply older native palette stage.',
        remaining='Full action art, palette runtime/performance proof, menu/portrait replacements, packaging, visible launch and screenshots')
    path=ROOT/'build/art/reviewed-integration/grouped-palette-pilot.json';path.write_text(json.dumps(final,indent=2)+'\n')
    print(json.dumps(dict(manifest=str(path),romSha1=final['romSha1'],productionAccepted=False)))


if __name__=='__main__':build()
