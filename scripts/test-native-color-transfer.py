"""Check native conversion provenance, cross-frame colors and actual ROM tiles."""
import argparse, datetime, hashlib, json, struct
from pathlib import Path
from PIL import Image
from native_art import ROOT, pack_tiles, sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',type=Path,default=ROOT/'build/art/native-color-transfer-2026-09-20/dark-knight-candidate.json')
    manifest=parser.parse_args().manifest
    meta=json.loads(manifest.read_text());rom=Path(meta['path']).read_bytes()
    proof=meta['components']['reviewedActions'];ref=proof['nativeColorConversion']
    out=ROOT/'build/art/native-color-transfer-2026-09-20/checks'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);checks=[];failure=None
    def check(value,label):
        assert value,label
        checks.append(label)
    try:
        check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Actual ROM identity')
        raw=Path(ref['path']).read_bytes();check(sha(raw)==ref['sha256'],'Archived conversion recipe')
        conversion_spec=json.loads(raw)
        receipts=json.loads((ROOT/'src/art/race-study/native-color-study-v1.json').read_text())
        nonhuman=json.loads((ROOT/'src/art/race-study/nonhuman-native-color-v1.json').read_text())
        parent=json.loads(Path(proof['sourceManifest']).read_text());before=Path(parent['path']).read_bytes()
        check(rom[0x419d60:0x41a860]==before[0x419d60:0x41a860],'Native shared palette tables unchanged')
        for conversion in conversion_spec.get('units',[conversion_spec]):
            job=conversion['job']
            approved=next(g for g in receipts['generations']+receipts.get('nativeConversions',[])+nonhuman['bases'] if g.get('convertedSha256')==conversion['approvedNativeBaseSha256'])
            if job<118:
                check(approved['status'].startswith('native-base-user-approved'),'Explicit human native-base user approval')
            else:
                check(approved['status']=='native-base-primary-reviewed-for-integration' and conversion['reviewAuthority']=='primary agent; not user approval','Primary native-base review, not user approval')
            target=ROOT/conversion['approvedNativeBase']
            check(sha(target.read_bytes())==conversion['approvedNativeBaseSha256'],'Approved native PNG identity')
            assets={a['pose']:a for a in proof['assets'] if a['job']==job}
            check(set(assets)=={r['pose'] for r in conversion['records']} and len(assets)==conversion['poseCount'],'All declared land and water poses converted')
            color_map={};exact=0
            for row in conversion['records']:
                label=row['pose'];a=assets[label];src=ROOT/row['source'];dest=ROOT/a['source']
                check(sha(src.read_bytes())==row['sourceSha256'],'Original art identity '+label)
                check(sha(dest.read_bytes())==row['selected']['sha256']==a['sourceSha256'],'Imported conversion identity '+label)
                source=Image.open(src).convert('RGBA');converted=Image.open(dest)
                check(converted.size==(32,32) and converted.mode=='P' and converted.info.get('transparency')==0,'Native indexed cell '+label)
                words=struct.unpack_from('<16H',rom,a['nativePaletteOffset'])
                colors=[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
                check(converted.getpalette()[:48]==colors and set(converted.get_flattened_data())<=set(range(16)),'Only actual native palette indices '+label)
                check(pack_tiles(converted,16)==rom[a['tile']:a['tile']+512],'Actual ROM tiles equal converted drawing '+label)
                if row['selected']['exactApprovedBase']:
                    exact+=1;check(dest.read_bytes()==target.read_bytes(),'Exact approved base retained '+label)
                else:
                    check(source.getchannel('A').tobytes()==converted.convert('RGBA').getchannel('A').tobytes(),'Pose silhouette unchanged '+label)
                    for rgba,index in zip(source.get_flattened_data(),converted.get_flattened_data()):
                        if rgba[3]:
                            key=rgba[:3]
                            check(key not in color_map or color_map[key]==index,'Consistent RGB to native index '+label)
                            color_map[key]=index
            check(exact>0,'Approved base used in native animation graph')
        changes=conversion_spec.get('selectorChanges',[])
        check(changes==nonhuman.get('selectorChanges',[]) if changes else not proof.get('nativeSelectorChanges'),'Declared source native palette choices')
        table=struct.unpack_from('<I',before,0xc8598)[0]-0x08000000
        by_job={c['job']:c for c in changes}
        for job in range(126):
            offset=table+52*job+11;change=by_job.get(job)
            check(rom[offset]==(change['after'] if change else before[offset]),'Native selector choice '+str(job))
            if change:check(before[offset]==change['before'],'Original selector authenticated '+str(job))
        if 'retainedDarkKnightCandidate' in conversion_spec:
            prior_ref=conversion_spec['retainedDarkKnightCandidate'];prior_path=ROOT/prior_ref['path']
            check(sha(prior_path.read_bytes())==prior_ref['sha256'],'Retained tested Dark Knight candidate identity')
            prior=json.loads(prior_path.read_text());prior_rom=Path(prior['path']).read_bytes()
            check(hashlib.sha1(prior_rom).hexdigest()==prior_ref['romSha1'],'Retained tested Dark Knight ROM identity')
            old={a['pose']:a for a in prior['components']['reviewedActions']['assets'] if a['job']==117}
            current={a['pose']:a for a in proof['assets'] if a['job']==117}
            check(set(old)==set(current),'Every tested Dark Knight pose retained')
            for pose,a in current.items():
                b=old[pose]
                check(rom[a['tile']:a['tile']+512]==prior_rom[b['tile']:b['tile']+512], 'Tested Dark Knight tile bytes unchanged '+pose)
                check(rom[a['oam']:a['oam']+8]==prior_rom[b['oam']:b['oam']+8], 'Tested Dark Knight geometry unchanged '+pose)
                check((a['nativeSelector'],a['opposingSelector'])==(b['nativeSelector'],b['opposingSelector']), 'Tested Dark Knight side colors unchanged '+pose)
        check(len(proof['assets'])==675 and proof['importedDrawRecords']==3025 and proof['controlRecords']==1116,'Full original animation inventory preserved')
        check(not meta['reviewedArtPilot']['productionAccepted'],'Pilot does not claim final acceptance')
    except BaseException as error:failure=repr(error)
    report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],manifestSha256=sha(manifest.read_bytes()),
                checks=checks,failure=failure,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(checks),failure=failure,report=str(out/'report.json'))))
    assert failure is None,failure


if __name__=='__main__':main()
