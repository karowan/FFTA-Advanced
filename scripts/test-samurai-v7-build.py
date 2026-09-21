"""Build a private six-pose Samurai refinement without changing delivery indexes."""
import argparse, datetime, hashlib, importlib.util, json, struct
from pathlib import Path
from native_art import ROOT, sha

def module(name, file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--support-actions',action='store_true')
args=parser.parse_args()
label='samurai-support-v1' if args.support_actions else 'samurai-v7'
current=json.loads((ROOT/'build/art/connected/current.json').read_text(encoding='utf-8'))
live=current['components']['livePalette']
out=ROOT/'build/art/refinement'/label/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
protected=[ROOT/'build/art/connected/current.json',ROOT/'build/art/pipeline/delivery/current.json',
           ROOT/'build/art/live-palette/status-current.json',Path(current['sourcePaletteManifest'])]
before={p:p.read_bytes() for p in protected};checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    builder=module('samurai_palette','build-live-art-palette.py')
    builder.PARENT=Path(live['source']).parent/'manifest.json'
    flags=dict(history_slots=20,all_classes=True,workspace_low_address=True,provisional_history=True,
               fast_rotation=True,owned_menu_buffer=True,shared_battle_menu_heap=True,
               compact_us_keyboard=True,compact_battle_status=True,publish_current=False)
    if args.support_actions:
        # Reuse passing v7/default preservation evidence. Only the action-map
        # branch changed; rebuilding unrelated defaults adds no new coverage.
        full=json.loads((ROOT/'build/art/generated-effect/d80e763169223d98284b180a39fa047f650d50e5/samurai-v7-preview.json').read_text(encoding='utf-8'))
        baseline=full['components']['livePalette']
        check(hashlib.sha1(Path(baseline['path']).read_bytes()).hexdigest()==baseline['romSha1'],'Authenticated passing v7 palette baseline')
    else:
        baseline=builder.build(**flags)
        check(baseline['romSha1']==live['romSha1'],'Default no-override build preserves exact installed palette ROM')
        Path(current['sourcePaletteManifest']).write_bytes(before[Path(current['sourcePaletteManifest'])])
    revised=builder.build(**flags,art_overrides=ROOT/'src/art/imagegen'/(label+'-preview.json'))
    check(revised['romSha1']!=baseline['romSha1'],'Explicit artwork input changes candidate')
    check(revised['symbols']==baseline['symbols'],'No engine entry or data symbol relocation')
    a=Path(baseline['path']).read_bytes();b=Path(revised['path']).read_bytes()
    start=live['reservation'][0];codebytes=baseline['segments'][0]['bytes']
    colors=live['symbols']['ffta_art_custom_colors']-0x08000000
    check(a[start:colors]==b[start:colors] and a[colors+32:start+codebytes]==b[colors+32:start+codebytes],
          'Compiled engine differs only in Samurai 32-byte palette')
    if args.support_actions:check(a[start:start+codebytes]==b[start:start+codebytes],'Full compiled engine and every class palette byte-exact')
    old={(x['resource'],x['slot']):x for x in baseline['assignments']}
    pose_hashes=set();explicit_keys=set()
    for row in revised['assignments']:
        prior=old[(row['resource'],row['slot'])]
        check(len(row['frames'])==len(prior['frames']),'Native frame count '+str((row['resource'],row['slot'])))
        for i,(new,previous) in enumerate(zip(row['frames'],prior['frames'])):
            p=row['sequence']+4+20*i;q=prior['sequence']+4+20*i
            check(a[q+8:q+20]==b[p+8:p+20],'Native commands/timing remain exact '+str((row['resource'],row['slot'],i)))
            if row['resource'] not in (256,257):
                check(new['tileSha256']==previous['tileSha256'],'Other class pixels preserved '+str((row['resource'],row['slot'],i)))
            elif row['resource']==256 and row['slot']<4:
                check(new['phase']==(0,1,2,1)[i%4]+(3 if row['slot']%2 else 0),'Explicit Samurai alternating gait')
                pose_hashes.add(new['tileSha256'])
            if args.support_actions:
                if 'explicitAction' not in new:
                    check(new['tileSha256']==previous['tileSha256'] and new['y']==previous['y'],'Unmapped pixels/alignment preserved '+str((row['resource'],row['slot'],i)))
                else:
                    explicit_keys.add(new['explicitAction']['nativePose'])
                    check(row['resource']==256,'Only Samurai land receives support assignments')
                    ref=new['explicitAction'];plan=json.loads((ROOT/'src/art/imagegen/samurai-support-v1-plan.json').read_text(encoding='utf-8'))
                    manifest=ROOT/plan['assets'][ref['asset']]['conversionManifest']
                    check(sha((manifest.parent/f'frame-{ref["frame"]:02}.4bpp').read_bytes())==new['tileSha256'],'Exact declared support pixels '+str((row['slot'],i)))
    check(len(pose_hashes)==6,'All six distinct Samurai land poses assigned')
    if args.support_actions:
        check(len(explicit_keys)==10,'Eight support poses and two v7 neutral poses mapped')
        check(revised['actionPlans'][0]['productionAccepted'] is False,'Partial native-pose coverage does not accept art')
    connected=module('samurai_connected','build-connected-art.py').build(
        Path(revised['path']).parent/'manifest.json',publish_current=False,fixture_source=current['fixtureSource'])
    if args.support_actions:check(connected['romSha1']=='5fe7c35d4b4a89e71f3cdc059e5bff75e747ee33','Reproduces exact reviewed support-v1 connected ROM')
    candidate=Path(connected['path']).parent/(label+'-preview.json')
    candidate.write_text(json.dumps(connected,indent=2)+'\n',encoding='utf-8')
    view=ROOT/'build/art/connected'/connected['romSha1']/'live-palette-view.json'
    (out.parent/'current.json').write_bytes(view.read_bytes())
    check(all(p.read_bytes()==raw for p,raw in before.items()),'Installed and historical source indexes unchanged')
    report=dict(status='passed',romSha1=connected['romSha1'],checks=checks,manifest=str(candidate),view=str(view),
        sourceOverride=revised['artOverrides'],scope='Private Samurai own-palette import. Other class pixels and all native commands/timing preserved. Partial support-action map retains unmapped temporary poses and cropped water. No runtime, final-art or installed delivery acceptance.' if args.support_actions else 'Private Samurai v7 own-palette six-pose import. Default build byte-exact; compiled engine changes only Samurai color table; other class pixels and all native commands/timing preserved. Other actions still repeat march poses and water is cropped. No runtime, final-art or installed delivery acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');raise
finally:
    for p,raw in before.items():p.write_bytes(raw)
