"""Reproduce and describe the expanded temporary-art technical preview.

The eight-stage gameplay source build is authenticated and reused. All eight
art stages are rebuilt, with original generated images as pinned private inputs.
This does not regenerate images, accept final art, install a ROM or touch saves.
"""
import datetime,hashlib,json,runpy
from pathlib import Path
from native_art import ROOT,sha

def build():
    root=ROOT/'build/art/assembled';out=root/'rebuild'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);checks=[]
    before=json.loads((ROOT/'build/art/generated-effect/current.json').read_text())
    target=Path(before['path']).read_bytes();assert hashlib.sha1(target).hexdigest()==before['romSha1']
    try:
        chain=runpy.run_path(str(ROOT/'scripts/build-clean-art-chain.py'))['build']()
        from generated_weapon_transport import build as weapon_build
        from generated_effect_transport import build as effect_build
        weapon=weapon_build();effect=effect_build()
        assert weapon['baseRomSha1']==chain['romSha1'] and effect['baseRomSha1']==weapon['romSha1']
        checks.append('Eight rebuilt art stages retain authenticated parent chain')
        assert Path(effect['path']).read_bytes()==target
        checks.append('Complete assembled ROM exactly reproduces tested impact candidate')
        components=dict(chain['components']);components.update(weapon=weapon,effect=effect)
        data=dict(schema=2,path=effect['path'],romSha1=effect['romSha1'],romSha256=sha(target),
            source=effect['releaseSource'],baseRomSha1=hashlib.sha1(Path(effect['releaseSource']).read_bytes()).hexdigest(),
            components=components,sourceRebuild=chain['sourceRebuild'],
            status='technical candidate; temporary artwork; not final release',
            coverage=dict(
                equipmentPreview='Ten generated portrait crops and revised labels; Item List/Buy/Sell two-page eligibility grid.',
                battleActor='Ten classes, independent land/water resources; all770 present non-idle descriptor slots use temporary generated poses with native commands/timing. Named characters retain native identity.',
                menuFigure='Ten separate compressed job-wheel figures plus ten independent large portraits.',
                palettes='Actor and miniature conversion uses original consumer palettes. Large portraits have independent48-color palettes. Expanded actor palette allocation deferred to final sprite refinement.',
                weaponsEffectsStatus='All17 axe icons, independent held axe276, Tomahawk projectile and action425 primary impact, Exposed/Centered glyphs. Other weapon/effect families retain existing presentation.',
                limitations='Technical art only: repeated idle poses are not finished animation; water crops are not swimming art. Natural water-map traversal, every action/effect family, remaining repaired-data consumer classification and production-art acceptance are not established. No full campaign replay on this art candidate.'),
            rebuildReport=str(out/'report.json'))
        folder=root/data['romSha1'];folder.mkdir(parents=True,exist_ok=True)
        for p in (folder/'manifest.json',root/'current.json'):p.write_text(json.dumps(data,indent=2)+'\n')
        result=dict(status='passed',romSha1=data['romSha1'],checks=checks,
            manifest=str(folder/'manifest.json'),manifestSha256=sha((folder/'manifest.json').read_bytes()),
            sourceRebuild=chain['sourceRebuild'],
            scope='Rebuild all eight art stages from the authenticated corrected gameplay build and exact generated-image/conversion inputs. Complete byte equality to existing tested candidate; no deterministic regeneration, final-art or campaign acceptance.')
        (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(status='passed',checks=len(checks),romSha1=data['romSha1'],report=str(out/'report.json'))));return data
    except Exception as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise

if __name__=='__main__':build()
