"""Connect the all-class palette candidate to existing imagegen asset imports.

Private technical candidate only. Explicit inputs keep historical component
indexes, the installed preview and player saves unchanged. No image creation.
"""
import datetime, hashlib, json
from pathlib import Path
from native_art import ROOT, sha
from generated_status_transport import build as status_build
from generated_equipment_transport import build as equipment_build
from generated_weapon_transport import build as weapon_build
from generated_effect_transport import build as effect_build

SOURCE = ROOT/'build/art/live-palette/all-classes-workspace-current.json'

def load(path):
    raw=Path(path).read_bytes();meta=json.loads(raw)
    assert hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==meta['romSha1']
    return meta

def manifest(meta):
    return Path(meta['path']).parent/'manifest.json'

def build(source=SOURCE, *, publish_current=True, fixture_source=None, build_only=False):
    live=load(source)
    fixture_source=Path(fixture_source or live.get('fixtureSource',live['releaseSource']))
    fixture_sha1=hashlib.sha1(fixture_source.read_bytes()).hexdigest()
    if not build_only:
        fixture_report=json.loads((fixture_source.parent/'fixture/report.json').read_text())
        assert fixture_report['passed'] and fixture_report['romSha1']==fixture_sha1
        assert (fixture_source.parent/'fixture/accepted-world.state').is_file()
    assert live['allClasses'] and live['historySlots']==20
    assert live['workspaceLowAddress'] and live['provisionalHistory'] and live['fastRotation']
    actions=load(Path(live['source']).parent/'manifest.json')
    portraits=load(Path(actions['source']).parent/'manifest.json')
    classes=load(Path(portraits['source']).parent/'manifest.json')
    resources=load(Path(classes['source']).parent/'manifest.json')
    root=ROOT/'build/art/connected'
    work=root/'rebuild'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    work.mkdir(parents=True)
    indexes=[ROOT/'build/art'/n/'current.json' for n in
             ('assembled','clean-chain','generated-status','generated-equipment','generated-weapon','generated-effect')]
    indexes += [SOURCE,ROOT/'build/art/live-palette/poc.json',ROOT/'build/expansion/probes/integrated-jobs/current.json']
    original_indexes={p:p.read_bytes() for p in indexes if p.exists() or not build_only}
    checks=[];components={}
    try:
        status=status_build(source,publish_current=False)
        equipment=equipment_build(manifest(status),publish_current=False)
        weapon=weapon_build(manifest(equipment),equipment_manifest=manifest(equipment),publish_current=False)
        effect=effect_build(manifest(weapon),publish_current=False)
        components=dict(classResources=resources,classes=classes,portraits=portraits,actions=actions,
                        preview=classes['preview'],livePalette=live,status=status,equipment=equipment,weapon=weapon,effect=effect)
        parent=live
        for child in (status,equipment,weapon,effect):
            assert child['baseRomSha1']==parent['romSha1'] and child['source']==parent['path']
            checks.append('Exact explicit parent '+child['romSha1']);parent=child
        rom=Path(effect['path']).read_bytes();old=Path(live['path']).read_bytes()
        lo,hi=live['reservation'];assert rom[lo:hi]==old[lo:hi]
        for patch in live['changes']:
            p,n=patch['offset'],patch['bytes'];assert rom[p:p+n]==old[p:p+n]
        checks.append('Complete live-palette module and every installed hook preserved')
        # The added held resource must reference the latest palette-aware
        # actor descriptors, not an earlier component's animation table.
        import struct
        table=struct.unpack_from('<I',old,0x2102c)[0]-0x08000000
        assert rom[weapon['table']:weapon['table']+276*4]==old[table:table+276*4]
        checks.append('All 276 latest actor/auxiliary references preserved in extended table')
        assert all(p.read_bytes()==raw for p,raw in original_indexes.items())
        checks.append('Historical component and installed/release indexes unchanged')
        data=dict(schema=3,path=effect['path'],romSha1=effect['romSha1'],romSha256=sha(rom),
            source=live['releaseSource'],baseRomSha1=hashlib.sha1(Path(live['releaseSource']).read_bytes()).hexdigest(),
            fixtureSource=str(fixture_source),fixtureRomSha1=fixture_sha1,components=components,
            sourcePaletteManifest=str(manifest(live)),sourcePaletteManifestSha256=sha(manifest(live).read_bytes()),
            status='Connected technical candidate; repeated-pose imagegen drafts; acceptance is recorded separately',
            scope='All ten custom actor palettes, generated class/menu/portrait transports, two status glyphs, all17 axe icons/projectiles, held axe276 and Tomahawk425 impact. Native runtime composition, remaining action/effect lifetimes, timing, final artwork and delivery remain separate.')
        if build_only:
            data.update(fixtureSource=None,fixtureRomSha1=None,buildOnly=True)
        folder=root/data['romSha1'];folder.mkdir(parents=True,exist_ok=True)
        for p in ((folder/'manifest.json',root/'current.json') if publish_current else (folder/'manifest.json',)):
            p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        # Existing live-palette tests accept this view without rewriting their
        # historical candidate index. The final ROM has identical live code.
        view=dict(live,path=data['path'],romSha1=data['romSha1'],connectedManifest=str(folder/'manifest.json'),
                  fixtureSource=str(fixture_source),fixtureRomSha1=fixture_sha1)
        if build_only:view.update(fixtureSource=None,fixtureRomSha1=None,buildOnly=True)
        (folder/'live-palette-view.json').write_text(json.dumps(view,indent=2)+'\n',encoding='utf-8')
        report=dict(status='passed',romSha1=data['romSha1'],checks=checks,manifest=str(folder/'manifest.json'),
                    scope='Explicit reproducible composition and preservation checks only; no runtime or final-art acceptance.')
        (work/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(status='passed',checks=len(checks),romSha1=data['romSha1'],report=str(work/'report.json'))))
        return data
    except Exception as error:
        (work/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8')
        print('Artifacts: '+str(work));raise

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=SOURCE)
    parser.add_argument('--fixture-source',type=Path)
    args=parser.parse_args();build(args.source,fixture_source=args.fixture_source)
